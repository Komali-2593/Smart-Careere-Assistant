from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/resources", tags=["Learning Resources"])

@router.get("/", response_model=List[schemas.ResourceResponse])
def get_resources(skills: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Retrieve learning resources, optionally filtered by matching skills list (comma-separated).
    If no matches are found, returns a core fallback list of general development resources.
    """
    try:
        query = db.query(models.Resource)
        if skills:
            skills_list = [s.strip() for s in skills.split(",") if s.strip()]
            if skills_list:
                # Apply case-insensitive OR conditions for all skills in list
                conditions = [models.Resource.skill.ilike(f"%{s}%") for s in skills_list]
                matched = query.filter(or_(*conditions)).all()
                if matched:
                    return matched
        
        # Fallback: if no skills matched or no skills provided, return general core resources
        core_skills = ["Python", "JavaScript", "React", "Git", "System Design", "HTML", "CSS"]
        return query.filter(models.Resource.skill.in_(core_skills)).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
