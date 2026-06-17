import frappe

def run():
    doc = frappe.get_doc("DocType", "Money Receipt")
    
    # current fields
    ordered = []
    
    # Find mr_no
    mr_no_field = next((f for f in doc.fields if f.fieldname == "mr_no"), None)
    
    if mr_no_field:
        ordered.append(mr_no_field)
        for f in doc.fields:
            if f.fieldname != "mr_no":
                ordered.append(f)
                
        doc.fields = ordered
        doc.save()
        frappe.db.commit()
        print("MR No moved to the top.")
    else:
        print("MR No not found.")
