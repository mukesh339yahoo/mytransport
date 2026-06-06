import frappe

def run():
    # LR Register
    if not frappe.db.exists("Report", "LR Register"):
        doc = frappe.get_doc({
            "doctype": "Report",
            "name": "LR Register",
            "report_name": "LR Register",
            "ref_doctype": "Lorry Receipt",
            "report_type": "Script Report",
            "is_standard": "Yes",
            "module": "Mytransport"
        })
        doc.insert(ignore_permissions=True)
        print("LR Register report created.")

    # LR Status Report
    if not frappe.db.exists("Report", "LR Status Report"):
        doc = frappe.get_doc({
            "doctype": "Report",
            "name": "LR Status Report",
            "report_name": "LR Status Report",
            "ref_doctype": "Lorry Receipt",
            "report_type": "Script Report",
            "is_standard": "Yes",
            "module": "Mytransport"
        })
        doc.insert(ignore_permissions=True)
        print("LR Status Report created.")
        
    frappe.db.commit()
