from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import bcrypt
import jwt
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'istem-secret-key-2025')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Security
security = HTTPBearer()

# Enums
class UserRole(str, Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"

class LessonType(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    role: UserRole = UserRole.STUDENT
    avatar: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    role: UserRole = UserRole.STUDENT

class UserLogin(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class Course(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    instructor_id: str
    instructor_name: str
    thumbnail: Optional[str] = None
    duration_hours: int
    level: str  # Beginner, Intermediate, Advanced
    price: float = 0.0
    is_published: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CourseCreate(BaseModel):
    title: str
    description: str
    thumbnail: Optional[str] = None
    duration_hours: int
    level: str
    price: float = 0.0

class Lesson(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    title: str
    description: str
    content: str  # Can be video URL, text content, etc.
    lesson_type: LessonType
    duration_minutes: int
    order: int
    is_completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LessonCreate(BaseModel):
    title: str
    description: str
    content: str
    lesson_type: LessonType
    duration_minutes: int
    order: int

class Enrollment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    progress_percentage: float = 0.0
    completed_lessons: List[str] = []
    last_accessed: datetime = Field(default_factory=datetime.utcnow)

class Progress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    lesson_id: str
    completed: bool = False
    time_spent_minutes: int = 0
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Meeting(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    title: str
    description: str
    scheduled_at: datetime
    duration_minutes: int = 60
    meeting_url: str
    instructor_id: str
    max_participants: int = 50
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MeetingCreate(BaseModel):
    course_id: str
    title: str
    description: str
    scheduled_at: datetime
    duration_minutes: int = 60
    meeting_url: str
    max_participants: int = 50

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

# Auth Routes
@api_router.post("/auth/register", response_model=AuthResponse)
async def register_user(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        name=user_data.name,
        role=user_data.role
    )
    
    # Store user with password
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    await db.users.insert_one(user_dict)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return AuthResponse(access_token=access_token, user=user)

@api_router.post("/auth/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin):
    # Find user
    user_doc = await db.users.find_one({"email": login_data.email})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(login_data.password, user_doc["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    user = User(**user_doc)
    access_token = create_access_token(data={"sub": user.id})
    
    return AuthResponse(access_token=access_token, user=user)

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Course Routes
@api_router.get("/courses", response_model=List[Course])
async def get_courses():
    courses = await db.courses.find({"is_published": True}).to_list(1000)
    return [Course(**course) for course in courses]

@api_router.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: str):
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return Course(**course)

@api_router.post("/courses", response_model=Course)
async def create_course(course_data: CourseCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.INSTRUCTOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only instructors and admins can create courses")
    
    course = Course(
        **course_data.dict(),
        instructor_id=current_user.id,
        instructor_name=current_user.name
    )
    
    await db.courses.insert_one(course.dict())
    return course

# Enrollment Routes
@api_router.post("/enrollments/{course_id}")
async def enroll_in_course(course_id: str, current_user: User = Depends(get_current_user)):
    # Check if course exists
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if already enrolled
    existing_enrollment = await db.enrollments.find_one({
        "user_id": current_user.id,
        "course_id": course_id
    })
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")
    
    # Create enrollment
    enrollment = Enrollment(
        user_id=current_user.id,
        course_id=course_id
    )
    
    await db.enrollments.insert_one(enrollment.dict())
    return {"message": "Successfully enrolled in course"}

@api_router.get("/my-courses", response_model=List[dict])
async def get_my_courses(current_user: User = Depends(get_current_user)):
    # Get user's enrollments
    enrollments = await db.enrollments.find({"user_id": current_user.id}).to_list(1000)
    
    my_courses = []
    for enrollment in enrollments:
        course = await db.courses.find_one({"id": enrollment["course_id"]})
        if course:
            course_data = Course(**course)
            my_courses.append({
                "course": course_data,
                "enrollment": Enrollment(**enrollment)
            })
    
    return my_courses

# Lesson Routes
@api_router.get("/courses/{course_id}/lessons", response_model=List[Lesson])
async def get_course_lessons(course_id: str, current_user: User = Depends(get_current_user)):
    # Check enrollment
    enrollment = await db.enrollments.find_one({
        "user_id": current_user.id,
        "course_id": course_id
    })
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")
    
    lessons = await db.lessons.find({"course_id": course_id}).sort("order", 1).to_list(1000)
    return [Lesson(**lesson) for lesson in lessons]

@api_router.post("/courses/{course_id}/lessons", response_model=Lesson)
async def create_lesson(course_id: str, lesson_data: LessonCreate, current_user: User = Depends(get_current_user)):
    # Check if user is instructor or admin
    if current_user.role not in [UserRole.INSTRUCTOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only instructors and admins can create lessons")
    
    # Check if course exists and user is the instructor
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course["instructor_id"] != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to add lessons to this course")
    
    lesson = Lesson(course_id=course_id, **lesson_data.dict())
    await db.lessons.insert_one(lesson.dict())
    return lesson

# Progress Routes
@api_router.post("/progress/{lesson_id}")
async def mark_lesson_complete(lesson_id: str, current_user: User = Depends(get_current_user)):
    # Get lesson
    lesson = await db.lessons.find_one({"id": lesson_id})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check enrollment
    enrollment = await db.enrollments.find_one({
        "user_id": current_user.id,
        "course_id": lesson["course_id"]
    })
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")
    
    # Create or update progress
    progress = Progress(
        user_id=current_user.id,
        course_id=lesson["course_id"],
        lesson_id=lesson_id,
        completed=True,
        completed_at=datetime.utcnow()
    )
    
    await db.progress.replace_one(
        {"user_id": current_user.id, "lesson_id": lesson_id},
        progress.dict(),
        upsert=True
    )
    
    # Update enrollment progress
    total_lessons = await db.lessons.count_documents({"course_id": lesson["course_id"]})
    completed_lessons = await db.progress.count_documents({
        "user_id": current_user.id,
        "course_id": lesson["course_id"],
        "completed": True
    })
    
    progress_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
    
    await db.enrollments.update_one(
        {"user_id": current_user.id, "course_id": lesson["course_id"]},
        {
            "$set": {
                "progress_percentage": progress_percentage,
                "last_accessed": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Progress updated", "progress_percentage": progress_percentage}

@api_router.get("/courses/{course_id}/progress")
async def get_course_progress(course_id: str, current_user: User = Depends(get_current_user)):
    # Get user progress for this course
    progress_docs = await db.progress.find({
        "user_id": current_user.id,
        "course_id": course_id
    }).to_list(1000)
    
    progress_list = [Progress(**doc) for doc in progress_docs]
    
    # Get enrollment info
    enrollment = await db.enrollments.find_one({
        "user_id": current_user.id,
        "course_id": course_id
    })
    
    return {
        "progress": progress_list,
        "enrollment": Enrollment(**enrollment) if enrollment else None
    }

# Meeting Routes
@api_router.get("/courses/{course_id}/meetings", response_model=List[Meeting])
async def get_course_meetings(course_id: str, current_user: User = Depends(get_current_user)):
    # Check enrollment
    enrollment = await db.enrollments.find_one({
        "user_id": current_user.id,
        "course_id": course_id
    })
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")
    
    meetings = await db.meetings.find({"course_id": course_id}).sort("scheduled_at", 1).to_list(1000)
    return [Meeting(**meeting) for meeting in meetings]

@api_router.post("/courses/{course_id}/meetings", response_model=Meeting)
async def create_meeting(course_id: str, meeting_data: MeetingCreate, current_user: User = Depends(get_current_user)):
    # Check if user is instructor or admin
    if current_user.role not in [UserRole.INSTRUCTOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only instructors and admins can create meetings")
    
    # Check if course exists and user is the instructor
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course["instructor_id"] != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to create meetings for this course")
    
    meeting = Meeting(
        **meeting_data.dict(),
        instructor_id=current_user.id
    )
    
    await db.meetings.insert_one(meeting.dict())
    return meeting

# Dashboard Routes
@api_router.get("/dashboard")
async def get_dashboard(current_user: User = Depends(get_current_user)):
    # Get user's enrollments with course info
    enrollments = await db.enrollments.find({"user_id": current_user.id}).to_list(1000)
    
    dashboard_data = {
        "user": current_user,
        "total_courses": len(enrollments),
        "recent_courses": [],
        "upcoming_meetings": []
    }
    
    # Get recent courses with progress
    for enrollment in enrollments[:5]:  # Last 5 courses
        course = await db.courses.find_one({"id": enrollment["course_id"]})
        if course:
            dashboard_data["recent_courses"].append({
                "course": Course(**course),
                "progress": enrollment["progress_percentage"],
                "last_accessed": enrollment["last_accessed"]
            })
    
    # Get upcoming meetings
    upcoming_meetings = await db.meetings.find({
        "course_id": {"$in": [e["course_id"] for e in enrollments]},
        "scheduled_at": {"$gte": datetime.utcnow()}
    }).sort("scheduled_at", 1).limit(5).to_list(5)
    
    dashboard_data["upcoming_meetings"] = [Meeting(**meeting) for meeting in upcoming_meetings]
    
    return dashboard_data

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()