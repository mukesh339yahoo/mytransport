import json
import os

base_path = "apps/mytransport/mytransport/mytransport/doctype"

# 1. Create Previous Challan Payment doctype JSON
prev_pay_dir = os.path.join(base_path, "previous_challan_payment")
os.makedirs(prev_pay_dir, exist_ok=True)

prev_pay_json = {
    "actions": [],
    "allow_rename": 1,
    "creation": "2026-06-29 12:00:00.000000",
    "doctype": "DocType",
    "editable_grid": 1,
    "engine": "InnoDB",
    "field_order": [
        "challan_no",
        "voucher_no",
        "voucher_date",
        "amount",
        "vendor"
    ],
    "fields": [
        {
            "fieldname": "challan_no",
            "fieldtype": "Data",
            "in_list_view": 1,
            "label": "Challan No",
            "read_only": 1
        },
        {
            "fieldname": "voucher_no",
            "fieldtype": "Data",
            "in_list_view": 1,
            "label": "Voucher No",
            "read_only": 1
        },
        {
            "fieldname": "voucher_date",
            "fieldtype": "Date",
            "in_list_view": 1,
            "label": "Voucher Date",
            "read_only": 1
        },
        {
            "fieldname": "amount",
            "fieldtype": "Currency",
            "in_list_view": 1,
            "label": "Amount",
            "read_only": 1
        },
        {
            "fieldname": "vendor",
            "fieldtype": "Link",
            "in_list_view": 1,
            "label": "Vendor",
            "options": "Supplier",
            "read_only": 1
        }
    ],
    "index_web_pages_for_search": 1,
    "istable": 1,
    "links": [],
    "modified": "2026-06-29 12:00:00.000000",
    "modified_by": "Administrator",
    "module": "Mytransport",
    "name": "Previous Challan Payment",
    "owner": "Administrator",
    "permissions": [],
    "sort_field": "creation",
    "sort_order": "DESC",
    "states": []
}

with open(os.path.join(prev_pay_dir, "previous_challan_payment.json"), "w") as f:
    json.dump(prev_pay_json, f, indent=1)

with open(os.path.join(prev_pay_dir, "previous_challan_payment.py"), "w") as f:
    f.write("import frappe\nfrom frappe.model.document import Document\n\nclass PreviousChallanPayment(Document):\n\tpass\n")

with open(os.path.join(prev_pay_dir, "__init__.py"), "w") as f:
    f.write("")

# 2. Update Expense Voucher JSON
ev_path = os.path.join(base_path, "expense_voucher", "expense_voucher.json")
with open(ev_path, "r") as f:
    ev_data = json.load(f)

has_previous_payments = any(field.get("fieldname") == "previous_payments" for field in ev_data.get("fields", []))

if not has_previous_payments:
    new_fields = [
        {
            "fieldname": "previous_payments_section",
            "fieldtype": "Section Break",
            "label": "Previous Challan Payments"
        },
        {
            "fieldname": "previous_payments",
            "fieldtype": "Table",
            "label": "Previous Challan Payments",
            "options": "Previous Challan Payment",
            "read_only": 1
        }
    ]
    
    # Insert at the end
    ev_data["fields"].extend(new_fields)
    ev_data["field_order"].extend(["previous_payments_section", "previous_payments"])
    
    with open(ev_path, "w") as f:
        json.dump(ev_data, f, indent=1)
    print("Updated Expense Voucher JSON")
else:
    print("Expense Voucher already has previous payments details")

