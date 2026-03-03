from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
# llms to wordk

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    exam_type = Column(String, index=True)
    target_marks_rank = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    mock_tests = relationship("MockTest", back_populates="student")
    revision_plans = relationship("RevisionPlan", back_populates="student")
    progress_tracking = relationship("ProgressTracking", back_populates="student")
    chat_history = relationship("ChatHistory", back_populates="student")

class MockTest(Base):
    __tablename__ = "mock_tests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"))
    test_result_text = Column(Text)
    weak_topics_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("StudentProfile", back_populates="mock_tests")

class RevisionPlan(Base):
    __tablename__ = "revision_plans"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"))
    weekday_hours = Column(Float)
    weekend_hours = Column(Float)
    plan_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("StudentProfile", back_populates="revision_plans")

class ProgressTracking(Base):
    """Tracks student progress for dashboard and analytics"""
    __tablename__ = "progress_tracking"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"))
    topic = Column(String, index=True)
    status = Column(String, default="pending")  # pending, in_progress, completed, mastered
    study_date = Column(DateTime, default=datetime.utcnow)
    time_spent_minutes = Column(Integer, default=0)
    performance_score = Column(Float, nullable=True)  # 0-100
    notes = Column(Text, nullable=True)
    resource_id = Column(Integer, ForeignKey("free_resources.id"), nullable=True)

    student = relationship("StudentProfile", back_populates="progress_tracking")
    resource = relationship("FreeResource", back_populates="progress_items")

class FreeResource(Base):
    """Stores free learning resources for each topic"""
    __tablename__ = "free_resources"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    exam_type = Column(String)  # JEE, NEET, GRE, etc.
    resource_type = Column(String)  # video, article, pdf, problem_set, practice_test
    title = Column(String)
    description = Column(Text)
    url = Column(String)
    duration_minutes = Column(Integer, nullable=True)
    difficulty_level = Column(String, default="beginner")  # beginner, intermediate, advanced
    source = Column(String)  # YouTube, Khan Academy, etc.
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    progress_items = relationship("ProgressTracking", back_populates="resource")

class ChatHistory(Base):
    """Stores chat history for Q&A bot"""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"))
    question = Column(Text)
    answer = Column(Text)
    topic = Column(String, nullable=True)
    helpful = Column(Boolean, nullable=True)  # User feedback
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("StudentProfile", back_populates="chat_history")
