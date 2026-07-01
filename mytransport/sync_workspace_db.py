import frappe

def sync():
    frappe.init(site="mytransport.localhost")
    frappe.connect()
    
    doc = frappe.get_doc("Workspace", "Transport")
    
    # Clear existing links
    doc.links = []
    
    # Add Documents section
    doc.append("links", {
        "type": "Card Break",
        "label": "Documents",
        "link_type": "DocType",
        "is_query_report": 0,
        "hidden": 0
    })
    
    docs = [
        ("Lorry Receipt", "DocType"),
        ("Challan", "DocType"),
        ("Transport Invoice", "DocType"),
        ("Money Receipt", "DocType"),
        ("Expense Voucher", "DocType")
    ]
    
    for label, link_type in docs:
        doc.append("links", {
            "type": "Link",
            "label": label,
            "link_to": label,
            "link_type": link_type,
            "is_query_report": 0,
            "hidden": 0
        })
        
    # Add Reports section
    doc.append("links", {
        "type": "Card Break",
        "label": "Reports",
        "link_type": "DocType",
        "is_query_report": 0,
        "hidden": 0
    })
    
    reports = [
        ("LR Register", "Report"),
        ("LR Status Report", "Report"),
        ("Challan Costing Report", "Report"),
        ("Challan Register", "Report")
    ]
    
    for label, link_type in reports:
        doc.append("links", {
            "type": "Link",
            "label": label,
            "link_to": label,
            "link_type": link_type,
            "is_query_report": 0,
            "hidden": 0
        })
        
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    print("Workspace Transport updated in DB!")

if __name__ == "__main__":
    sync()
