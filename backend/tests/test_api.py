import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main
from main import app

client = TestClient(app)

class FakeDBClient:
    def __init__(self):
        self.invoices = {}
        self.match_results = {}
        self.resolutions = {}

    def get_resolution(self, invoice_id):
        return self.resolutions.get(invoice_id)

    def get_all_resolutions(self):
        return list(self.resolutions.values())

    def save_resolution(self, resolution):
        self.resolutions[resolution["invoice_id"]] = resolution

    def save_invoice(self, invoice):
        self.invoices[invoice["invoice_id"]] = invoice

    def save_match_result(self, match_result):
        self.match_results[match_result["invoice_id"]] = match_result

@pytest.fixture(autouse=True)
def setup_mock_db():
    # Instantiate and override the main app's db_client with our clean in-memory client
    fake_db = FakeDBClient()
    main.db_client = fake_db
    yield
    # No cleanup necessary as we re-override every test

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
    res_id = "INV-API-TEST"
    resolution_data = {
        "invoice_id": res_id,
        "status": "auto_resolved",
        "reasoning": "Matching successful.",
        "resolved_by": "policy_rule",
        "estimated_manual_cost": 12.0,
        "estimated_time_saved_minutes": 4.5
    }
    
    main.db_client.save_resolution(resolution_data)
        
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
