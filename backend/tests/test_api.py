import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db_client

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_mock_db():
    # Setup mock data in the active DB client (which defaults to InMemoryDB if firestore credentials are missing)
    # Clear old items to ensure isolated tests
    if hasattr(db_client, "resolutions"):
        db_client.resolutions.clear()
    if hasattr(db_client, "invoices"):
        db_client.invoices.clear()
    if hasattr(db_client, "match_results"):
        db_client.match_results.clear()

def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

def test_api_dashboard_summary_empty():
    res = client.get("/dashboard-summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_processed"] == 0
    assert data["status_counts"]["auto_resolved"] == 0

def test_api_resolutions_empty():
    res = client.get("/resolutions")
    assert res.status_code == 200
    assert res.json() == []

def test_api_resolution_not_found():
    res = client.get("/resolutions/INV-MISSING")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

def test_api_process_invoice_invalid():
    # Missing field checks
    res = client.post("/process-invoice", json={"raw_text": "", "po_number": "PO-1001"})
    assert res.status_code == 422

    res = client.post("/process-invoice", json={"raw_text": "Sample text", "po_number": ""})
    assert res.status_code == 422

def test_api_resolutions_list_and_get():
    # Inject fake data into the in-memory store
    res_id = "INV-API-TEST"
    resolution_data = {
        "invoice_id": res_id,
        "status": "auto_resolved",
        "reasoning": "Matching successful.",
        "resolved_by": "policy_rule",
        "estimated_manual_cost": 12.0,
        "estimated_time_saved_minutes": 4.5
    }
    
    if hasattr(db_client, "save_resolution"):
        db_client.save_resolution(resolution_data)
        
    # Test GET list
    res = client.get("/resolutions")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["invoice_id"] == res_id

    # Test GET single
    res = client.get(f"/resolutions/{res_id}")
    assert res.status_code == 200
    assert res.json()["invoice_id"] == res_id

    # Test GET dashboard summary populated
    res = client.get("/dashboard-summary")
    assert res.status_code == 200
    summary = res.json()
    assert summary["total_processed"] == 1
    assert summary["total_cost_saved_usd"] == 12.0
