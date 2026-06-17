import json

file_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/lr_item/lr_item.json"
with open(file_path, "r") as f:
    data = json.load(f)

# Remove rate and amount
data["fields"] = [f for f in data["fields"] if f["fieldname"] not in ("rate", "amount")]

# Update Item Description
for f in data["fields"]:
    if f["fieldname"] == "item_description":
        f["fieldtype"] = "Select"
        f["options"] = "Oil\nPlastic Dana\nGenerator"

# Add new fields if not exist
existing_fields = [f["fieldname"] for f in data["fields"]]

new_fields = []
if "packaging_type" not in existing_fields:
    new_fields.append({
        "fieldname": "packaging_type",
        "fieldtype": "Select",
        "label": "Packaging Type",
        "options": "Loose\nCarton\nPallet\nDrum",
        "in_list_view": 1
    })

if "load_type" not in existing_fields:
    new_fields.append({
        "fieldname": "load_type",
        "fieldtype": "Select",
        "label": "Load Type",
        "options": "9MT\n16 MT\n21 MT\n32 MT",
        "in_list_view": 1
    })

if "lorry_freight" not in existing_fields:
    new_fields.append({
        "fieldname": "lorry_freight",
        "fieldtype": "Currency",
        "label": "Lorry Freight",
        "in_list_view": 1
    })

# Make charged_weight visible in list view if it isn't
for f in data["fields"]:
    if f["fieldname"] == "charged_weight":
        f["in_list_view"] = 1

data["fields"].extend(new_fields)

# Update field_order
data["field_order"] = [
    "item_description",
    "packaging_type",
    "load_type",
    "qty",
    "actual_weight",
    "charged_weight",
    "lorry_freight"
]

with open(file_path, "w") as f:
    json.dump(data, f, indent=1)

print("Schema updated successfully")
