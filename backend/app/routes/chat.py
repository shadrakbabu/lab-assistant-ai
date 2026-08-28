from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.chat import ChatRequest, ChatResponse
from backend.app.models.manual import ExperimentDB, LabManualDB
from backend.app.rag.qa_engine import qa_engine

router = APIRouter(prefix="/chat", tags=["Grounded AI Chat"])


@router.post("", response_model=ChatResponse)
def grounded_chat(request: ChatRequest, db: Session = Depends(get_db)):
    manual = db.query(LabManualDB).filter(LabManualDB.id == request.manual_id).first()
    if not manual:
        raise HTTPException(status_code=404, detail=f"Lab Manual '{request.manual_id}' not found.")

    exp_context = None
    exp_number = None

    if request.experiment_id:
        exp = db.query(ExperimentDB).filter(ExperimentDB.id == request.experiment_id).first()
        if exp:
            exp_number = exp.experiment_number
            exp_context = {
                "experiment_number": exp.experiment_number,
                "title": exp.title,
                "aim": exp.aim,
                "theory": exp.theory,
                "equipment": exp.equipment,
                "procedure": exp.procedure,
                "safety": exp.safety,
                "troubleshooting": exp.troubleshooting
            }

    response = qa_engine.answer_question(
        manual_id=request.manual_id,
        query=request.query,
        experiment_id=request.experiment_id,
        exp_number=exp_number,
        mode=request.mode or "standard",
        exp_context=exp_context
    )

    return response
