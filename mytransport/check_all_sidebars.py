import frappe

def check():
    frappe.init(site="mytransport.localhost")
    frappe.connect()
    
    docs = frappe.get_all("Workspace Sidebar", pluck="name")
    for ws_name in docs[:5]:
        doc = frappe.get_doc("Workspace Sidebar", ws_name)
        if doc.items:
            item = doc.items[0]
            print(f"[{ws_name}] {item.label}: type={item.type}, link_type={item.link_type}, link_to={item.link_to}")

if __name__ == "__main__":
    check()
