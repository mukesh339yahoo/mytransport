import frappe

def run():
    # Challan Costing Report
    if not frappe.db.exists("Report", "Challan Costing Report"):
        doc = frappe.get_doc({
            "doctype": "Report",
            "name": "Challan Costing Report",
            "report_name": "Challan Costing Report",
            "ref_doctype": "Challan",
            "report_type": "Script Report",
            "is_standard": "Yes",
            "module": "Mytransport"
        })
        doc.insert(ignore_permissions=True)
        print("Challan Costing Report created.")
    frappe.db.commit()
