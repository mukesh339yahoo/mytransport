import frappe

def run():
    doc = frappe.get_doc("DocType", "Expense Voucher")
    
    # 1. Remove old fields
    fields_to_remove = ["challan", "payment_reference", "amount"]
    doc.fields = [f for f in doc.fields if f.fieldname not in fields_to_remove]
    
    fields_dict = {f.fieldname: f for f in doc.fields}
    
    # 2. Add new fields
    new_fields = [
        {"fieldname": "voucher_no", "fieldtype": "Data", "label": "Voucher No"},
        {"fieldname": "vendor", "fieldtype": "Link", "options": "Supplier", "label": "Vendor"},
        {"fieldname": "cheque_no", "fieldtype": "Data", "label": "Cheque No", "depends_on": "eval:doc.voucher_type=='Bank'"},
        {"fieldname": "cheque_date", "fieldtype": "Date", "label": "Cheque Date", "depends_on": "eval:doc.voucher_type=='Bank'"},
        {"fieldname": "get_unpaid_challans", "fieldtype": "Button", "label": "Get Unpaid Challans"},
        {"fieldname": "allocated_challans", "fieldtype": "Table", "options": "Allocated Challan", "label": "Allocated Challans"},
        {"fieldname": "total_paid_amt", "fieldtype": "Currency", "label": "Total Paid Amt", "read_only": 1},
        {"fieldname": "amount_in_words", "fieldtype": "Small Text", "label": "Amount in Words", "read_only": 1},
        {"fieldname": "on_account", "fieldtype": "Data", "label": "On Account"}
    ]
    
    for nf in new_fields:
        if nf["fieldname"] not in fields_dict:
            doc.append("fields", nf)
            fields_dict[nf["fieldname"]] = doc.fields[-1]
            
    # 3. Update section break labels if necessary
    if "sb1" in fields_dict:
        fields_dict["sb1"].label = "Allocation"
    if "sb2" in fields_dict:
        fields_dict["sb2"].label = "Totals & Remarks"
        
    # 4. Set field order
    new_order = [
        "voucher_no",
        "company",
        "date",
        "cb1",
        "voucher_type",
        "payment_account",
        "cheque_no",
        "cheque_date",
        "sb1",
        "expense_category",
        "expense_account",
        "vendor",
        "get_unpaid_challans",
        "allocated_challans",
        "sb2",
        "on_account",
        "total_paid_amt",
        "amount_in_words",
        "paid_to",
        "remarks",
        "journal_entry",
        "amended_from"
    ]
    
    ordered_fields = []
    for fn in new_order:
        if fn in fields_dict:
            ordered_fields.append(fields_dict[fn])
            
    doc.fields = ordered_fields
    doc.save()
    frappe.db.commit()
    print("Expense Voucher layout updated successfully.")
