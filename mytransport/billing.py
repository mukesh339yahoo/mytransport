import frappe

def on_submit(doc, method):
    # Link all LRs associated with this Sales Invoice
    for item in doc.items:
        if item.lorry_receipt:
            frappe.db.set_value("Lorry Receipt", item.lorry_receipt, {
                "sales_invoice": doc.name,
                "status": "Billed"
            })

def on_cancel(doc, method):
    # Unlink all LRs associated with this Sales Invoice
    for item in doc.items:
        if item.lorry_receipt:
            frappe.db.set_value("Lorry Receipt", item.lorry_receipt, {
                "sales_invoice": None,
                "status": "Unbilled"
            })
