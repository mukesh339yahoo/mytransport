import frappe

def patch():
    frappe.init(site="mytransport.localhost")
    frappe.connect()
    
    doc = frappe.get_doc("Workspace Sidebar", "Transport")
    
    new_reports = ["Transport Invoice Register", "Money Receipt Register", "Expense Voucher Register"]
    
    for report_name in new_reports:
        # Check if already exists
        if not any(item.link_to == report_name for item in doc.items):
            doc.append("items", {
                "type": "Link",
                "label": report_name,
                "link_to": report_name,
                "link_type": "Report"
            })
            
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    print("Workspace Sidebar updated with new reports!")

if __name__ == "__main__":
    patch()
