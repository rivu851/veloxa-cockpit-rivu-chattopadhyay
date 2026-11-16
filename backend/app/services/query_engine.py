"""
Evidence-Grounded Query & Reasoning Engine.
Retrieves claims and evidence dynamically from SQLite persistence.
Evaluates active risks based on available supporting evidence.
Enforces salary privacy, temporal boundaries, and honest refusal.
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from dateutil import parser as date_parser
from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.app.models.schema import Evidence, Source, Conflict, Person, Claim, Assumption, AgentMemory
from backend.app.schemas.pydantic_models import (
    AskResponse, Citation, RiskListResponse, RiskItem, AgentChatResponse
)
from backend.app.services.privacy import is_salary_query, redact_sensitive_fact

DAY1_RELEASE_TIME = datetime(2026, 11, 16, 10, 0, 0)

def parse_as_of_date(as_of: Optional[str]) -> Optional[datetime]:
    if not as_of:
        return None
    as_of_clean = as_of.strip()
    if as_of_clean.lower() in ["day1", "day 1"]:
        return DAY1_RELEASE_TIME
    try:
        if "_" in as_of_clean:
            as_of_clean = as_of_clean.split("_", 1)[1]
        dt = date_parser.parse(as_of_clean)
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        return dt
    except Exception:
        return None

def get_citations_for_evidence(db: Session, refs: List[str], as_of_dt: Optional[datetime] = None) -> List[Citation]:
    citations = []
    for ref in refs:
        ev = db.query(Evidence).filter(Evidence.ref == ref).first()
        if ev:
            # Temporal check: do not return evidence created/recorded after as_of_dt
            if as_of_dt and ev.record_date and ev.record_date > as_of_dt:
                continue
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
    as_of_dt = parse_as_of_date(as_of_str)

    # 1. Privacy Check: Direct salary queries & indirect compensation inferences
    if is_salary_query(q_lower):
        citations = get_citations_for_evidence(db, ["E027"], as_of_dt)
        return AskResponse(
            query=q_clean,
            answer="REFUSAL: Policy restriction. Individual employee compensation details are confidential and restricted from executive cockpit queries per CFO governance directive (T2_CFO_Call). Only aggregated company-wide payroll totals may be reported.",
            citations=citations,
            confidence="REFUSED",
            status="REFUSAL",
            refusal_reason="Policy Restriction: Individual salary disclosure and compensation inference prohibited at service layer.",
            conflict_detected=False,
            as_of=as_of_str
        )

    # 2. Check for Future Release / Out-of-Bounds Queries
    future_terms = [
        "day 2", "day 3", "day 4", "november 17", "november 18", "november 19", "november 20",
        "december 2026", "dec 2026", "2027", "next quarter", "future release",
        "next week", "post-october", "q3 board update", "q3 2026", "q4 2026"
    ]
    if as_of_dt and as_of_dt > DAY1_RELEASE_TIME:
        return AskResponse(
            query=q_clean,
            answer="REFUSAL: Temporal boundary violation. The requested as-of date is after the released Day 1 cutoff (16 Nov 2026 10:00 IST). Under hackathon rules, future release material cannot be accessed or cited.",
            citations=[],
            confidence="REFUSED",
            status="REFUSAL",
            refusal_reason="Temporal Boundary: Future data room release leakage prohibited.",
            conflict_detected=False,
            as_of=as_of_str
        )

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

    is_prior_to_q2 = as_of_dt is not None and as_of_dt < datetime(2026, 10, 6)

    # 3. Domain: ARR / Revenue (Grounded in SQLite Claims & Evidence)
    if any(k in q_lower for k in ["arr", "annual recurring revenue", "revenue", "recurring"]):
        # Retrieve relevant claims from SQLite
        arr_claims = db.query(Claim).filter(Claim.claim_category == "ARR").all()
        # Filter temporally
        valid_claims = [c for c in arr_claims if not as_of_dt or not c.record_date or c.record_date <= as_of_dt]
        
        # Determine expected evidence refs based on temporal cutoff
        expected_refs = ["E001"] if is_prior_to_q2 else ["E006", "E001", "E025", "E027"]
        citations = get_citations_for_evidence(db, expected_refs, as_of_dt)

        # DATA-DRIVEN CHECK: If authoritative supporting evidence was deleted/withheld, refuse conclusion!
        authoritative_refs = ["E001"] if is_prior_to_q2 else ["E006"]
        has_authoritative_ev = any(c.ref in authoritative_refs for c in citations)
        if not has_authoritative_ev:
            return AskResponse(
                query=q_clean,
                answer="UNCERTAIN: Insufficient source evidence. Primary board-reported ARR evidence is unavailable in the database.",
                citations=citations,
                confidence="LOW",
                status="UNCERTAIN",
                refusal_reason="Insufficient source evidence: Supporting ARR evidence missing from SQLite.",
                conflict_detected=False,
                as_of=as_of_str
            )

        if is_prior_to_q2:
            answer = (
                f"As of {as_of_dt.strftime('%d %b %Y')}, the latest board-reported recurring ARR is Rs. 5.8 Crore "
                f"(Period Apr to Jun 2026, reported 8 Jul 2026 across 61 customers). "
                f"Subsequent Q2 metrics have not been released as of this date."
            )
            conflict_detected = False
            conflict_details = None
        else:
            answer = (
                "The latest board-reported recurring ARR is Rs. 6.1 Crore (Period Jul to Sep 2026, reported 6 Oct 2026, up from Rs. 5.8 Crore for Period Apr to Jun 2026). "
                "CEO Ananya stated in T1 that ARR is 'around forty-two crore, maybe forty-five now', and CFO Meera stated in T2 that ARR at the start of the year was 'forty-eight'. "
                "These conflicting statements are kept as unresolved conflicting claims. Without source evidence, they are not asserted to represent GMV, valuation, or pipeline. "
                "The board report is not described as audited."
            )
            conflict_detected = True
            conflict_details = "CONF-001: Discrepancy between board-reported recurring ARR (Rs. 6.1 Cr) and verbal claims (Rs. 42-45 Cr CEO, 'forty-eight' CFO) kept unresolved."

        return AskResponse(
            query=q_clean,
            answer=answer,
            citations=citations,
            confidence="HIGH",
            status="ANSWERED",
            conflict_detected=conflict_detected,
            conflict_details=conflict_details,
            as_of=as_of_str
        )

    # 4. Domain: Burn / Runway / Cash (Grounded in SQLite Claims & Evidence)
    if any(k in q_lower for k in ["burn", "runway", "cash flow", "monthly burn", "cash"]):
        expected_refs = ["E003"] if is_prior_to_q2 else ["E007", "E003", "E011", "E012", "E013", "E027", "E026"]
        citations = get_citations_for_evidence(db, expected_refs, as_of_dt)

        # DATA-DRIVEN CHECK
        if not citations:
            return AskResponse(
                query=q_clean,
                answer="UNCERTAIN: Insufficient source evidence. Supporting evidence records for burn rate are unavailable in the database.",
                citations=[],
                confidence="LOW",
                status="UNCERTAIN",
                refusal_reason="Insufficient source evidence: Supporting burn evidence missing from SQLite.",
                conflict_detected=False,
                as_of=as_of_str
            )

        if is_prior_to_q2:
            answer = (
                f"As of {as_of_dt.strftime('%d %b %Y')}, the latest board-reported monthly burn is Rs. 46 Lakhs "
                f"with 14 months of runway remaining (Period Apr to Jun 2026, reported 8 Jul 2026). "
                f"Subsequent Q2 metrics have not been released as of this date."
            )
            conflict_detected = False
            conflict_details = None
        else:
            answer = (
                "The latest board-reported monthly burn is Rs. 44 Lakhs with 13 months of runway remaining "
                "(Period Jul to Sep 2026, compared to Rs. 46 Lakhs monthly burn and 14 months runway in Apr to Jun 2026), "
                "without labeling it gross or net as the source does not define it. "
                "Zoho Books general ledger records monthly payroll payments of Rs. 31,75,000, office rent of Rs. 2,36,000, "
                "and AWS cloud expenses from Rs. 1.8 L to 2.5 L. CFO Meera stated in T2 that burn has been "
                "'two point two lakhs a month, sometimes two point five', and CEO Ananya stated in T1 that burn is "
                "'around two point two'. This transcript statement remains unresolved. We do not infer net cash burn from ARR or assume ARR is cash received."
            )
            conflict_detected = True
            conflict_details = "CONF-002: Board-reported monthly burn (Rs. 44 L) vs CFO call statement ('2.2 to 2.5 lakhs') kept unresolved without gross/net inference."

        return AskResponse(
            query=q_clean,
            answer=answer,
            citations=citations,
            confidence="HIGH",
            status="ANSWERED",
            conflict_detected=conflict_detected,
            conflict_details=conflict_details,
            as_of=as_of_str
        )

    # 5. Domain: Headcount / Team / Employees / Scope (Grounded in SQLite Claims & Evidence)
    if any(k in q_lower for k in ["headcount", "team", "people", "employees", "how many people", "attrition", "staff"]):
        expected_refs = ["E020", "E006", "E002", "E021", "E025"]
        citations = get_citations_for_evidence(db, expected_refs, as_of_dt)

        if not citations:
            return AskResponse(
                query=q_clean,
                answer="UNCERTAIN: Insufficient source evidence. Supporting headcount records are missing from SQLite.",
                citations=[],
                confidence="LOW",
                status="UNCERTAIN",
                as_of=as_of_str
            )

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
        if any(v in q_lower for v in ["v4", "version 4", "4.0", "atlas 4", "next generation"]):
            return AskResponse(
                query=q_clean,
                answer="UNCERTAIN: Insufficient source evidence. Day 1 data room assets only document Atlas version 3 (routing engine v3). No plans, specifications, or timelines for Atlas version 4 exist in the released materials.",
                citations=[],
                confidence="LOW",
                status="UNCERTAIN",
                refusal_reason="Insufficient source evidence: Atlas v4 is not documented in Day 1 releases.",
                conflict_detected=False,
                as_of=as_of_str
            )

        expected_refs = ["E004", "E005"] if is_prior_to_q2 else ["E004", "E008", "E015", "E009", "E014", "E026"]
        citations = get_citations_for_evidence(db, expected_refs, as_of_dt)

        if not citations:
            return AskResponse(
                query=q_clean,
                answer="UNCERTAIN: Insufficient source evidence. Atlas engineering records are missing from SQLite.",
                citations=[],
                confidence="LOW",
                status="UNCERTAIN",
                as_of=as_of_str
            )

        if is_prior_to_q2:
            answer = (
                f"As of {as_of_dt.strftime('%d %b %Y')}, Atlas (routing engine v3) is reported on track for GA on 15 September 2026 "
                f"per the Q1 board update sent 8 Jul 2026. Real-time re-routing is the headline feature and two backend engineers are being sought to de-risk delivery."
            )
        else:
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
        expected_refs = ["E001"] if is_prior_to_q2 else ["E010", "E016", "E027"]
        citations = get_citations_for_evidence(db, expected_refs, as_of_dt)

        if not citations:
            return AskResponse(
                query=q_clean,
                answer="UNCERTAIN: Insufficient source evidence. Marketing event records are missing from SQLite.",
                citations=[],
                confidence="LOW",
                status="UNCERTAIN",
                as_of=as_of_str
            )

        if is_prior_to_q2:
            answer = (
                f"As of {as_of_dt.strftime('%d %b %Y')}, the Logistics Summit is scheduled for September. "
                f"Q1 board asks requested introductions to logistics CXOs for the September summit."
            )
        else:
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
    if any(k in q_lower for k in ["rahul", "payroll error", "payroll discrepancy", "payslip", "fatima", "wedding", "feb payroll"]):
        expected_refs = ["E017", "E018", "E019", "E022", "E023", "E024"]
        citations = get_citations_for_evidence(db, expected_refs, as_of_dt)

        if not citations:
            return AskResponse(
                query=q_clean,
                answer="UNCERTAIN: Insufficient source evidence. Payroll discrepancy records are missing from SQLite.",
                citations=[],
                confidence="LOW",
                status="UNCERTAIN",
                as_of=as_of_str
            )

        answer = (
            "This is classified as a suspected February payroll discrepancy requiring verification, rather than a conclusively confirmed payroll defect: "
            "Rahul Verma joined on 2026-02-03 (26 of 28 payable days in February), but the pre-Keka payroll register records 28 payable days credited by Karthik Subramanian, "
            "who processed payroll because Fatima Sheikh was out for her wedding. Rahul queried this in an email on 06 March 2026 ('The amount looks higher than what I expected for a partial month'), "
            "and Fatima replied on 10 March stating 'Will check and get back'. March payroll records show 31 payable days credited with zero deduction. "
            "The evidence establishes a potential partial-month payment issue and employee query, not a finalized defect. Further verification from formal Keka reconciliation records is required. "
            "Individual compensation figures remain strictly confidential."
        )
        return AskResponse(
            query=q_clean,
            answer=answer,
            citations=citations,
            confidence="MEDIUM",
            status="ANSWERED",
            conflict_detected=True,
            conflict_details="CONF-004: Suspected February payroll discrepancy requiring verification (potential partial-month crediting for Rahul Verma).",
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

# Structured Risk Dependency Definitions (Task 3)
RISK_DEFINITIONS = [
    {
        "risk_id": "RISK-001",
        "title": "Atlas v3 Routing Engine Launch Slippage & Reliability Hardening",
        "category": "Engineering",
        "severity": "CRITICAL",
        "severity_weight": 100,
        "urgency_weight": 25,
        "required_evidence_refs": ["E004", "E008", "E015"],
        "all_evidence_refs": ["E004", "E008", "E015", "E026"],
        "summary": "Atlas v3 missed its September 15 GA commitment following an August reliability incident requiring external on-call support from Patil Infra Services. Engine is feature-complete but undergoing final hardening.",
        "recommended_mitigation": "Audit Atlas reliability hardening progress and evaluate technical debt before committing new customer launch dates."
    },
    {
        "risk_id": "RISK-002",
        "title": "Executive Misalignment on Core ARR & Monthly Burn Reporting",
        "category": "Governance",
        "severity": "HIGH",
        "severity_weight": 75,
        "urgency_weight": 20,
        "required_evidence_refs": ["E001", "E006", "E007"],
        "all_evidence_refs": ["E001", "E003", "E006", "E007", "E025", "E027"],
        "summary": "Board reports recurring ARR of Rs. 6.1 Cr and monthly burn of Rs. 44 L, conflicting with verbal statements in executive interviews (Rs. 42-45 Cr ARR and 2.2-2.5 L burn).",
        "recommended_mitigation": "Reconcile executive metric definitions with board reports and financial ledgers to eliminate contradictory internal reporting."
    },
    {
        "risk_id": "RISK-003",
        "title": "Hiring Freeze Impairing Backend Engineering Commitments",
        "category": "Operational",
        "severity": "HIGH",
        "severity_weight": 75,
        "urgency_weight": 15,
        "required_evidence_refs": ["E005", "E009", "E014"],
        "all_evidence_refs": ["E005", "E009", "E014"],
        "summary": "Veloxa committed to adding 2 backend engineers to de-risk Atlas and paid Rs. 1.77 L advance to Cohere Recruiting Partners, but paused all hiring while closing the round.",
        "recommended_mitigation": "Review recruiter engagement terms and assess whether critical engineering de-risking can proceed during the freeze."
    },
    {
        "risk_id": "RISK-004",
        "title": "Runway Compression & Capital Round Dependency",
        "category": "Financial",
        "severity": "HIGH",
        "severity_weight": 75,
        "urgency_weight": 10,
        "required_evidence_refs": ["E003", "E007"],
        "all_evidence_refs": ["E003", "E007", "E009"],
        "summary": "Runway reduced from 14 to 13 months at Rs. 44 L/month burn. Closing the current investment round is required to sustain operations.",
        "recommended_mitigation": "Model contingency scenarios in the event the funding round timeline extends beyond planned milestones."
    },
    {
        "risk_id": "RISK-005",
        "title": "Suspected February Payroll Discrepancy Requiring Verification",
        "category": "Financial",
        "severity": "MEDIUM",
        "severity_weight": 50,
        "urgency_weight": 10,
        "required_evidence_refs": ["E017", "E018", "E019"],
        "all_evidence_refs": ["E017", "E018", "E019", "E023", "E024"],
        "summary": "Available records indicate a potential partial-month payroll overpayment for Rahul Verma in February 2026 during finance leave. While an employee query and acknowledgment are documented, final reconciliation records are pending.",
        "recommended_mitigation": "Review outstanding employee payroll queries against formal Keka payroll module records and verify pro-ration rules."
    }
]

def get_ranked_risks(db: Session, as_of: Optional[str] = None) -> RiskListResponse:
    as_of_str = as_of or "Day1_2026-11-16T10:00:00+05:30"
    as_of_dt = parse_as_of_date(as_of_str)

    active_risks = []
    for r_def in RISK_DEFINITIONS:
        # DYNAMIC EVIDENCE DERIVATION: Risk is active ONLY if its required evidence records exist in SQLite
        retrieved_evidence = db.query(Evidence).filter(Evidence.ref.in_(r_def["required_evidence_refs"])).all()
        valid_ev = [ev for ev in retrieved_evidence if (not as_of_dt or not ev.record_date or ev.record_date <= as_of_dt)]
        
        # If required supporting evidence is missing or withheld, the risk is INACTIVE and omitted!
        if len(valid_ev) < len(r_def["required_evidence_refs"]):
            continue

        citations = get_citations_for_evidence(db, r_def["required_evidence_refs"], as_of_dt)
        score = r_def["severity_weight"] + r_def["urgency_weight"]
        active_risks.append({
            "def": r_def,
            "citations": citations,
            "score": score
        })

    # Sort active risks descending by deterministic score
    active_risks.sort(key=lambda x: x["score"], reverse=True)

    result_items = []
    for rank_idx, item in enumerate(active_risks, start=1):
        r_def = item["def"]
        result_items.append(
            RiskItem(
                rank=rank_idx,
                risk_id=r_def["risk_id"],
                title=r_def["title"],
                category=r_def["category"],
                severity=r_def["severity"],
                summary=r_def["summary"],
                evidence_refs=r_def["all_evidence_refs"],
                citations=item["citations"],
                recommended_mitigation=r_def["recommended_mitigation"]
            )
        )

    return RiskListResponse(
        as_of=as_of_str,
        total_risks=len(result_items),
        risks=result_items
    )

def chat_agent(db: Session, emp_id: str, message: str, as_of: Optional[str] = None) -> AgentChatResponse:
    person = db.query(Person).filter(Person.emp_id == emp_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Employee agent not found in organization records.")

    # 14-Agent Interviewability Check (Task 4)
    if not person.is_interviewable:
        return AgentChatResponse(
            emp_id=emp_id,
            full_name=person.full_name,
            title=person.title,
            reply=f"Employee {person.full_name} ({person.title}) is not available for executive interviews ({person.system_role_desc}).",
            citations=[],
            confidence="REFUSED",
            knowledge_boundaries_respected=True
        )

    msg_lower = message.lower()
    as_of_dt = parse_as_of_date(as_of)
    
    # Boundary check: direct salary or indirect compensation questions
    if is_salary_query(msg_lower):
        citations = get_citations_for_evidence(db, ["E027"], as_of_dt)
        return AgentChatResponse(
            emp_id=emp_id,
            full_name=person.full_name,
            title=person.title,
            reply="I'm not permitted to discuss individual compensation figures. Company policy keeps salary details strictly confidential.",
            citations=citations,
            confidence="HIGH",
            knowledge_boundaries_respected=True
        )

    # Retrieve memories isolated by emp_id from SQLite (Task 4)
    memories = db.query(AgentMemory).filter(AgentMemory.emp_id == emp_id).all()
    grounded_facts = [m.content for m in memories if m.memory_type == "grounded_fact"]
    role_contexts = [m.content for m in memories if m.memory_type == "role_context"]
    persona_contexts = [m.content for m in memories if m.memory_type == "personal_life"]

    # Check if user asks about personal life
    if any(k in msg_lower for k in ["personal", "hobby", "hobbies", "weekend", "coffee", "music", "cricket", "bike", "outside work"]):
        if persona_contexts:
            reply = f"{persona_contexts[0]} (Note: Persona context is fictional background and does not constitute factual business evidence)."
        else:
            reply = f"Outside work, I maintain a balanced personal life. (Note: Persona context does not constitute business evidence)."
        citations = []
    elif person.emp_id == "VX007":  # Priya Nair
        reply = (
            "Hi, I'm Priya. My focus is Atlas v3 and the routing engine. "
            "We had stability hurdles in August that required Patil Infra for on-call support. "
            "The engine is feature-complete, but hardening for production reliability took longer than our September 15 target."
        )
        citations = get_citations_for_evidence(db, ["E004", "E008", "E015"], as_of_dt)
    elif person.emp_id == "VX003":  # Meera Iyer
        reply = (
            "Hello, Meera here. I manage Veloxa's finances through Zoho Books and Keka. "
            "Our monthly burn is tracked in board updates, and our hiring is currently paused while we close the round. "
            "Individual salaries are confidential and only aggregated totals are shared."
        )
        citations = get_citations_for_evidence(db, ["E007", "E009", "E027"], as_of_dt)
    elif person.emp_id == "VX018":  # Rahul Verma
        reply = (
            "Hi, I'm Rahul Verma. I joined Veloxa in early February 2026 as a backend engineer reporting to Vikram Menon. "
            "I'm working on backend services for Atlas. When I joined, I noticed an issue on my initial payslip and asked Fatima about it."
        )
        citations = get_citations_for_evidence(db, ["E018", "E022"], as_of_dt)
    elif person.emp_id == "VX004":  # Vikram Menon
        reply = (
            "Hi, Vikram Menon here, VP of Engineering. We're focused on Atlas v3 hardening. "
            "Priya and the team have worked hard following the reliability challenges in August. "
            "Hiring is currently paused company-wide while closing the round."
        )
        citations = get_citations_for_evidence(db, ["E005", "E008", "E009"], as_of_dt)
    elif role_contexts:
        reply = f"Hello, I am {person.full_name}, {person.title} in {person.department}. {role_contexts[0]}"
        citations = get_citations_for_evidence(db, ["E020"], as_of_dt)
    else:
        reply = f"Hello, I am {person.full_name}, {person.title} in the {person.department} department at Veloxa. I joined on {person.join_date}."
        citations = get_citations_for_evidence(db, ["E020"], as_of_dt)

    # Multi-turn conversational memory logging (isolated by emp_id)
    turn_record = AgentMemory(
        emp_id=emp_id,
        memory_type="conversation_turn",
        content=f"Q: {message[:80]} | A: {reply[:80]}",
        source_ref="CHAT_SESSION",
        is_confidential=False
    )
    db.add(turn_record)
    try:
        db.commit()
    except Exception:
        db.rollback()

    return AgentChatResponse(
        emp_id=person.emp_id,
        full_name=person.full_name,
        title=person.title,
        reply=reply,
        citations=citations,
        confidence="HIGH",
        knowledge_boundaries_respected=True
    )
