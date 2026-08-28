import uuid
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models.manual import LabManualDB, ExperimentDB, LabManualResponse, ManualSummaryResponse
from backend.app.parsers.pdf_extractor import PDFExtractor
from backend.app.parsers.experiment_parser import ExperimentParser
from backend.app.parsers.subject_classifier import SubjectClassifier
from backend.app.rag.text_splitter import TextSplitter
from backend.app.rag.vector_store import vector_store

router = APIRouter(prefix="/manuals", tags=["Manuals"])
pdf_extractor = PDFExtractor(max_file_size_mb=settings.MAX_FILE_SIZE_MB)
exp_parser = ExperimentParser()
text_splitter = TextSplitter(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)


@router.post("/upload", response_model=LabManualResponse)
async def upload_lab_manual(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    manual_id = f"man_{uuid.uuid4().hex[:10]}"
    file_path = settings.DATA_DIR / f"{manual_id}_{file.filename}"

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # Extract text from PDF
    extraction_result = pdf_extractor.extract_pdf_data(str(file_path))
    if not extraction_result["success"]:
        raise HTTPException(status_code=400, detail=extraction_result["error"])

    full_text = extraction_result["extracted_text"]
    num_pages = extraction_result["num_pages"]
    file_size_kb = extraction_result["file_size_kb"]

    # Classify subject
    subject = SubjectClassifier.classify(full_text)

    # Parse experiments
    parsed_exps = exp_parser.parse_experiments(full_text)

    # Create manual record in database
    manual_db = LabManualDB(
        id=manual_id,
        filename=file.filename,
        file_path=str(file_path),
        file_size_kb=file_size_kb,
        page_count=num_pages,
        subject=subject,
        extracted_text=full_text,
        num_experiments=len(parsed_exps)
    )
    db.add(manual_db)

    # Add experiments to database
    exp_db_objects = []
    for exp_data in parsed_exps:
        exp_id = f"{manual_id}_exp_{exp_data['experiment_number']}"
        exp_db = ExperimentDB(
            id=exp_id,
            manual_id=manual_id,
            experiment_number=exp_data["experiment_number"],
            title=exp_data["title"],
            aim=exp_data["aim"],
            theory=exp_data["theory"],
            equipment=exp_data["equipment"],
            procedure=exp_data["procedure"],
            observations=exp_data["observations"],
            result=exp_data["result"],
            safety=exp_data["safety"],
            troubleshooting=exp_data["troubleshooting"],
            subject=subject,
            raw_content=exp_data["raw_content"]
        )
        db.add(exp_db)
        exp_db_objects.append(exp_db)

    db.commit()
    db.refresh(manual_db)

    # Build and save FAISS index
    chunks = text_splitter.split_experiments(manual_id, parsed_exps)
    vector_store.build_and_save_index(manual_id, chunks)

    return manual_db


@router.get("", response_model=List[ManualSummaryResponse])
def list_manuals(db: Session = Depends(get_db)):
    return db.query(LabManualDB).order_by(LabManualDB.created_at.desc()).all()


@router.get("/{manual_id}", response_model=LabManualResponse)
def get_manual_details(manual_id: str, db: Session = Depends(get_db)):
    manual = db.query(LabManualDB).filter(LabManualDB.id == manual_id).first()
    if not manual:
        raise HTTPException(status_code=404, detail=f"Manual with ID '{manual_id}' not found.")
    return manual
