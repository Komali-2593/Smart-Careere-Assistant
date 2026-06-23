from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/internships", tags=["Internships"])

@router.get("/", response_model=List[schemas.InternshipResponse])
def get_internships(role: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Retrieve internships, optionally filtered by matching career role category, title, or description.
    """
    try:
        query = db.query(models.Internship)
        if role:
            role_clean = role.strip()
            # 1. Full phrase case-insensitive matching
            full_match = query.filter(
                or_(
                    models.Internship.role_category.ilike(f"%{role_clean}%"),
                    models.Internship.title.ilike(f"%{role_clean}%"),
                    models.Internship.description.ilike(f"%{role_clean}%")
                )
            ).all()
            if full_match:
                return full_match
            
            # 2. Keyword matching if full phrase matched nothing
            words = [w.strip() for w in role_clean.split() if len(w.strip()) > 2]
            if words:
                conditions = []
                for w in words:
                    conditions.extend([
                        models.Internship.role_category.ilike(f"%{w}%"),
                        models.Internship.title.ilike(f"%{w}%"),
                        models.Internship.description.ilike(f"%{w}%")
                    ])
                keyword_match = query.filter(or_(*conditions)).all()
                if keyword_match:
                    return keyword_match
        
        # Fallback: if no matches or no role query provided, return all internships
        return query.all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
