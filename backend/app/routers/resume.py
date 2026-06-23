import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import pypdf

from ..database import get_db
from .. import models, schemas
from ..agents import CoordinatorAgent

router = APIRouter(prefix="/api/resume", tags=["Resume"])
coordinator = CoordinatorAgent()

@router.post("/upload", response_model=schemas.ResumeResponse)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a resume file (.pdf or .txt) and parse its contents.
    """
    filename = file.filename
    content_type = file.content_type
    
    file_bytes = await file.read()
    raw_text = ""

    if filename.endswith(".pdf") or content_type == "application/pdf":
        try:
            pdf_stream = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(pdf_stream)
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text() or "")
            raw_text = "\n".join(text_parts).strip()
            if not raw_text:
                raise ValueError("PDF file appears to be empty or contains scanned images only.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF resume: {str(e)}")
    elif filename.endswith(".txt") or content_type == "text/plain":
        try:
            raw_text = file_bytes.decode("utf-8").strip()
        except UnicodeDecodeError:
            try:
                raw_text = file_bytes.decode("latin-1").strip()
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to read TXT file: {str(e)}")
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a PDF or plain text (.txt) file."
        )

    if not raw_text or len(raw_text) < 10:
        raise HTTPException(
            status_code=400,
            detail="Resume content is too short to process."
        )

    try:
        db_resume = coordinator.process_new_resume(db, raw_text=raw_text, filename=filename)
        return db_resume
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing error: {str(e)}")

@router.post("/text", response_model=schemas.ResumeResponse)
def input_resume_text(payload: schemas.ResumeTextInput, db: Session = Depends(get_db)):
    """
    Submit raw resume text directly.
    """
    if not payload.text or len(payload.text.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Resume text is too short to parse."
        )
    
    try:
        db_resume = coordinator.process_new_resume(db, raw_text=payload.text, filename="raw_text_input.txt")
        return db_resume
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing error: {str(e)}")

@router.get("/{resume_id}", response_model=schemas.ResumeResponse)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """
    Fetch a previously parsed resume by ID.
    """
    resume = db.query(models.UserResume).filter(models.UserResume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return resume
