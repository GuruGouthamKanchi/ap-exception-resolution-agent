import os
import sys
import json
import pytest
from dotenv import load_dotenv

# Ensure parent directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from agents.extractor import ExtractorAgent

def test_extractor_agent_quality():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("Skipping Extractor Agent test because GEMINI_API_KEY is not configured.")

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    
    with open(os.path.join(data_dir, "raw_invoice_texts.json"), "r") as f:
        raw_invoices = json.load(f)
        
    with open(os.path.join(data_dir, "invoices.json"), "r") as f:
        gt_invoices = json.load(f)

    # Take first 3 samples
    test_samples = raw_invoices[:3]
    
    agent = ExtractorAgent()
    
    for idx, sample in enumerate(test_samples):
        inv_id = sample["invoice_id"]
        raw_text = sample["raw_text"]
        
        print(f"\n==================================================")
        print(f"RUNNING EXTRACTOR FOR INVOICE: {inv_id}")
        print(f"==================================================")
        print("--- RAW TEXT ---")
        print(raw_text)
        
        res = agent.run({"raw_text": raw_text})
        
        # Get ground truth
        gt = next(item for item in gt_invoices if item["invoice_id"] == inv_id)
        
        print("\n--- GROUND TRUTH ---")
        print(json.dumps(gt, indent=2))
        
        print("\n--- EXTRACTED RESULT ---")
        print(json.dumps(res, indent=2))
        
        if not res["success"]:
            err_msg = str(res.get("error", "")).lower()
            if "rate limit" in err_msg or "quota" in err_msg or "limit" in err_msg:
                pytest.skip(f"Skipping Extractor Agent test due to API rate limit: {res.get('error')}")
        assert res["success"] is True
        assert res["invoice"]["invoice_id"] == inv_id

