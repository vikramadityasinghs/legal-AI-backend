from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatusEnum(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentSummary(BaseModel):
    case_number: str
    parties: str
    court: str
    document_type: str
    summary: str
    key_legal_issues: List[str]
    confidence: float = 0.0

class ExtractedEvent(BaseModel):
    date: str
    event_type: str
    description: str
    parties_involved: List[str]
    confidence: float
    document_source: Optional[str] = None

class LegalRecommendation(BaseModel):
    category: str
    priority: str  # High, Medium, Low
    action: str
    legal_basis: str
    timeline: str
    rationale: str

class CaseStrength(BaseModel):
    overall: str  # Strong, Moderate, Weak
    strengths: List[str]
    weaknesses: List[str]
    score: float

class LegalAnalysis(BaseModel):
    recommendations: List[LegalRecommendation]
    case_strength: CaseStrength
    legal_analysis: str
    next_steps: List[str]

class AnalysisRequest(BaseModel):
    job_id: str
    options: Optional[Dict[str, Any]] = {}

class AnalysisResponse(BaseModel):
    job_id: str
    case_summary: str
    document_summaries: List[DocumentSummary]
    events: List[ExtractedEvent]
    recommendations: LegalAnalysis
    extraction_stats: Dict[str, Any]
    completed_at: str

class JobStatus(BaseModel):
    job_id: str
    status: JobStatusEnum
    progress: int  # 0-100
    current_step: str
    created_at: str
    error: Optional[str] = None
    cache_hit: Optional[bool] = False
    completed_steps: Optional[List[str]] = []

class UploadResponse(BaseModel):
    job_id: str
    files_uploaded: int
    status: str
    message: str

class ExportRequest(BaseModel):
    format: str  # excel, json, pdf
    include_attachments: bool = False
