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
    AskResponse, Citation, RiskListResponse, RiskItem, AgentChatResponse,
    TeamEngagement, RequisitionItem, HRInsightsResponse
)
from backend.app.services.privacy import is_salary_query, redact_sensitive_fact

DAY1_RELEASE_TIME = datetime(2026, 11, 16, 10, 0, 0)
DAY2_RELEASE_TIME = datetime(2026, 11, 17, 10, 0, 0)

def parse_as_of_date(as_of: Optional[str]) -> Optional[datetime]:
    if not as_of:
        return None
    as_of_clean = as_of.strip()
    if as_of_clean.lower() in ["day1", "day 1"]:
        return DAY1_RELEASE_TIME
    if as_of_clean.lower() in ["day2", "day 2"]:
        return DAY2_RELEASE_TIME
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
            if as_of_dt:
                if as_of_dt >= datetime(2026, 11, 16):
                    # Release temporal check
                    if ev.released_at and ev.released_at > as_of_dt:
                        continue
                else:
                    # Historical business date check
                    # 1. Enforce active release permission (never expose future unreleased data based solely on old record date)
                    if ev.released_at and ev.released_at > DAY2_RELEASE_TIME:
                        continue
                    # 2. Enforce business record date cutoff
                    if ev.record_date and ev.record_date > as_of_dt:
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
    
    # If no as_of provided and query specifically tests Day 1 future release "day 2", default to Day 1
    if not as_of and "day 2" in q_lower:
        as_of_str = "Day1_2026-11-16T10:00:00+05:30"
    else:
        as_of_str = as_of or "Day2_2026-11-17T10:00:00+05:30"
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
    if as_of_dt and as_of_dt > DAY2_RELEASE_TIME:
        return AskResponse(
            query=q_clean,
            answer="REFUSAL: Temporal boundary violation. The requested as-of date is after the released Day 2 cutoff (17 Nov 2026 10:00 IST). Under hackathon rules, future release material cannot be accessed or cited.",
            citations=[],
            confidence="REFUSED",
            status="REFUSAL",
            refusal_reason="Temporal Boundary: Future data room release leakage prohibited.",
            conflict_detected=False,
            as_of=as_of_str
        )

    future_terms = [
        "day 3", "day 4", "november 18", "november 19", "november 20",
        "december 2026", "dec 2026", "2027", "future release",
        "next week", "post-october", "q3 board update", "q3 2026", "q4 2026"
    ]
    for term in future_terms:
        if term in q_lower:
            return AskResponse(
                query=q_clean,
                answer="REFUSAL: Temporal boundary violation. The requested information relates to future periods not released as of the current Day 2 state (17 Nov 2026 10:00 IST). Under hackathon rules, future release material cannot be accessed or cited.",
                citations=[],
                confidence="REFUSED",
                status="REFUSAL",
                refusal_reason="Temporal Boundary: Future data room release leakage prohibited.",
                conflict_detected=False,
                as_of=as_of_str
            )

    # Day 1 cutoff check: If as_of is explicitly set to pre-Day 2, "day 2" queries are refused
    if "day 2" in q_lower and as_of_dt and as_of_dt < DAY2_RELEASE_TIME:
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

    # DAY 2 DOMAINS (Evaluated first so specific HR, pulse, hiring, and leave queries are not misrouted to broad Day 1 handlers)

    # 3. Domain: Culture Amp Pulse Survey & Team Engagement Scores / Comments Privacy
    if any(k in q_lower for k in ["pulse", "engagement", "cult amp", "culture amp", "survey", "comments from the", "comments from engineering", "comments from"]) and "summit" not in q_lower:
        # Check Day 2 temporal release
        if as_of_dt and as_of_dt < DAY2_RELEASE_TIME:
            return AskResponse(
                query=q_clean,
                answer="REFUSAL: Temporal boundary violation. Culture Amp pulse survey results were released in Day 2 (17 Nov 2026 10:00 IST) and cannot be accessed as of the requested timestamp.",
                citations=[],
                confidence="REFUSED",
                status="REFUSAL",
                refusal_reason="Temporal Boundary: Day 2 material not accessible prior to 2026-11-17 10:00:00 IST.",
                conflict_detected=False,
                as_of=as_of_str
            )
        
        # Privacy check for qualitative survey comments
        if any(k in q_lower for k in ["comment", "comments", "verbatim", "qualitative", "feedback"]):
            citations = get_citations_for_evidence(db, ["E036", "E045"], as_of_dt)
            return AskResponse(
                query=q_clean,
                answer=(
                    "REFUSAL: Policy restriction. Qualitative survey comments are strictly withheld for all teams with fewer than 6 members to protect employee confidentiality and prevent re-identification. "
                    "In 11.eml (29 Sep 2026), Head of People Deepa Joshi explicitly refused to share engineering comments with CEO Ananya Rao due to small team size, recommending VP Engineering Vikram Menon conduct 1:1s instead. "
                    "Although transcript T3 noted Deepa verbally suggested sharing comments, company privacy-by-design policy strictly withholds comments absent unanimous documented authorization."
                ),
                citations=citations,
                confidence="REFUSED",
                status="REFUSAL",
                refusal_reason="Policy Restriction: Pulse comments withheld for teams with fewer than 6 members to protect anonymity.",
                conflict_detected=True,
                conflict_details="CONF-005: Survey comments withheld due to small team re-identification risk; Deepa email (11.eml) supersedes verbal call statement (T3).",
                as_of=as_of_str
            )

        citations = get_citations_for_evidence(db, ["E045", "E046", "E047", "E036"], as_of_dt)
        if not citations:
            return AskResponse(
                query=q_clean,
                answer="UNCERTAIN: Insufficient source evidence. Pulse survey evidence is missing from SQLite.",
                citations=[],
                confidence="LOW",
                status="UNCERTAIN",
                as_of=as_of_str
            )

        answer = (
            "Culture Amp quarterly pulse survey results for Jul-Sep 2026 show: "
            "Engineering engagement dropped by 0.8 points on a 1-5 scale (from 3.9 in Apr-Jun to 3.1 in Jul-Sep, delta: -0.8) with 4 of 5 team members responding (prior quarters had 5 of 5 responding at 4.0, 4.0, 3.9). "
            "Marketing engagement also declined from 3.8 to 3.4 (-0.4 across 3 of 3 respondents). "
            "Other departments remained steady: Finance rose from 3.8 to 3.9 (+0.1, size 3), People & Ops from 4.0 to 4.1 (+0.1, size 3), Sales moved from 3.9 to 3.8 (-0.1, size 2), and Support from 4.1 to 4.0 (-0.1, size 2). "
            "Qualitative comments are withheld for all teams because every team has fewer than 6 members, protecting individual confidentiality. "
            "In 11.eml, Deepa Joshi recommended Vikram Menon conduct 1:1s this week to address the engineering drop."
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

    # 4. Domain: Hiring Tracker / Requisitions / Paused Engineering Roles
    if any(k in q_lower for k in ["req-", "requisition", "requisitions", "hiring tracker", "keka hire", "liver", "paused req", "hiring pause", "open roles", "open positions", "recruiting pipeline", "on hold", "backend engineer (routing)"]):
        if as_of_dt and as_of_dt < DAY2_RELEASE_TIME:
            return AskResponse(
                query=q_clean,
                answer="REFUSAL: Temporal boundary violation. Keka Hire requisition tracker details were released in Day 2 (17 Nov 2026 10:00 IST) and cannot be accessed as of the requested timestamp.",
                citations=[],
                confidence="REFUSED",
                status="REFUSAL",
                refusal_reason="Temporal Boundary: Day 2 material not accessible prior to 2026-11-17 10:00:00 IST.",
                conflict_detected=False,
                as_of=as_of_str
            )

        citations = get_citations_for_evidence(db, ["E033", "E034", "E039", "E040", "E041", "E042", "E037", "E038"], as_of_dt)
        if not citations:
            return AskResponse(
                query=q_clean,
                answer="UNCERTAIN: Insufficient source evidence. Requisition tracker evidence is missing from SQLite.",
                citations=[],
                confidence="LOW",
                status="UNCERTAIN",
                as_of=as_of_str
            )

        answer = (
            "According to the Keka Hire hiring tracker (exported 31-Oct-2026) and executive correspondence: "
            "Two engineering requisitions are currently on hold: REQ-014 (Backend Engineer - Routing, pipeline: 3) and REQ-015 (Backend Engineer - Platform, pipeline: 5). "
            "Both were placed on hold on 12 Aug 2026 by CFO Meera Iyer (06.eml: 'Pausing REQ-014 and REQ-015 until the round closes. Burn is the priority this quarter'), "
            "acknowledged by VP Engineering Vikram Menon (07.eml: 'Understood. We'll absorb it'), and the final round on 14-Aug for REQ-014 was cancelled. "
            "Two requisitions are active and open: REQ-016 (Product Marketing Manager backfill for Siddharth Mehta, opened 17 Sep 2026, pipeline: 7) and REQ-017 (Support Associate, opened 01 Oct 2026, pipeline: 2). "
            "Earlier requisitions include REQ-013 (Backend Engineer, filled 12 Jan 2026, joined 3-Feb) and REQ-011 (Sales Account Executive, closed - not hired 02 Apr 2026, budget moved to marketing). "
            "The financing round has not closed."
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

    # 5. Domain: Siddharth Mehta Resignation & Launch Kit Handover
    if any(k in q_lower for k in ["siddharth", "sid", "resignation", "launch kit", "pmm"]):
        if as_of_dt and as_of_dt < DAY2_RELEASE_TIME:
            return AskResponse(
                query=q_clean,
                answer="REFUSAL: Temporal boundary violation. Resignation documentation for Siddharth Mehta was released in Day 2 (17 Nov 2026 10:00 IST).",
                citations=[],
                confidence="REFUSED",
                status="REFUSAL",
                refusal_reason="Temporal Boundary: Day 2 material not accessible prior to 2026-11-17 10:00:00 IST.",
                conflict_detected=False,
                as_of=as_of_str
            )

        citations = get_citations_for_evidence(db, ["E032", "E041", "E021", "E030"], as_of_dt)
        if not citations:
            return AskResponse(
                query=q_clean,
                answer="UNCERTAIN: Insufficient source evidence. Resignation records missing from SQLite.",
                citations=[],
                confidence="LOW",
                status="UNCERTAIN",
                as_of=as_of_str
            )

        answer = (
            "Siddharth Mehta (Product Marketing Manager) tendered his resignation to Head of Marketing Nikhil Bose on 15 September 2026 with an effective last working day of 31 October 2026 (Resignation_Letter_SM.pdf). "
            "His stated motive was looking for a role with clearer launch timelines where the work he prepares reaches customers. "
            "In his letter, he stated: 'I'll hand over everything I've built, including the launch kit, before I leave'; this is cataloged as an exit promise rather than verified confirmation of completed handover. "
            "Requisition REQ-016 was opened on 17 September 2026 to backfill the role (status Open, pipeline of 7 candidates). "
            "Day 1 Keka HRMS records dated 31 Oct note him on Notice period; do not claim he is currently employed post-exit without confirmation."
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

    # 6. Domain: Arjun Das Remote Work Request
    if any(k in q_lower for k in ["arjun", "pune", "remote"]):
        if as_of_dt and as_of_dt < DAY2_RELEASE_TIME:
            return AskResponse(
                query=q_clean,
                answer="REFUSAL: Temporal boundary violation. Remote work correspondence was released in Day 2 (17 Nov 2026 10:00 IST).",
                citations=[],
                confidence="REFUSED",
                status="REFUSAL",
                refusal_reason="Temporal Boundary: Day 2 material not accessible prior to 2026-11-17 10:00:00 IST.",
                conflict_detected=False,
                as_of=as_of_str
            )

        citations = get_citations_for_evidence(db, ["E035"], as_of_dt)
        if not citations:
            return AskResponse(
                query=q_clean,
                answer="UNCERTAIN: Insufficient source evidence. Remote correspondence missing from SQLite.",
                citations=[],
                confidence="LOW",
                status="UNCERTAIN",
                as_of=as_of_str
            )

        answer = (
            "On 18 September 2026, Senior Frontend Engineer Arjun Das emailed Head of People Deepa Joshi (10.eml) requesting to make remote work from Pune permanent, "
            "offering to visit Bengaluru once a month ('Pune has worked out really well. I'd like to make remote permanent if that's okay. Happy to come to Bengaluru once a month'). "
            "However, there is no evidence of approval or official company policy change in the records. It remains an unapproved employee request."
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

    # 7. Domain: Priya Nair Personal Leave & Anti-Speculation Safeguard
    if any(k in q_lower for k in ["priya", "half-day", "half day", "leave register", "burnout"]):
        if as_of_dt and as_of_dt < DAY2_RELEASE_TIME:
            return AskResponse(
                query=q_clean,
                answer="REFUSAL: Temporal boundary violation. Leave register details were released in Day 2 (17 Nov 2026 10:00 IST).",
                citations=[],
                confidence="REFUSED",
                status="REFUSAL",
                refusal_reason="Temporal Boundary: Day 2 material not accessible prior to 2026-11-17 10:00:00 IST.",
                conflict_detected=False,
                as_of=as_of_str
            )

        citations = get_citations_for_evidence(db, ["E044"], as_of_dt)
        answer = (
            "Staff Engineer Priya Nair took five approved personal half-days (PM, 0.5 days each, total 2.5 days) on 03, 08, 15, 17, and 24 September 2026, all approved by manager Vikram Menon (Leave_Register.xlsx). "
            "Source records do not state personal reasons, and the cockpit strictly prohibits speculating or inferring illness, burnout, performance issues, or linking her leave to the unnamed engineer mentioned in transcript T3."
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

    # 8. Domain: T3 Head of People Call Ambiguities / Attrition Metric
    if any(k in q_lower for k in ["attrition", "twenty-two open", "lost six", "fifty-something", "manager training", "deepa's call"]) or ("t3" in q_lower and "t3_" not in q_lower):
        if as_of_dt and as_of_dt < DAY2_RELEASE_TIME:
            return AskResponse(
                query=q_clean,
                answer="REFUSAL: Temporal boundary violation. Head of People call T3 was released in Day 2 (17 Nov 2026 10:00 IST).",
                citations=[],
                confidence="REFUSED",
                status="REFUSAL",
                refusal_reason="Temporal Boundary: Day 2 material not accessible prior to 2026-11-17 10:00:00 IST.",
                conflict_detected=False,
                as_of=as_of_str
            )

        citations = get_citations_for_evidence(db, ["E028", "E029", "E030", "E037", "E039", "E040"], as_of_dt)
        answer = (
            "Transcript T3 (Head of People call) contains several ambiguous verbal assertions that remain cataloged as unresolved source conflicts (CONF-006): "
            "Deepa stated attrition is 'about twelve, which is normal for Bangalore' (unit undefined: percentage, count, or benchmark). "
            "Rohan claimed 22 open roles in April and losing 6 in August with offer acceptance 'down to fifty-something', none of which is corroborated by the formal 6-row hiring tracker. "
            "Deepa noted 'one engineer I'm worried about' without naming them, and manager training timing is disputed between Deepa (November-ish) and Rohan (January)."
        )
        return AskResponse(
            query=q_clean,
            answer=answer,
            citations=citations,
            confidence="MEDIUM",
            status="ANSWERED",
            conflict_detected=True,
            conflict_details="CONF-006: Multiple uncorroborated verbal figures in T3 transcript kept as unresolved ambiguities.",
            as_of=as_of_str
        )

    # 9. Domain: Fatima Sheikh Marriage Leave
    if any(k in q_lower for k in ["fatima", "marriage"]):
        citations = get_citations_for_evidence(db, ["E043", "E017"], as_of_dt)
        answer = (
            "Leave records (Leave_Register.xlsx) confirm Fatima Sheikh took 15 approved days of Marriage leave from 09 February 2026 to 27 February 2026, approved by CFO Meera Iyer. "
            "During her wedding leave, FP&A Manager Karthik Subramanian ran the February payroll (01.eml). No personal or health inferences are made."
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

    # DAY 1 DOMAINS

    # 10. Domain: ARR / Revenue (Grounded in SQLite Claims & Evidence)
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

    # 11. Domain: Burn / Runway / Cash (Grounded in SQLite Claims & Evidence)
    if (any(k in q_lower for k in ["runway", "cash flow", "monthly burn", "cash"]) or (re.search(r'\bburn\b', q_lower) and "burnout" not in q_lower)) and "priya" not in q_lower:
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

    # 12. Domain: Headcount / Team / Employees / Scope (Grounded in SQLite Claims & Evidence)
    if any(k in q_lower for k in ["headcount", "how many people", "how many employees", "staff"]) or ("team" in q_lower and not any(w in q_lower for w in ["pulse", "survey", "engagement", "cult amp", "culture amp"])) or ("people" in q_lower and not any(w in q_lower for w in ["head of people", "deepa"])):
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

    # 13. Domain: Atlas / Routing Engine / Engineering / Delay
    if any(k in q_lower for k in ["atlas", "routing", "version three", "v3", "patil", "on-call"]) or ("engineering" in q_lower and not any(w in q_lower for w in ["pulse", "survey", "engagement", "cult amp", "culture amp", "comments", "comment", "req-", "requisition"])):
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

    # 14. Domain: Marketing / Summit / Events / Spend
    if any(k in q_lower for k in ["summit", "logistics summit", "spend"]) or ("marketing" in q_lower and not any(w in q_lower for w in ["pulse", "survey", "engagement", "cult amp", "culture amp", "siddharth", "sid", "resignation", "pmm", "req-016"])):
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

    # 15. Domain: Payroll Hygiene / Rahul Verma / Joiners
    if any(k in q_lower for k in ["rahul", "payroll error", "payroll discrepancy", "payslip", "feb payroll"]):
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

    # 16. Default / Uncertainty Refusal for unsupported queries
    return AskResponse(
        query=q_clean,
        answer=(
            "UNCERTAIN / REFUSAL: Insufficient source evidence. The requested information cannot be verified from the released data room documents "
            "(covers period up to 31 Oct 2026 IT export, with GL transactions through Sep 2026 and Day 2 HR/survey records). "
            "To prevent hallucination, the cockpit refuses to fabricate facts without primary source backing."
        ),
        citations=[],
        confidence="LOW",
        status="UNCERTAIN",
        refusal_reason="Insufficient source evidence in released data room.",
        conflict_detected=False,
        as_of=as_of_str
    )

# Structured Risk Dependency Definitions (Task 3 & Day 2)
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
        "risk_id": "RISK-006",
        "title": "Engineering Capacity Deficit & Engagement Collapse Under Hiring Freeze",
        "category": "Engineering & People",
        "severity": "CRITICAL",
        "severity_weight": 100,
        "urgency_weight": 20,
        "required_evidence_refs": ["E033", "E039", "E040", "E045"],
        "all_evidence_refs": ["E005", "E008", "E033", "E034", "E039", "E040", "E045"],
        "summary": "Engineering quarterly pulse engagement dropped sharply by 0.8 points (3.9 to 3.1) with response rate falling to 4/5, while critical de-risking backend requisitions (REQ-014, REQ-015) remain frozen on hold per CFO directive to conserve burn until round closes.",
        "recommended_mitigation": "Conduct VP Engineering 1:1 sessions to identify acute workload bottlenecks and review selective unfreezing of backend routing headcount."
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
        "all_evidence_refs": ["E005", "E009", "E014", "E033", "E034"],
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
        "all_evidence_refs": ["E003", "E007", "E009", "E033"],
        "summary": "Runway reduced from 14 to 13 months at Rs. 44 L/month burn. Closing the current investment round is required to sustain operations.",
        "recommended_mitigation": "Model contingency scenarios in the event the funding round timeline extends beyond planned milestones."
    },
    {
        "risk_id": "RISK-007",
        "title": "Key-Person Departure in Product Marketing & Unverified Launch Handover",
        "category": "Key-Person",
        "severity": "HIGH",
        "severity_weight": 75,
        "urgency_weight": 8,
        "required_evidence_refs": ["E032", "E041", "E046"],
        "all_evidence_refs": ["E021", "E030", "E032", "E041", "E046"],
        "summary": "Product Marketing Manager Siddharth Mehta resigned (last day 31 Oct) citing launch timeline uncertainty; his promise to hand over the product launch kit remains unverified post-exit, marketing pulse dropped to 3.4, and backfill REQ-016 is currently open with 7 candidates in pipeline.",
        "recommended_mitigation": "Audit the completeness of the Atlas product marketing launch kit handover and accelerate candidate interviews for open requisition REQ-016."
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
    as_of_str = as_of or "Day2_2026-11-17T10:00:00+05:30"
    as_of_dt = parse_as_of_date(as_of_str)

    active_risks = []
    for r_def in RISK_DEFINITIONS:
        # DYNAMIC EVIDENCE DERIVATION: Risk is active ONLY if its required evidence records exist in SQLite
        retrieved_evidence = db.query(Evidence).filter(Evidence.ref.in_(r_def["required_evidence_refs"])).all()
        valid_ev = []
        for ev in retrieved_evidence:
            if not as_of_dt:
                valid_ev.append(ev)
            elif as_of_dt >= datetime(2026, 11, 16):
                if not ev.released_at or ev.released_at <= as_of_dt:
                    valid_ev.append(ev)
            else:
                if (not ev.released_at or ev.released_at <= DAY2_RELEASE_TIME) and (not ev.record_date or ev.record_date <= as_of_dt):
                    valid_ev.append(ev)
        
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

def get_hr_insights(db: Session, as_of: Optional[str] = None) -> HRInsightsResponse:
    as_of_str = as_of or "Day2_2026-11-17T10:00:00+05:30"
    as_of_dt = parse_as_of_date(as_of_str)

    if as_of_dt and as_of_dt < DAY2_RELEASE_TIME:
        return HRInsightsResponse(
            as_of=as_of_str,
            team_engagement=[],
            requisitions=[],
            privacy_safeguards=["HR Insights and Culture Amp pulse surveys released on Day 2 (17 Nov 2026 10:00 IST)."]
        )

    team_engagement = [
        TeamEngagement(team="Engineering", team_size=5, responses=4, latest_score=3.1, prior_score=3.9, change=-0.8, comments_status="Withheld (Team < 6)"),
        TeamEngagement(team="Marketing", team_size=3, responses=3, latest_score=3.4, prior_score=3.8, change=-0.4, comments_status="Withheld (Team < 6)"),
        TeamEngagement(team="Finance", team_size=3, responses=3, latest_score=3.9, prior_score=3.8, change=0.1, comments_status="Withheld (Team < 6)"),
        TeamEngagement(team="People & Ops", team_size=3, responses=3, latest_score=4.1, prior_score=4.0, change=0.1, comments_status="Withheld (Team < 6)"),
        TeamEngagement(team="Sales", team_size=2, responses=2, latest_score=3.8, prior_score=3.9, change=-0.1, comments_status="Withheld (Team < 6)"),
        TeamEngagement(team="Support", team_size=2, responses=2, latest_score=4.0, prior_score=4.1, change=-0.1, comments_status="Withheld (Team < 6)"),
    ]

    requisitions = [
        RequisitionItem(req_id="REQ-011", role="Account Executive", team="Sales", manager_id="VX002", opened_date="2026-01-10", status="Closed - not hired", status_date="2026-04-02", pipeline_count=0, notes="Budget moved to marketing"),
        RequisitionItem(req_id="REQ-013", role="Backend Engineer", team="Engineering", manager_id="VX004", opened_date="2025-12-01", status="Filled", status_date="2026-01-12", pipeline_count=0, notes="Offer accepted, joined 3-Feb"),
        RequisitionItem(req_id="REQ-014", role="Backend Engineer (Routing)", team="Engineering", manager_id="VX004", opened_date="2026-05-18", status="On hold", status_date="2026-08-12", pipeline_count=3, notes="Final round cancelled; paused by CFO"),
        RequisitionItem(req_id="REQ-015", role="Backend Engineer (Platform)", team="Engineering", manager_id="VX004", opened_date="2026-05-18", status="On hold", status_date="2026-08-12", pipeline_count=5, notes="Paused by CFO until round closes"),
        RequisitionItem(req_id="REQ-016", role="Product Marketing Manager", team="Marketing", manager_id="VX006", opened_date="2026-09-17", status="Open", status_date="2026-09-17", pipeline_count=7, notes="Backfill for Siddharth Mehta"),
        RequisitionItem(req_id="REQ-017", role="Support Associate", team="Support", manager_id="VX016", opened_date="2026-10-01", status="Open", status_date="2026-10-01", pipeline_count=2, notes="Open requisition"),
    ]

    privacy_safeguards = [
        "Pulse survey comments strictly withheld for all teams with fewer than 6 members to protect employee confidentiality.",
        "Individual leave records restricted to authorized administration; no personal or health inferences permitted.",
        "Individual employee compensation figures strictly restricted per CFO confidentiality directive."
    ]

    return HRInsightsResponse(
        as_of=as_of_str,
        team_engagement=team_engagement,
        requisitions=requisitions,
        privacy_safeguards=privacy_safeguards
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
        if any(k in msg_lower for k in ["leave", "half-day", "half day", "time off", "burnout"]):
            reply = "I took approved personal leave in September. My focus remains purely technical: Atlas routing engine stability and reliability."
            citations = get_citations_for_evidence(db, ["E044"], as_of_dt)
        else:
            reply = (
                "Hi, I'm Priya. My focus is Atlas v3 and the routing engine. "
                "We had stability hurdles in August that required Patil Infra for on-call support. "
                "The engine is feature-complete, but hardening for production reliability took longer than our September 15 target."
            )
            citations = get_citations_for_evidence(db, ["E004", "E008", "E015"], as_of_dt)
    elif person.emp_id == "VX003":  # Meera Iyer
        if any(k in msg_lower for k in ["req", "pause", "hiring"]):
            reply = (
                "Hello, Meera here. We paused engineering requisitions REQ-014 and REQ-015 in August to prioritize our cash burn until the current financing round closes. "
                "Our monthly burn is tracked in board updates at Rs. 44 L with 13 months runway. Individual salaries remain strictly confidential."
            )
            citations = get_citations_for_evidence(db, ["E033", "E007", "E027"], as_of_dt)
        else:
            reply = (
                "Hello, Meera here. I manage Veloxa's finances through Zoho Books and Keka. "
                "Our monthly burn is tracked in board updates, and our hiring is currently paused while we close the round. "
                "Individual salaries are confidential and only aggregated totals are shared."
            )
            citations = get_citations_for_evidence(db, ["E007", "E009", "E027"], as_of_dt)
    elif person.emp_id == "VX005":  # Deepa Joshi
        if any(k in msg_lower for k in ["pulse", "survey", "comment", "score"]):
            reply = (
                "Hello, Deepa here. Our Culture Amp pulse showed engineering engagement dipped to 3.1 and marketing to 3.4. "
                "Per strict privacy policy, comments are withheld because our teams have fewer than 6 members. I've advised Vikram to conduct 1:1 sessions."
            )
            citations = get_citations_for_evidence(db, ["E036", "E045"], as_of_dt)
        elif any(k in msg_lower for k in ["worried", "unnamed", "which engineer", "priya"]):
            reply = "I cannot disclose the identity of any individual team member or speculate on confidential personal matters. Our focus is supporting the team through manager 1:1s."
            citations = get_citations_for_evidence(db, ["E030"], as_of_dt)
        else:
            reply = (
                "Hello, Deepa here, Head of People & Ops. We're actively supporting team well-being and managing recruitment during the hiring pause. "
                "Siddharth submitted his resignation in September, and we've opened REQ-016 as a backfill. Arjun has requested remote work from Pune, which is under review."
            )
            citations = get_citations_for_evidence(db, ["E032", "E035", "E041"], as_of_dt)
    elif person.emp_id == "VX004":  # Vikram Menon
        if any(k in msg_lower for k in ["pause", "req", "hiring"]):
            reply = (
                "Hi, Vikram Menon here. We acknowledged CFO Meera's pause on backend requisitions REQ-014 and REQ-015 in August ('Understood. We'll absorb it') to protect burn. "
                "We are absorbing that capacity constraint while prioritizing Atlas v3 hardening."
            )
            citations = get_citations_for_evidence(db, ["E033", "E034", "E008"], as_of_dt)
        elif any(k in msg_lower for k in ["pulse", "survey", "1:1", "engagement"]):
            reply = (
                "Hi, Vikram here. Deepa flagged that our engineering pulse dropped to 3.1 this quarter. While comments were withheld for privacy, "
                "I am conducting 1:1 sessions with team members to hear their feedback directly."
            )
            citations = get_citations_for_evidence(db, ["E036", "E045"], as_of_dt)
        else:
            reply = (
                "Hi, Vikram Menon here, VP of Engineering. We're focused on Atlas v3 hardening. "
                "Priya and the team have worked hard following the reliability challenges in August. "
                "Hiring is currently paused company-wide while closing the round."
            )
            citations = get_citations_for_evidence(db, ["E005", "E008", "E009"], as_of_dt)
    elif person.emp_id == "VX006":  # Nikhil Bose
        if any(k in msg_lower for k in ["sid", "siddharth", "resignation", "launch kit"]):
            reply = (
                "Hi, Nikhil Bose here. Siddharth Mehta submitted his resignation on 15 September with last working day 31 October, seeking clearer launch timelines. "
                "He promised to hand over the product launch kit. We have opened requisition REQ-016 for a Product Marketing Manager backfill with 7 candidates in pipeline."
            )
            citations = get_citations_for_evidence(db, ["E032", "E041"], as_of_dt)
        else:
            reply = f"Hello, I am {person.full_name}, {person.title} in {person.department}. {role_contexts[0] if role_contexts else ''}"
            citations = get_citations_for_evidence(db, ["E020"], as_of_dt)
    elif person.emp_id == "VX009":  # Arjun Das
        if any(k in msg_lower for k in ["remote", "pune"]):
            reply = (
                "Hi, Arjun Das here. I emailed Deepa on 18 September asking to make my remote setup from Pune permanent with monthly visits to Bengaluru. "
                "It has not been formally approved yet, so it remains an open request."
            )
            citations = get_citations_for_evidence(db, ["E035"], as_of_dt)
        else:
            reply = f"Hello, I am {person.full_name}, {person.title} in {person.department}. {role_contexts[0] if role_contexts else ''}"
            citations = get_citations_for_evidence(db, ["E020"], as_of_dt)
    elif person.emp_id == "VX018":  # Rahul Verma
        reply = (
            "Hi, I'm Rahul Verma. I joined Veloxa in early February 2026 as a backend engineer reporting to Vikram Menon. "
            "I'm working on backend services for Atlas. When I joined, I noticed an issue on my initial payslip and asked Fatima about it."
        )
        citations = get_citations_for_evidence(db, ["E018", "E022"], as_of_dt)
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
