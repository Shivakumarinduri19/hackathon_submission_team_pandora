from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Student Profile Schemas ---
class StudentProfileBase(BaseModel):
    exam_type: str
    target_marks_rank: str

class StudentProfileCreate(StudentProfileBase):
    pass

class StudentProfile(StudentProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Mock Test Schemas ---
class MockTestCreate(BaseModel):
    student_id: int
    test_result_text: str

class MockTest(BaseModel):
    id: int
    student_id: int
    test_result_text: str
    weak_topics_json: str

    class Config:
        from_attributes = True

class WeakTopicsAnalysis(BaseModel):
    weak_topics: List[str]

# --- Revision Plan Schemas ---
class StudyHours(BaseModel):
    student_id: int
    weekday_hours: float
    weekend_hours: float

class RevisionPlanResponse(BaseModel):
    plan_text: str

# --- Free Resources Schemas ---
class FreeResourceCreate(BaseModel):
    topic: str
    exam_type: str
    resource_type: str
    title: str
    description: str
    url: str
    duration_minutes: Optional[int] = None
    difficulty_level: str = "beginner"
    source: str

class FreeResource(FreeResourceCreate):
    id: int
    created_at: datetime
    likes: int = 0

    class Config:
        from_attributes = True

# --- Progress Tracking Schemas ---
class ProgressTrackingCreate(BaseModel):
    student_id: int
    topic: str
    status: str = "pending"
    time_spent_minutes: int = 0
    performance_score: Optional[float] = None
    notes: Optional[str] = None
    resource_id: Optional[int] = None

class ProgressTrackingUpdate(BaseModel):
    status: Optional[str] = None
    time_spent_minutes: Optional[int] = None
    performance_score: Optional[float] = None
    notes: Optional[str] = None

class ProgressTracking(BaseModel):
    id: int
    student_id: int
    topic: str
    status: str
    study_date: datetime
    time_spent_minutes: int
    performance_score: Optional[float]
    notes: Optional[str]
    resource_id: Optional[int]

    class Config:
        from_attributes = True

class TopicResourceWithProgress(BaseModel):
    """Returns topic with available resources and student progress"""
    topic: str
    resources: List[FreeResource]
    student_progress: Optional[ProgressTracking] = None
    status: str = "pending"

# --- Chat History Schemas ---
class ChatMessageCreate(BaseModel):
    student_id: int
    question: str
    topic: Optional[str] = None

class ChatMessageResponse(BaseModel):
    id: int
    student_id: int
    question: str
    answer: str
    topic: Optional[str]
    helpful: Optional[bool]
    created_at: datetime

    class Config:
        from_attributes = True

class ChatFeedback(BaseModel):
    chat_id: int
    helpful: bool

# --- Dashboard Schemas ---
class DashboardStats(BaseModel):
    total_topics: int
    topics_completed: int
    topics_in_progress: int
    overall_progress_percentage: float
    average_performance_score: Optional[float]
    total_study_hours: float
    weak_topics: List[str]
    recent_chat_count: int

class DashboardTopicStatus(BaseModel):
    topic: str
    status: str
    progress_percentage: float
    performance_score: Optional[float]
    last_studied: Optional[datetime]
    resources_count: int
    free_resources: List[FreeResource]

class StudentDashboard(BaseModel):
    profile: StudentProfile
    stats: DashboardStats
    topics: List[DashboardTopicStatus]
    recent_chats: List[ChatMessageResponse]
