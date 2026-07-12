import frappe

def create_doctypes():
    frappe.flags.in_test = True

    if not frappe.db.exists("DocType", "Branch"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "Mytransport",
            "custom": 0,
            "name": "Branch",
            "autoname": "field:branch_name",
            "fields": [
                {"fieldname": "branch_name", "fieldtype": "Data", "label": "Branch Name", "reqd": 1, "unique": 1, "in_list_view": 1},
                {"fieldname": "branch_code", "fieldtype": "Data", "label": "Branch Code", "reqd": 1, "in_list_view": 1},
                {"fieldname": "address", "fieldtype": "Small Text", "label": "Address"},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "contact_person", "fieldtype": "Data", "label": "Contact Person", "in_list_view": 1},
                {"fieldname": "phone", "fieldtype": "Data", "label": "Phone Number"}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "export": 1, "report": 1, "share": 1, "print": 1, "email": 1},
                {"role": "All", "read": 1}
            ]
        })
        doc.insert()
        frappe.db.commit()  # nosemgrep: required in standalone setup scripts
        print("Created Branch DocType")
    else:
        print("Branch DocType already exists")
