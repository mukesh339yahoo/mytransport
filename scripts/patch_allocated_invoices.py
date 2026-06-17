import frappe

def run():
    doc = frappe.get_doc("DocType", "Allocated Transport Invoice")
    
    fields_dict = {f.fieldname: f for f in doc.fields}
    
    # 1. Add transport_invoice Link field if not exists
    if "transport_invoice" not in fields_dict:
        doc.append("fields", {
            "fieldname": "transport_invoice",
            "fieldtype": "Link",
            "options": "Transport Invoice",
            "label": "Invoice Ref",
            "in_list_view": 1,
            "reqd": 1,
            "insert_after": "idx" if "idx" in fields_dict else ""
        })
    
    # 2. Update bill_no to be Data, fetched from transport_invoice.bill_no
    if "bill_no" in fields_dict:
        fields_dict["bill_no"].fieldtype = "Data"
        fields_dict["bill_no"].options = ""
        fields_dict["bill_no"].label = "Bill No"
        fields_dict["bill_no"].fetch_from = "transport_invoice.bill_no"
        fields_dict["bill_no"].read_only = 1
        fields_dict["bill_no"].reqd = 0
        
    # 3. Update other fetched fields to use transport_invoice
    if "bill_date" in fields_dict:
        fields_dict["bill_date"].fetch_from = "transport_invoice.date"
    if "total_amt" in fields_dict:
        fields_dict["total_amt"].fetch_from = "transport_invoice.total_amount"
    if "balance" in fields_dict:
        fields_dict["balance"].fetch_from = "transport_invoice.outstanding_amount"
        
    # Make sure transport_invoice is first
    ordered_fields = []
    
    # ensure transport_invoice is first, then bill_no, bill_date, etc.
    desired_order = ["transport_invoice", "bill_no", "bill_date", "total_amt", "balance", "paid_amt", "deduct_amt", "tds_amt", "outstanding_amt"]
    
    for f_name in desired_order:
        f = next((f for f in doc.fields if f.fieldname == f_name), None)
        if f:
            ordered_fields.append(f)
            
    doc.fields = ordered_fields
    doc.save()
    frappe.db.commit()
    print("Allocated Transport Invoice child table updated.")
