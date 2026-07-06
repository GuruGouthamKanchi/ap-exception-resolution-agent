import os
import sys
import json
from dotenv import load_dotenv

# Ensure parent directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from services.firestore_client import FirestoreClient, FirestoreConnectionError

def load_data_to_firestore():
    # Sanity-check the environment path
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if not cred_path or not os.path.exists(cred_path):
        print(f"ERROR: Firebase credentials file not found at '{cred_path}'.")
        print("Please configure a valid service account credentials JSON in backend/.env to use live Firestore.")
        sys.exit(1)

    try:
        client = FirestoreClient()
    except FirestoreConnectionError as e:
        print(f"ERROR initializing Firestore Client: {str(e)}")
        sys.exit(1)

    data_dir = os.path.dirname(os.path.abspath(__file__))
    po_path = os.path.join(data_dir, "purchase_orders.json")
    gr_path = os.path.join(data_dir, "goods_receipts.json")

    # Load Purchase Orders
    po_count = 0
    try:
        with open(po_path, "r") as f:
            pos = json.load(f)
        for po in pos:
            client.save_purchase_order(po)
            po_count += 1
    except Exception as e:
        print(f"Error loading purchase orders: {str(e)}")
        sys.exit(1)

    # Load Goods Receipts
    gr_count = 0
    try:
        with open(gr_path, "r") as f:
            grs = json.load(f)
        for gr in grs:
            client.save_goods_receipt(gr)
            gr_count += 1
    except Exception as e:
        print(f"Error loading goods receipts: {str(e)}")
        sys.exit(1)

    print("=" * 50)
    print("FIRESTORE LOAD COMPLETE")
    print("=" * 50)
    print(f"Successfully loaded {po_count} Purchase Orders.")
    print(f"Successfully loaded {gr_count} Goods Receipts.")
    print("=" * 50)

if __name__ == "__main__":
    load_data_to_firestore()
