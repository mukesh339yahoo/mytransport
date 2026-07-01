import frappe

def check():
    frappe.init(site="mytransport.localhost")
    frappe.connect()
    
    doc = frappe.get_doc("Workspace Sidebar", "Transport")
    
    print(f"Child tables for Workspace Sidebar:")
    for d in doc.meta.get("fields", {"fieldtype": "Table"}):
        print(f" - {d.fieldname} (options: {d.options})")
        
    print("\nChild table fields:")
    child_table = doc.meta.get("fields", {"fieldtype": "Table"})[0].options
    child_meta = frappe.get_meta(child_table)
    for d in child_meta.get("fields"):
        print(f" - {d.fieldname} ({d.fieldtype})")

if __name__ == "__main__":
    check()
