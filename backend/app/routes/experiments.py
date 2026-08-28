from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.manual import ExperimentDB, ExperimentResponse

router = APIRouter(prefix="/experiments", tags=["Experiments"])


@router.get("/manual/{manual_id}", response_model=List[ExperimentResponse])
def get_experiments_by_manual(manual_id: str, db: Session = Depends(get_db)):
    experiments = db.query(ExperimentDB).filter(ExperimentDB.manual_id == manual_id).order_by(ExperimentDB.experiment_number.asc()).all()
    return experiments


@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment_details(experiment_id: str, db: Session = Depends(get_db)):
    exp = db.query(ExperimentDB).filter(ExperimentDB.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail=f"Experiment '{experiment_id}' not found.")
    return exp
