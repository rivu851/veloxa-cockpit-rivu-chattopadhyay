import re
from typing import Tuple

DIRECT_SALARY_PATTERNS = [
    r"\b(salary|salaries|compensation|pay|payslip|ctc|remuneration|gross|net)\b.*\b(of|for)\b.*\b([A-Za-z]+)\b",
    r"\b(what|how much)\b.*\b(earn|make|paid|drawing|gets?)\b",
    r"\b([A-Za-z]+('s)?)\s+(salary|pay|compensation|ctc|package|payslip|deductions?|take[- ]home)\b",
    r"\bindividual\s+(salary|compensation|pay)\b",
    r"\b(who\s+(makes?|earns?|gets?))\b",
]

INDIRECT_INFERENCE_PATTERNS = [
    r"\b(highest|lowest|top|bottom|max|min|most|least)\s+(paid|earner|salary|compensation|package)\b",
    r"\b(who\s+is\s+the\s+(highest|lowest|top|bottom)\s+paid)\b",
    r"\b(average|median|mean)\s+(engineering|sales|marketing|finance|employee|staff)?\s*(salary|pay|compensation)\b",
    r"\b(compare|ranking|rank|breakdown)\s+(of\s+)?(salaries|compensation|pay)\b",
    r"\b(deductions?|take[- ]home)\b.*\b(of|for)\b",
]

AGGREGATE_ALLOWLIST = [
    "total payroll",
    "total salary",
    "monthly payroll",
    "aggregate payroll",
    "payroll expense",
    "payroll burn",
    "total burn",
    "payroll register",
]

def is_salary_query(query: str) -> bool:
    q_lower = query.lower()
    
    # Check if this is an explicit aggregate query (e.g. monthly company payroll total)
    for agg in AGGREGATE_ALLOWLIST:
        if agg in q_lower:
            # If asking about an individual within an aggregate query, still block
            if not any(re.search(p, q_lower) for p in [r"\b(of|for)\s+[A-Za-z]+\b"]):
                return False
            
    # Check direct individual salary patterns
    for pattern in DIRECT_SALARY_PATTERNS:
        if re.search(pattern, q_lower):
            return True
            
    # Check indirect salary inference patterns
    for pattern in INDIRECT_INFERENCE_PATTERNS:
        if re.search(pattern, q_lower):
            return True
            
    return False

def redact_sensitive_fact(fact_text: str, is_confidential: bool = False) -> Tuple[str, bool]:
    """
    Masks individual compensation figures while keeping role/month/status intact.
    Protects gross, net, deduction amounts and per-person salary numbers.
    """
    if not is_confidential and "Gross" not in fact_text and "Net" not in fact_text and "Deductions" not in fact_text:
        return fact_text, False

    # Redact gross/net/deduction figures
    redacted = re.sub(r"(Gross\s*\(?Rs\.?\)?\s*[:=]?\s*)\d+", r"\1[REDACTED_CONFIDENTIAL]", fact_text, flags=re.IGNORECASE)
    redacted = re.sub(r"(Net\s*\(?Rs\.?\)?\s*[:=]?\s*)\d+", r"\1[REDACTED_CONFIDENTIAL]", redacted, flags=re.IGNORECASE)
    redacted = re.sub(r"(Deductions\s*\(?Rs\.?\)?\s*[:=]?\s*)\d+", r"\1[REDACTED_CONFIDENTIAL]", redacted, flags=re.IGNORECASE)
    return redacted, True
