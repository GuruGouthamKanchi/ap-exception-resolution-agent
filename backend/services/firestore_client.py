import os
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.client import Client

class FirestoreConnectionError(Exception):
    """Raised when Firestore fails to initialize or connect due to configuration/credential errors."""
    pass

class FirestoreClient:
    """
    The single point of contact with Firestore.
    
    Provides logic for storing and retrieving invoices, matching results, resolutions,
    and stage audit logs. Handles initialization error parsing.
    """
    def __init__(self):
        try:
            if not firebase_admin._apps:
                cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
                if not cred_path:
                    raise FirestoreConnectionError(
                        "FIREBASE_CREDENTIALS_PATH environment variable is missing."
                    )
                if not os.path.exists(cred_path):
                    raise FirestoreConnectionError(
                        f"Firebase credentials file not found at path: {cred_path}"
                    )
                
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                
            self.db: Client = firestore.client()
        except FirestoreConnectionError:
            raise
        except Exception as e:
            raise FirestoreConnectionError(f"Failed to initialize Firestore Client: {str(e)}") from e

    def save_invoice(self, invoice: dict) -> None:
        """Saves an invoice to the 'invoices' collection, keyed by invoice_id."""
        try:
            invoice_id = invoice.get("invoice_id")
            if not invoice_id:
                raise ValueError("Invoice data is missing required 'invoice_id'.")
            self.db.collection("invoices").document(invoice_id).set(invoice)
        except Exception as e:
            raise FirestoreConnectionError(f"Error saving invoice: {str(e)}") from e

    def save_match_result(self, match_result: dict) -> None:
        """Saves a match result to the 'match_results' collection, keyed by invoice_id."""
        try:
            invoice_id = match_result.get("invoice_id")
            if not invoice_id:
                raise ValueError("Match result is missing required 'invoice_id'.")
            self.db.collection("match_results").document(invoice_id).set(match_result)
        except Exception as e:
            raise FirestoreConnectionError(f"Error saving match result: {str(e)}") from e

    def save_resolution(self, resolution: dict) -> None:
        """Saves a resolution to the 'resolutions' collection, keyed by invoice_id."""
        try:
            invoice_id = resolution.get("invoice_id")
            if not invoice_id:
                raise ValueError("Resolution is missing required 'invoice_id'.")
            self.db.collection("resolutions").document(invoice_id).set(resolution)
        except Exception as e:
            raise FirestoreConnectionError(f"Error saving resolution: {str(e)}") from e

    def save_audit_log(self, invoice_id: str, stage: str, data: dict) -> None:
        """
        Appends an entry to a subcollection 'audit_logs' under document invoices/{invoice_id}.
        Includes stage name, server timestamp, and the payload data.
        """
        try:
            audit_ref = self.db.collection("invoices").document(invoice_id).collection("audit_logs")
            audit_ref.add({
                "stage": stage,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "data": data
            })
        except Exception as e:
            raise FirestoreConnectionError(f"Error saving audit log: {str(e)}") from e

    def get_all_resolutions(self) -> list:
        """Returns every document in 'resolutions' as a list of dictionaries."""
        try:
            docs = self.db.collection("resolutions").stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            raise FirestoreConnectionError(f"Error fetching resolutions: {str(e)}") from e

    def get_resolution(self, invoice_id: str) -> dict | None:
        """Fetch a single resolution by invoice ID, or None if not found."""
        try:
            doc_ref = self.db.collection("resolutions").document(invoice_id).get()
            if doc_ref.exists:
                return doc_ref.to_dict()
            return None
        except Exception as e:
            raise FirestoreConnectionError(f"Error fetching resolution {invoice_id}: {str(e)}") from e

    def get_invoice(self, invoice_id: str) -> dict | None:
        """Fetch a single invoice by ID from Firestore, or None if not found."""
        try:
            doc_ref = self.db.collection("invoices").document(invoice_id).get()
            if doc_ref.exists:
                return doc_ref.to_dict()
            return None
        except Exception as e:
            raise FirestoreConnectionError(f"Error fetching invoice {invoice_id}: {str(e)}") from e

    def get_match_result(self, invoice_id: str) -> dict | None:
        """Fetch a single match result by invoice ID from Firestore, or None if not found."""
        try:
            doc_ref = self.db.collection("match_results").document(invoice_id).get()
            if doc_ref.exists:
                return doc_ref.to_dict()
            return None
        except Exception as e:
            raise FirestoreConnectionError(f"Error fetching match result {invoice_id}: {str(e)}") from e

            raise FirestoreConnectionError(f"Error fetching resolution {invoice_id}: {str(e)}") from e

    def get_purchase_order(self, po_number: str) -> dict | None:
        """Fetch a purchase order by PO number from Firestore, or None if not found."""
        try:
            doc_ref = self.db.collection("purchase_orders").document(po_number).get()
            if doc_ref.exists:
                return doc_ref.to_dict()
            return None
        except Exception as e:
            raise FirestoreConnectionError(f"Error fetching purchase order {po_number}: {str(e)}") from e

    def get_goods_receipt(self, po_number: str) -> dict | None:
        """Fetch a goods receipt by PO number from Firestore, or None if not found."""
        try:
            doc_ref = self.db.collection("goods_receipts").document(po_number).get()
            if doc_ref.exists:
                return doc_ref.to_dict()
            return None
        except Exception as e:
            raise FirestoreConnectionError(f"Error fetching goods receipt {po_number}: {str(e)}") from e

    def save_purchase_order(self, po: dict) -> None:
        """Saves a purchase order to the 'purchase_orders' collection, keyed by po_number."""
        try:
            po_number = po.get("po_number")
            if not po_number:
                raise ValueError("Purchase order is missing required 'po_number'.")
            self.db.collection("purchase_orders").document(po_number).set(po)
        except Exception as e:
            raise FirestoreConnectionError(f"Error saving purchase order: {str(e)}") from e

    def save_goods_receipt(self, gr: dict) -> None:
        """Saves a goods receipt to the 'goods_receipts' collection, keyed by po_number."""
        try:
            po_number = gr.get("po_number")
            if not po_number:
                raise ValueError("Goods receipt is missing required 'po_number'.")
            self.db.collection("goods_receipts").document(po_number).set(gr)
        except Exception as e:
            raise FirestoreConnectionError(f"Error saving goods receipt: {str(e)}") from e


