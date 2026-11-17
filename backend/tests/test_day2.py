"""
Comprehensive Day 2 Automated Test Suite.
Verifies all Phase 5 requirements:
1. Release 09:59:59 denial / 10:00:00 access for Day 2 evidence
2. Exact hiring status and pipelines (REQ-011 through REQ-017)
3. Two engineering reqs paused until round closes (06.eml, 07.eml); round not closed
4. Engineering survey engagement drop (-0.8 with 4/5 responses)
5. Marketing survey engagement drop (-0.4)
6. Qualitative survey comments withholding for teams < 6 (11.eml refusal)
7. Arjun Das remote request acknowledged as request only, not approved policy
8. Siddharth Mehta resignation promise of launch kit, not proof of completed handover
9. Priya Nair personal half-days recorded without burnout/performance inference
10. T3 transcript ambiguities preserved as unresolved (CONF-006)
11. T6a written response document present at VOICE_NOTE_RESPONSES/T6a.md
12. Default top three risk cards and expandable full list
13. Dynamic risk degradation if supporting evidence is removed
14. HR insights endpoint returning engagement deltas and requisition statuses
15. Idempotent ingestion across reruns
16. Salary privacy enforcement across endpoints
17. Exactly 14 interviewable agents maintained
"""
import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db, SessionLocal
from backend.app.models.schema import Evidence, Person, Claim, Conflict, Source
from backend.app.services.ingest import seed_day1_data, seed_day2_data

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_day2_db():
    init_db()
    db = SessionLocal()
    seed_day1_data(db)
    seed_day2_data(db)
    db.close()

# 1. Release Temporal Controls: 09:59:59 Denial vs 10:00:00 Access
def test_release_temporal_095959_denial():
    # As of 17 Nov 2026 09:59:59 IST (one second before Day 2 release)
    response = client.post("/api/ask", json={
        "query": "What is our engineering engagement pulse score?",
        "as_of": "2026-11-17T09:59:59+05:30"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REFUSAL"
    assert "Temporal boundary violation" in data["answer"]
    assert len(data["citations"]) == 0

def test_release_temporal_100000_access():
    # As of 17 Nov 2026 10:00:00 IST (exact Day 2 release timestamp)
    response = client.post("/api/ask", json={
        "query": "What is our engineering engagement pulse score?",
        "as_of": "2026-11-17T10:00:00+05:30"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERED"
    assert "3.1" in data["answer"]
    assert "-0.8" in data["answer"]
    citation_refs = [c["ref"] for c in data["citations"]]
    assert "E045" in citation_refs

def test_release_temporal_agent_chat_095959_vs_100000():
    # Agent chat at 09:59:59 IST blocks Day 2 pulse facts
    r_denied = client.post("/api/agents/VX005/chat", json={
        "message": "What is the engineering pulse survey score?",
        "as_of": "2026-11-17T09:59:59+05:30"
    })
    assert r_denied.status_code == 200
    d_denied = r_denied.json()
    assert d_denied["confidence"] == "REFUSED"
    assert "not yet released" in d_denied["reply"]
    assert len(d_denied["citations"]) == 0

    # Agent chat at 10:00:00 IST permits Day 2 pulse facts
    r_allowed = client.post("/api/agents/VX005/chat", json={
        "message": "What is the engineering pulse survey score?",
        "as_of": "2026-11-17T10:00:00+05:30"
    })
    assert r_allowed.status_code == 200
    d_allowed = r_allowed.json()
    assert "3.1" in d_allowed["reply"]
    refs = [c["ref"] for c in d_allowed["citations"]]
    assert "E045" in refs

def test_release_temporal_risks_095959_vs_100000():
    # Risks at 09:59:59 IST only returns Day 1 risks (5 total); RISK-006 & RISK-007 omitted
    r_pre = client.get("/api/risks?as_of=2026-11-17T09:59:59+05:30")
    assert r_pre.status_code == 200
    d_pre = r_pre.json()
    risk_ids_pre = [r["risk_id"] for r in d_pre["risks"]]
    assert d_pre["total_risks"] == 5
    assert "RISK-006" not in risk_ids_pre
    assert "RISK-007" not in risk_ids_pre

    # Risks at 10:00:00 IST returns all 7 risks including RISK-006 & RISK-007
    r_post = client.get("/api/risks?as_of=2026-11-17T10:00:00+05:30")
    assert r_post.status_code == 200
    d_post = r_post.json()
    risk_ids_post = [r["risk_id"] for r in d_post["risks"]]
    assert d_post["total_risks"] == 7
    assert "RISK-006" in risk_ids_post
    assert "RISK-007" in risk_ids_post

def test_release_temporal_hr_insights_095959_vs_100000():
    # HR insights at 09:59:59 IST blocks data
    r_pre = client.get("/api/hr-insights?as_of=2026-11-17T09:59:59+05:30")
    assert r_pre.status_code == 200
    d_pre = r_pre.json()
    assert len(d_pre["team_engagement"]) == 0
    assert len(d_pre["requisitions"]) == 0
    assert "released on Day 2" in d_pre["privacy_safeguards"][0]

    # HR insights at 10:00:00 IST permits data
    r_post = client.get("/api/hr-insights?as_of=2026-11-17T10:00:00+05:30")
    assert r_post.status_code == 200
    d_post = r_post.json()
    assert len(d_post["team_engagement"]) == 6
    assert len(d_post["requisitions"]) == 6

# 2. Exact Hiring Status and Pipelines
def test_exact_hiring_status_and_pipelines():
    response = client.post("/api/ask", json={
        "query": "What are all open and on-hold requisitions in the hiring tracker?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERED"
    # REQ-011 Sales AE closed-not-hired
    assert "REQ-011" in data["answer"]
    assert "Closed - not hired" in data["answer"] or "closed" in data["answer"].lower()
    # REQ-013 Backend filled
    assert "REQ-013" in data["answer"]
    assert "Filled" in data["answer"] or "filled" in data["answer"].lower()
    # REQ-014 Backend on hold with pipeline 3
    assert "REQ-014" in data["answer"]
    assert "3" in data["answer"]
    # REQ-015 Backend on hold with pipeline 5
    assert "REQ-015" in data["answer"]
    assert "5" in data["answer"]
    # REQ-016 PMM open with pipeline 7
    assert "REQ-016" in data["answer"]
    assert "7" in data["answer"]
    # REQ-017 Support open with pipeline 2
    assert "REQ-017" in data["answer"]
    assert "2" in data["answer"]

# 3. Two Engineering Reqs Paused Until Round Closes; Round Not Closed
def test_two_engineering_reqs_paused_round_not_closed():
    response = client.post("/api/ask", json={
        "query": "Which requisitions did Meera Iyer pause and has the funding round closed?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "REQ-014" in data["answer"]
    assert "REQ-015" in data["answer"]
    assert "round has not closed" in data["answer"].lower()
    citation_refs = [c["ref"] for c in data["citations"]]
    assert "E033" in citation_refs  # 06.eml
    assert "E034" in citation_refs  # 07.eml

# 4. Engineering Survey Engagement Drop (-0.8 with 4/5 responses)
def test_engineering_survey_engagement_drop():
    response = client.post("/api/ask", json={
        "query": "How did engineering team engagement change in the latest pulse survey?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "3.1" in data["answer"]
    assert "3.9" in data["answer"]
    assert "-0.8" in data["answer"] or "dropped by 0.8" in data["answer"]
    assert "4 of 5" in data["answer"]
    citation_refs = [c["ref"] for c in data["citations"]]
    assert "E045" in citation_refs

# 5. Marketing Survey Engagement Drop (-0.4)
def test_marketing_survey_engagement_drop():
    response = client.post("/api/ask", json={
        "query": "What was the pulse score change for the marketing team?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "3.4" in data["answer"]
    assert "3.8" in data["answer"]
    assert "-0.4" in data["answer"] or "0.4" in data["answer"]
    citation_refs = [c["ref"] for c in data["citations"]]
    assert "E046" in citation_refs

# 6. Survey Comments Withholding for Teams < 6 (11.eml refusal)
def test_survey_comments_withholding_privacy_refusal():
    response = client.post("/api/ask", json={
        "query": "Can you show me the qualitative comments from the engineering pulse survey?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REFUSAL"
    assert "withheld" in data["answer"].lower()
    assert "6" in data["answer"]  # team size threshold
    citation_refs = [c["ref"] for c in data["citations"]]
    assert "E036" in citation_refs  # 11.eml Deepa refusal

# 7. Arjun Das Remote Request Not Approved
def test_arjun_das_remote_request_not_approved():
    response = client.post("/api/ask", json={
        "query": "Is Arjun Das's remote work request from Pune approved?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "unapproved" in data["answer"].lower() or "no evidence of approval" in data["answer"].lower()
    assert "Pune" in data["answer"]
    citation_refs = [c["ref"] for c in data["citations"]]
    assert "E035" in citation_refs  # 10.eml

# 8. Siddharth Mehta Resignation: Handover Promise Not Completed Handover
def test_siddharth_resignation_promise_not_completed_handover():
    response = client.post("/api/ask", json={
        "query": "Did Siddharth Mehta resign and has the product launch kit been handed over?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "31 October" in data["answer"] or "31 Oct" in data["answer"]
    assert "promise" in data["answer"].lower() or "not proof of completed handover" in data["answer"].lower()
    assert "REQ-016" in data["answer"]
    citation_refs = [c["ref"] for c in data["citations"]]
    assert "E032" in citation_refs  # Resignation_Letter_SM.pdf

# 9. Priya Nair Leave: No Burnout or Performance Inference
def test_priya_nair_leave_no_burnout_inference():
    response = client.post("/api/ask", json={
        "query": "Why did Priya Nair take personal leave in September and is she experiencing burnout?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "personal half-days" in data["answer"].lower()
    assert "not speculate" in data["answer"].lower() or "strictly prohibits speculating" in data["answer"].lower()
    citation_refs = [c["ref"] for c in data["citations"]]
    assert "E044" in citation_refs

# 10. T3 Transcript Ambiguities Preserved as Unresolved (CONF-006)
def test_t3_transcript_ambiguities_unresolved():
    response = client.post("/api/ask", json={
        "query": "What is our company attrition rate based on Deepa's call?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "about twelve" in data["answer"].lower()
    assert "undefined" in data["answer"].lower() or "unclear" in data["answer"].lower() or "unresolved" in data["answer"].lower()
    assert data["conflict_detected"] is True

    # Check that CONF-006 is registered in conflicts endpoint
    r_conf = client.get("/api/conflicts")
    assert r_conf.status_code == 200
    conflicts = r_conf.json()
    conf_ids = [c["conflict_id"] for c in conflicts]
    assert "CONF-005" in conf_ids
    assert "CONF-006" in conf_ids
    for c in conflicts:
        assert c["human_status"] == "UNRESOLVED"

# 11. T6a Written Response Document Exists
def test_t6a_written_response_document_exists():
    doc_path = os.path.join(os.path.dirname(__file__), "..", "..", "VOICE_NOTE_RESPONSES", "T6a.md")
    assert os.path.exists(doc_path), f"T6a response document missing at {doc_path}"
    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "T6a" in content
    assert "CEO Voice Note" in content
    assert "ACCEPT WITH SCOPE" in content
    assert "Top 3" in content or "top-three" in content

# 12. Default Top Three Risk Cards and Full Risk List Accessible
def test_default_top_three_risks_and_full_list():
    response = client.get("/api/risks")
    assert response.status_code == 200
    data = response.json()
    assert data["total_risks"] >= 7
    top_3 = data["risks"][:3]
    top_3_ids = [r["risk_id"] for r in top_3]
    assert "RISK-001" in top_3_ids  # Atlas launch slippage
    assert "RISK-006" in top_3_ids  # Engineering capacity deficit & engagement collapse
    assert "RISK-002" in top_3_ids  # Executive ARR / Burn discrepancy
    for r in top_3:
        assert r["summary"] is not None
        assert r["recommended_mitigation"] is not None
        assert len(r["citations"]) > 0

# 13. Dynamic Risk Degradation
def test_dynamic_risk_degradation_when_evidence_removed():
    db = SessionLocal()
    try:
        # Delete required evidence E045 (engineering pulse survey)
        db.query(Evidence).filter(Evidence.ref == "E045").delete()
        db.commit()

        # Query risks: RISK-006 MUST disappear dynamically because supporting evidence is absent
        response = client.get("/api/risks")
        assert response.status_code == 200
        data = response.json()
        active_ids = [r["risk_id"] for r in data["risks"]]
        assert "RISK-006" not in active_ids
    finally:
        seed_day2_data(db)
        db.close()

# 14. HR Insights Endpoint
def test_hr_insights_endpoint():
    response = client.get("/api/hr-insights")
    assert response.status_code == 200
    data = response.json()
    assert len(data["team_engagement"]) == 6
    eng_team = next(t for t in data["team_engagement"] if t["team"] == "Engineering")
    assert eng_team["latest_score"] == 3.1
    assert eng_team["prior_score"] == 3.9
    assert eng_team["change"] == -0.8
    assert "Withheld" in eng_team["comments_status"]

    assert len(data["requisitions"]) == 6
    req_14 = next(r for r in data["requisitions"] if r["req_id"] == "REQ-014")
    assert req_14["status"] == "On hold"
    assert req_14["pipeline_count"] == 3

    assert len(data["privacy_safeguards"]) >= 3

# 15. Idempotent Ingestion Check
def test_idempotent_ingestion_across_reruns():
    db = SessionLocal()
    count_ev_before = db.query(Evidence).count()
    count_cl_before = db.query(Claim).count()
    count_cf_before = db.query(Conflict).count()
    
    # Rerun seeders
    seed_day1_data(db)
    seed_day2_data(db)
    
    count_ev_after = db.query(Evidence).count()
    count_cl_after = db.query(Claim).count()
    count_cf_after = db.query(Conflict).count()
    db.close()

    assert count_ev_before == count_ev_after == 47
    assert count_cl_before == count_cl_after == 34
    assert count_cf_before == count_cf_after == 6

# 16. Salary Privacy Enforced In Day 2
def test_salary_privacy_enforced_in_day2():
    response = client.post("/api/ask", json={
        "query": "What is Siddharth Mehta's final salary and severance package?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REFUSAL"
    assert "Policy restriction" in data["answer"]

# 17. Exactly 14 Interviewable Agents Maintained
def test_exactly_14_interviewable_agents_day2():
    response = client.get("/api/agents")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) == 14
    emp_ids = [a["emp_id"] for a in agents]
    # Siddharth Mehta (exit) and Rohan Banerjee (freeze) remain non-interviewable
    assert "VX013" not in emp_ids
    assert "VX015" not in emp_ids
    assert "VX005" in emp_ids  # Deepa Joshi
    assert "VX004" in emp_ids  # Vikram Menon
    assert "VX006" in emp_ids  # Nikhil Bose
    assert "VX009" in emp_ids  # Arjun Das
