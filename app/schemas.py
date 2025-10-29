from pydantic import BaseModel
from datetime import datetime

class TeacherBase(BaseModel):
    name: str

class TeacherCreate(TeacherBase):
    pass

class TeacherOut(TeacherBase):
    id: int
    magic_token: str
    status: str

    class Config:
        from_attributes = True


class SessionOut(BaseModel):
    id: int
    class_id: int
    start_dt: datetime
    end_dt: datetime
    topic: str | None = None

    class Config:
        from_attributes = True
