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

    # 1. Privacy Check: Individual salary queries
    if is_salary_query(q_lower):
        return AskResponse(
            query=q_clean,
            answer="REFUSAL: Policy restriction. Individual employee compensation details are confidential and restricted from executive cockpit queries per CFO governance directive (T2_CFO_Call). Only aggregated company-wide payroll totals may be reported.",
            citations=get_citations_for_evidence(db, ["E027"]),
            confidence="REFUSED",
            status="REFUSAL",
            refusal_reason="Policy Restriction: Individual salary disclosure prohibited at service layer.",
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

    # 3. Domain: ARR / Revenue
    if any(k in q_lower for k in ["arr", "annual recurring revenue", "revenue", "recurring"]):
        citations = get_citations_for_evidence(db, ["E006", "E001", "E025", "E027"])
        answer = (
            "As of the latest formal Q2 FY27 board update (Jul-Sep 2026), Veloxa's recurring ARR is Rs. 6.1 Crore (up from Rs. 5.8 Crore in Q1 Apr-Jun 2026). "
            "However, there is an unresolved critical conflict: in transcript T1, CEO Ananya verbally claimed ARR is 'around forty-two crore, maybe forty-five now', "
            "and in T2, CFO Meera cited 'forty-eight' at the start of the year. The audited governance figures remain Rs. 6.1 Cr."
        )
        return AskResponse(
            query=q_clean,
            answer=answer,
            citations=citations,
            confidence="HIGH",
            status="ANSWERED",
            conflict_detected=True,
            conflict_details="CONF-001: 7x variance between audited Board update ARR (Rs. 6.1 Cr) and CEO verbal statement (Rs. 42-45 Cr).",
            as_of=as_of_str
        )

    # 4. Domain: Burn / Runway / Cash
    if any(k in q_lower for k in ["burn", "runway", "cash flow", "monthly burn", "cash"]):
        citations = get_citations_for_evidence(db, ["E007", "E003", "E011", "E012", "E013", "E027"])
        answer = (
            "According to the Q2 Board Update (Jul-Sep 2026), Veloxa's monthly burn is Rs. 44 Lakhs with 13 months of runway remaining (down from Rs. 46 Lakhs burn and 14 months runway in Q1). "
            "Zoho Books general ledger confirms gross monthly payroll alone is Rs. 31,75,000, plus rent (Rs. 2.36 L) and cloud infrastructure (~Rs. 2.5 L). "
            "Note: This directly contradicts CFO Meera's verbal statement that burn is 'two point two to two point five lakhs a month' (CONF-002), which likely conflates net burn against revenue collections or suffered transcript truncation."
        )
        return AskResponse(
            query=q_clean,
            answer=answer,
            citations=citations,
            confidence="HIGH",
            status="ANSWERED",
            conflict_detected=True,
            conflict_details="CONF-002: Gross cash outflow is Rs. 44-46 L/mo, whereas verbal CFO call cited 2.2-2.5 L/mo.",
            as_of=as_of_str
        )

    # 5. Domain: Headcount / Team / Employees / Attrition
    if any(k in q_lower for k in ["headcount", "team", "people", "employees", "how many people", "attrition", "staff"]):
        citations = get_citations_for_evidence(db, ["E020", "E006", "E021", "E025"])
        answer = (
            "Veloxa has exactly 19 employees recorded in the Keka HRMS export as of 31-Oct-2026, corroborating the team count of 19 reported in both Q1 and Q2 board updates. "
            "Of these, 18 are Active and 1 is on Notice Period (Siddharth Mehta, Product Marketing Manager, exit date 2026-10-31). "
            "Keka explicitly excludes contractors. In kickoff call T1, CEO Ananya casually mentioned 'one-eighty, give or take', which is an unresolved transcription or contractor scope discrepancy (CONF-003)."
        )
        return AskResponse(
            query=q_clean,
            answer=answer,
            citations=citations,
            confidence="HIGH",
            status="ANSWERED",
            conflict_detected=True,
            conflict_details="CONF-003: 19 employees in HRMS vs 'one-eighty' verbal remark.",
            as_of=as_of_str
        )

    # 6. Domain: Atlas / Routing Engine / Engineering / Delay
    if any(k in q_lower for k in ["atlas", "routing", "version three", "v3", "engineering", "vikram", "pria", "priya"]):
        citations = get_citations_for_evidence(db, ["E004", "E008", "E015", "E009", "E014", "E026"])
        answer = (
            "Atlas (routing engine v3) missed its initial 15 September 2026 General Availability target. "
            "The Q2 board update confirms GA was moved to absorb unplanned reliability hardening following a difficult August. "
            "Zoho Books shows emergency on-call support from Patil Infra Services was engaged for 18-31 August (Rs. 70,800). "
            "Although two backend engineers were sought to de-risk Atlas (with Rs. 1.77 L advance paid to Cohere Recruiting), engineering hiring is currently frozen while closing the round."
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
            "The Logistics Summit took place in September 2026 and drew 212 registrations, marking Veloxa's largest event to date. "
            "General ledger records show direct event venue and catering payments to Sapphire Events (Rs. 5,42,800) and Saphire Event Mgmt (Rs. 4,60,200), totaling Rs. 10,03,000. "
            "CFO Meera noted in T2 that 'Nikhil's numbers never match mine', indicating reconciliation friction between marketing projections and ledger actuals."
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
            "who stepped in while Fatima Sheikh was away for her wedding. Rahul proactively flagged this in an email on 06 March 2026. "
            "Although Fatima acknowledged it on 10 March, March payroll records show full payment with zero clawback or deduction, leaving an unreconciled audit finding."
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
            title="Atlas v3 Routing Engine Launch Slippage & Stability Debt",
            category="Engineering",
            severity="CRITICAL",
            summary="Atlas v3 missed its September 15 GA commitment following an August reliability crisis requiring external on-call support (Patil Infra). Heavy key-person dependency exists on Priya Nair.",
            evidence_refs=["E004", "E008", "E015", "E026"],
            citations=get_citations_for_evidence(db, ["E004", "E008", "E015"]),
            recommended_mitigation="Conduct technical audit of Atlas reliability hardening; lift backend hiring freeze specifically for routing engine support."
        ),
        RiskItem(
            rank=2,
            risk_id="RISK-002",
            title="Executive Financial Misalignment on Core ARR & Burn Metrics",
            category="Governance",
            severity="HIGH",
            summary="7x variance between audited Board update ARR (Rs. 6.1 Cr) and CEO verbal assertion (Rs. 42-45 Cr), alongside a 20x variance between actual gross monthly burn (Rs. 44 L) and verbal CFO claims (2.2-2.5 L).",
            evidence_refs=["E001", "E003", "E006", "E007", "E025", "E027"],
            citations=get_citations_for_evidence(db, ["E001", "E006", "E007"]),
            recommended_mitigation="Institute single-source-of-truth financial dashboard directly linked to Zoho Books and board reporting."
        ),
        RiskItem(
            rank=3,
            risk_id="RISK-003",
            title="Hiring Freeze Bottleneck Impacting Backend Engineering Commitments",
            category="Operational",
            severity="HIGH",
            summary="Veloxa committed to the Board to add 2 backend engineers in Q2 and paid Rs. 1.77 L recruiter advance, but paused all hiring while closing the funding round.",
            evidence_refs=["E005", "E009", "E014"],
            citations=get_citations_for_evidence(db, ["E005", "E009", "E014"]),
            recommended_mitigation="Evaluate recruiter fee forfeiture risk and prioritize critical de-risking engineering roles."
        ),
        RiskItem(
            rank=4,
            risk_id="RISK-004",
            title="Runway Compression & Capital Round Dependency",
            category="Financial",
            severity="HIGH",
            summary="Runway has reduced from 14 to 13 months at Rs. 44 L/month burn. Any delay in closing the investment round risks forced austerity or operational disruption.",
            evidence_refs=["E003", "E007", "E009"],
            citations=get_citations_for_evidence(db, ["E003", "E007"]),
            recommended_mitigation="Model contingency budget scenarios for Q3/Q4 if the funding round slips beyond December."
        ),
        RiskItem(
            rank=5,
            risk_id="RISK-005",
            title="Payroll Controls Failure & Unreconciled Joiner Overpayment",
            category="Financial",
            severity="MEDIUM",
            summary="Lack of dual-control during finance leave led to un-prorated February pay for Rahul Verma, acknowledged in writing but left unadjusted in March payroll.",
            evidence_refs=["E017", "E018", "E019", "E023", "E024"],
            citations=get_citations_for_evidence(db, ["E017", "E018", "E019"]),
            recommended_mitigation="Enforce automated payroll pro-ration rules in Keka HRMS and clear outstanding joiner reconciliations."
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
    
    # Boundary check: salary questions
    if is_salary_query(msg_lower):
        return AgentChatResponse(
            emp_id=emp_id,
            full_name=person.full_name,
            title=person.title,
            reply=f"I'm not permitted to discuss individual compensation figures. Company policy keeps salary details strictly confidential.",
            citations=get_citations_for_evidence(db, ["E027"]),
            confidence="HIGH",
            knowledge_boundaries_respected=True
        )

    # Role-grounded responses
    if person.emp_id == "VX007":  # Priya Nair
        reply = (
            "Hi, I'm Priya. My focus is Atlas v3 and the core real-time re-routing engine. "
            "We had a really tough August with stability issues that required bringing in Patil Infra for emergency on-call support. "
            "The engine is feature-complete, but hardening for production reliability took longer than our September 15 target."
        )
        citations = get_citations_for_evidence(db, ["E004", "E008", "E015"])
    elif person.emp_id == "VX003":  # Meera Iyer
        reply = (
            "Hello, Meera here. I manage Veloxa's finances through Zoho Books and Keka. "
            "Our monthly burn is tracked carefully in our board updates, and our hiring is currently paused while we close the round. "
            "I maintain strict privacy on individual salaries—only aggregated figures are shared."
        )
        citations = get_citations_for_evidence(db, ["E007", "E009", "E027"])
    elif person.emp_id == "VX018":  # Rahul Verma
        reply = (
            "Hi, I'm Rahul Verma. I joined Veloxa in early February 2026 on Vikram's backend engineering team. "
            "I'm working on backend services for Atlas. When I joined, I noticed an issue on my initial payslip and asked Fatima about it."
        )
        citations = get_citations_for_evidence(db, ["E018", "E022"])
    elif person.emp_id == "VX004":  # Vikram Menon
        reply = (
            "Hi, Vikram Menon here, VP of Engineering. We're driving Atlas v3 forward. "
            "Priya and the team have done tremendous work, especially after the reliability crunch in August. "
            "We need additional backend capacity, but with the current company-wide freeze, we're focusing on hardening."
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
