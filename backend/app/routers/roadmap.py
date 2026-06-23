from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..agents import CoordinatorAgent

router = APIRouter(prefix="/api/roadmap", tags=["Learning Roadmap"])
coordinator = CoordinatorAgent()

@router.get("/analysis/{analysis_id}", response_model=schemas.RoadmapResponse)
def get_roadmap_by_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the customized learning roadmap for a career analysis report.
    """
    # Check if analysis exists
    analysis = db.query(models.CareerAnalysis).filter(models.CareerAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis report not found.")

    try:
        # Coordinator handles loading or lazy generating the roadmap
        db_roadmap = coordinator.generate_roadmap(db, analysis_id=analysis_id)
        return db_roadmap
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving roadmap: {str(e)}")
