from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    magic_token: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hourly_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active")

    checkins = relationship("TeacherCheckin", back_populates="teacher")


class Class(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    room: Mapped[str | None] = mapped_column(String, nullable=True)

    sessions = relationship("ClassSession", back_populates="clazz")
    teachers = relationship("ClassTeacher", back_populates="clazz")


class ClassTeacher(Base):
    __tablename__ = "class_teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), index=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"), index=True)

    clazz = relationship("Class", back_populates="teachers")
    teacher = relationship("Teacher")

    __table_args__ = (
        UniqueConstraint("class_id", "teacher_id", name="uq_class_teacher"),
    )


class ClassSession(Base):
    __tablename__ = "class_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), index=True)
    start_dt: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    end_dt: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    topic: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="scheduled")

    clazz = relationship("Class", back_populates="sessions")
    checkins = relationship("TeacherCheckin", back_populates="session")


class TeacherCheckin(Base):
    __tablename__ = "teacher_checkins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("class_sessions.id"), index=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"), index=True)
    checkin_dt: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    checkout_dt: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    method: Mapped[str | None] = mapped_column(String, nullable=True)

    session = relationship("ClassSession", back_populates="checkins")
    teacher = relationship("Teacher", back_populates="checkins")

    __table_args__ = (
        UniqueConstraint("session_id", "teacher_id", "checkout_dt", name="uq_open_once"),
    )
