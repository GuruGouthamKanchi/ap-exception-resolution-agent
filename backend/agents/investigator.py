import os
import sys

# Ensure parent directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base import Agent
from models.schemas import Resolution, Invoice
from policy.rules import can_auto_resolve, auto_resolve_reasoning, estimate_savings
from services.gemini_client import GeminiClient

class InvestigatorAgent(Agent):
    """
    Agent responsible for investigating major matching discrepancies using Gemini
    to propose a root cause and resolution action.
    """
    def __init__(self):
        self._name = "investigator"
        self.client = GeminiClient()

    @property
    def name(self) -> str:
        return self._name

    def run(self, input_data: dict) -> dict:
        """
        Runs investigation on discrepancies and returns a Resolution decision.
        
        Args:
            input_data (dict): Expected to contain {"invoice": dict, "match_result": dict}
            
        Returns:
            dict: {"success": True, "resolution": dict}
        """
        invoice_dict = input_data.get("invoice")
        match_result = input_data.get("match_result")

        if not invoice_dict or not match_result:
            # Fallback error resolution
            savings = estimate_savings(was_exception=True)
            res = Resolution(
                invoice_id=invoice_dict.get("invoice_id", "UNKNOWN") if invoice_dict else "UNKNOWN",
                status="escalated",
                reasoning="Missing required input data (invoice or match_result).",
                resolved_by="human_required",
                estimated_manual_cost=savings["cost_saved"],
                estimated_time_saved_minutes=savings["time_saved_minutes"]
            )
            return {"success": True, "resolution": res.model_dump()}

        invoice_id = invoice_dict.get("invoice_id")
        
        # 1. First check if we can auto-resolve
        if can_auto_resolve(match_result):
            savings = estimate_savings(was_exception=False)
            reasoning = auto_resolve_reasoning(match_result)
            res = Resolution(
                invoice_id=invoice_id,
                status="auto_resolved",
                reasoning=reasoning,
                resolved_by="policy_rule",
                estimated_manual_cost=savings["cost_saved"],
                estimated_time_saved_minutes=savings["time_saved_minutes"]
            )
            return {"success": True, "resolution": res.model_dump()}

        # 2. Major discrepancies exist, invoke Gemini Client
        savings = estimate_savings(was_exception=True)
        discrepancies = match_result.get("discrepancies", [])
        discrepancies_str = "\n".join([
            f"- Field: {d.get('field')} | Invoice: {d.get('invoice_value')} vs PO/GR: {d.get('po_value')} | Severity: {d.get('severity')}"
            for d in discrepancies
        ])

        prompt = (
            "You are an accounts payable forensic investigator. Inspect this invoice discrepancy "
            "and suggest a root-cause explanation and next action.\n\n"
            f"Invoice ID: {invoice_id}\n"
            f"Vendor: {invoice_dict.get('vendor_name')}\n"
            f"Total Amount: {invoice_dict.get('total_amount')}\n"
            f"PO Reference: {invoice_dict.get('po_number')}\n\n"
            f"Discrepancies Detected:\n{discrepancies_str}\n\n"
            "Analyze the above discrepancies and output your response in the exact format below:\n"
            "ACTION: <action>\n"
            "\n"
            "<Your reasoning / root-cause hypothesis explanation>\n\n"
            "Requirements for <action>:\n"
            "It must be exactly one of: 'auto_approve_with_note', 'request_vendor_clarification', or 'escalate_to_finance_manager'.\n"
            "Be realistic in your reasoning. If unit price is renegotiated slightly, you might auto approve. "
            "If items are missing or there is a major price variance or wrong PO number, escalate or request vendor clarification."
        )

        try:
            gemini_response = self.client.reason(prompt)
            
            # Parse ACTION and reasoning
            action = "escalate_to_finance_manager"  # Default fallback
            reasoning = gemini_response.strip()
            
            lines = gemini_response.strip().split("\n")
            first_line = lines[0].strip()
            
            if first_line.startswith("ACTION:"):
                extracted_action = first_line.replace("ACTION:", "").strip().lower()
                # Clean enclosing quotes or periods
                extracted_action = extracted_action.strip("'\"`.")
                
                valid_actions = ["auto_approve_with_note", "request_vendor_clarification", "escalate_to_finance_manager"]
                for v_act in valid_actions:
                    if extracted_action == v_act.lower():
                        action = v_act
                        break
                
                # Reasoning is the rest of the text
                reasoning = "\n".join(lines[1:]).strip()

            # Map action to status
            if action == "auto_approve_with_note":
                status = "auto_resolved"
            else:
                status = "escalated"

            res = Resolution(
                invoice_id=invoice_id,
                status=status,
                reasoning=reasoning,
                resolved_by="gemini_investigation",
                estimated_manual_cost=savings["cost_saved"],
                estimated_time_saved_minutes=savings["time_saved_minutes"]
            )
            return {"success": True, "resolution": res.model_dump()}

        except Exception as e:
            # Fallback Resolution path
            res = Resolution(
                invoice_id=invoice_id,
                status="escalated",
                reasoning=f"Automated investigation failed; requires manual review. Error: {str(e)}",
                resolved_by="human_required",
                estimated_manual_cost=savings["cost_saved"],
                estimated_time_saved_minutes=savings["time_saved_minutes"]
            )
            return {"success": True, "resolution": res.model_dump()}
