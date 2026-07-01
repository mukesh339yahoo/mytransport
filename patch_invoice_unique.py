import json
import os

base_path = "apps/mytransport/mytransport/mytransport/doctype"

invoice_path = os.path.join(base_path, "transport_invoice", "transport_invoice.json")
with open(invoice_path, "r") as f:
    doc = json.load(f)

for field in doc.get("fields", []):
    if field.get("fieldname") == "bill_no":
        field["unique"] = 1
        print("Set bill_no to unique in Transport Invoice")

with open(invoice_path, "w") as f:
    json.dump(doc, f, indent=1)

