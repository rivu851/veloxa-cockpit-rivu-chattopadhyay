import re
from typing import Tuple

SALARY_QUERY_PATTERNS = [
    r"\b(salary|salaries|compensation|pay|payslip|ctc|remuneration|gross|net)\b.*\b(of|for)\b.*\b([A-Za-z]+)\b",
    r"\b(what|how much)\b.*\b(earn|make|paid|drawing|gets?)\b",
    r"\b([A-Za-z]+('s)?)\s+(salary|pay|compensation|ctc|package)\b",
    r"\bindividual\s+(salary|compensation|pay)\b",
]

AGGREGATE_TERMS = [
    "total payroll",
    "total salary",
    "monthly payroll",
    "aggregate payroll",
    "payroll expense",
    "payroll burn",
    "total burn",
]

def is_salary_query(query: str) -> bool:
    q_lower = query.lower()
    # Check if asking for aggregates
    for agg in AGGREGATE_TERMS:
        if agg in q_lower:
            return False
            
    for pattern in SALARY_QUERY_PATTERNS:
        if re.search(pattern, q_lower):
            return True
    return False

def redact_sensitive_fact(fact_text: str, is_confidential: bool = False) -> Tuple[str, bool]:
    """
    Masks individual compensation figures while keeping role/month/status intact.
    """
    if not is_confidential and "Gross (Rs.)" not in fact_text and "Net (Rs.)" not in fact_text:
        return fact_text, False

    # Redact gross/net monetary amounts associated with an individual
    redacted = re.sub(r"(Gross\s*\(?Rs\.?\)?\s*[:=]?\s*)\d+", r"\1[REDACTED_CONFIDENTIAL]", fact_text)
    redacted = re.sub(r"(Net\s*\(?Rs\.?\)?\s*[:=]?\s*)\d+", r"\1[REDACTED_CONFIDENTIAL]", redacted)
    redacted = re.sub(r"(Deductions\s*\(?Rs\.?\)?\s*[:=]?\s*)\d+", r"\1[REDACTED_CONFIDENTIAL]", redacted)
    return redacted, True
