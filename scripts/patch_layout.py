import frappe

def run():
    mr = frappe.get_doc("DocType", "Money Receipt")
    
    # Remove total_amount_received and unallocated_amount and cb2
    mr.fields = [f for f in mr.fields if f.fieldname not in ("total_amount_received", "unallocated_amount", "cb2")]
    
    # Get the fields dictionary for easy updates
    fields_dict = {f.fieldname: f for f in mr.fields}
    
    # Change on_account to Data (text box)
    if "on_account" in fields_dict:
        fields_dict["on_account"].fieldtype = "Data"
        fields_dict["on_account"].label = "On Account"
    
    # Rename sb2 to "Totals & Remarks"
    if "sb2" in fields_dict:
        fields_dict["sb2"].label = "Totals & Remarks"
        
    # Create an sb3 for spreading across columns if needed
    if "sb3" not in fields_dict:
        mr.append("fields", {
            "fieldname": "sb3",
            "fieldtype": "Section Break",
            "label": "Additional Information"
        })
    
    # Set the precise field order
    new_order = [
        "company",
        "customer",
        "date",
        "cb1",
        "payment_mode",
        "deposit_account",
        "cheque_no",
        "cheque_date",
        "sb1",
        "get_unpaid_bills",
        "allocated_invoices",
        "sb3",
        "on_account",
        "sb2",
        "total_amount",
        "amount_in_words",
        "remarks",
        "payment_entry",
        "amended_from"
    ]
    
    # Apply order
    ordered_fields = []
    for fieldname in new_order:
        # Find the field in current fields
        field = next((f for f in mr.fields if f.fieldname == fieldname), None)
        if field:
            ordered_fields.append(field)
            
    mr.fields = ordered_fields
    mr.save()
    frappe.db.commit()
    print("Money Receipt Layout Updated Successfully.")
