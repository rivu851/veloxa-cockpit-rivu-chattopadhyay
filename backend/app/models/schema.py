import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(255), unique=True, nullable=False)
    file_type = Column(String(50), nullable=False)  # docx, pdf, xlsx, eml, txt
    release_day = Column(String(20), nullable=False, default="Day1")  # Day1, Day2, Day3, Day4
    released_at = Column(DateTime, nullable=False)  # e.g., 2026-11-16 10:00:00 IST
    description = Column(Text, nullable=True)
    provenance = Column(Text, nullable=True)
    is_confidential = Column(Boolean, default=False)

    evidence_items = relationship("Evidence", back_populates="source", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="source", cascade="all, delete-orphan")


class Evidence(Base):
    """
    Direct granular fact extracted from a primary source file.
    Preserves exact sheet, page, and row citations.
    """
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ref = Column(String(20), unique=True, nullable=False, index=True)  # E001, E002, etc.
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    sheet_or_page = Column(String(100), nullable=True)
    row_or_line = Column(String(100), nullable=True)
    fact_text = Column(Text, nullable=False)
    entities_named = Column(String(255), nullable=True)
    date_as_written = Column(String(100), nullable=True)
    date_normalized = Column(DateTime, nullable=True)
    confidence = Column(String(5), default="H")  # H, M, L
    is_confidential = Column(Boolean, default=False)  # e.g. individual salary data
    released_at = Column(DateTime, nullable=False)

    source = relationship("Source", back_populates="evidence_items")


class Claim(Base):
    """
    Assertion made by an individual, transcript speaker, or document.
    May be verified, disputed, or contradicted by evidence.
    """
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(50), unique=True, nullable=False)
    speaker_or_author = Column(String(100), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    claim_text = Column(Text, nullable=False)
    claim_category = Column(String(50), nullable=False)  # ARR, Burn, Headcount, Product, Culture
    date_asserted = Column(String(100), nullable=True)
    is_disputed = Column(Boolean, default=False)
    competing_evidence_refs = Column(String(255), nullable=True)
    released_at = Column(DateTime, nullable=False)

    source = relationship("Source", back_populates="claims")


class Person(Base):
    """
    Veloxa employee grounded in Keka HRMS records.
    """
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, autoincrement=True)
    emp_id = Column(String(20), unique=True, nullable=False, index=True)  # VX001..VX019
    full_name = Column(String(100), nullable=False)
    work_email = Column(String(100), unique=True, nullable=False)
    department = Column(String(50), nullable=False)
    title = Column(String(100), nullable=False)
    manager_id = Column(String(20), nullable=True)
    join_date = Column(String(20), nullable=False)
    location = Column(String(50), nullable=False)
    status = Column(String(30), nullable=False, default="Active")
    exit_date = Column(String(20), nullable=True)
    is_interviewable = Column(Boolean, default=True)
    system_role_desc = Column(Text, nullable=True)
    released_at = Column(DateTime, nullable=False)


class Conflict(Base):
    """
    Documented factual contradictions between sources.
    Must have proposed interpretations, confidence, what would change mind,
    and require explicit human review (status='UNRESOLVED' until confirmed).
    """
    __tablename__ = "conflicts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conflict_id = Column(String(50), unique=True, nullable=False, index=True)
    topic = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    competing_sources = Column(Text, nullable=False)
    proposed_interpretation = Column(Text, nullable=False)
    confidence = Column(String(5), default="M")  # H, M, L
    what_would_change = Column(Text, nullable=False)
    impact_level = Column(String(20), default="HIGH")  # HIGH, MEDIUM, LOW
    human_status = Column(String(30), default="UNRESOLVED")  # UNRESOLVED, RESOLVED
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Assumption(Base):
    """
    Explicitly tracked analytical assumptions.
    """
    __tablename__ = "assumptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assumption_id = Column(String(50), unique=True, nullable=False, index=True)
    domain = Column(String(50), nullable=False)  # ARR, Payroll, Attrition, Culture
    statement = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    risk_if_wrong = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AgentMemory(Base):
    """
    Grounded knowledge and persona context for interviewable agents.
    Strictly isolated to facts the employee would realistically know.
    """
    __tablename__ = "agent_memories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    emp_id = Column(String(20), ForeignKey("people.emp_id"), nullable=False)
    memory_type = Column(String(50), default="grounded_fact")  # grounded_fact, role_context, personal_life
    content = Column(Text, nullable=False)
    source_ref = Column(String(100), nullable=True)
    is_confidential = Column(Boolean, default=False)


class AuditLog(Base):
    """
    Access log recording queries, citations, and redactions.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    actor = Column(String(100), default="CEO")
    endpoint = Column(String(100), nullable=False)
    query_text = Column(Text, nullable=True)
    citations_returned = Column(Text, nullable=True)
    redaction_applied = Column(Boolean, default=False)
