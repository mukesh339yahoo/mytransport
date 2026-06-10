import frappe

def run():
    # 1. Create Child Table Doctype: Transport Invoice Item
    if not frappe.db.exists("DocType", "Transport Invoice Item"):
        doc_item = frappe.get_doc({
            "doctype": "DocType",
            "module": "Mytransport",
            "custom": 0,
            "istable": 1,
            "name": "Transport Invoice Item",
            "editable_grid": 1,
            "fields": [
                {
                    "fieldname": "lorry_receipt",
                    "label": "Lorry Receipt",
                    "fieldtype": "Link",
                    "options": "Lorry Receipt",
                    "in_list_view": 1,
                    "reqd": 1
                },
                {
                    "fieldname": "date",
                    "label": "Date",
                    "fieldtype": "Date",
                    "fetch_from": "lorry_receipt.date",
                    "in_list_view": 1,
                    "read_only": 1
                },
                {
                    "fieldname": "from_city",
                    "label": "From City",
                    "fieldtype": "Data",
                    "fetch_from": "lorry_receipt.from_city",
                    "read_only": 1
                },
                {
                    "fieldname": "to_city",
                    "label": "To City",
                    "fieldtype": "Data",
                    "fetch_from": "lorry_receipt.to_city",
                    "read_only": 1
                },
                {
                    "fieldname": "vehicle_number",
                    "label": "Vehicle Number",
                    "fieldtype": "Data",
                    "fetch_from": "lorry_receipt.vehicle_number",
                    "read_only": 1
                },
                {
                    "fieldname": "amount",
                    "label": "Amount",
                    "fieldtype": "Currency",
                    "fetch_from": "lorry_receipt.total_amount",
                    "in_list_view": 1,
                    "read_only": 1
                }
            ]
        })
        doc_item.insert()
        print("Transport Invoice Item Doctype created.")
    else:
        print("Transport Invoice Item Doctype already exists.")

    # 2. Create Main Doctype: Transport Invoice
    if not frappe.db.exists("DocType", "Transport Invoice"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "Mytransport",
            "custom": 0,
            "name": "Transport Invoice",
            "naming_rule": "Expression",
            "autoname": "INV-.YYYY.-.#####",
            "is_submittable": 1,
            "title_field": "customer",
            "search_fields": "customer, status",
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1, "write": 1, "create": 1, "delete": 1,
                    "submit": 1, "cancel": 1, "amend": 1
                }
            ],
            "fields": [
                {
                    "fieldname": "customer",
                    "label": "Customer",
                    "fieldtype": "Link",
                    "options": "Customer",
                    "reqd": 1,
                    "in_list_view": 1
                },
                {
                    "fieldname": "date",
                    "label": "Date",
                    "fieldtype": "Date",
                    "default": "Today",
                    "reqd": 1,
                    "in_list_view": 1
                },
                {
                    "fieldname": "due_date",
                    "label": "Due Date",
                    "fieldtype": "Date"
                },
                {
                    "fieldname": "column_break_1",
                    "fieldtype": "Column Break"
                },
                {
                    "fieldname": "status",
                    "label": "Status",
                    "fieldtype": "Select",
                    "options": "Draft\nUnpaid\nPartially Paid\nPaid\nCancelled",
                    "default": "Draft",
                    "in_list_view": 1,
                    "read_only": 1
                },
                {
                    "fieldname": "branch",
                    "label": "Branch",
                    "fieldtype": "Link",
                    "options": "Branch"
                },
                {
                    "fieldname": "amended_from",
                    "label": "Amended From",
                    "fieldtype": "Link",
                    "options": "Transport Invoice",
                    "read_only": 1,
                    "no_copy": 1,
                    "print_hide": 1
                },
                {
                    "fieldname": "items_section",
                    "fieldtype": "Section Break",
                    "label": "Lorry Receipts"
                },
                {
                    "fieldname": "get_unbilled_lrs",
                    "label": "Get Unbilled LRs",
                    "fieldtype": "Button"
                },
                {
                    "fieldname": "items",
                    "label": "Lorry Receipts",
                    "fieldtype": "Table",
                    "options": "Transport Invoice Item"
                },
                {
                    "fieldname": "totals_section",
                    "fieldtype": "Section Break",
                    "label": "Totals"
                },
                {
                    "fieldname": "total_amount",
                    "label": "Total Amount",
                    "fieldtype": "Currency",
                    "read_only": 1,
                    "in_list_view": 1
                },
                {
                    "fieldname": "column_break_2",
                    "fieldtype": "Column Break"
                },
                {
                    "fieldname": "paid_amount",
                    "label": "Amount Paid",
                    "fieldtype": "Currency",
                    "default": "0"
                },
                {
                    "fieldname": "outstanding_amount",
                    "label": "Outstanding Amount",
                    "fieldtype": "Currency",
                    "read_only": 1
                },
                {
                    "fieldname": "terms_section",
                    "fieldtype": "Section Break",
                    "label": "Terms & Remarks"
                },
                {
                    "fieldname": "remarks",
                    "label": "Remarks",
                    "fieldtype": "Small Text"
                },
                {
                    "fieldname": "terms_and_conditions",
                    "label": "Terms and Conditions",
                    "fieldtype": "Text Editor"
                }
            ]
        })
        doc.insert()
        frappe.db.commit()
        print("Transport Invoice Doctype created.")
    else:
        print("Transport Invoice Doctype already exists.")

