from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Role
    role = Column(String, default="student")  # student, teacher, admin

class Activity(Base):
    __tablename__ = "activity"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    schedule = Column(String)
    max_participants = Column(Integer)
    # Add more fields as needed

    # Enrollments
    enrollments = relationship("Enrollment", back_populates="activity")

class Enrollment(Base):
    __tablename__ = "enrollment"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    activity_id = Column(Integer, ForeignKey("activity.id"))
    status = Column(String, default="pending")  # pending, approved, rejected

    user = relationship("User")
    activity = relationship("Activity", back_populates="enrollments")