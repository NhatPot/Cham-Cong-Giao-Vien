from fastapi import APIRouter, Request, Depends, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db import get_db
from app.models import Teacher, ClassSession, TeacherCheckin
from app.main import settings
from app.security import verify_token
from app.services.timesheet import get_month_hours
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os

router = APIRouter(tags=["teacher"])

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "templates"))


class ScanRequest(BaseModel):
    session_id: int
    qr_token: str


def _today_range():
    now = datetime.now()
    start = datetime(now.year, now.month, now.day)
    end = start + timedelta(days=1)
    return start, end


@router.get("/t/{magic_token}", response_class=HTMLResponse)
def teacher_home(magic_token: str, request: Request, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.magic_token == magic_token).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    start_day, end_day = _today_range()
    sessions = (
        db.query(ClassSession)
        .filter(ClassSession.start_dt >= start_day, ClassSession.start_dt < end_day)
        .order_by(ClassSession.start_dt)
        .all()
    )
    # find open checkins for teacher keyed by session
    open_by_session = {}
    for s in sessions:
        open_rec = (
            db.query(TeacherCheckin)
            .filter(TeacherCheckin.session_id == s.id, TeacherCheckin.teacher_id == teacher.id)
            .order_by(TeacherCheckin.id.desc())
            .first()
        )
        open_by_session[s.id] = open_rec

    # Get current month for history link
    now = datetime.now()
    current_month = now.strftime("%Y-%m")
    
    return templates.TemplateResponse(
        "teacher_home.html",
        {"request": request, "teacher": teacher, "sessions": sessions, "open_by_session": open_by_session, "current_month": current_month},
    )


@router.get("/t/{magic_token}/scan", response_class=HTMLResponse)
def teacher_scan(magic_token: str, request: Request, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.magic_token == magic_token).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return templates.TemplateResponse("teacher_scan.html", {"request": request, "teacher": teacher})


@router.get("/t/{magic_token}/history", response_class=HTMLResponse)
def teacher_history(magic_token: str, request: Request, month: str = Query(...), db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.magic_token == magic_token).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Get month data
    year, mon = map(int, month.split("-"))
    start = datetime(year, mon, 1)
    if mon == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, mon + 1, 1)
    
    # Get checkins for the month
    checkins = (
        db.query(TeacherCheckin)
        .join(ClassSession, TeacherCheckin.session_id == ClassSession.id)
        .filter(
            TeacherCheckin.teacher_id == teacher.id,
            ClassSession.start_dt >= start,
            ClassSession.start_dt < end,
        )
        .order_by(ClassSession.start_dt.desc())
        .all()
    )
    
    # Calculate total hours
    total_hours = get_month_hours(db, teacher.id, month)
    
    return templates.TemplateResponse("teacher_history.html", {
        "request": request,
        "teacher": teacher,
        "month": month,
        "checkins": checkins,
        "total_hours": total_hours
    })


@router.post("/t/{magic_token}/checkin")
def manual_checkin(magic_token: str, session_id: int = Form(...), db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.magic_token == magic_token).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    session = db.query(ClassSession).get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Kiểm tra khung giờ: cho phép cấu hình qua settings
    now = datetime.now()
    if not settings.ALLOW_MANUAL_ANYTIME:
        early = timedelta(minutes=settings.CHECKIN_EARLY_MIN)
        late = timedelta(minutes=settings.CHECKIN_LATE_MIN)
        if not (session.start_dt - early <= now <= session.start_dt + late):
            raise HTTPException(status_code=400, detail="Outside check-in window")

    # ensure only one open record per (session, teacher)
    open_rec = (
        db.query(TeacherCheckin)
        .filter(TeacherCheckin.session_id == session.id, TeacherCheckin.teacher_id == teacher.id, TeacherCheckin.checkout_dt == None)  # noqa: E711
        .first()
    )
    if open_rec:
        raise HTTPException(status_code=400, detail="Already checked in")

    rec = TeacherCheckin(session_id=session.id, teacher_id=teacher.id, checkin_dt=now, method="manual")
    db.add(rec)
    db.commit()
    return RedirectResponse(url=f"/t/{magic_token}", status_code=303)


@router.post("/t/{magic_token}/checkout")
def manual_checkout(magic_token: str, session_id: int = Form(...), db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.magic_token == magic_token).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    session = db.query(ClassSession).get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    now = datetime.now()
    # Kiểm tra khung giờ checkout
    if not settings.ALLOW_MANUAL_ANYTIME:
        early = timedelta(minutes=settings.CHECKOUT_EARLY_MIN)
        late = timedelta(minutes=settings.CHECKOUT_LATE_MIN)
        if not (session.end_dt - early <= now <= session.end_dt + late):
            raise HTTPException(status_code=400, detail="Outside check-out window")

    open_rec = (
        db.query(TeacherCheckin)
        .filter(TeacherCheckin.session_id == session.id, TeacherCheckin.teacher_id == teacher.id, TeacherCheckin.checkout_dt == None)  # noqa: E711
        .order_by(TeacherCheckin.id.desc())
        .first()
    )
    if not open_rec:
        raise HTTPException(status_code=400, detail="No open check-in")

    open_rec.checkout_dt = now
    open_rec.method = open_rec.method or "manual"
    db.commit()
    return RedirectResponse(url=f"/t/{magic_token}", status_code=303)


@router.post("/t/{magic_token}/scan-checkin")
def scan_checkin(magic_token: str, request: ScanRequest, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.magic_token == magic_token).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Verify QR token
    try:
        session_id, exp_ts = verify_token(request.qr_token)
        if session_id != request.session_id:
            raise HTTPException(status_code=400, detail="Token session mismatch")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid token: {e}")
    
    session = db.query(ClassSession).get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check time window for QR (không bỏ qua bằng ALLOW_MANUAL_ANYTIME)
    now = datetime.now()
    early = timedelta(minutes=settings.CHECKIN_EARLY_MIN)
    late = timedelta(minutes=settings.CHECKIN_LATE_MIN)
    if not (session.start_dt - early <= now <= session.start_dt + late):
        raise HTTPException(status_code=400, detail="Outside check-in window")

    # Ensure only one open record per (session, teacher)
    open_rec = (
        db.query(TeacherCheckin)
        .filter(TeacherCheckin.session_id == session.id, TeacherCheckin.teacher_id == teacher.id, TeacherCheckin.checkout_dt == None)  # noqa: E711
        .first()
    )
    if open_rec:
        raise HTTPException(status_code=400, detail="Already checked in")

    rec = TeacherCheckin(session_id=session.id, teacher_id=teacher.id, checkin_dt=now, method="qr")
    db.add(rec)
    db.commit()
    return {"status": "success", "message": "Check-in successful"}


@router.post("/t/{magic_token}/scan-checkout")
def scan_checkout(magic_token: str, request: ScanRequest, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.magic_token == magic_token).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Verify QR token
    try:
        session_id, exp_ts = verify_token(request.qr_token)
        if session_id != request.session_id:
            raise HTTPException(status_code=400, detail="Token session mismatch")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid token: {e}")
    
    session = db.query(ClassSession).get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    now = datetime.now()
    # Check time window for QR
    early = timedelta(minutes=settings.CHECKOUT_EARLY_MIN)
    late = timedelta(minutes=settings.CHECKOUT_LATE_MIN)
    if not (session.end_dt - early <= now <= session.end_dt + late):
        raise HTTPException(status_code=400, detail="Outside check-out window")

    open_rec = (
        db.query(TeacherCheckin)
        .filter(TeacherCheckin.session_id == session.id, TeacherCheckin.teacher_id == teacher.id, TeacherCheckin.checkout_dt == None)  # noqa: E711
        .order_by(TeacherCheckin.id.desc())
        .first()
    )
    if not open_rec:
        raise HTTPException(status_code=400, detail="No open check-in")

    open_rec.checkout_dt = now
    open_rec.method = "qr"
    db.commit()
    return {"status": "success", "message": "Check-out successful"}
