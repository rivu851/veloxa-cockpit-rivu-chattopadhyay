# Veloxa CXO Cockpit — Source Conflict Decisions Register
**Assessment Phase:** Individual Hackathon (Day 2 Release — Tue 17 Nov 2026 10:00 IST)  
**Author / Candidate:** Rivu Chattopadhyay  
**Status Policy:** All consequential source conflicts are cataloged with competing evidence, human decisions, and sensitivity analysis. Discrepancies are maintained as unresolved conflicting claims without ungrounded speculation.

---

## Conflict CONF-001: Annual Recurring Revenue (ARR) Discrepancy

### 1. Competing Sources
- **Board Update A:** `Board_Update_Apr-Jun_2026.pdf` (Page 1, Key Numbers)  
  *Reported Metric:* `ARR (recurring): Rs. 5.8 Cr` (61 customers). Sent 8 Jul 2026. Confidential.
- **Board Update B:** `Board_Update_Jul-Sep_2026.pdf` (Page 1, Key Numbers)  
  *Reported Metric:* `ARR (recurring): Rs. 6.1 Cr` (66 customers). Sent 6 Oct 2026. Confidential.
- **Verbal Statement C:** `T1_CEO_Kickoff_Call.docx` (Summary)  
  *CEO Ananya Rao assertion:* Says ARR is *"around forty-two crore, maybe forty-five now"*.
- **Verbal Statement D:** `T2_CFO_Call.docx` (Summary)  
  *CFO Meera Iyer assertion:* ARR at the start of the year was *"forty-eight"*.

### 2. Human Conflict Decision
- **Authoritative Operational Metric:** Use **Rs. 6.1 Crore** as the latest board-reported recurring ARR (as of Period Jul to Sep 2026, reported 6 Oct 2026).
- **Treatment of Verbal Claims:** Keep the CEO's Rs. 42–45 Cr and CFO's Rs. 48 Cr statements as **unresolved conflicting claims**.
- **Negative Constraints:**
  - Do **not** assert or speculate that verbal claims represent GMV, company valuation, or sales pipeline without primary source evidence.
  - Do **not** describe the board report as "audited", as the document itself is labeled a confidential board update rather than a statutory audit.
- **Impact on Cockpit Logic:** Executive queries return Rs. 6.1 Cr as the board-reported recurring ARR, cite E006 and E001, and trigger a `CONF-001` conflict notice citing the unresolved CEO and CFO statements.
- **Confidence:** **MEDIUM**
- **What Would Change Conclusion:** Formal audited statutory accounts, general ledger revenue recognition schedules, or signed board minutes clarifying the basis of executive figures.
- **Human Decision Status:** **`UNRESOLVED`** (Formal conflict remains documented and open).

---

## Conflict CONF-002: Monthly Burn Rate Discrepancy

### 1. Competing Sources
- **Board Update A:** `Board_Update_Apr-Jun_2026.pdf` (Page 1, Key Numbers)  
  *Reported Metric:* `Monthly burn: Rs. 46 L` (Runway: 14 months). Sent 8 Jul 2026.
- **Board Update B:** `Board_Update_Jul-Sep_2026.pdf` (Page 1, Key Numbers)  
  *Reported Metric:* `Monthly burn: Rs. 44 L` (Runway: 13 months). Sent 6 Oct 2026.
- **Financial General Ledger:** `GL_Export_Apr-Sep_2026.xlsx` (Zoho Books, Apr to Sep 2026)  
  *Disbursements:* Salaries (payroll) payment is entered at `Rs. 31,75,000` on the 28th of each month from Apr to Sep 2026. Office rent to WeWork India is `Rs. 2,36,000` monthly. AWS expenses range from `Rs. 1,81,200` to `Rs. 2,48,310`.
- **Verbal Statement C:** `T2_CFO_Call.docx` (Summary)  
  *CFO Meera Iyer assertion:* Burn has been *"two point two lakhs a month, sometimes two point five"*.
- **Verbal Statement D:** `T1_CEO_Kickoff_Call.docx` (Key points)  
  *CEO Ananya Rao assertion:* Burn is *"around two point two"* (unit not stated).

### 2. Human Conflict Decision
- **Authoritative Operational Metric:** Use **Rs. 44 Lakh** as the latest board-reported monthly burn (Period Jul to Sep 2026).
- **Labeling Constraint:** Do **not** label this figure as "gross" or "net" burn, because the primary board update source document does not explicitly define the term.
- **Inference Prohibition:** Do **not** infer net cash burn from ARR or assume ARR is cash received. General ledger inflows are not provided in Day 1 data.
- **Treatment of Transcript Statement:** Keep CFO Meera's statement of *"two point two lakhs a month, sometimes two point five"* as an **unresolved transcript claim**.
- **Impact on Cockpit Logic:** Queries return Rs. 44 Lakh monthly burn and 13 months runway from the Q2 board update, cite E007 and E003, list ledger payroll/rent/cloud actuals, and flag `CONF-002`.
- **Confidence:** **MEDIUM**
- **What Would Change Conclusion:** Complete monthly cash-flow statement from Zoho Books, cash receipts journals, or written CFO reconciliation.
- **Human Decision Status:** **`UNRESOLVED`** (Formal conflict remains documented and open).

---

## Conflict CONF-003: Headcount & Company Scope Discrepancy

### 1. Competing Sources
- **HR System Record:** `Employee_Master.xlsx` (Sheet Employees, Rows 1-22)  
  *Reported Count:* 19 employees. Row 1 notes: *"Keka HRMS export, employees only (contractors are not in Keka). Exported 31-Oct-2026."* 18 Active, 1 Notice period (Siddharth Mehta, exit date 2026-10-31).
- **Board Updates:** `Board_Update_Apr-Jun_2026.pdf` & `Board_Update_Jul-Sep_2026.pdf`  
  *Reported Metric:* `Team: 19` in both Q1 and Q2.
- **Verbal Statement:** `T1_CEO_Kickoff_Call.docx` (Summary)  
  *CEO Ananya Rao assertion:* Company is *"roughly eighteen people ('one-eighty, give or take')"*.
- **Candidate Brief:** Hackathon problem description  
  *Description:* Characterizes the company as a 180-person organization.

### 2. Human Conflict Decision
- **Authoritative Operational Metric:** Use **19** as the board-reported and Keka-recorded employee count.
- **Scope Treatment:** Keep the candidate brief's 180-person company description and the ambiguous CEO transcript statement (*"one-eighty, give or take"*) as **unresolved scope differences**.
- **Negative Constraints:**
  - Do **not** invent or extrapolate unlisted contractors to bridge the gap without primary records.
  - Do **not** assume the CEO meant 18 active employees.
- **Impact on Cockpit Logic:** Cockpit reports 19 employees from Keka and board reports, cites E020 and E006, notes the 18 active + 1 notice breakdown, and flags the unresolved 180-person scope difference (`CONF-003`).
- **Confidence:** **MEDIUM**
- **What Would Change Conclusion:** Official contractor registry, Culture Amp pulse participant roster, or organizational audit report.
- **Human Decision Status:** **`UNRESOLVED`** (Formal conflict remains documented and open).

---

## Conflict CONF-004: Suspected February Payroll Discrepancy Requiring Verification

### 1. Competing Sources
- `Employee_Master.xlsx` (Row 21): Rahul Verma Join Date `2026-02-03` (26 of 28 payable days in February).
- `01.eml` (28 Feb 2026): Karthik states he ran February payroll using the January template and added the new joiner while Fatima was on leave for her wedding.
- `Payroll_Register_Jan-Mar_2026.xlsx` (Rows 39 & 58): Rahul Verma's entry lists 28 payable days in February with full gross pay processed by KS. March payroll records list 31 payable days with zero clawback or adjustment noted.
- `02.eml` (6 Mar 2026): Rahul emailed Fatima asking if his February pay should have been calculated for 26 days instead of 28.
- `03.eml` (10 Mar 2026): Fatima acknowledged the query ("Will check and get back").

### 2. Human Conflict Decision (Reclassification & Audit)
- **Classification:** Reclassified as a **suspected February payroll discrepancy requiring verification**.
- **Assessment of Uncertainty:** The available records establish a potential partial-month payment issue and an employee query, not a conclusively confirmed payroll defect. The documentation shows an inquiry acknowledged by payroll, but formal adjustments or reconciliations may exist outside the workbook.
- **Privacy Constraint:** Individual compensation amounts are strictly confidential and redacted at the service layer (`[REDACTED_CONFIDENTIAL]`). Executive queries report the governance and control aspect without exposing individual salary figures.
- **Impact on Cockpit Logic:** Executive queries regarding payroll discrepancy report the suspected pro-ration issue under verification, cite E017, E018, E019, E023, E024, and redact monetary amounts.
- **Confidence:** **MEDIUM**
- **What Would Change Conclusion:** Formal Keka payroll reconciliation vouchers, year-end Form 16 / tax audit filings, or signed payroll audit report.
- **Human Decision Status:** **`UNRESOLVED`** (Formal conflict remains documented and open).

---

## Conflict CONF-005: Pulse Survey Comments Disclosure vs Small-Team Anonymity

### 1. Competing Sources
- **Verbal Statement:** `T3_Head_of_People_Call.docx` (MeetNotes AI summary, recording 31 min)  
  *Deepa Joshi assertion:* Wants Ananya to see survey comments directly, asserting *"numbers alone hide everything"*.
- **Written Directive:** `11.eml` (Date: Tue, 29 Sep 2026 17:30:00 +0530)  
  *Deepa Joshi to Ananya Rao:* *"Ananya, engineering pulse dropped this quarter. The team is too small for me to share comments. I'd suggest Vikram does 1:1s this week."*
- **Survey Dataset:** `Pulse_Survey.xlsx` (Culture Amp quarterly export)  
  *Team Sizes:* Engineering has 5 members (4 responded), Marketing has 3 members (3 responded), Finance 3, People & Ops 3, Sales 2, Support 2.

### 2. Human Conflict Decision
- **Authoritative Operational Policy:** Enforce privacy-by-design policy strictly **withholding qualitative comments** for any team with fewer than 6 members to protect employee confidentiality and prevent re-identification.
- **Precedence Hierarchy:** Deepa Joshi's written directive in `11.eml` directly supersedes the earlier verbal suggestion in `T3_Head_of_People_Call.docx`.
- **Negative Constraints:**
  - Do **not** disclose engineering or marketing qualitative comments to executive queries.
  - Do **not** claim comments were lost or unrecorded; they exist in Cult Amp but are restricted at the service layer.
- **Impact on Cockpit Logic:** Queries requesting survey comments return `REFUSAL` with policy restriction explanation and cite `E036` (11.eml) and `E045`.
- **Confidence:** **HIGH**
- **What Would Change Conclusion:** Written consent waiver from all 5 engineering team members or HR board governance amendment reducing the re-identification threshold.
- **Human Decision Status:** **`UNRESOLVED`** (Maintained as an active governance policy pending candidate / board confirmation).

---

## Conflict CONF-006: T3 Verbal Recruitment & Attrition Assertions vs Formal Hiring Tracker

### 1. Competing Sources
- **Verbal Assertions:** `T3_Head_of_People_Call.docx`  
  - Deepa asserts attrition is *"about twelve, which is normal for Bangalore"* (unspecified whether 12%, 12 headcount, or industry benchmark).
  - Rohan claims there were *"twenty-two open roles in April"* and *"we lost six of them in August"*, with offer acceptance *"down to fifty-something"*.
  - Disputed manager training timing: Deepa states *"November-ish"*, Rohan asserts *"January"*.
- **Formal System Record:** `Hiring_Tracker.xlsx` (Keka Hire export, 31-Oct-2026)  
  *Total Requisitions:* Exactly 6 rows (`REQ-011` through `REQ-017`, excluding `REQ-012`), with status: REQ-011 (Closed-not hired), REQ-013 (Filled), REQ-014 (On hold, pipeline 3), REQ-015 (On hold, pipeline 5), REQ-016 (Open, pipeline 7), REQ-017 (Open, pipeline 2).
- **Formal Executive Correspondence:** `06.eml` & `07.eml`  
  *Meera Iyer & Vikram Menon:* Only 2 requisitions (`REQ-014` and `REQ-015`) were paused on 12 Aug 2026 until the funding round closes.

### 2. Human Conflict Decision
- **Authoritative Operational Source:** Ground all operational counts in `Hiring_Tracker.xlsx` (6 requisitions) and `06.eml`/`07.eml`.
- **Treatment of Transcript Statements:** Catalog Deepa's "about twelve" and Rohan's "twenty-two open / lost six / fifty-something" as **unresolved verbal ambiguities**.
- **Negative Constraints:**
  - Do **not** invent units for "about twelve" (do not assume 12% or 12 resignations).
  - Do **not** assert 22 open roles existed or 6 resignations occurred without primary ATS records.
  - Do **not** guess which engineer Deepa was worried about or link her comment to Priya Nair.
- **Impact on Cockpit Logic:** Queries regarding attrition return the literal quote *"about twelve"* with unit undefined, flag `CONF-006`, and cite E028.
- **Confidence:** **LOW (for verbal claims)** / **HIGH (for Keka Hire tracker)**
- **What Would Change Conclusion:** Official historical ATS requisitions dump from Lever/Keka Hire for April–August 2026 or signed HRBP exit ledger.
- **Human Decision Status:** **`UNRESOLVED`** (Formal conflict remains documented and open).

---

## T6a Executive Voice Note Decision Record

### 1. Source Context
- **Source:** `T6a_CEO_Voice_Note.docx` (Auto-transcribed WhatsApp voice note forwarded by Ananya's assistant)  
- **Transcription Text:** *"Hi, quick one. I won't type questions every morning, na. When I open it, it should just tell me what to worry about. Top three. Okay, bye."*
- **Candidate Governance Status:** **PROPOSED ACCEPT WITH SCOPE (Awaiting Candidate Confirmation)**.

### 2. Decision & Scope Analysis
- **Decision:** **ACCEPT WITH SCOPE**  
- **What Was Accepted:**
  - Default landing screen prominently displays the top-3 ranked enterprise risks (`RISK-001` Atlas v3 launch slippage, `RISK-006` Engineering capacity deficit & engagement collapse, `RISK-002` Executive ARR/burn discrepancy).
  - Each risk card includes severity badge, category, summary, recommended mitigation, and expandable evidence citations.
  - Zero-click executive briefing satisfies Ananya's request without manual morning typing.
- **What Was Refused / Bound by Policy:**
  - The cockpit refuses to hide the remaining enterprise risks: a toggle button (`View All 7 Risks`) guarantees full transparency.
  - The cockpit refuses to invent unverified risks or expose confidential qualitative HR comments.
  - The decision is logged as **PROPOSED** pending candidate confirmation, preserving the human decision boundary.
