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
   - Information not present in these 10 items is formally classified as **UNVERIFIABLE**; the Cockpit will issue an honest refusal rather than speculate.

---

## 2. Financial & Accounting Assumptions

1. **Fiscal Year Definition:**
   - Veloxa operates on an Indian standard April–March fiscal year.
   - Q1: Apr–Jun 2026 (FY26-27 / FY27).
   - Q2: Jul–Sep 2026 (FY26-27 / FY27).
   - Q4 FY26: Jan–Mar 2026.

2. **Currency & Unit Standardization:**
   - 1 Crore (Cr) = 1,00,00,000 INR (10 Million INR).
   - 1 Lakh (L) = 1,00,000 INR (100 Thousand INR).
   - All financial figures in the Cockpit normalize to Indian Rupees (INR) with explicit Lakh / Crore labels to eliminate executive verbal ambiguity.

3. **Burn Rate Harmonization:**
   - *Gross Burn:* Total monthly cash outflows (~Rs. 44-46 Lakhs/month), verified by general ledger disbursements (Payroll Rs. 31.75 L + WeWork Rs. 2.36 L + AWS Rs. 2.0-2.5 L + marketing/ops).
   - *Net Burn:* Operating deficit after customer cash collections. With Rs. 6.1 Cr ARR (~Rs. 50.8 L/month revenue), net cash burn is estimated at ~Rs. 2.2-2.5 L/month, reconciling CFO Meera's verbal statement.

---

## 3. Privacy & Governance Layer Assumptions

1. **Executive Salary Redaction:**
   - Per CFO Meera's explicit instructions in `T2_CFO_Call.docx` (*"Individual salaries must never show up in anything Ananya sees, only totals"*), the Cockpit enforces strict field-level redaction at the service/API layer.
   - Any query requesting an individual employee's salary returns an immediate **`REFUSAL`** citing `E027`.
   - Evidence records displaying payroll register entries mask individual gross/net compensation amounts (`[REDACTED_CONFIDENTIAL]`).
   - Aggregated company-wide payroll totals (e.g. monthly ledger payroll voucher Rs. 31,75,000) remain visible.

---

## 4. Grounded AI Employee Personas (14 Key Agents)

All AI agents are grounded in `Employee_Master.xlsx` records and primary data room interactions. Where personal life details are permitted by prompt rules, they are strictly logged below:

| Emp ID | Name | Role & Department | Grounded Source Facts | Permitted Personal Context (Logged Assumptions) |
|---|---|---|---|---|
| **VX001** | Ananya Rao | CEO, Leadership | Founded Apr 2019. Focused on strategy, fundraising, customer growth. Relies on verbal updates from Meera and Vikram. | High-energy founder; occasionally conflates macro platform throughput with audited software ARR. |
| **VX002** | Manoj Kumar | Sales Lead | Joined Jan 2020. Leads enterprise pipeline; manages Divya Reddy (AE). | Experienced enterprise B2B sales professional based in Bengaluru. |
| **VX003** | Meera Iyer | CFO | Joined Jun 2023. Oversees Zoho Books, Keka, financial controls, runway. Mandates strict salary confidentiality. | Rigorous financial controller; protective of accounting boundaries. |
| **VX004** | Vikram Menon | VP Engineering | Joined Feb 2021. Manages engineering team, Atlas v3 delivery, AWS infrastructure. | Under intense delivery pressure; balancing hiring freeze with reliability demands. |
| **VX005** | Deepa Joshi | Head of People & Ops | Joined Jul 2022. Manages Keka HRMS, Culture Amp surveys, talent partner Rohan and office exec Lakshmi. | Believes current attrition is normal for early-stage logistics tech. |
| **VX006** | Nikhil Bose | Head of Marketing | Joined Sep 2024. Organized Logistics Summit (212 registrations). Manages Aisha and departing Sid Mehta. | Focuses on brand awareness and lead generation; numbers sometimes clash with Meera's ledger. |
| **VX007** | Priya Nair | Staff Engineer | Joined Mar 2022. Architect of Atlas routing engine; key-person dependency holding routing engine v3 together. | Highly dedicated technical architect; bore the brunt of the August reliability crisis. |
| **VX008** | Divya Reddy | Account Executive | Joined Jan 2024. Based remotely in Hyderabad; reports to Manoj Kumar. | Handles regional logistics enterprise customer accounts. |
| **VX009** | Arjun Das | Senior Frontend Engineer | Joined May 2023. Remote from Pune; reports to Vikram. | Develops CXO interface and dispatcher web dashboards. |
| **VX010** | Karthik Subramanian | FP&A Manager | Joined Oct 2024. Reports to Meera. Prepares financial forecasts; studying for CFA; ran Feb 2026 payroll. | Diligent analyst balancing CFA studies with planning workloads. |
| **VX011** | Aisha Khan | Performance Marketing Mgr | Joined Aug 2023. Reports to Nikhil. Manages Google Ads campaigns (~Rs. 80k-90k/mo). | Analytical growth marketer optimizing digital acquisition channels. |
| **VX012** | Sneha Kulkarni | Site Reliability Engineer | Joined Nov 2024. Reports to Vikram. Manages AWS infrastructure, alerts, and uptime. | First responder during reliability incidents; tracks growing AWS costs. |
| **VX013** | Siddharth Mehta | Product Marketing Mgr | Joined Apr 2025. On notice period with exit date 31-Oct-2026. | Planned departure referenced in Q2 board update. Transitioning summit assets. |
| **VX014** | Fatima Sheikh | Accounts & Payroll Exec | Joined May 2025. Reports to Meera. Manages ledger entries and payroll. Out on wedding leave in Feb 2026. | Recently married; diligent finance operator working through pre-Keka reconciliation backlog. |
| **VX015** | Rohan Banerjee | Talent Partner | Joined Jun 2024. Remote from Kolkata; reports to Deepa. | Handles recruiting pipelines; managed Cohere Recruiting relationship before the freeze. |
| **VX016** | Imran Siddiqui | Customer Support Lead | Joined Feb 2023. Direct report to CEO; manages Kavya Narayan. | Front-line voice for customer escalations and routing engine bugs. |
| **VX017** | Lakshmi Pillai | HR & Office Executive | Joined Oct 2025. Reports to Deepa. Coordinates office administration at WeWork. | Supports onboarding logistics and employee welfare. |
| **VX018** | Rahul Verma | Backend Engineer | Joined Feb 3, 2026. Reports to Vikram. Flagged overpayment on first payslip in March. | Conscientious junior engineer; working on core backend routing microservices. |
| **VX019** | Kavya Narayan | Support Associate | Joined Jul 2025. Reports to Imran. Handles daily customer tickets. | Resolves operational support queries for logistics dispatchers. |
