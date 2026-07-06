import os
import sys
import json
from dotenv import load_dotenv

# Ensure parent directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from agents.matcher import MatcherAgent

def run_matcher_tests():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    
    with open(os.path.join(data_dir, "invoices.json"), "r") as f:
        invoices = json.load(f)
        
    with open(os.path.join(data_dir, "purchase_orders.json"), "r") as f:
        purchase_orders = json.load(f)
        
    with open(os.path.join(data_dir, "goods_receipts.json"), "r") as f:
        goods_receipts = json.load(f)

    # Hand-picked cases:
    # 2 Clean Matches (indices 0, 1)
    # 2 Minor Discrepancies (indices 18, 19)
    # 1 Major Discrepancy (index 25)
    selected_indices = [0, 1, 18, 19, 25]
    
    matcher = MatcherAgent()
    
    print("=" * 70)
    print("RUNNING 3-WAY MATCHING TEST FOR 5 HAND-PICKED CASES")
    print("=" * 70)
    
    for idx in selected_indices:
        invoice = invoices[idx]
        inv_id = invoice["invoice_id"]
        po_num = invoice["po_number"]
        
        # Match corresponding PO and GR
        po = next((p for p in purchase_orders if p["po_number"] == po_num), None)
        # If PO is not found due to wrong PO reference in major mismatch, find PO matching vendor name or PO of same index
        if not po:
            # For major mismatch, po_number might be wrong. Find the PO matching vendor name to perform matching attempt
            po = next((p for p in purchase_orders if p["vendor_name"] == invoice["vendor_name"]), None)
            
        gr = next((g for g in goods_receipts if g["po_number"] == (po["po_number"] if po else po_num)), None)

        print(f"\nInvoice ID: {inv_id} | Vendor: {invoice['vendor_name']} | PO Ref: {invoice['po_number']}")
        
        res = matcher.run({
            "invoice": invoice,
            "purchase_order": po,
            "goods_receipt": gr
        })
        
        if res["success"]:
            match_res = res["match_result"]
            print(f"Is Match: {match_res['is_match']}")
            if match_res["discrepancies"]:
                print("Discrepancies Found:")
                for disc in match_res["discrepancies"]:
                    print(f"  - Field '{disc['field']}': Invoice={disc['invoice_value']} vs PO/GR={disc['po_value']} | Severity: {disc['severity']}")
            else:
                print("  No discrepancies. Perfect match!")
        else:
            print(f"Error: {res['error']}")
            
        print("-" * 70)

if __name__ == "__main__":
    run_matcher_tests()
