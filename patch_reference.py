import json
import os

base_path = "apps/mytransport/mytransport/mytransport/doctype"

# Expense Voucher
ev_path = os.path.join(base_path, "expense_voucher", "expense_voucher.json")
with open(ev_path, "r") as f:
    ev_doc = json.load(f)
for field in ev_doc.get("fields", []):
    if field.get("fieldname") == "voucher_type":
        field["label"] = "Payment Mode"
        field["options"] = "Cash\nBank\nCheque\nUPI"
        print("Updated Payment Mode in EV")
    if field.get("fieldname") == "cheque_no":
        field["label"] = "Reference No"
        field["depends_on"] = "eval:in_list(['Bank', 'Cheque', 'UPI'], doc.voucher_type)"
        print("Updated Reference No in EV")
    if field.get("fieldname") == "cheque_date":
        field["label"] = "Reference Date"
        field["depends_on"] = "eval:in_list(['Bank', 'Cheque', 'UPI'], doc.voucher_type)"
        print("Updated Reference Date in EV")
with open(ev_path, "w") as f:
    json.dump(ev_doc, f, indent=1)

# Money Receipt
mr_path = os.path.join(base_path, "money_receipt", "money_receipt.json")
with open(mr_path, "r") as f:
    mr_doc = json.load(f)
for field in mr_doc.get("fields", []):
    if field.get("fieldname") == "cheque_no":
        field["label"] = "Reference No"
        print("Updated Reference No in MR")
    if field.get("fieldname") == "cheque_date":
        field["label"] = "Reference Date"
        print("Updated Reference Date in MR")
with open(mr_path, "w") as f:
    json.dump(mr_doc, f, indent=1)

