import json
import os

base_path = "apps/mytransport/mytransport/mytransport/doctype"

# Money Receipt
mr_path = os.path.join(base_path, "money_receipt", "money_receipt.json")
with open(mr_path, "r") as f:
    mr_doc = json.load(f)
for field in mr_doc.get("fields", []):
    if field.get("fieldname") in ["cheque_no", "cheque_date"]:
        field["depends_on"] = "eval:in_list(['Bank', 'Cheque', 'UPI'], doc.payment_mode)"
        print(f"Updated depends_on for {field['fieldname']} in MR")
with open(mr_path, "w") as f:
    json.dump(mr_doc, f, indent=1)

