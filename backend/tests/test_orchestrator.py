import os
import sys
import pytest

# Ensure parent directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator import PipelineOrchestrator

# Mock FirestoreClient using in-memory dictionaries
class MockFirestoreClient:
    def __init__(self):
        self.invoices = {}
        self.match_results = {}
        self.resolutions = {}
        self.purchase_orders = {}
        self.goods_receipts = {}
        self.audit_logs = {}

    def save_invoice(self, invoice):
        self.invoices[invoice["invoice_id"]] = invoice

    def save_match_result(self, match_result):
        self.match_results[match_result["invoice_id"]] = match_result

    def save_resolution(self, resolution):
        self.resolutions[resolution["invoice_id"]] = resolution

    def save_audit_log(self, invoice_id, stage, data):
        if invoice_id not in self.audit_logs:
            self.audit_logs[invoice_id] = []
        self.audit_logs[invoice_id].append({
            "stage": stage,
            "data": data
        })

    def get_purchase_order(self, po_number):
        return self.purchase_orders.get(po_number)

    def get_goods_receipt(self, po_number):
        return self.goods_receipts.get(po_number)


# Mock Agents
class MockExtractorAgent:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def run(self, input_data):
        if self.should_fail:
            return {"success": False, "error": "Mocked extraction failure"}
        return {
            "success": True,
            "invoice": {
                "invoice_id": "INV-MOCK-1111",
                "vendor_name": "Mock Vendor",
                "invoice_date": "2026-07-06",
                "po_number": "PO-MOCK-2222",
                "currency": "USD",
                "line_items": [],
                "total_amount": 500.0,
                "raw_source": "pdf"
            }
        }

class MockMatcherAgent:
    def run(self, input_data):
        return {
            "success": True,
            "match_result": {
                "invoice_id": "INV-MOCK-1111",
                "po_number": "PO-MOCK-2222",
                "is_match": True,
                "discrepancies": []
            }
        }

class MockInvestigatorAgent:
    def run(self, input_data):
        return {
            "success": True,
            "resolution": {
                "invoice_id": "INV-MOCK-1111",
                "status": "auto_resolved",
                "reasoning": "Mocked policy approval",
                "resolved_by": "policy_rule",
                "estimated_manual_cost": 12.00,
                "estimated_time_saved_minutes": 4.5
            }
        }


def test_pipeline_orchestrator_success():
    db = MockFirestoreClient()
    
    # Pre-populate purchase orders and receipts in mock db
    db.purchase_orders["PO-MOCK-2222"] = {
        "po_number": "PO-MOCK-2222",
        "vendor_name": "Mock Vendor",
        "line_items": [],
        "total_amount": 500.0,
        "status": "open"
    }
    db.goods_receipts["PO-MOCK-2222"] = {
        "po_number": "PO-MOCK-2222",
        "received_items": [],
        "receipt_date": "2026-07-05"
    }

    orchestrator = PipelineOrchestrator(
        extractor_agent=MockExtractorAgent(),
        matcher_agent=MockMatcherAgent(),
        investigator_agent=MockInvestigatorAgent(),
        firestore_client=db
    )

    result = orchestrator.process_invoice(
        raw_text="Mock invoice OCR content...",
        po_number="PO-MOCK-2222"
    )

    # Asserts
    assert result["invoice_id"] == "INV-MOCK-1111"
    assert result["stage_failed"] is None
    assert result["match_result"]["is_match"] is True
    assert result["resolution"]["status"] == "auto_resolved"

    # Verify mock database persistence
    assert "INV-MOCK-1111" in db.invoices
    assert "INV-MOCK-1111" in db.match_results
    assert "INV-MOCK-1111" in db.resolutions
    
    # Verify mock database audit trails
    logs = db.audit_logs["INV-MOCK-1111"]
    stages = [log["stage"] for log in logs]
    assert "extraction" in stages
    assert "matching" in stages
    assert "investigation" in stages


def test_pipeline_orchestrator_extraction_failure():
    db = MockFirestoreClient()
    
    orchestrator = PipelineOrchestrator(
        extractor_agent=MockExtractorAgent(should_fail=True),
        matcher_agent=MockMatcherAgent(),
        investigator_agent=MockInvestigatorAgent(),
        firestore_client=db
    )

    result = orchestrator.process_invoice(
        raw_text="Broken invoice text...",
        po_number="PO-MOCK-2222"
    )

    # Asserts
    assert result["invoice_id"] is None
    assert result["stage_failed"] == "extraction"
    assert result["match_result"] is None
    assert result["resolution"] is None
