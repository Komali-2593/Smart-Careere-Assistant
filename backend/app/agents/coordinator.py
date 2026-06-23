import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from .. import models
from .resume import ResumeAgent
from .skill_gap import SkillGapAgent
from .roadmap import RoadmapAgent
from .interview import InterviewAgent

logger = logging.getLogger(__name__)

class CoordinatorAgent:
    def __init__(self):
        self.resume_agent = ResumeAgent()
        self.skill_gap_agent = SkillGapAgent()
        self.roadmap_agent = RoadmapAgent()
        self.interview_agent = InterviewAgent()
        logger.info("CoordinatorAgent initialized with sub-agents.")

    def process_new_resume(self, db: Session, raw_text: str, filename: str = None) -> models.UserResume:
        """
        Parses resume raw text and commits the parsed profile to the DB.
        """
        logger.info(f"Coordinator: Parsing new resume {filename or 'text input'}")
        parsed_profile = self.resume_agent.parse(raw_text)
        
        db_resume = models.UserResume(
            filename=filename,
            raw_text=raw_text,
            parsed_profile=parsed_profile
        )
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        return db_resume

    def perform_career_analysis(self, db: Session, resume_id: int, target_role: str) -> models.CareerAnalysis:
        """
        Analyzes skill gaps and generates recommendations for a target role.
        """
        logger.info(f"Coordinator: Analyzing career path for resume_id {resume_id} and role '{target_role}'")
        
        # 1. Fetch resume
        resume = db.query(models.UserResume).filter(models.UserResume.id == resume_id).first()
        if not resume:
            raise ValueError(f"Resume with ID {resume_id} not found.")

        # 2. Extract current skills
        profile = resume.parsed_profile or {}
        current_skills = profile.get("skills", [])

        # 3. Analyze skill gaps
        analysis_result = self.skill_gap_agent.analyze(db, current_skills, target_role)

        # 4. Save analysis to DB
        db_analysis = models.CareerAnalysis(
            resume_id=resume_id,
            target_role=target_role,
            overall_fit_score=analysis_result["overall_fit_score"],
            current_skills=analysis_result["current_skills"],
            required_skills=analysis_result["required_skills"],
            skill_gaps=analysis_result["skill_gaps"],
            recommendations=analysis_result["recommendations"]
        )
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)

        # 5. Automatically trigger roadmap generation
        self.generate_roadmap(db, db_analysis.id)

        return db_analysis

    def generate_roadmap(self, db: Session, analysis_id: int) -> models.LearningRoadmap:
        """
        Generates a structured learning roadmap from an analysis.
        """
        logger.info(f"Coordinator: Generating learning roadmap for analysis_id {analysis_id}")
        
        analysis = db.query(models.CareerAnalysis).filter(models.CareerAnalysis.id == analysis_id).first()
        if not analysis:
            raise ValueError(f"Analysis with ID {analysis_id} not found.")

        # If a roadmap already exists, return it
        existing_roadmap = db.query(models.LearningRoadmap).filter(models.LearningRoadmap.analysis_id == analysis_id).first()
        if existing_roadmap:
            return existing_roadmap

        # Generate roadmap using Roadmap Agent
        roadmap_data = self.roadmap_agent.generate(db, analysis.skill_gaps or [], analysis.target_role, analysis.overall_fit_score)

        # Save to DB
        db_roadmap = models.LearningRoadmap(
            analysis_id=analysis_id,
            steps=roadmap_data["steps"],
            estimated_duration=roadmap_data["estimated_duration"]
        )
        db.add(db_roadmap)
        db.commit()
        db.refresh(db_roadmap)
        return db_roadmap

    def get_interview_response(self, db: Session, session_id: int, user_message: str) -> models.InterviewMessage:
        """
        Records the candidate message, queries the Interview Agent for a coach response, and records it.
        """
        session = db.query(models.InterviewSession).filter(models.InterviewSession.id == session_id).first()
        if not session:
            raise ValueError(f"Interview session {session_id} not found.")

        # Save Candidate message
        candidate_msg = models.InterviewMessage(
            session_id=session_id,
            sender="candidate",
            message=user_message
        )
        db.add(candidate_msg)
        db.commit()

        # Fetch entire chat history for agent context
        chat_history = (
            db.query(models.InterviewMessage)
            .filter(models.InterviewMessage.session_id == session_id)
            .order_by(models.InterviewMessage.created_at.asc())
            .all()
        )
        history_list = [{"sender": m.sender, "message": m.message} for m in chat_history]

        # Fetch resume profile if attached
        profile = {}
        if session.resume_id:
            resume = db.query(models.UserResume).filter(models.UserResume.id == session.resume_id).first()
            if resume and resume.parsed_profile:
                profile = resume.parsed_profile

        # Ask Interview Agent for coach response
        coach_text = self.interview_agent.generate_next_message(history_list, session.target_role, profile)

        # Save Coach response
        coach_msg = models.InterviewMessage(
            session_id=session_id,
            sender="coach",
            message=coach_text
        )
        db.add(coach_msg)
        db.commit()
        db.refresh(coach_msg)

        return coach_msg

    def finalize_interview(self, db: Session, session_id: int) -> models.InterviewSession:
        """
        Evaluates the interview session, generates feedback and stores it, marking session as completed.
        """
        session = db.query(models.InterviewSession).filter(models.InterviewSession.id == session_id).first()
        if not session:
            raise ValueError(f"Interview session {session_id} not found.")

        chat_history = (
            db.query(models.InterviewMessage)
            .filter(models.InterviewMessage.session_id == session_id)
            .order_by(models.InterviewMessage.created_at.asc())
            .all()
        )
        history_list = [{"sender": m.sender, "message": m.message} for m in chat_history]

        feedback_report = self.interview_agent.generate_feedback(history_list, session.target_role)

        session.status = "completed"
        session.feedback = feedback_report
        db.commit()
        db.refresh(session)
        return session
