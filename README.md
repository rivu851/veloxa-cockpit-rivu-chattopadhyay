# Veloxa CXO Cockpit — Executive Intelligence & Governance System

**Candidate:** Rivu Chattopadhyay  
**Hackathon Assessment:** Hiyaku Systems individual Veloxa CXO Cockpit hackathon  
**Timeline:** Monday 16 Nov 2026 10:00 IST through Friday 20 Nov 2026 18:00 IST  
**Public Repository:** [https://github.com/rivu851/veloxa-cockpit-rivu-chattopadhyay](https://github.com/rivu851/veloxa-cockpit-rivu-chattopadhyay)  
**Day 1 Release Milestone:** Mon 16 Nov 2026 by 23:59 IST (Architecture & Baseline Scaffold)  
**Day 2 Release Milestone:** Tue 17 Nov 2026 by 23:59 IST (Day 2 Source Ingestion & T6a Executive Response)  
**Day 3 Release Milestone:** Wed 18 Nov 2026 by 10:00 IST (Day 3 Ingestion, T6b Governance Response & Cockpit Extensions)  

---

## 1. Executive Summary

The **Veloxa CXO Cockpit** is a full-stack executive intelligence platform built for the CEO and leadership of Veloxa Technologies. It unifies disparate, contradictory, and unstructured operational data rooms—including Keka HRMS, Zoho Books general ledgers, board governance decks, pre-Keka payroll registers, executive call transcripts, Culture Amp pulse surveys, Keka Hire requisition trackers, and personal leave registers—into an authoritative, evidence-backed decision system.

### Key Capabilities
- **Deterministic Factual Grounding:** Every factual answer is linked to granular citations (`E001`, `E002`, ... `E047`) preserving exact source file, sheet, page, and row coordinates.
- **T6a Default Morning Risk Briefing:** Implements zero-click executive risk assessment on startup answering CEO voice note T6a ("tell me what to worry about. Top three") with confidence, concise action/why, expandable evidence, and full risk list toggle.
- **Strict Salary & Survey Privacy at Service Layer:** Enforces CFO Meera Iyer's directive (`T2_CFO_Call`) preventing individual compensation from appearing in queries, and Deepa Joshi's directive (`11.eml`) strictly withholding qualitative pulse comments for teams under 6 members to protect employee anonymity.
- **Honest Refusal & Uncertainty Engine:** Explicitly distinguishes confirmed facts from disputed claims and inferred interpretations. Refuses to hallucinate when source evidence is absent or temporal boundaries are crossed.
- **Temporal Dual-Axis Time-Travel (`as_of`):** Historical queries filter evidence by effective business dates and data room release timestamps (`2026-11-17T10:00:00+05:30` cutoff), preventing future release leakage.
- **14 Grounded AI Employee Agents:** Conversational AI personas grounded in official Keka HRMS records operating within verified knowledge boundaries.
- **Human-in-the-Loop Conflict Governance:** Contradictions between verbal executive statements and audited board decks or trackers are cataloged with proposed interpretations and marked `UNRESOLVED` pending human confirmation.

---

## 2. Key Data Room Conflicts Identified

Six consequential source discrepancies were uncovered across Day 1 and Day 2 data rooms and cataloged in [DECISIONS.md](DECISIONS.md):

1. **CONF-001 (ARR Discrepancy):** Board Update reports **Rs. 6.1 Crore recurring ARR** (Q2 Jul-Sep 2026), whereas CEO Ananya verbally asserted ARR is *"around forty-two crore, maybe forty-five now"* (T1), and CFO Meera cited *"forty-eight"* (T2). These statements remain unresolved conflicting claims without primary evidence asserting GMV, valuation, or pipeline. The board update is not described as audited.
2. **CONF-002 (Monthly Burn Discrepancy):** Board deck reports **Rs. 44 Lakhs monthly burn** (Q2, with 13 months runway), not labeled gross or net as the source does not define it. Zoho Books records monthly payroll disbursements of Rs. 31.75 Lakhs + rent Rs. 2.36 L + cloud ~Rs. 2.5 L. In contrast, CFO Meera claimed burn is *"two point two lakhs a month, sometimes two point five"* (T2). This statement is kept as an unresolved transcript claim; net burn is not inferred from ARR.
3. **CONF-003 (Headcount Scope):** Keka HRMS and board decks record **19 employees** (18 Active, 1 Notice period; contractors excluded), while candidate brief describes 180 people and CEO Ananya remarked *"roughly eighteen people ('one-eighty, give or take')"*. Unresolved scope difference maintained without inventing unlisted contractors or assuming CEO meant 18 active employees.
4. **CONF-004 (Suspected February Payroll Discrepancy):** Reclassified as a suspected February payroll discrepancy requiring verification. Rahul Verma joined on 2026-02-03 (26/28 payable days) with full month pay processed while Fatima was on leave. Rahul queried this and Fatima acknowledged, with March payroll paying a full month. Evidence establishes a potential partial-month payment issue and query, not a confirmed defect, requiring formal Keka reconciliation records. Individual compensation numbers remain strictly confidential.
5. **CONF-005 (Pulse Survey Comment Disclosure vs Small-Team Anonymity):** In transcript T3, Deepa Joshi verbally suggested sharing pulse survey comments with CEO Ananya (*"numbers alone hide everything"*). However, on 29 Sep 2026 (`11.eml`), Deepa explicitly refused to share comments because the engineering team (5 members, 4 responses) is too small to protect anonymity. Written directive supersedes verbal call; comments remain strictly withheld.
6. **CONF-006 (T3 Verbal Recruitment Assertions vs Hiring Tracker):** In T3, Deepa cited attrition as *"about twelve"* (unit undefined: % vs headcount vs benchmark), and Rohan claimed 22 open roles in April and losing 6 in August with offer acceptance *"down to fifty-something"*. In contrast, formal `Hiring_Tracker.xlsx` lists exactly 6 total requisitions (REQ-011 to REQ-017) and `06.eml` pauses only 2 backend roles until the round closes. Verbal claims are preserved as unresolved source ambiguities without inventing unrecorded figures.

*All conflict resolutions remain marked `UNRESOLVED` in [DECISIONS.md](DECISIONS.md) pending human confirmation.*

---

## 3. Core Governance & Audit Documents

| Document | Purpose & Description |
|---|---|
| [VOICE_NOTE_RESPONSES/T6a.md](VOICE_NOTE_RESPONSES/T6a.md) | **Defensible written response to CEO voice note T6a** ("tell me what to worry about. Top three"), detailing accepted scope, risk ranking, refusal boundaries, and test coverage. |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Relational schema, system architecture, privacy design, temporal dual-axis filtering, and deployment contracts. |
| [DECISIONS.md](DECISIONS.md) | Structured register of 6 source conflicts (`CONF-001`–`CONF-006`) and T6a decision record, confidence levels, and review status (`UNRESOLVED`). |
| [ASSUMPTIONS.md](ASSUMPTIONS.md) | Grounded operational assumptions (`ASM-001`–`ASM-007`), data room boundaries, and 14 AI employee persona boundaries. |
| [TRANSCRIPT_NOTES.md](TRANSCRIPT_NOTES.md) | Acoustic analysis of MeetNotes AI transcriptions across T1, T2, T3, and T6a voice note. |
| [AI_LOG.md](AI_LOG.md) | Transparent audit log of all AI assistance, prompts, tool executions, and verified test results. |

---

## 4. Technology Stack

- **Backend:** FastAPI (Python 3.10+), SQLAlchemy 2.0 ORM, SQLite relational persistence, Pydantic v2 schemas.
- **Frontend:** Next.js 14.2 (App Router), TypeScript, Tailwind CSS, Lucide React icons, interactive As-Of temporal selector, T6a Top 3 Morning Briefing cards, HR & People Insights panel.
- **Source Adapters:** Extensible adapter architecture (`backend/app/services/adapters/`) with unified parsing contracts.
- **Testing:** Pytest 9.2 (**75 automated tests passing**, including Day 2 temporal release gates, Culture Amp drops, hiring tracker states, comments withholding, dynamic risk degradation, and salary privacy).
- **Execution Mode:** Deterministic No-Key engine is default. Zero external API keys required to run full test suite and cockpit interface.

---

## 5. Verified Single Fresh-Clone Setup & Run Command

### Quick Start (Automated Script)
- **Windows (PowerShell):**
  ```powershell
  .\run_all.ps1
  ```
- **Linux / macOS / WSL (Bash):**
  ```bash
  ./run_all.sh
  ```
The script automatically copies `.env.example` to `.env` if needed, installs backend dependencies in a virtual environment, executes all 57 pytest tests, installs frontend npm dependencies, and boots both FastAPI (port 8000) and Next.js (port 3000).

### Manual Step-by-Step Instructions

#### 1. Backend Setup & Test Verification
```bash
# From repository root:
python -m venv .venv
.\.venv\Scripts\pip install -r backend/requirements.txt

# Run all 57 automated tests:
.\.venv\Scripts\python -m pytest backend/tests -v

# Start FastAPI server on port 8000:
.\.venv\Scripts\python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup
```bash
# In a second terminal:
cd frontend
npm install
npm run dev
```

Visit the executive dashboard at **[http://localhost:3000](http://localhost:3000)**. The backend API is available at **[http://localhost:8000](http://localhost:8000)** (Interactive OpenAPI docs at **[http://localhost:8000/docs](http://localhost:8000/docs)**).

---

## 6. Test Suite Verification Summary

```text
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\Rivu Chattopadhyay\Desktop\Hiya\veloxa-cockpit-rivu-chattopadhyay
collected 75 items

backend\tests\test_audit_api.py ......................                   [ 29%]
backend\tests\test_cockpit.py ...........................                [ 65%]
backend\tests\test_data_driven.py ........                               [ 76%]
backend\tests\test_day2.py ..................                            [100%]

======================= 75 passed, 2 warnings in 1.99s ========================
```

Key Day 2 Automated Test Validations:
- `test_release_temporal_095959_denial`: Refusal for Day 2 queries prior to release timestamp (`2026-11-17T09:59:59+05:30`).
- `test_release_temporal_100000_access`: Immediate access to Day 2 pulse data at `2026-11-17T10:00:00+05:30`.
- `test_exact_hiring_status_and_pipelines`: Requisition states, on-hold reasons, and pipelines verified (`REQ-011` through `REQ-017`).
- `test_two_engineering_reqs_paused_round_not_closed`: Meera 06.eml pause until round closes confirmed.
- `test_engineering_survey_engagement_drop`: -0.8 drop (3.9 to 3.1) with 4 of 5 participation verified.
- `test_marketing_survey_engagement_drop`: -0.4 drop (3.8 to 3.4) across 3 respondents verified.
- `test_survey_comments_withholding_privacy_refusal`: 11.eml Deepa directive enforcing comment withholding for teams <6 verified.
- `test_arjun_das_remote_request_not_approved`: Acknowledged as request without policy approval verified.
- `test_siddharth_resignation_promise_not_completed_handover`: Launch kit handover classified as exit promise verified.
- `test_priya_nair_leave_no_burnout_inference`: Approved personal half-days recorded without burnout speculation verified.
- `test_t3_transcript_ambiguities_unresolved`: Unresolved verbal figures maintained under `CONF-006`.
- `test_t6a_written_response_document_exists`: Defensible document present at `VOICE_NOTE_RESPONSES/T6a.md`.
- `test_default_top_three_risks_and_full_list`: Default top 3 risk cards and full list verified.
- `test_dynamic_risk_degradation_when_evidence_removed`: Removing `E045` dynamically deactivates `RISK-006`.
- `test_hr_insights_endpoint`: Dedicated `/api/hr-insights` endpoint returning engagement and requisitions verified.
- `test_idempotent_ingestion_across_reruns`: Counts remain constant across repeat seed executions (`sources=22`, `evidence=47`, `claims=34`, `conflicts=6`).
- `test_salary_privacy_enforced_in_day2`: Confidential severance/compensation refusal verified.
- `test_exactly_14_interviewable_agents_day2`: 14 interviewable personas maintained without leakage.
```
