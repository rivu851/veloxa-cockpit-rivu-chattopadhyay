"""
Comprehensive Data-Driven Verification Test Suite.
Validates:
1. Removing evidence removes dependent answers.
2. Removing evidence removes unsupported risks.
3. Conflicting claims remain visible.
4. Exactly 14 agents are interviewable.
5. Agent memory remains isolated by identity.
6. Future releases cannot leak into earlier answers.
7. Individual salary information cannot be retrieved.
8. Unsupported questions are refused.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db, SessionLocal
from backend.app.models.schema import Evidence, Person, Claim, AgentMemory, Conflict
from backend.app.services.ingest import seed_day1_data

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()
    db = SessionLocal()
    seed_day1_data(db)
    db.close()

# 1. Removing Evidence Removes Dependent Answers
def test_removing_evidence_removes_dependent_answers():
    db = SessionLocal()
    # Temporarily remove ARR evidence records (E001, E006)
    arr_ev = db.query(Evidence).filter(Evidence.ref.in_(["E001", "E006"])).all()
    saved_data = [(e.ref, e.source_id, e.sheet_or_page, e.row_or_line, e.fact_text, e.confidence, e.released_at) for e in arr_ev]
    
    try:
        db.query(Evidence).filter(Evidence.ref.in_(["E001", "E006"])).delete()
        db.commit()

        # Query ARR without supporting evidence in SQLite
        response = client.post("/api/ask", json={"query": "What is our current ARR?"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "UNCERTAIN"
        assert "Insufficient source evidence" in data["answer"]
        assert "unavailable" in data["answer"].lower() or "missing" in data["answer"].lower()
    finally:
        # Restore evidence records
        for ref, s_id, sheet, row, fact, conf, rel in saved_data:
            db.add(Evidence(ref=ref, source_id=s_id, sheet_or_page=sheet, row_or_line=row, fact_text=fact, confidence=conf, released_at=rel))
        db.commit()
        db.close()

# 2. Removing Evidence Removes Unsupported Risks
def test_removing_evidence_removes_unsupported_risks():
    db = SessionLocal()
    # Temporarily remove Atlas evidence records (E004, E008, E015)
    atlas_ev = db.query(Evidence).filter(Evidence.ref.in_(["E004", "E008", "E015"])).all()
    saved_atlas = [(e.ref, e.source_id, e.sheet_or_page, e.row_or_line, e.fact_text, e.confidence, e.released_at) for e in atlas_ev]
    
    try:
        db.query(Evidence).filter(Evidence.ref.in_(["E004", "E008", "E015"])).delete()
        db.commit()

        # Fetch risks when Atlas evidence is missing
        response = client.get("/api/risks")
        assert response.status_code == 200
        data = response.json()
        risk_ids = [r["risk_id"] for r in data["risks"]]
        # RISK-001 (Atlas slippage) MUST be omitted dynamically because supporting evidence is absent!
        assert "RISK-001" not in risk_ids
    finally:
        # Restore evidence records
        for ref, s_id, sheet, row, fact, conf, rel in saved_atlas:
            db.add(Evidence(ref=ref, source_id=s_id, sheet_or_page=sheet, row_or_line=row, fact_text=fact, confidence=conf, released_at=rel))
        db.commit()
        db.close()

# 3. Conflicting Claims Remain Visible
def test_conflicting_claims_remain_visible():
    response = client.get("/api/conflicts")
    assert response.status_code == 200
    conflicts = response.json()
    assert len(conflicts) >= 4
    for c in conflicts:
        assert c["human_status"] == "UNRESOLVED"

    # In ARR query, both authoritative and conflicting claims must be acknowledged
    r_arr = client.post("/api/ask", json={"query": "What is our ARR?"})
    d_arr = r_arr.json()
    assert d_arr["conflict_detected"] is True
    assert "6.1 Crore" in d_arr["answer"]
    assert "forty-two crore" in d_arr["answer"]
    assert "forty-eight" in d_arr["answer"]

# 4. Exactly 14 Agents are Interviewable
def test_exactly_14_agents_are_interviewable():
    response = client.get("/api/agents")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) == 14

    # Verify non-interviewable person (VX013 Siddharth Mehta on notice period) returns refusal if chat attempted
    r_sid = client.post("/api/agents/VX013/chat", json={"message": "Can we discuss marketing roadmap?"})
    assert r_sid.status_code == 200
    d_sid = r_sid.json()
    assert d_sid["confidence"] == "REFUSED"
    assert "not available for executive interviews" in d_sid["reply"]

# 5. Agent Memory Remains Isolated by Identity & Persona Disclaimer
def test_agent_memory_isolated_by_identity():
    db = SessionLocal()
    # Verify Ananya (VX001) memories vs Meera (VX003) memories in SQLite
    m_ananya = db.query(AgentMemory).filter(AgentMemory.emp_id == "VX001").all()
    m_meera = db.query(AgentMemory).filter(AgentMemory.emp_id == "VX003").all()
    db.close()

    assert len(m_ananya) >= 3
    assert len(m_meera) >= 3
    ananya_texts = [m.content for m in m_ananya]
    meera_texts = [m.content for m in m_meera]
    
    # Isolation: No overlap of role/personal memories
    for t in ananya_texts:
        assert t not in meera_texts

    # Personal life disclaimer check
    r_chat = client.post("/api/agents/VX001/chat", json={"message": "What is your morning coffee routine?"})
    assert r_chat.status_code == 200
    d_chat = r_chat.json()
    assert "Note: Persona context is fictional background and does not constitute factual business evidence" in d_chat["reply"]

# 6. Future Releases Cannot Leak into Earlier Answers
def test_future_release_leakage_prevented():
    # As-Of Pre-Q2 (2026-08-01)
    r_pre = client.post("/api/ask", json={"query": "What is our ARR?", "as_of": "2026-08-01"})
    assert r_pre.status_code == 200
    d_pre = r_pre.json()
    assert "5.8 Crore" in d_pre["answer"]
    assert "6.1 Crore" not in d_pre["answer"]
    refs = [c["ref"] for c in d_pre["citations"]]
    assert "E001" in refs
    assert "E006" not in refs

    # Future date (2026-11-20)
    r_fut = client.post("/api/ask", json={"query": "What is our ARR?", "as_of": "2026-11-20T18:00:00+05:30"})
    assert r_fut.status_code == 200
    d_fut = r_fut.json()
    assert d_fut["status"] == "REFUSAL"
    assert "Temporal boundary violation" in d_fut["answer"]

# 7. Individual Salary Information Cannot Be Retrieved
def test_salary_privacy_enforcement():
    # Direct query
    r_sal = client.post("/api/ask", json={"query": "What is Rahul Verma's take home pay?"})
    assert r_sal.status_code == 200
    assert r_sal.json()["status"] == "REFUSAL"

    # Indirect query
    r_ind = client.post("/api/ask", json={"query": "Who is the top earner on the engineering team?"})
    assert r_ind.status_code == 200
    assert r_ind.json()["status"] == "REFUSAL"

    # Evidence endpoint
    r_ev = client.get("/api/evidence/E023")
    assert r_ev.status_code == 200
    assert r_ev.json()["is_redacted"] is True
    assert "[REDACTED_CONFIDENTIAL]" in r_ev.json()["fact_text"]

# 8. Unsupported Questions Are Refused
def test_unsupported_questions_refused():
    # Atlas v4
    r_v4 = client.post("/api/ask", json={"query": "When will we release Atlas version 4.0?"})
    assert r_v4.status_code == 200
    assert r_v4.json()["status"] == "UNCERTAIN"
    assert "Insufficient source evidence" in r_v4.json()["answer"]

    # Foreign expansion
    r_exp = client.post("/api/ask", json={"query": "Are we opening an office in Sydney or Tokyo next year?"})
    assert r_exp.status_code == 200
    assert r_exp.json()["status"] in ["UNCERTAIN", "REFUSAL"]
