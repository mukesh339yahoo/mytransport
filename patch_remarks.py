import json
import os

base_path = "apps/mytransport/mytransport/mytransport/doctype/expense_voucher/expense_voucher.json"

with open(base_path, "r") as f:
    doc = json.load(f)

if "remarks" in doc["field_order"]:
    doc["field_order"].remove("remarks")
    doc["field_order"].append("remarks")

with open(base_path, "w") as f:
    json.dump(doc, f, indent=1)

print("Remarks moved to bottom.")
