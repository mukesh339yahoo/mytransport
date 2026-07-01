import json
import os

base_path = "apps/mytransport/mytransport/mytransport/doctype"

# Money Receipt
mr_path = os.path.join(base_path, "money_receipt", "money_receipt.json")
with open(mr_path, "r") as f:
    mr_doc = json.load(f)
for field in mr_doc.get("fields", []):
    if field.get("fieldname") == "mr_no":
        field["unique"] = 1
        print("Set mr_no to unique in Money Receipt")
with open(mr_path, "w") as f:
    json.dump(mr_doc, f, indent=1)

# Expense Voucher
ev_path = os.path.join(base_path, "expense_voucher", "expense_voucher.json")
with open(ev_path, "r") as f:
    ev_doc = json.load(f)
for field in ev_doc.get("fields", []):
    if field.get("fieldname") == "voucher_no":
        field["unique"] = 1
        print("Set voucher_no to unique in Expense Voucher")
with open(ev_path, "w") as f:
    json.dump(ev_doc, f, indent=1)

