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
    Explicitly distinguishes:
    1. released_at: timestamp when file was made available in the data room.
    2. record_date: date when document/record was officially created or transmitted.
    3. effective_date: date when underlying business event occurred or period concluded.
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
    record_date = Column(DateTime, nullable=True)
    effective_date = Column(DateTime, nullable=True)
    date_normalized = Column(DateTime, nullable=True)  # For backward-compatible query filtering
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
    claim_id = Column(String(50), unique=True, nullable=False, index=True)
    speaker_or_author = Column(String(100), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    claim_text = Column(Text, nullable=False)
    claim_category = Column(String(50), nullable=False)  # ARR, Burn, Headcount, Product, Culture, Engineering, Payroll, Operations, Marketing
    date_asserted = Column(String(100), nullable=True)
    record_date = Column(DateTime, nullable=True)
    effective_date = Column(DateTime, nullable=True)
    is_disputed = Column(Boolean, default=False)
    competing_evidence_refs = Column(String(255), nullable=True)
    evidence_ref = Column(String(50), nullable=True)
    confidence = Column(String(5), default="M")
    conflict_id = Column(String(50), nullable=True)
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


# ==========================================
# DAY 3 NORMALIZED STRUCTURED DATA MODELS
# ==========================================

class GitCommit(Base):
    """
    Structured normalized record of a Git commit across Veloxa repositories.
    Preserves raw commit metadata, author email, timestamp, and changed files.
    """
    __tablename__ = "git_commits"

    sha = Column(String(50), primary_key=True)
    author_email = Column(String(100), nullable=False, index=True)
    author_name = Column(String(100), nullable=True)
    committed_at = Column(DateTime, nullable=False, index=True)
    committed_at_str = Column(String(50), nullable=False)
    repo = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    files_changed = Column(Integer, default=0)
    released_at = Column(DateTime, nullable=False)


class JiraIssue(Base):
    """
    Structured record from Jira project ATLAS export.
    Preserves exact key, epic link, story points, status, and dates.
    """
    __tablename__ = "jira_issues"

    key = Column(String(50), primary_key=True)
    issue_type = Column(String(50), nullable=False)
    summary = Column(Text, nullable=False)
    epic_key = Column(String(50), nullable=False, index=True)
    assignee_initials = Column(String(20), nullable=False, index=True)
    story_points = Column(Integer, default=0)
    status = Column(String(50), nullable=False, index=True)
    created_date = Column(String(50), nullable=False)
    resolved_date = Column(String(50), nullable=True)
    fix_version = Column(String(50), nullable=True)
    row_number = Column(Integer, nullable=True)
    released_at = Column(DateTime, nullable=False)


class JiraEpic(Base):
    """
    Jira Epic definitions for project ATLAS.
    """
    __tablename__ = "jira_epics"

    key = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    released_at = Column(DateTime, nullable=False)


class JiraVersion(Base):
    """
    Jira Version record tracking planned vs revised release dates and audit changes.
    """
    __tablename__ = "jira_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version_name = Column(String(100), nullable=False)
    release_date = Column(String(50), nullable=False)
    original_release_date = Column(String(50), nullable=False)
    last_changed = Column(String(50), nullable=False)
    changed_by = Column(String(50), nullable=False)
    released_at = Column(DateTime, nullable=False)


class Incident(Base):
    """
    PagerDuty incident export (Aug - Oct 2026).
    Timestamped in UTC with explicit IST display conversion support.
    """
    __tablename__ = "incidents"

    incident_id = Column(String(50), primary_key=True)
    severity = Column(String(20), nullable=False, index=True)  # SEV1, SEV2, SEV3
    opened_at_utc = Column(DateTime, nullable=False)
    resolved_at_utc = Column(DateTime, nullable=False)
    opened_at_str = Column(String(50), nullable=False)
    resolved_at_str = Column(String(50), nullable=False)
    service = Column(String(50), nullable=False, index=True)
    responder = Column(String(50), nullable=False, index=True)
    duration_minutes = Column(Float, nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    released_at = Column(DateTime, nullable=False)


class OnCallEntry(Base):
    """
    Weekly primary and secondary on-call rota from engineering wiki.
    """
    __tablename__ = "on_call_rota"

    id = Column(Integer, primary_key=True, autoincrement=True)
    week_of = Column(String(50), nullable=False, index=True)
    primary_responder = Column(String(50), nullable=False)
    secondary_responder = Column(String(50), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    released_at = Column(DateTime, nullable=False)


class LaunchKitAsset(Base):
    """
    Atlas Launch Kit asset status from Atlas_Launch_Kit_v1.pdf.
    """
    __tablename__ = "launch_kit_assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_name = Column(String(100), nullable=False)
    status = Column(String(100), nullable=False)
    owner = Column(String(50), nullable=False)
    planned_date = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    released_at = Column(DateTime, nullable=False)


class OrgReportingLine(Base):
    """
    Effective-dated, reversible organizational reporting structure.
    Allows modeling proposed vs active reporting lines (e.g. T6b Marketing -> CRO)
    without mutating employee identities, memory, or historical attribution.
    """
    __tablename__ = "org_reporting_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(String(20), nullable=True)  # e.g. VX006
    department = Column(String(50), nullable=False)
    role_title = Column(String(100), nullable=False)
    reports_to_role = Column(String(100), nullable=False)  # "CEO", "CRO"
    reports_to_person_id = Column(String(20), nullable=True)  # VX001, or None for unfilled role
    status = Column(String(30), nullable=False, default="active")  # active, proposed, deprecated
    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=True)
    source_ref = Column(String(50), nullable=True)
    citation = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    released_at = Column(DateTime, nullable=False)

