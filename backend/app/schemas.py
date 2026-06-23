from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

# Resume Schemas
class ResumeTextInput(BaseModel):
    text: str = Field(..., min_length=10, description="Raw text content of the resume")

class ParsedProfileSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    summary: Optional[str] = None

class ResumeResponse(BaseModel):
    id: int
    filename: Optional[str]
    raw_text: str
    parsed_profile: Optional[ParsedProfileSchema]
    created_at: datetime

    class Config:
        from_attributes = True

# Analysis Schemas
class AnalysisRequest(BaseModel):
    resume_id: int
    target_role: str = Field(..., min_length=2, description="Target job title / career role")

class AnalysisResponse(BaseModel):
    id: int
    resume_id: int
    target_role: str
    overall_fit_score: int
    current_skills: List[str]
    required_skills: List[str]
    skill_gaps: List[str]
    recommendations: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Roadmap Schemas
class RoadmapStepSchema(BaseModel):
    step_number: int
    topic: str
    duration: str
    description: str
    skills_learned: List[str]

class RoadmapResponse(BaseModel):
    id: int
    analysis_id: int
    steps: List[RoadmapStepSchema]
    estimated_duration: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Interview Schemas
class InterviewSessionCreate(BaseModel):
    target_role: str = Field(..., min_length=2)
    resume_id: Optional[int] = None

class InterviewMessageCreate(BaseModel):
    message: str = Field(..., min_length=1)

class InterviewMessageResponse(BaseModel):
    id: int
    session_id: int
    sender: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

class InterviewSessionResponse(BaseModel):
    id: int
    target_role: str
    resume_id: Optional[int]
    status: str
    feedback: Optional[str]
    created_at: datetime
    messages: List[InterviewMessageResponse] = []

    class Config:
        from_attributes = True

class InterviewFeedbackResponse(BaseModel):
    status: str
    feedback: str

    class Config:
        from_attributes = True

class CareerRoleResponse(BaseModel):
    id: int
    name: str
    description: str
    required_skills: List[str]
    beginner_roadmap: List[Dict[str, Any]]
    intermediate_roadmap: List[Dict[str, Any]]
    advanced_roadmap: List[Dict[str, Any]]

    class Config:
        from_attributes = True


class InternshipResponse(BaseModel):
    id: int
    title: str
    company: str
    location: Optional[str] = None
    link: str
    description: Optional[str] = None
    role_category: str

    class Config:
        from_attributes = True


class ResourceResponse(BaseModel):
    id: int
    title: str
    type: str
    link: str
    skill: str

    class Config:
        from_attributes = True

