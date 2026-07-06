import os
import sys
import json
import time
from dotenv import load_dotenv

# Ensure parent directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from agents.extractor import ExtractorAgent

def evaluate_extractor():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY is not set in the environment variables.")
        print("Please copy backend/.env.example to backend/.env and populate GEMINI_API_KEY.")
        sys.exit(1)

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    
    with open(os.path.join(data_dir, "raw_invoice_texts.json"), "r") as f:
        raw_invoices = json.load(f)
        
    with open(os.path.join(data_dir, "invoices.json"), "r") as f:
        gt_invoices = json.load(f)

    agent = ExtractorAgent()
    
    total_invoices = len(raw_invoices)
    perfect_matches = 0
    mismatches = 0
    extraction_failures = 0
    
    # Track field level accuracy
    total_fields = 0
    correct_fields = 0
    
    mismatch_details = []

    print(f"Starting evaluation of ExtractorAgent against {total_invoices} invoices...\n")

    for index, sample in enumerate(raw_invoices, 1):
        inv_id = sample["invoice_id"]
        raw_text = sample["raw_text"]
        
        gt = next(item for item in gt_invoices if item["invoice_id"] == inv_id)
        
        print(f"Processing invoice {index}/{total_invoices} (ID: {inv_id})...")
        res = agent.run({"raw_text": raw_text})
        
        # Fixed delay to comply with Free Tier rate limits (RPM <= 15)
        time.sleep(4.5)
        
        if not res.get("success"):
            extraction_failures += 1

            mismatch_details.append({
                "invoice_id": inv_id,
                "type": "extraction_failure",
                "error": res.get("error"),
                "raw_text": raw_text,
                "ground_truth": gt
            })
            continue

        extracted = res["invoice"]
        
        # Compare fields
        fields_to_check = {
            "vendor_name": (
                gt["vendor_name"].strip().lower(),
                extracted.get("vendor_name", "").strip().lower()
            ),
            "po_number": (
                gt["po_number"].strip(),
                extracted.get("po_number", "").strip()
            ),
            "total_amount": (
                round(gt["total_amount"], 2),
                round(extracted.get("total_amount", 0.0), 2)
            ),
            "line_item_count": (
                len(gt["line_items"]),
                len(extracted.get("line_items", []))
            )
        }
        
        invoice_has_mismatch = False
        invoice_errors = {}
        
        for field, (expected, actual) in fields_to_check.items():
            total_fields += 1
            is_correct = False
            
            if field == "total_amount":
                # Tolerant match within 0.01
                is_correct = abs(expected - actual) <= 0.01
            else:
                is_correct = expected == actual
                
            if is_correct:
                correct_fields += 1
            else:
                invoice_has_mismatch = True
                invoice_errors[field] = {"expected": expected, "actual": actual}
                
        if invoice_has_mismatch:
            mismatches += 1
            mismatch_details.append({
                "invoice_id": inv_id,
                "type": "field_mismatch",
                "details": invoice_errors
            })
        else:
            perfect_matches += 1

    # Print summary
    field_accuracy = (correct_fields / total_fields * 100) if total_fields > 0 else 0.0
    
    print("=" * 60)
    print("EXTRACTOR ACCURACY SUMMARY")
    print("=" * 60)
    print(f"Total Invoices Evaluated: {total_invoices}")
    print(f"Perfect Matches (all fields correct): {perfect_matches}")
    print(f"At Least One Field Mismatched: {mismatches}")
    print(f"Failed Extractions: {extraction_failures}")
    print(f"Overall Field-Level Accuracy: {field_accuracy:.2f}% ({correct_fields}/{total_fields} fields)")
    print("=" * 60)
    
    # Track error groups
    error_groups = {}

    if mismatch_details:
        print("\nMISMATCH AND FAILURE DETAILS:")
        print("=" * 60)
        for item in mismatch_details:
            if item["type"] == "extraction_failure":
                print(f"\n--- FAILURE FOR INVOICE {item['invoice_id']} ---")
                print(f"Error Message: {item['error']}")
                print("\nRaw Text Passed to Gemini:")
                print(item["raw_text"])
                print("\nGround Truth Fields:")
                print(json.dumps(item["ground_truth"], indent=2))
                print("-" * 60)
                
                # Group by simple key (rate limit vs other)
                err_msg = item["error"]
                if "quota" in err_msg.lower() or "429" in err_msg.lower() or "rate limit" in err_msg.lower():
                    group_key = "Gemini Quota/Rate Limit Exceeded (429)"
                else:
                    group_key = err_msg
                error_groups[group_key] = error_groups.get(group_key, 0) + 1
            else:
                print(f"Invoice {item['invoice_id']}: Field mismatches found:")
                for field, error in item["details"].items():
                    print(f"  - {field}: Expected '{error['expected']}', got '{error['actual']}'")
                print("-" * 60)

    # Print error grouping summary if there were failures
    if error_groups:
        print("\n" + "=" * 60)
        print("FAILURE GROUPING SUMMARY")
        print("=" * 60)
        for err_type, count in error_groups.items():
            print(f"- {err_type}: {count} failures")
        print("=" * 60)

if __name__ == "__main__":
    evaluate_extractor()

