# Veloxa CXO Cockpit — Executive Intelligence & Governance System

**Candidate:** Rivu Chattopadhyay  
**Hackathon Assessment:** Hiyaku Systems individual Veloxa CXO Cockpit hackathon  
**Timeline:** Monday 16 Nov 2026 10:00 IST through Friday 20 Nov 2026 18:00 IST  
**Public Repository:** [https://github.com/rivu851/veloxa-cockpit-rivu-chattopadhyay](https://github.com/rivu851/veloxa-cockpit-rivu-chattopadhyay)  
**Day 1 Release Milestone:** Mon 16 Nov 2026 by 23:59 IST (Architecture & Baseline Scaffold)

---

## 1. Executive Summary

The **Veloxa CXO Cockpit** is a full-stack executive intelligence platform built for the CEO and leadership of Veloxa Technologies. It unifies disparate, contradictory, and unstructured operational data rooms—including Keka HRMS, Zoho Books general ledgers, board governance decks, pre-Keka payroll registers, and executive call transcripts—into an authoritative, evidence-backed decision system.

### Key Capabilities
- **Deterministic Factual Grounding:** Every factual answer is linked to granular citations (`E001`, `E002`, ...) preserving exact source file, sheet, page, and row coordinates.
- **Strict Salary Confidentiality at Service Layer:** Enforces CFO Meera Iyer's directive (`T2_CFO_Call`) preventing individual employee compensation figures from ever reaching executive query outputs.
- **Honest Refusal & Uncertainty Engine:** Explicitly distinguishes confirmed facts from disputed claims and inferred interpretations. Refuses to hallucinate when source evidence is absent or temporal boundaries are crossed.
- **Temporal Time-Travel (`as_of`):** Historical queries filter evidence by effective business dates and data room release timestamps, preventing future release leakage.
- **14 Grounded AI Employee Agents:** Conversational AI personas grounded in official Keka HRMS records operating within verified knowledge boundaries.
- **Human-in-the-Loop Conflict Governance:** Contradictions between verbal executive statements and audited board decks are cataloged with proposed interpretations and marked `UNRESOLVED` pending human confirmation.

---

## 2. Key Day 1 Conflicts Identified

Four consequential source discrepancies were uncovered in the Day 1 data room and cataloged in [DECISIONS.md](DECISIONS.md):

1. **CONF-001 (ARR Discrepancy):** Audited Board Update reports **Rs. 6.1 Crore recurring ARR** (Q2 Jul-Sep 2026), whereas CEO Ananya verbally asserted ARR is *"around forty-two crore, maybe forty-five now"* (T1), and CFO Meera cited *"forty-eight"* (T2).
2. **CONF-002 (Monthly Burn Discrepancy):** Board decks report **Rs. 44 Lakhs monthly burn** (Q2), and Zoho Books confirms gross monthly payroll alone is Rs. 31.75 Lakhs + rent Rs. 2.36 L + cloud ~Rs. 2.5 L. In contrast, CFO Meera verbally claimed burn is *"two point two lakhs a month, sometimes two point five"* (T2).
3. **CONF-003 (Headcount Scope):** Keka HRMS confirms **19 employees** (18 Active, 1 Notice period; contractors excluded), while CEO Ananya casually mentioned *"roughly eighteen people ('one-eighty, give or take')"*.
4. **CONF-004 (Rahul Verma Payroll Calculation Error):** Rahul Verma joined on 2026-02-03 (26/28 payable days) but was credited for a full 28 days by Karthik Subramanian while Fatima was on wedding leave. Acknowledged by Fatima on 10 March, but March payroll was disbursed with zero adjustment.

*All conflict resolutions remain marked `UNRESOLVED` in [DECISIONS.md](DECISIONS.md) pending human confirmation.*

---

## 3. Core Governance & Audit Documents

| Document | Purpose & Description |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Relational schema, system architecture, privacy design, temporal filtering, and deployment contracts. |
| [DECISIONS.md](DECISIONS.md) | Structured register of source conflicts, proposed interpretations, confidence levels, and human review status (`UNRESOLVED`). |
| [ASSUMPTIONS.md](ASSUMPTIONS.md) | Grounded operational assumptions, data room boundaries, and 14 AI employee persona boundaries. |
| [TRANSCRIPT_NOTES.md](TRANSCRIPT_NOTES.md) | Acoustic analysis of MeetNotes AI transcriptions (Jira, Zoho Books, Keka, Culture Amp, burn mishearings). |
| [AI_LOG.md](AI_LOG.md) | Transparent audit log of all AI assistance, prompts, tool executions, and verified test results. |

---

## 4. Technology Stack

- **Backend:** FastAPI (Python 3.14+), SQLAlchemy 2.0 ORM, SQLite relational persistence, Pydantic v2 schemas.
- **Frontend:** Next.js 14.2 (App Router), TypeScript, Tailwind CSS, Lucide React icons.
- **Testing:** Pytest 9.2 (25 automated tests, including 6 refusal/uncertainty tests and 5 privacy tests).
- **Execution Mode:** Deterministic No-Key engine is default. Zero external API keys required to run full test suite and cockpit interface.

---

## 5. Verified Single Fresh-Clone Setup & Run Command

### Quick Start (Automated PowerShell Script)
From the repository root:
```powershell
.\run_all.ps1
```

### Manual Step-by-Step Instructions

#### 1. Backend Setup & Test Verification
```bash
# From repository root:
python -m venv .venv
.\.venv\Scripts\pip install -r backend/requirements.txt

# Run all 25 automated tests:
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
collected 25 items

backend/tests/test_cockpit.py::test_health_check PASSED                  [  4%]
backend/tests/test_cockpit.py::test_source_conflicts_endpoint PASSED     [  8%]
backend/tests/test_cockpit.py::test_agent_listing PASSED                 [ 12%]
backend/tests/test_cockpit.py::test_privacy_refusal_individual_salary_vikram PASSED [ 16%]
backend/tests/test_cockpit.py::test_privacy_refusal_individual_salary_rahul PASSED [ 20%]
backend/tests/test_cockpit.py::test_privacy_redaction_evidence_endpoint PASSED [ 24%]
backend/tests/test_cockpit.py::test_privacy_agent_chat_coworker_salary PASSED [ 28%]
backend/tests/test_cockpit.py::test_privacy_refusal_fatima_salary PASSED [ 32%]
backend/tests/test_cockpit.py::test_uncertainty_future_release_leakage PASSED [ 36%]
backend/tests/test_cockpit.py::test_uncertainty_future_date_query PASSED [ 40%]
backend/tests/test_cockpit.py::test_uncertainty_hallucinated_customer_names PASSED [ 44%]
backend/tests/test_cockpit.py::test_uncertainty_missing_financial_metric PASSED [ 48%]
backend/tests/test_cockpit.py::test_uncertainty_unsupported_speculation PASSED [ 52%]
backend/tests/test_cockpit.py::test_uncertainty_office_expansion_plans PASSED [ 56%]
backend/tests/test_cockpit.py::test_arr_query_with_conflict_detection PASSED [ 60%]
backend/tests/test_cockpit.py::test_burn_query_with_conflict_detection PASSED [ 64%]
backend/tests/test_cockpit.py::test_headcount_query PASSED               [ 68%]
backend/tests/test_cockpit.py::test_atlas_v3_status_and_slippage PASSED  [ 72%]
backend/tests/test_cockpit.py::test_logistics_summit_spend PASSED        [ 76%]
backend/tests/test_cockpit.py::test_ranked_risks PASSED                  [ 80%]
backend/tests/test_cockpit.py::test_agent_chat_priya PASSED              [ 84%]
backend/tests/test_cockpit.py::test_agent_chat_rahul PASSED              [ 88%]
backend/tests/test_cockpit.py::test_evidence_e001_retrieval PASSED       [ 92%]
backend/tests/test_cockpit.py::test_evidence_not_found PASSED            [ 96%]
backend/tests/test_cockpit.py::test_payroll_defect_query PASSED          [100%]

======================= 25 passed, 2 warnings in 1.52s ========================
```
