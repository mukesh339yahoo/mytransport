import json
import os

base_path = "apps/mytransport/mytransport/mytransport/doctype"

for dt in ["expense_voucher", "money_receipt"]:
    path = os.path.join(base_path, dt, f"{dt}.json")
    with open(path, "r") as f:
        doc = json.load(f)
        
    print(f"{dt}: autoname={doc.get('autoname')}, naming_rule={doc.get('naming_rule')}")
