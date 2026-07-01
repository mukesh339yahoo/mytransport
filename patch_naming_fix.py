import json
import os

base_path = "apps/mytransport/mytransport/mytransport/doctype"

for dt in ["expense_voucher", "money_receipt"]:
    path = os.path.join(base_path, dt, f"{dt}.json")
    with open(path, "r") as f:
        doc = json.load(f)
        
    old_autoname = doc.get("autoname")
    if old_autoname and ".YYYY." in old_autoname:
        new_autoname = old_autoname.replace(".YYYY.", "{YYYY}").replace(".#####", "{#####}")
        doc["autoname"] = new_autoname
        doc["naming_rule"] = "Expression"
        with open(path, "w") as f:
            json.dump(doc, f, indent=1)
        print(f"Updated {dt}: {new_autoname}")

