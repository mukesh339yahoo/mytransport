import frappe
import json

def run():
    # 1. Create Report
    if not frappe.db.exists("Report", "Challan Register"):
        doc = frappe.get_doc({
            "doctype": "Report",
            "name": "Challan Register",
            "report_name": "Challan Register",
            "ref_doctype": "Challan",
            "report_type": "Script Report",
            "is_standard": "Yes",
            "module": "Mytransport"
        })
        doc.insert(ignore_permissions=True)
        print("Challan Register report created.")

    # 2. Add to Workspace
    if frappe.db.exists("Workspace", "Transport"):
        ws = frappe.get_doc("Workspace", "Transport")
        
        # Check if shortcut already exists
        exists = False
        for s in ws.shortcuts:
            if s.link_to == "Challan Register":
                exists = True
                break
        
        if not exists:
            # Add to shortcuts table
            ws.append("shortcuts", {
                "type": "Report",
                "link_to": "Challan Register",
                "label": "Challan Register",
                "report_ref_doctype": "Challan"
            })
            
            # Add to content blocks
            content = json.loads(ws.content) if ws.content else []
            content.append({
                "id": frappe.generate_hash(length=10),
                "type": "shortcut",
                "data": {
                    "shortcut_name": "Challan Register",
                    "col": 3
                }
            })
            ws.content = json.dumps(content)
            ws.save(ignore_permissions=True)
            print("Added to Transport Workspace.")
            
    frappe.db.commit()  # nosemgrep: required in standalone setup scripts
