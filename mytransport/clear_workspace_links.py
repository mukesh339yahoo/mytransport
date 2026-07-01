import frappe

def clear():
    frappe.init(site="mytransport.localhost")
    frappe.connect()
    
    doc = frappe.get_doc("Workspace", "Transport")
    doc.links = []
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    print("Transport Workspace links cleared in DB!")

if __name__ == "__main__":
    clear()
