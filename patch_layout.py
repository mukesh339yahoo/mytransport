import json
import os

base_path = "apps/mytransport/mytransport/mytransport/doctype/expense_voucher/expense_voucher.json"

with open(base_path, "r") as f:
    doc = json.load(f)

# Ensure cb2 exists
has_cb2 = any(f["fieldname"] == "cb2" for f in doc["fields"])
if not has_cb2:
    doc["fields"].append({
        "fieldname": "cb2",
        "fieldtype": "Column Break"
    })

# Desired field order
desired_order = [
    "voucher_no",
    "vendor",
    "branch",
    "company",
    "cb1",
    "date",
    "voucher_type",
    "payment_account",
    "cheque_no",
    "cheque_date",
    "sb1",
    "expense_category",
    "expense_account",
    "cb2",
    "paid_to",
    "sb2",
    "remarks",
    "journal_entry",
    "amended_from",
    "get_unpaid_challans",
    "allocated_challans",
    "expense_details_section",
    "expense_details",
    "total_paid_amt",
    "amount_in_words",
    "on_account",
    "previous_payments_section",
    "previous_payments"
]

# Ensure all current fields are in desired_order
current_fields = [f["fieldname"] for f in doc["fields"]]
missing = [f for f in current_fields if f not in desired_order]
desired_order.extend(missing)

doc["field_order"] = desired_order

with open(base_path, "w") as f:
    json.dump(doc, f, indent=1)

print("Layout updated.")
