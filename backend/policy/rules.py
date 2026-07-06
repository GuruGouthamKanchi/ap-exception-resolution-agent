"""
Configurable Accounts Payable (AP) Tolerance Policies.

These thresholds represent configurable company policy. In a real deployment,
these would be loaded from a database or configured by the finance/policy team
rather than hardcoded.

Tolerance Rules:
1. Amount Variance:
   - Difference <= 2%: classified as "minor" variance (usually accepted or auto-resolved)
   - Difference > 5%: classified as "major" variance (requires escalation/investigation)
   - Difference between 2% and 5%: classified as "minor" or "major" depending on bounds.
2. Quantity Variance:
   - Quantities must match exactly. If they don't, the dollar impact determines severity:
     * (qty_diff * unit_price) relative to PO line total determines minor vs major.
"""

# Policy Constants
AMOUNT_MINOR_TOLERANCE_PCT = 0.02   # 2% variance
AMOUNT_MAJOR_THRESHOLD_PCT = 0.05   # 5%+ variance
QUANTITY_EXACT_MATCH_REQUIRED = True

def classify_amount_variance(invoice_value: float, po_value: float) -> str:
    """
    Classifies the variance between an invoice total/price and a PO value.
    
    Returns:
        str: "match", "minor", or "major"
    """
    if po_value == 0.0:
        return "major" if invoice_value > 0.0 else "match"
        
    diff = abs(invoice_value - po_value)
    pct_diff = diff / po_value
    
    if pct_diff == 0.0:
        return "match"
    elif pct_diff <= AMOUNT_MINOR_TOLERANCE_PCT:
        return "minor"
    elif pct_diff >= AMOUNT_MAJOR_THRESHOLD_PCT:
        return "major"
    else:
        # Between 2% and 5%
        return "minor"

def classify_line_item_variance(invoice_qty: float, po_qty: float, unit_price: float) -> str:
    """
    Classifies quantity discrepancies based on the dollar impact of the mismatch
    relative to the total line item value on the Purchase Order.
    
    Returns:
        str: "match", "minor", or "major"
    """
    if invoice_qty == po_qty:
        return "match"
        
    po_line_total = po_qty * unit_price
    dollar_impact = abs(invoice_qty - po_qty) * unit_price
    
    if po_line_total == 0.0:
        return "major" if dollar_impact > 0.0 else "match"
        
    pct_impact = dollar_impact / po_line_total
    
    if pct_impact <= AMOUNT_MINOR_TOLERANCE_PCT:
        return "minor"
    elif pct_impact >= AMOUNT_MAJOR_THRESHOLD_PCT:
        return "major"
    else:
        return "minor"

MANUAL_PROCESSING_COST_USD = 15.00
AUTOMATED_PROCESSING_COST_USD = 3.00
MANUAL_EXCEPTION_TIME_MINUTES = 25.0
AUTOMATED_EXCEPTION_TIME_MINUTES = 3.0
MANUAL_BASE_TIME_MINUTES = 5.0
AUTOMATED_BASE_TIME_MINUTES = 0.5

def estimate_savings(was_exception: bool) -> dict:
    """
    Returns the cost and time SAVED by automation (manual cost/time minus 
    automated cost/time).
    
    Returns:
        dict: {"cost_saved": float, "time_saved_minutes": float}
    """
    cost_saved = MANUAL_PROCESSING_COST_USD - AUTOMATED_PROCESSING_COST_USD
    if was_exception:
        time_saved = MANUAL_EXCEPTION_TIME_MINUTES - AUTOMATED_EXCEPTION_TIME_MINUTES
    else:
        time_saved = MANUAL_BASE_TIME_MINUTES - AUTOMATED_BASE_TIME_MINUTES
        
    return {"cost_saved": cost_saved, "time_saved_minutes": time_saved}



def can_auto_resolve(match_result: dict) -> bool:
    """
    Determines if a MatchResult can be auto-resolved per policy.
    True if all discrepancies are minor, or if there are no discrepancies.
    """
    discrepancies = match_result.get("discrepancies", [])
    return all(d.get("severity") == "minor" for d in discrepancies)

def auto_resolve_reasoning(match_result: dict) -> str:
    """
    Generates a plain-English explanation for auto-resolvable invoices.
    """
    discrepancies = match_result.get("discrepancies", [])
    if not discrepancies:
        return "Invoice matches purchase order exactly. No discrepancies found."
        
    explanations = []
    for d in discrepancies:
        field = d.get("field", "")
        inv_val = d.get("invoice_value", "")
        po_val = d.get("po_value", "")
        
        if "total_amount" in field:
            try:
                diff = abs(float(inv_val) - float(po_val))
                pct = (diff / float(po_val) * 100) if float(po_val) != 0 else 0
                explanations.append(f"Total amount variance of ${diff:.2f} ({pct:.2f}%) is within the 2% auto-approval tolerance.")
            except ValueError:
                explanations.append(f"Total amount variance (Invoice: {inv_val} vs PO: {po_val}) is within tolerance.")
        elif "unit_price" in field:
            explanations.append(f"Line item unit price difference for '{field}' (Invoice: {inv_val} vs PO: {po_val}) is within tolerance.")
        else:
            explanations.append(f"Minor discrepancy in '{field}' (Invoice: {inv_val} vs PO/GR: {po_val}) is within tolerance.")
            
    return " ".join(explanations) + " Auto-approved per policy."

if __name__ == "__main__":
    # Sanity-check scenarios
    scenarios = [
        # (Scenario Description, invoice_val, po_val)
        ("Exact match total amount", 100.0, 100.0),
        ("Minor difference (1% off)", 101.0, 100.0),
        ("Borderline minor difference (2% off)", 102.0, 100.0),
        ("Medium difference (3.5% off)", 103.5, 100.0),
        ("Major difference (6% off)", 106.0, 100.0),
    ]
    
    print("--- Amount Variance Classifications ---")
    for desc, inv, po in scenarios:
        res = classify_amount_variance(inv, po)
        pct = abs(inv - po) / po * 100
        print(f"{desc:<40} | Inv: {inv:<5} PO: {po:<5} | Diff: {pct:.1f}% -> Result: {res}")
        
    print("\n--- Line Item Quantity Variance Classifications ---")
    qty_scenarios = [
        # (Description, inv_qty, po_qty, unit_price)
        ("Exact quantity match", 10.0, 10.0, 15.0),
        ("Minor quantity difference (1 unit off, 10% impact but PO quantity is 50)", 49.0, 50.0, 10.0), # 1 unit off, po_total=500, impact=10 (2% impact)
        ("Major quantity difference (5 units off, PO quantity is 10)", 5.0, 10.0, 20.0), # 50% impact
    ]
    for desc, inv_qty, po_qty, price in qty_scenarios:
        res = classify_line_item_variance(inv_qty, po_qty, price)
        po_total = po_qty * price
        impact = abs(inv_qty - po_qty) * price
        pct = (impact / po_total * 100) if po_total > 0 else 0
        print(f"{desc:<65} | Inv Qty: {inv_qty:<4} PO Qty: {po_qty:<4} | Impact: {pct:.1f}% -> Result: {res}")

    print("\n--- Auto-Resolution Policy Check ---")
    dummy_match_clean = {"discrepancies": []}
    dummy_match_minor = {
        "discrepancies": [
            {"field": "total_amount", "invoice_value": "100.50", "po_value": "100.00", "severity": "minor"}
        ]
    }
    dummy_match_major = {
        "discrepancies": [
            {"field": "total_amount", "invoice_value": "106.00", "po_value": "100.00", "severity": "major"}
        ]
    }

    for name, r in [("Clean", dummy_match_clean), ("Minor", dummy_match_minor), ("Major", dummy_match_major)]:
        print(f"MatchResult [{name}] can auto-resolve? {can_auto_resolve(r)}")
        if can_auto_resolve(r):
            print(f"Reasoning: {auto_resolve_reasoning(r)}")

