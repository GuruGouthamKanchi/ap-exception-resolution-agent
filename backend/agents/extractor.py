import os
import sys
from pydantic import ValidationError

# Ensure parent directory is in sys.path if run as script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base import Agent
from models.schemas import Invoice
from services.gemini_client import GeminiClient, GeminiExtractionError

class ExtractorAgent(Agent):
    """
    Agent responsible for extracting structured Invoice data from unstructured raw OCR text using Gemini.
    """
    def __init__(self):
        self._name = "extractor"
        self.client = GeminiClient()

    @property
    def name(self) -> str:
        return self._name

    def run(self, input_data: dict) -> dict:
        """
        Extracts structured Invoice data from raw text.
        
        Args:
            input_data (dict): Expected to contain {"raw_text": str}
            
        Returns:
            dict: {"success": bool, "invoice": dict, "error": str}
        """
        raw_text = input_data.get("raw_text")
        if not raw_text:
            return {"success": False, "error": "No 'raw_text' provided in input data."}

        prompt = (
            "You are an expert accounts payable extraction assistant. Extract the invoice details "
            "from the following raw OCR text and format the output according to the requested JSON schema.\n\n"
            "Instructions:\n"
            "1. Extract the invoice_id, vendor_name, po_number, currency, line_items, total_amount, and raw_source.\n"
            "2. Normalize the invoice_date to ISO format (YYYY-MM-DD).\n"
            "3. Strip currency symbols (e.g. '$') from unit prices and totals; provide only numeric values.\n"
            "4. For raw_source, set it to 'pdf'.\n"
            "5. Ensure that all line items match the schema containing: description, quantity, unit_price, line_total.\n\n"
            f"Raw OCR Invoice Text:\n{raw_text}"
        )

        try:
            extracted_dict = self.client.extract_structured(prompt, Invoice)
            # Validate schema integrity explicitly using the model constructor
            Invoice(**extracted_dict)
            return {"success": True, "invoice": extracted_dict}
        except GeminiExtractionError as e:
            return {"success": False, "error": f"Gemini extraction failed: {str(e)}"}
        except ValidationError as e:
            return {"success": False, "error": f"Pydantic validation failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error during extraction: {str(e)}"}
