"""
High School Management System API

A FastAPI application with user authentication and role-based permissions
for managing extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
from pathlib import Path

from database import engine, get_db, Base
from models import User, Activity, Enrollment
from schemas import Activity as ActivitySchema, ActivityCreate, Enrollment as EnrollmentSchema, EnrollmentCreate
from auth import UserManager
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication

# Create tables
Base.metadata.create_all(bind=engine)

SECRET = "your-secret-key"  # In production, use env var

auth_backends = [
    JWTAuthentication(secret=SECRET, lifetime_seconds=3600),
]

fastapi_users = FastAPIUsers[User, int](
    UserManager,
    auth_backends,
)

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities with authentication")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

# Include auth routers
app.include_router(
    fastapi_users.get_auth_router(auth_backends[0]),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(),
    prefix="/users",
    tags=["users"],
)

# Dependency
current_user = fastapi_users.current_user()
current_active_user = fastapi_users.current_user(active=True)

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")

@app.get("/activities", response_model=list[ActivitySchema])
def get_activities(db: Session = Depends(get_db), user: User = Depends(current_active_user)):
    activities = db.query(Activity).all()
    return activities

@app.post("/activities", response_model=ActivitySchema)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db), user: User = Depends(current_active_user)):
    if user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_activity = Activity(**activity.dict())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@app.post("/enrollments", response_model=EnrollmentSchema)
def enroll(enrollment: EnrollmentCreate, db: Session = Depends(get_db), user: User = Depends(current_active_user)):
    # Check if already enrolled
    existing = db.query(Enrollment).filter(Enrollment.user_id == user.id, Enrollment.activity_id == enrollment.activity_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled")
    db_enrollment = Enrollment(user_id=user.id, **enrollment.dict())
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

# For simplicity, populate some initial data
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    if not db.query(Activity).first():
        activities_data = [
            {"title": "Chess Club", "description": "Learn strategies and compete in chess tournaments", "schedule": "Fridays, 3:30 PM - 5:00 PM", "max_participants": 12},
            {"title": "Programming Class", "description": "Learn programming fundamentals and build software projects", "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM", "max_participants": 20},
            {"title": "Gym Class", "description": "Physical education and sports activities", "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM", "max_participants": 30},
            {"title": "Soccer Team", "description": "Join the school soccer team and compete in matches", "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM", "max_participants": 22},
            {"title": "Basketball Team", "description": "Practice and play basketball with the school team", "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM", "max_participants": 15},
        ]
        for data in activities_data:
            activity = Activity(**data)
            db.add(activity)
        db.commit()
    db.close()
