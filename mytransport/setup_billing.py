import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def run():
    custom_fields = {
        "Sales Invoice Item": [
            {
                "fieldname": "lorry_receipt",
                "label": "Lorry Receipt",
                "fieldtype": "Link",
                "options": "Lorry Receipt",
                "insert_after": "item_code"
            }
        ]
    }
    
    create_custom_fields(custom_fields, ignore_validate=True)
    frappe.db.commit()
    print("Created custom fields for Sales Invoice Item.")
