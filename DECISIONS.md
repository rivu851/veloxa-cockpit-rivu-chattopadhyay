# Veloxa CXO Cockpit — Source Conflict Decisions Register
**Assessment Phase:** Individual Hackathon (Day 1 Release — Mon 16 Nov 2026 10:00 IST)  
**Author / Candidate:** Rivu Chattopadhyay  
**Status Policy:** All consequential source conflicts are presented with competing evidence, structured interpretation options, and sensitivity analysis. Every decision is marked **`UNRESOLVED`** until personally reviewed and ratified by the human candidate.

---

## Conflict CONF-001: Annual Recurring Revenue (ARR) Discrepancy

### 1. Competing Sources
- **Formal Governance Record A:** `Board_Update_Apr-Jun_2026.pdf` (Page 1, Key Numbers)  
  *Reported Metric:* `ARR (recurring): Rs. 5.8 Cr` (61 customers). Sent 8 Jul 2026.
- **Formal Governance Record B:** `Board_Update_Jul-Sep_2026.pdf` (Page 1, Key Numbers)  
  *Reported Metric:* `ARR (recurring): Rs. 6.1 Cr` (66 customers). Sent 6 Oct 2026.
- **Verbal Statement C:** `T1_CEO_Kickoff_Call.docx` (Summary)  
  *CEO Ananya Rao assertion:* ARR is *"around forty-two crore, maybe forty-five now"*.
- **Verbal Statement D:** `T2_CFO_Call.docx` (Summary)  
  *CFO Meera Iyer assertion:* ARR at start of year was *"forty-eight"*.

### 2. Discrepancy Analysis
A massive **~7x to 8x variance** exists between formal board reports (Rs. 6.1 Cr) and the CEO's verbal claim (Rs. 42-45 Cr).

### 3. Proposed Interpretation Options
- **Option 1 (Recommended Cockpit Base):** The audited Board reports represent true SaaS subscription Annual Recurring Revenue (Rs. 6.1 Cr as of Q2). The CEO conflated platform Gross Merchandise Value (GMV) / annualized transaction volume passing through Veloxa's routing engine with recurring software license fees.
- **Option 2:** The CEO is referencing multi-year Total Contract Value (TCV) across customer lifespans or unweighted sales pipeline.
- **Option 3:** The CEO conflated company post-money equity valuation (e.g. $5M / ~Rs. 42 Cr) with annual revenue. CFO Meera's "forty-eight" refers to Rs. 4.8 Cr (48 Lakhs x 10 or FY26 closing ARR).

### 4. Candidate Assessment & Recommendation
- **Cockpit Decision:** Treat **Rs. 6.1 Crore** as the authoritative recurring revenue metric in all financial answers. When CEO asks for ARR, present Rs. 6.1 Cr, cite E006, and trigger `CONF-001` conflict alert explaining the verbal variance.
- **Confidence:** **MEDIUM**
- **What Would Change Conclusion:** Audited FY26-27 statutory financial statements, detailed revenue recognition schedule from Zoho Books, or signed customer Master Services Agreements (MSAs).
- **Human Decision Status:** **`UNRESOLVED`** (Pending Candidate Confirmation)

---

## Conflict CONF-002: Monthly Burn Rate Discrepancy

### 1. Competing Sources
- **Formal Governance Record A:** `Board_Update_Apr-Jun_2026.pdf` (Page 1, Key Numbers)  
  *Reported Metric:* `Monthly burn: Rs. 46 L` (Runway: 14 months). Sent 8 Jul 2026.
- **Formal Governance Record B:** `Board_Update_Jul-Sep_2026.pdf` (Page 1, Key Numbers)  
  *Reported Metric:* `Monthly burn: Rs. 44 L` (Runway: 13 months). Sent 6 Oct 2026.
- **Financial General Ledger:** `GL_Export_Apr-Sep_2026.xlsx` (Selected cost centres)  
  *Ledger Outflow:* Monthly payroll alone (`PAYROLL`) is fixed at `Rs. 31,75,000` (~31.75 L) every month from Apr to Sep 2026. WeWork rent is `Rs. 2,36,000` (2.36 L), and AWS cloud infra ranges from `Rs. 1,81,200` to `Rs. 2,48,310`. Total fixed monthly cash outflow exceeds Rs. 36-45 Lakhs.
- **Verbal Statement C:** `T2_CFO_Call.docx` (Summary)  
  *CFO Meera Iyer assertion:* Burn has been *"two point two lakhs a month, sometimes two point five"*.
- **Verbal Statement D:** `T1_CEO_Kickoff_Call.docx` (Key points)  
  *CEO Ananya Rao assertion:* Burn is *"around two point two"* (unit unstated).

### 2. Discrepancy Analysis
A **~20x variance** between verified cash ledger outflows / board burn reports (~Rs. 44 L) and verbal executive statements (Rs. 2.2-2.5 L). If gross burn were only 2.2 L/month with 13 months runway, Veloxa's cash balance would be an implausibly small Rs. 28 Lakhs. At Rs. 44 L/month with 13 months runway, Veloxa holds ~Rs. 5.72 Crore in bank reserves, matching an institutional Series A venture profile.

### 3. Proposed Interpretation Options
- **Option 1 (Mathematically Grounded - Recommended):** CFO Meera was stating **Net Cash Burn**, not Gross Burn. At Rs. 6.1 Cr ARR, monthly revenue collections are approximately Rs. 50.8 Lakhs. If gross operating expenses are ~Rs. 53 Lakhs, net cash depletion is approximately **Rs. 2.2 to 2.5 Lakhs per month**.
- **Option 2 (Acoustic Truncation):** MeetNotes AI dropped "forty" over the speakerphone, truncating *"forty-two point five"* (42.5 L) to *"two point two to two point five"*.
- **Option 3:** Executive referred strictly to non-payroll discretionary spending (rent + AWS + marketing SaaS).

### 4. Candidate Assessment & Recommendation
- **Cockpit Decision:** Report **Rs. 44 Lakhs/month** as the authoritative Gross Burn Rate (with 13 months runway), while documenting Option 1 (Net Burn ~2.2 L) as the primary explanatory hypothesis.
- **Confidence:** **MEDIUM**
- **What Would Change Conclusion:** Monthly bank reconciliation statements, actual customer cash receipts ledger, or CFO confirmation.
- **Human Decision Status:** **`UNRESOLVED`** (Pending Candidate Confirmation)

---

## Conflict CONF-003: Headcount & Scope of Keka HRMS Export

### 1. Competing Sources
- **HR System Record:** `Employee_Master.xlsx` (Sheet Employees, Row 1 & Rows 3-22)  
  *Reported Headcount:* Exactly 19 employee rows (VX001 to VX019). Row 1 explicitly states: *"Keka HRMS export, employees only (contractors are not in Keka). Exported 31-Oct-2026."*
- **Board Governance Updates:** `Board_Update_Apr-Jun_2026.pdf` & `Board_Update_Jul-Sep_2026.pdf`  
  *Reported Metric:* `Team: 19` in both Q1 and Q2.
- **Verbal Statement:** `T1_CEO_Kickoff_Call.docx` (Summary)  
  *CEO Ananya Rao assertion:* Company is *"roughly eighteen people ('one-eighty, give or take')"*.

### 2. Discrepancy Analysis
The HR database and board reports confirm 19 employees. Within Keka, 18 are "Active" and 1 is on "Notice period" (Siddharth Mehta, exit date 2026-10-31). The CEO's remark contains both "eighteen" and "one-eighty".

### 3. Proposed Interpretation Options
- **Option 1 (Acoustic Artifact):** MeetNotes AI transcribed the CEO's verbal phrase *"eighteen, give or take"* as *"one-eighty, give or take"*. Ananya counted active full-time staff (18 active excluding Siddharth on notice).
- **Option 2 (Extended Workforce):** Veloxa employs ~180 total personnel when counting third-party logistics contractors, delivery drivers, and warehouse operators who are not onboarded into Keka HRMS.

### 4. Candidate Assessment & Recommendation
- **Cockpit Decision:** Authoritative full-time employee headcount is **19** (18 Active, 1 Notice Period). Clearly disclose that contractors are excluded from Keka.
- **Confidence:** **HIGH**
- **What Would Change Conclusion:** Vendor contractor agreements, Culture Amp pulse survey respondent counts, or contractor payroll registers.
- **Human Decision Status:** **`UNRESOLVED`** (Pending Candidate Confirmation)

---

## Conflict CONF-004: Rahul Verma Partial-Month February Payroll Defect

### 1. Competing Sources
- **Employee Master:** `Employee_Master.xlsx` (Row 21)  
  *Rahul Verma (VX018):* Join Date: `2026-02-03`.
- **Payroll Email Thread:** `01.eml` (28 Feb 2026 20:15 IST)  
  *Karthik Subramanian to Meera Iyer:* *"Ran Feb payroll since Fatima is out. Used the Jan sheet and added the new joiner. Totals attached in the register."*
- **Payroll Register:** `Payroll_Register_Jan-Mar_2026.xlsx` (Sheet Payroll Q4)  
  *Feb-2026 (Row 39):* Rahul Verma is credited with `Days in Month: 28`, `Days Payable: 28`, Gross: Rs. 1,10,000 (100% full month pay, zero pro-ration for joining on Feb 3).  
  *Mar-2026 (Row 58):* Rahul Verma is paid full gross Rs. 1,10,000 with zero clawback or deduction.
- **Employee Inquiry:** `02.eml` (06 Mar 2026 11:02 IST)  
  *Rahul Verma to Fatima Sheikh:* *"The amount looks higher than what I expected for a partial month. Is that right?"*
- **Payroll Acknowledgement:** `03.eml` (10 Mar 2026 15:40 IST)  
  *Fatima Sheikh to Rahul Verma:* *"Will check and get back."*

### 2. Discrepancy Analysis
Rahul joined on 3 Feb 2026. In a 28-day month, days payable should have been 26 days (`26/28 * Rs. 1,10,000 = Rs. 1,02,143`). Overpayment was Rs. 7,857. Karthik copied the January template without adjusting days payable. Rahul reported it honestly, Fatima acknowledged it, but March payroll was processed without adjustment.

### 3. Governance & Privacy Constraint
Under CFO Meera's directive (`T2_CFO_Call`), individual salary figures must **never** be presented to CEO Ananya. Therefore, the Cockpit must report the procedural controls defect (un-prorated joiner pay and absence of dual-authorization) without revealing Rahul's specific salary numbers in executive queries.

### 4. Candidate Assessment & Recommendation
- **Cockpit Decision:** Flag this as an internal accounting control risk (Risk #5). Mask individual compensation figures in CEO queries via the service privacy layer.
- **Confidence:** **HIGH**
- **What Would Change Conclusion:** April payroll adjustments or Keka module migration reconciliation notes.
- **Human Decision Status:** **`UNRESOLVED`** (Pending Candidate Confirmation)
