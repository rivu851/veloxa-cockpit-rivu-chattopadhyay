from typing import List, Optional
from pydantic import BaseModel, Field

class Citation(BaseModel):
    ref: str
    source_file: str
    sheet_or_page: Optional[str] = None
    row_or_line: Optional[str] = None
    fact_text: str
    confidence: str = "H"

class AskRequest(BaseModel):
    query: str
    as_of: Optional[str] = Field(default=None, description="ISO timestamp or release day (e.g., 'Day1', '2026-11-16T10:00:00+05:30')")

class AskResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation] = []
    confidence: str = Field(default="HIGH", description="HIGH, MEDIUM, LOW, REFUSED")
    status: str = Field(default="ANSWERED", description="ANSWERED, UNCERTAIN, REFUSAL")
    refusal_reason: Optional[str] = None
    conflict_detected: bool = False
    conflict_details: Optional[str] = None
    as_of: str

class RiskItem(BaseModel):
    rank: int
    risk_id: str
    title: str
    category: str  # Financial, Engineering, Operational, Governance, Key-Person
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    summary: str
    evidence_refs: List[str]
    citations: List[Citation]
    recommended_mitigation: str

class RiskListResponse(BaseModel):
    as_of: str
    total_risks: int
    risks: List[RiskItem]

class AgentSummary(BaseModel):
    emp_id: str
    full_name: str
    title: str
    department: str
    manager_id: Optional[str] = None
    location: str
    status: str
    is_interviewable: bool

class AgentChatRequest(BaseModel):
    message: str
    as_of: Optional[str] = None

class AgentChatResponse(BaseModel):
    emp_id: str
    full_name: str
    title: str
    reply: str
    citations: List[Citation] = []
    confidence: str = "HIGH"
    knowledge_boundaries_respected: bool = True

class EvidenceResponse(BaseModel):
    ref: str
    source_file: str
    sheet_or_page: Optional[str] = None
    row_or_line: Optional[str] = None
    fact_text: str
    entities_named: Optional[str] = None
    date_as_written: Optional[str] = None
    date_normalized: Optional[str] = None
    confidence: str
    is_redacted: bool
    released_at: str

class ConflictResponse(BaseModel):
    conflict_id: str
    topic: str
    description: str
    competing_sources: str
    proposed_interpretation: str
    confidence: str
    what_would_change: str
    impact_level: str
    human_status: str
    resolution_notes: Optional[str] = None
