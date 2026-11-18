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
- **Human Decision Status:** **`POLICY APPROVED (Disclosure Restriction Enforced) / FACTUAL DISCREPANCY UNRESOLVED`**  
  *Candidate Ratification:* Candidate approved treating the written HR restriction in `11.eml` as governing disclosure (withholding qualitative pulse comments for teams with fewer than 6 members). The verbal disagreement in transcript T3 is preserved as an unresolved historical difference, but the written HR restriction governs cockpit disclosure across all endpoints.

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
- **Human Decision Status:** **`OPERATIONAL POLICY APPROVED (Hiring Tracker Authoritative for Listed Requisitions) / HISTORICAL CLAIMS UNRESOLVED`**  
  *Candidate Ratification:* Candidate approved treating `Hiring_Tracker.xlsx` as authoritative for its listed requisitions (REQ-011 through REQ-017), not as proof of all historical hiring. Ambiguous T3 attrition ("about twelve"), offer acceptance ("down to fifty-something"), and historical hiring claims ("twenty-two open", "lost six") are explicitly preserved as unresolved numeric discrepancies without inventing unrecorded figures.

---

## Conflict CONF-007: On-Call Rota Alias & SRE Contractor Identity: Sneha vs Snehal vs S. Patil

### 1. Competing Sources
- **On-Call Rota:** `OnCall_Rota.xlsx` (Sheet On-call, Rows 4-20)  
  *Entries:* Weeks 1–6 (2026-07-06 through 2026-08-10): Primary is strictly `Sneha` with Secondary alternating `Arjun` and `Priya`. Starting week of `2026-08-17`, `Snehal` appears as Primary (Secondary: `Sneha`); thereafter `Sneha` and `Snehal` alternate Primary and Secondary weekly through `2026-10-26`.
- **PagerDuty Incident Export:** `Incidents_Aug-Oct_2026.xlsx` (Sheet Incidents)  
  *Entries:* Early August incidents handled by `Sneha` (`INC-201`, `INC-203`, `INC-204`, `INC-205`); `Snehal` responded to `INC-206` (27 Aug), `INC-207` (5 Sep), `INC-209` (28 Sep), and `INC-211` (21 Oct).
- **Vendor Retainer Invoice:** `Invoice_PIS-114.pdf` (01/10/2026, Patil Infra Services, Baner Road, Pune)  
  *Billing:* "On-call SRE support, S. Patil, September 2026 (monthly retainer) Rs. 1,20,000 + IGST @ 18% Rs. 21,600 = Total Rs. 1,41,600." Note confirms: *"Previous invoice PIS-108 (18 to 31 Aug, pro rata) settled."*
- **SRE Email Escalation:** `08.eml` (Mon, 24 Aug 2026 09:05 IST)  
  *Sneha Kulkarni to Vikram Menon:* *"Third SEV1 this month. I'm pausing the Atlas perf tickets to stabilise routing-api. The contractor starts on the rota this week."*
- **Verbal Transcript Statement:** `T5_VP_Engineering_Call.docx` (P4, P6)  
  *Vikram Menon assertion:* *"Snehal on SRE and on-call... Mentions Sneha once later; unclear if same person."*

### 2. Human Conflict Decision (Competing Hypotheses & Roster Integrity)
- **Classification:** **COMPETING HYPOTHESES MAINTAINED AS UNRESOLVED (`CONF-007`)**.
- **Assessment of Competing Hypotheses:**
  - **Hypothesis A (Most Grounded):** *Snehal is contractor S. Patil* from Patil Infra Services, engaged on pro-rata retainer starting 18 August (`PIS-108`), joining the on-call rota the week of 17/24 August (`08.eml`), and continuing on monthly retainer (`PIS-114`) to provide critical SRE relief following three August SEV1s.
  - **Hypothesis B:** *Snehal is an informal tool alias or phonetic variant* for full-time Site Reliability Engineer Sneha Kulkarni (`VX012`).
  - **Hypothesis C:** *Snehal is a separate unrecorded full-time engineer* omitted from Keka HRMS.
- **Negative Constraints:**
  - Do **not** merge Sneha Kulkarni and Snehal into one identity, or assert Snehal = S. Patil as verified fact without primary IAM/SOW documentation.
  - Do **not** expand the 14-person grounded agent cohort with an unverified 15th agent persona.
- **Impact on Cockpit Logic:** Cockpit presents the competing evidence and timeline, flags `CONF-007`, and maintains Sneha Kulkarni (`VX012`) as the sole grounded SRE agent persona.
- **Confidence:** **MEDIUM**
- **What Would Change Conclusion:** Executed contractor Statement of Work (SOW) naming S. Patil, Okta/AWS IAM identity logs, or signed HR contractor master.
- **Human Decision Status:** **`UNRESOLVED`** (Maintained as open competing hypotheses pending formal verification).

---

## Conflict CONF-008: Atlas GA Target Date: Jira Version Record vs Transcript T5 Perception

### 1. Competing Sources
- **Jira Project Version Record:** `Jira_Export_ATLAS.xlsx` (Sheet Versions, Row 2)  
  *Authoritative Changelog:* Version `Atlas GA`, Release Date `2026-12-15`, Original Release Date `2026-09-15`, Last Changed `2026-09-02`, Changed By `vikram`.
- **Engineering Requisition Plan:** `04.eml` (Tue, 02 Jun 2026 09:30 IST)  
  *Vikram Menon to Ananya Rao:* *"Atlas plan: Priya leads the core engine and re-routing, Rahul on the API, Arjun on the UI, Sneha on hardening. 15 Sep GA is achievable if the two backend hires land by July."*
- **Verbal Transcript Statement:** `T5_VP_Engineering_Call.docx` (MeetNotes AI summary, 31 Oct 2026)  
  *Vikram Menon assertion:* Claims Atlas v3 is *"on track, maybe a couple of weeks of buffer needed"* and the board date is *"still September-ish"*.

### 2. Human Conflict Decision (Engineering System Baseline vs Verbal Optimism)
- **Authoritative Operational Schedule:** Prefer the **Jira project ATLAS version export (`2026-12-15`)** as the recorded authoritative engineering schedule state.
- **Treatment of Verbal Claims:** Vikram's statement of *"still September-ish"* is cataloged as an **unaligned executive perception** or optimistic conversational framing, not a scheduled or achieved production release.
- **Causality Plurality Assessment:** The shift from 15-Sep to 15-Dec was driven by compound factors: (1) Paused backend hiring (`REQ-014`/`REQ-015` frozen on 12 Aug, `06.eml`); (2) Three SEV1 incidents in August (`E053`); (3) Pausing of performance hardening tickets (`ATLAS-5` at only 14% completion, `08.eml`, `E061`).
- **Impact on Cockpit Logic:** Executive queries return 2026-12-15 as the recorded GA target, cite `E051`, and trigger conflict alert `CONF-008` citing Vikram's T5 statement.
- **Confidence:** **HIGH**
- **What Would Change Conclusion:** Subsequent sprint release commit or an approved Q3 board deck with a different ratified release date.
- **Human Decision Status:** **`PROPOSED FOR RATIFICATION / VERBAL DISCREPANCY UNRESOLVED`** (Jira system record authoritative for engineering schedule).

---

## Conflict CONF-009: Marketing Spend "One Point Eight" & Summit Overrun vs Verified Financial Records

### 1. Competing Sources
- **Verbal Transcript Statement:** `T4_Head_of_Marketing_Call.docx` (MeetNotes AI summary, 31 Oct 2026)  
  *Nikhil Bose assertion:* Asserts total marketing spend for the half was *"one point eight by his numbers"*, notes that finance *"counts things differently"*, and admits the September logistics summit budget *"went a little over, nothing crazy"*. Claims the summit was *"our best quarter ever for pipeline"* while dismissing Sales Lead Manoj's feedback that summit leads were cold.
- **Financial General Ledger:** `GL_Export_Apr-Sep_2026.xlsx` (Zoho Books, Apr to Sep 2026)  
  *Disbursements:* Contains specific line items for advertising (Google Ads, LinkedIn) and summit venue/production expenses, but provides no consolidated Rs. 1.8 Cr or Rs. 1.8 L total.
- **Board Updates:** `Board_Update_Apr-Jun_2026.pdf` & `Board_Update_Jul-Sep_2026.pdf`  
  *Financial Reporting:* Highlights overall monthly burn (Rs. 44–46 L) and recurring ARR without separating a discrete marketing H1 total.

### 2. Human Conflict Decision (Unverified Marketing Metrics)
- **Classification:** **UNVERIFIED MARKETING PERCEPTION (`CONF-009`)**.
- **Assessment of Uncertainty:** The "one point eight" claim lacks explicit currency units (Lakhs vs Crores) and verified reconciliation against Zoho Books GL cost centres. Pipeline claims lack CRM conversion backing.
- **Negative Constraints:**
  - Do **not** invent currency units (do not assume Rs. 1.8 Crore or Rs. 1.8 Lakhs).
  - Do **not** force mathematical reconciliation against GL advertising line items without an authoritative marketing accounting schedule.
  - Do **not** assert that summit leads were objectively high quality or cold as established fact.
- **Impact on Cockpit Logic:** Cockpit quotes Nikhil's statement verbatim with an explicit uncertainty warning, flags `CONF-009`, and cites `E048`.
- **Confidence:** **LOW (for verbal claim)** / **HIGH (for GL records)**
- **What Would Change Conclusion:** Signed marketing budget variance report from CFO Meera Iyer or FP&A Manager Karthik Subramanian, or verified HubSpot lead-to-opportunity pipeline export.
- **Human Decision Status:** **`UNRESOLVED`** (Maintained as unverified verbal claim).

---

## Conflict CONF-010: Atlas Launch Kit Preparation vs Verified Handover & Website Publishing Status

### 1. Competing Sources
- **Product Marketing Document:** `Atlas_Launch_Kit_v1.pdf` (Owner: Sid, 21 Jul 2026)  
  *Asset Status Register:*
  - Launch deck (sales): `Ready`
  - Website page: `Ready, unpublished`
  - Customer email sequence (3): `Ready`
  - Press note: `Draft`
  - Launch date: `TBC with engineering (planned 22 Sep)`
- **Verbal Transcript Statement:** `T4_Head_of_Marketing_Call.docx` (P6)  
  *Nikhil Bose assertion:* Claims Sid's *"v3 launch kit has been ready since July, just waiting on engineering"*.
- **Executive Correspondence:** `05.eml` (Wed, 22 Jul 2026 18:05 IST)  
  *Siddharth Mehta to Nikhil Bose & Vikram Menon:* *"Launch kit is done (deck, page, emails). Just need a date from engineering."*
- **Offboarding Records:** `Resignation_Letter_SM.pdf` & `Hiring_Tracker.xlsx`  
  *Exit Context:* Sid Mehta exited on 31 Oct 2026; his promise to hand over materials remains an exit commitment; backfill `REQ-016` remains open with 7 pipeline candidates.

### 2. Human Conflict Decision (Asset Readiness vs Publication & Operational Handover)
- **Authoritative Operational Distinction:** Distinguish between **asset preparation**, **public publishing**, and **verified operational handover**:
  1. *Preparation:* Marketing assets (sales deck, website copy, 3 email sequences) were drafted by July 2026.
  2. *Publishing:* The website page is explicitly **Ready, unpublished** and the press release is in **Draft** status awaiting engineering GA.
  3. *Handover:* With Siddharth Mehta having exited on 31 October and backfill `REQ-016` open, handover to an active full-time owner remains unverified post-exit.
- **Impact on Cockpit Logic:** Queries regarding launch readiness confirm asset preparation but clarify that the website is unpublished and press note draft, cite `E055` and `E058`, and flag `CONF-010`.
- **Confidence:** **HIGH**
- **What Would Change Conclusion:** Live website publication verification, CMS publishing audit log, or signed handover acknowledgement from Nikhil Bose.
- **Human Decision Status:** **`RESOLVED WITH DISTINCTIONS`** (Grounded in launch kit asset status table).

---

## T6b Executive Voice Note Decision Record

### 1. Source Context
- **Source:** `T6b_CEO_Voice_Note.docx` (`E050`) (Auto-transcribed WhatsApp voice note forwarded by Ananya's assistant)  
- **Transcription Text:** *"So, marketing will report to the new CRO from next month. Or the month after, still finalising. Make sure the thing doesn't break when we move people around."*  
- **Candidate Governance Status:** **`PROPOSED: ACCEPT WITH GUARDRAILS (Awaiting Human Approval)`**

### 2. Decision & Scope Analysis
- **Decision:** **ACCEPT WITH GUARDRAILS (NOT AN IMMEDIATE FORCED REORGANIZATION)**  
- **What Was Accepted:**
  - Implemented an effective-dated, reversible organizational reporting structure (`OrgReportingLine`) tracking person IDs, roles, reporting targets, effective periods, and governance status (`active` vs `proposed`).
  - Modeled the Chief Revenue Officer (CRO) as an unfilled organizational position without fabricating an unrecorded employee.
  - Delivered an interactive Organizational Simulation endpoint (`GET /api/org/simulation`) allowing executives to preview the reporting hierarchy if marketing reports to the CRO.
  - Preserved access permissions by explicit role and person ID, ensuring changes in reporting titles do not compromise security or data governance.
- **What Was Refused / Bound by Policy:**
  - Refused immediate forced reassignment of Nikhil Bose's active manager to CRO prior to verified hiring records and confirmed effective dates.
  - Refused to alter historical memory attribution, employee identity records, or earlier approved governance decisions.
  - Refused to expand the 14-person grounded agent cohort with an invented CRO persona.
- **Implementation Verification:** Full test coverage in `backend/tests/test_day3.py` verifying proposed line status, dual-mode simulation, and unfinalized guardrails.


### 1. Source Context
- **Source:** `T6a_CEO_Voice_Note.docx` (Auto-transcribed WhatsApp voice note forwarded by Ananya's assistant)  
- **Transcription Text:** *"Hi, quick one. I won't type questions every morning, na. When I open it, it should just tell me what to worry about. Top three. Okay, bye."*
- **Candidate Governance Status:** **`APPROVED: ACCEPT WITH SCOPE (Ratified by Candidate / Human Reviewer)`**

### 2. Decision & Scope Analysis
- **Decision:** **ACCEPT WITH SCOPE**  
- **What Was Accepted:**
  - Default landing screen prominently displays the top-3 ranked enterprise risks (`RISK-001` Atlas v3 launch slippage, `RISK-006` Engineering capacity deficit & engagement collapse, `RISK-002` Executive ARR/burn discrepancy).
  - Each risk card includes severity badge, category, summary, recommended mitigation, and expandable evidence citations.
  - Zero-click executive briefing satisfies Ananya's request without manual morning typing.
- **What Was Refused / Bound by Policy:**
  - The cockpit preserves access to the full enterprise risk registry: a toggle button (`View All 7 Risks`) guarantees full visibility.
  - The cockpit refuses to invent unverified risks or expose confidential qualitative HR comments.
  - Decision is ratified by candidate review while preserving strict evidence boundaries.
