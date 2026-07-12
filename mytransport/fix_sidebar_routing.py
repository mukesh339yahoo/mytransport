import frappe

def fix():
    frappe.init(site="mytransport.localhost")
    frappe.connect()
    
    doc = frappe.get_doc("Workspace Sidebar", "Transport")
    
    # Check if Home link already exists
    if not any(item.link_type == "Workspace" for item in doc.items):
        # Insert at the top
        home_item = doc.append("items", {
            "type": "Link",
            "label": "Home",
            "link_to": "Transport",
            "link_type": "Workspace"
        })
        
        # Move it to the beginning of the list
        doc.items.insert(0, doc.items.pop())
        
        # Re-index
        for i, item in enumerate(doc.items):
            item.idx = i + 1
            
        doc.save(ignore_permissions=True)
        frappe.db.commit()  # nosemgrep: required in standalone setup scripts
        print("Transport Workspace routing fixed!")

if __name__ == "__main__":
    fix()
