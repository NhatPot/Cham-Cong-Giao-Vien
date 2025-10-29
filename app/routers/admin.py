from fastapi import APIRouter, Request, Depends, Header, HTTPException, Form, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Teacher, Class, ClassTeacher, ClassSession, TeacherCheckin
from app.services.timesheet import get_month_hours
from app.services.attendance import auto_close_overdue
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from uuid import uuid4
import csv
import io
import os
from app.main import settings

router = APIRouter(tags=["admin"])

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "templates"))


def require_admin(x_admin_key: str | None = Header(default=None, alias="X-ADMIN-KEY")):
    if x_admin_key != settings.ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/admin", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
def admin_home(request: Request, db: Session = Depends(get_db)):
    # Auto-close overdue checkins
    auto_close_overdue(db)
    
    # Get current month data
    now = datetime.now()
    current_month = now.strftime("%Y-%m")
    
    # Get all teachers with their hours
    teachers = db.query(Teacher).all()
    teacher_hours = []
    for teacher in teachers:
        hours = get_month_hours(db, teacher.id, current_month)
        teacher_hours.append({
            "teacher": teacher,
            "hours": hours
        })
    
    # Get all classes
    classes = db.query(Class).all()
    
    # Get all sessions for current month
    start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        end_month = now.replace(year=now.year + 1, month=1, day=1)
    else:
        end_month = now.replace(month=now.month + 1, day=1)
    
    sessions = db.query(ClassSession).filter(
        ClassSession.start_dt >= start_month,
        ClassSession.start_dt < end_month
    ).order_by(ClassSession.start_dt.desc()).all()
    
    return templates.TemplateResponse("admin_home.html", {
        "request": request,
        "teachers": teachers,
        "classes": classes,
        "sessions": sessions,
        "teacher_hours": teacher_hours,
        "current_month": current_month
    })


@router.post("/admin/teacher", dependencies=[Depends(require_admin)])
def create_teacher(name: str = Form(...), hourly_rate: int = Form(120000), db: Session = Depends(get_db)):
    magic_token = str(uuid4())
    teacher = Teacher(name=name, magic_token=magic_token, hourly_rate=hourly_rate, status="active")
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    
    magic_link = f"/t/{magic_token}"
    return {"status": "success", "teacher_id": teacher.id, "magic_link": magic_link}


@router.post("/admin/class", dependencies=[Depends(require_admin)])
def create_class(name: str = Form(...), room: str = Form(""), db: Session = Depends(get_db)):
    class_obj = Class(name=name, room=room)
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    return {"status": "success", "class_id": class_obj.id}


@router.post("/admin/class/{class_id}/add-teacher", dependencies=[Depends(require_admin)])
def add_teacher_to_class(class_id: int, teacher_id: int = Form(...), db: Session = Depends(get_db)):
    # Check if already exists
    existing = db.query(ClassTeacher).filter(
        ClassTeacher.class_id == class_id,
        ClassTeacher.teacher_id == teacher_id
    ).first()
    
    if existing:
        return {"status": "error", "message": "Teacher already in class"}
    
    class_teacher = ClassTeacher(class_id=class_id, teacher_id=teacher_id)
    db.add(class_teacher)
    db.commit()
    return {"status": "success"}


@router.post("/admin/session", dependencies=[Depends(require_admin)])
def create_session(
    class_id: int = Form(...),
    start_dt: str = Form(...),
    end_dt: str = Form(...),
    topic: str = Form(""),
    db: Session = Depends(get_db)
):
    try:
        start_datetime = datetime.fromisoformat(start_dt)
        end_datetime = datetime.fromisoformat(end_dt)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")
    
    session = ClassSession(
        class_id=class_id,
        start_dt=start_datetime,
        end_dt=end_datetime,
        topic=topic,
        status="scheduled"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"status": "success", "session_id": session.id}


@router.delete("/admin/teacher/{teacher_id}", dependencies=[Depends(require_admin)])
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    # Delete dependent records: checkins and class mappings
    db.query(TeacherCheckin).filter(TeacherCheckin.teacher_id == teacher_id).delete()
    db.query(ClassTeacher).filter(ClassTeacher.teacher_id == teacher_id).delete()
    # Delete teacher
    teacher = db.query(Teacher).get(teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db.delete(teacher)
    db.commit()
    return {"status": "success"}


@router.delete("/admin/class/{class_id}", dependencies=[Depends(require_admin)])
def delete_class(class_id: int, db: Session = Depends(get_db)):
    # Delete dependent: sessions -> checkins, then class mappings, then class
    sessions = db.query(ClassSession).filter(ClassSession.class_id == class_id).all()
    session_ids = [s.id for s in sessions]
    if session_ids:
        db.query(TeacherCheckin).filter(TeacherCheckin.session_id.in_(session_ids)).delete(synchronize_session=False)
        db.query(ClassSession).filter(ClassSession.id.in_(session_ids)).delete(synchronize_session=False)
    db.query(ClassTeacher).filter(ClassTeacher.class_id == class_id).delete()
    clazz = db.query(Class).get(class_id)
    if not clazz:
        raise HTTPException(status_code=404, detail="Class not found")
    db.delete(clazz)
    db.commit()
    return {"status": "success"}


@router.delete("/admin/session/{session_id}", dependencies=[Depends(require_admin)])
def delete_session(session_id: int, db: Session = Depends(get_db)):
    # Delete dependent checkins then session
    db.query(TeacherCheckin).filter(TeacherCheckin.session_id == session_id).delete()
    session = db.query(ClassSession).get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"status": "success"}


@router.get("/admin/timesheet", dependencies=[Depends(require_admin)])
def get_timesheet(
    month: str = Query(...),
    db: Session = Depends(get_db)
):
    teachers = db.query(Teacher).all()
    teacher_hours = []
    for teacher in teachers:
        hours = get_month_hours(db, teacher.id, month)
        teacher_hours.append({
            "teacher": teacher,
            "hours": hours
        })
    
    return {"month": month, "teacher_hours": teacher_hours}


@router.get("/admin/timesheet/export.csv", dependencies=[Depends(require_admin)])
def export_timesheet_csv(
    month: str = Query(...),
    db: Session = Depends(get_db)
):
    teachers = db.query(Teacher).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Tên giáo viên", "Số giờ tháng", "Tỷ lệ/giờ", "Tổng tiền"])
    
    for teacher in teachers:
        hours = get_month_hours(db, teacher.id, month)
        total_amount = hours * (teacher.hourly_rate or 0)
        writer.writerow([
            teacher.name,
            hours,
            teacher.hourly_rate or 0,
            total_amount
        ])
    
    output.seek(0)
    
    def generate():
        yield output.getvalue()
    
    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=timesheet_{month}.csv"}
    )
