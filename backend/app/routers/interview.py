from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..agents import CoordinatorAgent

router = APIRouter(prefix="/api/interview", tags=["Interview Coach"])
coordinator = CoordinatorAgent()

@router.post("/session", response_model=schemas.InterviewSessionResponse)
def start_interview_session(payload: schemas.InterviewSessionCreate, db: Session = Depends(get_db)):
    """
    Start a new mock interview session and generate the initial welcoming prompt.
    """
    # Verify resume exists if provided
    if payload.resume_id:
        resume = db.query(models.UserResume).filter(models.UserResume.id == payload.resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Attached resume not found.")

    try:
        # 1. Create session
        db_session = models.InterviewSession(
            target_role=payload.target_role,
            resume_id=payload.resume_id,
            status="active"
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        # 2. Get welcoming question from InterviewAgent
        # Initial call has empty chat history
        profile = {}
        if payload.resume_id and resume.parsed_profile:
            profile = resume.parsed_profile

        initial_message = coordinator.interview_agent.generate_next_message(
            chat_history=[],
            target_role=payload.target_role,
            parsed_profile=profile
        )

        # 3. Save initial coach message
        db_msg = models.InterviewMessage(
            session_id=db_session.id,
            sender="coach",
            message=initial_message
        )
        db.add(db_msg)
        db.commit()
        
        # Reload session to include the initial message in relation
        db.refresh(db_session)
        return db_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")

@router.get("/session/{session_id}", response_model=schemas.InterviewSessionResponse)
def get_interview_session(session_id: int, db: Session = Depends(get_db)):
    """
    Retrieve interview session status and message log.
    """
    session = db.query(models.InterviewSession).filter(models.InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    return session

@router.post("/session/{session_id}/message", response_model=schemas.InterviewMessageResponse)
def send_interview_message(session_id: int, payload: schemas.InterviewMessageCreate, db: Session = Depends(get_db)):
    """
    Submit candidate response and receive next coach question/prompt.
    """
    session = db.query(models.InterviewSession).filter(models.InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    
    if session.status == "completed":
        raise HTTPException(status_code=400, detail="This mock interview session is already completed.")

    try:
        # Coordinator saves user message and returns coach response
        coach_response_msg = coordinator.get_interview_response(
            db, session_id=session_id, user_message=payload.message
        )
        return coach_response_msg
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.post("/session/{session_id}/complete", response_model=schemas.InterviewFeedbackResponse)
def complete_interview_session(session_id: int, db: Session = Depends(get_db)):
    """
    Conclude mock interview session and generate final performance evaluation.
    """
    session = db.query(models.InterviewSession).filter(models.InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    try:
        updated_session = coordinator.finalize_interview(db, session_id=session_id)
        return {
            "status": updated_session.status,
            "feedback": updated_session.feedback
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate session: {str(e)}")
