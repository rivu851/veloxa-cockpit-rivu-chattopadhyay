import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import threading
import time
import uvicorn
import httpx

def run_server():
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, log_level="error")

def main():
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(2)

    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=10.0) as client:
        print("=== 1. FASTAPI STARTUP & DOCS VERIFICATION ===")
        r_docs = client.get("/docs")
        print(f"/docs -> HTTP {r_docs.status_code} (HTML length: {len(r_docs.text)})")

        r_openapi = client.get("/openapi.json")
        openapi_data = r_openapi.json()
        print(f"/openapi.json -> HTTP {r_openapi.status_code} (title: '{openapi_data.get('info', {}).get('title')}', endpoints: {len(openapi_data.get('paths', {}))})")

        r_health = client.get("/health")
        print(f"/health -> HTTP {r_health.status_code} (response: {r_health.json()})")

        print("\n=== 2. QUERY: ARR ===")
        r_arr = client.post("/api/ask", json={"query": "What is our current ARR?"})
        data_arr = r_arr.json()
        print(f"Status: HTTP {r_arr.status_code}")
        print(f"Answer: {data_arr['answer']}")
        print(f"Citations: {[c['ref'] + ' (' + c['source_file'] + ')' for c in data_arr['citations']]}")
        print(f"Conflict: {data_arr.get('conflict_details')}")

        print("\n=== 3. QUERY: MONTHLY BURN ===")
        r_burn = client.post("/api/ask", json={"query": "What is our monthly burn rate and runway?"})
        data_burn = r_burn.json()
        print(f"Status: HTTP {r_burn.status_code}")
        print(f"Answer: {data_burn['answer']}")
        print(f"Citations: {[c['ref'] + ' (' + c['source_file'] + ')' for c in data_burn['citations']]}")
        print(f"Conflict: {data_burn.get('conflict_details')}")

        print("\n=== 4. QUERY: HEADCOUNT ===")
        r_hc = client.post("/api/ask", json={"query": "How many employees work at Veloxa?"})
        data_hc = r_hc.json()
        print(f"Status: HTTP {r_hc.status_code}")
        print(f"Answer: {data_hc['answer']}")
        print(f"Citations: {[c['ref'] + ' (' + c['source_file'] + ')' for c in data_hc['citations']]}")
        print(f"Conflict: {data_hc.get('conflict_details')}")

        print("\n=== 5. QUERY: ATLAS DELAY ===")
        r_atlas = client.post("/api/ask", json={"query": "Is Atlas version 3 on track?"})
        data_atlas = r_atlas.json()
        print(f"Status: HTTP {r_atlas.status_code}")
        print(f"Answer: {data_atlas['answer']}")
        print(f"Citations: {[c['ref'] + ' (' + c['source_file'] + ')' for c in data_atlas['citations']]}")

        print("\n=== 6. ENDPOINT: RANKED BUSINESS RISKS ===")
        r_risks = client.get("/api/risks")
        data_risks = r_risks.json()
        print(f"Status: HTTP {r_risks.status_code} (Total risks: {data_risks['total_risks']})")
        for r in data_risks["risks"]:
            print(f"Rank {r['rank']} [{r['severity']}]: {r['title']} (Refs: {r['evidence_refs']})")

        print("\n=== 7. TEMPORAL PROBES (AS-OF FILTERING & BOUNDARY REFUSAL) ===")
        r_temp_pre = client.post("/api/ask", json={"query": "What is our current ARR?", "as_of": "2026-08-01"})
        data_temp_pre = r_temp_pre.json()
        print(f"As-Of 2026-08-01 (Pre-Q2) -> Answer: {data_temp_pre['answer']}")
        print(f"As-Of 2026-08-01 Citations: {[c['ref'] for c in data_temp_pre['citations']]}")

        r_temp_fut = client.post("/api/ask", json={"query": "What is our ARR?", "as_of": "2026-11-20T18:00:00+05:30"})
        data_temp_fut = r_temp_fut.json()
        print(f"As-Of 2026-11-20 (Future) -> Status: {data_temp_fut['status']} | Answer: {data_temp_fut['answer']}")

        print("\n=== 8. PRIVACY REFUSAL PROBES ===")
        r_sal = client.post("/api/ask", json={"query": "What is Vikram Menon's salary?"})
        data_sal = r_sal.json()
        print(f"Direct Salary Query -> Status: {data_sal['status']} | Refusal Reason: {data_sal['refusal_reason']}")

        r_sal_ind = client.post("/api/ask", json={"query": "Who is the highest paid engineer?"})
        data_sal_ind = r_sal_ind.json()
        print(f"Indirect Inference Query -> Status: {data_sal_ind['status']} | Refusal Reason: {data_sal_ind['refusal_reason']}")

        r_ev_red = client.get("/api/evidence/E023")
        data_ev_red = r_ev_red.json()
        print(f"Evidence E023 Redacted -> is_redacted: {data_ev_red['is_redacted']} | Text: {data_ev_red['fact_text']}")

if __name__ == "__main__":
    main()
