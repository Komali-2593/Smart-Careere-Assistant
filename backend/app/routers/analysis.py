from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..agents import CoordinatorAgent

router = APIRouter(prefix="/api/analysis", tags=["Career Analysis"])
coordinator = CoordinatorAgent()

@router.post("", response_model=schemas.AnalysisResponse)
def run_career_analysis(payload: schemas.AnalysisRequest, db: Session = Depends(get_db)):
    """
    Run career analysis and skill gap assessment for a resume against a target role.
    """
    try:
        db_analysis = coordinator.perform_career_analysis(
            db, resume_id=payload.resume_id, target_role=payload.target_role
        )
        return db_analysis
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing analysis: {str(e)}")

@router.get("/{analysis_id}", response_model=schemas.AnalysisResponse)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Fetch details of a specific career analysis by ID.
    """
    analysis = db.query(models.CareerAnalysis).filter(models.CareerAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis report not found.")
    return analysis

@router.get("/resume/{resume_id}", response_model=List[schemas.AnalysisResponse])
def get_analyses_for_resume(resume_id: int, db: Session = Depends(get_db)):
    """
    Fetch all analysis reports corresponding to a resume ID.
    """
    analyses = db.query(models.CareerAnalysis).filter(models.CareerAnalysis.resume_id == resume_id).all()
    return analyses
