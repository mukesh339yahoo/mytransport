import json
import os

base_path = "apps/mytransport/mytransport/mytransport/doctype"

# Challan
challan_path = os.path.join(base_path, "challan", "challan.json")
with open(challan_path, "r") as f:
    doc = json.load(f)
for field in doc.get("fields", []):
    if field.get("fieldname") == "challan_number":
        field["unique"] = 1
        print("Set challan_number to unique in Challan")
with open(challan_path, "w") as f:
    json.dump(doc, f, indent=1)

# Lorry Receipt
lr_path = os.path.join(base_path, "lorry_receipt", "lorry_receipt.json")
with open(lr_path, "r") as f:
    doc = json.load(f)
for field in doc.get("fields", []):
    if field.get("fieldname") == "lr_number":
        field["unique"] = 1
        print("Set lr_number to unique in Lorry Receipt")
with open(lr_path, "w") as f:
    json.dump(doc, f, indent=1)

