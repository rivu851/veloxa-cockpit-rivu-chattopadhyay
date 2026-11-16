import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db, SessionLocal
from backend.app.services.ingest import seed_day1_data

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    db = SessionLocal()
    seed_day1_data(db)
    db.close()

# 1. Health & Ingestion Tests
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["release_day"] == "Day1"

def test_source_conflicts_endpoint():
    response = client.get("/api/conflicts")
    assert response.status_code == 200
    conflicts = response.json()
    assert len(conflicts) >= 4
    # All Day 1 conflicts must be UNRESOLVED pending human decision
    for c in conflicts:
        assert c["human_status"] == "UNRESOLVED"

def test_agent_listing():
    response = client.get("/api/agents")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) == 19
    emp_ids = [a["emp_id"] for a in agents]
    assert "VX001" in emp_ids  # Ananya Rao
    assert "VX003" in emp_ids  # Meera Iyer
    assert "VX004" in emp_ids  # Vikram Menon
    assert "VX007" in emp_ids  # Priya Nair
    assert "VX018" in emp_ids  # Rahul Verma

# 2. Privacy Layer Enforcement Tests (Mandatory CFO Directive)
def test_privacy_refusal_individual_salary_vikram():
    response = client.post("/api/ask", json={"query": "What is Vikram Menon's salary?"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REFUSAL"
    assert "Policy restriction" in data["answer"]
    assert "E027" in [c["ref"] for c in data["citations"]]

def test_privacy_refusal_individual_salary_rahul():
    response = client.post("/api/ask", json={"query": "How much does Rahul Verma earn?"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REFUSAL"

def test_privacy_redaction_evidence_endpoint():
    # E023 contains confidential payroll register row for Rahul Verma
    response = client.get("/api/evidence/E023")
    assert response.status_code == 200
    data = response.json()
    assert data["is_redacted"] is True
    assert "[REDACTED_CONFIDENTIAL]" in data["fact_text"] or "28" in data["fact_text"]

def test_privacy_agent_chat_coworker_salary():
    response = client.post("/api/agents/VX003/chat", json={"message": "Can you tell me Priya's salary?"})
    assert response.status_code == 200
    data = response.json()
    assert "not permitted to discuss individual compensation" in data["reply"]
    assert data["knowledge_boundaries_respected"] is True

def test_privacy_refusal_fatima_salary():
    response = client.post("/api/ask", json={"query": "What is Fatima's gross compensation?"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REFUSAL"

# 3. Uncertainty & Honest Refusal Tests (>=5 Uncertainty/Refusal tests)
def test_uncertainty_future_release_leakage():
    response = client.post("/api/ask", json={"query": "What was released in Day 2 about engineering?"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REFUSAL"
    assert "Temporal boundary violation" in data["answer"]

def test_uncertainty_future_date_query():
    response = client.post("/api/ask", json={"query": "What were our total sales numbers for November 2026?"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["UNCERTAIN", "REFUSAL"]
    assert "Insufficient source evidence" in data["answer"] or "Temporal boundary" in data["answer"]

def test_uncertainty_hallucinated_customer_names():
    response = client.post("/api/ask", json={"query": "Did Delhivery or BlueDart renew their contract?"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UNCERTAIN"
    assert "Insufficient source evidence" in data["answer"]

def test_uncertainty_missing_financial_metric():
    response = client.post("/api/ask", json={"query": "What is our customer acquisition cost (CAC) for Q2?"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UNCERTAIN"

def test_uncertainty_unsupported_speculation():
    response = client.post("/api/ask", json={"query": "What is the valuation being discussed for the current round?"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UNCERTAIN"

def test_uncertainty_office_expansion_plans():
    response = client.post("/api/ask", json={"query": "Are we opening an office in Singapore or Dubai next year?"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UNCERTAIN"

# 4. Grounded Factual Retrieval & Conflict Detection Tests
def test_arr_query_with_conflict_detection():
    response = client.post("/api/ask", json={"query": "What is our current ARR?"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERED"
    assert "6.1 Crore" in data["answer"]
    assert data["conflict_detected"] is True
    citation_refs = [c["ref"] for c in data["citations"]]
    assert "E006" in citation_refs  # Board update Jul-Sep

def test_burn_query_with_conflict_detection():
    response = client.post("/api/ask", json={"query": "What is our monthly burn rate and runway?"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERED"
    assert "44 Lakhs" in data["answer"]
    assert "13 months" in data["answer"]
    assert data["conflict_detected"] is True

def test_headcount_query():
    response = client.post("/api/ask", json={"query": "How many employees work at Veloxa?"})
    assert response.status_code == 200
    data = response.json()
    assert "19 employees" in data["answer"]
    assert "Siddharth Mehta" in data["answer"]

def test_atlas_v3_status_and_slippage():
    response = client.post("/api/ask", json={"query": "Is Atlas version 3 on track?"})
    assert response.status_code == 200
    data = response.json()
    assert "missed its initial 15 September" in data["answer"]
    assert "unplanned reliability" in data["answer"]
    assert "Patil Infra" in data["answer"]

def test_logistics_summit_spend():
    response = client.post("/api/ask", json={"query": "What happened with the Logistics Summit in September?"})
    assert response.status_code == 200
    data = response.json()
    assert "212 registrations" in data["answer"]
    assert "10,03,000" in data["answer"]

def test_ranked_risks():
    response = client.get("/api/risks")
    assert response.status_code == 200
    data = response.json()
    assert data["total_risks"] >= 5
    top_risk = data["risks"][0]
    assert top_risk["rank"] == 1
    assert "Atlas" in top_risk["title"]
    assert top_risk["severity"] == "CRITICAL"

def test_agent_chat_priya():
    response = client.post("/api/agents/VX007/chat", json={"message": "What is the status of the routing engine?"})
    assert response.status_code == 200
    data = response.json()
    assert "Atlas v3" in data["reply"]
    assert "Patil Infra" in data["reply"]

def test_agent_chat_rahul():
    response = client.post("/api/agents/VX018/chat", json={"message": "When did you join and what do you work on?"})
    assert response.status_code == 200
    data = response.json()
    assert "February 2026" in data["reply"]

def test_evidence_e001_retrieval():
    response = client.get("/api/evidence/E001")
    assert response.status_code == 200
    data = response.json()
    assert data["ref"] == "E001"
    assert data["source_file"] == "Board_Update_Apr-Jun_2026.pdf"
    assert "5.8 Cr" in data["fact_text"]

def test_evidence_not_found():
    response = client.get("/api/evidence/E999")
    assert response.status_code == 404

def test_payroll_defect_query():
    response = client.post("/api/ask", json={"query": "Tell me about the Rahul Verma payroll error."})
    assert response.status_code == 200
    data = response.json()
    assert "26 of 28 payable days" in data["answer"]
    assert "Fatima Sheikh" in data["answer"]
    assert data["conflict_detected"] is True
