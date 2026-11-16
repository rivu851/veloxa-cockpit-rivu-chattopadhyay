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

## 4. Grounded AI Employee Personas (14 Interviewable Agents Cohort)

All 19 employees from `Employee_Master.xlsx` are preserved in the `people` table. Exactly 14 are selected as active interviewable personas based on documented operational criteria:

### Selection Criteria for Interviewable Cohort (14 Agents)
1. **Executive Leadership:** Strategic direction, governance, and capital funding (`VX001` Ananya Rao, `VX003` Meera Iyer, `VX004` Vikram Menon, `VX005` Deepa Joshi, `VX006` Nikhil Bose).
2. **Core Technical & Engineering:** Critical contributors to Atlas v3 routing engine and reliability (`VX007` Priya Nair, `VX009` Arjun Das, `VX012` Sneha Kulkarni, `VX018` Rahul Verma).
3. **Commercial & Customer Growth:** Revenue execution and campaign metrics (`VX002` Manoj Kumar, `VX008` Divya Reddy, `VX011` Aisha Khan).
4. **Financial Control & Payroll Operations:** Direct participants in ledger vouchers and payroll registers (`VX010` Karthik Subramanian, `VX014` Fatima Sheikh).

### Documented Exclusion Criteria (5 Non-Interviewable Employees)
- `VX013` (Siddharth Mehta, Product Marketing Manager): `is_interviewable=False`. On notice period with formal exit date 31-Oct-2026; excluded per offboarding governance.
- `VX015` (Rohan Banerjee, Talent Partner): `is_interviewable=False`. Recruitment activities halted under company-wide hiring freeze.
- `VX016` (Imran Siddiqui, Customer Support Lead): `is_interviewable=False`. Tier 2 ticket operations; non-core for Day 1 strategic decisions.
- `VX017` (Lakshmi Pillai, HR & Office Executive): `is_interviewable=False`. Routine facility and clerical logistics; non-core.
- `VX019` (Kavya Narayan, Support Associate): `is_interviewable=False`. Junior customer support associate; non-core.

### Persona Assumption & Memory Safeguard Policy
- **Fictional Context Boundary:** Permitted personal background (e.g. coffee preferences, cycling, cricket) is logged in `agent_memories` with `memory_type="personal_life"` and must include an explicit disclaimer:
  > *"Note: Persona context is fictional background and does not constitute factual business evidence."*
- **Memory Isolation:** Multi-turn conversational memory is strictly keyed to `emp_id`. An agent cannot retrieve another agent's dialogue turns.
- **Privacy Barrier:** Conversational memory queries cannot bypass salary redaction or retrieve future-release material.

---

## 5. Formal Analytical Assumptions (Persisted in SQLite `assumptions` Table)

| ID | Domain | Statement | Grounded Rationale | Risk if Wrong |
|---|---|---|---|---|
| **`ASM-001`** | ARR | Board-reported recurring ARR of Rs. 6.1 Cr reflects operational subscription run-rate; verbal executive statements of 42-45 Cr are uncorroborated conflicting claims. | Board updates provide concrete customer counts (66) and comparative growth without statutory audit notation. | If verbal figures represent booked GMV or contract values, financial scale is understated. |
| **`ASM-002`** | Burn | Board-reported monthly burn of Rs. 44 L reflects total operational cash outflow without distinguishing gross vs net in absence of ledger receipts. | Primary source does not define gross vs net; ledger disbursements confirm salary alone is 31.75 L. | If 44 L is gross and net is lower, runway projection is compressed. |
| **`ASM-003`** | Headcount | Keka HRMS export of 19 employees represents full-time workforce; contractors are unrecorded in HRMS. | Keka export header explicitly notes contractors are not in Keka. | If contractor pool is large, operational burn and true organization size are underestimated. |
| **`ASM-004`** | Payroll | Rahul Verma February pay is a suspected partial-month calculation discrepancy requiring formal verification. | Rahul queried 26/28 days in 02.eml, acknowledged in 03.eml, but March had no adjustment. | If formal reconciliation was handled off-register or via tax vouchers, discrepancy is non-existent. |
| **`ASM-005`** | Engineering | Atlas v3 is feature-complete but requires production reliability hardening before GA. | Q2 Board update confirms GA shifted for unplanned reliability work after August incidents. | If fundamental routing architecture is unstable, GA timeline may slip into 2027. |
