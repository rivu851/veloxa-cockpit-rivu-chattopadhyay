from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.schema import Evidence, Person, Conflict, Source
from backend.app.schemas.pydantic_models import (
    AskRequest, AskResponse, RiskListResponse, AgentSummary,
    AgentChatRequest, AgentChatResponse, EvidenceResponse, ConflictResponse,
    HRInsightsResponse
)
from backend.app.services.query_engine import (
    answer_ceo_query, get_ranked_risks, chat_agent, get_hr_insights
)
from backend.app.services.privacy import redact_sensitive_fact

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    """
    CEO Cockpit question answering.
    Returns grounded answers with precise citations, confidence rating,
    temporal as-of compliance, and honest refusal if evidence is missing or restricted.
    """
    return answer_ceo_query(db, request.query, request.as_of)

@router.get("/risks", response_model=RiskListResponse)
def get_risks(as_of: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """
    Returns ranked, evidence-backed company risks.
    """
    return get_ranked_risks(db, as_of)

@router.get("/agents", response_model=List[AgentSummary])
def list_agents(db: Session = Depends(get_db)):
    """
    Returns interviewable employee agents grounded in Keka HRMS records.
    """
    people = db.query(Person).filter(Person.is_interviewable == True).all()
    return [
        AgentSummary(
            emp_id=p.emp_id,
            full_name=p.full_name,
            title=p.title,
            department=p.department,
            manager_id=p.manager_id,
            location=p.location,
            status=p.status,
            is_interviewable=p.is_interviewable
        )
        for p in people
    ]

@router.post("/agents/{emp_id}/chat", response_model=AgentChatResponse)
def chat_with_agent(emp_id: str, request: AgentChatRequest, db: Session = Depends(get_db)):
    """
    Direct interview with an individual employee agent.
    Strictly constrained by the employee's role, organizational boundary, and privacy rules.
    """
    return chat_agent(db, emp_id, request.message, request.as_of)

@router.get("/evidence/{ref}", response_model=EvidenceResponse)
def get_evidence(ref: str, db: Session = Depends(get_db)):
    """
    Detailed evidence inspector with exact source file, sheet/page, row, and text.
    Individual salary data is redacted at the service layer.
    """
    ev = db.query(Evidence).filter(Evidence.ref == ref).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence item not found")
        
    source = db.query(Source).filter(Source.id == ev.source_id).first()
    fact_text, is_redacted = redact_sensitive_fact(ev.fact_text, ev.is_confidential)
    
    return EvidenceResponse(
        ref=ev.ref,
        source_file=source.file_name if source else "Unknown",
        sheet_or_page=ev.sheet_or_page,
        row_or_line=ev.row_or_line,
        fact_text=fact_text,
        entities_named=ev.entities_named,
        date_as_written=ev.date_as_written,
        date_normalized=ev.date_normalized.isoformat() if ev.date_normalized else None,
        confidence=ev.confidence,
        is_redacted=is_redacted,
        released_at=ev.released_at.isoformat()
    )

@router.get("/conflicts", response_model=List[ConflictResponse])
def list_conflicts(db: Session = Depends(get_db)):
    """
    Returns documented source conflicts with proposed interpretations and human review status.
    """
    conflicts = db.query(Conflict).all()
    return [
        ConflictResponse(
            conflict_id=c.conflict_id,
            topic=c.topic,
            description=c.description,
            competing_sources=c.competing_sources,
            proposed_interpretation=c.proposed_interpretation,
            confidence=c.confidence,
            what_would_change=c.what_would_change,
            impact_level=c.impact_level,
            human_status=c.human_status,
            resolution_notes=c.resolution_notes
        )
        for c in conflicts
    ]

@router.get("/hr-insights", response_model=HRInsightsResponse)
def get_insights(as_of: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """
    Returns authorized team-level Culture Amp engagement and Keka Hire requisition insights.
    Maintains strict privacy: comments withheld for teams < 6, leave registers protected.
    """
    return get_hr_insights(db, as_of)
