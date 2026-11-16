"""
Deterministic Day 1 Ingestion Engine.
Loads structured seed data extracted from Day 1 text room with exact row/column references.
Ensures idempotency and testability.
"""
import datetime
from sqlalchemy.orm import Session
from backend.app.models.schema import Source, Evidence, Claim, Person, Conflict, Assumption, AgentMemory

DAY1_RELEASE_TIME = datetime.datetime(2026, 11, 16, 10, 0, 0)

def seed_day1_data(db: Session):
    # Check if already seeded
    if db.query(Source).count() > 0:
        return

    # 1. Sources
    sources_data = [
        {"file_name": "README.txt", "file_type": "txt", "description": "Veloxa data room export manifest as of 31 Oct 2026.", "provenance": "Exported by IT on 31 Oct 2026."},
        {"file_name": "T1_CEO_Kickoff_Call.docx", "file_type": "docx", "description": "MeetNotes AI auto-summary of CEO Ananya Rao kickoff call (38 min, fair audio).", "provenance": "Executive interview transcript."},
        {"file_name": "T2_CFO_Call.docx", "file_type": "docx", "description": "MeetNotes AI auto-summary of CFO Meera Iyer call (26 min, poor speakerphone audio).", "provenance": "Executive interview transcript."},
        {"file_name": "Board_Update_Apr-Jun_2026.pdf", "file_type": "pdf", "description": "Q1 FY27 Quarterly update sent 8 Jul 2026.", "provenance": "Formal board report."},
        {"file_name": "Board_Update_Jul-Sep_2026.pdf", "file_type": "pdf", "description": "Q2 FY27 Quarterly update sent 6 Oct 2026.", "provenance": "Formal board report."},
        {"file_name": "01.eml", "file_type": "eml", "description": "Email from Karthik Subramanian to Meera Iyer re: Feb payroll done.", "provenance": "Email server export (2026-02-28 20:15 IST)."},
        {"file_name": "02.eml", "file_type": "eml", "description": "Email from Rahul Verma to Fatima Sheikh re: payslip query.", "provenance": "Email server export (2026-03-06 11:02 IST)."},
        {"file_name": "03.eml", "file_type": "eml", "description": "Email from Fatima Sheikh to Rahul Verma re: Re: payslip query.", "provenance": "Email server export (2026-03-10 15:40 IST)."},
        {"file_name": "Employee_Master.xlsx", "file_type": "xlsx", "description": "Keka HRMS export, employees only (19 headcount), exported 31-Oct-2026.", "provenance": "HRMS primary export."},
        {"file_name": "GL_Export_Apr-Sep_2026.xlsx", "file_type": "xlsx", "description": "General ledger export, Zoho Books, Apr to Sep 2026 (selected cost centres).", "provenance": "Zoho Books export."},
        {"file_name": "Payroll_Register_Jan-Mar_2026.xlsx", "file_type": "xlsx", "description": "Payroll register, Jan to Mar 2026 from pre-Keka payroll workbook.", "provenance": "Finance payroll workbook.", "is_confidential": True},
        {"file_name": "Connection_Worksheet.pdf", "file_type": "pdf", "description": "Connection worksheet template for chain-of-evidence synthesis.", "provenance": "Assessment template."},
    ]

    source_map = {}
    for s_dict in sources_data:
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

    # 2. Employees (People)
    employees_data = [
        {"emp_id": "VX001", "full_name": "Ananya Rao", "work_email": "ananya@veloxa.in", "department": "Leadership", "title": "CEO", "manager_id": None, "join_date": "2019-04-01", "location": "Bengaluru", "status": "Active", "system_role_desc": "Founder & CEO, macro focused, relies on verbal summaries."},
        {"emp_id": "VX002", "full_name": "Manoj Kumar", "work_email": "manoj@veloxa.in", "department": "Sales", "title": "Sales Lead", "manager_id": "VX001", "join_date": "2020-01-06", "location": "Bengaluru", "status": "Active", "system_role_desc": "Enterprise sales lead."},
        {"emp_id": "VX003", "full_name": "Meera Iyer", "work_email": "meera@veloxa.in", "department": "Finance", "title": "CFO", "manager_id": "VX001", "join_date": "2023-06-12", "location": "Bengaluru", "status": "Active", "system_role_desc": "CFO, strict confidentiality guardian, runs Zoho Books and Keka."},
        {"emp_id": "VX004", "full_name": "Vikram Menon", "work_email": "vikram@veloxa.in", "department": "Engineering", "title": "VP Engineering", "manager_id": "VX001", "join_date": "2021-02-01", "location": "Bengaluru", "status": "Active", "system_role_desc": "VP Engineering, managing Atlas v3 routing engine."},
        {"emp_id": "VX005", "full_name": "Deepa Joshi", "work_email": "deepa@veloxa.in", "department": "People & Ops", "title": "Head of People & Ops", "manager_id": "VX001", "join_date": "2022-07-04", "location": "Bengaluru", "status": "Active", "system_role_desc": "Head of HR and operations."},
        {"emp_id": "VX006", "full_name": "Nikhil Bose", "work_email": "nikhil@veloxa.in", "department": "Marketing", "title": "Head of Marketing", "manager_id": "VX001", "join_date": "2024-09-02", "location": "Bengaluru", "status": "Active", "system_role_desc": "Head of Marketing, organized Logistics Summit."},
        {"emp_id": "VX007", "full_name": "Priya Nair", "work_email": "priya.n@veloxa.in", "department": "Engineering", "title": "Staff Engineer", "manager_id": "VX004", "join_date": "2022-03-14", "location": "Bengaluru", "status": "Active", "system_role_desc": "Core routing engine architect, key-person dependency."},
        {"emp_id": "VX008", "full_name": "Divya Reddy", "work_email": "divya@veloxa.in", "department": "Sales", "title": "Account Executive", "manager_id": "VX002", "join_date": "2024-01-15", "location": "Hyderabad", "status": "Active", "system_role_desc": "Sales AE based in Hyderabad."},
        {"emp_id": "VX009", "full_name": "Arjun Das", "work_email": "arjun@veloxa.in", "department": "Engineering", "title": "Senior Frontend Engineer", "manager_id": "VX004", "join_date": "2023-05-08", "location": "Pune (remote)", "status": "Active", "system_role_desc": "Frontend engineer working remotely from Pune."},
        {"emp_id": "VX010", "full_name": "Karthik Subramanian", "work_email": "karthik.s@veloxa.in", "department": "Finance", "title": "FP&A Manager", "manager_id": "VX003", "join_date": "2024-10-01", "location": "Bengaluru", "status": "Active", "system_role_desc": "FP&A manager, studying for CFA, processed Feb 2026 payroll."},
        {"emp_id": "VX011", "full_name": "Aisha Khan", "work_email": "aisha@veloxa.in", "department": "Marketing", "title": "Performance Marketing Manager", "manager_id": "VX006", "join_date": "2023-08-21", "location": "Bengaluru", "status": "Active", "system_role_desc": "Manages Google Ads campaigns."},
        {"emp_id": "VX012", "full_name": "Sneha Kulkarni", "work_email": "sneha.k@veloxa.in", "department": "Engineering", "title": "Site Reliability Engineer", "manager_id": "VX004", "join_date": "2024-11-04", "location": "Bengaluru", "status": "Active", "system_role_desc": "SRE managing AWS infrastructure and reliability."},
        {"emp_id": "VX013", "full_name": "Siddharth Mehta", "work_email": "sid@veloxa.in", "department": "Marketing", "title": "Product Marketing Manager", "manager_id": "VX006", "join_date": "2025-04-07", "location": "Bengaluru", "status": "Notice period", "exit_date": "2026-10-31", "system_role_desc": "Product marketing manager exiting 31 Oct 2026."},
        {"emp_id": "VX014", "full_name": "Fatima Sheikh", "work_email": "fatima@veloxa.in", "department": "Finance", "title": "Accounts & Payroll Executive", "manager_id": "VX003", "join_date": "2025-05-12", "location": "Bengaluru", "status": "Active", "system_role_desc": "Accounts and payroll executive, on wedding leave in Feb 2026."},
        {"emp_id": "VX015", "full_name": "Rohan Banerjee", "work_email": "rohan@veloxa.in", "department": "People & Ops", "title": "Talent Partner", "manager_id": "VX005", "join_date": "2024-06-03", "location": "Kolkata (remote)", "status": "Active", "system_role_desc": "Recruiting talent partner based remotely in Kolkata."},
        {"emp_id": "VX016", "full_name": "Imran Siddiqui", "work_email": "imran@veloxa.in", "department": "Support", "title": "Customer Support Lead", "manager_id": "VX001", "join_date": "2023-02-13", "location": "Bengaluru", "status": "Active", "system_role_desc": "Customer support lead."},
        {"emp_id": "VX017", "full_name": "Lakshmi Pillai", "work_email": "lakshmi.p@veloxa.in", "department": "People & Ops", "title": "HR & Office Executive", "manager_id": "VX005", "join_date": "2025-10-06", "location": "Bengaluru", "status": "Active", "system_role_desc": "HR & office coordinator."},
        {"emp_id": "VX018", "full_name": "Rahul Verma", "work_email": "rahul.v@veloxa.in", "department": "Engineering", "title": "Backend Engineer", "manager_id": "VX004", "join_date": "2026-02-03", "location": "Bengaluru", "status": "Active", "system_role_desc": "Junior backend engineer hired Feb 2026; questioned first payslip."},
        {"emp_id": "VX019", "full_name": "Kavya Narayan", "work_email": "kavya@veloxa.in", "department": "Support", "title": "Support Associate", "manager_id": "VX016", "join_date": "2025-07-01", "location": "Bengaluru", "status": "Active", "system_role_desc": "Support associate."},
    ]

    for emp in employees_data:
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

    # 3. Evidence Index (Facts)
    evidence_items = [
        # Board Update Apr-Jun
        {"ref": "E001", "source_file": "Board_Update_Apr-Jun_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Key numbers", "fact_text": "ARR (recurring) is Rs. 5.8 Cr as of Period Apr to Jun 2026.", "entities_named": "Veloxa Technologies, Board", "date_as_written": "Sent 8 Jul 2026", "date_normalized": datetime.datetime(2026, 7, 8), "confidence": "H"},
        {"ref": "E002", "source_file": "Board_Update_Apr-Jun_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Key numbers", "fact_text": "Customer count is 61; Team headcount is 19 as of Q1 2026.", "entities_named": "Veloxa Technologies", "date_as_written": "Sent 8 Jul 2026", "date_normalized": datetime.datetime(2026, 7, 8), "confidence": "H"},
        {"ref": "E003", "source_file": "Board_Update_Apr-Jun_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Key numbers", "fact_text": "Monthly burn is Rs. 46 L; Runway is 14 months as of Q1 2026.", "entities_named": "Veloxa Technologies", "date_as_written": "Sent 8 Jul 2026", "date_normalized": datetime.datetime(2026, 7, 8), "confidence": "H"},
        {"ref": "E004", "source_file": "Board_Update_Apr-Jun_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Product", "fact_text": "Atlas (routing engine v3) is on track for GA on 15 September; Real-time re-routing is headline feature.", "entities_named": "Atlas v3", "date_as_written": "Sent 8 Jul 2026", "date_normalized": datetime.datetime(2026, 7, 8), "confidence": "H"},
        {"ref": "E005", "source_file": "Board_Update_Apr-Jun_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Team", "fact_text": "Veloxa planned to add two backend engineers in Q2 to de-risk Atlas with search underway.", "entities_named": "Engineering Team, Atlas", "date_as_written": "Sent 8 Jul 2026", "date_normalized": datetime.datetime(2026, 7, 8), "confidence": "H"},
        
        # Board Update Jul-Sep
        {"ref": "E006", "source_file": "Board_Update_Jul-Sep_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Key numbers", "fact_text": "ARR (recurring) is Rs. 6.1 Cr; Customers reached 66; Team headcount is 19 as of Period Jul to Sep 2026.", "entities_named": "Veloxa Technologies", "date_as_written": "Sent 6 Oct 2026", "date_normalized": datetime.datetime(2026, 10, 6), "confidence": "H"},
        {"ref": "E007", "source_file": "Board_Update_Jul-Sep_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Key numbers", "fact_text": "Monthly burn is Rs. 44 L; Runway is 13 months as of Q2 2026.", "entities_named": "Veloxa Technologies", "date_as_written": "Sent 6 Oct 2026", "date_normalized": datetime.datetime(2026, 10, 6), "confidence": "H"},
        {"ref": "E008", "source_file": "Board_Update_Jul-Sep_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Product", "fact_text": "Atlas GA was moved to absorb unplanned reliability work after a difficult August; engine itself is feature-complete.", "entities_named": "Atlas v3", "date_as_written": "Sent 6 Oct 2026", "date_normalized": datetime.datetime(2026, 10, 6), "confidence": "H"},
        {"ref": "E009", "source_file": "Board_Update_Jul-Sep_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Team", "fact_text": "Hiring is paused while closing the round; One planned departure in marketing.", "entities_named": "Team, Siddharth Mehta", "date_as_written": "Sent 6 Oct 2026", "date_normalized": datetime.datetime(2026, 10, 6), "confidence": "H"},
        {"ref": "E010", "source_file": "Board_Update_Jul-Sep_2026.pdf", "sheet_or_page": "Page 1", "row_or_line": "Marketing", "fact_text": "Logistics Summit drew 212 registrations, largest event yet.", "entities_named": "Logistics Summit", "date_as_written": "Sent 6 Oct 2026", "date_normalized": datetime.datetime(2026, 10, 6), "confidence": "H"},

        # GL Export (Selected major operational items)
        {"ref": "E011", "source_file": "GL_Export_Apr-Sep_2026.xlsx", "sheet_or_page": "GL Apr-Sep", "row_or_line": "Row 5, 9, 13, 18, 22, 30", "fact_text": "Monthly payroll disbursement is fixed at exactly Rs. 31,75,000 for each month from April to September 2026.", "entities_named": "Salaries (payroll), FS", "date_as_written": "Apr-Sep 2026", "date_normalized": datetime.datetime(2026, 9, 28), "confidence": "H"},
        {"ref": "E012", "source_file": "GL_Export_Apr-Sep_2026.xlsx", "sheet_or_page": "GL Apr-Sep", "row_or_line": "Row 6, 10, 14, 19, 24, 31", "fact_text": "WeWork India office rent is Rs. 2,36,000 per month consistently from Apr to Sep 2026.", "entities_named": "WeWork India, FS", "date_as_written": "Apr-Sep 2026", "date_normalized": datetime.datetime(2026, 9, 30), "confidence": "H"},
        {"ref": "E013", "source_file": "GL_Export_Apr-Sep_2026.xlsx", "sheet_or_page": "GL Apr-Sep", "row_or_line": "Row 4, 8, 12, 17, 21, 28", "fact_text": "AWS infrastructure cost escalated from Rs. 1,81,200 in April to Rs. 2,48,310 in September 2026.", "entities_named": "Amazon Web Services, FS", "date_as_written": "Apr-Sep 2026", "date_normalized": datetime.datetime(2026, 9, 8), "confidence": "H"},
        {"ref": "E014", "source_file": "GL_Export_Apr-Sep_2026.xlsx", "sheet_or_page": "GL Apr-Sep", "row_or_line": "Row 15", "fact_text": "Cohere Recruiting Partners was paid Rs. 1,77,000 on 2026-06-30 as 50% advance for 2 backend roles (JV-0688, Ref CRP-0412).", "entities_named": "Cohere Recruiting Partners, FS", "date_as_written": "2026-06-30", "date_normalized": datetime.datetime(2026, 6, 30), "confidence": "H"},
        {"ref": "E015", "source_file": "GL_Export_Apr-Sep_2026.xlsx", "sheet_or_page": "GL Apr-Sep", "row_or_line": "Row 25", "fact_text": "Patil Infra Services was paid Rs. 70,800 on 2026-09-02 for on-call support during 18-31 Aug (JV-0902, Ref PIS-108).", "entities_named": "Patil Infra Services, FS", "date_as_written": "2026-09-02", "date_normalized": datetime.datetime(2026, 9, 2), "confidence": "H"},
        {"ref": "E016", "source_file": "GL_Export_Apr-Sep_2026.xlsx", "sheet_or_page": "GL Apr-Sep", "row_or_line": "Row 23, 26", "fact_text": "Sapphire Events & Saphire Event Mgmt were paid Rs. 5,42,800 (venue, AV) and Rs. 4,60,200 (catering) totaling Rs. 10,03,000 for Summit.", "entities_named": "Sapphire Events, Nikhil Bose", "date_as_written": "2026-08-29, 2026-09-03", "date_normalized": datetime.datetime(2026, 9, 3), "confidence": "H"},

        # Emails (Payroll & Personnel)
        {"ref": "E017", "source_file": "01.eml", "sheet_or_page": "Email", "row_or_line": "Headers & Body", "fact_text": "Karthik Subramanian ran Feb payroll using Jan sheet and added new joiner because Fatima Sheikh was out.", "entities_named": "Karthik Subramanian, Meera Iyer, Fatima Sheikh", "date_as_written": "Sat, 28 Feb 2026 20:15:00 +0530", "date_normalized": datetime.datetime(2026, 2, 28, 20, 15), "confidence": "H"},
        {"ref": "E018", "source_file": "02.eml", "sheet_or_page": "Email", "row_or_line": "Headers & Body", "fact_text": "Rahul Verma inquired with Fatima Sheikh noting his first payslip amount looked higher than expected for a partial month.", "entities_named": "Rahul Verma, Fatima Sheikh", "date_as_written": "Fri, 06 Mar 2026 11:02:00 +0530", "date_normalized": datetime.datetime(2026, 3, 6, 11, 2), "confidence": "H"},
        {"ref": "E019", "source_file": "03.eml", "sheet_or_page": "Email", "row_or_line": "Headers & Body", "fact_text": "Fatima Sheikh replied to Rahul Verma promising to check and get back on his payslip discrepancy.", "entities_named": "Fatima Sheikh, Rahul Verma", "date_as_written": "Tue, 10 Mar 2026 15:40:00 +0530", "date_normalized": datetime.datetime(2026, 3, 10, 15, 40), "confidence": "H"},

        # Employee Master Summary
        {"ref": "E020", "source_file": "Employee_Master.xlsx", "sheet_or_page": "Employees", "row_or_line": "Row 1, Row 3-22", "fact_text": "Keka HRMS lists exactly 19 employees as of 31-Oct-2026; note explicitly confirms contractors are excluded from Keka.", "entities_named": "Keka HRMS, Veloxa", "date_as_written": "31-Oct-2026", "date_normalized": datetime.datetime(2026, 10, 31), "confidence": "H"},
        {"ref": "E021", "source_file": "Employee_Master.xlsx", "sheet_or_page": "Employees", "row_or_line": "Row 16", "fact_text": "Siddharth Mehta (Product Marketing Manager) is on notice period with exit date 2026-10-31.", "entities_named": "Siddharth Mehta, Nikhil Bose", "date_as_written": "2026-10-31", "date_normalized": datetime.datetime(2026, 10, 31), "confidence": "H"},
        {"ref": "E022", "source_file": "Employee_Master.xlsx", "sheet_or_page": "Employees", "row_or_line": "Row 21", "fact_text": "Rahul Verma joined as Backend Engineer on 2026-02-03 reporting to Vikram Menon.", "entities_named": "Rahul Verma, Vikram Menon", "date_as_written": "2026-02-03", "date_normalized": datetime.datetime(2026, 2, 3), "confidence": "H"},

        # Payroll Register (Confidential figures aggregated/redacted for executive view)
        {"ref": "E023", "source_file": "Payroll_Register_Jan-Mar_2026.xlsx", "sheet_or_page": "Payroll Q4", "row_or_line": "Row 39", "fact_text": "Rahul Verma Feb-2026 payroll record lists Days in Month: 28, Days Payable: 28 with full monthly gross credited despite joining on Feb 3.", "entities_named": "Rahul Verma, Karthik Subramanian", "date_as_written": "Feb-2026", "date_normalized": datetime.datetime(2026, 2, 28), "confidence": "H", "is_confidential": True},
        {"ref": "E024", "source_file": "Payroll_Register_Jan-Mar_2026.xlsx", "sheet_or_page": "Payroll Q4", "row_or_line": "Row 58", "fact_text": "Rahul Verma Mar-2026 payroll record lists Days Payable: 31 with full monthly gross and zero recovery or adjustment.", "entities_named": "Rahul Verma, Fatima Sheikh", "date_as_written": "Mar-2026", "date_normalized": datetime.datetime(2026, 3, 31), "confidence": "H", "is_confidential": True},
        
        # T1 & T2 Transcript Evidence
        {"ref": "E025", "source_file": "T1_CEO_Kickoff_Call.docx", "sheet_or_page": "Transcript", "row_or_line": "Summary", "fact_text": "CEO Ananya claimed ARR is around 42 crore, maybe 45 now and company is roughly 18 people ('one-eighty, give or take').", "entities_named": "Ananya Rao", "date_as_written": "Kickoff Call", "date_normalized": datetime.datetime(2026, 11, 1), "confidence": "M"},
        {"ref": "E026", "source_file": "T1_CEO_Kickoff_Call.docx", "sheet_or_page": "Transcript", "row_or_line": "Key points", "fact_text": "CEO stated burn is around two point two (unit unstated) and expressed fear Atlas v3 will miss festive season.", "entities_named": "Ananya Rao, Vikram Menon, Priya Nair", "date_as_written": "Kickoff Call", "date_normalized": datetime.datetime(2026, 11, 1), "confidence": "M"},
        {"ref": "E027", "source_file": "T2_CFO_Call.docx", "sheet_or_page": "Transcript", "row_or_line": "Summary & Key points", "fact_text": "CFO Meera stated ARR was forty-eight at start of year, burn is 2.2 to 2.5 lakhs a month, and mandated individual salaries must NEVER show up to Ananya.", "entities_named": "Meera Iyer, Ananya Rao", "date_as_written": "CFO Call", "date_normalized": datetime.datetime(2026, 11, 2), "confidence": "M"},
    ]

    for item in evidence_items:
        e = Evidence(
            ref=item["ref"],
            source_id=source_map[item["source_file"]],
            sheet_or_page=item.get("sheet_or_page"),
            row_or_line=item.get("row_or_line"),
            fact_text=item["fact_text"],
            entities_named=item.get("entities_named"),
            date_as_written=item.get("date_as_written"),
            date_normalized=item.get("date_normalized"),
            confidence=item.get("confidence", "H"),
            is_confidential=item.get("is_confidential", False),
            released_at=DAY1_RELEASE_TIME
        )
        db.add(e)

    # 4. Documented Source Conflicts
    conflicts_data = [
        {
            "conflict_id": "CONF-001",
            "topic": "Annual Recurring Revenue (ARR) Discrepancy",
            "description": "Board updates report ARR of Rs. 5.8 Cr (Jun 2026) and Rs. 6.1 Cr (Sep 2026). CEO Ananya claims ARR is 'around forty-two crore, maybe forty-five now' (T1). CFO Meera refers to ARR as 'forty-eight' (T2).",
            "competing_sources": "Board_Update_Apr-Jun_2026.pdf (E001), Board_Update_Jul-Sep_2026.pdf (E006) VS T1_CEO_Kickoff_Call.docx (E025), T2_CFO_Call.docx (E027)",
            "proposed_interpretation": "Board reporting (Rs. 6.1 Cr) is the audited SaaS subscription recurring revenue. CEO is likely quoting platform Gross Merchandise Value (GMV) / contract pipeline or valuation, or confused Lakhs/Crores. CFO 'forty-eight' may refer to Rs. 4.8 Cr (48 Lakhs x 10 or FY26 closing).",
            "confidence": "M",
            "what_would_change": "Audited FY26 P&L statements, customer contracts schedule, or clarification interview with CFO/CEO.",
            "impact_level": "HIGH",
            "human_status": "UNRESOLVED",
        },
        {
            "conflict_id": "CONF-002",
            "topic": "Monthly Burn Rate Discrepancy",
            "description": "Board updates report Monthly Burn of Rs. 46 L (Q1) and Rs. 44 L (Q2). General ledger confirms monthly payroll alone is Rs. 31.75 L plus rent and cloud totaling >Rs. 36-45 L/mo. Conversely, CFO claims burn is 'two point two lakhs a month, sometimes two point five' and CEO echoes 'around two point two'.",
            "competing_sources": "Board_Update_Apr-Jun_2026.pdf (E003), Board_Update_Jul-Sep_2026.pdf (E007), GL_Export_Apr-Sep_2026.xlsx (E011-E013) VS T2_CFO_Call.docx (E027), T1_CEO_Kickoff_Call.docx (E026)",
            "proposed_interpretation": "Gross cash burn is Rs. 44-46 L/month. The CFO's statement of '2.2 to 2.5 lakhs' likely reflects NET burn (Gross Outflow ~Rs. 53 L minus Monthly Inflow ~Rs. 50.8 L from 6.1 Cr ARR = ~Rs. 2.2 L net deficit), or an acoustic transcription truncation of 'forty-two point five'.",
            "confidence": "M",
            "what_would_change": "Monthly bank cash flow statements, collections ledger, or CFO verbal clarification.",
            "impact_level": "HIGH",
            "human_status": "UNRESOLVED",
        },
        {
            "conflict_id": "CONF-003",
            "topic": "Company Headcount & Keka Scope",
            "description": "CEO states company is 'roughly eighteen people ('one-eighty, give or take')'. Employee Master lists exactly 19 employees. Board update lists 19.",
            "competing_sources": "Employee_Master.xlsx (E020), Board_Update_Jul-Sep_2026.pdf (E006) VS T1_CEO_Kickoff_Call.docx (E025)",
            "proposed_interpretation": "Official full-time employee headcount is 19 (18 active + 1 notice period). MeetNotes AI acoustic mishearing distorted 'eighteen' into 'one-eighty', or CEO included non-Keka contractors and third-party warehouse/field associates.",
            "confidence": "H",
            "what_would_change": "Contractor / vendor service agreements and Culture Amp survey participant count.",
            "impact_level": "MEDIUM",
            "human_status": "UNRESOLVED",
        },
        {
            "conflict_id": "CONF-004",
            "topic": "Rahul Verma Feb 2026 Payroll Calculation Error",
            "description": "Rahul Verma joined 2026-02-03 (26 of 28 payable days). Feb payroll credited full 28 days. Rahul flagged to Fatima on 06 Mar. Fatima promised to check, but March payroll paid full month with no clawback.",
            "competing_sources": "01.eml (E017), 02.eml (E018), 03.eml (E019), Payroll_Register_Jan-Mar_2026.xlsx (E023, E024), Employee_Master.xlsx (E022)",
            "proposed_interpretation": "Fatima's absence for her wedding led Karthik to copy January's sheet and add Rahul without pro-rating partial month days (26/28). Discrepancy acknowledged by Fatima but never reconciled.",
            "confidence": "H",
            "what_would_change": "Fatima's reconciliation notes or April payroll adjustments in Keka module.",
            "impact_level": "LOW",
            "human_status": "UNRESOLVED",
        }
    ]

    for c in conflicts_data:
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

    # 5. Grounded Agent Memories (Sample starter set for 14 interviewable agents)
    memories_data = [
        {"emp_id": "VX001", "content": "I am Ananya Rao, CEO. I focus on customer expansion and strategic vision. I rely on Meera for finance numbers and Vikram for engineering deliverables.", "source_ref": "T1_CEO_Kickoff_Call.docx"},
        {"emp_id": "VX003", "content": "I am Meera Iyer, CFO. I maintain strict controls over company expenditure. Individual employee salaries are strictly confidential and must never be shown to Ananya. We moved to Zoho Books and Keka.", "source_ref": "T2_CFO_Call.docx"},
        {"emp_id": "VX004", "content": "I am Vikram Menon, VP of Engineering. Atlas v3 is our top priority. We experienced stability hurdles in August requiring outside support, and hiring is frozen.", "source_ref": "Board_Update_Jul-Sep_2026.pdf"},
        {"emp_id": "VX007", "content": "I am Priya Nair, Staff Engineer. I lead the core algorithm and real-time re-routing architecture for Atlas v3. I was heavily burdened during the August reliability incident.", "source_ref": "T1_CEO_Kickoff_Call.docx"},
        {"emp_id": "VX010", "content": "I am Karthik Subramanian, FP&A Manager. I am preparing for my CFA exams. I processed February payroll while Fatima was on wedding leave.", "source_ref": "01.eml, T2_CFO_Call.docx"},
        {"emp_id": "VX014", "content": "I am Fatima Sheikh, Accounts & Payroll Executive. I handle Zoho entries and payroll disbursements. I was away for my wedding in February 2026.", "source_ref": "03.eml, T2_CFO_Call.docx"},
        {"emp_id": "VX018", "content": "I am Rahul Verma, Backend Engineer. I joined Veloxa on February 3, 2026. I flagged a query on my first payslip because the amount appeared higher than partial month pro-ration.", "source_ref": "02.eml, Employee_Master.xlsx"},
    ]

    for m in memories_data:
        am = AgentMemory(
            emp_id=m["emp_id"],
            memory_type="grounded_fact",
            content=m["content"],
            source_ref=m.get("source_ref"),
            is_confidential=False
        )
        db.add(am)

    db.commit()
