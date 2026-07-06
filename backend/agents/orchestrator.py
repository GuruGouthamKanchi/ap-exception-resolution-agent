import os
import sys
import logging

# Ensure parent directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    """
    Coordinates the 3-agent AP Exception Resolution pipeline.
    Runs Extractor, Matcher, and Investigator in sequence, persisting
    intermediate state and audit trails directly to Firestore.
    """
    def __init__(self, extractor_agent, matcher_agent, investigator_agent, firestore_client):
        self.extractor = extractor_agent
        self.matcher = matcher_agent
        self.investigator = investigator_agent
        self.db = firestore_client

    def process_invoice(self, raw_text: str, po_number: str) -> dict:
        """
        Runs the full accounts payable pipeline for a raw invoice text.
        
        Args:
            raw_text (str): Unstructured raw OCR invoice text.
            po_number (str): The expected PO reference.
            
        Returns:
            dict: Pipeline execution summary.
        """
        # 1. Extraction Stage
        try:
            logger.info("Executing extraction stage...")
            ext_res = self.extractor.run({"raw_text": raw_text})
            
            invoice_data = ext_res.get("invoice", {})
            invoice_id = invoice_data.get("invoice_id", "UNKNOWN")
            
            # Save extraction audit trail
            self.db.save_audit_log(
                invoice_id=invoice_id,
                stage="extraction",
                data=ext_res
            )
            
            if not ext_res.get("success"):
                logger.error(f"Extraction failed: {ext_res.get('error')}")
                return {
                    "invoice_id": None,
                    "stage_failed": "extraction",
                    "error": ext_res.get("error"),
                    "match_result": None,
                    "resolution": None
                }
                
        except Exception as e:
            logger.exception("Pipeline crashed at extraction stage.")
            return {
                "invoice_id": None,
                "stage_failed": "extraction",
                "error": f"Exception at extraction stage: {str(e)}",
                "match_result": None,
                "resolution": None
            }

        # 2. Fetch PO and Goods Receipt from Firestore
        try:
            po = self.db.get_purchase_order(po_number)
            gr = self.db.get_goods_receipt(po_number)
        except Exception as e:
            logger.exception("Pipeline crashed fetching PO or Goods Receipt.")
            return {
                "invoice_id": invoice_id,
                "stage_failed": "fetching_records",
                "error": f"Failed to retrieve PO/GR: {str(e)}",
                "match_result": None,
                "resolution": None
            }

        # 3. Matching Stage
        try:
            logger.info(f"Executing matching stage against PO {po_number}...")
            match_res = self.matcher.run({
                "invoice": invoice_data,
                "purchase_order": po,
                "goods_receipt": gr
            })
            
            # Save matching audit trail
            self.db.save_audit_log(
                invoice_id=invoice_id,
                stage="matching",
                data=match_res
            )
            
            if not match_res.get("success"):
                logger.error(f"Matching failed: {match_res.get('error')}")
                return {
                    "invoice_id": invoice_id,
                    "stage_failed": "matching",
                    "error": match_res.get("error"),
                    "match_result": None,
                    "resolution": None
                }
                
            match_result_data = match_res["match_result"]
            
        except Exception as e:
            logger.exception("Pipeline crashed at matching stage.")
            return {
                "invoice_id": invoice_id,
                "stage_failed": "matching",
                "error": f"Exception at matching stage: {str(e)}",
                "match_result": None,
                "resolution": None
            }

        # 4. Investigation Stage
        try:
            logger.info("Executing investigation stage...")
            inv_res = self.investigator.run({
                "invoice": invoice_data,
                "match_result": match_result_data
            })
            
            # Save investigation audit trail
            self.db.save_audit_log(
                invoice_id=invoice_id,
                stage="investigation",
                data=inv_res
            )
            
            if not inv_res.get("success"):
                logger.error(f"Investigation failed: {inv_res.get('error')}")
                return {
                    "invoice_id": invoice_id,
                    "stage_failed": "investigation",
                    "error": inv_res.get("error"),
                    "match_result": match_result_data,
                    "resolution": None
                }
                
            resolution_data = inv_res["resolution"]
            
        except Exception as e:
            logger.exception("Pipeline crashed at investigation stage.")
            return {
                "invoice_id": invoice_id,
                "stage_failed": "investigation",
                "error": f"Exception at investigation stage: {str(e)}",
                "match_result": match_result_data,
                "resolution": None
            }

        # 5. Persist final results to their respective Firestore collections
        try:
            logger.info(f"Persisting AP resolution artifacts for Invoice {invoice_id}...")
            self.db.save_invoice(invoice_data)
            self.db.save_match_result(match_result_data)
            self.db.save_resolution(resolution_data)
        except Exception as e:
            logger.error(f"Failed to persist pipeline results to Firestore: {str(e)}")
            # We don't fail the pipeline return here since the analysis was completed
            return {
                "invoice_id": invoice_id,
                "stage_failed": "persistence",
                "error": f"Analysis completed but failed to save in db: {str(e)}",
                "match_result": match_result_data,
                "resolution": resolution_data
            }

        return {
            "invoice_id": invoice_id,
            "stage_failed": None,
            "match_result": match_result_data,
            "resolution": resolution_data
        }
