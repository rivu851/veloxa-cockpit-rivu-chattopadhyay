"""
Deterministic Day 1 Ingestion Engine.
Loads structured seed data extracted from Day 1 text room with exact row/column references.
Ensures idempotency across multiple runs and supports incremental future release ingestion.
"""
import os
import json
import re
import datetime
from sqlalchemy.orm import Session
from backend.app.models.schema import (
    Source, Evidence, Claim, Person, Conflict, Assumption, AgentMemory,
    GitCommit, JiraIssue, JiraEpic, JiraVersion, Incident, OnCallEntry,
    LaunchKitAsset, OrgReportingLine
)

DAY1_RELEASE_TIME = datetime.datetime(2026, 11, 16, 10, 0, 0)
DAY2_RELEASE_TIME = datetime.datetime(2026, 11, 17, 10, 0, 0)
DAY3_RELEASE_TIME = datetime.datetime(2026, 11, 18, 10, 0, 0)
DAY4_RELEASE_TIME = datetime.datetime(2026, 11, 19, 10, 0, 0)

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
        {"emp_id": "VX001", "full_name": "Ananya Rao", "work_email": "ananya@veloxa.in", "department": "Leadership", "title": "CEO", "manager_id": None, "join_date": "2019-04-01", "location": "Bengaluru", "status": "Active", "is_interviewable": True, "system_role_desc": "Chief Executive Officer. Strategic growth, board governance, and capital fundraising."},
        {"emp_id": "VX002", "full_name": "Manoj Kumar", "work_email": "manoj@veloxa.in", "department": "Sales", "title": "Sales Lead", "manager_id": "VX001", "join_date": "2020-01-06", "location": "Bengaluru", "status": "Active", "is_interviewable": True, "system_role_desc": "Enterprise sales lead managing B2B logistics pipeline and customer expansions."},
        {"emp_id": "VX003", "full_name": "Meera Iyer", "work_email": "meera@veloxa.in", "department": "Finance", "title": "CFO", "manager_id": "VX001", "join_date": "2023-06-12", "location": "Bengaluru", "status": "Active", "is_interviewable": True, "system_role_desc": "Chief Financial Officer. Cash management, Zoho Books, Keka payroll, and board financial reporting."},
        {"emp_id": "VX004", "full_name": "Vikram Menon", "work_email": "vikram@veloxa.in", "department": "Engineering", "title": "VP Engineering", "manager_id": "VX001", "join_date": "2021-02-01", "location": "Bengaluru", "status": "Active", "is_interviewable": True, "system_role_desc": "VP Engineering overseeing Atlas routing engine development and architecture."},
        {"emp_id": "VX005", "full_name": "Deepa Joshi", "work_email": "deepa@veloxa.in", "department": "People & Ops", "title": "Head of People & Ops", "manager_id": "VX001", "join_date": "2022-07-04", "location": "Bengaluru", "status": "Active", "is_interviewable": True, "system_role_desc": "Head of People & Ops managing HR policies, organizational culture, and workplace operations."},
        {"emp_id": "VX006", "full_name": "Nikhil Bose", "work_email": "nikhil@veloxa.in", "department": "Marketing", "title": "Head of Marketing", "manager_id": "VX001", "join_date": "2024-09-02", "location": "Bengaluru", "status": "Active", "is_interviewable": True, "system_role_desc": "Head of Marketing overseeing brand, demand generation, and the September Logistics Summit."},
        {"emp_id": "VX007", "full_name": "Priya Nair", "work_email": "priya.n@veloxa.in", "department": "Engineering", "title": "Staff Engineer", "manager_id": "VX004", "join_date": "2022-03-14", "location": "Bengaluru", "status": "Active", "is_interviewable": True, "system_role_desc": "Staff Engineer and core technical architect of the Atlas routing engine algorithms."},
        {"emp_id": "VX008", "full_name": "Divya Reddy", "work_email": "divya@veloxa.in", "department": "Sales", "title": "Account Executive", "manager_id": "VX002", "join_date": "2024-01-15", "location": "Hyderabad", "status": "Active", "is_interviewable": True, "system_role_desc": "Account Executive handling mid-market enterprise accounts and customer onboarding."},
        {"emp_id": "VX009", "full_name": "Arjun Das", "work_email": "arjun@veloxa.in", "department": "Engineering", "title": "Senior Frontend Engineer", "manager_id": "VX004", "join_date": "2023-05-08", "location": "Pune (remote)", "status": "Active", "is_interviewable": True, "system_role_desc": "Senior Frontend Engineer developing web consoles and telemetry dashboards for Atlas."},
        {"emp_id": "VX010", "full_name": "Karthik Subramanian", "work_email": "karthik.s@veloxa.in", "department": "Finance", "title": "FP&A Manager", "manager_id": "VX003", "join_date": "2024-10-01", "location": "Bengaluru", "status": "Active", "is_interviewable": True, "system_role_desc": "FP&A Manager handling financial modeling, runway tracking, and payroll disbursements."},
        {"emp_id": "VX011", "full_name": "Aisha Khan", "work_email": "aisha@veloxa.in", "department": "Marketing", "title": "Performance Marketing Manager", "manager_id": "VX006", "join_date": "2023-08-21", "location": "Bengaluru", "status": "Active", "is_interviewable": True, "system_role_desc": "Performance Marketing Manager managing digital campaigns and event registrations."},
        {"emp_id": "VX012", "full_name": "Sneha Kulkarni", "work_email": "sneha.k@veloxa.in", "department": "Engineering", "title": "Site Reliability Engineer", "manager_id": "VX004", "join_date": "2024-11-04", "location": "Bengaluru", "status": "Active", "is_interviewable": True, "system_role_desc": "Site Reliability Engineer managing AWS cloud infrastructure, incident response, and uptime."},
        {"emp_id": "VX013", "full_name": "Siddharth Mehta", "work_email": "sid@veloxa.in", "department": "Marketing", "title": "Product Marketing Manager", "manager_id": "VX006", "join_date": "2025-04-07", "location": "Bengaluru", "status": "Notice period", "exit_date": "2026-10-31", "is_interviewable": False, "system_role_desc": "Product Marketing Manager on notice period (exit date 31 Oct 2026); excluded from executive interview cohort."},
        {"emp_id": "VX014", "full_name": "Fatima Sheikh", "work_email": "fatima@veloxa.in", "department": "Finance", "title": "Accounts & Payroll Executive", "manager_id": "VX003", "join_date": "2025-05-12", "location": "Bengaluru", "status": "Active", "is_interviewable": True, "system_role_desc": "Accounts & Payroll Executive managing monthly payroll registers and employee inquiries."},
        {"emp_id": "VX015", "full_name": "Rohan Banerjee", "work_email": "rohan@veloxa.in", "department": "People & Ops", "title": "Talent Partner", "manager_id": "VX005", "join_date": "2024-06-03", "location": "Kolkata (remote)", "status": "Active", "is_interviewable": False, "system_role_desc": "Talent Partner; recruitment activities paused under Q2 hiring freeze, excluded from active interview cohort."},
        {"emp_id": "VX016", "full_name": "Imran Siddiqui", "work_email": "imran@veloxa.in", "department": "Support", "title": "Customer Support Lead", "manager_id": "VX001", "join_date": "2023-02-13", "location": "Bengaluru", "status": "Active", "is_interviewable": False, "system_role_desc": "Support operations lead; excluded from executive strategic query cohort."},
        {"emp_id": "VX017", "full_name": "Lakshmi Pillai", "work_email": "lakshmi.p@veloxa.in", "department": "People & Ops", "title": "HR & Office Executive", "manager_id": "VX005", "join_date": "2025-10-06", "location": "Bengaluru", "status": "Active", "is_interviewable": False, "system_role_desc": "Office administrative operations executive; excluded from interview cohort."},
        {"emp_id": "VX018", "full_name": "Rahul Verma", "work_email": "rahul.v@veloxa.in", "department": "Engineering", "title": "Backend Engineer", "manager_id": "VX004", "join_date": "2026-02-03", "location": "Bengaluru", "status": "Active", "is_interviewable": True, "system_role_desc": "Backend Engineer on Atlas core data pipelines; raised February joiner payslip inquiry."},
        {"emp_id": "VX019", "full_name": "Kavya Narayan", "work_email": "kavya@veloxa.in", "department": "Support", "title": "Support Associate", "manager_id": "VX016", "join_date": "2025-07-01", "location": "Bengaluru", "status": "Active", "is_interviewable": False, "system_role_desc": "Support Associate handling client tickets; excluded from interview cohort."},
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
                is_interviewable=emp.get("is_interviewable", True),
                system_role_desc=emp.get("system_role_desc"),
                released_at=DAY1_RELEASE_TIME
            )
            db.add(p)
        else:
            existing.is_interviewable = emp.get("is_interviewable", True)
            existing.system_role_desc = emp.get("system_role_desc")

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

def ingest_day1_claims(db: Session, source_map: dict):
    claims_data = [
        {
            "claim_id": "CLM-001", "speaker_or_author": "Board of Directors / Finance", "source_file": "Board_Update_Apr-Jun_2026.pdf",
            "claim_category": "ARR", "claim_text": "ARR (recurring) is Rs. 5.8 Cr for Period Apr to Jun 2026 across 61 customers.",
            "date_asserted": "Sent 8 Jul 2026", "record_date": datetime.datetime(2026, 7, 8), "effective_date": datetime.datetime(2026, 6, 30),
            "is_disputed": True, "competing_evidence_refs": "E025,E027", "evidence_ref": "E001", "confidence": "H", "conflict_id": "CONF-001"
        },
        {
            "claim_id": "CLM-002", "speaker_or_author": "Board of Directors / Finance", "source_file": "Board_Update_Jul-Sep_2026.pdf",
            "claim_category": "ARR", "claim_text": "ARR (recurring) is Rs. 6.1 Cr for Period Jul to Sep 2026 across 66 customers.",
            "date_asserted": "Sent 6 Oct 2026", "record_date": datetime.datetime(2026, 10, 6), "effective_date": datetime.datetime(2026, 9, 30),
            "is_disputed": True, "competing_evidence_refs": "E025,E027", "evidence_ref": "E006", "confidence": "H", "conflict_id": "CONF-001"
        },
        {
            "claim_id": "CLM-003", "speaker_or_author": "Ananya Rao (CEO)", "source_file": "T1_CEO_Kickoff_Call.docx",
            "claim_category": "ARR", "claim_text": "ARR is around forty-two crore, maybe forty-five now.",
            "date_asserted": "Kickoff Call (T1)", "record_date": datetime.datetime(2026, 11, 1), "effective_date": datetime.datetime(2026, 11, 1),
            "is_disputed": True, "competing_evidence_refs": "E001,E006", "evidence_ref": "E025", "confidence": "M", "conflict_id": "CONF-001"
        },
        {
            "claim_id": "CLM-004", "speaker_or_author": "Meera Iyer (CFO)", "source_file": "T2_CFO_Call.docx",
            "claim_category": "ARR", "claim_text": "ARR at start of the year was forty-eight.",
            "date_asserted": "CFO Call (T2)", "record_date": datetime.datetime(2026, 11, 2), "effective_date": datetime.datetime(2026, 11, 2),
            "is_disputed": True, "competing_evidence_refs": "E001,E006", "evidence_ref": "E027", "confidence": "M", "conflict_id": "CONF-001"
        },
        {
            "claim_id": "CLM-005", "speaker_or_author": "Board of Directors / Finance", "source_file": "Board_Update_Apr-Jun_2026.pdf",
            "claim_category": "Burn", "claim_text": "Monthly burn is Rs. 46 L; Runway is 14 months for Period Apr to Jun 2026.",
            "date_asserted": "Sent 8 Jul 2026", "record_date": datetime.datetime(2026, 7, 8), "effective_date": datetime.datetime(2026, 6, 30),
            "is_disputed": True, "competing_evidence_refs": "E026,E027", "evidence_ref": "E003", "confidence": "H", "conflict_id": "CONF-002"
        },
        {
            "claim_id": "CLM-006", "speaker_or_author": "Board of Directors / Finance", "source_file": "Board_Update_Jul-Sep_2026.pdf",
            "claim_category": "Burn", "claim_text": "Monthly burn is Rs. 44 L; Runway is 13 months for Period Jul to Sep 2026.",
            "date_asserted": "Sent 6 Oct 2026", "record_date": datetime.datetime(2026, 10, 6), "effective_date": datetime.datetime(2026, 9, 30),
            "is_disputed": True, "competing_evidence_refs": "E026,E027", "evidence_ref": "E007", "confidence": "H", "conflict_id": "CONF-002"
        },
        {
            "claim_id": "CLM-007", "speaker_or_author": "Ananya Rao (CEO)", "source_file": "T1_CEO_Kickoff_Call.docx",
            "claim_category": "Burn", "claim_text": "Burn is around two point two (unit not stated).",
            "date_asserted": "Kickoff Call (T1)", "record_date": datetime.datetime(2026, 11, 1), "effective_date": datetime.datetime(2026, 11, 1),
            "is_disputed": True, "competing_evidence_refs": "E003,E007,E011,E012,E013", "evidence_ref": "E026", "confidence": "M", "conflict_id": "CONF-002"
        },
        {
            "claim_id": "CLM-008", "speaker_or_author": "Meera Iyer (CFO)", "source_file": "T2_CFO_Call.docx",
            "claim_category": "Burn", "claim_text": "Burn has been two point two lakhs a month, sometimes two point five.",
            "date_asserted": "CFO Call (T2)", "record_date": datetime.datetime(2026, 11, 2), "effective_date": datetime.datetime(2026, 11, 2),
            "is_disputed": True, "competing_evidence_refs": "E003,E007,E011,E012,E013", "evidence_ref": "E027", "confidence": "M", "conflict_id": "CONF-002"
        },
        {
            "claim_id": "CLM-009", "speaker_or_author": "Keka HRMS System", "source_file": "Employee_Master.xlsx",
            "claim_category": "Headcount", "claim_text": "Company headcount is 19 employees (18 Active, 1 Notice period; contractors excluded).",
            "date_asserted": "Exported 31-Oct-2026", "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 10, 31),
            "is_disputed": True, "competing_evidence_refs": "E025", "evidence_ref": "E020", "confidence": "H", "conflict_id": "CONF-003"
        },
        {
            "claim_id": "CLM-010", "speaker_or_author": "Board of Directors / HR", "source_file": "Board_Update_Jul-Sep_2026.pdf",
            "claim_category": "Headcount", "claim_text": "Team count is 19 as of Q2 board update.",
            "date_asserted": "Sent 6 Oct 2026", "record_date": datetime.datetime(2026, 10, 6), "effective_date": datetime.datetime(2026, 9, 30),
            "is_disputed": True, "competing_evidence_refs": "E025", "evidence_ref": "E006", "confidence": "H", "conflict_id": "CONF-003"
        },
        {
            "claim_id": "CLM-011", "speaker_or_author": "Ananya Rao (CEO)", "source_file": "T1_CEO_Kickoff_Call.docx",
            "claim_category": "Headcount", "claim_text": "Company is roughly eighteen people ('one-eighty, give or take').",
            "date_asserted": "Kickoff Call (T1)", "record_date": datetime.datetime(2026, 11, 1), "effective_date": datetime.datetime(2026, 11, 1),
            "is_disputed": True, "competing_evidence_refs": "E020,E006", "evidence_ref": "E025", "confidence": "M", "conflict_id": "CONF-003"
        },
        {
            "claim_id": "CLM-012", "speaker_or_author": "VP Engineering / Board Update", "source_file": "Board_Update_Apr-Jun_2026.pdf",
            "claim_category": "Engineering", "claim_text": "Atlas (routing engine v3) is on track for GA on 15 September 2026.",
            "date_asserted": "Sent 8 Jul 2026", "record_date": datetime.datetime(2026, 7, 8), "effective_date": datetime.datetime(2026, 6, 30),
            "is_disputed": True, "competing_evidence_refs": "E008,E015,E026", "evidence_ref": "E004", "confidence": "H", "conflict_id": None
        },
        {
            "claim_id": "CLM-013", "speaker_or_author": "VP Engineering / Board Update", "source_file": "Board_Update_Jul-Sep_2026.pdf",
            "claim_category": "Engineering", "claim_text": "Atlas v3 GA was moved to absorb unplanned reliability work after a difficult August; the engine itself is feature-complete.",
            "date_asserted": "Sent 6 Oct 2026", "record_date": datetime.datetime(2026, 10, 6), "effective_date": datetime.datetime(2026, 9, 30),
            "is_disputed": False, "competing_evidence_refs": None, "evidence_ref": "E008", "confidence": "H", "conflict_id": None
        },
        {
            "claim_id": "CLM-014", "speaker_or_author": "Ananya Rao (CEO)", "source_file": "T1_CEO_Kickoff_Call.docx",
            "claim_category": "Engineering", "claim_text": "Atlas routing engine version 3 promised by festive season might not make it.",
            "date_asserted": "Kickoff Call (T1)", "record_date": datetime.datetime(2026, 11, 1), "effective_date": datetime.datetime(2026, 11, 1),
            "is_disputed": False, "competing_evidence_refs": None, "evidence_ref": "E026", "confidence": "M", "conflict_id": None
        },
        {
            "claim_id": "CLM-015", "speaker_or_author": "Rahul Verma / Fatima Sheikh", "source_file": "02.eml",
            "claim_category": "Payroll", "claim_text": "Rahul Verma queried full 28-day pay for joining Feb 3; suspected partial-month calculation discrepancy requiring formal verification.",
            "date_asserted": "6-10 Mar 2026", "record_date": datetime.datetime(2026, 3, 10), "effective_date": datetime.datetime(2026, 2, 28),
            "is_disputed": True, "competing_evidence_refs": "E017,E023,E024", "evidence_ref": "E018", "confidence": "M", "conflict_id": "CONF-004"
        },
        {
            "claim_id": "CLM-016", "speaker_or_author": "Head of Marketing", "source_file": "GL_Export_Apr-Sep_2026.xlsx",
            "claim_category": "Marketing", "claim_text": "Logistics Summit 2026 total spend was Rs. 10,03,000 across venue and production for 212 registrations.",
            "date_asserted": "2026-09-24", "record_date": datetime.datetime(2026, 9, 24), "effective_date": datetime.datetime(2026, 9, 24),
            "is_disputed": False, "competing_evidence_refs": None, "evidence_ref": "E016", "confidence": "H", "conflict_id": None
        },
        {
            "claim_id": "CLM-017", "speaker_or_author": "Executive Team / Board", "source_file": "Board_Update_Jul-Sep_2026.pdf",
            "claim_category": "Operations", "claim_text": "Hiring is currently paused company-wide while closing the round.",
            "date_asserted": "Sent 6 Oct 2026", "record_date": datetime.datetime(2026, 10, 6), "effective_date": datetime.datetime(2026, 9, 30),
            "is_disputed": False, "competing_evidence_refs": None, "evidence_ref": "E009", "confidence": "H", "conflict_id": None
        },
        {
            "claim_id": "CLM-018", "speaker_or_author": "Finance / Engineering", "source_file": "GL_Export_Apr-Sep_2026.xlsx",
            "claim_category": "Engineering", "claim_text": "Patil Infra Services was paid Rs. 70,800 on 2026-09-02 for emergency on-call support during 18-31 August.",
            "date_asserted": "2026-09-02", "record_date": datetime.datetime(2026, 9, 2), "effective_date": datetime.datetime(2026, 8, 31),
            "is_disputed": False, "competing_evidence_refs": None, "evidence_ref": "E015", "confidence": "H", "conflict_id": None
        },
        {
            "claim_id": "CLM-019", "speaker_or_author": "Finance / People", "source_file": "GL_Export_Apr-Sep_2026.xlsx",
            "claim_category": "Operations", "claim_text": "Cohere Recruiting Partners was paid Rs. 1,77,000 advance on 2026-06-30 for 2 backend engineers to de-risk Atlas.",
            "date_asserted": "2026-06-30", "record_date": datetime.datetime(2026, 6, 30), "effective_date": datetime.datetime(2026, 6, 30),
            "is_disputed": False, "competing_evidence_refs": None, "evidence_ref": "E014", "confidence": "H", "conflict_id": None
        },
        {
            "claim_id": "CLM-020", "speaker_or_author": "Finance / Zoho Books", "source_file": "GL_Export_Apr-Sep_2026.xlsx",
            "claim_category": "Burn", "claim_text": "Monthly salaries payroll disbursement is entered at Rs. 31,75,000 on the 28th of each month from Apr to Sep 2026.",
            "date_asserted": "Monthly (28th)", "record_date": datetime.datetime(2026, 9, 28), "effective_date": datetime.datetime(2026, 9, 28),
            "is_disputed": False, "competing_evidence_refs": None, "evidence_ref": "E011", "confidence": "H", "conflict_id": None
        },
        {
            "claim_id": "CLM-021", "speaker_or_author": "Finance / Zoho Books", "source_file": "GL_Export_Apr-Sep_2026.xlsx",
            "claim_category": "Burn", "claim_text": "Office rent to WeWork India is Rs. 2,36,000 disbursed monthly from Apr to Sep 2026.",
            "date_asserted": "Monthly", "record_date": datetime.datetime(2026, 9, 5), "effective_date": datetime.datetime(2026, 9, 5),
            "is_disputed": False, "competing_evidence_refs": None, "evidence_ref": "E012", "confidence": "H", "conflict_id": None
        },
        {
            "claim_id": "CLM-022", "speaker_or_author": "Finance / Zoho Books", "source_file": "GL_Export_Apr-Sep_2026.xlsx",
            "claim_category": "Burn", "claim_text": "AWS cloud hosting expenses range from Rs. 1,81,200 to Rs. 2,48,310 monthly across Apr to Sep 2026.",
            "date_asserted": "Monthly", "record_date": datetime.datetime(2026, 9, 7), "effective_date": datetime.datetime(2026, 9, 7),
            "is_disputed": False, "competing_evidence_refs": None, "evidence_ref": "E013", "confidence": "H", "conflict_id": None
        }
    ]
    for c in claims_data:
        s_id = source_map.get(c["source_file"])
        if not s_id:
            s_obj = db.query(Source).filter(Source.file_name == c["source_file"]).first()
            s_id = s_obj.id if s_obj else 1

        existing = db.query(Claim).filter(Claim.claim_id == c["claim_id"]).first()
        if not existing:
            cl = Claim(
                claim_id=c["claim_id"],
                speaker_or_author=c["speaker_or_author"],
                source_id=s_id,
                claim_text=c["claim_text"],
                claim_category=c["claim_category"],
                date_asserted=c.get("date_asserted"),
                record_date=c.get("record_date"),
                effective_date=c.get("effective_date"),
                is_disputed=c.get("is_disputed", False),
                competing_evidence_refs=c.get("competing_evidence_refs"),
                evidence_ref=c.get("evidence_ref"),
                confidence=c.get("confidence", "M"),
                conflict_id=c.get("conflict_id"),
                released_at=DAY1_RELEASE_TIME
            )
            db.add(cl)
        else:
            existing.speaker_or_author = c["speaker_or_author"]
            existing.claim_text = c["claim_text"]
            existing.claim_category = c["claim_category"]
            existing.is_disputed = c.get("is_disputed", False)
            existing.competing_evidence_refs = c.get("competing_evidence_refs")
            existing.evidence_ref = c.get("evidence_ref")
            existing.confidence = c.get("confidence", "M")
            existing.conflict_id = c.get("conflict_id")

def ingest_day1_assumptions(db: Session):
    assumptions_data = [
        {
            "assumption_id": "ASM-001",
            "domain": "ARR",
            "statement": "Board-reported recurring ARR of Rs. 6.1 Cr reflects operational subscription run-rate; verbal executive statements of 42-45 Cr are uncorroborated conflicting claims.",
            "rationale": "Board updates provide concrete customer counts (66) and comparative growth without statutory audit notation.",
            "risk_if_wrong": "If verbal figures represent booked GMV or contract values, financial scale is understated."
        },
        {
            "assumption_id": "ASM-002",
            "domain": "Burn",
            "statement": "Board-reported monthly burn of Rs. 44 L reflects total operational cash outflow without distinguishing gross vs net in absence of ledger receipts.",
            "rationale": "Primary source does not define gross vs net; ledger disbursements confirm salary alone is 31.75 L.",
            "risk_if_wrong": "If 44 L is gross and net is lower, runway projection is compressed."
        },
        {
            "assumption_id": "ASM-003",
            "domain": "Headcount",
            "statement": "Keka HRMS export of 19 employees represents full-time workforce; contractors are unrecorded in HRMS.",
            "rationale": "Keka export header explicitly notes contractors are not in Keka.",
            "risk_if_wrong": "If contractor pool is large, operational burn and true organization size are underestimated."
        },
        {
            "assumption_id": "ASM-004",
            "domain": "Payroll",
            "statement": "Rahul Verma February pay is a suspected partial-month calculation discrepancy requiring formal verification.",
            "rationale": "Rahul queried 26/28 days in 02.eml, acknowledged in 03.eml, but March had no adjustment.",
            "risk_if_wrong": "If formal reconciliation was handled off-register or via tax vouchers, discrepancy is non-existent."
        },
        {
            "assumption_id": "ASM-005",
            "domain": "Engineering",
            "statement": "Atlas v3 is feature-complete but requires production reliability hardening before GA.",
            "rationale": "Q2 Board update confirms GA shifted for unplanned reliability work after August incidents.",
            "risk_if_wrong": "If fundamental routing architecture is unstable, GA timeline may slip into 2027."
        }
    ]
    for a in assumptions_data:
        existing = db.query(Assumption).filter(Assumption.assumption_id == a["assumption_id"]).first()
        if not existing:
            ass = Assumption(
                assumption_id=a["assumption_id"],
                domain=a["domain"],
                statement=a["statement"],
                rationale=a["rationale"],
                risk_if_wrong=a["risk_if_wrong"]
            )
            db.add(ass)
        else:
            existing.statement = a["statement"]
            existing.rationale = a["rationale"]
            existing.risk_if_wrong = a["risk_if_wrong"]

def ingest_day1_memories(db: Session):
    memories_data = [
        # VX001 Ananya Rao (CEO)
        {"emp_id": "VX001", "memory_type": "grounded_fact", "content": "CEO of Veloxa Technologies since April 2019. Leading company through current capital fundraise round.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX001", "memory_type": "role_context", "content": "Focuses on strategic direction, board communications, and customer trust.", "source_ref": "T1", "is_confidential": False},
        {"emp_id": "VX001", "memory_type": "personal_life", "content": "Enjoys black pour-over coffee during morning planning sessions.", "source_ref": "ASSUMPTION_PERSONA", "is_confidential": False},

        # VX002 Manoj Kumar (Sales Lead)
        {"emp_id": "VX002", "memory_type": "grounded_fact", "content": "Sales Lead joined January 2020. Manages enterprise B2B client expansion.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX002", "memory_type": "role_context", "content": "Reports to CEO Ananya Rao; oversees Divya Reddy in Hyderabad.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX002", "memory_type": "personal_life", "content": "Passionate badminton player and weekend marathon runner.", "source_ref": "ASSUMPTION_PERSONA", "is_confidential": False},

        # VX003 Meera Iyer (CFO)
        {"emp_id": "VX003", "memory_type": "grounded_fact", "content": "CFO joined June 2023. Manages Zoho Books general ledger and Keka HRMS.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX003", "memory_type": "role_context", "content": "Reports monthly burn (Rs. 44 L) and runway (13 months) to board. Enforces salary privacy.", "source_ref": "E007,E027", "is_confidential": False},
        {"emp_id": "VX003", "memory_type": "personal_life", "content": "Enjoys classical Carnatic music concerts in Bengaluru.", "source_ref": "ASSUMPTION_PERSONA", "is_confidential": False},

        # VX004 Vikram Menon (VP Engineering)
        {"emp_id": "VX004", "memory_type": "grounded_fact", "content": "VP Engineering joined February 2021. Leads Atlas v3 routing engine development.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX004", "memory_type": "role_context", "content": "Manages engineering team including Priya Nair, Sneha Kulkarni, Arjun Das, and Rahul Verma.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX004", "memory_type": "personal_life", "content": "Custom mechanical keyboard enthusiast with a collection of tactile switches.", "source_ref": "ASSUMPTION_PERSONA", "is_confidential": False},

        # VX005 Deepa Joshi (Head of People & Ops)
        {"emp_id": "VX005", "memory_type": "grounded_fact", "content": "Head of People & Ops joined July 2022. Oversees company operations and HR policies.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX005", "memory_type": "role_context", "content": "Directs HR operations; manages Lakshmi Pillai and talent partner Rohan Banerjee.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX005", "memory_type": "personal_life", "content": "Avid urban gardener maintaining a balcony hydroponic setup.", "source_ref": "ASSUMPTION_PERSONA", "is_confidential": False},

        # VX006 Nikhil Bose (Head of Marketing)
        {"emp_id": "VX006", "memory_type": "grounded_fact", "content": "Head of Marketing joined September 2024. Organized the September 2026 Logistics Summit.", "source_ref": "E020,E016", "is_confidential": False},
        {"emp_id": "VX006", "memory_type": "role_context", "content": "Manages marketing campaigns, event sponsorships, and brand positioning.", "source_ref": "E016", "is_confidential": False},
        {"emp_id": "VX006", "memory_type": "personal_life", "content": "Specialty filter coffee brewer and street photography enthusiast.", "source_ref": "ASSUMPTION_PERSONA", "is_confidential": False},

        # VX007 Priya Nair (Staff Engineer)
        {"emp_id": "VX007", "memory_type": "grounded_fact", "content": "Staff Engineer joined March 2022. Principal architect of the Atlas routing engine.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX007", "memory_type": "role_context", "content": "Led reliability hardening post-August incident; worked with Patil Infra on-call support.", "source_ref": "E008,E015", "is_confidential": False},
        {"emp_id": "VX007", "memory_type": "personal_life", "content": "Weekend cyclist riding trails around Bengaluru outskirts.", "source_ref": "ASSUMPTION_PERSONA", "is_confidential": False},

        # VX008 Divya Reddy (Account Executive)
        {"emp_id": "VX008", "memory_type": "grounded_fact", "content": "Account Executive based in Hyderabad joined January 2024.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX008", "memory_type": "role_context", "content": "Drives enterprise expansion in southern industrial hubs.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX008", "memory_type": "personal_life", "content": "Contemporary pottery enthusiast attending weekend studio workshops.", "source_ref": "ASSUMPTION_PERSONA", "is_confidential": False},

        # VX009 Arjun Das (Senior Frontend Engineer)
        {"emp_id": "VX009", "memory_type": "grounded_fact", "content": "Senior Frontend Engineer joined May 2023, working remotely from Pune.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX009", "memory_type": "role_context", "content": "Builds dispatch consoles, map telemetry, and real-time frontend interfaces for Atlas.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX009", "memory_type": "personal_life", "content": "Indie video game developer and electronic music synthesizer hobbyist.", "source_ref": "ASSUMPTION_PERSONA", "is_confidential": False},

        # VX010 Karthik Subramanian (FP&A Manager)
        {"emp_id": "VX010", "memory_type": "grounded_fact", "content": "FP&A Manager joined October 2024. Handles financial spreadsheets and payroll run.", "source_ref": "E020,E017", "is_confidential": False},
        {"emp_id": "VX010", "memory_type": "role_context", "content": "Executed February 2026 payroll while Fatima Sheikh was on wedding leave.", "source_ref": "E017", "is_confidential": False},
        {"emp_id": "VX010", "memory_type": "personal_life", "content": "Passionate follower of test match cricket and cricket trivia.", "source_ref": "ASSUMPTION_PERSONA", "is_confidential": False},

        # VX011 Aisha Khan (Performance Marketing Manager)
        {"emp_id": "VX011", "memory_type": "grounded_fact", "content": "Performance Marketing Manager joined August 2023.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX011", "memory_type": "role_context", "content": "Managed registrations for the Logistics Summit (212 delegates).", "source_ref": "E016", "is_confidential": False},
        {"emp_id": "VX011", "memory_type": "personal_life", "content": "Host of a local book club focused on translated South Asian fiction.", "source_ref": "ASSUMPTION_PERSONA", "is_confidential": False},

        # VX012 Sneha Kulkarni (Site Reliability Engineer)
        {"emp_id": "VX012", "memory_type": "grounded_fact", "content": "Site Reliability Engineer joined November 2024.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX012", "memory_type": "role_context", "content": "Monitors AWS hosting uptime and coordinate on-call rotation with Vikram and Priya.", "source_ref": "E013,E015", "is_confidential": False},
        {"emp_id": "VX012", "memory_type": "personal_life", "content": "Keeps an aquarium of rare freshwater planted aquascapes.", "source_ref": "ASSUMPTION_PERSONA", "is_confidential": False},

        # VX014 Fatima Sheikh (Accounts & Payroll Executive)
        {"emp_id": "VX014", "memory_type": "grounded_fact", "content": "Accounts & Payroll Executive joined May 2025. Reports to CFO Meera Iyer.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX014", "memory_type": "role_context", "content": "Was away for wedding in late February 2026; acknowledged Rahul's query on 10 March 2026.", "source_ref": "E017,E019", "is_confidential": False},
        {"emp_id": "VX014", "memory_type": "personal_life", "content": "Amateur sourdough and pastry baker experimenting with wild yeast starters.", "source_ref": "ASSUMPTION_PERSONA", "is_confidential": False},

        # VX018 Rahul Verma (Backend Engineer)
        {"emp_id": "VX018", "memory_type": "grounded_fact", "content": "Backend Engineer joined on 2026-02-03. Reports to VP Engineering Vikram Menon.", "source_ref": "E020", "is_confidential": False},
        {"emp_id": "VX018", "memory_type": "role_context", "content": "Works on Atlas routing microservices; flagged February partial-month query to Fatima.", "source_ref": "E018", "is_confidential": False},
        {"emp_id": "VX018", "memory_type": "personal_life", "content": "Hard science fiction enthusiast and retro pixel-art illustrator.", "source_ref": "ASSUMPTION_PERSONA", "is_confidential": False},
    ]

    for m in memories_data:
        existing = db.query(AgentMemory).filter(
            AgentMemory.emp_id == m["emp_id"],
            AgentMemory.content == m["content"]
        ).first()
        if not existing:
            mem = AgentMemory(
                emp_id=m["emp_id"],
                memory_type=m["memory_type"],
                content=m["content"],
                source_ref=m.get("source_ref"),
                is_confidential=m.get("is_confidential", False)
            )
            db.add(mem)

def seed_day1_data(db: Session):
    source_map = ingest_day1_sources(db)
    ingest_day1_people(db)
    ingest_day1_evidence(db, source_map)
    ingest_day1_claims(db, source_map)
    ingest_day1_conflicts(db)
    ingest_day1_assumptions(db)
    ingest_day1_memories(db)
    db.commit()

DAY2_RELEASE_TIME = datetime.datetime(2026, 11, 17, 10, 0, 0)

def ingest_day2_sources(db: Session) -> dict:
    sources_data = [
        {
            "file_name": "T3_Head_of_People_Call.docx",
            "file_type": "docx",
            "description": "MeetNotes AI auto-summary of Head of People call (31 min, good audio). Speakers: Deepa J., Ananya R., Rohan (joined late).",
            "provenance": "Executive interview transcript (provenance_type='user_supplied_text_transcription')."
        },
        {
            "file_name": "T6a_CEO_Voice_Note.docx",
            "file_type": "docx",
            "description": "Auto-transcribed WhatsApp voice notes forwarded by Ananya's assistant.",
            "provenance": "CEO voice note audio transcription (provenance_type='user_supplied_text_transcription')."
        },
        {
            "file_name": "Resignation_Letter_SM.pdf",
            "file_type": "pdf",
            "description": "Resignation letter from Siddharth Mehta (Product Marketing Manager) to Nikhil Bose, dated 15 Sep 2026.",
            "provenance": "HR formal personnel documentation (provenance_type='user_supplied_text_transcription')."
        },
        {
            "file_name": "06.eml",
            "file_type": "eml",
            "description": "Email from Meera Iyer to Vikram Menon pausing REQ-014 and REQ-015.",
            "provenance": "Email server export (provenance_type='user_supplied_text_transcription')."
        },
        {
            "file_name": "07.eml",
            "file_type": "eml",
            "description": "Email from Vikram Menon to Meera Iyer acknowledging hiring pause.",
            "provenance": "Email server export (provenance_type='user_supplied_text_transcription')."
        },
        {
            "file_name": "10.eml",
            "file_type": "eml",
            "description": "Email from Arjun Das to Deepa Joshi requesting permanent remote from Pune.",
            "provenance": "Email server export (provenance_type='user_supplied_text_transcription')."
        },
        {
            "file_name": "11.eml",
            "file_type": "eml",
            "description": "Email from Deepa Joshi to Ananya Rao on pulse results and comment withholding.",
            "provenance": "Email server export (provenance_type='user_supplied_text_transcription')."
        },
        {
            "file_name": "Hiring_Tracker.xlsx",
            "file_type": "xlsx",
            "description": "Hiring tracker (Keka Hire) exported 31-Oct-2026.",
            "provenance": "Keka Hire system export (provenance_type='user_supplied_text_transcription')."
        },
        {
            "file_name": "Leave_Register.xlsx",
            "file_type": "xlsx",
            "description": "Leave register maintained by People & Ops (Google Sheet). Nov 2025 to Oct 2026.",
            "provenance": "People & Ops internal leave spreadsheet (provenance_type='user_supplied_text_transcription').",
            "is_confidential": True
        },
        {
            "file_name": "Pulse_Survey.xlsx",
            "file_type": "xlsx",
            "description": "Culture Amp quarterly pulse, team level only (Oct 2025 to Sep 2026).",
            "provenance": "Culture Amp quarterly pulse export (provenance_type='user_supplied_text_transcription')."
        }
    ]

    source_map = {}
    for s_dict in sources_data:
        existing = db.query(Source).filter(Source.file_name == s_dict["file_name"]).first()
        if not existing:
            s = Source(
                file_name=s_dict["file_name"],
                file_type=s_dict["file_type"],
                release_day="Day2",
                released_at=DAY2_RELEASE_TIME,
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

def ingest_day2_evidence(db: Session, source_map: dict):
    evidence_items = [
        # T3 Head of People Call
        {
            "ref": "E028", "source_file": "T3_Head_of_People_Call.docx", "sheet_or_page": "Transcript", "row_or_line": "Summary",
            "fact_text": "Deepa says attrition is 'about twelve, which is normal for Bangalore' (unclear if this is a percentage, a headcount, or a target); pulse surveys run quarterly on 'Cult Amp'; engineering scores 'dipped in the July round'; and she wants Ananya to see survey comments directly ('numbers alone hide everything').",
            "entities_named": "Deepa J., Ananya R., Culture Amp", "date_as_written": "People Call",
            "record_date": datetime.datetime(2026, 11, 3), "effective_date": datetime.datetime(2026, 11, 3), "confidence": "M"
        },
        {
            "ref": "E029", "source_file": "T3_Head_of_People_Call.docx", "sheet_or_page": "Transcript", "row_or_line": "Key points",
            "fact_text": "HR team consists of Deepa, Rohan on hiring, and Lakshmi as HRBP ('she handles exits'). Rohan says there were 'twenty-two open roles in April' and 'we lost six of them in August'; offer acceptance is 'down to fifty-something'; hiring runs on 'Liver' (probable transcription of Keka Hire) and HR records on 'Kekka' (probable transcription of Keka).",
            "entities_named": "Deepa, Rohan, Lakshmi", "date_as_written": "People Call",
            "record_date": datetime.datetime(2026, 11, 3), "effective_date": datetime.datetime(2026, 11, 3), "confidence": "M"
        },
        {
            "ref": "E030", "source_file": "T3_Head_of_People_Call.docx", "sheet_or_page": "Transcript", "row_or_line": "Key points",
            "fact_text": "Exit interviews: 'most of them say workload'. Deepa mentions 'Sid from marketing' has put in his papers. Deepa says there is 'one engineer I'm worried about' but will not name them on the call. Manager training started 'after Diwali, so November-ish' (Rohan says 'January').",
            "entities_named": "Deepa, Rohan, Sid from marketing", "date_as_written": "People Call",
            "record_date": datetime.datetime(2026, 11, 3), "effective_date": datetime.datetime(2026, 11, 3), "confidence": "M"
        },
        # T6a CEO Voice Note
        {
            "ref": "E031", "source_file": "T6a_CEO_Voice_Note.docx", "sheet_or_page": "Voice Note", "row_or_line": "Audio transcript",
            "fact_text": "CEO Ananya Rao requests: 'Hi, quick one. I won't type questions every morning, na. When I open it, it should just tell me what to worry about. Top three. Okay, bye.'",
            "entities_named": "Ananya Rao", "date_as_written": "Voice Note T6a",
            "record_date": datetime.datetime(2026, 11, 17, 8, 30), "effective_date": datetime.datetime(2026, 11, 17), "confidence": "H"
        },
        # Resignation Letter SM
        {
            "ref": "E032", "source_file": "Resignation_Letter_SM.pdf", "sheet_or_page": "Page 1", "row_or_line": "Body",
            "fact_text": "Siddharth Mehta submitted resignation on 15 September 2026 to Nikhil Bose with last working day 31 October 2026; seeking clearer launch timelines where prepared work reaches customers; promises to hand over launch kit before leaving.",
            "entities_named": "Siddharth Mehta, Nikhil Bose", "date_as_written": "15 September 2026",
            "record_date": datetime.datetime(2026, 9, 15), "effective_date": datetime.datetime(2026, 10, 31), "confidence": "H"
        },
        # Emails
        {
            "ref": "E033", "source_file": "06.eml", "sheet_or_page": "Email", "row_or_line": "Headers & Body",
            "fact_text": "CFO Meera Iyer emailed Vikram Menon (cc Ananya Rao, Rohan Banerjee) on 12 Aug 2026: 'Pausing REQ-014 and REQ-015 until the round closes. Burn is the priority this quarter.'",
            "entities_named": "Meera Iyer, Vikram Menon, Ananya Rao, Rohan Banerjee", "date_as_written": "Wed, 12 Aug 2026 10:12:00 +0530",
            "record_date": datetime.datetime(2026, 8, 12, 10, 12), "effective_date": datetime.datetime(2026, 8, 12), "confidence": "H"
        },
        {
            "ref": "E034", "source_file": "07.eml", "sheet_or_page": "Email", "row_or_line": "Headers & Body",
            "fact_text": "Vikram Menon replied to Meera Iyer on 12 Aug 2026: 'Understood. We'll absorb it.'",
            "entities_named": "Vikram Menon, Meera Iyer", "date_as_written": "Wed, 12 Aug 2026 11:48:00 +0530",
            "record_date": datetime.datetime(2026, 8, 12, 11, 48), "effective_date": datetime.datetime(2026, 8, 12), "confidence": "H"
        },
        {
            "ref": "E035", "source_file": "10.eml", "sheet_or_page": "Email", "row_or_line": "Headers & Body",
            "fact_text": "Arjun Das emailed Deepa Joshi on 18 Sep 2026 requesting to make remote from Pune permanent with offers to visit Bengaluru once a month; no approval or policy change is documented in records.",
            "entities_named": "Arjun Das, Deepa Joshi", "date_as_written": "Fri, 18 Sep 2026 12:00:00 +0530",
            "record_date": datetime.datetime(2026, 9, 18, 12, 0), "effective_date": datetime.datetime(2026, 9, 18), "confidence": "H"
        },
        {
            "ref": "E036", "source_file": "11.eml", "sheet_or_page": "Email", "row_or_line": "Headers & Body",
            "fact_text": "Deepa Joshi emailed Ananya Rao on 29 Sep 2026: 'Ananya, engineering pulse dropped this quarter. The team is too small for me to share comments. I'd suggest Vikram does 1:1s this week.'",
            "entities_named": "Deepa Joshi, Ananya Rao, Vikram Menon", "date_as_written": "Tue, 29 Sep 2026 17:30:00 +0530",
            "record_date": datetime.datetime(2026, 9, 29, 17, 30), "effective_date": datetime.datetime(2026, 9, 29), "confidence": "H"
        },
        # Hiring Tracker
        {
            "ref": "E037", "source_file": "Hiring_Tracker.xlsx", "sheet_or_page": "Requisitions", "row_or_line": "Row 4",
            "fact_text": "REQ-011: Account Executive, Sales, Hiring Manager VX002, Opened 2026-01-10, Status: Closed - not hired, Status Date: 2026-04-02, In pipeline: 0, Notes: Budget moved to marketing.",
            "entities_named": "REQ-011, Manoj Kumar", "date_as_written": "2026-04-02",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 4, 2), "confidence": "H"
        },
        {
            "ref": "E038", "source_file": "Hiring_Tracker.xlsx", "sheet_or_page": "Requisitions", "row_or_line": "Row 5",
            "fact_text": "REQ-013: Backend Engineer, Engineering, Hiring Manager VX004, Opened 2025-12-01, Status: Filled, Status Date: 2026-01-12, In pipeline: 0, Notes: Offer accepted, joining 3-Feb.",
            "entities_named": "REQ-013, Vikram Menon, Rahul Verma", "date_as_written": "2026-01-12",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 1, 12), "confidence": "H"
        },
        {
            "ref": "E039", "source_file": "Hiring_Tracker.xlsx", "sheet_or_page": "Requisitions", "row_or_line": "Row 6",
            "fact_text": "REQ-014: Backend Engineer (Routing), Engineering, Hiring Manager VX004, Opened 2026-05-18, Status: On hold, Status Date: 2026-08-12, In pipeline: 3, Notes: Final round 14-Aug cancelled.",
            "entities_named": "REQ-014, Vikram Menon", "date_as_written": "2026-08-12",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 8, 12), "confidence": "H"
        },
        {
            "ref": "E040", "source_file": "Hiring_Tracker.xlsx", "sheet_or_page": "Requisitions", "row_or_line": "Row 7",
            "fact_text": "REQ-015: Backend Engineer (Platform), Engineering, Hiring Manager VX004, Opened 2026-05-18, Status: On hold, Status Date: 2026-08-12, In pipeline: 5.",
            "entities_named": "REQ-015, Vikram Menon", "date_as_written": "2026-08-12",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 8, 12), "confidence": "H"
        },
        {
            "ref": "E041", "source_file": "Hiring_Tracker.xlsx", "sheet_or_page": "Requisitions", "row_or_line": "Row 8",
            "fact_text": "REQ-016: Product Marketing Manager, Marketing, Hiring Manager VX006, Opened 2026-09-17, Status: Open, Status Date: 2026-09-17, In pipeline: 7, Notes: Backfill.",
            "entities_named": "REQ-016, Nikhil Bose, Siddharth Mehta", "date_as_written": "2026-09-17",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 9, 17), "confidence": "H"
        },
        {
            "ref": "E042", "source_file": "Hiring_Tracker.xlsx", "sheet_or_page": "Requisitions", "row_or_line": "Row 9",
            "fact_text": "REQ-017: Support Associate, Support, Hiring Manager VX016, Opened 2026-10-01, Status: Open, Status Date: 2026-10-01, In pipeline: 2.",
            "entities_named": "REQ-017, Imran Siddiqui", "date_as_written": "2026-10-01",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 10, 1), "confidence": "H"
        },
        # Leave Register (Confidential HR Records)
        {
            "ref": "E043", "source_file": "Leave_Register.xlsx", "sheet_or_page": "Leave FY", "row_or_line": "Rows 4-15, 21-22",
            "fact_text": "Approved company leave records Nov 2025 to Oct 2026 include A. Das (Casual 1d, Relocation 5d), K. Subramanian (Casual 1d, Exam 5d), F. Sheikh (Marriage 15d), S. Kulkarni (Sick 2d), N. Bose (Casual 1d), A. Khan (Earned 5d), R. Verma (Casual 1d), S. Mehta (Earned 5d), D. Joshi (Earned 5d), L. Pillai (Casual 1d), V. Menon (Earned 5d).",
            "entities_named": "Veloxa staff leave", "date_as_written": "Nov 2025 - Oct 2026",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 10, 31), "confidence": "H", "is_confidential": True
        },
        {
            "ref": "E044", "source_file": "Leave_Register.xlsx", "sheet_or_page": "Leave FY", "row_or_line": "Rows 16-20",
            "fact_text": "P. Nair took five approved personal half-days (PM, 0.5 days each, total 2.5 days) on 2026-09-03, 2026-09-08, 2026-09-15, 2026-09-17, and 2026-09-24, all approved by VM (Vikram Menon). Source documents do not state reason; no inference of illness, burnout, or performance is permitted.",
            "entities_named": "P. Nair, VM", "date_as_written": "Sep 2026",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 9, 24), "confidence": "H", "is_confidential": True
        },
        # Pulse Survey
        {
            "ref": "E045", "source_file": "Pulse_Survey.xlsx", "sheet_or_page": "Pulse by team", "row_or_line": "Rows 4-7",
            "fact_text": "Engineering pulse scores on 1-5 scale: Oct-Dec 2025: 4.0 (size 5, 5 responses); Jan-Mar 2026: 4.0 (size 5, 5 responses); Apr-Jun 2026: 3.9 (size 5, 5 responses); Jul-Sep 2026: 3.1 (size 5, 4 responses; drop of -0.8). Comments: Not shown: team smaller than 6.",
            "entities_named": "Engineering Team, Culture Amp", "date_as_written": "Jul-Sep 2026",
            "record_date": datetime.datetime(2026, 10, 1), "effective_date": datetime.datetime(2026, 9, 30), "confidence": "H"
        },
        {
            "ref": "E046", "source_file": "Pulse_Survey.xlsx", "sheet_or_page": "Pulse by team", "row_or_line": "Rows 16-19",
            "fact_text": "Marketing pulse scores on 1-5 scale: Oct-Dec 2025: 3.9; Jan-Mar 2026: 3.9; Apr-Jun 2026: 3.8; Jul-Sep 2026: 3.4 (size 3, 3 responses; drop of -0.4). Comments: Not shown: team smaller than 6.",
            "entities_named": "Marketing Team, Culture Amp", "date_as_written": "Jul-Sep 2026",
            "record_date": datetime.datetime(2026, 10, 1), "effective_date": datetime.datetime(2026, 9, 30), "confidence": "H"
        },
        {
            "ref": "E047", "source_file": "Pulse_Survey.xlsx", "sheet_or_page": "Pulse by team", "row_or_line": "Rows 8-15, 20-27",
            "fact_text": "Quarterly pulse scores across other teams (Apr-Jun to Jul-Sep 2026): Finance 3.8 to 3.9 (+0.1, size 3); People & Ops 4.0 to 4.1 (+0.1, size 3); Sales 3.9 to 3.8 (-0.1, size 2); Support 4.1 to 4.0 (-0.1, size 2). All comments withheld because team sizes are smaller than 6.",
            "entities_named": "Finance, People & Ops, Sales, Support Teams, Culture Amp", "date_as_written": "Jul-Sep 2026",
            "record_date": datetime.datetime(2026, 10, 1), "effective_date": datetime.datetime(2026, 9, 30), "confidence": "H"
        }
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
                date_normalized=item.get("effective_date"),
                confidence=item.get("confidence", "H"),
                is_confidential=item.get("is_confidential", False),
                released_at=DAY2_RELEASE_TIME
            )
            db.add(e)
        else:
            existing.fact_text = item["fact_text"]
            existing.entities_named = item.get("entities_named")
            existing.record_date = item.get("record_date")
            existing.effective_date = item.get("effective_date")
            existing.date_normalized = item.get("effective_date")
            existing.confidence = item.get("confidence", "H")
            existing.is_confidential = item.get("is_confidential", False)

def ingest_day2_claims(db: Session, source_map: dict):
    claims_data = [
        {
            "claim_id": "CLM-023", "speaker_or_author": "Deepa Joshi (Head of People)", "source_file": "T3_Head_of_People_Call.docx",
            "claim_category": "Culture", "claim_text": "Deepa states attrition is 'about twelve, which is normal for Bangalore' (unit/denominator undefined).",
            "date_asserted": "People Call (T3)", "record_date": datetime.datetime(2026, 11, 3), "effective_date": datetime.datetime(2026, 11, 3),
            "is_disputed": True, "competing_evidence_refs": None, "evidence_ref": "E028", "confidence": "M", "conflict_id": "CONF-006"
        },
        {
            "claim_id": "CLM-024", "speaker_or_author": "Rohan Banerjee (Talent Partner)", "source_file": "T3_Head_of_People_Call.docx",
            "claim_category": "Operations", "claim_text": "Rohan asserts there were 22 open roles in April, 6 lost in August, and offer acceptance is down to fifty-something.",
            "date_asserted": "People Call (T3)", "record_date": datetime.datetime(2026, 11, 3), "effective_date": datetime.datetime(2026, 11, 3),
            "is_disputed": True, "competing_evidence_refs": "E037,E038,E039,E040,E041,E042", "evidence_ref": "E029", "confidence": "M", "conflict_id": "CONF-006"
        },
        {
            "claim_id": "CLM-025", "speaker_or_author": "Deepa Joshi (Head of People)", "source_file": "T3_Head_of_People_Call.docx",
            "claim_category": "Culture", "claim_text": "Exit interviews indicate most departures cite workload, and there is one unnamed engineer Deepa is worried about.",
            "date_asserted": "People Call (T3)", "record_date": datetime.datetime(2026, 11, 3), "effective_date": datetime.datetime(2026, 11, 3),
            "is_disputed": True, "competing_evidence_refs": None, "evidence_ref": "E030", "confidence": "M", "conflict_id": "CONF-006"
        },
        {
            "claim_id": "CLM-026", "speaker_or_author": "Deepa Joshi / Rohan Banerjee", "source_file": "T3_Head_of_People_Call.docx",
            "claim_category": "Operations", "claim_text": "Manager training start date is disputed: Deepa says after Diwali (November-ish); Rohan says January.",
            "date_asserted": "People Call (T3)", "record_date": datetime.datetime(2026, 11, 3), "effective_date": datetime.datetime(2026, 11, 3),
            "is_disputed": True, "competing_evidence_refs": None, "evidence_ref": "E030", "confidence": "M", "conflict_id": "CONF-006"
        },
        {
            "claim_id": "CLM-027", "speaker_or_author": "Deepa Joshi (Head of People)", "source_file": "T3_Head_of_People_Call.docx",
            "claim_category": "Culture", "claim_text": "Deepa verbally advocated for Ananya to see pulse survey comments directly ('numbers alone hide everything').",
            "date_asserted": "People Call (T3)", "record_date": datetime.datetime(2026, 11, 3), "effective_date": datetime.datetime(2026, 11, 3),
            "is_disputed": True, "competing_evidence_refs": "E036,E045,E046,E047", "evidence_ref": "E028", "confidence": "M", "conflict_id": "CONF-005"
        },
        {
            "claim_id": "CLM-028", "speaker_or_author": "Deepa Joshi (Head of People)", "source_file": "11.eml",
            "claim_category": "Culture", "claim_text": "Deepa explicitly refused to share engineering survey comments with Ananya due to team size being too small, advising Vikram 1:1s.",
            "date_asserted": "2026-09-29", "record_date": datetime.datetime(2026, 9, 29, 17, 30), "effective_date": datetime.datetime(2026, 9, 29),
            "is_disputed": True, "competing_evidence_refs": "E028", "evidence_ref": "E036", "confidence": "H", "conflict_id": "CONF-005"
        },
        {
            "claim_id": "CLM-029", "speaker_or_author": "Meera Iyer (CFO)", "source_file": "06.eml",
            "claim_category": "Operations", "claim_text": "Pausing REQ-014 and REQ-015 until the funding round closes; burn is the priority this quarter.",
            "date_asserted": "2026-08-12", "record_date": datetime.datetime(2026, 8, 12, 10, 12), "effective_date": datetime.datetime(2026, 8, 12),
            "is_disputed": False, "competing_evidence_refs": None, "evidence_ref": "E033", "confidence": "H", "conflict_id": None
        },
        {
            "claim_id": "CLM-030", "speaker_or_author": "Vikram Menon (VP Eng)", "source_file": "07.eml",
            "claim_category": "Operations", "claim_text": "Vikram acknowledged pausing REQ-014 and REQ-015: 'Understood. We'll absorb it.'",
            "date_asserted": "2026-08-12", "record_date": datetime.datetime(2026, 8, 12, 11, 48), "effective_date": datetime.datetime(2026, 8, 12),
            "is_disputed": False, "competing_evidence_refs": None, "evidence_ref": "E034", "confidence": "H", "conflict_id": None
        },
        {
            "claim_id": "CLM-031", "speaker_or_author": "Siddharth Mehta (Product Marketing Manager)", "source_file": "Resignation_Letter_SM.pdf",
            "claim_category": "Marketing", "claim_text": "Siddharth resigned on 15 Sep 2026 with last day 31 Oct 2026; seeking clearer launch timelines; promises launch kit handover.",
            "date_asserted": "2026-09-15", "record_date": datetime.datetime(2026, 9, 15), "effective_date": datetime.datetime(2026, 10, 31),
            "is_disputed": False, "competing_evidence_refs": None, "evidence_ref": "E032", "confidence": "H", "conflict_id": None
        },
        {
            "claim_id": "CLM-032", "speaker_or_author": "Arjun Das (Sr Frontend Engineer)", "source_file": "10.eml",
            "claim_category": "Operations", "claim_text": "Arjun requested permanent remote work from Pune with monthly visits; request is unapproved in records.",
            "date_asserted": "2026-09-18", "record_date": datetime.datetime(2026, 9, 18, 12, 0), "effective_date": datetime.datetime(2026, 9, 18),
            "is_disputed": False, "competing_evidence_refs": None, "evidence_ref": "E035", "confidence": "H", "conflict_id": None
        },
        {
            "claim_id": "CLM-033", "speaker_or_author": "Culture Amp Pulse Survey", "source_file": "Pulse_Survey.xlsx",
            "claim_category": "Culture", "claim_text": "Engineering engagement dropped from 3.9 (Apr-Jun) to 3.1 (Jul-Sep 2026) with 4 of 5 responding; marketing dropped from 3.8 to 3.4; comments withheld for all teams.",
            "date_asserted": "Jul-Sep 2026", "record_date": datetime.datetime(2026, 10, 1), "effective_date": datetime.datetime(2026, 9, 30),
            "is_disputed": False, "competing_evidence_refs": None, "evidence_ref": "E045", "confidence": "H", "conflict_id": None
        },
        {
            "claim_id": "CLM-034", "speaker_or_author": "Keka Hire System", "source_file": "Hiring_Tracker.xlsx",
            "claim_category": "Operations", "claim_text": "Requisition status: REQ-011 closed-not-hired, REQ-013 filled, REQ-014 on hold (pipeline 3), REQ-015 on hold (pipeline 5), REQ-016 open (pipeline 7), REQ-017 open (pipeline 2).",
            "date_asserted": "Exported 31-Oct-2026", "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 10, 31),
            "is_disputed": False, "competing_evidence_refs": None, "evidence_ref": "E037", "confidence": "H", "conflict_id": None
        }
    ]

    for c in claims_data:
        s_id = source_map.get(c["source_file"])
        if not s_id:
            s_obj = db.query(Source).filter(Source.file_name == c["source_file"]).first()
            s_id = s_obj.id if s_obj else 1

        existing = db.query(Claim).filter(Claim.claim_id == c["claim_id"]).first()
        if not existing:
            cl = Claim(
                claim_id=c["claim_id"],
                speaker_or_author=c["speaker_or_author"],
                source_id=s_id,
                claim_text=c["claim_text"],
                claim_category=c["claim_category"],
                date_asserted=c.get("date_asserted"),
                record_date=c.get("record_date"),
                effective_date=c.get("effective_date"),
                is_disputed=c.get("is_disputed", False),
                competing_evidence_refs=c.get("competing_evidence_refs"),
                evidence_ref=c.get("evidence_ref"),
                confidence=c.get("confidence", "M"),
                conflict_id=c.get("conflict_id"),
                released_at=DAY2_RELEASE_TIME
            )
            db.add(cl)
        else:
            existing.claim_text = c["claim_text"]
            existing.claim_category = c["claim_category"]
            existing.is_disputed = c.get("is_disputed", False)
            existing.competing_evidence_refs = c.get("competing_evidence_refs")
            existing.evidence_ref = c.get("evidence_ref")
            existing.confidence = c.get("confidence", "M")
            existing.conflict_id = c.get("conflict_id")

def ingest_day2_conflicts(db: Session):
    conflicts_data = [
        {
            "conflict_id": "CONF-005",
            "topic": "Engineering Survey Comment Visibility vs Re-Identification Privacy",
            "description": "In transcript T3, Deepa advocated for CEO Ananya to see survey comments directly ('numbers alone hide everything'). In email 11.eml (29 Sep 2026), Deepa explicitly refused to share engineering comments with Ananya stating the team is too small (<6 members) and advised Vikram conduct 1:1s instead. In Pulse_Survey.xlsx, comments for all teams are withheld with notice 'Not shown: team smaller than 6'.",
            "competing_sources": "T3_Head_of_People_Call.docx (E028) VS 11.eml (E036), Pulse_Survey.xlsx (E045-E047)",
            "proposed_interpretation": "Strict privacy-by-design policy: withhold all qualitative survey comments for teams under 6 members to protect employee confidentiality and prevent re-identification. Deepa's written refusal (11.eml) supersedes verbal call sentiment. Vikram should conduct 1:1s as suggested.",
            "confidence": "H",
            "what_would_change": "Documented written waiver from all team members or anonymized aggregate sentiment themes verified by third-party HR auditor.",
            "impact_level": "HIGH",
            "human_status": "UNRESOLVED"
        },
        {
            "conflict_id": "CONF-006",
            "topic": "People & Talent Operations Ambiguities (T3 Call Discrepancies)",
            "description": "T3 call transcript contains multiple unverified verbal assertions: Deepa states attrition is 'about twelve' (unit undefined: percentage, count, or target); Rohan claims 22 open roles in April and losing 6 in August with offer acceptance 'down to fifty-something' (none corroborated by the 6-row hiring tracker); Deepa notes 'one engineer I'm worried about' without naming them; manager training start date is disputed between Deepa (November-ish) and Rohan (January).",
            "competing_sources": "T3_Head_of_People_Call.docx (E028-E030) VS Hiring_Tracker.xlsx (E037-E042)",
            "proposed_interpretation": "Maintain ambiguous verbal transcript numbers as uncorroborated claims. Base hiring facts strictly on the Keka Hire 6-requisition tracker. Do not guess the unnamed engineer's identity or attribute Priya Nair's personal half-days to burnout/performance. Do not treat 4/5 survey responses as an attrition statistic.",
            "confidence": "M",
            "what_would_change": "Formal ATS historical requisition logs, official HR attrition calculation methodology, or signed HR quarterly report.",
            "impact_level": "MEDIUM",
            "human_status": "UNRESOLVED"
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

def ingest_day2_assumptions(db: Session):
    assumptions_data = [
        {
            "assumption_id": "ASM-006",
            "domain": "Engineering / Culture",
            "statement": "Engineering pulse engagement drop (-0.8 to 3.1) and missing 5th response reflects acute workload pressure following August reliability issues and hiring freeze, but individual causes cannot be attributed without 1:1 feedback.",
            "rationale": "Q2 board update and GL actuals confirm August incidents; hiring pause left team shorthanded; comments withheld to protect small team.",
            "risk_if_wrong": "If drop was driven by compensation or management friction, 1:1s will fail to diagnose root causes."
        },
        {
            "assumption_id": "ASM-007",
            "domain": "Operations / HR",
            "statement": "Arjun Das's request for permanent remote work remains an unapproved individual request, and Siddharth Mehta's promise to hand over the launch kit remains an unverified commitment until validated post-exit.",
            "rationale": "No approval email exists in records for Arjun; Siddharth's last working day was 31 Oct and replacement REQ-016 is currently open in pipeline.",
            "risk_if_wrong": "If remote was verbally agreed or launch kit was not handed over, Atlas frontend delivery and product marketing will suffer gaps."
        }
    ]

    for a in assumptions_data:
        existing = db.query(Assumption).filter(Assumption.assumption_id == a["assumption_id"]).first()
        if not existing:
            ass = Assumption(
                assumption_id=a["assumption_id"],
                domain=a["domain"],
                statement=a["statement"],
                rationale=a["rationale"],
                risk_if_wrong=a["risk_if_wrong"]
            )
            db.add(ass)
        else:
            existing.statement = a["statement"]
            existing.rationale = a["rationale"]
            existing.risk_if_wrong = a["risk_if_wrong"]

def ingest_day2_memories(db: Session):
    memories_data = [
        # VX005 Deepa Joshi (Head of People & Ops)
        {"emp_id": "VX005", "memory_type": "grounded_fact", "content": "Culture Amp quarterly pulse showed engineering dropped from 3.9 to 3.1 and marketing dropped to 3.4. Refused to share comments to protect team anonymity.", "source_ref": "E036,E045,E046", "is_confidential": False},
        {"emp_id": "VX005", "memory_type": "role_context", "content": "Recommended Vikram conduct 1:1s with engineering team; received remote work request from Arjun Das (pending review); received Siddharth Mehta's resignation letter.", "source_ref": "E032,E035,E036", "is_confidential": False},

        # VX004 Vikram Menon (VP Engineering)
        {"emp_id": "VX004", "memory_type": "grounded_fact", "content": "Acknowledged CFO Meera's pause on backend requisitions REQ-014 and REQ-015 in August ('Understood. We'll absorb it.').", "source_ref": "E033,E034", "is_confidential": False},
        {"emp_id": "VX004", "memory_type": "role_context", "content": "Planning 1:1 sessions with engineering team members to discuss workload following the difficult August incident and pulse survey drop.", "source_ref": "E036", "is_confidential": False},

        # VX003 Meera Iyer (CFO)
        {"emp_id": "VX003", "memory_type": "grounded_fact", "content": "Paused engineering requisitions REQ-014 and REQ-015 on 12 Aug 2026 to prioritize cash burn until financing round closes.", "source_ref": "E033", "is_confidential": False},

        # VX006 Nikhil Bose (Head of Marketing)
        {"emp_id": "VX006", "memory_type": "grounded_fact", "content": "Received Siddharth Mehta's resignation letter on 15 Sep 2026 (last day 31 Oct); opened REQ-016 backfill requisition (7 candidates in pipeline).", "source_ref": "E032,E041", "is_confidential": False},
        {"emp_id": "VX006", "memory_type": "role_context", "content": "Marketing pulse dropped to 3.4 in Jul-Sep; awaiting verified completion of Atlas launch kit handover.", "source_ref": "E032,E046", "is_confidential": False},

        # VX009 Arjun Das (Senior Frontend Engineer)
        {"emp_id": "VX009", "memory_type": "grounded_fact", "content": "Sent email on 18 Sep 2026 to Deepa requesting permanent remote work from Pune with monthly Bengaluru visits; awaiting formal company response.", "source_ref": "E035", "is_confidential": False},
    ]

    for m in memories_data:
        existing = db.query(AgentMemory).filter(
            AgentMemory.emp_id == m["emp_id"],
            AgentMemory.content == m["content"]
        ).first()
        if not existing:
            mem = AgentMemory(
                emp_id=m["emp_id"],
                memory_type=m["memory_type"],
                content=m["content"],
                source_ref=m.get("source_ref"),
                is_confidential=m.get("is_confidential", False)
            )
            db.add(mem)

def seed_day2_data(db: Session):
    source_map = ingest_day2_sources(db)
    ingest_day2_evidence(db, source_map)
    ingest_day2_claims(db, source_map)
    ingest_day2_conflicts(db)
    ingest_day2_assumptions(db)
    ingest_day2_memories(db)
    db.commit()


# ==============================================================================
# DAY 3 INGESTION ENGINE
# ==============================================================================

def ingest_day3_sources(db: Session) -> dict:
    sources_data = [
        {
            "file_name": "T4_Head_of_Marketing_Call.docx",
            "file_type": "docx",
            "description": "MeetNotes AI auto-summary of Head of Marketing Nikhil Bose call (22 min, fair audio).",
            "provenance": "Executive interview transcript."
        },
        {
            "file_name": "T5_VP_Engineering_Call.docx",
            "file_type": "docx",
            "description": "MeetNotes AI auto-summary of VP Engineering Vikram Menon call (19 min, fair audio, audio gap 11:20-15:30).",
            "provenance": "Executive interview transcript."
        },
        {
            "file_name": "T6b_CEO_Voice_Note.docx",
            "file_type": "docx",
            "description": "Auto-transcribed WhatsApp voice note forwarded by Ananya's assistant re: marketing reporting to new CRO.",
            "provenance": "CEO WhatsApp voice note."
        },
        {
            "file_name": "Jira_Export_ATLAS.xlsx",
            "file_type": "xlsx",
            "description": "Jira export for project ATLAS: 62 issues, 5 epics, version records with release dates and changelog.",
            "provenance": "Jira system export."
        },
        {
            "file_name": "git_log.csv",
            "file_type": "csv",
            "description": "Git commit history across 4 repositories (atlas-engine, planner-web, infra, atlas-api) totaling 1,453 commits.",
            "provenance": "Git version control export."
        },
        {
            "file_name": "Incidents_Aug-Oct_2026.xlsx",
            "file_type": "xlsx",
            "description": "PagerDuty incident export (Aug-Oct 2026) totaling 11 incidents with UTC timestamps, severities, and responders.",
            "provenance": "PagerDuty system export."
        },
        {
            "file_name": "OnCall_Rota.xlsx",
            "file_type": "xlsx",
            "description": "Weekly primary and secondary on-call rota from engineering wiki across 17 weeks (Jul-Oct 2026).",
            "provenance": "Engineering team wiki export."
        },
        {
            "file_name": "Atlas_Launch_Kit_v1.pdf",
            "file_type": "pdf",
            "description": "Atlas launch kit document authored by Sid on 21 Jul 2026 listing status of 5 launch assets.",
            "provenance": "Product marketing document."
        },
        {
            "file_name": "Invoice_PIS-114.pdf",
            "file_type": "pdf",
            "description": "Tax invoice from Patil Infra Services dated 01/10/2026 for September SRE retainer (Rs. 1,41,600 total incl. IGST).",
            "provenance": "Vendor billing invoice."
        },
        {
            "file_name": "04.eml",
            "file_type": "eml",
            "description": "Email from Vikram Menon to Ananya Rao on 02 Jun 2026 re: Atlas plan and conditional 15 Sep GA.",
            "provenance": "Email server export (2026-06-02 09:30 IST)."
        },
        {
            "file_name": "05.eml",
            "file_type": "eml",
            "description": "Email from Siddharth Mehta to Nikhil Bose on 22 Jul 2026 re: Atlas launch kit ready.",
            "provenance": "Email server export (2026-07-22 18:05 IST)."
        },
        {
            "file_name": "08.eml",
            "file_type": "eml",
            "description": "Email from Sneha Kulkarni to Vikram Menon on 24 Aug 2026 re: Third SEV1 in August and contractor starting on rota.",
            "provenance": "Email server export (2026-08-24 09:05 IST)."
        },
        {
            "file_name": "09.eml",
            "file_type": "eml",
            "description": "Email from Priya Nair to Vikram Menon on 01 Sep 2026 re: requesting time to discuss Atlas ownership.",
            "provenance": "Email server export (2026-09-01 23:47 IST)."
        },
        {
            "file_name": "Email_Printouts.pdf",
            "file_type": "pdf",
            "description": "Printout collection containing duplicate copies of emails 01-11; deduplicated as corroborating secondary provenance.",
            "provenance": "Consolidated email printout export."
        },
        {
            "file_name": "Candidate_Brief.docx",
            "file_type": "docx",
            "description": "Original 10-day candidate brief provided as background context, superseded by authoritative 5-day schedule.",
            "provenance": "Candidate orientation document."
        }
    ]

    source_map = {}
    for s_dict in sources_data:
        existing = db.query(Source).filter(Source.file_name == s_dict["file_name"]).first()
        if not existing:
            s = Source(
                file_name=s_dict["file_name"],
                file_type=s_dict["file_type"],
                release_day="Day3",
                released_at=DAY3_RELEASE_TIME,
                description=s_dict.get("description"),
                provenance=s_dict.get("provenance"),
                is_confidential=False
            )
            db.add(s)
            db.flush()
            source_map[s.file_name] = s.id
        else:
            source_map[existing.file_name] = existing.id
    return source_map


def ingest_day3_evidence(db: Session, source_map: dict):
    evidence_items = [
        # T4 Head of Marketing
        {
            "ref": "E048", "source_file": "T4_Head_of_Marketing_Call.docx", "sheet_or_page": "P4, P8, P9", "row_or_line": "Summary & Key points",
            "fact_text": "Total marketing spend for the half is 'one point eight' by Nikhil's numbers; notes finance 'counts things differently'; calls September summit best quarter ever for pipeline; claims summit leads cold feedback dismissed.",
            "entities_named": "Nikhil Bose, Ayesha Khan, Siddharth Mehta, Manoj Kumar", "date_as_written": "Recorded 31 Oct 2026",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 9, 30),
            "confidence": "M", "is_confidential": False
        },
        # T5 VP Engineering
        {
            "ref": "E049", "source_file": "T5_VP_Engineering_Call.docx", "sheet_or_page": "P4, P6, P10", "row_or_line": "Summary & Key points",
            "fact_text": "Vikram states v3 is 'on track, maybe a couple of weeks of buffer needed' and board date is 'still September-ish'; disputes overload; mentions Pria late nights, Snehal on SRE/on-call, and audio gap 11:20-15:30.",
            "entities_named": "Vikram Menon, Ananya Rao, Priya Nair, Snehal, Sneha, Arjun Das, Rahul Verma", "date_as_written": "Recorded 31 Oct 2026",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 9, 30),
            "confidence": "M", "is_confidential": False
        },
        # T6b CEO Voice Note
        {
            "ref": "E050", "source_file": "T6b_CEO_Voice_Note.docx", "sheet_or_page": "P3", "row_or_line": "Voice note transcript",
            "fact_text": "Ananya voice note: 'So, marketing will report to the new CRO from next month. Or the month after, still finalising. Make sure the thing doesn't break when we move people around.'",
            "entities_named": "Ananya Rao, CRO, Nikhil Bose, Marketing", "date_as_written": "18 Nov 2026",
            "record_date": datetime.datetime(2026, 11, 18), "effective_date": None,
            "confidence": "H", "is_confidential": False
        },
        # Jira Version Atlas GA
        {
            "ref": "E051", "source_file": "Jira_Export_ATLAS.xlsx", "sheet_or_page": "Sheet Versions", "row_or_line": "Row 2",
            "fact_text": "Jira version record Atlas GA: Original Release Date 2026-09-15, revised Release Date 2026-12-15, Last Changed 2026-09-02, Changed By vikram.",
            "entities_named": "Vikram Menon, ATLAS Project, Atlas GA", "date_as_written": "2026-09-02",
            "record_date": datetime.datetime(2026, 9, 2), "effective_date": datetime.datetime(2026, 12, 15),
            "confidence": "H", "is_confidential": False
        },
        # Git log aggregate
        {
            "ref": "E052", "source_file": "git_log.csv", "sheet_or_page": "All Repos", "row_or_line": "Rows 2-1454",
            "fact_text": "Git log across 4 repositories contains 1,453 commits: Priya Nair 588 commits (425 priya.n@veloxa.in + 163 pnair@users.noreply.github.com), Arjun Das 348, Rahul Verma 237, Sneha Kulkarni 235, Vikram Menon 45.",
            "entities_named": "Priya Nair, Arjun Das, Rahul Verma, Sneha Kulkarni, Vikram Menon", "date_as_written": "2025-11-03 to 2026-10-31",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 10, 31),
            "confidence": "H", "is_confidential": False
        },
        # Incidents August SEV1s
        {
            "ref": "E053", "source_file": "Incidents_Aug-Oct_2026.xlsx", "sheet_or_page": "Sheet Incidents", "row_or_line": "Rows 4, 6, 8",
            "fact_text": "PagerDuty incident export records 11 incidents from Aug to Oct 2026. Exactly 3 SEV1 incidents occurred in August (INC-201 on Aug 4, INC-203 on Aug 13, INC-205 on Aug 22), all affecting routing-api with responder Sneha.",
            "entities_named": "Sneha Kulkarni, routing-api, PagerDuty", "date_as_written": "Aug 2026",
            "record_date": datetime.datetime(2026, 8, 31), "effective_date": datetime.datetime(2026, 8, 31),
            "confidence": "H", "is_confidential": False
        },
        # OnCall Rota
        {
            "ref": "E054", "source_file": "OnCall_Rota.xlsx", "sheet_or_page": "Sheet On-call", "row_or_line": "Rows 4-20",
            "fact_text": "On-call rota across 17 weeks: Weeks 1-6 (Jul 6 to Aug 10) Primary is Sneha with Secondary alternating Arjun/Priya. Starting week of Aug 17, Snehal is Primary (Secondary Sneha); thereafter Sneha and Snehal alternate Primary and Secondary weekly through Oct 26.",
            "entities_named": "Sneha Kulkarni, Snehal, Arjun Das, Priya Nair", "date_as_written": "2026-07-06 to 2026-10-26",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 10, 26),
            "confidence": "H", "is_confidential": False
        },
        # Launch Kit Assets
        {
            "ref": "E055", "source_file": "Atlas_Launch_Kit_v1.pdf", "sheet_or_page": "Page 1", "row_or_line": "Rows 1-5",
            "fact_text": "Atlas launch kit v1 (Owner Sid, 21 Jul 2026): Launch deck ready, Website page 'Ready, unpublished', Customer email sequence ready, Press note 'Draft', Launch date 'TBC with engineering (planned 22 Sep)'.",
            "entities_named": "Siddharth Mehta, Atlas Launch Kit", "date_as_written": "21 Jul 2026",
            "record_date": datetime.datetime(2026, 7, 21), "effective_date": datetime.datetime(2026, 9, 22),
            "confidence": "H", "is_confidential": False
        },
        # Invoice PIS-114
        {
            "ref": "E056", "source_file": "Invoice_PIS-114.pdf", "sheet_or_page": "Page 1", "row_or_line": "Full invoice",
            "fact_text": "Invoice PIS-114 dated 01/10/2026 from Patil Infra Services: On-call SRE support, S. Patil, September 2026 retainer Rs. 1,20,000 + IGST 18% Rs. 21,600 = Rs. 1,41,600. Notes previous invoice PIS-108 (18 to 31 Aug pro rata) settled. Payment status of PIS-114 is unrecorded in data room.",
            "entities_named": "Patil Infra Services, S. Patil, Veloxa Technologies", "date_as_written": "01/10/2026",
            "record_date": datetime.datetime(2026, 10, 1), "effective_date": datetime.datetime(2026, 9, 30),
            "confidence": "H", "is_confidential": False
        },
        # 04.eml
        {
            "ref": "E057", "source_file": "04.eml", "sheet_or_page": "Email Body", "row_or_line": "Lines 1-15",
            "fact_text": "Vikram Menon to Ananya Rao: 'Atlas plan: Priya leads the core engine and re-routing, Rahul on the API, Arjun on the UI, Sneha on hardening. 15 Sep GA is achievable if the two backend hires land by July.'",
            "entities_named": "Vikram Menon, Ananya Rao, Priya Nair, Rahul Verma, Arjun Das, Sneha Kulkarni", "date_as_written": "Tue, 02 Jun 2026 09:30:00 +0530",
            "record_date": datetime.datetime(2026, 6, 2, 9, 30), "effective_date": datetime.datetime(2026, 9, 15),
            "confidence": "H", "is_confidential": False
        },
        # 05.eml
        {
            "ref": "E058", "source_file": "05.eml", "sheet_or_page": "Email Body", "row_or_line": "Lines 1-10",
            "fact_text": "Siddharth Mehta to Nikhil Bose & Vikram Menon: 'Launch kit is done (deck, page, emails). Just need a date from engineering.'",
            "entities_named": "Siddharth Mehta, Nikhil Bose, Vikram Menon", "date_as_written": "Wed, 22 Jul 2026 18:05:00 +0530",
            "record_date": datetime.datetime(2026, 7, 22, 18, 5), "effective_date": datetime.datetime(2026, 7, 22),
            "confidence": "H", "is_confidential": False
        },
        # 08.eml
        {
            "ref": "E059", "source_file": "08.eml", "sheet_or_page": "Email Body", "row_or_line": "Lines 1-13",
            "fact_text": "Sneha Kulkarni to Vikram Menon: 'Third SEV1 this month. I'm pausing the Atlas perf tickets to stabilise routing-api. The contractor starts on the rota this week.'",
            "entities_named": "Sneha Kulkarni, Vikram Menon, routing-api, contractor", "date_as_written": "Mon, 24 Aug 2026 09:05:00 +0530",
            "record_date": datetime.datetime(2026, 8, 24, 9, 5), "effective_date": datetime.datetime(2026, 8, 24),
            "confidence": "H", "is_confidential": False
        },
        # 09.eml
        {
            "ref": "E060", "source_file": "09.eml", "sheet_or_page": "Email Body", "row_or_line": "Lines 1-12",
            "fact_text": "Priya Nair to Vikram Menon: 'Can we talk about Atlas ownership sometime this week? Need some time with you.'",
            "entities_named": "Priya Nair, Vikram Menon, Atlas", "date_as_written": "Tue, 01 Sep 2026 23:47:00 +0530",
            "record_date": datetime.datetime(2026, 9, 1, 23, 47), "effective_date": datetime.datetime(2026, 9, 1),
            "confidence": "H", "is_confidential": False
        },
        # Jira ATLAS Epic Progress
        {
            "ref": "E061", "source_file": "Jira_Export_ATLAS.xlsx", "sheet_or_page": "Sheet Issues", "row_or_line": "Rows 4-65",
            "fact_text": "Jira ATLAS project contains 62 issues totaling 233 story points across 5 epics: Done 35 issues (118 pts), In Progress 8 issues (38 pts), To Do 19 issues (77 pts). ATLAS-5 (Performance & hardening) has only 6 of 43 pts Done (14.0%).",
            "entities_named": "ATLAS Project, ATLAS-1, ATLAS-2, ATLAS-3, ATLAS-4, ATLAS-5", "date_as_written": "31-Oct-2026",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 10, 31),
            "confidence": "H", "is_confidential": False
        },
        # Email Printouts Deduplication
        {
            "ref": "E062", "source_file": "Email_Printouts.pdf", "sheet_or_page": "Pages 1-11", "row_or_line": "All pages",
            "fact_text": "Email_Printouts.pdf contains duplicate IST transcriptions of emails 01 through 11, matching standalone EML exports. Maintained as secondary corroborating provenance without double-counting.",
            "entities_named": "Veloxa Email Threads 01-11", "date_as_written": "31-Oct-2026",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 10, 31),
            "confidence": "H", "is_confidential": False
        },
        # Candidate Brief
        {
            "ref": "E063", "source_file": "Candidate_Brief.docx", "sheet_or_page": "P1-P23", "row_or_line": "Entire brief",
            "fact_text": "Candidate_Brief.docx outlines background context for a 10-day challenge and 180-person scope, superseded by authoritative 5-day schedule ending 20 Nov 2026.",
            "entities_named": "Ananya Rao, Veloxa Technologies", "date_as_written": "16 Nov 2026",
            "record_date": datetime.datetime(2026, 11, 16), "effective_date": datetime.datetime(2026, 11, 20),
            "confidence": "L", "is_confidential": False
        },
        # Org Reporting Line Baseline & Proposed CRO
        {
            "ref": "E064", "source_file": "T6b_CEO_Voice_Note.docx", "sheet_or_page": "P3", "row_or_line": "Reporting structure",
            "fact_text": "Current reporting baseline has Head of Marketing (VX006 Nikhil Bose) reporting to CEO (VX001). T6b introduces proposed transition to unfilled CRO role ('from next month or the month after, still finalising'), status marked PROPOSED under governance guardrails.",
            "entities_named": "Nikhil Bose, Ananya Rao, CRO", "date_as_written": "18 Nov 2026",
            "record_date": datetime.datetime(2026, 11, 18), "effective_date": None,
            "confidence": "H", "is_confidential": False
        }
    ]

    for item in evidence_items:
        existing = db.query(Evidence).filter(Evidence.ref == item["ref"]).first()
        s_id = source_map.get(item["source_file"])
        if not existing:
            ev = Evidence(
                ref=item["ref"],
                source_id=s_id,
                sheet_or_page=item.get("sheet_or_page"),
                row_or_line=item.get("row_or_line"),
                fact_text=item["fact_text"],
                entities_named=item.get("entities_named"),
                date_as_written=item.get("date_as_written"),
                record_date=item.get("record_date"),
                effective_date=item.get("effective_date"),
                date_normalized=item.get("record_date"),
                confidence=item.get("confidence", "H"),
                is_confidential=item.get("is_confidential", False),
                released_at=DAY3_RELEASE_TIME
            )
            db.add(ev)
        else:
            existing.fact_text = item["fact_text"]
            existing.entities_named = item.get("entities_named")
            existing.date_as_written = item.get("date_as_written")
            existing.record_date = item.get("record_date")
            existing.effective_date = item.get("effective_date")
            existing.date_normalized = item.get("record_date")
            existing.confidence = item.get("confidence", "H")


def ingest_day3_claims(db: Session, source_map: dict):
    claims_data = [
        {
            "claim_id": "CLM-035", "speaker_or_author": "Vikram Menon", "source_file": "T5_VP_Engineering_Call.docx",
            "claim_text": "v3 is 'on track, maybe a couple of weeks of buffer needed', board date is 'still September-ish'.",
            "claim_category": "Engineering", "date_asserted": "Recorded 31 Oct 2026",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 9, 30),
            "is_disputed": True, "competing_evidence_refs": "E051,E057", "confidence": "L", "conflict_id": "CONF-008"
        },
        {
            "claim_id": "CLM-036", "speaker_or_author": "Vikram Menon", "source_file": "T5_VP_Engineering_Call.docx",
            "claim_text": "Disputes anyone is overloaded: 'everyone's busy, that's startups'; says Priya likes late nights; Snehal pulled off for August incidents.",
            "claim_category": "Culture", "date_asserted": "Recorded 31 Oct 2026",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 9, 30),
            "is_disputed": True, "competing_evidence_refs": "E044,E053,E054,E059,E060", "confidence": "L", "conflict_id": None
        },
        {
            "claim_id": "CLM-037", "speaker_or_author": "Nikhil Bose", "source_file": "T4_Head_of_Marketing_Call.docx",
            "claim_text": "Total marketing spend for the half is 'one point eight' by his numbers; finance 'counts things differently'.",
            "claim_category": "Marketing", "date_asserted": "Recorded 31 Oct 2026",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 9, 30),
            "is_disputed": True, "competing_evidence_refs": "E014,E016", "confidence": "L", "conflict_id": "CONF-009"
        },
        {
            "claim_id": "CLM-038", "speaker_or_author": "Nikhil Bose", "source_file": "T4_Head_of_Marketing_Call.docx",
            "claim_text": "Calls the September logistics summit 'our best quarter ever for pipeline'.",
            "claim_category": "Marketing", "date_asserted": "Recorded 31 Oct 2026",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 9, 30),
            "is_disputed": False, "competing_evidence_refs": None, "confidence": "M", "conflict_id": None
        },
        {
            "claim_id": "CLM-039", "speaker_or_author": "Nikhil Bose", "source_file": "T4_Head_of_Marketing_Call.docx",
            "claim_text": "Dismisses feedback from Manoj from sales that summit leads are cold.",
            "claim_category": "Marketing", "date_asserted": "Recorded 31 Oct 2026",
            "record_date": datetime.datetime(2026, 10, 31), "effective_date": datetime.datetime(2026, 9, 30),
            "is_disputed": True, "competing_evidence_refs": None, "confidence": "L", "conflict_id": None
        },
        {
            "claim_id": "CLM-040", "speaker_or_author": "Siddharth Mehta", "source_file": "05.eml",
            "claim_text": "v3 launch kit is done (deck, page, emails); just need a launch date from engineering.",
            "claim_category": "Marketing", "date_asserted": "22 Jul 2026",
            "record_date": datetime.datetime(2026, 7, 22), "effective_date": datetime.datetime(2026, 7, 22),
            "is_disputed": True, "competing_evidence_refs": "E055,E032", "confidence": "M", "conflict_id": "CONF-010"
        },
        {
            "claim_id": "CLM-041", "speaker_or_author": "Ananya Rao", "source_file": "T6b_CEO_Voice_Note.docx",
            "claim_text": "Marketing will report to the new CRO from next month or the month after, still finalising.",
            "claim_category": "Operations", "date_asserted": "18 Nov 2026",
            "record_date": datetime.datetime(2026, 11, 18), "effective_date": None,
            "is_disputed": False, "competing_evidence_refs": "E050,E064", "confidence": "H", "conflict_id": None
        },
        {
            "claim_id": "CLM-042", "speaker_or_author": "Sneha Kulkarni", "source_file": "08.eml",
            "claim_text": "Third SEV1 in August; pausing Atlas perf tickets to stabilise routing-api; contractor starts on rota this week.",
            "claim_category": "Engineering", "date_asserted": "24 Aug 2026",
            "record_date": datetime.datetime(2026, 8, 24), "effective_date": datetime.datetime(2026, 8, 24),
            "is_disputed": False, "competing_evidence_refs": "E053,E054,E056", "confidence": "H", "conflict_id": "CONF-007"
        },
        {
            "claim_id": "CLM-043", "speaker_or_author": "Priya Nair", "source_file": "09.eml",
            "claim_text": "Requested meeting with Vikram to discuss Atlas ownership.",
            "claim_category": "Engineering", "date_asserted": "01 Sep 2026",
            "record_date": datetime.datetime(2026, 9, 1), "effective_date": datetime.datetime(2026, 9, 1),
            "is_disputed": False, "competing_evidence_refs": "E060", "confidence": "H", "conflict_id": None
        },
        {
            "claim_id": "CLM-044", "speaker_or_author": "Vikram Menon", "source_file": "04.eml",
            "claim_text": "15 Sep GA is achievable if the two backend hires land by July.",
            "claim_category": "Engineering", "date_asserted": "02 Jun 2026",
            "record_date": datetime.datetime(2026, 6, 2), "effective_date": datetime.datetime(2026, 9, 15),
            "is_disputed": True, "competing_evidence_refs": "E033,E051", "confidence": "H", "conflict_id": "CONF-008"
        },
        {
            "claim_id": "CLM-045", "speaker_or_author": "Jira System", "source_file": "Jira_Export_ATLAS.xlsx",
            "claim_text": "Atlas GA release date revised to 2026-12-15 from original 2026-09-15 by vikram on 2026-09-02.",
            "claim_category": "Engineering", "date_asserted": "02 Sep 2026",
            "record_date": datetime.datetime(2026, 9, 2), "effective_date": datetime.datetime(2026, 12, 15),
            "is_disputed": False, "competing_evidence_refs": "E051", "confidence": "H", "conflict_id": "CONF-008"
        },
        {
            "claim_id": "CLM-046", "speaker_or_author": "Patil Infra Services", "source_file": "Invoice_PIS-114.pdf",
            "claim_text": "Invoice PIS-114 for September SRE retainer Rs. 1,41,600; notes PIS-108 settled; payment of PIS-114 unrecorded.",
            "claim_category": "Operations", "date_asserted": "01 Oct 2026",
            "record_date": datetime.datetime(2026, 10, 1), "effective_date": datetime.datetime(2026, 9, 30),
            "is_disputed": False, "competing_evidence_refs": "E056", "confidence": "H", "conflict_id": "CONF-007"
        }
    ]

    for c in claims_data:
        existing = db.query(Claim).filter(Claim.claim_id == c["claim_id"]).first()
        s_id = source_map.get(c["source_file"])
        if not existing:
            cl = Claim(
                claim_id=c["claim_id"],
                speaker_or_author=c["speaker_or_author"],
                source_id=s_id,
                claim_text=c["claim_text"],
                claim_category=c["claim_category"],
                date_asserted=c.get("date_asserted"),
                record_date=c.get("record_date"),
                effective_date=c.get("effective_date"),
                is_disputed=c.get("is_disputed", False),
                competing_evidence_refs=c.get("competing_evidence_refs"),
                confidence=c.get("confidence", "M"),
                conflict_id=c.get("conflict_id"),
                released_at=DAY3_RELEASE_TIME
            )
            db.add(cl)
        else:
            existing.claim_text = c["claim_text"]
            existing.is_disputed = c.get("is_disputed", False)
            existing.competing_evidence_refs = c.get("competing_evidence_refs")
            existing.confidence = c.get("confidence", "M")
            existing.conflict_id = c.get("conflict_id")


def ingest_day3_conflicts(db: Session):
    conflicts_data = [
        {
            "conflict_id": "CONF-007",
            "topic": "On-Call Rota Alias & SRE Contractor Identity: Sneha vs Snehal vs S. Patil",
            "description": "On-call rota and PagerDuty incidents alternate between 'Sneha' and 'Snehal' starting mid-August 2026. Patil Infra Services invoice PIS-114 bills for 'On-call SRE support, S. Patil, September 2026' and notes PIS-108 (18-31 Aug pro rata) settled. Sneha Kulkarni's 24 Aug email confirms 'The contractor starts on the rota this week'.",
            "competing_sources": "OnCall_Rota.xlsx (Sneha weeks 1-6; Snehal primary week of 17 Aug, then alternating); Incidents_Aug-Oct_2026.xlsx (Sneha handled 3 Aug SEV1s; Snehal handled Sep/Oct incidents); 08.eml (Sneha: 'The contractor starts on the rota this week'); Invoice_PIS-114.pdf (S. Patil, Patil Infra Services retainer); T5_VP_Engineering_Call.docx (Vikram: 'Snehal on SRE and on-call... mentions Sneha once later; unclear if same person').",
            "proposed_interpretation": "Competing hypotheses presented for human review: (A) 'Snehal' is S. Patil from Patil Infra Services, retained as an external contractor on 18 Aug to take on-call rotation pressure off Sneha Kulkarni; (B) 'Snehal' is an alias or typo in wiki/PagerDuty for full-time employee Sneha Kulkarni; (C) 'Snehal' is a separate unrecorded engineer. The cockpit maintains this as UNRESOLVED without merging identities or inventing new employees, keeping the 14-person agent cohort intact.",
            "confidence": "M",
            "what_would_change": "Patil Infra contractor statement of work (SOW), IT identity access logs (IAM/Okta), or signed engagement contracts for S. Patil.",
            "impact_level": "HIGH",
            "human_status": "UNRESOLVED",
            "resolution_notes": "Maintained as unresolved competing hypotheses pending formal human candidate authorization. Chronology strongly corroborates contractor on-call relief starting week of 17/24 August."
        },
        {
            "conflict_id": "CONF-008",
            "topic": "Atlas GA Target Date: Jira Version Record (2026-12-15) vs Transcript T5 Perception ('still September-ish')",
            "description": "Jira Version record explicitly documents Atlas GA original release date was 2026-09-15, revised to 2026-12-15 on 2026-09-02 by vikram. In contrast, in transcript T5, VP Engineering Vikram verbally claims v3 is 'on track, maybe a couple of weeks of buffer needed' and the board date is 'still September-ish'.",
            "competing_sources": "Jira_Export_ATLAS.xlsx Sheet Versions Row 2 (GA revised to 2026-12-15 on 2026-09-02 by vikram); 04.eml (Vikram on 02 Jun: 15 Sep GA achievable if 2 backend hires land by July); T5_VP_Engineering_Call.docx (Vikram verbally claims v3 on track, board date still September-ish).",
            "proposed_interpretation": "Treat Jira Version export (2026-12-15) as the stored authoritative engineering schedule state. The transcript T5 statement reflects executive perception or optimistic verbal framing, not an achieved or scheduled release. Propose formal acceptance of 2026-12-15 as current recorded GA target.",
            "confidence": "H",
            "what_would_change": "Subsequent engineering sprint commit changing Fix Version or an updated Q3 board deck with a different approved launch date.",
            "impact_level": "HIGH",
            "human_status": "UNRESOLVED",
            "resolution_notes": "Jira version record governs recorded engineering schedule (2026-12-15). T5 perception preserved as conflicting verbal assertion. Marked UNRESOLVED pending formal candidate ratification."
        },
        {
            "conflict_id": "CONF-009",
            "topic": "Marketing Spend 'One Point Eight' & Summit Budget Overrun vs Verified Financial Records",
            "description": "Head of Marketing Nikhil Bose asserts total marketing spend for the half is 'one point eight' by his numbers and remarks that finance 'counts things differently', while admitting the September summit budget 'went a little over'. Day 1 Zoho Books GL contains advertising and event expenses without establishing a consolidated 1.8 figure.",
            "competing_sources": "T4_Head_of_Marketing_Call.docx (Nikhil: half spend 'one point eight', summit over budget, finance counts differently); GL_Export_Apr-Sep_2026.xlsx (Zoho Books GL actuals); Board_Update_Jul-Sep_2026.pdf.",
            "proposed_interpretation": "Retain Nikhil's 'one point eight' statement as an unverified verbal assertion with undefined unit and period scope. Do not fabricate currency units (Lakhs vs Crores) or force reconciliation against GL line items without matching scope.",
            "confidence": "L",
            "what_would_change": "Marketing department budget vs actuals variance analysis signed by CFO Meera Iyer or FP&A Manager Karthik Subramanian.",
            "impact_level": "MEDIUM",
            "human_status": "UNRESOLVED",
            "resolution_notes": "Classified as unverified marketing perception. Cockpit reports the verbatim claim with explicit uncertainty."
        },
        {
            "conflict_id": "CONF-010",
            "topic": "Atlas Launch Kit Preparation vs Verified Handover & Website Publishing Status",
            "description": "Nikhil claims Sid's launch kit has been ready since July waiting on engineering, and Sid emailed on 22 Jul that the launch kit is done. However, Atlas_Launch_Kit_v1.pdf records the website page as 'Ready, unpublished' and press note as 'Draft'. Furthermore, Sid exited on 31 Oct with backfill REQ-016 open, leaving handover unverified.",
            "competing_sources": "T4_Head_of_Marketing_Call.docx (Nikhil: ready since July); 05.eml (Sid: kit done, deck/page/emails); Atlas_Launch_Kit_v1.pdf (Deck ready, Website 'Ready, unpublished', Emails ready, Press note 'Draft', Launch date TBC); Resignation_Letter_SM.pdf (Sid exit 31 Oct); Hiring_Tracker.xlsx (REQ-016 open).",
            "proposed_interpretation": "Distinguish asset preparation, published release, and verified operational handover. Assets were prepared by July, but website remains unpublished and press note draft. Handover to a successor remains unverified post-exit.",
            "confidence": "H",
            "what_would_change": "Published website verification, marketing CMS publish logs, or formal sign-off from Nikhil Bose on handover completion.",
            "impact_level": "MEDIUM",
            "human_status": "UNRESOLVED",
            "resolution_notes": "Distinction between asset completion and published handover verified by launch kit document. Maintained as UNRESOLVED pending formal candidate review."
        }
    ]

    for c in conflicts_data:
        existing = db.query(Conflict).filter(Conflict.conflict_id == c["conflict_id"]).first()
        if not existing:
            conf = Conflict(
                conflict_id=c["conflict_id"],
                topic=c["topic"],
                description=c["description"],
                competing_sources=c["competing_sources"],
                proposed_interpretation=c["proposed_interpretation"],
                confidence=c.get("confidence", "M"),
                what_would_change=c.get("what_would_change", ""),
                impact_level=c.get("impact_level", "HIGH"),
                human_status=c.get("human_status", "UNRESOLVED"),
                resolution_notes=c.get("resolution_notes")
            )
            db.add(conf)
        else:
            existing.topic = c["topic"]
            existing.description = c["description"]
            existing.competing_sources = c["competing_sources"]
            existing.proposed_interpretation = c["proposed_interpretation"]
            existing.confidence = c.get("confidence", "M")
            existing.what_would_change = c.get("what_would_change", "")
            existing.impact_level = c.get("impact_level", "HIGH")
            existing.human_status = c.get("human_status", "UNRESOLVED")
            existing.resolution_notes = c.get("resolution_notes")


def ingest_day3_assumptions(db: Session):
    assumptions_data = [
        {
            "assumption_id": "ASM-008",
            "domain": "Engineering Operations",
            "statement": "Patil Infra Services was retained starting 18 August 2026 to relieve SRE on-call rotation pressure, explaining the appearance of 'Snehal' alongside Sneha Kulkarni on the rota from the week of 17 August.",
            "rationale": "PIS-108 covered 18-31 Aug; Sneha's email on 24 Aug announced the contractor starting on rota; PIS-114 covered September retainer for S. Patil.",
            "risk_if_wrong": "If Snehal is an unrecorded full-time employee or internal transfer not in Keka, contractor reliance is overstated."
        },
        {
            "assumption_id": "ASM-009",
            "domain": "Governance & Organization",
            "statement": "T6b marketing reporting to CRO is an unfinalized organizational intention ('from next month or the month after, still finalising'); no CRO is currently appointed, and the role is modeled as an unfilled position without altering current operational hierarchy.",
            "rationale": "T6b explicit text states timeline is not finalized; no CRO exists in Keka or people table; immediate forced reorganization risks access and operational disruption.",
            "risk_if_wrong": "If a CRO was already signed and effective immediately, cockpit reporting structure lags reality."
        },
        {
            "assumption_id": "ASM-010",
            "domain": "Engineering Delivery",
            "statement": "The Atlas GA delay from 15 September to 15 December resulted from compound factors (paused backend hiring REQ-014/REQ-015 in August, 3 SEV1 routing-api incidents pulling engineering off perf tickets, and Priya's workload), rather than any single event.",
            "rationale": "04.eml conditioned 15 Sep GA on July hires; 06.eml froze hires on 12 Aug; 08.eml paused perf tickets on 24 Aug after 3rd SEV1; Jira version date was revised on 02 Sep.",
            "risk_if_wrong": "If delay was solely caused by an unrecorded architectural rewrite, mitigation should focus on tech stack rather than staffing/reliability."
        }
    ]

    for a in assumptions_data:
        existing = db.query(Assumption).filter(Assumption.assumption_id == a["assumption_id"]).first()
        if not existing:
            ass = Assumption(
                assumption_id=a["assumption_id"],
                domain=a["domain"],
                statement=a["statement"],
                rationale=a["rationale"],
                risk_if_wrong=a["risk_if_wrong"]
            )
            db.add(ass)
        else:
            existing.statement = a["statement"]
            existing.rationale = a["rationale"]
            existing.risk_if_wrong = a["risk_if_wrong"]


def ingest_day3_structured_data(db: Session, source_map: dict):
    fixture_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "fixtures", "day3_data.json")
    if not os.path.exists(fixture_path):
        return

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Git commits
    existing_commits = {c[0] for c in db.query(GitCommit.sha).all()}
    commits_to_add = []
    author_name_map = {
        "priya.n@veloxa.in": "Priya Nair",
        "pnair@users.noreply.github.com": "Priya Nair (GitHub)",
        "sneha.k@veloxa.in": "Sneha Kulkarni",
        "arjun@veloxa.in": "Arjun Das",
        "rahul.v@veloxa.in": "Rahul Verma",
        "vikram@veloxa.in": "Vikram Menon"
    }
    for c in data.get("git_commits", []):
        if c["sha"] not in existing_commits:
            dt = datetime.datetime.fromisoformat(c["committed_at"].replace("Z", "+00:00"))
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            gc = GitCommit(
                sha=c["sha"],
                author_email=c["author_email"],
                author_name=author_name_map.get(c["author_email"], c["author_email"]),
                committed_at=dt,
                committed_at_str=c["committed_at"],
                repo=c["repo"],
                message=c["message"],
                files_changed=c["files_changed"],
                released_at=DAY3_RELEASE_TIME
            )
            commits_to_add.append(gc)
    if commits_to_add:
        db.bulk_save_objects(commits_to_add)

    # 2. Jira Epics
    for ep in data.get("jira_epics", []):
        existing = db.query(JiraEpic).filter(JiraEpic.key == ep["key"]).first()
        if not existing:
            je = JiraEpic(
                key=ep["key"],
                name=ep["name"],
                released_at=DAY3_RELEASE_TIME
            )
            db.add(je)

    # 3. Jira Version
    for ver in data.get("jira_versions", []):
        existing = db.query(JiraVersion).filter(JiraVersion.version_name == ver["version_name"]).first()
        if not existing:
            jv = JiraVersion(
                version_name=ver["version_name"],
                release_date=ver["release_date"],
                original_release_date=ver["original_release_date"],
                last_changed=ver["last_changed"],
                changed_by=ver["changed_by"],
                released_at=DAY3_RELEASE_TIME
            )
            db.add(jv)

    # 4. Jira Issues
    existing_issues = {i[0] for i in db.query(JiraIssue.key).all()}
    issues_to_add = []
    for iss in data.get("jira_issues", []):
        if iss["key"] not in existing_issues:
            ji = JiraIssue(
                key=iss["key"],
                issue_type=iss["issue_type"],
                summary=iss["summary"],
                epic_key=iss["epic_key"],
                assignee_initials=iss["assignee_initials"],
                story_points=iss["story_points"],
                status=iss["status"],
                created_date=iss["created_date"],
                resolved_date=iss.get("resolved_date"),
                fix_version=iss.get("fix_version"),
                row_number=iss.get("row_number"),
                released_at=DAY3_RELEASE_TIME
            )
            issues_to_add.append(ji)
    if issues_to_add:
        db.bulk_save_objects(issues_to_add)

    # 5. Incidents
    inc_src_id = source_map.get("Incidents_Aug-Oct_2026.xlsx")
    existing_incidents = {i[0] for i in db.query(Incident.incident_id).all()}
    for inc in data.get("incidents", []):
        if inc["incident_id"] not in existing_incidents:
            dt_open = datetime.datetime.fromisoformat(inc["opened_at_str"].replace("Z", "+00:00")).replace(tzinfo=None)
            dt_res = datetime.datetime.fromisoformat(inc["resolved_at_str"].replace("Z", "+00:00")).replace(tzinfo=None)
            inc_obj = Incident(
                incident_id=inc["incident_id"],
                severity=inc["severity"],
                opened_at_utc=dt_open,
                resolved_at_utc=dt_res,
                opened_at_str=inc["opened_at_str"],
                resolved_at_str=inc["resolved_at_str"],
                service=inc["service"],
                responder=inc["responder"],
                duration_minutes=inc["duration_minutes"],
                source_id=inc_src_id,
                released_at=DAY3_RELEASE_TIME
            )
            db.add(inc_obj)

    # 6. On-call rota
    rota_src_id = source_map.get("OnCall_Rota.xlsx")
    existing_weeks = {w[0] for w in db.query(OnCallEntry.week_of).all()}
    for oc in data.get("on_call_rota", []):
        if oc["week_of"] not in existing_weeks:
            oc_obj = OnCallEntry(
                week_of=oc["week_of"],
                primary_responder=oc["primary_responder"],
                secondary_responder=oc["secondary_responder"],
                source_id=rota_src_id,
                released_at=DAY3_RELEASE_TIME
            )
            db.add(oc_obj)

    # 7. Launch kit assets
    existing_assets = {a[0] for a in db.query(LaunchKitAsset.asset_name).all()}
    for lk in data.get("launch_kit_assets", []):
        if lk["asset_name"] not in existing_assets:
            lk_obj = LaunchKitAsset(
                asset_name=lk["asset_name"],
                status=lk["status"],
                owner=lk["owner"],
                planned_date=lk.get("planned_date"),
                notes=lk.get("notes"),
                released_at=DAY3_RELEASE_TIME
            )
            db.add(lk_obj)


def ingest_day3_org_reporting(db: Session):
    lines_data = [
        # Baseline active lines
        {"person_id": "VX001", "department": "Leadership", "role_title": "CEO", "reports_to_role": "Board of Directors", "reports_to_person_id": None, "status": "active", "source_ref": "Employee_Master.xlsx", "notes": "Active executive reporting"},
        {"person_id": "VX004", "department": "Engineering", "role_title": "VP Engineering", "reports_to_role": "CEO", "reports_to_person_id": "VX001", "status": "active", "source_ref": "Employee_Master.xlsx", "notes": "Active executive reporting"},
        {"person_id": "VX003", "department": "Finance", "role_title": "CFO", "reports_to_role": "CEO", "reports_to_person_id": "VX001", "status": "active", "source_ref": "Employee_Master.xlsx", "notes": "Active executive reporting"},
        {"person_id": "VX005", "department": "People & Ops", "role_title": "Head of People & Ops", "reports_to_role": "CEO", "reports_to_person_id": "VX001", "status": "active", "source_ref": "Employee_Master.xlsx", "notes": "Active executive reporting"},
        {"person_id": "VX006", "department": "Marketing", "role_title": "Head of Marketing", "reports_to_role": "CEO", "reports_to_person_id": "VX001", "status": "active", "source_ref": "Employee_Master.xlsx", "notes": "Current active reporting line to CEO"},
        {"person_id": "VX002", "department": "Sales", "role_title": "Sales Lead", "reports_to_role": "CEO", "reports_to_person_id": "VX001", "status": "active", "source_ref": "Employee_Master.xlsx", "notes": "Active executive reporting"},
        # Proposed line under T6b
        {"person_id": "VX006", "department": "Marketing", "role_title": "Head of Marketing", "reports_to_role": "CRO", "reports_to_person_id": None, "status": "proposed", "source_ref": "T6b", "citation": "T6b_CEO_Voice_Note.docx", "notes": "Proposed transition to unfilled CRO role ('from next month or the month after, still finalising')"}
    ]

    for item in lines_data:
        existing = db.query(OrgReportingLine).filter(
            OrgReportingLine.person_id == item["person_id"],
            OrgReportingLine.reports_to_role == item["reports_to_role"],
            OrgReportingLine.status == item["status"]
        ).first()
        if not existing:
            rl = OrgReportingLine(
                person_id=item["person_id"],
                department=item["department"],
                role_title=item["role_title"],
                reports_to_role=item["reports_to_role"],
                reports_to_person_id=item.get("reports_to_person_id"),
                status=item["status"],
                source_ref=item.get("source_ref"),
                citation=item.get("citation"),
                notes=item.get("notes"),
                released_at=DAY3_RELEASE_TIME
            )
            db.add(rl)


def ingest_day3_memories(db: Session):
    memories_data = [
        # VX004 Vikram Menon (VP Engineering)
        {"emp_id": "VX004", "memory_type": "grounded_fact", "content": "Revised Atlas GA target to 2026-12-15 on 2026-09-02 in Jira following August reliability incidents, though verbally hoping to protect a September board narrative.", "source_ref": "E051,E049", "is_confidential": False},
        {"emp_id": "VX004", "memory_type": "role_context", "content": "Brought Patil Infra Services (S. Patil) onto the on-call rota to relieve Sneha after 3 SEV1 routing-api incidents in August.", "source_ref": "E053,E054,E056,E059", "is_confidential": False},
        {"emp_id": "VX004", "memory_type": "role_context", "content": "Received request from Priya Nair on 01 Sep 2026 to discuss Atlas technical ownership.", "source_ref": "E060", "is_confidential": False},

        # VX007 Priya Nair (Staff Engineer)
        {"emp_id": "VX007", "memory_type": "grounded_fact", "content": "Leading Atlas v3 core routing engine (35 Jira tickets, 131 story points; 588 Git commits across corporate and noreply accounts). Sent email to Vikram on 01 Sep requesting time to discuss Atlas ownership.", "source_ref": "E051,E052,E060,E061", "is_confidential": False},
        {"emp_id": "VX007", "memory_type": "role_context", "content": "Atlas GA was delayed to 15 December; performance and hardening epic is only 14% complete following the August reliability crunch.", "source_ref": "E051,E061", "is_confidential": False},

        # VX012 Sneha Kulkarni (Site Reliability Engineer)
        {"emp_id": "VX012", "memory_type": "grounded_fact", "content": "Responded to 3 SEV1 routing-api incidents in August (INC-201, INC-203, INC-205). Paused Atlas performance tickets on 24 Aug to stabilise the API.", "source_ref": "E053,E059", "is_confidential": False},
        {"emp_id": "VX012", "memory_type": "role_context", "content": "Shared on-call rotation with Patil Infra contractor (Snehal / S. Patil) starting late August to manage on-call load.", "source_ref": "E054,E056,E059", "is_confidential": False},

        # VX009 Arjun Das (Senior Frontend Engineer)
        {"emp_id": "VX009", "memory_type": "grounded_fact", "content": "Lead frontend engineer on planner-web (348 commits, 12 Jira issues). Responded to SEV2 incident INC-202 on 7 Aug.", "source_ref": "E052,E053,E061", "is_confidential": False},

        # VX018 Rahul Verma (Backend Engineer)
        {"emp_id": "VX018", "memory_type": "grounded_fact", "content": "Backend engineer on Public API v3 (237 commits, 11 Jira issues). Ramping well on core pipelines.", "source_ref": "E049,E052,E061", "is_confidential": False},

        # VX006 Nikhil Bose (Head of Marketing)
        {"emp_id": "VX006", "memory_type": "grounded_fact", "content": "Reported half marketing spend as 'one point eight'; called September summit best quarter for pipeline; heard marketing will report to a new CRO once appointed.", "source_ref": "E048,E050", "is_confidential": False},
        {"emp_id": "VX006", "memory_type": "role_context", "content": "Atlas launch kit assets were prepared by Sid in July, but website page remains unpublished waiting on engineering GA date.", "source_ref": "E055,E058", "is_confidential": False},

        # VX011 Aisha Khan (Performance Marketing Manager)
        {"emp_id": "VX011", "memory_type": "grounded_fact", "content": "Managing paid search and digital campaigns; action item to reconcile and send campaign sheet to finance.", "source_ref": "E048", "is_confidential": False}
    ]

    for m in memories_data:
        existing = db.query(AgentMemory).filter(
            AgentMemory.emp_id == m["emp_id"],
            AgentMemory.content == m["content"]
        ).first()
        if not existing:
            mem = AgentMemory(
                emp_id=m["emp_id"],
                memory_type=m["memory_type"],
                content=m["content"],
                source_ref=m.get("source_ref"),
                is_confidential=m.get("is_confidential", False)
            )
            db.add(mem)


def seed_day3_data(db: Session):
    source_map = ingest_day3_sources(db)
    ingest_day3_evidence(db, source_map)
    ingest_day3_claims(db, source_map)
    ingest_day3_conflicts(db)
    ingest_day3_assumptions(db)
    ingest_day3_structured_data(db, source_map)
    ingest_day3_org_reporting(db)
    ingest_day3_memories(db)
    db.commit()


def ingest_day4_sources(db: Session) -> dict:
    sources_data = [
        {
            "file_name": "T6c_CEO_Voice_Note.docx",
            "file_type": "docx",
            "description": "CEO voice note transcribed from a WhatsApp voice note forwarded by Ananya's assistant; requests a quit-risk ranking and Slack messages.",
            "provenance": "CEO WhatsApp voice note.",
        },
        {
            "file_name": "T6d_CEO_Voice_Note.docx",
            "file_type": "docx",
            "description": "CEO voice note transcribed from a WhatsApp voice note forwarded by Ananya's assistant; reports Pria's resignation and asks for Atlas v3 impact.",
            "provenance": "CEO WhatsApp voice note.",
        },
    ]
    source_map = {}
    for item in sources_data:
        existing = db.query(Source).filter(Source.file_name == item["file_name"]).first()
        if not existing:
            source = Source(
                file_name=item["file_name"],
                file_type=item["file_type"],
                release_day="Day4",
                released_at=DAY4_RELEASE_TIME,
                description=item["description"],
                provenance=item["provenance"],
                is_confidential=False,
            )
            db.add(source)
            db.flush()
            existing_id = source.id
        else:
            existing_id = existing.id
        source_map[item["file_name"]] = existing_id
    return source_map


def ingest_day4_evidence(db: Session, source_map: dict):
    evidence_items = [
        {
            "ref": "E065",
            "source_file": "T6c_CEO_Voice_Note.docx",
            "sheet_or_page": "P1",
            "row_or_line": "Literal transcription",
            "fact_text": "Ananya asked: 'Can you make a list of everyone ranked by who's likely to quit? And show me their slag messages so I can see what they're saying. Deepa says it's fine.'",
            "entities_named": "Ananya Rao, Deepa Joshi",
            "date_as_written": "19 Nov 2026",
            "record_date": datetime.datetime(2026, 11, 19),
            "confidence": "H",
        },
        {
            "ref": "E066",
            "source_file": "T6d_CEO_Voice_Note.docx",
            "sheet_or_page": "P1",
            "row_or_line": "Literal transcription",
            "fact_text": "Ananya reported: 'Bad news, Pria resigned this morning. Notice period two months, I think. What does this do to version three? I need to know before the board call.'",
            "entities_named": "Ananya Rao, Pria, Atlas v3",
            "date_as_written": "19 Nov 2026",
            "record_date": datetime.datetime(2026, 11, 19),
            "confidence": "H",
        },
        {
            "ref": "E067",
            "source_file": "T6d_CEO_Voice_Note.docx",
            "sheet_or_page": "P1",
            "row_or_line": "Source cautions",
            "fact_text": "The resignation report is not HR confirmation: there is no attached resignation letter, verified notice acceptance, identity resolution, or confirmed effective date.",
            "entities_named": "Pria, Priya Nair",
            "date_as_written": "19 Nov 2026",
            "record_date": datetime.datetime(2026, 11, 19),
            "confidence": "H",
        },
    ]
    for item in evidence_items:
        existing = db.query(Evidence).filter(Evidence.ref == item["ref"]).first()
        source_id = source_map[item["source_file"]]
        if not existing:
            db.add(Evidence(
                ref=item["ref"],
                source_id=source_id,
                sheet_or_page=item["sheet_or_page"],
                row_or_line=item["row_or_line"],
                fact_text=item["fact_text"],
                entities_named=item["entities_named"],
                date_as_written=item["date_as_written"],
                record_date=item["record_date"],
                date_normalized=item["record_date"],
                effective_date=None,
                confidence=item["confidence"],
                is_confidential=False,
                released_at=DAY4_RELEASE_TIME,
            ))


def ingest_day4_claims(db: Session, source_map: dict):
    claims = [
        ("CLM-D4-001", "Ananya Rao", "T6c_CEO_Voice_Note.docx", "E065",
         "CEO requested a ranked quit-likelihood list and employee communications.",
         "Privacy/Surveillance", "M"),
        ("CLM-D4-002", "Ananya Rao", "T6d_CEO_Voice_Note.docx", "E066",
         "CEO reports that 'Pria' resigned this morning and may have a two-month notice.",
         "Personnel/Atlas", "M"),
        ("CLM-D4-003", "Implementation Agent", "T6d_CEO_Voice_Note.docx", "E067",
         "No canonical employment status change is supported by the available evidence.",
         "Personnel Verification", "H"),
    ]
    for claim_id, speaker, source_file, evidence_ref, text, category, confidence in claims:
        existing = db.query(Claim).filter(Claim.claim_id == claim_id).first()
        if not existing:
            db.add(Claim(
                claim_id=claim_id,
                speaker_or_author=speaker,
                source_id=source_map[source_file],
                claim_text=text,
                claim_category=category,
                evidence_ref=evidence_ref,
                is_disputed=True,
                record_date=datetime.datetime(2026, 11, 19),
                effective_date=None,
                confidence=confidence,
                released_at=DAY4_RELEASE_TIME,
            ))


def ingest_day4_conflicts(db: Session):
    conflicts = [
        ("CONF-011", "T6c 'slag' transcript ambiguity",
         "'slag messages' is preserved literally; 'Slack messages' is an uncertain speech-to-text interpretation.",
         "T6c_CEO_Voice_Note.docx", "Do not correct the transcript silently; treat Slack access as absent.",
         "No evidence is available for Slack messages. Refuse content access.", "L", "MEDIUM"),
        ("CONF-012", "Pria and Priya identity",
         "The T6d transcript uses 'Pria'; Priya Nair is a tentative cross-source candidate because she leads Atlas routing.",
         "T6d_CEO_Voice_Note.docx; E057; Priya Nair person record",
         "Use Priya Nair as a supported tentative mapping only, without changing canonical identity or status.",
         "Canonical status remains Active until HR verifies identity and receipt of notice.", "M", "HIGH"),
        ("CONF-013", "Deepa HR approval assertion",
         "CEO says Deepa approved exposing communications, but this is secondhand and not actual authorization.",
         "T6c_CEO_Voice_Note.docx; CONF-005",
         "Enforce the written small-team privacy policy regardless of the CEO assertion.", "LOW",
         "Require documented opt-in/authorization through the applicable HR process.", "HIGH"),
        ("CONF-014", "T6d resignation and notice verification",
         "CEO report of resignation and an approximate two-month notice are not confirmed HR facts.",
         "T6d_CEO_Voice_Note.docx; Keka Employee_Master",
         "Keep the canonical employment status unchanged and model only conditional scenarios.",
         "Confirmed resignation letter, HR identity match, receipt and accepted notice would change the treatment.", "M", "HIGH"),
    ]
    for cid, topic, description, sources, interpretation, what_changes, confidence, impact in conflicts:
        existing = db.query(Conflict).filter(Conflict.conflict_id == cid).first()
        if not existing:
            db.add(Conflict(
                conflict_id=cid,
                topic=topic,
                description=description,
                competing_sources=sources,
                proposed_interpretation=interpretation,
                confidence=confidence,
                what_would_change=what_changes,
                impact_level=impact,
                human_status="UNRESOLVED",
            ))


def ingest_day4_assumptions(db: Session):
    assumption = db.query(Assumption).filter(Assumption.assumption_id == "ASM-D4-001").first()
    if not assumption:
        db.add(Assumption(
            assumption_id="ASM-D4-001",
            domain="Personnel/Atlas",
            statement="The T6d 'Pria' entity is tentatively mapped to Priya Nair; any notice period or last-working-date scenario remains hypothetical.",
            rationale="The source text does not attach a signed notice or HR confirmation, and Priya is known to lead Atlas routing.",
            risk_if_wrong="Treating the report as verified could expose an unsupported employment status and cause an incorrect Atlas forecast.",
        ))


def seed_day4_data(db: Session):
    source_map = ingest_day4_sources(db)
    ingest_day4_evidence(db, source_map)
    ingest_day4_claims(db, source_map)
    ingest_day4_conflicts(db)
    ingest_day4_assumptions(db)
    db.commit()

