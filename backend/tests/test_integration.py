import os
import sys
import pytest
from unittest.mock import MagicMock

# Ensure backend root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator import PipelineOrchestrator
from agents.extractor import ExtractorAgent
from agents.matcher import MatcherAgent
from agents.investigator import InvestigatorAgent

class MockFirestoreClient:
    def __init__(self):
        self.invoices = {}
        self.match_results = {}
        self.resolutions = {}
        self.purchase_orders = {}
        self.goods_receipts = {}
        
        self.save_invoice = MagicMock()
        self.save_match_result = MagicMock()
        self.save_resolution = MagicMock()
        self.save_audit_log = MagicMock()

    def get_purchase_order(self, po_number):
        return self.purchase_orders.get(po_number)

    def get_goods_receipt(self, po_number):
        return self.goods_receipts.get(po_number)

class MockGeminiClient:
    def __init__(self, mode="clean"):
        self.mode = mode

    def extract_structured(self, prompt, response_schema):
        if self.mode == "clean":
            return {
                "invoice_id": "INV-INT-CLEAN",
                "vendor_name": "Clean Vendor",
                "invoice_date": "2026-07-06",
                "po_number": "PO-CLEAN",
                "currency": "USD",
                "line_items": [{"description": "Widget", "quantity": 10.0, "unit_price": 10.0, "line_total": 100.0}],
                "total_amount": 100.0,
                "raw_source": "pdf"
            }
        elif self.mode == "minor":
            return {
                "invoice_id": "INV-INT-MINOR",
                "vendor_name": "Minor Vendor",
                "invoice_date": "2026-07-06",
                "po_number": "PO-MINOR",
                "currency": "USD",
                "line_items": [{"description": "Widget", "quantity": 10.0, "unit_price": 10.1, "line_total": 101.0}],
                "total_amount": 101.0,
                "raw_source": "pdf"
            }
        else:
            return {
                "invoice_id": "INV-INT-MAJOR",
                "vendor_name": "Major Vendor",
                "invoice_date": "2026-07-06",
                "po_number": "PO-MAJOR",
                "currency": "USD",
                "line_items": [{"description": "Widget", "quantity": 10.0, "unit_price": 20.0, "line_total": 200.0}],
                "total_amount": 200.0,
                "raw_source": "pdf"
            }

    def reason(self, prompt):
        return "ACTION: escalate_to_finance_manager\nMajor discrepancy found."


def test_pipeline_integration_clean():
    db = MockFirestoreClient()
    db.purchase_orders["PO-CLEAN"] = {
        "po_number": "PO-CLEAN",
        "vendor_name": "Clean Vendor",
        "line_items": [{"description": "Widget", "quantity": 10.0, "unit_price": 10.0, "line_total": 100.0}],
        "total_amount": 100.0,
        "status": "open"
    }

    extractor = ExtractorAgent()
    extractor.client = MockGeminiClient(mode="clean")
    
    matcher = MatcherAgent()
    
    investigator = InvestigatorAgent()
    investigator.client = MockGeminiClient(mode="clean")

    orchestrator = PipelineOrchestrator(extractor, matcher, investigator, db)

    res = orchestrator.process_invoice("Clean OCR text", "PO-CLEAN")

    assert res["invoice_id"] == "INV-INT-CLEAN"
    assert res["stage_failed"] is None
    assert res["match_result"]["is_match"] is True
    assert res["resolution"]["status"] == "auto_resolved"
    assert res["resolution"]["resolved_by"] == "policy_rule"
    assert res["resolution"]["estimated_manual_cost"] >= 0
    assert res["resolution"]["estimated_time_saved_minutes"] >= 0

    # Assert database calls
    db.save_invoice.assert_called_once()
    db.save_match_result.assert_called_once()
    db.save_resolution.assert_called_once()
    assert db.save_audit_log.call_count == 3  # extraction, matching, investigation

def test_pipeline_integration_minor():
    db = MockFirestoreClient()
    db.purchase_orders["PO-MINOR"] = {
        "po_number": "PO-MINOR",
        "vendor_name": "Minor Vendor",
        "line_items": [{"description": "Widget", "quantity": 10.0, "unit_price": 10.0, "line_total": 100.0}],
        "total_amount": 100.0,
        "status": "open"
    }

    extractor = ExtractorAgent()
    extractor.client = MockGeminiClient(mode="minor")
    
    matcher = MatcherAgent()
    
    investigator = InvestigatorAgent()
    investigator.client = MockGeminiClient(mode="minor")

    orchestrator = PipelineOrchestrator(extractor, matcher, investigator, db)

    res = orchestrator.process_invoice("Minor variance OCR text", "PO-MINOR")

    assert res["invoice_id"] == "INV-INT-MINOR"
    assert res["match_result"]["is_match"] is False
    assert res["resolution"]["status"] == "auto_resolved"
    assert res["resolution"]["resolved_by"] == "policy_rule"

def test_pipeline_integration_major():
    db = MockFirestoreClient()
    db.purchase_orders["PO-MAJOR"] = {
        "po_number": "PO-MAJOR",
        "vendor_name": "Major Vendor",
        "line_items": [{"description": "Widget", "quantity": 10.0, "unit_price": 10.0, "line_total": 100.0}],
        "total_amount": 100.0,
        "status": "open"
    }

    extractor = ExtractorAgent()
    extractor.client = MockGeminiClient(mode="major")
    
    matcher = MatcherAgent()
    
    investigator = InvestigatorAgent()
    investigator.client = MockGeminiClient(mode="major")

    orchestrator = PipelineOrchestrator(extractor, matcher, investigator, db)

    res = orchestrator.process_invoice("Major exception OCR text", "PO-MAJOR")

    assert res["invoice_id"] == "INV-INT-MAJOR"
    assert res["match_result"]["is_match"] is False
    assert res["resolution"]["status"] == "escalated"
    assert res["resolution"]["resolved_by"] == "gemini_investigation"
