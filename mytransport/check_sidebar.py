import frappe

def check():
    frappe.init(site="mytransport.localhost")
    frappe.connect()
    
    doc = frappe.get_doc("Workspace Sidebar", "Build")
    
    for item in doc.items:
        print(f"{item.label}: type={item.type}, link_type={item.link_type}, link_to={item.link_to}")

if __name__ == "__main__":
    check()
