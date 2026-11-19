from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.schema import Evidence, Person, Conflict, Source
from backend.app.schemas.pydantic_models import (
    AskRequest, AskResponse, RiskListResponse, AgentSummary,
    AgentChatRequest, AgentChatResponse, EvidenceResponse, ConflictResponse,
    HRInsightsResponse, EngineeringOverviewResponse, MarketingOverviewResponse,
    OrgSimulationResponse
)
from backend.app.services.query_engine import (
    answer_ceo_query, get_ranked_risks, chat_agent, get_hr_insights,
    get_engineering_overview, get_marketing_overview, get_org_simulation,
    parse_as_of_date, DAY4_RELEASE_TIME
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
    return answer_ceo_query(db, request.query, request.get_as_of())

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
@router.post("/agent/{emp_id}/chat", response_model=AgentChatResponse)
def chat_with_agent(emp_id: str, request: AgentChatRequest, db: Session = Depends(get_db)):
    """
    Direct interview with an individual employee agent.
    Strictly constrained by the employee's role, organizational boundary, and privacy rules.
    """
    return chat_agent(db, emp_id, request.message, request.as_of)

@router.get("/evidence/{ref}", response_model=EvidenceResponse)
def get_evidence(ref: str, as_of: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """
    Detailed evidence inspector with exact source file, sheet/page, row, and text.
    Individual salary data is redacted at the service layer.
    """
    ev = db.query(Evidence).filter(Evidence.ref == ref).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence item not found")
    as_of_dt = parse_as_of_date(as_of)
    if as_of_dt and ev.released_at and ev.released_at > as_of_dt:
        raise HTTPException(status_code=423, detail="Evidence not released at the requested as-of timestamp.")
        
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
def list_conflicts(as_of: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """
    Returns documented source conflicts with proposed interpretations and human review status.
    """
    conflicts = db.query(Conflict).all()
    as_of_dt = parse_as_of_date(as_of)
    if as_of_dt and as_of_dt < DAY4_RELEASE_TIME:
        conflicts = [c for c in conflicts if c.conflict_id not in {"CONF-011", "CONF-012", "CONF-013", "CONF-014"}]
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

@router.get("/engineering-overview", response_model=EngineeringOverviewResponse)
def engineering_overview(as_of: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """
    Day 3 Engineering telemetry overview.
    Reports Jira epic progress, GA original vs revised dates, on-call rota,
    August SEV1 incident metrics, and Git commit activity aggregates.
    """
    return get_engineering_overview(db, as_of)

@router.get("/marketing-overview", response_model=MarketingOverviewResponse)
def marketing_overview(as_of: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """
    Day 3 Marketing launch kit and campaign status.
    Reports launch kit asset readiness (website unpublished, press note draft),
    Siddharth Mehta handover uncertainty, spend reconciliation, and CRO reporting.
    """
    return get_marketing_overview(db, as_of)

@router.get("/org/simulation", response_model=OrgSimulationResponse)
def org_simulation(
    mode: Optional[str] = Query("actual_as_of", description="'actual_as_of' or 'simulated_cro'"),
    as_of: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Day 3 Organizational Reporting Simulation.
    Provides a preview simulation of marketing reporting to an unfilled CRO role
    under T6b governance guardrails, separate from active as-of reporting lines.
    """
    return get_org_simulation(db, mode, as_of)

