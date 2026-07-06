import os
import sys

# Ensure parent directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base import Agent
from models.schemas import MatchResult, MatchDiscrepancy, Invoice, PurchaseOrder, GoodsReceipt
from policy.rules import classify_amount_variance, classify_line_item_variance

class MatcherAgent(Agent):
    """
    Agent responsible for performing a 3-way match comparing an Invoice,
    a Purchase Order, and optionally a Goods Receipt.
    """
    def __init__(self):
        self._name = "matcher"

    @property
    def name(self) -> str:
        return self._name

    def run(self, input_data: dict) -> dict:
        """
        Performs 3-way matching on accounts payable documents.
        
        Args:
            input_data (dict): Contains:
                - "invoice": dict
                - "purchase_order": dict
                - "goods_receipt": dict | None
                
        Returns:
            dict: {"success": bool, "match_result": dict, "error": str}
        """
        try:
            invoice_dict = input_data.get("invoice")
            po_dict = input_data.get("purchase_order")
            gr_dict = input_data.get("goods_receipt")

            if not invoice_dict or not po_dict:
                return {"success": False, "error": "Missing required 'invoice' or 'purchase_order' in input data."}

            # Convert to models for easier attribute lookup and schema verification
            invoice = Invoice(**invoice_dict)
            po = PurchaseOrder(**po_dict)
            gr = GoodsReceipt(**gr_dict) if gr_dict else None

            discrepancies = []

            # 1. Compare PO numbers
            if invoice.po_number != po.po_number:
                discrepancies.append(MatchDiscrepancy(
                    field="po_number",
                    invoice_value=invoice.po_number,
                    po_value=po.po_number,
                    severity="major"
                ))

            # 2. Compare Total Amount
            total_var = classify_amount_variance(invoice.total_amount, po.total_amount)
            if total_var != "match":
                discrepancies.append(MatchDiscrepancy(
                    field="total_amount",
                    invoice_value=str(invoice.total_amount),
                    po_value=str(po.total_amount),
                    severity=total_var
                ))

            # 3. Compare Line Items (Invoice vs PO)
            po_items = {item.description: item for item in po.line_items}
            
            # Track receipts by item description if Goods Receipt exists
            received_items = {}
            if gr:
                received_items = {item.description: item.quantity for item in gr.received_items}

            for inv_item in invoice.line_items:
                desc = inv_item.description
                if desc not in po_items:
                    discrepancies.append(MatchDiscrepancy(
                        field="line_item_missing_in_po",
                        invoice_value=desc,
                        po_value="N/A",
                        severity="major"
                    ))
                    continue

                po_item = po_items[desc]

                # Check quantity variance
                qty_var = classify_line_item_variance(inv_item.quantity, po_item.quantity, po_item.unit_price)
                if qty_var != "match":
                    discrepancies.append(MatchDiscrepancy(
                        field=f"line_item_quantity[{desc}]",
                        invoice_value=str(inv_item.quantity),
                        po_value=str(po_item.quantity),
                        severity=qty_var
                    ))

                # Check unit price variance
                price_var = classify_amount_variance(inv_item.unit_price, po_item.unit_price)
                if price_var != "match":
                    discrepancies.append(MatchDiscrepancy(
                        field=f"line_item_unit_price[{desc}]",
                        invoice_value=str(inv_item.unit_price),
                        po_value=str(po_item.unit_price),
                        severity=price_var
                    ))

                # 4. Compare with Goods Receipt (Partial Receipt scenario)
                if gr:
                    received_qty = received_items.get(desc, 0.0)
                    if inv_item.quantity > received_qty:
                        # Invoiced quantity exceeds received quantity
                        gr_severity = classify_line_item_variance(
                            invoice_qty=inv_item.quantity,
                            po_qty=received_qty,
                            unit_price=po_item.unit_price
                        )

                        discrepancies.append(MatchDiscrepancy(
                            field=f"received_quantity_shortfall[{desc}]",
                            invoice_value=str(inv_item.quantity),
                            po_value=str(received_qty),
                            severity=gr_severity
                        ))


            is_match = len(discrepancies) == 0
            match_result = MatchResult(
                invoice_id=invoice.invoice_id,
                po_number=po.po_number,
                is_match=is_match,
                discrepancies=discrepancies
            )

            return {"success": True, "match_result": match_result.model_dump()}
        except Exception as e:
            return {"success": False, "error": f"Matcher execution failed: {str(e)}"}
