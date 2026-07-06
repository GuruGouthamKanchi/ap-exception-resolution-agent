import os
import json
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from models.schemas import ProcessInvoiceRequest
from services.firestore_client import FirestoreClient, FirestoreConnectionError
from agents.extractor import ExtractorAgent
from agents.matcher import MatcherAgent
from agents.investigator import InvestigatorAgent
from agents.orchestrator import PipelineOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AP_Agent_API")

app = FastAPI(title="AP Exception Resolution Agent API")

# Enable CORS for Next.js frontend running on localhost:3000
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# InMemory database fallback for demo/test mode if Firestore is not configured
class InMemoryDB:
    def __init__(self):
        self.invoices = {}
        self.match_results = {}
        self.resolutions = {}
        self.audit_logs = {}
        
        # Load local synthetic POs and GRs to mimic populated DB
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        try:
            with open(os.path.join(data_dir, "purchase_orders.json"), "r") as f:
                pos = json.load(f)
                self.purchase_orders = {po["po_number"]: po for po in pos}
            with open(os.path.join(data_dir, "goods_receipts.json"), "r") as f:
                grs = json.load(f)
                self.goods_receipts = {gr["po_number"]: gr for gr in grs}
            logger.info("InMemoryDB loaded local synthetic POs and Goods Receipts.")
        except Exception as e:
            logger.warning(f"InMemoryDB failed to load local JSON files: {e}")
            self.purchase_orders = {}
            self.goods_receipts = {}

    def save_invoice(self, invoice: dict) -> None:
        self.invoices[invoice["invoice_id"]] = invoice

    def save_match_result(self, match_result: dict) -> None:
        self.match_results[match_result["invoice_id"]] = match_result

    def save_resolution(self, resolution: dict) -> None:
        self.resolutions[resolution["invoice_id"]] = resolution

    def save_audit_log(self, invoice_id: str, stage: str, data: dict) -> None:
        if invoice_id not in self.audit_logs:
            self.audit_logs[invoice_id] = []
        self.audit_logs[invoice_id].append({"stage": stage, "data": data})

    def get_all_resolutions(self) -> list:
        return list(self.resolutions.values())

    def get_resolution(self, invoice_id: str) -> dict | None:
        return self.resolutions.get(invoice_id)

    def get_invoice(self, invoice_id: str) -> dict | None:
        return self.invoices.get(invoice_id)

    def get_match_result(self, invoice_id: str) -> dict | None:
        return self.match_results.get(invoice_id)


    def get_purchase_order(self, po_number: str) -> dict | None:
        return self.purchase_orders.get(po_number)

    def get_goods_receipt(self, po_number: str) -> dict | None:
        return self.goods_receipts.get(po_number)


# Initialize DB Client (Fallback to InMemory if Firestore fails initialization)
try:
    db_client = FirestoreClient()
    logger.info("FirestoreClient successfully initialized.")
except FirestoreConnectionError as e:
    logger.warning(f"Firestore not configured ({e}). Falling back to InMemoryDB for demo mode.")
    db_client = InMemoryDB()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/process-invoice", status_code=status.HTTP_200_OK)
def process_invoice(req: ProcessInvoiceRequest):
    logger.info(f"POST /process-invoice | PO Ref: {req.po_number}")
    
    if not req.raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="raw_text cannot be empty."
        )
    if not req.po_number.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="po_number cannot be empty."
        )
        
    try:
        # Dependency Injection
        extractor = ExtractorAgent()
        matcher = MatcherAgent()
        investigator = InvestigatorAgent()
        
        orchestrator = PipelineOrchestrator(
            extractor_agent=extractor,
            matcher_agent=matcher,
            investigator_agent=investigator,
            firestore_client=db_client
        )
        
        res = orchestrator.process_invoice(req.raw_text, req.po_number)
        
        if res.get("stage_failed"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Pipeline failed at stage '{res['stage_failed']}': {res['error']}"
            )
            
        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in process_invoice endpoint.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected server error: {str(e)}"
        )

@app.get("/resolutions")
def get_resolutions():
    logger.info("GET /resolutions")
    try:
        return db_client.get_all_resolutions()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.get("/resolutions/{invoice_id}")
def get_resolution(invoice_id: str):
    logger.info(f"GET /resolutions/{invoice_id}")
    try:
        resolution = db_client.get_resolution(invoice_id)
        if not resolution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resolution for invoice {invoice_id} not found."
            )
        return resolution
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: str):
    logger.info(f"GET /invoices/{invoice_id}")
    try:
        invoice = db_client.get_invoice(invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice {invoice_id} not found."
            )
        return invoice
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.get("/match-results/{invoice_id}")
def get_match_result(invoice_id: str):
    logger.info(f"GET /match-results/{invoice_id}")
    try:
        match_result = db_client.get_match_result(invoice_id)
        if not match_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match result for invoice {invoice_id} not found."
            )
        return match_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@app.get("/dashboard-summary")
def get_dashboard_summary():
    logger.info("GET /dashboard-summary")
    try:
        resolutions = db_client.get_all_resolutions()
        
        total_processed = len(resolutions)
        auto_resolved_count = sum(1 for r in resolutions if r.get("status") == "auto_resolved")
        escalated_count = sum(1 for r in resolutions if r.get("status") == "escalated")
        
        total_cost_saved = sum(r.get("estimated_manual_cost", 0.0) for r in resolutions)
        total_time_saved_mins = sum(r.get("estimated_time_saved_minutes", 0.0) for r in resolutions)
        total_time_saved_hours = round(total_time_saved_mins / 60.0, 2)
        
        policy_rule_count = sum(1 for r in resolutions if r.get("resolved_by") == "policy_rule")
        gemini_investigation_count = sum(1 for r in resolutions if r.get("resolved_by") == "gemini_investigation")
        human_required_count = sum(1 for r in resolutions if r.get("resolved_by") == "human_required")

        return {
            "total_processed": total_processed,
            "status_counts": {
                "auto_resolved": auto_resolved_count,
                "escalated": escalated_count
            },
            "total_cost_saved_usd": round(total_cost_saved, 2),
            "total_time_saved_minutes": round(total_time_saved_mins, 2),
            "total_time_saved_hours": total_time_saved_hours,
            "resolved_by_counts": {
                "policy_rule": policy_rule_count,
                "gemini_investigation": gemini_investigation_count,
                "human_required": human_required_count
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
