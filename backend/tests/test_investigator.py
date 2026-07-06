import os
import sys
import json
from dotenv import load_dotenv

# Ensure parent directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from agents.matcher import MatcherAgent
from agents.investigator import InvestigatorAgent

def run_investigator_tests():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    
    with open(os.path.join(data_dir, "invoices.json"), "r") as f:
        invoices = json.load(f)
        
    with open(os.path.join(data_dir, "purchase_orders.json"), "r") as f:
        purchase_orders = json.load(f)
        
    with open(os.path.join(data_dir, "goods_receipts.json"), "r") as f:
        goods_receipts = json.load(f)

    # Selected Test Cases:
    # 2 Clean Matches (indices 0, 1)
    # 2 Minor Discrepancies (indices 18, 19)
    # 1 Major Discrepancy (index 25)
    selected_indices = [0, 1, 18, 19, 25]
    
    matcher = MatcherAgent()
    investigator = InvestigatorAgent()

    print("=" * 70)
    print("RUNNING INVESTIGATOR AGENT TEST FOR ALL 5 CASES")
    print("=" * 70)

    for idx in selected_indices:
        invoice = invoices[idx]
        inv_id = invoice["invoice_id"]

        po_num = invoice["po_number"]
        
        po = next((p for p in purchase_orders if p["po_number"] == po_num), None)
        if not po:
            po = next((p for p in purchase_orders if p["vendor_name"] == invoice["vendor_name"]), None)
            
        gr = next((g for g in goods_receipts if g["po_number"] == (po["po_number"] if po else po_num)), None)

        print(f"\nEvaluating Invoice ID: {inv_id}")
        
        # Step 1: Match
        match_res = matcher.run({
            "invoice": invoice,
            "purchase_order": po,
            "goods_receipt": gr
        })
        
        if not match_res["success"]:
            print(f"Match failed for {inv_id}")
            continue
            
        result_dict = match_res["match_result"]
        
        # Step 2: Investigate
        investigate_res = investigator.run({
            "invoice": invoice,
            "match_result": result_dict
        })
        
        if investigate_res["success"]:
            resolution = investigate_res["resolution"]
            print("RESOLUTION DECISION:")
            print(f"  - Status: {resolution['status']}")
            print(f"  - Resolved By: {resolution['resolved_by']}")
            print(f"  - Manual Cost Savings: ${resolution['estimated_manual_cost']:.2f}")
            print(f"  - Time Saved: {resolution['estimated_time_saved_minutes']} mins")
            print("  - Reasoning:")
            print(f"    {resolution['reasoning']}")
        else:
            print(f"Investigation failed: {investigate_res.get('error')}")
            
        print("-" * 70)

if __name__ == "__main__":
    run_investigator_tests()
