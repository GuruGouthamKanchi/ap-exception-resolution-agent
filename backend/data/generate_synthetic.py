"""
Synthetic Data Generator for AP Exception Resolution Agent.
Generates realistic purchase orders, invoices, and goods receipts with controlled discrepancies:
- Clean Matches (18): Invoice and PO details are identical.
- Minor Discrepancies (7): Small differences under 2% (e.g., unit price off by $0.01, rounding differences).
- Major Discrepancies (5): Missing items, quantity mismatch, wrong PO number, or total off by > 5%.
- Goods Receipts (30): 3 simulated as partial receipts (fewer items/quantities than PO).
"""

import os
import json
import random
import sys
from datetime import datetime, timedelta

# Ensure parent directory is in sys.path to run as script directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import LineItem, Invoice, PurchaseOrder, GoodsReceipt

def generate_synthetic_data():
    random.seed(42)

    # 15 realistic vendors
    vendors = [
        "Global Logistics Solutions", "Nexis Office Supplies", "Titan Industrial Parts",
        "Aurora Cloud Services", "Prime Packaging Corp", "Vanguard Electronics",
        "Zenith Catering", "Apex Tooling Co", "Sentinel Facilities Management",
        "Egis Security Systems", "Verdant Landscaping", "Summit Marketing Agency",
        "Atlas Construction Materials", "Novus Tech Solutions", "Pinnacle Consulting Group"
    ]

    # Sample items per vendor category to make line items look realistic
    item_catalog = {
        "Logistics": [("Shipping pallets", 25.00), ("Freight fee", 150.00), ("Bubble wrap rolls", 45.00)],
        "Office": [("Ergonomic chairs", 199.99), ("Whiteboards", 85.00), ("Copy paper cases", 32.50)],
        "Industrial": [("Hydraulic fluid", 80.00), ("Replacement gaskets", 4.50), ("Steel bolts pack", 12.00)],
        "Cloud": [("SaaS Seat License", 45.00), ("Compute resource unit", 12.50), ("Storage GB premium", 0.15)],
        "Packaging": [("Cardboard boxes small", 0.75), ("Packing tape", 3.20), ("Mailer envelopes", 0.45)],
        "Electronics": [("Monitors 27inch", 249.99), ("HDMI Cables", 9.99), ("USB-C Hubs", 39.99)]
    }
    catalog_keys = list(item_catalog.keys())

    purchase_orders = []
    invoices = []
    goods_receipts = []

    # Distribution tracks
    clean_invoices_needed = 18
    minor_invoices_needed = 7
    major_invoices_needed = 5
    partial_receipts_needed = 3

    for i in range(1, 31):
        po_number = f"PO-{1000 + i}"
        invoice_id = f"INV-{5000 + i}"
        vendor_name = vendors[i % len(vendors)]
        
        # Determine items
        category = catalog_keys[i % len(catalog_keys)]
        items_pool = item_catalog[category]
        num_items = random.randint(1, 4)
        selected_pool_items = random.sample(items_pool, min(num_items, len(items_pool)))
        
        po_line_items = []
        po_total = 0.0
        for desc, unit_price in selected_pool_items:
            quantity = float(random.randint(5, 50))
            line_total = round(quantity * unit_price, 2)
            po_line_items.append(LineItem(
                description=desc,
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total
            ))
            po_total += line_total
        po_total = round(po_total, 2)

        # Create PO
        po = PurchaseOrder(
            po_number=po_number,
            vendor_name=vendor_name,
            line_items=po_line_items,
            total_amount=po_total,
            status="open"
        )
        purchase_orders.append(po)

        # Create Invoice
        invoice_date = (datetime.now() - timedelta(days=random.randint(1, 10))).isoformat()
        
        # Decide discrepancy type
        if clean_invoices_needed > 0:
            # Clean Match
            inv_line_items = [LineItem(**item.model_dump()) for item in po_line_items]
            inv_total = po_total
            inv_po_number = po_number
            clean_invoices_needed -= 1
        elif minor_invoices_needed > 0:
            # Minor Discrepancy (e.g. price off by 1 cent, or minor rounding discrepancy < 2%)
            inv_line_items = []
            inv_total = 0.0
            
            # Modify unit price or total by a minor amount
            for idx, item in enumerate(po_line_items):
                mod_item = LineItem(**item.model_dump())
                if idx == 0:  # Modify first item unit price slightly
                    mod_item.unit_price = round(mod_item.unit_price + 0.01, 2)
                    mod_item.line_total = round(mod_item.quantity * mod_item.unit_price, 2)
                inv_line_items.append(mod_item)
                inv_total += mod_item.line_total
            
            # Or add a tiny tax rounding to overall total (0.50)
            if random.choice([True, False]):
                inv_total = round(inv_total + 0.50, 2)
            else:
                inv_total = round(inv_total, 2)

            inv_po_number = po_number
            minor_invoices_needed -= 1
        else:
            # Major Discrepancy
            inv_line_items = []
            inv_total = 0.0
            major_type = major_invoices_needed  # Let's do different types of major mismatch

            if major_type == 5:
                # Type 1: Missing a line item (if more than 1 item)
                if len(po_line_items) > 1:
                    inv_line_items = [LineItem(**item.model_dump()) for item in po_line_items[:-1]]
                else:
                    inv_line_items = [LineItem(**item.model_dump()) for item in po_line_items]
                    # Fallback to quantity mismatch
                    inv_line_items[0].quantity = round(inv_line_items[0].quantity * 1.5, 2)
                    inv_line_items[0].line_total = round(inv_line_items[0].quantity * inv_line_items[0].unit_price, 2)
            elif major_type == 4:
                # Type 2: Quantity mismatch (double the quantity)
                for item in po_line_items:
                    mod_item = LineItem(**item.model_dump())
                    mod_item.quantity = round(mod_item.quantity * 2, 2)
                    mod_item.line_total = round(mod_item.quantity * mod_item.unit_price, 2)
                    inv_line_items.append(mod_item)
            elif major_type == 3:
                # Type 3: Wrong PO number reference
                inv_line_items = [LineItem(**item.model_dump()) for item in po_line_items]
                inv_po_number = f"PO-{1999 + i}"
            elif major_type == 2:
                # Type 4: Total amount off by > 5% (excessive billing)
                inv_line_items = [LineItem(**item.model_dump()) for item in po_line_items]
                inv_total = round(po_total * 1.15, 2)
            else:
                # Type 5: Completely different unit price
                for item in po_line_items:
                    mod_item = LineItem(**item.model_dump())
                    mod_item.unit_price = round(mod_item.unit_price * 1.30, 2)
                    mod_item.line_total = round(mod_item.quantity * mod_item.unit_price, 2)
                    inv_line_items.append(mod_item)

            if not inv_total:
                inv_total = round(sum(item.line_total for item in inv_line_items), 2)
            if 'inv_po_number' not in locals():
                inv_po_number = po_number

            inv_line_items = inv_line_items if inv_line_items else [LineItem(**item.model_dump()) for item in po_line_items]
            major_invoices_needed -= 1

        inv = Invoice(
            invoice_id=invoice_id,
            vendor_name=vendor_name,
            invoice_date=invoice_date,
            po_number=inv_po_number,
            currency="USD",
            line_items=inv_line_items,
            total_amount=inv_total,
            raw_source="pdf"
        )
        invoices.append(inv)

        # Create GoodsReceipt corresponding to PO
        receipt_items = []
        if partial_receipts_needed > 0 and i in [5, 12, 23]:  # Select specific records for partial receipts
            # Partial Receipt: Lower quantity on first item
            for idx, item in enumerate(po_line_items):
                mod_item = LineItem(**item.model_dump())
                if idx == 0:
                    mod_item.quantity = max(1.0, round(mod_item.quantity - 3.0, 2))
                    mod_item.line_total = round(mod_item.quantity * mod_item.unit_price, 2)
                receipt_items.append(mod_item)
            partial_receipts_needed -= 1
        else:
            # Full Receipt
            receipt_items = [LineItem(**item.model_dump()) for item in po_line_items]

        receipt = GoodsReceipt(
            po_number=po_number,
            received_items=receipt_items,
            receipt_date=(datetime.now() - timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d")
        )
        goods_receipts.append(receipt)

    # Save to JSON files
    data_dir = os.path.dirname(os.path.abspath(__file__))
    
    with open(os.path.join(data_dir, "purchase_orders.json"), "w") as f:
        json.dump([po.model_dump() for po in purchase_orders], f, indent=2)
        
    with open(os.path.join(data_dir, "invoices.json"), "w") as f:
        json.dump([inv.model_dump() for inv in invoices], f, indent=2)

    with open(os.path.join(data_dir, "goods_receipts.json"), "w") as f:
        json.dump([gr.model_dump() for gr in goods_receipts], f, indent=2)

    # Print summary counts for verification
    print("Generation complete!")
    print(f"Total Purchase Orders generated: {len(purchase_orders)}")
    print(f"Total Invoices generated: {len(invoices)}")
    print(f"Total Goods Receipts generated: {len(goods_receipts)}")
    
    # Calculate distributions from created data
    clean_cnt = 0
    minor_cnt = 0
    major_cnt = 0
    partial_gr_cnt = 0

    for po, inv, gr in zip(purchase_orders, invoices, goods_receipts):
        # Check partial GR
        if len(gr.received_items) < len(po.line_items) or any(
            gr.received_items[idx].quantity < item.quantity 
            for idx, item in enumerate(po.line_items)
        ):
            partial_gr_cnt += 1

        # Evaluate mismatch severity
        if inv.po_number != po.po_number:
            major_cnt += 1
            continue
            
        po_items_map = {item.description: item for item in po.line_items}
        inv_items_map = {item.description: item for item in inv.line_items}
        
        if set(po_items_map.keys()) != set(inv_items_map.keys()):
            major_cnt += 1
            continue
            
        # Check items discrepancy
        has_major = False
        has_minor = False
        for desc, po_item in po_items_map.items():
            inv_item = inv_items_map[desc]
            qty_diff_pct = abs(inv_item.quantity - po_item.quantity) / po_item.quantity
            price_diff_pct = abs(inv_item.unit_price - po_item.unit_price) / po_item.unit_price
            
            if qty_diff_pct > 0.05 or price_diff_pct > 0.05:
                has_major = True
            elif qty_diff_pct > 0.0 or price_diff_pct > 0.0:
                has_minor = True

        total_diff_pct = abs(inv.total_amount - po.total_amount) / po.total_amount
        if total_diff_pct > 0.05:
            has_major = True
        elif total_diff_pct > 0.0:
            has_minor = True

        if has_major:
            major_cnt += 1
        elif has_minor:
            minor_cnt += 1
        else:
            clean_cnt += 1

    print(f"  - Clean Matches: {clean_cnt}")
    print(f"  - Minor Discrepancies: {minor_cnt}")
    print(f"  - Major Discrepancies: {major_cnt}")
    print(f"  - Partial Receipts: {partial_gr_cnt}")

def generate_raw_invoice_text(invoice: Invoice) -> str:
    """
    Renders an Invoice object as a messy, realistic plain text OCR simulation.
    Varies layout styles, dates, currency formats, and inserts whitespace noise.
    Ground truth values remain recoverable.
    """
    # Deterministic styling based on invoice_id hash
    seed_val = sum(ord(c) for c in invoice.invoice_id)
    r = random.Random(seed_val)
    
    # Date formatting styles
    date_obj = datetime.fromisoformat(invoice.invoice_date.replace("Z", ""))
    date_styles = [
        date_obj.strftime("%Y-%m-%d"),
        date_obj.strftime("%m/%d/%Y"),
        date_obj.strftime("%B %d, %Y"),
        date_obj.strftime("%d-%b-%Y")
    ]
    formatted_date = r.choice(date_styles)
    
    # Currency styles
    def fmt_curr(val):
        styles = [
            f"${val:,.2f}",
            f"{val:,.2f} USD",
            f"USD {val:,.2f}",
            f"${val:,.2f}    "
        ]
        return r.choice(styles).strip()

    layout_type = r.choice(["label_value", "loose_table", "mixed_layout"])
    
    lines = []
    
    # Vendor & header section variation
    if r.choice([True, False]):
        lines.append(f"=== {invoice.vendor_name.upper()} ===")
        lines.append(f"Invoice Ref: {invoice.invoice_id}")
    else:
        lines.append(f"INVOICE: #{invoice.invoice_id}")
        lines.append(f"Vendor: {invoice.vendor_name}")
        
    lines.append(f"Date: {formatted_date}")
    lines.append(f"PO Number: {invoice.po_number}")
    lines.append("")
    
    if layout_type == "label_value":
        lines.append("--- LINE ITEMS ---")
        for item in invoice.line_items:
            lines.append(f"Item: {item.description}")
            lines.append(f"  Qty: {item.quantity}  @  {fmt_curr(item.unit_price)}")
            lines.append(f"  Total: {fmt_curr(item.line_total)}")
            lines.append("")
    elif layout_type == "loose_table":
        lines.append(f"Description                      Qty      Unit Price     Total")
        lines.append(f"--------------------------------------------------------------")
        for item in invoice.line_items:
            desc_part = f"{item.description:<30}"
            qty_part = f"{item.quantity:>5}"
            price_part = f"{fmt_curr(item.unit_price):>15}"
            total_part = f"{fmt_curr(item.line_total):>15}"
            lines.append(f"{desc_part} {qty_part} {price_part} {total_part}")
    else:
        lines.append("Items purchased:")
        for item in invoice.line_items:
            lines.append(f"* {item.description} -- {item.quantity} units x {fmt_curr(item.unit_price)} = {fmt_curr(item.line_total)}")
            
    lines.append("")
    lines.append(f"Total Amount Due: {fmt_curr(invoice.total_amount)}")
    lines.append(f"Currency: {invoice.currency}")
    lines.append("Please remit payment within 30 days.")
    
    raw_text = "\n".join(lines)
    # Inject occasional raw text noise
    if r.choice([True, False]):
        raw_text = raw_text.replace("Amount Due:", "Amount  \nDue:")
    if r.choice([True, False]):
        raw_text = raw_text.replace("PO Number:", "P.O. NO:")
        
    return raw_text

def run_raw_text_generation():
    """Reads invoices.json, generates raw text, and saves to raw_invoice_texts.json."""
    data_dir = os.path.dirname(os.path.abspath(__file__))
    invoices_path = os.path.join(data_dir, "invoices.json")
    
    with open(invoices_path, "r") as f:
        invoices_data = json.load(f)
        
    raw_texts = []
    for inv_dict in invoices_data:
        # Load back into Pydantic model
        invoice_obj = Invoice(**inv_dict)
        raw_text = generate_raw_invoice_text(invoice_obj)
        raw_texts.append({
            "invoice_id": invoice_obj.invoice_id,
            "raw_text": raw_text
        })
        
    output_path = os.path.join(data_dir, "raw_invoice_texts.json")
    with open(output_path, "w") as f:
        json.dump(raw_texts, f, indent=2)
        
    print(f"Generated raw text OCR simulations for {len(raw_texts)} invoices.")
    print("\n--- SAMPLE 1 ---")
    print(raw_texts[0]["raw_text"])
    print("\n--- SAMPLE 2 ---")
    print(raw_texts[1]["raw_text"])
    print("\n--- SAMPLE 3 ---")
    print(raw_texts[2]["raw_text"])

if __name__ == "__main__":
    generate_synthetic_data()
    run_raw_text_generation()

