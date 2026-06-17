import frappe

def run():
    doc = frappe.get_doc("DocType", "Money Receipt")
    
    fields_dict = {f.fieldname: f for f in doc.fields}
    
    # 1. Add mr_no Data field if not exists
    if "mr_no" not in fields_dict:
        doc.append("fields", {
            "fieldname": "mr_no",
            "fieldtype": "Data",
            "label": "MR No",
            "insert_after": "date"
        })
        
        # Sort fields to respect insert_after
        # A simple way to reorder based on insert_after
        ordered = []
        # Find 'date' field index
        date_idx = 0
        for i, f in enumerate(doc.fields):
            if f.fieldname == "date":
                date_idx = i
                break
                
        # Move mr_no right after date
        # It's at the end of doc.fields right now
        mr_no_field = doc.fields.pop()
        doc.fields.insert(date_idx + 1, mr_no_field)
        
        doc.save()
        frappe.db.commit()
        print("Added MR No field to Money Receipt.")
    else:
        print("MR No field already exists.")
