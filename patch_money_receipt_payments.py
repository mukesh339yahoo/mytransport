import json
import os

base_path = "apps/mytransport/mytransport/mytransport/doctype"

# 1. Create Previous Invoice Payment doctype JSON
prev_pay_dir = os.path.join(base_path, "previous_invoice_payment")
os.makedirs(prev_pay_dir, exist_ok=True)

prev_pay_json = {
    "actions": [],
    "allow_rename": 1,
    "creation": "2026-07-01 12:00:00.000000",
    "doctype": "DocType",
    "editable_grid": 1,
    "engine": "InnoDB",
    "field_order": [
        "mr_no",
        "bill_no",
        "cheque_no",
        "paid_amt",
        "deduct_amt",
        "tds_amt"
    ],
    "fields": [
        {
            "fieldname": "mr_no",
            "fieldtype": "Data",
            "in_list_view": 1,
            "label": "MR No",
            "read_only": 1
        },
        {
            "fieldname": "bill_no",
            "fieldtype": "Data",
            "in_list_view": 1,
            "label": "Bill No",
            "read_only": 1
        },
        {
            "fieldname": "cheque_no",
            "fieldtype": "Data",
            "in_list_view": 1,
            "label": "Cheque No",
            "read_only": 1
        },
        {
            "fieldname": "paid_amt",
            "fieldtype": "Currency",
            "in_list_view": 1,
            "label": "Paid Amt",
            "read_only": 1
        },
        {
            "fieldname": "deduct_amt",
            "fieldtype": "Currency",
            "in_list_view": 1,
            "label": "Deduct Amt",
            "read_only": 1
        },
        {
            "fieldname": "tds_amt",
            "fieldtype": "Currency",
            "in_list_view": 1,
            "label": "TDS Amt",
            "read_only": 1
        }
    ],
    "index_web_pages_for_search": 1,
    "istable": 1,
    "links": [],
    "modified": "2026-07-01 12:00:00.000000",
    "modified_by": "Administrator",
    "module": "Mytransport",
    "name": "Previous Invoice Payment",
    "owner": "Administrator",
    "permissions": [],
    "sort_field": "creation",
    "sort_order": "DESC",
    "states": []
}

with open(os.path.join(prev_pay_dir, "previous_invoice_payment.json"), "w") as f:
    json.dump(prev_pay_json, f, indent=1)

with open(os.path.join(prev_pay_dir, "previous_invoice_payment.py"), "w") as f:
    f.write("import frappe\nfrom frappe.model.document import Document\n\nclass PreviousInvoicePayment(Document):\n\tpass\n")

with open(os.path.join(prev_pay_dir, "__init__.py"), "w") as f:
    f.write("")

# 2. Update Money Receipt JSON
mr_path = os.path.join(base_path, "money_receipt", "money_receipt.json")
with open(mr_path, "r") as f:
    mr_data = json.load(f)

has_previous_payments = any(field.get("fieldname") == "previous_payments" for field in mr_data.get("fields", []))

if not has_previous_payments:
    new_fields = [
        {
            "fieldname": "previous_payments_section",
            "fieldtype": "Section Break",
            "label": "Previous Payments for Transport Invoices"
        },
        {
            "fieldname": "previous_payments",
            "fieldtype": "Table",
            "label": "Previous Payments for Transport Invoices",
            "options": "Previous Invoice Payment",
            "read_only": 1
        }
    ]
    
    mr_data["fields"].extend(new_fields)
    mr_data["field_order"].extend(["previous_payments_section", "previous_payments"])
    
    with open(mr_path, "w") as f:
        json.dump(mr_data, f, indent=1)
    print("Updated Money Receipt JSON")
else:
    print("Money Receipt already has previous payments details")

