import frappe

def create_doctypes():
    frappe.flags.in_test = True

    # 1. Create LR Item
    if not frappe.db.exists("DocType", "LR Item"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "Mytransport",
            "custom": 0,
            "name": "LR Item",
            "istable": 1,
            "editable_grid": 1,
            "fields": [
                {"fieldname": "item_description", "fieldtype": "Data", "label": "Item Description", "in_list_view": 1},
                {"fieldname": "qty", "fieldtype": "Int", "label": "Quantity", "in_list_view": 1},
                {"fieldname": "actual_weight", "fieldtype": "Float", "label": "Actual Weight", "in_list_view": 1},
                {"fieldname": "charged_weight", "fieldtype": "Float", "label": "Charged Weight"},
                {"fieldname": "rate", "fieldtype": "Currency", "label": "Rate", "in_list_view": 1},
                {"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "in_list_view": 1}
            ]
        })
        doc.insert()
        frappe.db.commit()  # nosemgrep: required in standalone setup scripts
        print("Created LR Item DocType")
    else:
        print("LR Item already exists")

    # 2. Create Lorry Receipt
    if not frappe.db.exists("DocType", "Lorry Receipt"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "Mytransport",
            "custom": 0,
            "name": "Lorry Receipt",
            "is_submittable": 1,
            "autoname": "naming_series:",
            "fields": [
                {"fieldname": "naming_series", "fieldtype": "Select", "label": "Naming Series", "options": "LR-.YYYY.-.#####"},
                {"fieldname": "date", "fieldtype": "Date", "label": "Date", "default": "Today", "reqd": 1, "in_list_view": 1},
                {"fieldname": "payment_terms", "fieldtype": "Select", "label": "Payment Terms", "options": "To Pay\nPaid\nTBB", "in_list_view": 1},
                
                {"fieldname": "party_details_sec", "fieldtype": "Section Break", "label": "Party Details"},
                {"fieldname": "consignor", "fieldtype": "Data", "label": "Consignor", "reqd": 1},
                {"fieldname": "from_city", "fieldtype": "Data", "label": "From City", "reqd": 1},
                {"fieldname": "column_break_1", "fieldtype": "Column Break"},
                {"fieldname": "consignee", "fieldtype": "Data", "label": "Consignee", "reqd": 1},
                {"fieldname": "to_city", "fieldtype": "Data", "label": "To City", "reqd": 1},
                
                {"fieldname": "vehicle_details_sec", "fieldtype": "Section Break", "label": "Vehicle Details"},
                {"fieldname": "challan_number", "fieldtype": "Data", "label": "Challan Number", "in_list_view": 1},
                {"fieldname": "vehicle_number", "fieldtype": "Data", "label": "Vehicle Number"},
                {"fieldname": "column_break_2", "fieldtype": "Column Break"},
                {"fieldname": "driver_name", "fieldtype": "Data", "label": "Driver Name"},
                
                {"fieldname": "items_sec", "fieldtype": "Section Break", "label": "Items"},
                {"fieldname": "items", "fieldtype": "Table", "label": "Items", "options": "LR Item"},
                
                {"fieldname": "freight_details_sec", "fieldtype": "Section Break", "label": "Freight Details"},
                {"fieldname": "basic_freight", "fieldtype": "Currency", "label": "Basic Freight"},
                {"fieldname": "hamali_charges", "fieldtype": "Currency", "label": "Hamali / Loading"},
                {"fieldname": "column_break_3", "fieldtype": "Column Break"},
                {"fieldname": "bilty_charges", "fieldtype": "Currency", "label": "Bilty / Docket Charges"},
                {"fieldname": "total_amount", "fieldtype": "Currency", "label": "Total Amount", "read_only": 1, "in_list_view": 1}
            ]
        })
        doc.insert()
        frappe.db.commit()  # nosemgrep: required in standalone setup scripts
        print("Created Lorry Receipt DocType")
    else:
        print("Lorry Receipt already exists")
