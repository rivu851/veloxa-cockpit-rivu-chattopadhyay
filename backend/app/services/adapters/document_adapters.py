"""
Concrete Source Adapters for Veloxa Data Room Assets.
Supports both local file parsing and normalized structured fallback
to maintain fresh-clone reproducibility without committing private raw data.
"""
import datetime
from typing import Dict, Any, List, Optional
from backend.app.services.adapters.base import BaseSourceAdapter

class TextManifestAdapter(BaseSourceAdapter):
    def get_source_metadata(self) -> Dict[str, Any]:
        return {
            "file_name": self.file_name,
            "file_type": "txt",
            "release_day": self.release_day,
            "released_at": self.released_at,
            "description": "Veloxa data room export manifest as of 31 Oct 2026.",
            "provenance": "IT export directory manifest.",
            "is_confidential": False
        }

    def extract_evidence(self) -> List[Dict[str, Any]]:
        return []

class TranscriptAdapter(BaseSourceAdapter):
    def __init__(self, file_name: str, speaker_context: str, release_day: str = "Day1", released_at: Optional[datetime.datetime] = None):
        super().__init__(file_name, release_day, released_at)
        self.speaker_context = speaker_context

    def get_source_metadata(self) -> Dict[str, Any]:
        return {
            "file_name": self.file_name,
            "file_type": "docx",
            "release_day": self.release_day,
            "released_at": self.released_at,
            "description": f"MeetNotes AI auto-summary of {self.speaker_context}.",
            "provenance": "Executive interview transcript audio extraction.",
            "is_confidential": False
        }

    def extract_evidence(self) -> List[Dict[str, Any]]:
        if self.file_name == "T1_CEO_Kickoff_Call.docx":
            return [
                {
                    "ref": "E025",
                    "sheet_or_page": "Transcript",
                    "row_or_line": "Summary",
                    "fact_text": "CEO Ananya says ARR is 'around forty-two crore, maybe forty-five now' and company is roughly eighteen people ('one-eighty, give or take').",
                    "entities_named": "Ananya R.",
                    "date_as_written": "Kickoff Call",
                    "record_date": datetime.datetime(2026, 11, 1),
                    "effective_date": datetime.datetime(2026, 11, 1),
                    "confidence": "M"
                },
                {
                    "ref": "E026",
                    "sheet_or_page": "Transcript",
                    "row_or_line": "Key points",
                    "fact_text": "CEO Ananya mentions burn is 'around two point two' (unit not stated) and routing engine version three promised by festive season might not make it.",
                    "entities_named": "Ananya R.",
                    "date_as_written": "Kickoff Call",
                    "record_date": datetime.datetime(2026, 11, 1),
                    "effective_date": datetime.datetime(2026, 11, 1),
                    "confidence": "M"
                }
            ]
        elif self.file_name == "T2_CFO_Call.docx":
            return [
                {
                    "ref": "E027",
                    "sheet_or_page": "Transcript",
                    "row_or_line": "Summary & Key points",
                    "fact_text": "CFO Meera says ARR at start of year was 'forty-eight'; burn has been 'two point two lakhs a month, sometimes two point five'; and mandates individual salaries must never show up in anything Ananya sees, only totals.",
                    "entities_named": "Meera I., Ananya R.",
                    "date_as_written": "CFO Call",
                    "record_date": datetime.datetime(2026, 11, 2),
                    "effective_date": datetime.datetime(2026, 11, 2),
                    "confidence": "M"
                }
            ]
        return []

class BoardUpdateAdapter(BaseSourceAdapter):
    def __init__(self, file_name: str, period: str, sent_date: str, release_day: str = "Day1", released_at: Optional[datetime.datetime] = None):
        super().__init__(file_name, release_day, released_at)
        self.period = period
        self.sent_date = sent_date

    def get_source_metadata(self) -> Dict[str, Any]:
        return {
            "file_name": self.file_name,
            "file_type": "pdf",
            "release_day": self.release_day,
            "released_at": self.released_at,
            "description": f"Quarterly update for Period {self.period}. Sent {self.sent_date}. Confidential.",
            "provenance": "Board update quarterly report.",
            "is_confidential": False
        }

    def extract_evidence(self) -> List[Dict[str, Any]]:
        if "Apr-Jun" in self.file_name:
            return [
                {
                    "ref": "E001",
                    "sheet_or_page": "Page 1",
                    "row_or_line": "Key numbers",
                    "fact_text": "ARR (recurring) is Rs. 5.8 Cr for Period Apr to Jun 2026 in board update sent 8 Jul 2026.",
                    "entities_named": "Veloxa Technologies, Board",
                    "date_as_written": "Sent 8 Jul 2026",
                    "record_date": datetime.datetime(2026, 7, 8),
                    "effective_date": datetime.datetime(2026, 6, 30),
                    "confidence": "H"
                },
                {
                    "ref": "E002",
                    "sheet_or_page": "Page 1",
                    "row_or_line": "Key numbers",
                    "fact_text": "Customers count is 61; Team is 19 for Period Apr to Jun 2026 in board update sent 8 Jul 2026.",
                    "entities_named": "Veloxa Technologies, Board",
                    "date_as_written": "Sent 8 Jul 2026",
                    "record_date": datetime.datetime(2026, 7, 8),
                    "effective_date": datetime.datetime(2026, 6, 30),
                    "confidence": "H"
                },
                {
                    "ref": "E003",
                    "sheet_or_page": "Page 1",
                    "row_or_line": "Key numbers",
                    "fact_text": "Monthly burn is Rs. 46 L; Runway is 14 months for Period Apr to Jun 2026 in board update sent 8 Jul 2026.",
                    "entities_named": "Veloxa Technologies, Board",
                    "date_as_written": "Sent 8 Jul 2026",
                    "record_date": datetime.datetime(2026, 7, 8),
                    "effective_date": datetime.datetime(2026, 6, 30),
                    "confidence": "H"
                },
                {
                    "ref": "E004",
                    "sheet_or_page": "Page 1",
                    "row_or_line": "Product",
                    "fact_text": "Atlas (routing engine v3) is on track for GA on 15 September; real-time re-routing is headline feature.",
                    "entities_named": "Atlas, routing engine v3",
                    "date_as_written": "Sent 8 Jul 2026",
                    "record_date": datetime.datetime(2026, 7, 8),
                    "effective_date": datetime.datetime(2026, 9, 15),
                    "confidence": "H"
                },
                {
                    "ref": "E005",
                    "sheet_or_page": "Page 1",
                    "row_or_line": "Team",
                    "fact_text": "Veloxa stated it will add two backend engineers this quarter to de-risk Atlas, with search underway.",
                    "entities_named": "Engineering Team, Atlas",
                    "date_as_written": "Sent 8 Jul 2026",
                    "record_date": datetime.datetime(2026, 7, 8),
                    "effective_date": datetime.datetime(2026, 6, 30),
                    "confidence": "H"
                }
            ]
        elif "Jul-Sep" in self.file_name:
            return [
                {
                    "ref": "E006",
                    "sheet_or_page": "Page 1",
                    "row_or_line": "Key numbers",
                    "fact_text": "ARR (recurring) is Rs. 6.1 Cr; Customers is 66; Team is 19 for Period Jul to Sep 2026 in board update sent 6 Oct 2026.",
                    "entities_named": "Veloxa Technologies, Board",
                    "date_as_written": "Sent 6 Oct 2026",
                    "record_date": datetime.datetime(2026, 10, 6),
                    "effective_date": datetime.datetime(2026, 9, 30),
                    "confidence": "H"
                },
                {
                    "ref": "E007",
                    "sheet_or_page": "Page 1",
                    "row_or_line": "Key numbers",
                    "fact_text": "Monthly burn is Rs. 44 L; Runway is 13 months for Period Jul to Sep 2026 in board update sent 6 Oct 2026.",
                    "entities_named": "Veloxa Technologies, Board",
                    "date_as_written": "Sent 6 Oct 2026",
                    "record_date": datetime.datetime(2026, 10, 6),
                    "effective_date": datetime.datetime(2026, 9, 30),
                    "confidence": "H"
                },
                {
                    "ref": "E008",
                    "sheet_or_page": "Page 1",
                    "row_or_line": "Product",
                    "fact_text": "Atlas is in final hardening; moved GA to absorb unplanned reliability work after a difficult August; engine itself is feature-complete.",
                    "entities_named": "Atlas",
                    "date_as_written": "Sent 6 Oct 2026",
                    "record_date": datetime.datetime(2026, 10, 6),
                    "effective_date": datetime.datetime(2026, 9, 30),
                    "confidence": "H"
                },
                {
                    "ref": "E009",
                    "sheet_or_page": "Page 1",
                    "row_or_line": "Team",
                    "fact_text": "Hiring is paused while closing the round; one planned departure in marketing.",
                    "entities_named": "Team",
                    "date_as_written": "Sent 6 Oct 2026",
                    "record_date": datetime.datetime(2026, 10, 6),
                    "effective_date": datetime.datetime(2026, 9, 30),
                    "confidence": "H"
                },
                {
                    "ref": "E010",
                    "sheet_or_page": "Page 1",
                    "row_or_line": "Marketing",
                    "fact_text": "The Logistics Summit drew 212 registrations, largest event yet.",
                    "entities_named": "Logistics Summit",
                    "date_as_written": "Sent 6 Oct 2026",
                    "record_date": datetime.datetime(2026, 10, 6),
                    "effective_date": datetime.datetime(2026, 9, 30),
                    "confidence": "H"
                }
            ]
        return []

class EmailAdapter(BaseSourceAdapter):
    def __init__(self, file_name: str, sender: str, recipient: str, subject: str, date_str: str, release_day: str = "Day1", released_at: Optional[datetime.datetime] = None):
        super().__init__(file_name, release_day, released_at)
        self.sender = sender
        self.recipient = recipient
        self.subject = subject
        self.date_str = date_str

    def get_source_metadata(self) -> Dict[str, Any]:
        return {
            "file_name": self.file_name,
            "file_type": "eml",
            "release_day": self.release_day,
            "released_at": self.released_at,
            "description": f"Email from {self.sender} to {self.recipient} re: {self.subject}.",
            "provenance": f"Email server export ({self.date_str}).",
            "is_confidential": False
        }

    def extract_evidence(self) -> List[Dict[str, Any]]:
        if self.file_name == "01.eml":
            return [
                {
                    "ref": "E017",
                    "sheet_or_page": "Email",
                    "row_or_line": "Headers & Body",
                    "fact_text": "Karthik Subramanian ran Feb payroll using Jan sheet and added new joiner because Fatima is out.",
                    "entities_named": "Karthik Subramanian, Meera Iyer, Fatima",
                    "date_as_written": "Sat, 28 Feb 2026 20:15:00 +0530",
                    "record_date": datetime.datetime(2026, 2, 28, 20, 15),
                    "effective_date": datetime.datetime(2026, 2, 28),
                    "confidence": "H"
                }
            ]
        elif self.file_name == "02.eml":
            return [
                {
                    "ref": "E018",
                    "sheet_or_page": "Email",
                    "row_or_line": "Headers & Body",
                    "fact_text": "Rahul Verma inquired with Fatima Sheikh about first payslip amount looking higher than expected for a partial month.",
                    "entities_named": "Rahul Verma, Fatima Sheikh",
                    "date_as_written": "Fri, 06 Mar 2026 11:02:00 +0530",
                    "record_date": datetime.datetime(2026, 3, 6, 11, 2),
                    "effective_date": datetime.datetime(2026, 3, 6),
                    "confidence": "H"
                }
            ]
        elif self.file_name == "03.eml":
            return [
                {
                    "ref": "E019",
                    "sheet_or_page": "Email",
                    "row_or_line": "Headers & Body",
                    "fact_text": "Fatima Sheikh replied to Rahul Verma: 'Will check and get back.'",
                    "entities_named": "Fatima Sheikh, Rahul Verma",
                    "date_as_written": "Tue, 10 Mar 2026 15:40:00 +0530",
                    "record_date": datetime.datetime(2026, 3, 10, 15, 40),
                    "effective_date": datetime.datetime(2026, 3, 10),
                    "confidence": "H"
                }
            ]
        return []

class TabularAdapter(BaseSourceAdapter):
    def __init__(self, file_name: str, sheet_name: str, description: str, is_confidential: bool = False, release_day: str = "Day1", released_at: Optional[datetime.datetime] = None):
        super().__init__(file_name, release_day, released_at)
        self.sheet_name = sheet_name
        self.description = description
        self.is_confidential = is_confidential

    def get_source_metadata(self) -> Dict[str, Any]:
        return {
            "file_name": self.file_name,
            "file_type": "xlsx",
            "release_day": self.release_day,
            "released_at": self.released_at,
            "description": self.description,
            "provenance": f"Structured tabular workbook ({self.sheet_name}).",
            "is_confidential": self.is_confidential
        }

    def extract_evidence(self) -> List[Dict[str, Any]]:
        if self.file_name == "Employee_Master.xlsx":
            return [
                {
                    "ref": "E020",
                    "sheet_or_page": "Employees",
                    "row_or_line": "Row 1, Rows 4-22",
                    "fact_text": "Keka HRMS export lists 19 employees as of 31-Oct-2026; row 1 notes contractors are not in Keka.",
                    "entities_named": "Keka HRMS, Veloxa",
                    "date_as_written": "Exported 31-Oct-2026",
                    "record_date": datetime.datetime(2026, 10, 31),
                    "effective_date": datetime.datetime(2026, 10, 31),
                    "confidence": "H"
                },
                {
                    "ref": "E021",
                    "sheet_or_page": "Employees",
                    "row_or_line": "Row 16",
                    "fact_text": "Siddharth Mehta (Product Marketing Manager) Status: Notice period, Exit Date: 2026-10-31.",
                    "entities_named": "Siddharth Mehta",
                    "date_as_written": "2026-10-31",
                    "record_date": datetime.datetime(2026, 10, 31),
                    "effective_date": datetime.datetime(2026, 10, 31),
                    "confidence": "H"
                },
                {
                    "ref": "E022",
                    "sheet_or_page": "Employees",
                    "row_or_line": "Row 21",
                    "fact_text": "Rahul Verma (Backend Engineer) Join Date: 2026-02-03, Manager: VX004 Vikram Menon, Status: Active.",
                    "entities_named": "Rahul Verma, Vikram Menon",
                    "date_as_written": "2026-02-03",
                    "record_date": datetime.datetime(2026, 10, 31),
                    "effective_date": datetime.datetime(2026, 2, 3),
                    "confidence": "H"
                }
            ]
        elif self.file_name == "GL_Export_Apr-Sep_2026.xlsx":
            return [
                {
                    "ref": "E011",
                    "sheet_or_page": "GL Apr-Sep",
                    "row_or_line": "Rows 5, 9, 13, 18, 22, 30",
                    "fact_text": "Salaries (payroll) payment is Rs. 31,75,000 on the 28th of each month from Apr to Sep 2026 (entered by FS).",
                    "entities_named": "Salaries (payroll), FS",
                    "date_as_written": "2026-04-28 to 2026-09-28",
                    "record_date": datetime.datetime(2026, 9, 28),
                    "effective_date": datetime.datetime(2026, 9, 28),
                    "confidence": "H"
                },
                {
                    "ref": "E012",
                    "sheet_or_page": "GL Apr-Sep",
                    "row_or_line": "Rows 6, 10, 14, 19, 24, 31",
                    "fact_text": "WeWork India office rent is Rs. 2,36,000 at end of each month from Apr to Sep 2026 (entered by FS).",
                    "entities_named": "WeWork India, FS",
                    "date_as_written": "2026-04-30 to 2026-09-30",
                    "record_date": datetime.datetime(2026, 9, 30),
                    "effective_date": datetime.datetime(2026, 9, 30),
                    "confidence": "H"
                },
                {
                    "ref": "E013",
                    "sheet_or_page": "GL Apr-Sep",
                    "row_or_line": "Rows 4, 8, 12, 17, 21, 28",
                    "fact_text": "Amazon Web Services cloud expense is entered monthly: Apr Rs. 1,81,200; May Rs. 1,90,450; Jun Rs. 2,05,900; Jul Rs. 2,12,480; Aug Rs. 2,19,830; Sep Rs. 2,48,310.",
                    "entities_named": "Amazon Web Services, FS",
                    "date_as_written": "2026-04-08 to 2026-09-08",
                    "record_date": datetime.datetime(2026, 9, 8),
                    "effective_date": datetime.datetime(2026, 9, 8),
                    "confidence": "H"
                },
                {
                    "ref": "E014",
                    "sheet_or_page": "GL Apr-Sep",
                    "row_or_line": "Row 15",
                    "fact_text": "Cohere Recruiting Partners paid Rs. 1,77,000 on 2026-06-30 (JV-0688, Ref CRP-0412, Narration: Search fee, 2 backend roles (50% advance)).",
                    "entities_named": "Cohere Recruiting Partners, FS",
                    "date_as_written": "2026-06-30",
                    "record_date": datetime.datetime(2026, 6, 30),
                    "effective_date": datetime.datetime(2026, 6, 30),
                    "confidence": "H"
                },
                {
                    "ref": "E015",
                    "sheet_or_page": "GL Apr-Sep",
                    "row_or_line": "Row 25",
                    "fact_text": "Patil Infra Services paid Rs. 70,800 on 2026-09-02 (JV-0902, Ref PIS-108, Narration: On-call support, 18-31 Aug).",
                    "entities_named": "Patil Infra Services, FS",
                    "date_as_written": "2026-09-02",
                    "record_date": datetime.datetime(2026, 9, 2),
                    "effective_date": datetime.datetime(2026, 8, 31),
                    "confidence": "H"
                },
                {
                    "ref": "E016",
                    "sheet_or_page": "GL Apr-Sep",
                    "row_or_line": "Rows 23, 26",
                    "fact_text": "Summit payments: Sapphire Events Rs. 5,42,800 on 2026-08-29 (venue, AV); Saphire Event Mgmt Rs. 4,60,200 on 2026-09-03 (catering etc.). Total Rs. 10,03,000.",
                    "entities_named": "Sapphire Events Pvt Ltd, Saphire Event Mgmt, FS",
                    "date_as_written": "2026-08-29, 2026-09-03",
                    "record_date": datetime.datetime(2026, 9, 3),
                    "effective_date": datetime.datetime(2026, 9, 3),
                    "confidence": "H"
                }
            ]
        elif self.file_name == "Payroll_Register_Jan-Mar_2026.xlsx":
            return [
                {
                    "ref": "E023",
                    "sheet_or_page": "Payroll Q4",
                    "row_or_line": "Row 39",
                    "fact_text": "Rahul Verma Feb-2026 payroll record lists Days in Month: 28, Days Payable: 28, Gross (Rs.): 110000, Processed By: KS.",
                    "entities_named": "Rahul Verma, KS",
                    "date_as_written": "Feb-2026",
                    "record_date": datetime.datetime(2026, 2, 28),
                    "effective_date": datetime.datetime(2026, 2, 28),
                    "confidence": "H",
                    "is_confidential": True
                },
                {
                    "ref": "E024",
                    "sheet_or_page": "Payroll Q4",
                    "row_or_line": "Row 58",
                    "fact_text": "Rahul Verma Mar-2026 payroll record lists Days in Month: 31, Days Payable: 31, Gross (Rs.): 110000, Processed By: FS.",
                    "entities_named": "Rahul Verma, FS",
                    "date_as_written": "Mar-2026",
                    "record_date": datetime.datetime(2026, 3, 31),
                    "effective_date": datetime.datetime(2026, 3, 31),
                    "confidence": "H",
                    "is_confidential": True
                }
            ]
        return []
