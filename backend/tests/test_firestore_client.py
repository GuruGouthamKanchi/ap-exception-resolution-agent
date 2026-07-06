import os
import sys
import pytest
from dotenv import load_dotenv

# Ensure parent directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from services.firestore_client import FirestoreClient, FirestoreConnectionError

def test_firestore_client():
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if not cred_path or not os.path.exists(cred_path):
        pytest.skip(f"Skipping Firestore test because FIREBASE_CREDENTIALS_PATH ({cred_path}) is not set or file does not exist.")

    try:
        client = FirestoreClient()
    except FirestoreConnectionError as e:
        pytest.fail(f"Failed to initialize FirestoreClient: {str(e)}")

    dummy_invoice = {
        "invoice_id": "INV-TEST-9999",
        "vendor_name": "Test Vendor",
        "total_amount": 123.45,
        "currency": "USD"
    }

    # Test Save
    try:
        client.save_invoice(dummy_invoice)
    except Exception as e:
        pytest.fail(f"Failed to save dummy invoice: {str(e)}")

    # Clean up test document after validation is out of scope or we can leave it
    print("Dummy invoice saved successfully.")
