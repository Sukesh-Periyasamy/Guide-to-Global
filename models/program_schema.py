"""
Pydantic models (schemas) for a university program document.

Each document stored in MongoDB represents ONE program at ONE university.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Nested sub-models
# ---------------------------------------------------------------------------


class UniversityInfo(BaseModel):
    name: str
    country: str
    city: str


class ProgramInfo(BaseModel):
    name: str
    degree: str  # e.g. "Masters", "PhD", "Bachelors"
    department: str
    duration: str  # e.g. "2 years"


class AdmissionInfo(BaseModel):
    status: str = "open"  # open | closed | rolling
    intake: str = ""  # e.g. "Fall 2025", "Winter 2026"
    deadline: Optional[str] = None  # ISO date string or human-readable


class IELTSRequirement(BaseModel):
    required: bool = False
    min_score: Optional[float] = None


class TOEFLRequirement(BaseModel):
    required: bool = False
    min_score: Optional[int] = None


class GRERequirement(BaseModel):
    required: bool = False
    recommended: bool = False
    min_score: Optional[int] = None


class DocumentRequirements(BaseModel):
    lor: int = 0          # number of Letters of Recommendation
    sop: bool = False     # Statement of Purpose
    resume: bool = False
    transcript: bool = False


class AdmissionRequirements(BaseModel):
    ielts: IELTSRequirement = Field(default_factory=IELTSRequirement)
    toefl: TOEFLRequirement = Field(default_factory=TOEFLRequirement)
    gre: GRERequirement = Field(default_factory=GRERequirement)
    documents: DocumentRequirements = Field(default_factory=DocumentRequirements)


class FinancialInfo(BaseModel):
    tuition_fee: Optional[str] = None   # e.g. "$15,000/year"
    scholarship_available: bool = False


class ProgramLinks(BaseModel):
    admission_page: Optional[str] = None
    program_page: Optional[str] = None
    apply_link: Optional[str] = None


class RawData(BaseModel):
    requirements_text: Optional[str] = None
    description_text: Optional[str] = None


class Metadata(BaseModel):
    last_scraped: Optional[datetime] = None
    source: Optional[str] = None


# ---------------------------------------------------------------------------
# Top-level document model
# ---------------------------------------------------------------------------


class ProgramDocument(BaseModel):
    """Full program document stored in MongoDB."""

    university: UniversityInfo
    program: ProgramInfo
    admission: AdmissionInfo = Field(default_factory=AdmissionInfo)
    requirements: AdmissionRequirements = Field(default_factory=AdmissionRequirements)
    financial: FinancialInfo = Field(default_factory=FinancialInfo)
    links: ProgramLinks = Field(default_factory=ProgramLinks)
    raw_data: RawData = Field(default_factory=RawData)
    metadata: Metadata = Field(default_factory=Metadata)


class ProgramResponse(ProgramDocument):
    """Response model that includes the MongoDB document id."""

    id: str = Field(..., alias="_id")

    class Config:
        populate_by_name = True
