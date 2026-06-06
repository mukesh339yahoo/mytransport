import frappe

def create_doctypes():
    frappe.flags.in_test = True

    # 1. Create Challan LR Item
    if not frappe.db.exists("DocType", "Challan LR Item"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "Mytransport",
            "custom": 0,
            "name": "Challan LR Item",
            "istable": 1,
            "editable_grid": 1,
            "fields": [
                {"fieldname": "lr_number", "fieldtype": "Link", "options": "Lorry Receipt", "label": "LR Number", "in_list_view": 1, "reqd": 1},
                {"fieldname": "to_city", "fieldtype": "Data", "label": "To City", "fetch_from": "lr_number.to_city", "read_only": 1, "in_list_view": 1},
                {"fieldname": "total_amount", "fieldtype": "Currency", "label": "Total Amount", "fetch_from": "lr_number.total_amount", "read_only": 1, "in_list_view": 1}
            ]
        })
        doc.insert()
        frappe.db.commit()
        print("Created Challan LR Item DocType")
    else:
        print("Challan LR Item already exists")

    # 2. Create Challan
    if not frappe.db.exists("DocType", "Challan"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "Mytransport",
            "custom": 0,
            "name": "Challan",
            "is_submittable": 1,
            "autoname": "field:challan_number",
            "fields": [
                {"fieldname": "challan_number", "fieldtype": "Data", "label": "Challan Number", "reqd": 1, "unique": 1},
                {"fieldname": "date", "fieldtype": "Date", "label": "Date", "default": "Today", "reqd": 1, "in_list_view": 1},
                
                {"fieldname": "location_sec", "fieldtype": "Section Break", "label": "Location Details"},
                {"fieldname": "from_location", "fieldtype": "Data", "label": "From Location", "reqd": 1, "in_list_view": 1},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "to_location", "fieldtype": "Data", "label": "To Location", "reqd": 1, "in_list_view": 1},
                
                {"fieldname": "vehicle_details_sec", "fieldtype": "Section Break", "label": "Vehicle Details"},
                {"fieldname": "vehicle_number", "fieldtype": "Data", "label": "Vehicle Number", "in_list_view": 1},
                {"fieldname": "driver_name", "fieldtype": "Data", "label": "Driver Name"},
                {"fieldname": "column_break_2", "fieldtype": "Column Break"},
                {"fieldname": "driver_phone", "fieldtype": "Data", "label": "Driver Phone"},
                
                {"fieldname": "lrs_sec", "fieldtype": "Section Break", "label": "Lorry Receipts"},
                {"fieldname": "lrs", "fieldtype": "Table", "label": "Lorry Receipts", "options": "Challan LR Item"},
                
                {"fieldname": "finance_sec", "fieldtype": "Section Break", "label": "Trip Finance"},
                {"fieldname": "total_hire_amount", "fieldtype": "Currency", "label": "Total Hire Amount"},
                {"fieldname": "column_break_3", "fieldtype": "Column Break"},
                {"fieldname": "advance", "fieldtype": "Currency", "label": "Advance"},
                {"fieldname": "balance_amount", "fieldtype": "Currency", "label": "Balance Amount", "read_only": 1}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1, "export": 1, "report": 1, "share": 1, "print": 1, "email": 1}
            ]
        })
        doc.insert()
        frappe.db.commit()
        print("Created Challan DocType")
    else:
        print("Challan already exists")
