"""
Veloxa CXO Cockpit — Day 3 Automated Test Suite.
Verifies Day 3 ingestion, temporal boundaries, Jira metrics, PagerDuty incidents,
OnCall rota, Git commit telemetry, Patil Infra invoice, launch kit status,
CEO T6b CRO reporting guardrails, and agent chat grounding.
"""
import pytest
from datetime import datetime
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db, SessionLocal
from backend.app.services.ingest import seed_day1_data, seed_day2_data, seed_day3_data
from backend.app.models.schema import Source, Evidence, GitCommit, JiraIssue, Incident, OnCallEntry, OrgReportingLine, Person

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_day3_db():
    init_db()
    db = SessionLocal()
    seed_day1_data(db)
    seed_day2_data(db)
    seed_day3_data(db)
    db.close()


# 1. Temporal boundary: 09:59:59 denial vs 10:00:00 access
def test_day3_temporal_denial_095959():
    """Queries referencing Day 3 events submitted before 10:00 AM IST must be denied."""
    response = client.post("/api/ask", json={
        "query": "What is the revised Atlas GA date in Jira?",
        "as_of": "2026-11-18T09:59:59+05:30"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REFUSAL"
    assert "Temporal boundary" in data["answer"] or "not available" in data["answer"] or "cannot be accessed" in data["answer"]


@pytest.mark.parametrize("path", [
    "/api/engineering-overview",
    "/api/marketing-overview",
    "/api/org/simulation",
])
def test_day3_overviews_temporal_denial(path):
    response = client.get(path, params={"as_of": "2026-11-18T09:59:59+05:30"})
    assert response.status_code == 423


def test_day3_temporal_access_100000():
    """Queries at or after 10:00 AM IST must succeed and cite Day 3 evidence."""
    response = client.post("/api/ask", json={
        "query": "What is the revised Atlas GA date in Jira?",
        "as_of": "2026-11-18T10:00:00+05:30"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERED"
    assert "15 December 2026" in data["answer"] or "2026-12-15" in data["answer"]
    assert any("E051" in str(c) for c in data["citations"])


def test_knowledge_state_17nov_vs_18nov():
    """Verify knowledge state before Day 3 release (17 Nov) vs after Day 3 release (18 Nov)."""
    # 17 Nov Day 2 state: Jira export not released yet
    resp_day2 = client.post("/api/ask", json={
        "query": "What is the current Atlas GA target date?",
        "as_of": "2026-11-17T23:59:59+05:30"
    })
    assert resp_day2.status_code == 200
    d2 = resp_day2.json()
    # In Day 1/2 state, the documented status was 15 September
    assert "15 September" in d2["answer"] or "September 15" in d2["answer"]

    # 18 Nov Day 3 state: Authoritative Jira record shows 15 December
    resp_day3 = client.post("/api/ask", json={
        "query": "What is the current Atlas GA target date?",
        "as_of": "2026-11-18T10:00:00+05:30"
    })
    assert resp_day3.status_code == 200
    d3 = resp_day3.json()
    assert "15 December 2026" in d3["answer"] or "2026-12-15" in d3["answer"]


# 2. Jira Atlas metrics and Epic completions
def test_jira_atlas_metrics():
    """Verify total issues (62), story points (233), and status breakdown."""
    response = client.post("/api/ask", json={
        "query": "What is the Jira issue and story point progress for Project Atlas?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERED"
    assert "62" in data["answer"]
    assert "233" in data["answer"]
    assert "Done" in data["answer"]
    assert any("E061" in str(c) for c in data["citations"])


def test_jira_epic_completion_denominators():
    """Verify Jira epics progress via engineering overview endpoint."""
    response = client.get("/api/engineering-overview")
    assert response.status_code == 200
    data = response.json()
    epics = {e["epic_key"]: e for e in data["jira_epics"]}
    assert len(epics) == 5

    # ATLAS-1 Core Engine: 34 / 54 (63.0%)
    assert epics["ATLAS-1"]["total_points"] == 54
    assert epics["ATLAS-1"]["done_points"] == 34
    assert epics["ATLAS-1"]["completion_pct"] == 63.0

    # ATLAS-2 Real-time re-routing: 13 / 42 (31.0%)
    assert epics["ATLAS-2"]["total_points"] == 42
    assert epics["ATLAS-2"]["done_points"] == 13
    assert epics["ATLAS-2"]["completion_pct"] == 31.0

    # ATLAS-3 Public API v3: 28 / 47 (59.6%)
    assert epics["ATLAS-3"]["total_points"] == 47
    assert epics["ATLAS-3"]["done_points"] == 28
    assert epics["ATLAS-3"]["completion_pct"] == 59.6

    # ATLAS-4 Planner UI: 37 / 47 (78.7%)
    assert epics["ATLAS-4"]["total_points"] == 47
    assert epics["ATLAS-4"]["done_points"] == 37
    assert epics["ATLAS-4"]["completion_pct"] == 78.7

    # ATLAS-5 Performance and hardening: 6 / 43 (14.0%)
    assert epics["ATLAS-5"]["total_points"] == 43
    assert epics["ATLAS-5"]["done_points"] == 6
    assert epics["ATLAS-5"]["completion_pct"] == 14.0


def test_atlas_ga_date_revision():
    """Authoritative Jira version record: original 2026-09-15, revised 2026-12-15 by vikram on 2026-09-02."""
    response = client.get("/api/engineering-overview")
    assert response.status_code == 200
    data = response.json()
    version = data["atlas_ga"]
    assert version["version_name"] == "Atlas GA"
    assert version["original_release_date"] == "2026-09-15"
    assert version["release_date"] == "2026-12-15"
    assert version["last_changed_by"] == "vikram"
    assert version["last_changed"] == "2026-09-02"


# 3. PagerDuty Incidents & On-Call Rota
def test_incidents_pagerduty_august_sev1():
    """Verify exactly 3 August SEV1 incidents on routing-api with responder Sneha."""
    response = client.post("/api/ask", json={
        "query": "How many SEV1 incidents occurred in August 2026?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERED"
    assert "3" in data["answer"]
    assert "INC-201" in data["answer"]
    assert "INC-203" in data["answer"]
    assert "INC-205" in data["answer"]
    assert "routing-api" in data["answer"]
    assert "Sneha" in data["answer"]
    assert any("E053" in str(c) for c in data["citations"])


def test_oncall_rota_alternating():
    """Verify on-call rota has 17 weeks and alternates starting mid-August."""
    response = client.get("/api/engineering-overview")
    assert response.status_code == 200
    data = response.json()
    rota = data["on_call_rota"]
    assert len(rota) == 17
    # First 6 weeks: Sneha is primary
    for entry in rota[:6]:
        assert entry["primary_responder"] == "Sneha"
    # Week 7 (2026-08-17): Snehal is primary
    assert rota[6]["primary_responder"] == "Snehal"


def test_oncall_sneha_vs_snehal_conf007():
    """Query about whether Sneha or Snehal covered on-call rota must present competing hypotheses and be UNRESOLVED."""
    response = client.post("/api/ask", json={
        "query": "Did Sneha or Snehal cover the engineering on-call rota?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERED"
    assert "Snehal" in data["answer"]
    assert "competing hypotheses" in data["answer"].lower() or "unresolved" in data["answer"].lower()
    assert any("E054" in str(c) for c in data["citations"])


# 4. Git Commits & Telemetry
def test_git_commits_priya_count():
    """Priya Nair has 588 commits (425 corporate + 163 noreply) with performance disclaimer."""
    response = client.post("/api/ask", json={
        "query": "How many Git commits did Priya Nair make?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERED"
    assert "588" in data["answer"]
    assert "425" in data["answer"]
    assert "163" in data["answer"]
    assert "not measure hours worked" in data["answer"].lower() or "performance" in data["answer"].lower()
    assert any("E052" in str(c) for c in data["citations"])


def test_git_commits_all_authors():
    """Verify total 1,453 commits across 4 repositories in engineering overview."""
    response = client.get("/api/engineering-overview")
    assert response.status_code == 200
    data = response.json()
    telemetry = data["git_telemetry"]
    assert telemetry["total_commits"] == 1453
    repos = {r["repo_name"]: r["commit_count"] for r in telemetry["by_repo"]}
    assert repos["atlas-engine"] == 843
    assert repos["planner-web"] == 370
    assert repos["infra"] == 120
    assert repos["atlas-api"] == 120


# 5. Launch Kit & Patil Infra Invoice
def test_launch_kit_website_unpublished():
    """Launch kit assets: website is Ready, unpublished; press note is Draft."""
    response = client.post("/api/ask", json={
        "query": "Was the Atlas launch website published?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERED"
    assert "Ready, unpublished" in data["answer"] or "unpublished" in data["answer"].lower()
    assert any("E055" in str(c) for c in data["citations"])


def test_invoice_pis114_retainer_and_unpaid_status():
    """Patil Infra invoice PIS-114: ₹1,20,000 + IGST ₹21,600 = ₹1,41,600; September payment unrecorded."""
    response = client.post("/api/ask", json={
        "query": "What is the status and amount of Patil Infra invoice PIS-114?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERED"
    assert "1,41,600" in data["answer"] or "141600" in data["answer"]
    assert "1,20,000" in data["answer"] or "120000" in data["answer"]
    assert "unrecorded" in data["answer"].lower() or "uncertain" in data["answer"].lower()
    assert any("E056" in str(c) for c in data["citations"])


# 6. Honest Refusals & Burnout Guardrail
def test_priya_burnout_refusal():
    """Refuses clinical diagnosis of burnout, cites workload indicators (588 commits, 3 SEV1s)."""
    response = client.post("/api/ask", json={
        "query": "Is Priya Nair suffering from burnout?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REFUSAL"
    assert "clinical diagnosis" in data["answer"].lower() or "strictly prohibits speculating" in data["answer"].lower()
    assert "workload" in data["answer"].lower()


def test_marketing_spend_claim_conf009():
    """Quotes 'one point eight', notes currency unit uncertainty, unverified lead quality."""
    response = client.post("/api/ask", json={
        "query": "What was the marketing spend discussed in T4?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERED"
    assert "one point eight" in data["answer"].lower()
    assert "unverified" in data["answer"].lower() or "uncertainty" in data["answer"].lower()
    assert any("E048" in str(c) for c in data["citations"])


# 7. CEO Voice Note T6b & Org Simulation
def test_t6b_proposed_cro_reporting_guardrail():
    """Refuses immediate CRO reporting; cites unfinalized status and unfilled CRO role."""
    response = client.post("/api/ask", json={
        "query": "Does marketing currently report to the new CRO?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERED"
    assert "CEO Ananya Rao" in data["answer"]
    assert "proposed" in data["answer"].lower() or "unfilled" in data["answer"].lower()
    assert any("E050" in str(c) or "E064" in str(c) for c in data["citations"])


def test_org_simulation_endpoint():
    """Validates /api/org/simulation for actual_as_of vs simulated_cro."""
    resp_actual = client.get("/api/org/simulation?mode=actual_as_of")
    assert resp_actual.status_code == 200
    d_actual = resp_actual.json()
    assert d_actual["mode"] == "actual_as_of"
    # In actual, Marketing reports to CEO
    mkt_actual = next(l for l in d_actual["reporting_lines"] if l["department"] == "Marketing")
    assert mkt_actual["role_title"] == "Head of Marketing"
    assert mkt_actual["reports_to_role"] == "CEO"
    assert mkt_actual["status"] == "active"

    resp_sim = client.get("/api/org/simulation?mode=simulated_cro")
    assert resp_sim.status_code == 200
    d_sim = resp_sim.json()
    assert d_sim["mode"] == "simulated_cro"
    # In simulated CRO, Marketing reports to CRO
    mkt_sim = next(l for l in d_sim["reporting_lines"] if l["department"] == "Marketing")
    assert mkt_sim["role_title"] == "Head of Marketing"
    assert mkt_sim["reports_to_role"] == "CRO"
    assert mkt_sim["status"] == "proposed"
    assert mkt_sim["is_unfilled_role"] is True


def test_t6b_future_activation_requires_confirmation():
    """Approved implementation may simulate future reporting, but no proposed line has an effective activation date."""
    db = SessionLocal()
    proposed = db.query(OrgReportingLine).filter(
        OrgReportingLine.status == "proposed",
        OrgReportingLine.department == "Marketing"
    ).all()
    db.close()

    assert len(proposed) == 1
    assert proposed[0].valid_from is None
    assert proposed[0].valid_to is None
    assert proposed[0].reports_to_person_id is None
    assert "T6b" in (proposed[0].source_ref or "")


def test_immutable_14_agent_roster():
    """Confirms people count is 19 and interviewable agents is exactly 14."""
    db = SessionLocal()
    people_count = db.query(Person).count()
    interviewable_count = db.query(Person).filter(Person.is_interviewable == True).count()
    db.close()
    assert people_count == 19
    assert interviewable_count == 14


# 8. Grounded Agent Chat
def test_agent_chat_day3_vikram():
    """Vikram acknowledges 15-Dec GA in Jira and August reliability crunch."""
    response = client.post("/api/agents/VX004/chat", json={
        "message": "Vikram, what is the current Atlas GA target date and status?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["emp_id"] == "VX004"
    assert "15-Dec" in data["reply"] or "December" in data["reply"] or "2026-12-15" in data["reply"]


def test_agent_chat_day3_sneha():
    """Sneha acknowledges 3 August SEV1s, paused perf tickets, and contractor on rota."""
    response = client.post("/api/agents/VX012/chat", json={
        "message": "Sneha, what happened with on-call and incidents in August?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["emp_id"] == "VX012"
    assert "SEV1" in data["reply"] or "incident" in data["reply"].lower()
    assert "contractor" in data["reply"].lower() or "rota" in data["reply"].lower()


def test_agent_chat_day3_priya():
    """Priya notes commits in atlas-engine and ownership discussion request."""
    response = client.post("/api/agents/VX007/chat", json={
        "message": "Priya, how is your workload on Atlas engine?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["emp_id"] == "VX007"
    assert "588" in data["reply"] or "commits" in data["reply"].lower()


def test_agent_chat_day3_nikhil():
    """Nikhil notes marketing spend claim, cold leads, unpublished website, and CRO rumors."""
    response = client.post("/api/agents/VX006/chat", json={
        "message": "Nikhil, what is happening with marketing and the launch kit?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["emp_id"] == "VX006"
    assert "unpublished" in data["reply"].lower() or "launch" in data["reply"].lower()


# 9. Endpoint Response Structures
def test_endpoint_engineering_overview():
    """Validates /api/engineering-overview response structure."""
    response = client.get("/api/engineering-overview")
    assert response.status_code == 200
    data = response.json()
    assert "atlas_ga" in data
    assert "jira_totals" in data
    assert "jira_epics" in data
    assert "august_sev1_count" in data
    assert "on_call_rota" in data
    assert "git_telemetry" in data
    assert data["august_sev1_count"] == 3


def test_endpoint_marketing_overview():
    """Validates /api/marketing-overview response structure."""
    response = client.get("/api/marketing-overview")
    assert response.status_code == 200
    data = response.json()
    assert "launch_kit_assets" in data
    assert "sid_departure_notes" in data
    assert "marketing_spend_claim" in data
    assert len(data["launch_kit_assets"]) == 5
    website_asset = next(a for a in data["launch_kit_assets"] if "Website" in a["asset_name"])
    assert website_asset["status"] == "Ready, unpublished"


def test_idempotent_ingestion_day3():
    """Verify running seed_day3_data multiple times does not duplicate records."""
    db = SessionLocal()
    initial_commits = db.query(GitCommit).count()
    initial_issues = db.query(JiraIssue).count()
    initial_incidents = db.query(Incident).count()
    initial_rota = db.query(OnCallEntry).count()
    initial_evidence = db.query(Evidence).count()

    # Run seed_day3_data again
    seed_day3_data(db)

    assert db.query(GitCommit).count() == initial_commits
    assert db.query(JiraIssue).count() == initial_issues
    assert db.query(Incident).count() == initial_incidents
    assert db.query(OnCallEntry).count() == initial_rota
    assert db.query(Evidence).count() == initial_evidence
    db.close()


def test_t6b_response_document_exists():
    """Verify VOICE_NOTE_RESPONSES/T6b.md exists and contains required sections."""
    t6b_path = Path("VOICE_NOTE_RESPONSES/T6b.md")
    assert t6b_path.exists()
    content = t6b_path.read_text(encoding="utf-8")
    assert "T6b" in content
    assert "ACCEPT WITH GUARDRAILS" in content
    assert "CRO" in content
    assert "E050" in content
    assert "Rollback" in content or "rollback" in content
