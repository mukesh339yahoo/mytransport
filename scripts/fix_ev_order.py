import frappe

def run():
    doc = frappe.get_doc("DocType", "Expense Voucher")
    
    # 1. Move 'voucher_no' to the top of the fields list
    voucher_field = None
    for f in doc.fields:
        if f.fieldname == "voucher_no":
            voucher_field = f
            break
            
    if voucher_field:
        doc.fields.remove(voucher_field)
        doc.fields.insert(0, voucher_field)
        
    doc.save()
    frappe.db.commit()
    print("Expense Voucher field order updated successfully.")
