import json
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import engine, Base, get_db
import models_enhanced as models
import schemas_enhanced as schemas
import llm_enhanced as llm
from datetime import datetime, timedelta
from typing import List

# Create ALL database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Exam Coach API")

@app.get("/")
def read_root():
    return {"message": "Welcome to Exam Coach API"}

# --- EXISTING ENDPOINTS ---

@app.post("/api/profile", response_model=schemas.StudentProfile)
def create_profile(profile: schemas.StudentProfileCreate, db: Session = Depends(get_db)):
    db_profile = models.StudentProfile(**profile.model_dump())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@app.post("/api/analyze-test", response_model=schemas.WeakTopicsAnalysis)
def analyze_mock_test(mock_test: schemas.MockTestCreate, db: Session = Depends(get_db)):
    student = db.query(models.StudentProfile).filter(models.StudentProfile.id == mock_test.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student Profile not found")
        
    profile_data = {
        "exam_type": student.exam_type,
        "target_marks_rank": student.target_marks_rank
    }
    
    try:
        weak_topics = llm.analyze_weak_topics(profile_data, mock_test.test_result_text)
        
        db_mock_test = models.MockTest(
            student_id=mock_test.student_id,
            test_result_text=mock_test.test_result_text,
            weak_topics_json=json.dumps(weak_topics)
        )
        db.add(db_mock_test)
        db.commit()
        
        return {"weak_topics": weak_topics}
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=str(traceback.format_exc()))

@app.post("/api/revision-plan", response_model=schemas.RevisionPlanResponse)
def generate_revision_plan(study_hours: schemas.StudyHours, db: Session = Depends(get_db)):
    student = db.query(models.StudentProfile).filter(models.StudentProfile.id == study_hours.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student Profile not found")
        
    profile_data = {
        "exam_type": student.exam_type,
        "target_marks_rank": student.target_marks_rank
    }
    
    latest_mock_test = db.query(models.MockTest)\
        .filter(models.MockTest.student_id == study_hours.student_id)\
        .order_by(models.MockTest.id.desc())\
        .first()
        
    if not latest_mock_test:
        raise HTTPException(status_code=400, detail="No mock test found to analyze. Please submit a mock test first.")
        
    weak_topics = json.loads(latest_mock_test.weak_topics_json)
    
    plan_text = llm.generate_revision_plan(
        profile_data, 
        weak_topics, 
        study_hours.weekday_hours, 
        study_hours.weekend_hours
    )
    
    db_plan = models.RevisionPlan(
        student_id=study_hours.student_id,
        weekday_hours=study_hours.weekday_hours,
        weekend_hours=study_hours.weekend_hours,
        plan_text=plan_text
    )
    db.add(db_plan)
    db.commit()
    
    return {"plan_text": plan_text}

# --- NEW: FREE RESOURCES ENDPOINTS ---

@app.post("/api/resources", response_model=schemas.FreeResource)
def add_free_resource(resource: schemas.FreeResourceCreate, db: Session = Depends(get_db)):
    """Add a free learning resource"""
    db_resource = models.FreeResource(**resource.model_dump())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

@app.get("/api/resources/topic/{topic}")
def get_resources_by_topic(topic: str, exam_type: str = "General", db: Session = Depends(get_db)) -> List[schemas.FreeResource]:
    """Get free resources for a specific topic"""
    query = db.query(models.FreeResource).filter(models.FreeResource.topic.ilike(f"%{topic}%"))
    if exam_type:
        query = query.filter(models.FreeResource.exam_type == exam_type)
    resources = query.order_by(models.FreeResource.difficulty_level).all()
    
    if not resources:
        # LLM auto-generation for open resources
        profile_data = {"exam_type": exam_type}
        try:
            new_resources = llm.find_open_resources(profile_data, topic)
            for nr in new_resources:
                db_res = models.FreeResource(**nr)
                db.add(db_res)
            db.commit()
            resources = db.query(models.FreeResource).filter(models.FreeResource.topic.ilike(f"%{topic}%")).all()
        except Exception as e:
            print("Failed to auto-generate resources:", e)
            
    return resources

@app.post("/api/resources/{resource_id}/like")
def like_resource(resource_id: int, db: Session = Depends(get_db)):
    """Like a resource to increase its popularity"""
    resource = db.query(models.FreeResource).filter(models.FreeResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    resource.likes = (resource.likes or 0) + 1
    db.commit()
    db.refresh(resource)
    return {"likes": resource.likes}

@app.get("/api/resources/exam/{exam_type}")
def get_all_resources_by_exam(exam_type: str, db: Session = Depends(get_db)) -> List[schemas.FreeResource]:
    """Get all resources for an exam type"""
    resources = db.query(models.FreeResource).filter(
        models.FreeResource.exam_type == exam_type
    ).all()
    return resources

# --- NEW: PROGRESS TRACKING ENDPOINTS ---

@app.post("/api/progress", response_model=schemas.ProgressTracking)
def track_progress(progress: schemas.ProgressTrackingCreate, db: Session = Depends(get_db)):
    """Record student progress on a topic"""
    student = db.query(models.StudentProfile).filter(models.StudentProfile.id == progress.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db_progress = models.ProgressTracking(**progress.model_dump())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

@app.put("/api/progress/{progress_id}", response_model=schemas.ProgressTracking)
def update_progress(progress_id: int, progress_update: schemas.ProgressTrackingUpdate, db: Session = Depends(get_db)):
    """Update student progress"""
    db_progress = db.query(models.ProgressTracking).filter(models.ProgressTracking.id == progress_id).first()
    if not db_progress:
        raise HTTPException(status_code=404, detail="Progress record not found")
    
    update_data = progress_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_progress, field, value)
    
    db.commit()
    db.refresh(db_progress)
    return db_progress

@app.get("/api/progress/student/{student_id}")
def get_student_progress(student_id: int, db: Session = Depends(get_db)) -> List[schemas.ProgressTracking]:
    """Get all progress records for a student"""
    student = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    progress = db.query(models.ProgressTracking).filter(
        models.ProgressTracking.student_id == student_id
    ).all()
    return progress

# --- NEW: RECOMMENDATION ENDPOINT (Resources with Progress) ---

@app.get("/api/recommendations/{student_id}/{topic}")
def get_topic_recommendations(student_id: int, topic: str, db: Session = Depends(get_db)):
    """Get recommended resources and progress for a topic"""
    student = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get resources for topic
    resources = db.query(models.FreeResource).filter(
        models.FreeResource.topic.ilike(f"%{topic}%"),
        models.FreeResource.exam_type == student.exam_type
    ).order_by(models.FreeResource.difficulty_level).all()
    
    # Get student's progress on this topic
    progress = db.query(models.ProgressTracking).filter(
        models.ProgressTracking.student_id == student_id,
        models.ProgressTracking.topic.ilike(f"%{topic}%")
    ).order_by(models.ProgressTracking.study_date.desc()).first()
    
    return {
        "topic": topic,
        "resources": resources,
        "student_progress": progress,
        "status": progress.status if progress else "pending"
    }

# --- NEW: DASHBOARD ENDPOINT ---

@app.get("/api/dashboard/{student_id}")
def get_student_dashboard(student_id: int, db: Session = Depends(get_db)):
    """Get comprehensive student dashboard with stats and topics"""
    student = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get latest weak topics
    latest_test = db.query(models.MockTest).filter(
        models.MockTest.student_id == student_id
    ).order_by(models.MockTest.id.desc()).first()
    
    weak_topics = []
    if latest_test:
        weak_topics = json.loads(latest_test.weak_topics_json)
    
    # Get progress stats
    all_progress = db.query(models.ProgressTracking).filter(
        models.ProgressTracking.student_id == student_id
    ).all()
    
    total_topics = len(set(p.topic for p in all_progress))
    topics_completed = len([p for p in all_progress if p.status in ["completed", "mastered"]])
    topics_in_progress = len([p for p in all_progress if p.status == "in_progress"])
    
    total_minutes = sum(p.time_spent_minutes for p in all_progress)
    total_hours = total_minutes / 60 if total_minutes else 0
    
    avg_score = None
    scores = [p.performance_score for p in all_progress if p.performance_score]
    if scores:
        avg_score = sum(scores) / len(scores)
    
    progress_pct = (topics_completed / total_topics * 100) if total_topics > 0 else 0
    
    # Get topic details
    topic_details = {}
    for progress in all_progress:
        if progress.topic not in topic_details:
            # Get resources for this topic
            resources = db.query(models.FreeResource).filter(
                models.FreeResource.topic.ilike(f"%{progress.topic}%"),
                models.FreeResource.exam_type == student.exam_type
            ).all()
            
            topic_details[progress.topic] = {
                "topic": progress.topic,
                "status": progress.status,
                "progress_percentage": 100.0 if progress.status == "mastered" else (75.0 if progress.status == "completed" else (50.0 if progress.status == "in_progress" else 0)),
                "performance_score": progress.performance_score,
                "last_studied": progress.study_date,
                "resources_count": len(resources),
                "free_resources": resources
            }
    
    # Recent chats
    recent_chats = db.query(models.ChatHistory).filter(
        models.ChatHistory.student_id == student_id
    ).order_by(models.ChatHistory.created_at.desc()).limit(5).all()
    
    # --- MOCK ANALYTICS DATA (7 Demo Tests, Error Analysis, Charts) ---
    import random
    from datetime import timedelta
    
    # Generate 7 Demo Tests for Progress Chart
    demo_tests = []
    base_date = datetime.now() - timedelta(days=7)
    base_score = 45 
    for i in range(1, 8):
        score = min(100, base_score + (i * 6) + random.randint(-4, 5))
        demo_tests.append({
            "Test": f"Test {i}",
            "Date": (base_date + timedelta(days=i)).strftime("%Y-%m-%d"),
            "Score": score
        })
        
    # Generate Weak Questions Breakdown
    weak_questions = [
        {"subject": "Physics", "topic": "Thermodynamics", "questions_missed": 12},
        {"subject": "Physics", "topic": "Optics", "questions_missed": 8},
        {"subject": "Chemistry", "topic": "Organic Chemistry", "questions_missed": 15},
        {"subject": "Chemistry", "topic": "Chemical Kinetics", "questions_missed": 9},
        {"subject": "Math", "topic": "Calculus", "questions_missed": 18},
        {"subject": "Math", "topic": "Algebra", "questions_missed": 7}
    ]
    
    analytics = {
        "demo_tests": demo_tests,
        "weak_questions": weak_questions,
        "error_types": {
            "Conceptual Gap": 40,
            "Calculation Error": 30,
            "Time Pressure": 20,
            "Silly / Read Error": 10
        },
        "accuracy": {
            "Correct": 62,
            "Incorrect": 38
        }
    }
    
    return {
        "profile": {
            "id": student.id,
            "exam_type": student.exam_type,
            "target_marks_rank": student.target_marks_rank,
            "created_at": student.created_at,
            "updated_at": student.updated_at
        },
        "stats": {
            "total_topics": total_topics,
            "topics_completed": topics_completed,
            "topics_in_progress": topics_in_progress,
            "overall_progress_percentage": progress_pct,
            "average_performance_score": avg_score,
            "total_study_hours": round(total_hours, 2),
            "weak_topics": weak_topics,
            "recent_chat_count": len(recent_chats)
        },
        "topics": list(topic_details.values()),
        "recent_chats": recent_chats,
        "analytics": analytics
    }

# --- NEW: AI CHATBOT Q&A ENDPOINTS ---

@app.post("/api/chat/ask")
def ask_question(chat: schemas.ChatMessageCreate, db: Session = Depends(get_db)):
    """Ask AI a question about exam topics"""
    student = db.query(models.StudentProfile).filter(models.StudentProfile.id == chat.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get AI answer using LLM
    profile_data = {
        "exam_type": student.exam_type,
        "target_marks_rank": student.target_marks_rank
    }
    
    answer = llm.answer_question(profile_data, chat.question, chat.topic)
    
    # Store chat history
    db_chat = models.ChatHistory(
        student_id=chat.student_id,
        question=chat.question,
        answer=answer,
        topic=chat.topic
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    
    return {
        "id": db_chat.id,
        "question": db_chat.question,
        "answer": db_chat.answer,
        "topic": db_chat.topic,
        "created_at": db_chat.created_at
    }

@app.get("/api/chat/history/{student_id}")
def get_chat_history(student_id: int, limit: int = 20, db: Session = Depends(get_db)):
    """Get chat history for a student"""
    student = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    chats = db.query(models.ChatHistory).filter(
        models.ChatHistory.student_id == student_id
    ).order_by(models.ChatHistory.created_at.desc()).limit(limit).all()
    
    return chats

@app.post("/api/chat/feedback")
def provide_chat_feedback(feedback: schemas.ChatFeedback, db: Session = Depends(get_db)):
    """Provide feedback on AI answer (helpful/not helpful)"""
    chat = db.query(models.ChatHistory).filter(models.ChatHistory.id == feedback.chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat.helpful = feedback.helpful
    db.commit()
    db.refresh(chat)
    
    return {"message": "Feedback recorded successfully"}
