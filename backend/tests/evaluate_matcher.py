import os
import sys
import json

# Ensure parent directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.matcher import MatcherAgent

def evaluate_matcher():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    
    with open(os.path.join(data_dir, "invoices.json"), "r") as f:
        invoices = json.load(f)
        
    with open(os.path.join(data_dir, "purchase_orders.json"), "r") as f:
        purchase_orders = json.load(f)
        
    with open(os.path.join(data_dir, "goods_receipts.json"), "r") as f:
        goods_receipts = json.load(f)

    matcher = MatcherAgent()
    
    # Counts for categories
    total_evaluated = len(invoices)
    
    # Classification counters
    clean_correct = 0
    clean_mismatched = 0
    
    minor_correct = 0  # Should be flagged as having only minor discrepancies
    minor_mismatched = 0
    
    major_correct = 0  # Should be flagged as having at least one major discrepancy
    major_mismatched = 0
    
    partial_receipt_correct = 0  # Should contain received_quantity_shortfall discrepancy
    partial_receipt_mismatched = 0
    
    alignment_issues = []

    # Indices of partial receipts (1-based: 5, 12, 23 -> 0-based: 4, 11, 22)
    partial_gr_indices = {4, 11, 22}

    print(f"Starting MatcherAgent evaluation across {total_evaluated} cases...\n")

    for i, invoice in enumerate(invoices):
        inv_id = invoice["invoice_id"]
        po_num = invoice["po_number"]
        
        # Find PO
        po = next((p for p in purchase_orders if p["po_number"] == po_num), None)
        if not po:
            # Fallback for wrong PO number cases (Major discrepancy)
            po = next((p for p in purchase_orders if p["vendor_name"] == invoice["vendor_name"]), None)
            
        # Find GR
        gr = next((g for g in goods_receipts if g["po_number"] == (po["po_number"] if po else po_num)), None)
        
        res = matcher.run({
            "invoice": invoice,
            "purchase_order": po,
            "goods_receipt": gr
        })
        
        if not res["success"]:
            print(f"Error executing MatcherAgent for {inv_id}: {res['error']}")
            continue
            
        match_result = res["match_result"]
        discrepancies = match_result["discrepancies"]
        
        has_major = any(d["severity"] == "major" for d in discrepancies)
        has_minor = any(d["severity"] == "minor" for d in discrepancies)
        is_clean = len(discrepancies) == 0
        
        has_shortfall = any("received_quantity_shortfall" in d["field"] for d in discrepancies)
        
        # Determine expected classification based on index range in generate_synthetic.py
        if i < 18:
            expected_category = "clean"
        elif i < 25:
            expected_category = "minor"
        else:
            expected_category = "major"
            
        # Also track partial receipt expectation
        is_expected_partial = i in partial_gr_indices

        # Evaluate clean matching
        if expected_category == "clean":
            if is_clean:
                clean_correct += 1
            else:
                clean_mismatched += 1
                alignment_issues.append((inv_id, "Expected CLEAN, but found discrepancies", discrepancies))
                
        # Evaluate minor matching
        elif expected_category == "minor":
            if has_minor and not has_major:
                minor_correct += 1
            else:
                minor_mismatched += 1
                alignment_issues.append((inv_id, f"Expected MINOR only, but has_minor={has_minor}, has_major={has_major}", discrepancies))
                
        # Evaluate major matching
        elif expected_category == "major":
            if has_major:
                major_correct += 1
            else:
                major_mismatched += 1
                alignment_issues.append((inv_id, "Expected MAJOR mismatch, but no major discrepancies found", discrepancies))

        # Evaluate partial receipt shortfall
        if is_expected_partial:
            if has_shortfall:
                partial_receipt_correct += 1
            else:
                partial_receipt_mismatched += 1
                alignment_issues.append((inv_id, "Expected PARTIAL RECEIPT shortfall, but shortfall flag was missing", discrepancies))

    # Print confusion-style summary
    print("=" * 60)
    print("MATCHER ACCURACY SUMMARY")
    print("=" * 60)
    print(f"Total Documents Processed: {total_evaluated}")
    print(f"Clean Matches: {clean_correct} / 18 correct ({clean_mismatched} mismatched)")
    print(f"Minor Discrepancies: {minor_correct} / 7 correct ({minor_mismatched} mismatched)")
    print(f"Major Discrepancies: {major_correct} / 5 correct ({major_mismatched} mismatched)")
    print(f"Partial Receipt Mismatch Detections: {partial_receipt_correct} / 3 correct ({partial_receipt_mismatched} mismatched)")
    print("=" * 60)
    
    if alignment_issues:
        print("\nALIGNMENT ISSUES & DISCREPANCY DEVIATIONS:")
        print("-" * 60)
        for inv_id, issue_desc, discs in alignment_issues:
            print(f"Invoice: {inv_id} | Issue: {issue_desc}")
            print("Actual Discrepancies:")
            for d in discs:
                print(f"  - Field: '{d['field']}' | Inv: '{d['invoice_value']}' vs PO/GR: '{d['po_value']}' | Severity: {d['severity']}")
            print("-" * 60)
    else:
        print("\nAll Matcher classifications perfectly aligned with original dataset design!")

if __name__ == "__main__":
    evaluate_matcher()
