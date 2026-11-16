"""
Deterministic Day 1 Ingestion Engine.
Loads structured seed data extracted from Day 1 text room with exact row/column references.
Ensures idempotency across multiple runs and supports incremental future release ingestion.
"""
import datetime
from sqlalchemy.orm import Session
from backend.app.models.schema import Source, Evidence, Claim, Person, Conflict, Assumption, AgentMemory

DAY1_RELEASE_TIME = datetime.datetime(2026, 11, 16, 10, 0, 0)

def ingest_day1_sources(db: Session) -> dict:
    sources_data = [
        {"file_name": "README.txt", "file_type": "txt", "description": "Veloxa data room export manifest as of 31 Oct 2026.", "provenance": "Exported by IT on 31 Oct 2026."},
        {"file_name": "T1_CEO_Kickoff_Call.docx", "file_type": "docx", "description": "MeetNotes AI auto-summary of CEO Ananya Rao kickoff call (38 min, fair audio).", "provenance": "Executive interview transcript."},
        {"file_name": "T2_CFO_Call.docx", "file_type": "docx", "description": "MeetNotes AI auto-summary of CFO Meera Iyer call (26 min, poor speakerphone audio).", "provenance": "Executive interview transcript."},
        {"file_name": "Board_Update_Apr-Jun_2026.pdf", "file_type": "pdf", "description": "Quarterly update for Period Apr to Jun 2026. Sent 8 Jul 2026. Confidential.", "provenance": "Board update document."},
        {"file_name": "Board_Update_Jul-Sep_2026.pdf", "file_type": "pdf", "description": "Quarterly update for Period Jul to Sep 2026. Sent 6 Oct 2026. Confidential.", "provenance": "Board update document."},
        {"file_name": "01.eml", "file_type": "eml", "description": "Email from Karthik Subramanian to Meera Iyer re: Feb payroll done.", "provenance": "Email server export (2026-02-28 20:15 IST)."},
        {"file_name": "02.eml", "file_type": "eml", "description": "Email from Rahul Verma to Fatima Sheikh re: payslip query.", "provenance": "Email server export (2026-03-06 11:02 IST)."},
        {"file_name": "03.eml", "file_type": "eml", "description": "Email from Fatima Sheikh to Rahul Verma re: Re: payslip query.", "provenance": "Email server export (2026-03-10 15:40 IST)."},
        {"file_name": "Employee_Master.xlsx", "file_type": "xlsx", "description": "Keka HRMS export, employees only (contractors are not in Keka). Exported 31-Oct-2026.", "provenance": "Keka HRMS export."},
        {"file_name": "GL_Export_Apr-Sep_2026.xlsx", "file_type": "xlsx", "description": "General ledger export, Zoho Books, Apr to Sep 2026 (selected cost centres).", "provenance": "Zoho Books export."},
        {"file_name": "Payroll_Register_Jan-Mar_2026.xlsx", "file_type": "xlsx", "description": "Payroll register, Jan to Mar 2026. Source: payroll workbook (pre-Keka payroll module).", "provenance": "Payroll workbook.", "is_confidential": True},
        {"file_name": "Connection_Worksheet.pdf", "file_type": "pdf", "description": "Connection worksheet template completed by hand in final session.", "provenance": "Assessment template."},
    ]

    source_map = {}
    for s_dict in sources_data:
        existing = db.query(Source).filter(Source.file_name == s_dict["file_name"]).first()
        if not existing:
            s = Source(
                file_name=s_dict["file_name"],
                file_type=s_dict["file_type"],
                release_day="Day1",
                released_at=DAY1_RELEASE_TIME,
                description=s_dict.get("description"),
                provenance=s_dict.get("provenance"),
                is_confidential=s_dict.get("is_confidential", False)
            )
            db.add(s)
            db.flush()
            source_map[s.file_name] = s.id
        else:
            source_map[existing.file_name] = existing.id
    return source_map

def ingest_day1_people(db: Session):
    employees_data = [
        {"emp_id": "VX001", "full_name": "Ananya Rao", "work_email": "ananya@veloxa.in", "department": "Leadership", "title": "CEO", "manager_id": None, "join_date": "2019-04-01", "location": "Bengaluru", "status": "Active", "system_role_desc": "CEO."},
        {"emp_id": "VX002", "full_name": "Manoj Kumar", "work_email": "manoj@veloxa.in", "department": "Sales", "title": "Sales Lead", "manager_id": "VX001", "join_date": "2020-01-06", "location": "Bengaluru", "status": "Active", "system_role_desc": "Sales Lead."},
        {"emp_id": "VX003", "full_name": "Meera Iyer", "work_email": "meera@veloxa.in", "department": "Finance", "title": "CFO", "manager_id": "VX001", "join_date": "2023-06-12", "location": "Bengaluru", "status": "Active", "system_role_desc": "CFO."},
        {"emp_id": "VX004", "full_name": "Vikram Menon", "work_email": "vikram@veloxa.in", "department": "Engineering", "title": "VP Engineering", "manager_id": "VX001", "join_date": "2021-02-01", "location": "Bengaluru", "status": "Active", "system_role_desc": "VP Engineering."},
        {"emp_id": "VX005", "full_name": "Deepa Joshi", "work_email": "deepa@veloxa.in", "department": "People & Ops", "title": "Head of People & Ops", "manager_id": "VX001", "join_date": "2022-07-04", "location": "Bengaluru", "status": "Active", "system_role_desc": "Head of People & Ops."},
        {"emp_id": "VX006", "full_name": "Nikhil Bose", "work_email": "nikhil@veloxa.in", "department": "Marketing", "title": "Head of Marketing", "manager_id": "VX001", "join_date": "2024-09-02", "location": "Bengaluru", "status": "Active", "system_role_desc": "Head of Marketing."},
        {"emp_id": "VX007", "full_name": "Priya Nair", "work_email": "priya.n@veloxa.in", "department": "Engineering", "title": "Staff Engineer", "manager_id": "VX004", "join_date": "2022-03-14", "location": "Bengaluru", "status": "Active", "system_role_desc": "Staff Engineer on routing engine."},
        {"emp_id": "VX008", "full_name": "Divya Reddy", "work_email": "divya@veloxa.in", "department": "Sales", "title": "Account Executive", "manager_id": "VX002", "join_date": "2024-01-15", "location": "Hyderabad", "status": "Active", "system_role_desc": "Account Executive."},
        {"emp_id": "VX009", "full_name": "Arjun Das", "work_email": "arjun@veloxa.in", "department": "Engineering", "title": "Senior Frontend Engineer", "manager_id": "VX004", "join_date": "2023-05-08", "location": "Pune (remote)", "status": "Active", "system_role_desc": "Senior Frontend Engineer."},
        {"emp_id": "VX010", "full_name": "Karthik Subramanian", "work_email": "karthik.s@veloxa.in", "department": "Finance", "title": "FP&A Manager", "manager_id": "VX003", "join_date": "2024-10-01", "location": "Bengaluru", "status": "Active", "system_role_desc": "FP&A Manager."},
        {"emp_id": "VX011", "full_name": "Aisha Khan", "work_email": "aisha@veloxa.in", "department": "Marketing", "title": "Performance Marketing Manager", "manager_id": "VX006", "join_date": "2023-08-21", "location": "Bengaluru", "status": "Active", "system_role_desc": "Performance Marketing Manager."},
        {"emp_id": "VX012", "full_name": "Sneha Kulkarni", "work_email": "sneha.k@veloxa.in", "department": "Engineering", "title": "Site Reliability Engineer", "manager_id": "VX004", "join_date": "2024-11-04", "location": "Bengaluru", "status": "Active", "system_role_desc": "Site Reliability Engineer."},
        {"emp_id": "VX013", "full_name": "Siddharth Mehta", "work_email": "sid@veloxa.in", "department": "Marketing", "title": "Product Marketing Manager", "manager_id": "VX006", "join_date": "2025-04-07", "location": "Bengaluru", "status": "Notice period", "exit_date": "2026-10-31", "system_role_desc": "Product Marketing Manager."},
        {"emp_id": "VX014", "full_name": "Fatima Sheikh", "work_email": "fatima@veloxa.in", "department": "Finance", "title": "Accounts & Payroll Executive", "manager_id": "VX003", "join_date": "2025-05-12", "location": "Bengaluru", "status": "Active", "system_role_desc": "Accounts & Payroll Executive."},
        {"emp_id": "VX015", "full_name": "Rohan Banerjee", "work_email": "rohan@veloxa.in", "department": "People & Ops", "title": "Talent Partner", "manager_id": "VX005", "join_date": "2024-06-03", "location": "Kolkata (remote)", "status": "Active", "system_role_desc": "Talent Partner."},
        {"emp_id": "VX016", "full_name": "Imran Siddiqui", "work_email": "imran@veloxa.in", "department": "Support", "title": "Customer Support Lead", "manager_id": "VX001", "join_date": "2023-02-13", "location": "Bengaluru", "status": "Active", "system_role_desc": "Customer Support Lead."},
        {"emp_id": "VX017", "full_name": "Lakshmi Pillai", "work_email": "lakshmi.p@veloxa.in", "department": "People & Ops", "title": "HR & Office Executive", "manager_id": "VX005", "join_date": "2025-10-06", "location": "Bengaluru", "status": "Active", "system_role_desc": "HR & Office Executive."},
        {"emp_id": "VX018", "full_name": "Rahul Verma", "work_email": "rahul.v@veloxa.in", "department": "Engineering", "title": "Backend Engineer", "manager_id": "VX004", "join_date": "2026-02-03", "location": "Bengaluru", "status": "Active", "system_role_desc": "Backend Engineer."},
        {"emp_id": "VX019", "full_name": "Kavya Narayan", "work_email": "kavya@veloxa.in", "department": "Support", "title": "Support Associate", "manager_id": "VX016", "join_date": "2025-07-01", "location": "Bengaluru", "status": "Active", "system_role_desc": "Support Associate."},
    ]

    for emp in employees_data:
        existing = db.query(Person).filter(Person.emp_id == emp["emp_id"]).first()
        if not existing:
            p = Person(
                emp_id=emp["emp_id"],
                full_name=emp["full_name"],
                work_email=emp["work_email"],
                department=emp["department"],
                title=emp["title"],
                manager_id=emp["manager_id"],
                join_date=emp["join_date"],
                location=emp["location"],
                status=emp["status"],
                exit_date=emp.get("exit_date"),
                is_interviewable=True,
                system_role_desc=emp.get("system_role_desc"),
                released_at=DAY1_RELEASE_TIME
            )
            db.add(p)

def ingest_day1_evidence(db: Session, source_map: dict):
    evidence_items = [
        # Board Update Apr-Jun 2026
        {
            "ref": "E001", "source_file": "Board_Update_Apr-Jun_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Key numbers",
            "fact_text": "ARR (recurring) is Rs. 5.8 Cr for Period Apr to Jun 2026 in board update sent 8 Jul 2026.",
            "entities_named": "Veloxa Technologies, Board", "date_as_written": "Sent 8 Jul 2026",
            "record_date": datetime.datetime(2026, 7, 8), "effective_date": datetime.datetime(2026, 6, 30), "confidence": "H"
        },
        {
            "ref": "E002", "source_file": "Board_Update_Apr-Jun_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Key numbers",
            "fact_text": "Customers count is 61; Team is 19 for Period Apr to Jun 2026 in board update sent 8 Jul 2026.",
            "entities_named": "Veloxa Technologies, Board", "date_as_written": "Sent 8 Jul 2026",
            "record_date": datetime.datetime(2026, 7, 8), "effective_date": datetime.datetime(2026, 6, 30), "confidence": "H"
        },
        {
            "ref": "E003", "source_file": "Board_Update_Apr-Jun_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Key numbers",
            "fact_text": "Monthly burn is Rs. 46 L; Runway is 14 months for Period Apr to Jun 2026 in board update sent 8 Jul 2026.",
            "entities_named": "Veloxa Technologies, Board", "date_as_written": "Sent 8 Jul 2026",
            "record_date": datetime.datetime(2026, 7, 8), "effective_date": datetime.datetime(2026, 6, 30), "confidence": "H"
        },
        {
            "ref": "E004", "source_file": "Board_Update_Apr-Jun_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Product",
            "fact_text": "Atlas (routing engine v3) is on track for GA on 15 September; real-time re-routing is headline feature.",
            "entities_named": "Atlas, routing engine v3", "date_as_written": "Sent 8 Jul 2026",
            "record_date": datetime.datetime(2026, 7, 8), "effective_date": datetime.datetime(2026, 9, 15), "confidence": "H"
        },
        {
            "ref": "E005", "source_file": "Board_Update_Apr-Jun_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Team",
            "fact_text": "Veloxa stated it will add two backend engineers this quarter to de-risk Atlas, with search underway.",
            "entities_named": "Engineering Team, Atlas", "date_as_written": "Sent 8 Jul 2026",
            "record_date": datetime.datetime(2026, 7, 8), "effective_date": datetime.datetime(2026, 6, 30), "confidence": "H"
        },
        # Board Update Jul-Sep 2026
        {
            "ref": "E006", "source_file": "Board_Update_Jul-Sep_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Key numbers",
            "fact_text": "ARR (recurring) is Rs. 6.1 Cr; Customers is 66; Team is 19 for Period Jul to Sep 2026 in board update sent 6 Oct 2026.",
            "entities_named": "Veloxa Technologies, Board", "date_as_written": "Sent 6 Oct 2026",
            "record_date": datetime.datetime(2026, 10, 6), "effective_date": datetime.datetime(2026, 9, 30), "confidence": "H"
        },
        {
            "ref": "E007", "source_file": "Board_Update_Jul-Sep_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Key numbers",
            "fact_text": "Monthly burn is Rs. 44 L; Runway is 13 months for Period Jul to Sep 2026 in board update sent 6 Oct 2026.",
            "entities_named": "Veloxa Technologies, Board", "date_as_written": "Sent 6 Oct 2026",
            "record_date": datetime.datetime(2026, 10, 6), "effective_date": datetime.datetime(2026, 9, 30), "confidence": "H"
        },
        {
            "ref": "E008", "source_file": "Board_Update_Jul-Sep_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Product",
            "fact_text": "Atlas is in final hardening; moved GA to absorb unplanned reliability work after a difficult August; engine itself is feature-complete.",
            "entities_named": "Atlas", "date_as_written": "Sent 6 Oct 2026",
            "record_date": datetime.datetime(2026, 10, 6), "effective_date": datetime.datetime(2026, 9, 30), "confidence": "H"
        },
        {
            "ref": "E009", "source_file": "Board_Update_Jul-Sep_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Team",
            "fact_text": "Hiring is paused while closing the round; one planned departure in marketing.",
            "entities_named": "Team", "date_as_written": "Sent 6 Oct 2026",
            "record_date": datetime.datetime(2026, 10, 6), "effective_date": datetime.datetime(2026, 9, 30), "confidence": "H"
        },
        {
            "ref": "E010", "source_file": "Board_Update_Jul-Sep_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Marketing",
            "fact_text": "The Logistics Summit drew 212 registrations, largest event yet.",
            "entities_named": "Logistics Summit", "date_as_written": "Sent 6 Oct 2026",
            "record_date": datetime.datetime(2026, 10, 6), "effective_date": datetime.datetime(2026, 9, 30), "confidence": "H"
        },
        # GL Export (Selected operational lines)
        {
            "ref": "E011", "source_file": "GL_Export_Apr-Sep_2026.xlsx", "sheet_or_page": "GL Apr-Sep", "row_or_line": "Rows 5, 9, 13, 18, 22, 30",
            "fact_text": "Salaries (payroll) payment is Rs. 31,75,000 on the 28th of each month from Apr to Sep 2026 (entered by FS).",
            "entities_named": "Salaries (payroll), FS", "date_as_written": "2026-04-28 to 2026-09-28",
            "record_date": datetime.datetime(2026, 9, 28), "effective_date": datetime.datetime(2026, 9, 28), "confidence": "H"
        },
        {
            "ref": "E012", "source_file": "GL_Export_Apr-Sep_2026.xlsx", "sheet_or_page": "GL Apr-Sep", "row_or_line": "Rows 6, 10, 14, 19, 24, 31",
            "fact_text": "WeWork India office rent is Rs. 2,36,000 at end of each month from Apr to Sep 2026 (entered by FS).",
            "entities_named": "WeWork India, FS", "date_as_written": "2026-04-30 to 2026-09-30",
            "record_date": datetime.datetime(2026, 9, 30), "effective_date": datetime.datetime(2026, 9, 30), "confidence": "H"
        },
        {
            "ref": "E013", "source_file": "GL_Export_Apr-Sep_2026.xlsx", "sheet_or_page": "GL Apr-Sep", "row_or_line": "Rows 4, 8, 12, 17, 21, 28",
            "fact_text": "Amazon Web Services cloud expense is entered monthly: Apr Rs. 1,81,200; May Rs. 1,90,450; Jun Rs. 2,05,900; Jul Rs. 2,12,480; Aug Rs. 2,19,830; Sep Rs. 2,48,310.",
            "entities_named": "Amazon Web Services, FS", "date_as_written": "2026-04-08 to 2026-09-08",
            "record_date": datetime.datetime(2026, 9, 8), "effective_date": datetime.datetime(2026, 9, 8), "confidence": "H"
        },
        {
            "ref": "E014", "source_file": "GL_Export_Apr-Sep_2026.xlsx", "sheet_or_page": "GL Apr-Sep", "row_or_line": "Row 15",
            "fact_text": "Cohere Recruiting Partners paid Rs. 1,77,000 on 2026-06-30 (JV-0688, Ref CRP-0412, Narration: Search fee, 2 backend roles (50% advance)).",
            "entities_named": "Cohere Recruiting Partners, FS", "date_as_written": "2026-06-30",
            "record_date": datetime.datetime(2026, 6, 30), "effective_date": datetime.datetime(2026, 6, 30), "confidence": "H"
        },
        {
            "ref": "E015", "source_file": "GL_Export_Apr-Sep_2026.xlsx", "sheet_or_page": "GL Apr-Sep", "row_or_line": "Row 25",
            "fact_text": "Patil Infra Services paid Rs. 70,800 on 2026-09-02 (JV-0902, Ref PIS-108, Narration: On-call support, 18-31 Aug).",
            "entities_named": "Patil Infra Services, FS", "date_as_written": "2026-09-02",
            "record_date": datetime.datetime(2026, 9, 2), "effective_date": datetime.datetime(2026, 8, 31), "confidence": "H"
        },
        {
            "ref": "E016", "source_file": "GL_Export_Apr-Sep_2026.xlsx", "sheet_or_page": "GL Apr-Sep", "row_or_line": "Rows 23, 26",
            "fact_text": "Summit payments: Sapphire Events Rs. 5,42,800 on 2026-08-29 (venue, AV); Saphire Event Mgmt Rs. 4,60,200 on 2026-09-03 (catering etc.). Total Rs. 10,03,000.",
            "entities_named": "Sapphire Events Pvt Ltd, Saphire Event Mgmt, FS", "date_as_written": "2026-08-29, 2026-09-03",
            "record_date": datetime.datetime(2026, 9, 3), "effective_date": datetime.datetime(2026, 9, 3), "confidence": "H"
        },
        # Emails
        {
            "ref": "E017", "source_file": "01.eml", "sheet_or_page": "Email", "row_or_line": "Headers & Body",
            "fact_text": "Karthik Subramanian ran Feb payroll using Jan sheet and added new joiner because Fatima is out.",
            "entities_named": "Karthik Subramanian, Meera Iyer, Fatima", "date_as_written": "Sat, 28 Feb 2026 20:15:00 +0530",
            "record_date": datetime.datetime(2026, 2, 28, 20, 15), "effective_date": datetime.datetime(2026, 2, 28), "confidence": "H"
        },
        {
            "ref": "E018", "source_file": "02.eml", "sheet_or_page": "Email", "row_or_line": "Headers & Body",
            "fact_text": "Rahul Verma inquired with Fatima Sheikh about first payslip amount looking higher than expected for a partial month.",
            "entities_named": "Rahul Verma, Fatima Sheikh", "date_as_written": "Fri, 06 Mar 2026 11:02:00 +0530",
            "record_date": datetime.datetime(2026, 3, 6, 11, 2), "effective_date": datetime.datetime(2026, 3, 6), "confidence": "H"
        },
        {
            "ref": "E019", "source_file": "03.eml", "sheet_or_page": "Email", "row_or_line": "Headers & Body",
            "fact_text": "Fatima Sheikh replied to Rahul Verma: 'Will check and get back.'",
            "entities_named": "Fatima Sheikh, Rahul Verma", "date_as_written": "Tue, 10 Mar 2026 15:40:00 +0530",
            "record_date": datetime.datetime(2026, 3, 10, 15, 40), "effective_date": datetime.datetime(2026, 3, 10), "confidence": "H"
        },
        # Employee Master
        {
            "ref": "E020", "source_file": "Employee_Master.xlsx", "sheet_or_page": "Employees", "row_or_line": "Row 1, Rows 4-22",
            "fact_text": "Keka HRMS export lists 19 employees as of 31-Oct-2026; row 1 notes contractors are not in Keka.",
            "entities_named": "Keka HRMS, Veloxa", "date_as_written": "Exported 31-Oct-2026",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 10, 31), "confidence": "H"
        },
        {
            "ref": "E021", "source_file": "Employee_Master.xlsx", "sheet_or_page": "Employees", "row_or_line": "Row 16",
            "fact_text": "Siddharth Mehta (Product Marketing Manager) Status: Notice period, Exit Date: 2026-10-31.",
            "entities_named": "Siddharth Mehta", "date_as_written": "2026-10-31",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 10, 31), "confidence": "H"
        },
        {
            "ref": "E022", "source_file": "Employee_Master.xlsx", "sheet_or_page": "Employees", "row_or_line": "Row 21",
            "fact_text": "Rahul Verma (Backend Engineer) Join Date: 2026-02-03, Manager: VX004 Vikram Menon, Status: Active.",
            "entities_named": "Rahul Verma, Vikram Menon", "date_as_written": "2026-02-03",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 2, 3), "confidence": "H"
        },
        # Payroll Register (Confidential figures)
        {
            "ref": "E023", "source_file": "Payroll_Register_Jan-Mar_2026.xlsx", "sheet_or_page": "Payroll Q4", "row_or_line": "Row 39",
            "fact_text": "Rahul Verma Feb-2026 payroll record lists Days in Month: 28, Days Payable: 28, Gross (Rs.): 110000, Processed By: KS.",
            "entities_named": "Rahul Verma, KS", "date_as_written": "Feb-2026",
            "record_date": datetime.datetime(2026, 2, 28), "effective_date": datetime.datetime(2026, 2, 28), "confidence": "H", "is_confidential": True
        },
        {
            "ref": "E024", "source_file": "Payroll_Register_Jan-Mar_2026.xlsx", "sheet_or_page": "Payroll Q4", "row_or_line": "Row 58",
            "fact_text": "Rahul Verma Mar-2026 payroll record lists Days in Month: 31, Days Payable: 31, Gross (Rs.): 110000, Processed By: FS.",
            "entities_named": "Rahul Verma, FS", "date_as_written": "Mar-2026",
            "record_date": datetime.datetime(2026, 3, 31), "effective_date": datetime.datetime(2026, 3, 31), "confidence": "H", "is_confidential": True
        },
        # Transcripts
        {
            "ref": "E025", "source_file": "T1_CEO_Kickoff_Call.docx", "sheet_or_page": "Transcript", "row_or_line": "Summary",
            "fact_text": "CEO Ananya says ARR is 'around forty-two crore, maybe forty-five now' and company is roughly eighteen people ('one-eighty, give or take').",
            "entities_named": "Ananya R.", "date_as_written": "Kickoff Call",
            "record_date": datetime.datetime(2026, 11, 1), "effective_date": datetime.datetime(2026, 11, 1), "confidence": "M"
        },
        {
            "ref": "E026", "source_file": "T1_CEO_Kickoff_Call.docx", "sheet_or_page": "Transcript", "row_or_line": "Key points",
            "fact_text": "CEO Ananya mentions burn is 'around two point two' (unit not stated) and routing engine version three promised by festive season might not make it.",
            "entities_named": "Ananya R.", "date_as_written": "Kickoff Call",
            "record_date": datetime.datetime(2026, 11, 1), "effective_date": datetime.datetime(2026, 11, 1), "confidence": "M"
        },
        {
            "ref": "E027", "source_file": "T2_CFO_Call.docx", "sheet_or_page": "Transcript", "row_or_line": "Summary & Key points",
            "fact_text": "CFO Meera says ARR at start of year was 'forty-eight'; burn has been 'two point two lakhs a month, sometimes two point five'; and mandates individual salaries must never show up in anything Ananya sees, only totals.",
            "entities_named": "Meera I., Ananya R.", "date_as_written": "CFO Call",
            "record_date": datetime.datetime(2026, 11, 2), "effective_date": datetime.datetime(2026, 11, 2), "confidence": "M"
        },
    ]

    for item in evidence_items:
        existing = db.query(Evidence).filter(Evidence.ref == item["ref"]).first()
        if not existing:
            e = Evidence(
                ref=item["ref"],
                source_id=source_map[item["source_file"]],
                sheet_or_page=item.get("sheet_or_page"),
                row_or_line=item.get("row_or_line"),
                fact_text=item["fact_text"],
                entities_named=item.get("entities_named"),
                date_as_written=item.get("date_as_written"),
                record_date=item.get("record_date"),
                effective_date=item.get("effective_date"),
                date_normalized=item.get("effective_date"),  # For filtering
                confidence=item.get("confidence", "H"),
                is_confidential=item.get("is_confidential", False),
                released_at=DAY1_RELEASE_TIME
            )
            db.add(e)

def ingest_day1_conflicts(db: Session):
    conflicts_data = [
        {
            "conflict_id": "CONF-001",
            "topic": "Annual Recurring Revenue (ARR) Discrepancy",
            "description": "Board updates report recurring ARR of Rs. 5.8 Cr (Q1 Apr-Jun 2026) and Rs. 6.1 Cr (Q2 Jul-Sep 2026). In T1, CEO Ananya states ARR is 'around forty-two crore, maybe forty-five now'. In T2, CFO Meera states ARR at start of year was 'forty-eight'.",
            "competing_sources": "Board_Update_Apr-Jun_2026.pdf (E001), Board_Update_Jul-Sep_2026.pdf (E006) VS T1_CEO_Kickoff_Call.docx (E025), T2_CFO_Call.docx (E027)",
            "proposed_interpretation": "Use Rs. 6.1 Cr as the latest board-reported recurring ARR. Keep the CEO's Rs. 42-45 Cr and CFO's Rs. 48 Cr statements as unresolved conflicting claims. Do not assert that they represent GMV, valuation, or pipeline without evidence. Do not describe the board report as audited.",
            "confidence": "M",
            "what_would_change": "Direct reconciliations from audited financial statements, billing registers, or formal clarification from Meera and Ananya.",
            "impact_level": "HIGH",
            "human_status": "UNRESOLVED",
        },
        {
            "conflict_id": "CONF-002",
            "topic": "Monthly Burn Rate Discrepancy",
            "description": "Board updates report monthly burn of Rs. 46 L (Q1) and Rs. 44 L (Q2). Zoho Books records monthly payroll alone at Rs. 31,75,000, office rent at Rs. 2,36,000, and AWS cloud at Rs. 1.8-2.5 L. In T2, CFO Meera states burn has been 'two point two lakhs a month, sometimes two point five'. In T1, CEO Ananya states burn is 'around two point two'.",
            "competing_sources": "Board_Update_Apr-Jun_2026.pdf (E003), Board_Update_Jul-Sep_2026.pdf (E007), GL_Export_Apr-Sep_2026.xlsx (E011-E013) VS T2_CFO_Call.docx (E027), T1_CEO_Kickoff_Call.docx (E026)",
            "proposed_interpretation": "Use Rs. 44 lakh as the latest board-reported monthly burn, without labeling it gross or net unless a source explicitly defines it. Do not infer net cash burn from ARR or assume ARR is cash received. Keep the CFO's Rs. 2.2-2.5 lakh transcript statement unresolved.",
            "confidence": "M",
            "what_would_change": "Monthly bank statements, cash-flow ledger definitions, or signed finance committee notes.",
            "impact_level": "HIGH",
            "human_status": "UNRESOLVED",
        },
        {
            "conflict_id": "CONF-003",
            "topic": "Headcount & Company Scope Discrepancy",
            "description": "Board updates report team size of 19 in Q1 and Q2. Keka HRMS export lists exactly 19 employees as of 31-Oct-2026 (contractors are not in Keka). In T1, CEO Ananya states company is 'roughly eighteen people (one-eighty, give or take)'. The candidate brief describes a 180-person company.",
            "competing_sources": "Employee_Master.xlsx (E020), Board_Update_Apr-Jun_2026.pdf (E002), Board_Update_Jul-Sep_2026.pdf (E006) VS T1_CEO_Kickoff_Call.docx (E025), Candidate Brief",
            "proposed_interpretation": "Use 19 as the board-reported and Keka-recorded employee count. Keep the candidate brief's 180-person company description and ambiguous CEO transcript as unresolved scope differences. Do not invent contractors or assume the CEO meant 18 active employees.",
            "confidence": "M",
            "what_would_change": "Company-wide master service contracts, Culture Amp pulse headcount roster, or organizational audit.",
            "impact_level": "HIGH",
            "human_status": "UNRESOLVED",
        },
        {
            "conflict_id": "CONF-004",
            "topic": "Suspected February Payroll Discrepancy Requiring Verification",
            "description": "Rahul Verma joined 2026-02-03 (26 of 28 payable days in February). Feb payroll register records Days Payable: 28 and Gross: Rs. 1,10,000 processed by Karthik Subramanian while Fatima was away for her wedding (01.eml). Rahul queried this in 02.eml, and Fatima acknowledged in 03.eml ('Will check and get back'). March payroll records list 31 payable days with Gross: Rs. 1,10,000 and zero deduction. The evidence establishes a potential partial-month payment issue and employee query, not a conclusively confirmed payroll defect, requiring further verification in official Keka reconciliation records.",
            "competing_sources": "01.eml (E017), 02.eml (E018), 03.eml (E019), Payroll_Register_Jan-Mar_2026.xlsx (E023, E024), Employee_Master.xlsx (E022)",
            "proposed_interpretation": "Reclassified as a suspected February payroll discrepancy requiring verification. The available evidence establishes a potential partial-month payment issue and an employee query, but does not conclusively prove a finalized defect. Further verification from formal Keka payroll reconciliation records is required. Individual compensation figures remain strictly confidential.",
            "confidence": "M",
            "what_would_change": "Formal Keka payroll module migration audit, reconciliation vouchers, or year-end Form 16 / tax filings.",
            "impact_level": "MEDIUM",
            "human_status": "UNRESOLVED",
        }
    ]

    for c in conflicts_data:
        existing = db.query(Conflict).filter(Conflict.conflict_id == c["conflict_id"]).first()
        if not existing:
            con = Conflict(
                conflict_id=c["conflict_id"],
                topic=c["topic"],
                description=c["description"],
                competing_sources=c["competing_sources"],
                proposed_interpretation=c["proposed_interpretation"],
                confidence=c["confidence"],
                what_would_change=c["what_would_change"],
                impact_level=c["impact_level"],
                human_status=c["human_status"]
            )
            db.add(con)
        else:
            existing.topic = c["topic"]
            existing.description = c["description"]
            existing.competing_sources = c["competing_sources"]
            existing.proposed_interpretation = c["proposed_interpretation"]
            existing.confidence = c["confidence"]
            existing.what_would_change = c["what_would_change"]
            existing.impact_level = c["impact_level"]
            existing.human_status = c["human_status"]

def seed_day1_data(db: Session):
    source_map = ingest_day1_sources(db)
    ingest_day1_people(db)
    ingest_day1_evidence(db, source_map)
    ingest_day1_conflicts(db)
    db.commit()
