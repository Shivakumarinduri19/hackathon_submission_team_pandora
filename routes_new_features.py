"""
New API routes — append to main_enhanced.py (or import this router).
Three new features:
  1. Multi-sheet upload + error pattern analysis
  2. WhatsApp reminder settings
  3. Open discussions / student forum
"""
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import io

from database import get_db
import models_enhanced as models
from models_new_features import (
    UploadedSheet, ErrorPattern,
    ReminderSetting, ReminderLog,
    DiscussionPost, DiscussionReply
)
import llm_new_features as llm_new
import whatsapp_notifier as wa

router = APIRouter(prefix="/api", tags=["new_features"])


# ═══════════════════════════════════════════════════════
#  FEATURE 1 — MULTI-SHEET UPLOAD & ERROR PATTERNS
# ═══════════════════════════════════════════════════════

@router.post("/sheets/upload")
async def upload_sheets(
    student_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload multiple mock test sheets (txt/csv files).  PDF support via text extraction."""
    student = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    saved_sheets = []
    for f in files:
        content_bytes = await f.read()
        try:
            raw_text = content_bytes.decode("utf-8", errors="ignore")
        except Exception:
            raw_text = content_bytes.decode("latin-1", errors="ignore")

        ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else "text"
        file_type = ext if ext in ("pdf", "csv", "txt", "text") else "text"

        extracted = llm_new.extract_text_from_content(raw_text, file_type)

        sheet = UploadedSheet(
            student_id=student_id,
            file_name=f.filename,
            file_type=file_type,
            raw_text=extracted,
        )
        db.add(sheet)
        db.flush()   # get sheet.id before commit
        saved_sheets.append({
            "id": sheet.id,
            "file_name": f.filename,
            "file_type": file_type,
            "char_count": len(extracted)
        })

    db.commit()
    return {"uploaded": len(saved_sheets), "sheets": saved_sheets}


@router.get("/sheets/{student_id}")
def get_student_sheets(student_id: int, db: Session = Depends(get_db)):
    """Get all uploaded sheets for a student."""
    sheets = db.query(UploadedSheet).filter(
        UploadedSheet.student_id == student_id
    ).order_by(UploadedSheet.uploaded_at.desc()).all()

    return [
        {
            "id": s.id,
            "file_name": s.file_name,
            "file_type": s.file_type,
            "score": s.score,
            "uploaded_at": s.uploaded_at.isoformat() if s.uploaded_at else None,
            "preview": (s.raw_text or "")[:200]
        }
        for s in sheets
    ]


@router.post("/sheets/analyze-patterns/{student_id}")
def analyze_error_patterns(student_id: int, db: Session = Depends(get_db)):
    """
    Run cross-sheet error pattern analysis for a student.
    Analyses ALL uploaded sheets and stores ErrorPattern records.
    """
    student = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    sheets = db.query(UploadedSheet).filter(UploadedSheet.student_id == student_id).all()
    if not sheets:
        raise HTTPException(status_code=400, detail="No sheets uploaded yet. Please upload mock test files first.")

    profile_data = {"exam_type": student.exam_type, "target_marks_rank": student.target_marks_rank}
    sheets_data  = [{"file_name": s.file_name, "raw_text": s.raw_text, "score": s.score} for s in sheets]

    patterns = llm_new.analyze_error_patterns_across_sheets(profile_data, sheets_data)

    # Clear old patterns for this student and save fresh ones
    db.query(ErrorPattern).filter(ErrorPattern.student_id == student_id).delete()
    for p in patterns:
        ep = ErrorPattern(
            student_id=student_id,
            topic=p.get("topic", "General"),
            error_type=p.get("error_type", "conceptual"),
            frequency=p.get("frequency", 1),
            description=p.get("description", ""),
            suggestion=p.get("suggestion", ""),
            severity=p.get("severity", "medium"),
        )
        db.add(ep)
    db.commit()

    # Send WhatsApp if reminder is active
    reminder = db.query(ReminderSetting).filter(
        ReminderSetting.student_id == student_id,
        ReminderSetting.is_active == True
    ).first()
    if reminder and "analysis" in (reminder.reminder_types or ""):
        wa.send_error_pattern_report(
            reminder.phone_number,
            f"Student {student_id}",
            patterns[:4]
        )

    return {"patterns_found": len(patterns), "patterns": patterns}


@router.get("/sheets/patterns/{student_id}")
def get_error_patterns(student_id: int, db: Session = Depends(get_db)):
    """Get stored error patterns for a student."""
    patterns = db.query(ErrorPattern).filter(
        ErrorPattern.student_id == student_id
    ).order_by(ErrorPattern.severity.desc(), ErrorPattern.frequency.desc()).all()

    return [
        {
            "id": p.id,
            "topic": p.topic,
            "error_type": p.error_type,
            "frequency": p.frequency,
            "description": p.description,
            "suggestion": p.suggestion,
            "severity": p.severity,
        }
        for p in patterns
    ]


# ═══════════════════════════════════════════════════════
#  FEATURE 2 — WHATSAPP REMINDERS
# ═══════════════════════════════════════════════════════

@router.post("/reminders/settings")
def save_reminder_settings(
    student_id: int,
    phone_number: str,
    reminder_time: str = "07:00",
    reminder_types: str = "daily,plan,analysis",
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """Save or update WhatsApp reminder settings for a student."""
    student = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing = db.query(ReminderSetting).filter(ReminderSetting.student_id == student_id).first()
    if existing:
        existing.phone_number   = phone_number
        existing.reminder_time  = reminder_time
        existing.reminder_types = reminder_types
        existing.is_active      = is_active
        existing.updated_at     = datetime.utcnow()
    else:
        existing = ReminderSetting(
            student_id=student_id,
            phone_number=phone_number,
            reminder_time=reminder_time,
            reminder_types=reminder_types,
            is_active=is_active,
        )
        db.add(existing)

    db.commit()
    db.refresh(existing)
    return {"message": "Reminder settings saved!", "settings": {
        "phone_number": existing.phone_number,
        "reminder_time": existing.reminder_time,
        "reminder_types": existing.reminder_types,
        "is_active": existing.is_active
    }}


@router.get("/reminders/settings/{student_id}")
def get_reminder_settings(student_id: int, db: Session = Depends(get_db)):
    """Get current reminder settings for a student."""
    setting = db.query(ReminderSetting).filter(ReminderSetting.student_id == student_id).first()
    if not setting:
        return {"configured": False}
    return {
        "configured": True,
        "phone_number": setting.phone_number,
        "reminder_time": setting.reminder_time,
        "reminder_types": setting.reminder_types,
        "is_active": setting.is_active
    }


@router.post("/reminders/test/{student_id}")
def send_test_reminder(student_id: int, db: Session = Depends(get_db)):
    """Send a test WhatsApp message immediately (for demo/verification)."""
    setting = db.query(ReminderSetting).filter(ReminderSetting.student_id == student_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="No reminder settings found. Please configure first.")

    success = wa.send_custom_reminder(
        setting.phone_number,
        f"Student {student_id}",
        "This is a test reminder from Exam Coach AI! 🎉 Your reminders are working correctly."
    )

    log = ReminderLog(
        student_id=student_id,
        phone=setting.phone_number,
        message="Test reminder",
        status="sent" if success else "failed"
    )
    db.add(log)
    db.commit()

    return {"sent": success, "phone": setting.phone_number}


@router.post("/reminders/send-daily/{student_id}")
def send_daily_reminder(student_id: int, db: Session = Depends(get_db)):
    """Manually trigger a daily study reminder (or call from scheduler)."""
    student = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    setting = db.query(ReminderSetting).filter(
        ReminderSetting.student_id == student_id,
        ReminderSetting.is_active == True
    ).first()
    if not setting:
        raise HTTPException(status_code=404, detail="No active reminder settings.")

    # Get today's topics from latest plan
    latest_plan = db.query(models.RevisionPlan).filter(
        models.RevisionPlan.student_id == student_id
    ).order_by(models.RevisionPlan.id.desc()).first()

    topics = []
    if latest_plan:
        try:
            plan_data = json.loads(latest_plan.plan_text)
            today_item = plan_data.get("plan", [{}])[0]
            topics = [today_item.get("topic", "Check your plan")]
        except:
            topics = ["Check your revision plan"]
    else:
        # Fall back to weak topics
        latest_test = db.query(models.MockTest).filter(
            models.MockTest.student_id == student_id
        ).order_by(models.MockTest.id.desc()).first()
        if latest_test:
            topics = json.loads(latest_test.weak_topics_json)[:3]

    if not topics:
        topics = ["Open Exam Coach AI to view your study plan"]

    success = wa.send_daily_reminder(
        setting.phone_number,
        f"Student {student_id}",
        topics,
        student.exam_type
    )

    log = ReminderLog(
        student_id=student_id,
        phone=setting.phone_number,
        message=f"Daily reminder: {', '.join(topics[:3])}",
        status="sent" if success else "failed"
    )
    db.add(log)
    db.commit()

    return {"sent": success, "topics": topics}


@router.get("/reminders/logs/{student_id}")
def get_reminder_logs(student_id: int, db: Session = Depends(get_db)):
    """Get reminder send history for a student."""
    logs = db.query(ReminderLog).filter(
        ReminderLog.student_id == student_id
    ).order_by(ReminderLog.sent_at.desc()).limit(20).all()

    return [
        {
            "phone": l.phone,
            "message": l.message[:80],
            "status": l.status,
            "sent_at": l.sent_at.isoformat() if l.sent_at else None
        }
        for l in logs
    ]


# ═══════════════════════════════════════════════════════
#  FEATURE 3 — OPEN DISCUSSIONS (STUDENT FORUM)
# ═══════════════════════════════════════════════════════

@router.get("/discussions")
def list_discussions(
    exam_tag: Optional[str] = None,
    topic_tag: Optional[str] = None,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """Get all discussion posts, optionally filtered by exam or topic."""
    q = db.query(DiscussionPost)
    if exam_tag:
        q = q.filter(DiscussionPost.exam_tag == exam_tag)
    if topic_tag:
        q = q.filter(DiscussionPost.topic_tag.ilike(f"%{topic_tag}%"))

    posts = q.order_by(DiscussionPost.created_at.desc()).limit(limit).all()

    return [
        {
            "id": p.id,
            "student_id": p.student_id,
            "title": p.title,
            "content": p.content[:300],
            "topic_tag": p.topic_tag,
            "exam_tag": p.exam_tag,
            "upvotes": p.upvotes,
            "is_resolved": p.is_resolved,
            "reply_count": len(p.replies),
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in posts
    ]


@router.post("/discussions")
def create_post(
    student_id: int,
    title: str,
    content: str,
    topic_tag: Optional[str] = None,
    exam_tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new discussion post."""
    student = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    post = DiscussionPost(
        student_id=student_id,
        title=title,
        content=content,
        topic_tag=topic_tag,
        exam_tag=exam_tag or student.exam_type,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"id": post.id, "title": post.title, "message": "Post created!"}


@router.get("/discussions/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a single discussion post with all replies."""
    post = db.query(DiscussionPost).filter(DiscussionPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "id": post.id,
        "student_id": post.student_id,
        "title": post.title,
        "content": post.content,
        "topic_tag": post.topic_tag,
        "exam_tag": post.exam_tag,
        "upvotes": post.upvotes,
        "is_resolved": post.is_resolved,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "replies": [
            {
                "id": r.id,
                "student_id": r.student_id,
                "content": r.content,
                "upvotes": r.upvotes,
                "is_ai_reply": r.is_ai_reply,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in sorted(post.replies, key=lambda x: x.created_at)
        ]
    }


@router.post("/discussions/{post_id}/reply")
def add_reply(
    post_id: int,
    student_id: int,
    content: str,
    db: Session = Depends(get_db)
):
    """Add a human reply to a post."""
    post = db.query(DiscussionPost).filter(DiscussionPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    reply = DiscussionReply(
        post_id=post_id,
        student_id=student_id,
        content=content,
        is_ai_reply=False
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)

    # Notify original poster if they have WhatsApp reminders configured
    if post.student_id != student_id:
        setting = db.query(ReminderSetting).filter(
            ReminderSetting.student_id == post.student_id,
            ReminderSetting.is_active == True
        ).first()
        if setting:
            wa.send_discussion_reply(setting.phone_number, f"Student {post.student_id}", post.title)

    return {"id": reply.id, "message": "Reply posted!"}


@router.post("/discussions/{post_id}/ai-reply")
def add_ai_reply(post_id: int, student_id: int, db: Session = Depends(get_db)):
    """Ask AI to answer a discussion post."""
    post = db.query(DiscussionPost).filter(DiscussionPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    student = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
    profile_data = {"exam_type": student.exam_type if student else ""} if student else {}

    ai_answer = llm_new.generate_ai_discussion_reply(
        profile_data, post.title, post.content, post.exam_tag
    )

    reply = DiscussionReply(
        post_id=post_id,
        student_id=student_id,
        content=ai_answer,
        is_ai_reply=True
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)

    return {"id": reply.id, "content": ai_answer, "is_ai_reply": True}


@router.post("/discussions/{post_id}/upvote")
def upvote_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(DiscussionPost).filter(DiscussionPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.upvotes = (post.upvotes or 0) + 1
    db.commit()
    return {"upvotes": post.upvotes}


@router.post("/discussions/replies/{reply_id}/upvote")
def upvote_reply(reply_id: int, db: Session = Depends(get_db)):
    reply = db.query(DiscussionReply).filter(DiscussionReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    reply.upvotes = (reply.upvotes or 0) + 1
    db.commit()
    return {"upvotes": reply.upvotes}


@router.post("/discussions/{post_id}/resolve")
def mark_resolved(post_id: int, db: Session = Depends(get_db)):
    post = db.query(DiscussionPost).filter(DiscussionPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.is_resolved = True
    db.commit()
    return {"message": "Marked as resolved ✅"}
