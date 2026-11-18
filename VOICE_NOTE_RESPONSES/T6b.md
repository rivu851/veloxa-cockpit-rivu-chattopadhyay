# Executive Decision Memo — Response to CEO Voice Note T6b

**To:** Ananya Rao, Chief Executive Officer, Veloxa Technologies  
**From:** Implementation Lead / CXO Cockpit Architecture (Candidate: Rivu Chattopadhyay)  
**Date:** Wednesday, 18 November 2026 (Day 3 Milestone, 11:59 PM IST Target)  
**Reference Document:** `T6b_CEO_Voice_Note.docx` (`E050`)  
**Decision Governance Status:** **`PROPOSED: ACCEPT WITH GUARDRAILS (Awaiting Candidate / Human Approval)`**  

---

## 1. Exact CEO Voice Note Request

> *"So, marketing will report to the new CRO from next month. Or the month after, still finalising. Make sure the thing doesn't break when we move people around."*  
> — Ananya Rao, CEO (forwarded WhatsApp voice note transcript, `T6b_CEO_Voice_Note.docx`, `E050`)

---

## 2. Decision Status & Executive Summary

- **Proposed Decision:** **ACCEPT WITH GUARDRAILS (NOT AN IMMEDIATE FORCED REORGANIZATION)**  
- **Governance Classification:** **PROPOSED**, awaiting explicit human approval. No approved effective date or appointment exists.
- **Executive Rationale:**  
  The CEO's directive signals an upcoming executive organizational realignment to introduce a Chief Revenue Officer (CRO) overseeing commercial and marketing operations. However, the voice note explicitly acknowledges that timing and arrangements remain unfinalized (*"from next month. Or the month after, still finalising"*). Crucially, no CRO exists in Keka HRMS, Employee Master (`E020`), or commercial contracts; no individual is appointed; and no effective appointment date is set.
  
  Executing an immediate, forced hard-coded reporting reassignment in production would violate fundamental data integrity principles:
  1. It would prematurely break active reporting lines, confusing active team governance.
  2. It would invent an ungrounded 20th person or alter the 14-person grounded agent cohort without primary HR backing.
  3. It would risk altering historical memory attribution, access privileges, and past audit trails.

  Therefore, we **accept** the strategic intent by architecting a versioned, effective-dated, and completely reversible organizational reporting framework (`OrgReportingLine`), but enforce strict **guardrails**:
  - The CRO position is modeled as an **unfilled executive role**, not a fabricated employee.
  - The proposed reporting relationship for Head of Marketing (Nikhil Bose) is cataloged with `status="proposed"`.
  - In active operational reporting (`as_of`), Nikhil Bose continues to report directly to CEO Ananya Rao (`status="active"`).
  - An interactive **Organizational Simulation Preview** (`/api/org/simulation`) is provided to preview the reporting structure without disrupting live system permissions or historical accountability.

---

## 3. What Was Changed in the CXO Cockpit

1. **Effective-Dated Reversible Reporting Data Model (`OrgReportingLine`):**
   - Implemented an immutable, versioned organizational relationship table in SQLite:
     ```python
     class OrgReportingLine(Base):
         id = Column(Integer, primary_key=True)
         person_id = Column(String(20), nullable=True)          # e.g. VX006 (Nikhil Bose)
         department = Column(String(50), nullable=False)        # Marketing
         role_title = Column(String(100), nullable=False)       # Head of Marketing
         reports_to_role = Column(String(100), nullable=False)  # "CEO" (active) / "CRO" (proposed)
         reports_to_person_id = Column(String(20), nullable=True) # VX001 (CEO) / None (unfilled)
         status = Column(String(30), nullable=False)            # "active" vs "proposed"
         valid_from = Column(DateTime, nullable=True)
         valid_to = Column(DateTime, nullable=True)
         source_ref = Column(String(50), nullable=True)         # "T6b", "Employee_Master.xlsx"
         citation = Column(Text, nullable=True)
     ```
   - Separates individual identity (`Person.emp_id`, e.g. `VX006`) from positional reporting relationships, ensuring employee IDs remain permanent and immutable across reorganizations.

2. **Unfilled Executive Role Modeling (No Persona Hallucination):**
   - The CRO is modeled as an unfilled positional entity (`reports_to_role="CRO"`, `reports_to_person_id=None`).
   - The 19-person Employee Master and 14 interviewable agent cohorts are strictly preserved. The Cockpit refuses to invent an unverified 20th employee or speculative persona.

3. **Dedicated Interactive Org Simulation Endpoint (`GET /api/org/simulation`):**
   - Supports dual-mode organizational inspection:
     - `mode="actual_as_of"`: Returns verified active reporting hierarchy where Nikhil Bose reports to CEO Ananya Rao (`E064`).
     - `mode="simulated_cro"`: Generates an organizational simulation illustrating marketing reporting to the proposed CRO position, clearly badged as `PROPOSED (UNFILLED ROLE)`.

4. **Marketing Dashboard Overview Integration (`GET /api/marketing-overview`):**
   - The cockpit marketing view displays an active governance notification banner:
     > `PROPOSED REALIGNMENT: Marketing -> CRO (Pending Appointment & Authorization; Active Line: CEO)`
   - Cites `E050` (`T6b_CEO_Voice_Note.docx`) and references `CONF-010` and `CONF-009`.

5. **Natural Language Query Refusal / Honest Guardrail:**
   - Queries asking *"Is the new CRO already managing marketing?"* or *"Who does marketing report to?"* return a structured refusal / guardrail explanation:
     > `REFUSAL / PROPOSED ONLY: Under CXO Cockpit governance guardrails, the new CRO is NOT currently managing marketing. In voice note T6b, CEO Ananya Rao stated the reporting transition is unfinalized ('from next month or the month after, still finalising'). No CRO is appointed in Employee Master records. Head of Marketing Nikhil Bose continues to report to CEO Ananya Rao in active operations.`

---

## 4. What Was Deliberately Refused or Bound by Policy

1. **Refusal of Immediate Forced Reassignment:**
   - The Cockpit refuses to flip Nikhil Bose's active manager to "CRO" or overwrite `people.manager_id` prior to formal HR appointment records and verified candidate authorization.
   - Immediate reassignment would disrupt auditability and create false compliance states.

2. **Refusal to Fabricate Employee Personas:**
   - The Cockpit strictly refuses to generate a fictional name, salary, bio, or agent memory for the CRO.
   - The CRO remains an unfilled institutional node until confirmed by formal hiring records.

3. **Protection of Historical Attribution and Memory Isolation:**
   - Historical agent memories (e.g., Nikhil's past campaign approvals, summit spend discussions with Meera, launch kit coordination with Sid) remain tied to `VX006` and are never retroactively attributed to the CRO.
   - System access permissions are bound to authenticated person IDs and explicit role scopes, not informal manager names.

---

## 5. Primary Source Evidence References

| Evidence Ref | Source Document | Key Grounded Fact |
|---|---|---|
| `E050` | `T6b_CEO_Voice_Note.docx` | CEO voice note: Marketing reporting to new CRO unfinalized ("from next month or month after"). |
| `E064` | `T6b_CEO_Voice_Note.docx` / `Employee_Master.xlsx` | Org reporting baseline: Head of Marketing currently reports to CEO; CRO line cataloged as proposed. |
| `E020` | `Employee_Master.xlsx` | Keka HRMS records establish 19 employees; no CRO exists in company headcount. |
| `E048` | `T4_Head_of_Marketing_Call.docx` | Nikhil Bose notes hearing rumors of reporting to new CRO but confirms no date exists. |
| `E055` | `Atlas_Launch_Kit_v1.pdf` | Atlas launch kit website remains "Ready, unpublished" under current marketing team. |
| `E058` | `05.eml` | Sid Mehta completed kit assets in July, waiting on engineering GA date. |
| `E032` | `Resignation_Letter_SM.pdf` | Sid Mehta exited 31 Oct; REQ-016 backfill remains open with 7 candidates. |

---

## 6. Analysis of Unknowns & Operational Risks

1. **Candidate Identity & Timing:**
   - Who the CRO will be, their compensation, start date, and whether sales (`VX002` Manoj Kumar) will also report to them are completely unrecorded.
   - The simulation currently isolates the change to Marketing; if Sales is later included, the schema supports adding an effective-dated line without migration overhead.

2. **Key-Person Vacuum During Commercial Realignment:**
   - With Siddharth Mehta having exited on 31 Oct (`E032`) and backfill REQ-016 open (`E041`), marketing leadership is already under strain.
   - Announcing premature reporting transitions without an appointed executive risks aggravating marketing pulse engagement (which fell to 3.4 in Q2, `E046`).

---

## 7. Automated Verification & Test Coverage

The implementation is verified by automated pytest tests in `backend/tests/test_day3.py`:
- `test_t6b_proposed_cro_reporting_guardrail`: Verifies that querying whether the CRO is managing marketing returns a refusal/guardrail explaining unfinalized status.
- `test_org_simulation_dual_mode`: Validates that `actual_as_of` reports Nikhil -> CEO (active) and `simulated_cro` reports Nikhil -> CRO (proposed, unfilled role).
- `test_immutable_person_master_preserved`: Asserts that `people` table remains strictly 19 records and 14 interviewable agents without inventing a CRO employee.
- `test_agent_nikhil_cro_knowledge`: Asserts that agent Nikhil Bose acknowledges hearing about the CRO transition but confirms no active date exists.

---

## 8. Rollback Plan

If executive leadership decides not to proceed with the CRO hire or alters commercial hierarchy:
1. Set `OrgReportingLine.status = "deprecated"` where `reports_to_role = "CRO"`.
2. No database migration or schema alteration is required.
3. Active operational reporting (`status="active"`) continues uninterrupted without data loss or historical skew.
