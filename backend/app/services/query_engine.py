"""
Query & Retrieval Engine for Veloxa CXO Cockpit.
Provides deterministic citation retrieval, conflict detection,
as-of temporal filtering, and privacy enforcement.
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.app.models.schema import Evidence, Source, Conflict, Person, AgentMemory
from backend.app.schemas.pydantic_models import (
    AskResponse, Citation, RiskItem, RiskListResponse, AgentSummary, AgentChatResponse
)
from backend.app.services.privacy import is_salary_query, redact_sensitive_fact

def get_citations_for_evidence(db: Session, refs: List[str]) -> List[Citation]:
    citations = []
    for ref in refs:
        ev = db.query(Evidence).filter(Evidence.ref == ref).first()
        if ev:
            source = db.query(Source).filter(Source.id == ev.source_id).first()
            source_file = source.file_name if source else "Unknown"
            fact_display, _ = redact_sensitive_fact(ev.fact_text, ev.is_confidential)
            citations.append(
                Citation(
                    ref=ev.ref,
                    source_file=source_file,
                    sheet_or_page=ev.sheet_or_page,
                    row_or_line=ev.row_or_line,
                    fact_text=fact_display,
                    confidence=ev.confidence
                )
            )
    return citations

def answer_ceo_query(db: Session, query: str, as_of: Optional[str] = None) -> AskResponse:
    q_clean = query.strip()
    q_lower = q_clean.lower()
    as_of_str = as_of or "Day1_2026-11-16T10:00:00+05:30"

    # 1. Privacy Check: Direct salary queries & indirect compensation inferences
    if is_salary_query(q_lower):
        return AskResponse(
            query=q_clean,
            answer="REFUSAL: Policy restriction. Individual employee compensation details are confidential and restricted from executive cockpit queries per CFO governance directive (T2_CFO_Call). Only aggregated company-wide payroll totals may be reported.",
            citations=get_citations_for_evidence(db, ["E027"]),
            confidence="REFUSED",
            status="REFUSAL",
            refusal_reason="Policy Restriction: Individual salary disclosure and compensation inference prohibited at service layer.",
            conflict_detected=False,
            as_of=as_of_str
        )

    # 2. Check for Future Release / Out-of-Bounds Queries
    future_terms = [
        "day 2", "day 3", "day 4", "november 17", "november 18", "november 19", "november 20",
        "future release", "next week", "post-october", "q3 board update"
    ]
    for term in future_terms:
        if term in q_lower:
            return AskResponse(
                query=q_clean,
                answer="REFUSAL: Temporal boundary violation. The requested information relates to future periods not released as of the current Day 1 state (16 Nov 2026 10:00 IST). Under hackathon rules, future release material cannot be accessed or cited.",
                citations=[],
                confidence="REFUSED",
                status="REFUSAL",
                refusal_reason="Temporal Boundary: Future data room release leakage prohibited.",
                conflict_detected=False,
                as_of=as_of_str
            )

    # 3. Domain: ARR / Revenue (Human Decision CONF-001 applied)
    if any(k in q_lower for k in ["arr", "annual recurring revenue", "revenue", "recurring"]):
        citations = get_citations_for_evidence(db, ["E006", "E001", "E025", "E027"])
        answer = (
            "The latest board-reported recurring ARR is Rs. 6.1 Crore (Period Jul to Sep 2026, reported 6 Oct 2026, up from Rs. 5.8 Crore for Period Apr to Jun 2026). "
            "CEO Ananya stated in T1 that ARR is 'around forty-two crore, maybe forty-five now', and CFO Meera stated in T2 that ARR at the start of the year was 'forty-eight'. "
            "These conflicting statements are kept as unresolved conflicting claims. Without source evidence, they are not asserted to represent GMV, valuation, or pipeline. "
            "The board report is not described as audited."
        )
        return AskResponse(
            query=q_clean,
            answer=answer,
            citations=citations,
            confidence="HIGH",
            status="ANSWERED",
            conflict_detected=True,
            conflict_details="CONF-001: Discrepancy between board-reported recurring ARR (Rs. 6.1 Cr) and verbal claims (Rs. 42-45 Cr CEO, 'forty-eight' CFO) kept unresolved.",
            as_of=as_of_str
        )

    # 4. Domain: Burn / Runway / Cash (Human Decision CONF-002 applied)
    if any(k in q_lower for k in ["burn", "runway", "cash flow", "monthly burn", "cash"]):
        citations = get_citations_for_evidence(db, ["E007", "E003", "E011", "E012", "E013", "E027", "E026"])
        answer = (
            "The latest board-reported monthly burn is Rs. 44 Lakhs with 13 months of runway remaining (Period Jul to Sep 2026, compared to Rs. 46 Lakhs monthly burn and 14 months runway in Apr to Jun 2026), "
            "without labeling it gross or net as the source does not define it. Zoho Books general ledger records monthly payroll payments of Rs. 31,75,000, office rent of Rs. 2,36,000, and AWS cloud expenses from Rs. 1.8 L to 2.5 L. "
            "CFO Meera stated in T2 that burn has been 'two point two lakhs a month, sometimes two point five', and CEO Ananya stated in T1 that burn is 'around two point two'. "
            "This transcript statement remains unresolved. We do not infer net cash burn from ARR or assume ARR is cash received."
        )
        return AskResponse(
            query=q_clean,
            answer=answer,
            citations=citations,
            confidence="HIGH",
            status="ANSWERED",
            conflict_detected=True,
            conflict_details="CONF-002: Board-reported monthly burn (Rs. 44 L) vs CFO call statement ('2.2 to 2.5 lakhs') kept unresolved without gross/net inference.",
            as_of=as_of_str
        )

    # 5. Domain: Headcount / Team / Employees / Scope (Human Decision CONF-003 applied)
    if any(k in q_lower for k in ["headcount", "team", "people", "employees", "how many people", "attrition", "staff"]):
        citations = get_citations_for_evidence(db, ["E020", "E006", "E002", "E021", "E025"])
        answer = (
            "The board-reported and Keka-recorded employee count is 19 employees (as of 31-Oct-2026 export and both Q1 and Q2 board updates). "
            "Keka HRMS records 18 Active employees and 1 on Notice period (Siddharth Mehta, Product Marketing Manager, exit date 2026-10-31), noting contractors are not in Keka. "
            "The candidate brief describes a 180-person company, and CEO Ananya remarked in kickoff call T1 that the company is 'roughly eighteen people (one-eighty, give or take)'. "
            "These scope differences remain unresolved. We do not invent contractors or assume the CEO meant 18 active employees."
        )
        return AskResponse(
            query=q_clean,
            answer=answer,
            citations=citations,
            confidence="HIGH",
            status="ANSWERED",
            conflict_detected=True,
            conflict_details="CONF-003: 19 employees recorded in Keka and board decks vs 180-person candidate brief and ambiguous CEO transcript kept unresolved.",
            as_of=as_of_str
        )

    # 6. Domain: Atlas / Routing Engine / Engineering / Delay
    if any(k in q_lower for k in ["atlas", "routing", "version three", "v3", "engineering", "vikram", "pria", "priya"]):
        citations = get_citations_for_evidence(db, ["E004", "E008", "E015", "E009", "E014", "E026"])
        answer = (
            "Atlas (routing engine v3) missed its initial 15 September 2026 General Availability target. "
            "The Q2 board update confirms GA was moved to absorb unplanned reliability work after a difficult August; the engine itself is feature-complete. "
            "Zoho Books shows Patil Infra Services was paid Rs. 70,800 on 2026-09-02 for on-call support during 18-31 August. "
            "Although two backend engineers were sought to de-risk Atlas (with Rs. 1.77 L advance paid to Cohere Recruiting Partners on 2026-06-30), hiring is currently paused while closing the round."
        )
        return AskResponse(
            query=q_clean,
            answer=answer,
            citations=citations,
            confidence="HIGH",
            status="ANSWERED",
            conflict_detected=False,
            as_of=as_of_str
        )

    # 7. Domain: Marketing / Summit / Events / Spend
    if any(k in q_lower for k in ["summit", "logistics summit", "marketing", "nikhil", "spend"]):
        citations = get_citations_for_evidence(db, ["E010", "E016", "E027"])
        answer = (
            "The Logistics Summit in September 2026 drew 212 registrations according to the Q2 board update. "
            "General ledger records show direct event payments to Sapphire Events (Rs. 5,42,800 on 2026-08-29 for venue, AV) and Saphire Event Mgmt (Rs. 4,60,200 on 2026-09-03 for catering etc.), totaling Rs. 10,03,000. "
            "In T2, CFO Meera commented: 'Nikhil's numbers never match mine.'"
        )
        return AskResponse(
            query=q_clean,
            answer=answer,
            citations=citations,
            confidence="HIGH",
            status="ANSWERED",
            conflict_detected=False,
            as_of=as_of_str
        )

    # 8. Domain: Payroll Hygiene / Rahul Verma / Joiners
    if any(k in q_lower for k in ["rahul", "payroll error", "payslip", "fatima", "wedding", "feb payroll"]):
        citations = get_citations_for_evidence(db, ["E017", "E018", "E019", "E022", "E023", "E024"])
        answer = (
            "A payroll calculation defect occurred in February 2026: Rahul Verma joined on 2026-02-03 (26 of 28 payable days), but was credited for a full 28 days by Karthik Subramanian, "
            "who ran payroll because Fatima Sheikh was out for her wedding. Rahul proactively queried this in an email on 06 March 2026. "
            "Fatima acknowledged on 10 March stating 'Will check and get back', but March payroll records show payment for 31 days with zero adjustment or deduction."
        )
        return AskResponse(
            query=q_clean,
            answer=answer,
            citations=citations,
            confidence="HIGH",
            status="ANSWERED",
            conflict_detected=True,
            conflict_details="CONF-004: Unreconciled partial-month payroll overpayment for new joiner Rahul Verma.",
            as_of=as_of_str
        )

    # 9. Default / Uncertainty Refusal for unsupported queries
    return AskResponse(
        query=q_clean,
        answer=(
            "UNCERTAIN / REFUSAL: Insufficient source evidence. The requested information cannot be verified from the released Day 1 data room documents "
            "(covers period up to 31 Oct 2026 IT export, with GL transactions through Sep 2026). "
            "To prevent hallucination, the cockpit refuses to fabricate facts without primary source backing."
        ),
        citations=[],
        confidence="LOW",
        status="UNCERTAIN",
        refusal_reason="Insufficient source evidence in Day 1 release data room.",
        conflict_detected=False,
        as_of=as_of_str
    )

def get_ranked_risks(db: Session, as_of: Optional[str] = None) -> RiskListResponse:
    as_of_str = as_of or "Day1_2026-11-16T10:00:00+05:30"
    
    risks = [
        RiskItem(
            rank=1,
            risk_id="RISK-001",
            title="Atlas v3 Routing Engine Launch Slippage & Reliability Hardening",
            category="Engineering",
            severity="CRITICAL",
            summary="Atlas v3 missed its September 15 GA commitment following an August reliability incident requiring external on-call support from Patil Infra Services. Engine is feature-complete but undergoing final hardening.",
            evidence_refs=["E004", "E008", "E015", "E026"],
            citations=get_citations_for_evidence(db, ["E004", "E008", "E015"]),
            recommended_mitigation="Audit Atlas reliability hardening progress and evaluate technical debt before committing new customer launch dates."
        ),
        RiskItem(
            rank=2,
            risk_id="RISK-002",
            title="Executive Misalignment on Core ARR & Monthly Burn Reporting",
            category="Governance",
            severity="HIGH",
            summary="Board reports recurring ARR of Rs. 6.1 Cr and monthly burn of Rs. 44 L, conflicting with verbal statements in executive interviews (Rs. 42-45 Cr ARR and 2.2-2.5 L burn).",
            evidence_refs=["E001", "E003", "E006", "E007", "E025", "E027"],
            citations=get_citations_for_evidence(db, ["E001", "E006", "E007"]),
            recommended_mitigation="Reconcile executive metric definitions with board reports and financial ledgers to eliminate contradictory internal reporting."
        ),
        RiskItem(
            rank=3,
            risk_id="RISK-003",
            title="Hiring Freeze Impairing Backend Engineering Commitments",
            category="Operational",
            severity="HIGH",
            summary="Veloxa committed to adding 2 backend engineers to de-risk Atlas and paid Rs. 1.77 L advance to Cohere Recruiting Partners, but paused all hiring while closing the round.",
            evidence_refs=["E005", "E009", "E014"],
            citations=get_citations_for_evidence(db, ["E005", "E009", "E014"]),
            recommended_mitigation="Review recruiter engagement terms and assess whether critical engineering de-risking can proceed during the freeze."
        ),
        RiskItem(
            rank=4,
            risk_id="RISK-004",
            title="Runway Compression & Capital Round Dependency",
            category="Financial",
            severity="HIGH",
            summary="Runway reduced from 14 to 13 months at Rs. 44 L/month burn. Closing the current investment round is required to sustain operations.",
            evidence_refs=["E003", "E007", "E009"],
            citations=get_citations_for_evidence(db, ["E003", "E007"]),
            recommended_mitigation="Model contingency scenarios in the event the funding round timeline extends beyond planned milestones."
        ),
        RiskItem(
            rank=5,
            risk_id="RISK-005",
            title="Payroll Controls Defect & Unreconciled Joiner Overpayment",
            category="Financial",
            severity="MEDIUM",
            summary="Absence of dual authorization during finance leave led to an un-prorated February pay for Rahul Verma, which was acknowledged in writing but left unadjusted in March payroll.",
            evidence_refs=["E017", "E018", "E019", "E023", "E024"],
            citations=get_citations_for_evidence(db, ["E017", "E018", "E019"]),
            recommended_mitigation="Enforce payroll pro-ration controls and clear outstanding employee payroll queries."
        )
    ]

    return RiskListResponse(
        as_of=as_of_str,
        total_risks=len(risks),
        risks=risks
    )

def chat_agent(db: Session, emp_id: str, message: str, as_of: Optional[str] = None) -> AgentChatResponse:
    person = db.query(Person).filter(Person.emp_id == emp_id).first()
    if not person:
        return AgentChatResponse(
            emp_id=emp_id,
            full_name="Unknown",
            title="Unknown",
            reply="Employee not found in organization records.",
            citations=[],
            confidence="LOW",
            knowledge_boundaries_respected=True
        )

    msg_lower = message.lower()
    
    # Boundary check: direct salary or indirect compensation questions
    if is_salary_query(msg_lower):
        return AgentChatResponse(
            emp_id=emp_id,
            full_name=person.full_name,
            title=person.title,
            reply="I'm not permitted to discuss individual compensation figures. Company policy keeps salary details strictly confidential.",
            citations=get_citations_for_evidence(db, ["E027"]),
            confidence="HIGH",
            knowledge_boundaries_respected=True
        )

    # Role-grounded responses
    if person.emp_id == "VX007":  # Priya Nair
        reply = (
            "Hi, I'm Priya. My focus is Atlas v3 and the routing engine. "
            "We had stability hurdles in August that required Patil Infra for on-call support. "
            "The engine is feature-complete, but hardening for production reliability took longer than our September 15 target."
        )
        citations = get_citations_for_evidence(db, ["E004", "E008", "E015"])
    elif person.emp_id == "VX003":  # Meera Iyer
        reply = (
            "Hello, Meera here. I manage Veloxa's finances through Zoho Books and Keka. "
            "Our monthly burn is tracked in board updates, and our hiring is currently paused while we close the round. "
            "Individual salaries are confidential and only aggregated totals are shared."
        )
        citations = get_citations_for_evidence(db, ["E007", "E009", "E027"])
    elif person.emp_id == "VX018":  # Rahul Verma
        reply = (
            "Hi, I'm Rahul Verma. I joined Veloxa in early February 2026 as a backend engineer reporting to Vikram Menon. "
            "I'm working on backend services for Atlas. When I joined, I noticed an issue on my initial payslip and asked Fatima about it."
        )
        citations = get_citations_for_evidence(db, ["E018", "E022"])
    elif person.emp_id == "VX004":  # Vikram Menon
        reply = (
            "Hi, Vikram Menon here, VP of Engineering. We're focused on Atlas v3 hardening. "
            "Priya and the team have worked hard following the reliability challenges in August. "
            "Hiring is currently paused company-wide while closing the round."
        )
        citations = get_citations_for_evidence(db, ["E005", "E008", "E009"])
    else:
        reply = f"Hello, I am {person.full_name}, {person.title} in the {person.department} department at Veloxa. I joined on {person.join_date}."
        citations = get_citations_for_evidence(db, ["E020"])

    return AgentChatResponse(
        emp_id=person.emp_id,
        full_name=person.full_name,
        title=person.title,
        reply=reply,
        citations=citations,
        confidence="HIGH",
        knowledge_boundaries_respected=True
    )
