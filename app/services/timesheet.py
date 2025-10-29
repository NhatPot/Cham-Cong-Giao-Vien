from datetime import datetime
from sqlalchemy.orm import Session
from app.models import TeacherCheckin, ClassSession, TimesheetOverride


def _overlap_seconds(checkin_dt, checkout_dt, start_dt, end_dt) -> int:
    if not checkin_dt or not checkout_dt:
        return 0
    a = max(checkin_dt, start_dt)
    b = min(checkout_dt, end_dt)
    if b <= a:
        return 0
    return int((b - a).total_seconds())


def get_month_hours(db: Session, teacher_id: int, month: str) -> float:
    # Override first
    override = (
        db.query(TimesheetOverride)
        .filter(TimesheetOverride.teacher_id == teacher_id, TimesheetOverride.month == month)
        .first()
    )
    if override is not None:
        return float(round(override.hours, 2))

    # month: YYYY-MM
    year, mon = map(int, month.split("-"))
    start = datetime(year, mon, 1)
    end = datetime(year + (mon // 12), (mon % 12) + 1, 1)

    q = db.query(TeacherCheckin).join(ClassSession, TeacherCheckin.session_id == ClassSession.id).filter(
        TeacherCheckin.teacher_id == teacher_id,
        ClassSession.start_dt >= start,
        ClassSession.start_dt < end,
    )
    seconds = 0
    for r in q.all():
        session = db.query(ClassSession).get(r.session_id)
        seconds += _overlap_seconds(r.checkin_dt, r.checkout_dt, session.start_dt, session.end_dt)
    return round(seconds / 3600.0, 2)
