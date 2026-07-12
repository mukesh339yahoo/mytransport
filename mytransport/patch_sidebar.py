import frappe

def patch():
    frappe.init(site="mytransport.localhost")
    frappe.connect()
    
    doc = frappe.get_doc("Workspace Sidebar", "Transport")
    
    # Clear existing items
    doc.items = []
    
    # Add Documents category
    doc.append("items", {
        "type": "Sidebar Item Group",
        "label": "Documents"
    })
    
    docs = [
        ("Lorry Receipt", "DocType"),
        ("Challan", "DocType"),
        ("Transport Invoice", "DocType"),
        ("Money Receipt", "DocType"),
        ("Expense Voucher", "DocType")
    ]
    
    for label, link_type in docs:
        doc.append("items", {
            "type": "Link",
            "label": label,
            "link_to": label,
            "link_type": link_type
        })
        
    # Add Reports category
    doc.append("items", {
        "type": "Sidebar Item Group",
        "label": "Reports"
    })
    
    reports = [
        ("LR Register", "Report"),
        ("LR Status Report", "Report"),
        ("Challan Costing Report", "Report"),
        ("Challan Register", "Report")
    ]
    
    for label, link_type in reports:
        doc.append("items", {
            "type": "Link",
            "label": label,
            "link_to": label,
            "link_type": link_type
        })
        
    doc.save(ignore_permissions=True)
    frappe.db.commit()  # nosemgrep: required in standalone setup scripts
    print("Workspace Sidebar updated successfully!")

if __name__ == "__main__":
    patch()
