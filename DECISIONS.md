# Veloxa CXO Cockpit — Source Conflict Decisions Register
**Assessment Phase:** Individual Hackathon (Day 1 Release — Mon 16 Nov 2026 10:00 IST)  
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

## Conflict CONF-004: Rahul Verma Partial-Month February Payroll Defect

### 1. Competing Sources
- `Employee_Master.xlsx` (Row 21): Rahul Verma Join Date `2026-02-03`.
- `01.eml` (28 Feb 2026): Karthik states he ran Feb payroll using the Jan sheet and added the new joiner because Fatima was out.
- `Payroll_Register_Jan-Mar_2026.xlsx` (Rows 39 & 58): Rahul Verma was credited for 28 payable days in February (full month gross). March payroll credited 31 payable days with zero clawback or adjustment.
- `02.eml` & `03.eml` (6 & 10 Mar 2026): Rahul queried the high payslip for a partial month; Fatima promised to check and get back.

### 2. Human Conflict Decision
- **Finding:** Procedural defect in payroll processing confirmed across email and payroll sheets.
- **Privacy Constraint:** Individual salary numbers are strictly confidential and must never be exposed to executive queries. The cockpit reports the audit defect (lack of pro-ration and absence of dual authorization) while redacting monetary figures.
- **Confidence:** **HIGH**
- **Human Decision Status:** **`UNRESOLVED`** (Pending reconciliation in Keka payroll module).
