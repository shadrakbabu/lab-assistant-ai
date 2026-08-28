from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base
from pydantic import BaseModel

Base = declarative_base()


class LabManualDB(Base):
    __tablename__ = "lab_manuals"

    id = Column(String(50), primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_kb = Column(Integer, default=0)
    page_count = Column(Integer, default=0)
    subject = Column(String(100), default="General Science")
    extracted_text = Column(Text, nullable=True)
    num_experiments = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    experiments = relationship("ExperimentDB", back_populates="manual", cascade="all, delete-orphan")


class ExperimentDB(Base):
    __tablename__ = "experiments"

    id = Column(String(100), primary_key=True, index=True)
    manual_id = Column(String(50), ForeignKey("lab_manuals.id", ondelete="CASCADE"), nullable=False)
    experiment_number = Column(Integer, nullable=False)
    title = Column(String(300), nullable=False)
    aim = Column(Text, nullable=True)
    theory = Column(Text, nullable=True)
    equipment = Column(JSON, default=list)  # List[str]
    procedure = Column(JSON, default=list)  # List[str] steps
    observations = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    safety = Column(JSON, default=list)     # List[str]
    troubleshooting = Column(Text, nullable=True)
    subject = Column(String(100), default="General Science")
    raw_content = Column(Text, nullable=True)

    manual = relationship("LabManualDB", back_populates="experiments")


# --- Pydantic Schemas ---

class ExperimentBase(BaseModel):
    experiment_number: int
    title: str
    aim: Optional[str] = ""
    theory: Optional[str] = ""
    equipment: List[str] = []
    procedure: List[str] = []
    observations: Optional[str] = ""
    result: Optional[str] = ""
    safety: List[str] = []
    troubleshooting: Optional[str] = ""
    subject: Optional[str] = "General Science"


class ExperimentResponse(ExperimentBase):
    id: str
    manual_id: str

    class Config:
        from_attributes = True


class LabManualResponse(BaseModel):
    id: str
    filename: str
    file_size_kb: int
    page_count: int
    subject: str
    num_experiments: int
    created_at: datetime
    experiments: List[ExperimentResponse] = []

    class Config:
        from_attributes = True


class ManualSummaryResponse(BaseModel):
    id: str
    filename: str
    file_size_kb: int
    page_count: int
    subject: str
    num_experiments: int
    created_at: datetime

    class Config:
        from_attributes = True
