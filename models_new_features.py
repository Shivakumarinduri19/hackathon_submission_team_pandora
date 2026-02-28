"""
New models for:
1. Multi-sheet upload & error pattern analysis
2. WhatsApp reminders
3. Open discussions / student forum
"""
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


# ─────────────────────────────────────────────
# FEATURE 1: Multi-sheet upload + error patterns
# ─────────────────────────────────────────────

class UploadedSheet(Base):
    """Stores each uploaded mock test sheet (PDF / image / text)"""
    __tablename__ = "uploaded_sheets"

    id          = Column(Integer, primary_key=True, index=True)
    student_id  = Column(Integer, ForeignKey("student_profiles.id"), index=True)
    file_name   = Column(String)
    file_type   = Column(String)          # pdf, image, text, csv
    raw_text    = Column(Text)            # extracted text content
    test_date   = Column(String, nullable=True)
    score       = Column(Float, nullable=True)
    total_marks = Column(Float, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    student      = relationship("StudentProfile", back_populates="uploaded_sheets")
    error_patterns = relationship("ErrorPattern", back_populates="sheet")


class ErrorPattern(Base):
    """Aggregated error analysis across multiple sheets"""
    __tablename__ = "error_patterns"

    id              = Column(Integer, primary_key=True, index=True)
    student_id      = Column(Integer, ForeignKey("student_profiles.id"), index=True)
    sheet_id        = Column(Integer, ForeignKey("uploaded_sheets.id"), nullable=True)
    topic           = Column(String, index=True)
    error_type      = Column(String)      # conceptual / calculation / silly / time_based
    frequency       = Column(Integer, default=1)
    description     = Column(Text)
    suggestion      = Column(Text)
    severity        = Column(String, default="medium")   # low / medium / high
    created_at      = Column(DateTime, default=datetime.utcnow)

    student = relationship("StudentProfile", back_populates="error_patterns")
    sheet   = relationship("UploadedSheet",  back_populates="error_patterns")


# ─────────────────────────────────────────────
# FEATURE 2: WhatsApp Reminders
# ─────────────────────────────────────────────

class ReminderSetting(Base):
    """Student's WhatsApp reminder preferences"""
    __tablename__ = "reminder_settings"

    id              = Column(Integer, primary_key=True, index=True)
    student_id      = Column(Integer, ForeignKey("student_profiles.id"), unique=True)
    phone_number    = Column(String)          # +91XXXXXXXXXX
    reminder_time   = Column(String, default="07:00")   # HH:MM
    is_active       = Column(Boolean, default=True)
    reminder_types  = Column(String, default="daily,plan,analysis")  # comma-separated
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("StudentProfile", back_populates="reminder_setting")


class ReminderLog(Base):
    """Log of every reminder sent"""
    __tablename__ = "reminder_logs"

    id          = Column(Integer, primary_key=True, index=True)
    student_id  = Column(Integer, ForeignKey("student_profiles.id"))
    phone       = Column(String)
    message     = Column(Text)
    status      = Column(String, default="sent")   # sent / failed / pending
    sent_at     = Column(DateTime, default=datetime.utcnow)

    student = relationship("StudentProfile", back_populates="reminder_logs")


# ─────────────────────────────────────────────
# FEATURE 3: Open Discussions (Student Forum)
# ─────────────────────────────────────────────

class DiscussionPost(Base):
    """A question or discussion post by a student"""
    __tablename__ = "discussion_posts"

    id          = Column(Integer, primary_key=True, index=True)
    student_id  = Column(Integer, ForeignKey("student_profiles.id"))
    title       = Column(String)
    content     = Column(Text)
    topic_tag   = Column(String, nullable=True)      # e.g. "Integration", "Optics"
    exam_tag    = Column(String, nullable=True)      # e.g. "JEE", "NEET"
    upvotes     = Column(Integer, default=0)
    is_resolved = Column(Boolean, default=False)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student  = relationship("StudentProfile", back_populates="discussion_posts")
    replies  = relationship("DiscussionReply",  back_populates="post", cascade="all, delete")


class DiscussionReply(Base):
    """A reply to a discussion post"""
    __tablename__ = "discussion_replies"

    id          = Column(Integer, primary_key=True, index=True)
    post_id     = Column(Integer, ForeignKey("discussion_posts.id"))
    student_id  = Column(Integer, ForeignKey("student_profiles.id"))
    content     = Column(Text)
    upvotes     = Column(Integer, default=0)
    is_ai_reply = Column(Boolean, default=False)   # True if AI answered
    created_at  = Column(DateTime, default=datetime.utcnow)

    post    = relationship("DiscussionPost",    back_populates="replies")
    student = relationship("StudentProfile",    back_populates="discussion_replies")
