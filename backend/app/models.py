import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from .database import Base

class UserResume(Base):
    __tablename__ = "user_resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=True)
    raw_text = Column(Text, nullable=False)
    parsed_profile = Column(JSON, nullable=True)  # JSON structure containing: name, email, skills, experience, education, summary
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analyses = relationship("CareerAnalysis", back_populates="resume", cascade="all, delete-orphan")

class CareerAnalysis(Base):
    __tablename__ = "career_analyses"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("user_resumes.id"), nullable=False)
    target_role = Column(String, nullable=False)
    overall_fit_score = Column(Integer, default=0)
    current_skills = Column(JSON, nullable=True)   # List of strings
    required_skills = Column(JSON, nullable=True)  # List of strings
    skill_gaps = Column(JSON, nullable=True)       # List of strings (missing)
    recommendations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    resume = relationship("UserResume", back_populates="analyses")
    roadmaps = relationship("LearningRoadmap", back_populates="analysis", cascade="all, delete-orphan")

class LearningRoadmap(Base):
    __tablename__ = "learning_roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("career_analyses.id"), nullable=False)
    steps = Column(JSON, nullable=False)  # List of dicts: {step_number, topic, duration, description, skills_learned}
    estimated_duration = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analysis = relationship("CareerAnalysis", back_populates="roadmaps")

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    target_role = Column(String, nullable=False)
    resume_id = Column(Integer, ForeignKey("user_resumes.id"), nullable=True)
    status = Column(String, default="active")  # active, completed
    feedback = Column(Text, nullable=True)      # Overall session assessment feedback
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    messages = relationship("InterviewMessage", back_populates="session", cascade="all, delete-orphan")

class InterviewMessage(Base):
    __tablename__ = "interview_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    sender = Column(String, nullable=False)  # 'candidate' (user) or 'coach' (AI)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("InterviewSession", back_populates="messages")

class CareerRole(Base):
    __tablename__ = "career_roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, nullable=False)      # List of strings
    beginner_roadmap = Column(JSON, nullable=False)     # List of steps (JSON)
    intermediate_roadmap = Column(JSON, nullable=False)  # List of steps (JSON)
    advanced_roadmap = Column(JSON, nullable=False)      # List of steps (JSON)


class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    link = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    role_category = Column(String, nullable=False)  # e.g., 'Software Engineer (Generalist)', 'Frontend Developer'


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)           # 'youtube', 'documentation', 'practice'
    link = Column(String, nullable=False)
    skill = Column(String, nullable=False)          # Associated skill name (e.g. 'Python', 'React')

