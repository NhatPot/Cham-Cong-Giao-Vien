from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta
from uuid import uuid4

from app.db import engine, Base, SessionLocal
from app.models import Teacher, Class, ClassTeacher, ClassSession


def create_all():
    Base.metadata.create_all(bind=engine)


def seed():
    db: Session = SessionLocal()
    try:
        # if there is any teacher, assume seeded
        if db.execute(select(Teacher)).first():
            return
        t1 = Teacher(name="Nguyen Van A", magic_token=str(uuid4()), hourly_rate=120000, status="active")
        t2 = Teacher(name="Tran Thi B", magic_token=str(uuid4()), hourly_rate=120000, status="active")
        db.add_all([t1, t2])
        db.flush()

        c1 = Class(name="Excel Cơ Bản", room="A101")
        db.add(c1)
        db.flush()

        db.add_all([
            ClassTeacher(class_id=c1.id, teacher_id=t1.id),
            ClassTeacher(class_id=c1.id, teacher_id=t2.id),
        ])

        now = datetime.now()
        start1 = now.replace(hour=18, minute=0, second=0, microsecond=0)
        end1 = now.replace(hour=20, minute=0, second=0, microsecond=0)
        start2 = now.replace(hour=20, minute=0, second=0, microsecond=0)
        end2 = now.replace(hour=22, minute=0, second=0, microsecond=0)

        s1 = ClassSession(class_id=c1.id, start_dt=start1, end_dt=end1, topic="Buổi 1", status="scheduled")
        s2 = ClassSession(class_id=c1.id, start_dt=start2, end_dt=end2, topic="Buổi 2", status="scheduled")
        db.add_all([s1, s2])

        db.commit()
    finally:
        db.close()
