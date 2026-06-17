import json

file_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/lorry_receipt/lorry_receipt.json"
with open(file_path, "r") as f:
    data = json.load(f)

new_fields = [
    {"fieldname": "detention_narration", "fieldtype": "Small Text", "label": "Detention Narration", "allow_on_submit": 1},
    {"fieldname": "hamali_narration", "fieldtype": "Small Text", "label": "Hamali Narration", "allow_on_submit": 1},
    {"fieldname": "other_charge_narration", "fieldtype": "Small Text", "label": "Other Charge Narration", "allow_on_submit": 1}
]

existing_fields = [f["fieldname"] for f in data["fields"]]
for nf in new_fields:
    if nf["fieldname"] not in existing_fields:
        data["fields"].append(nf)

# Insert them near their respective charge fields
fo = data["field_order"]
if "detention_charges" in fo and "detention_narration" not in fo:
    fo.insert(fo.index("detention_charges") + 1, "detention_narration")
if "hamali_charges" in fo and "hamali_narration" not in fo:
    fo.insert(fo.index("hamali_charges") + 1, "hamali_narration")
if "other_charges" in fo and "other_charge_narration" not in fo:
    fo.insert(fo.index("other_charges") + 1, "other_charge_narration")

with open(file_path, "w") as f:
    json.dump(data, f, indent=1)

print("lorry_receipt.json updated")
