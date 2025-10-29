from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import TeacherCheckin, ClassSession


def normalize_checkin_out(checkin: TeacherCheckin, start_dt, end_dt):
    if not checkin.checkin_dt or not checkin.checkout_dt:
        return checkin
    if checkin.checkin_dt < start_dt:
        checkin.checkin_dt = start_dt
    if checkin.checkout_dt > end_dt:
        checkin.checkout_dt = end_dt
    if checkin.checkout_dt < checkin.checkin_dt:
        checkin.checkout_dt = checkin.checkin_dt
    return checkin


def auto_close_overdue(db: Session):
    now = datetime.now()
    overdue_sessions = db.query(ClassSession).filter(ClassSession.end_dt + timedelta(minutes=60) < now).all()
    for sess in overdue_sessions:
        open_records = db.query(TeacherCheckin).filter(
            TeacherCheckin.session_id == sess.id,
            TeacherCheckin.checkout_dt == None,  # noqa: E711
        ).all()
        for rec in open_records:
            rec.checkout_dt = sess.end_dt
            if not rec.method:
                rec.method = "auto"
    if overdue_sessions:
        db.commit()
