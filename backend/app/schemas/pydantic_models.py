from typing import List, Optional
from pydantic import BaseModel, Field

class Citation(BaseModel):
    ref: str
    source_file: str
    sheet_or_page: Optional[str] = None
    row_or_line: Optional[str] = None
    fact_text: str
    confidence: str = "H"

class AskRequest(BaseModel):
    query: str
    as_of: Optional[str] = Field(default=None, description="ISO timestamp or release day (e.g., 'Day1', '2026-11-16T10:00:00+05:30')")
    as_of_date: Optional[str] = Field(default=None, description="Alias for as_of parameter")

    def get_as_of(self) -> Optional[str]:
        return self.as_of or self.as_of_date

class AskResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation] = []
    confidence: str = Field(default="HIGH", description="HIGH, MEDIUM, LOW, REFUSED")
    status: str = Field(default="ANSWERED", description="ANSWERED, UNCERTAIN, REFUSAL")
    refusal_reason: Optional[str] = None
    conflict_detected: bool = False
    conflict_details: Optional[str] = None
    as_of: str

class RiskItem(BaseModel):
    rank: int
    risk_id: str
    title: str
    category: str  # Financial, Engineering, Operational, Governance, Key-Person
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    summary: str
    evidence_refs: List[str]
    citations: List[Citation]
    recommended_mitigation: str

class RiskListResponse(BaseModel):
    as_of: str
    total_risks: int
    risks: List[RiskItem]

class AgentSummary(BaseModel):
    emp_id: str
    full_name: str
    title: str
    department: str
    manager_id: Optional[str] = None
    location: str
    status: str
    is_interviewable: bool

class AgentChatRequest(BaseModel):
    message: str
    as_of: Optional[str] = None

class AgentChatResponse(BaseModel):
    emp_id: str
    full_name: str
    title: str
    reply: str
    citations: List[Citation] = []
    confidence: str = "HIGH"
    knowledge_boundaries_respected: bool = True

class EvidenceResponse(BaseModel):
    ref: str
    source_file: str
    sheet_or_page: Optional[str] = None
    row_or_line: Optional[str] = None
    fact_text: str
    entities_named: Optional[str] = None
    date_as_written: Optional[str] = None
    date_normalized: Optional[str] = None
    confidence: str
    is_redacted: bool
    released_at: str

class ConflictResponse(BaseModel):
    conflict_id: str
    topic: str
    description: str
    competing_sources: str
    proposed_interpretation: str
    confidence: str
    what_would_change: str
    impact_level: str
    human_status: str
    resolution_notes: Optional[str] = None

class TeamEngagement(BaseModel):
    team: str
    team_size: int
    responses: int
    latest_score: float
    prior_score: float
    change: float
    comments_status: str

class RequisitionItem(BaseModel):
    req_id: str
    role: str
    team: str
    manager_id: str
    opened_date: str
    status: str
    status_date: str
    pipeline_count: int
    notes: Optional[str] = None

class HRInsightsResponse(BaseModel):
    as_of: str
    team_engagement: List[TeamEngagement]
    requisitions: List[RequisitionItem]
    privacy_safeguards: List[str]


# ==========================================
# DAY 3 SCHEMAS: ENGINEERING & MARKETING
# ==========================================

class JiraEpicProgress(BaseModel):
    epic_key: str
    name: str
    total_issues: int
    done_issues: int
    in_progress_issues: int
    todo_issues: int
    total_points: int
    done_points: int
    completion_pct: float

class JiraTotals(BaseModel):
    total_issues: int
    total_points: int
    done_issues: int
    done_points: int
    in_progress_issues: int
    in_progress_points: int
    todo_issues: int
    todo_points: int
    completion_pct: float

class JiraVersionInfo(BaseModel):
    version_name: str
    release_date: str
    original_release_date: str
    last_changed: str
    changed_by: str
    last_changed_by: str
    is_delayed: bool = True

class IncidentItem(BaseModel):
    incident_id: str
    severity: str
    opened_at_utc: str
    opened_at_ist: str
    resolved_at_utc: str
    resolved_at_ist: str
    duration_minutes: float
    service: str
    responder: str

class OnCallItem(BaseModel):
    week_of: str
    primary_responder: str
    secondary_responder: str

class GitAuthorStats(BaseModel):
    author_email: str
    display_name: str
    commit_count: int
    repos: List[str]

class GitRepoStats(BaseModel):
    repo_name: str
    commit_count: int

class GitTelemetry(BaseModel):
    total_commits: int
    by_author: List[GitAuthorStats]
    by_repo: List[GitRepoStats]
    priya_commits_total: int
    priya_corp_commits: int
    priya_noreply_commits: int
    disclaimer: str

class EngineeringOverviewResponse(BaseModel):
    as_of: str
    atlas_ga: JiraVersionInfo
    jira_epics: List[JiraEpicProgress]
    jira_totals: JiraTotals
    august_sev1_count: int
    total_incidents: int
    incidents: List[IncidentItem]
    on_call_rota: List[OnCallItem]
    git_telemetry: GitTelemetry
    source_freshness: str

class LaunchKitItem(BaseModel):
    asset_name: str
    status: str
    owner: str
    planned_date: Optional[str] = None
    notes: Optional[str] = None

class MarketingOverviewResponse(BaseModel):
    as_of: str
    launch_kit_assets: List[LaunchKitItem]
    sid_departure_notes: str
    marketing_spend_claim: str
    verified_spend_status: str
    proposed_cro_reporting: str

class OrgReportingLineItem(BaseModel):
    department: str
    role_title: str
    reports_to_role: str
    reports_to_person_id: Optional[str] = None
    status: str  # active, proposed
    is_unfilled_role: bool = False

class OrgSimulationResponse(BaseModel):
    as_of: str
    mode: str  # "actual_as_of" or "simulated_cro"
    reporting_lines: List[OrgReportingLineItem]
    description: str
    guardrails: List[str]

