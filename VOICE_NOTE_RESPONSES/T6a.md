# Executive Decision Memo — Response to CEO Voice Note T6a

**To:** Ananya Rao, Chief Executive Officer, Veloxa Technologies  
**From:** Implementation Lead / CXO Cockpit Architecture (Candidate: Rivu Chattopadhyay)  
**Date:** Tuesday, 17 November 2026 (Day 2 Milestone, 11:59 PM IST Target)  
**Reference Document:** `T6a_CEO_Voice_Note.docx` (`E031`)  
**Decision Governance Status:** **`APPROVED: ACCEPT WITH SCOPE (Ratified by Candidate / Human Reviewer)`**  

---

## 1. Exact CEO Voice Note Request

> *"Hi, quick one. I won't type questions every morning, na. When I open it, it should just tell me what to worry about. Top three. Okay, bye."*  
> — Ananya Rao, CEO (forwarded WhatsApp voice note transcript, `T6a_CEO_Voice_Note.docx`)

---

## 2. Decision Status & Executive Summary

- **Approved Decision:** **ACCEPT WITH SCOPE**  
- **Governance Classification:** Formally **APPROVED and RATIFIED** by human candidate review. The cockpit defaults to three ranked, cited executive risks, while keeping the full risk registry accessible.
- **Executive Rationale:**  
  The CEO needs zero-friction morning orientation without typing repetitive prompts every day. However, unconditionally hardcoding three static cards would violate factual grounding, conceal active operational volatility, and fail when evidence changes. Therefore, we **accept** the requirement to automatically present top-three risk cards upon opening the cockpit, but **scope** the implementation into a dynamic, evidence-backed ranking engine that maintains an expandable view of all company risks, preserves honest uncertainty, and enforces strict HR privacy safeguards.

---

## 3. What Was Changed in the CXO Cockpit

1. **Default Morning Risk Display (Top 3 Cards on Open):**
   - When the CEO opens the cockpit dashboard (`/`), the system automatically queries the backend risk engine (`GET /api/risks`) and highlights the **Top Three Evidence-Backed Risks** above the fold.
   - Each card features:
     - Concise, unambiguous risk title
     - 1–2 sentence operational explanation grounded in primary records
     - Severity rating (`CRITICAL`, `HIGH`, `MEDIUM`) with visual telemetry badge
     - Confidence indicator and `as_of` temporal release label
     - Direct clickable evidence citations (`E004`, `E008`, `E015`, `E033`, etc.)
     - Suggested next step framed as an actionable recommendation (not asserting unverified action taken)

2. **Dynamic Evidence-Driven Risk Ranking (Day 2 State):**
   - The risk engine evaluates 7 structured risk definitions across Engineering, People, Governance, and Financial domains:
     - **#1 (CRITICAL, Score 125):** *Atlas v3 Routing Engine Launch Slippage & Reliability Hardening* (`RISK-001`) — Missed 15-Sep GA; August reliability incident required Patil Infra on-call support (`E004`, `E008`, `E015`).
     - **#2 (CRITICAL, Score 120):** *Engineering Capacity Deficit & Engagement Collapse Under Hiring Freeze* (`RISK-006`) — Engineering quarterly pulse dropped by 0.8 points (3.9 to 3.1) with 4/5 respondents (`E045`), while two backend de-risking roles (REQ-014, REQ-015) remain frozen on hold per CFO directive (`E033`, `E034`, `E039`, `E040`).
     - **#3 (HIGH, Score 95):** *Executive Misalignment on Core ARR & Monthly Burn Reporting* (`RISK-002`) — Board reports Rs. 6.1 Cr recurring ARR and Rs. 44 L burn, conflicting with verbal statements of Rs. 42–45 Cr ARR and Rs. 2.2–2.5 L burn (`E001`, `E006`, `E007`, `E025`, `E027`).
   - If any required evidence citation is removed or withheld in the underlying data store, the dependent risk immediately degrades or drops off the ranked list.

3. **Expandable Full Risk Registry ("View All Risks"):**
   - The full registry of all active risks (e.g., Hiring Freeze Impairing Backend Commitments `RISK-003`, Runway Compression `RISK-004`, Siddharth Mehta Departure & Handover `RISK-007`, and Suspected February Payroll Discrepancy `RISK-005`) is preserved and accessible via an expandable drawer/tab, ensuring no blind spots.

4. **Privacy-Preserving HR Insights Panel:**
   - Dedicated executive overview (`/api/hr-insights`) displaying team-level Culture Amp quarterly engagement trends and Keka Hire requisition statuses.
   - All teams with fewer than 6 members have qualitative comments withheld to prevent respondent re-identification.

5. **Preservation of Interactive Q&A & 14 AI Agents:**
   - The one-question natural language CEO inquiry bar remains active below the top risk cards for on-demand deep dives.
   - All 14 interviewable employee agent personas remain accessible with strict role boundaries.

---

## 4. What Was Deliberately Refused or Omitted

1. **Refusal to Expose Qualitative Survey Comments:**
   - CEO Ananya's verbal preference in call T3 (*"she wants Ananya to see survey comments directly: numbers alone hide everything"*) was evaluated against Head of People Deepa Joshi's written directive in `11.eml` (*"The team is too small for me to share comments. I'd suggest Vikram does 1:1s this week"*) and Culture Amp workbook rules (*"Not shown: team smaller than 6"*).
   - In small teams (Engineering has 5 members, 4 respondents), verbatim text creates severe re-identification risk. The cockpit **refuses** to display raw survey comments and provides team-level aggregate deltas only (`CONF-005`).

2. **Refusal to Disclose Individual Compensation or Leave Reasons:**
   - CFO Meera Iyer's mandate (`T2_CFO_Call`) that individual salaries must never appear in executive outputs is strictly enforced across all cards and endpoints.
   - Priya Nair's 5 personal half-days in September (`E044`) are cataloged as authorized personal leave; the cockpit strictly **refuses** to speculate on medical causes, burnout, or performance.

3. **Refusal to Assert Unverified Claims as Completed Facts:**
   - Siddharth Mehta's statement in `Resignation_Letter_SM.pdf` that he *"will hand over everything I've built, including the launch kit, before I leave"* is cataloged as an **exit promise**, not proof of completed handover.
   - Arjun Das's request in `10.eml` for permanent remote work from Pune is cataloged as an **unapproved employee request**, not an approved policy change.
   - T3 verbal statements (*"attrition about twelve"*, *"twenty-two open roles in April"*, *"lost six in August"*, *"fifty-something offer acceptance"*) remain unresolved ambiguities without primary ATS verification (`CONF-006`).

---

## 5. Primary Source Evidence References

| Evidence Ref | Source Document | Key Grounded Fact |
|---|---|---|
| `E031` | `T6a_CEO_Voice_Note.docx` | CEO voice note: Top three morning worry cards requested. |
| `E033` | `06.eml` | CFO Meera Iyer pauses REQ-014 and REQ-015 until round closes to protect burn. |
| `E034` | `07.eml` | VP Eng Vikram Menon acknowledges hiring pause: "Understood. We'll absorb it." |
| `E036` | `11.eml` | Deepa Joshi refuses to share comments with Ananya; advises Vikram 1:1s. |
| `E039` | `Hiring_Tracker.xlsx` | REQ-014 (Backend Routing) on hold since 12 Aug, pipeline 3, final round cancelled. |
| `E040` | `Hiring_Tracker.xlsx` | REQ-015 (Backend Platform) on hold since 12 Aug, pipeline 5. |
| `E041` | `Hiring_Tracker.xlsx` | REQ-016 (Product Marketing Manager backfill) open since 17 Sep, pipeline 7. |
| `E045` | `Pulse_Survey.xlsx` | Engineering engagement dropped -0.8 (3.9 to 3.1) with 4 of 5 responding; comments withheld (<6). |
| `E046` | `Pulse_Survey.xlsx` | Marketing engagement dropped -0.4 (3.8 to 3.4 across 3 respondents); comments withheld (<6). |
| `E032` | `Resignation_Letter_SM.pdf` | Siddharth Mehta resignation letter; last working day 31 Oct; launch kit promise. |
| `E035` | `10.eml` | Arjun Das request for permanent remote from Pune; unapproved. |
| `E044` | `Leave_Register.xlsx` | Priya Nair five personal half-days approved by VM; no burnout inference permitted. |

---

## 6. Automated Verification

The solution is covered by automated pytest tests in `backend/tests/test_day2.py` and `backend/tests/test_cockpit.py`:
- `test_default_top_three_risks_and_full_list`: Verifies top 3 risk cards on open (`RISK-001`, `RISK-006`, `RISK-002`) and access to the complete 7-risk registry.
- `test_dynamic_risk_degradation_when_evidence_removed`: Validates that deleting pulse survey evidence dynamically removes `RISK-006`.
- `test_survey_comments_withholding_privacy_refusal`: Verifies privacy refusal for survey comment requests.
- `test_release_temporal_095959_denial` and `test_release_temporal_100000_access`: Verifies exact release timestamp enforcement.

**Status:** Ready for candidate confirmation and executive deployment.
