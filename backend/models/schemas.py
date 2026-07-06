from pydantic import BaseModel, Field
from typing import List

class LineItem(BaseModel):
    """Represents an individual itemized line in an invoice, purchase order, or goods receipt."""
    description: str
    quantity: float
    unit_price: float
    line_total: float

class Invoice(BaseModel):
    """Represents a vendor invoice to be processed and matched."""
    invoice_id: str
    vendor_name: str
    invoice_date: str  # ISO format
    po_number: str
    currency: str
    line_items: List[LineItem]
    total_amount: float
    raw_source: str  # "pdf" or "image"

class PurchaseOrder(BaseModel):
    """Represents an internal purchase order against which invoices are matched."""
    po_number: str
    vendor_name: str
    line_items: List[LineItem]
    total_amount: float
    status: str  # "open", "closed", "partially_received"

class GoodsReceipt(BaseModel):
    """Represents proof of received goods or services for matching verification."""
    po_number: str
    received_items: List[LineItem]
    receipt_date: str

class MatchDiscrepancy(BaseModel):
    """Represents a discrepancy found when matching an invoice against a purchase order."""
    field: str  # e.g. "total_amount", "line_item_quantity"
    invoice_value: str
    po_value: str
    severity: str  # "minor", "major"

class MatchResult(BaseModel):
    """Represents the outcome of matching an invoice against its associated purchase order."""
    invoice_id: str
    po_number: str
    is_match: bool
    discrepancies: List[MatchDiscrepancy]

class Resolution(BaseModel):
    """Represents the resolution decision and metrics for a matched invoice."""
    invoice_id: str
    status: str  # "auto_resolved", "escalated"
    reasoning: str  # human-readable explanation of the decision
    resolved_by: str  # "policy_rule" or "gemini_investigation" or "human_required"
    estimated_manual_cost: float  # in dollars
    estimated_time_saved_minutes: float

class ProcessInvoiceRequest(BaseModel):
    """Represents a request to process a raw invoice OCR text against a PO."""
    raw_text: str
    po_number: str


if __name__ == "__main__":
    # Create dummy LineItem
    line_item = LineItem(
        description="Widget A",
        quantity=10.0,
        unit_price=5.0,
        line_total=50.0
    )
    print("LineItem Example:")
    print(line_item.model_dump_json(indent=2))
    print("-" * 40)

    # Create dummy Invoice
    invoice = Invoice(
        invoice_id="INV-1001",
        vendor_name="Acme Corp",
        invoice_date="2026-07-06T00:00:00Z",
        po_number="PO-5001",
        currency="USD",
        line_items=[line_item],
        total_amount=50.0,
        raw_source="pdf"
    )
    print("Invoice Example:")
    print(invoice.model_dump_json(indent=2))
    print("-" * 40)

    # Create dummy PurchaseOrder
    po = PurchaseOrder(
        po_number="PO-5001",
        vendor_name="Acme Corp",
        line_items=[line_item],
        total_amount=50.0,
        status="open"
    )
    print("PurchaseOrder Example:")
    print(po.model_dump_json(indent=2))
    print("-" * 40)

    # Create dummy GoodsReceipt
    receipt = GoodsReceipt(
        po_number="PO-5001",
        received_items=[line_item],
        receipt_date="2026-07-05"
    )
    print("GoodsReceipt Example:")
    print(receipt.model_dump_json(indent=2))
    print("-" * 40)

    # Create dummy MatchDiscrepancy
    discrepancy = MatchDiscrepancy(
        field="line_item_quantity",
        invoice_value="10.0",
        po_value="8.0",
        severity="minor"
    )
    print("MatchDiscrepancy Example:")
    print(discrepancy.model_dump_json(indent=2))
    print("-" * 40)

    # Create dummy MatchResult
    match_result = MatchResult(
        invoice_id="INV-1001",
        po_number="PO-5001",
        is_match=False,
        discrepancies=[discrepancy]
    )
    print("MatchResult Example:")
    print(match_result.model_dump_json(indent=2))
    print("-" * 40)

    # Create dummy Resolution
    resolution = Resolution(
        invoice_id="INV-1001",
        status="auto_resolved",
        reasoning="Quantity discrepancy is within tolerable 10% deviation policy.",
        resolved_by="policy_rule",
        estimated_manual_cost=15.0,
        estimated_time_saved_minutes=12.5
    )
    print("Resolution Example:")
    print(resolution.model_dump_json(indent=2))
    print("-" * 40)
