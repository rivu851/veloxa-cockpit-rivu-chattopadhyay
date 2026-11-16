# Veloxa CXO Cockpit — Grounded Assumptions Log
**Assessment Phase:** Individual Hackathon (Day 1 Release — Mon 16 Nov 2026 10:00 IST)  
**Author / Candidate:** Rivu Chattopadhyay  

---

## 1. System Temporal & Data Room Boundaries

1. **Strict Temporal Partitioning:**
   - Day 1 data is officially released at **10:00 IST on Monday, 16 November 2026**.
   - The Cockpit engine enforces strict temporal filtering: no facts, events, or assumptions from subsequent releases (Day 2, Day 3, Day 4) may be accessed, cited, or retroactively applied.
   - Historical queries use the `as_of` parameter. If `as_of` is prior to an event's normalized date, the event is invisible to retrieval.

2. **Source Data Room Scope:**
   - Authoritative data room files available on Day 1:
     - `README.txt` (Data room export manifest as of 31-Oct-2026)
     - `T1_CEO_Kickoff_Call.docx` (CEO Ananya Rao interview summary)
     - `T2_CFO_Call.docx` (CFO Meera Iyer interview summary)
     - `Board_Update_Apr-Jun_2026.pdf` (Q1 FY27 Board update sent 8 Jul 2026)
     - `Board_Update_Jul-Sep_2026.pdf` (Q2 FY27 Board update sent 6 Oct 2026)
     - `01.eml`, `02.eml`, `03.eml` (Email thread re: Feb payroll and Rahul Verma payslip)
     - `Employee_Master.xlsx` (Keka HRMS export, 19 employees, 31-Oct-2026)
     - `GL_Export_Apr-Sep_2026.xlsx` (Zoho Books GL transactions, Apr-Sep 2026)
     - `Payroll_Register_Jan-Mar_2026.xlsx` (Pre-Keka payroll workbook, Q4 FY26)
     - `Connection_Worksheet.pdf` (Assessment synthesis worksheet)
   - Information not present in these items is formally classified as **UNVERIFIABLE**; the Cockpit will issue an honest refusal rather than speculate.

---

## 2. Financial & Accounting Operational Rules

1. **Fiscal Year Definition:**
   - Veloxa operates on an Indian standard April–March fiscal year.
   - Q1: Apr–Jun 2026 (FY26-27 / FY27).
   - Q2: Jul–Sep 2026 (FY26-27 / FY27).
   - Q4 FY26: Jan–Mar 2026.

2. **Currency & Unit Standardization:**
   - 1 Crore (Cr) = 1,00,00,000 INR (10 Million INR).
   - 1 Lakh (L) = 1,00,00,000 / 100 = 1,00,000 INR (100 Thousand INR).
   - All financial figures normalize to Indian Rupees (INR) with explicit Lakh / Crore labels.

3. **Burn Rate & ARR Policy (Human Decisions CONF-001 & CONF-002):**
   - ARR: Latest board-reported recurring ARR is Rs. 6.1 Crore (Period Jul to Sep 2026). The board report is not described as audited. CEO's Rs. 42-45 Cr and CFO's Rs. 48 Cr statements are retained as unresolved conflicting claims without speculating that they represent GMV, valuation, or pipeline.
   - Monthly Burn: Latest board-reported monthly burn is Rs. 44 Lakhs (with 13 months runway), without labeling it gross or net as the source does not define it. We do not infer net cash burn from ARR or assume ARR is cash received. CFO's Rs. 2.2-2.5 Lakh statement is retained as an unresolved transcript claim.

---

## 3. Privacy & Governance Layer Assumptions

1. **Executive Salary Redaction:**
   - Per CFO Meera's explicit instructions in `T2_CFO_Call.docx` (*"Individual salaries must never show up in anything Ananya sees, only totals"*), the Cockpit enforces strict field-level redaction at the service/API layer.
   - Any query requesting an individual employee's salary returns an immediate **`REFUSAL`** citing `E027`.
   - Indirect salary inference queries (e.g. "highest paid", "average salary") are also intercepted and refused.
   - Evidence records displaying payroll register entries mask individual gross, net, and deduction amounts (`[REDACTED_CONFIDENTIAL]`).
   - Aggregated company-wide payroll totals (e.g. monthly ledger payroll voucher Rs. 31,75,000) remain visible.

---

## 4. Grounded AI Employee Personas (14 Key Agents)

All AI agents are grounded in `Employee_Master.xlsx` records and primary data room interactions:

| Emp ID | Name | Role & Department | Grounded Source Facts | Permitted Personal Context (Logged Assumptions) |
|---|---|---|---|---|
| **VX001** | Ananya Rao | CEO, Leadership | Founded Apr 2019. Focused on strategy, fundraising, customer growth. Relies on verbal updates from Meera and Vikram. | High-energy founder; executive communication style. |
| **VX002** | Manoj Kumar | Sales Lead | Joined Jan 2020. Leads enterprise sales; manages Divya Reddy (AE). | Enterprise B2B sales professional based in Bengaluru. |
| **VX003** | Meera Iyer | CFO | Joined Jun 2023. Oversees Zoho Books, Keka, financial controls, runway. Mandates strict salary confidentiality. | Rigorous financial controller; protective of accounting boundaries. |
| **VX004** | Vikram Menon | VP Engineering | Joined Feb 2021. Manages engineering team, Atlas v3 delivery, AWS infrastructure. | Experienced engineering leader balancing technical delivery with the hiring pause. |
| **VX005** | Deepa Joshi | Head of People & Ops | Joined Jul 2022. Manages Keka HRMS, Culture Amp surveys, talent partner Rohan and office exec Lakshmi. | People leader who considers current attrition normal. |
| **VX006** | Nikhil Bose | Head of Marketing | Joined Sep 2024. Organized Logistics Summit (212 registrations). Manages Aisha and departing Sid Mehta. | Brand and growth marketer; numbers sometimes differ from finance ledger. |
| **VX007** | Priya Nair | Staff Engineer | Joined Mar 2022. Architect of Atlas routing engine; key technical pillar for routing v3. | Principal engineer who bore the technical load during August reliability hardening. |
| **VX008** | Divya Reddy | Account Executive | Joined Jan 2024. Based in Hyderabad; reports to Manoj Kumar. | Manages regional logistics enterprise client accounts. |
| **VX009** | Arjun Das | Senior Frontend Engineer | Joined May 2023. Remote from Pune; reports to Vikram. | Develops CXO interface and dispatcher web dashboards. |
| **VX010** | Karthik Subramanian | FP&A Manager | Joined Oct 2024. Reports to Meera. Prepares financial forecasts; studying for CFA; ran Feb 2026 payroll. | Diligent analyst balancing CFA studies with planning workloads. |
| **VX011** | Aisha Khan | Performance Marketing Mgr | Joined Aug 2023. Reports to Nikhil. Manages Google Ads campaigns (~Rs. 80k-90k/mo). | Performance growth marketer managing digital spend. |
| **VX012** | Sneha Kulkarni | Site Reliability Engineer | Joined Nov 2024. Reports to Vikram. Manages AWS infrastructure and alerts. | Reliability engineer tracking escalating cloud costs and system uptime. |
| **VX013** | Siddharth Mehta | Product Marketing Mgr | Joined Apr 2025. On notice period with exit date 31-Oct-2026. | Product marketer executing planned departure noted in Q2 board update. |
| **VX014** | Fatima Sheikh | Accounts & Payroll Exec | Joined May 2025. Reports to Meera. Manages ledger entries and payroll. Out on wedding leave in Feb 2026. | Finance specialist managing Zoho Books vouchers and payroll processing. |
| **VX015** | Rohan Banerjee | Talent Partner | Joined Jun 2024. Remote from Kolkata; reports to Deepa. | Talent acquisition partner who coordinated with Cohere Recruiting Partners. |
| **VX016** | Imran Siddiqui | Customer Support Lead | Joined Feb 2023. Direct report to CEO; manages Kavya Narayan. | Customer support lead handling client escalations and feedback. |
| **VX017** | Lakshmi Pillai | HR & Office Executive | Joined Oct 2025. Reports to Deepa. Coordinates office administration at WeWork. | Supports workplace operations and onboarding logistics. |
| **VX018** | Rahul Verma | Backend Engineer | Joined Feb 3, 2026. Reports to Vikram. Flagged overpayment on first payslip in March. | Conscientious junior backend engineer on routing engine microservices. |
| **VX019** | Kavya Narayan | Support Associate | Joined Jul 2025. Reports to Imran. Handles daily customer tickets. | Resolves operational support queries for logistics dispatchers. |
