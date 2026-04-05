from pydantic import BaseModel
from typing import Optional

class ActivityBase(BaseModel):
    title: str
    description: Optional[str] = None
    schedule: Optional[str] = None
    max_participants: Optional[int] = None

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int

    class Config:
        from_attributes = True

class EnrollmentBase(BaseModel):
    activity_id: int
    status: Optional[str] = "pending"

class EnrollmentCreate(EnrollmentBase):
    pass

class Enrollment(EnrollmentBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True