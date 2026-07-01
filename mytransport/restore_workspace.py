import frappe
import json
import os

def restore():
    frappe.init(site="mytransport.localhost")
    frappe.connect()
    
    app_path = frappe.get_app_path("mytransport")
    ws_path = os.path.join(app_path, "mytransport", "workspace", "transport", "transport.json")
    
    with open(ws_path, "r") as f:
        data = json.load(f)
        
    doc = frappe.get_doc("Workspace", "Transport")
    
    # Restore the exact fields from JSON
    doc.update(data)
    
    # Clear any links that were wrongly added
    doc.links = []
    if "links" in data:
        for l in data["links"]:
            doc.append("links", l)
            
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    print("Transport Workspace restored in DB!")

if __name__ == "__main__":
    restore()
