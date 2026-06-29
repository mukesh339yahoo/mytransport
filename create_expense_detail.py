import frappe
import sys

def execute():
    frappe.init(site="mytransport.localhost")
    frappe.connect()
    
    try:
        if not frappe.db.exists("DocType", "Expense Detail"):
            doc = frappe.get_doc({
                "doctype": "DocType",
                "name": "Expense Detail",
                "module": "Mytransport",
                "custom": 1,
                "istable": 1,
                "editable_grid": 1,
                "fields": [
                    {
                        "fieldname": "expense_item",
                        "fieldtype": "Select",
                        "label": "Expense Item",
                        "options": "Detention Charge\nHamali Charge\nAdvance\nBalance\nMiscellaneous",
                        "in_list_view": 1,
                        "reqd": 1
                    },
                    {
                        "fieldname": "expense_amount",
                        "fieldtype": "Currency",
                        "label": "Expense Amount",
                        "in_list_view": 1,
                        "reqd": 1
                    },
                    {
                        "fieldname": "challan_ref",
                        "fieldtype": "Link",
                        "label": "Challan Ref No",
                        "options": "Challan",
                        "in_list_view": 1
                    }
                ]
            })
            doc.insert(ignore_permissions=True)
            print("Expense Detail DocType created")
        else:
            print("Expense Detail DocType already exists")

        doc = frappe.get_doc("DocType", "Expense Voucher")
        
        has_section = any(f.fieldname == "expense_details_section" for f in doc.fields)
        if not has_section:
            insert_idx = len(doc.fields)
            for i, f in enumerate(doc.fields):
                if f.fieldname == "allocated_challans":
                    insert_idx = i + 1
                    break
                    
            doc.fields.insert(insert_idx, frappe._dict({
                "fieldname": "expense_details_section",
                "fieldtype": "Section Break",
                "label": "Expense Details"
            }))
            
            doc.fields.insert(insert_idx + 1, frappe._dict({
                "fieldname": "expense_details",
                "fieldtype": "Table",
                "label": "Expense Details",
                "options": "Expense Detail"
            }))
            
            doc.save(ignore_permissions=True)
            print("Expense Voucher updated with Expense Details section")
        else:
            print("Expense Voucher already has Expense Details section")
            
        frappe.db.commit()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        frappe.destroy()

if __name__ == "__main__":
    execute()
