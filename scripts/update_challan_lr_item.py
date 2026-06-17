import json

file_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/challan_lr_item/challan_lr_item.json"
with open(file_path, "r") as f:
    data = json.load(f)

# Remove Consignor/Consignee
data["fields"] = [f for f in data["fields"] if f["fieldname"] not in ("consignor", "consignee")]

# Add new fields
new_fields = [
    {"fieldname": "lr_date", "fieldtype": "Date", "label": "LR Date", "fetch_from": "lr_number.date", "read_only": 1, "in_list_view": 1},
    {"fieldname": "total_packages", "fieldtype": "Int", "label": "Total Packages", "fetch_from": "lr_number.total_packages", "read_only": 1, "in_list_view": 1},
    {"fieldname": "total_weight", "fieldtype": "Float", "label": "Total Weight", "fetch_from": "lr_number.total_weight", "read_only": 1, "in_list_view": 1},
    {"fieldname": "basic_freight", "fieldtype": "Currency", "label": "Basic Freight", "fetch_from": "lr_number.basic_freight", "read_only": 1},
    {"fieldname": "hamali_charges", "fieldtype": "Currency", "label": "Hamali Charges", "fetch_from": "lr_number.hamali_charges", "read_only": 1},
    {"fieldname": "detention_charges", "fieldtype": "Currency", "label": "Detention Charges", "fetch_from": "lr_number.detention_charges", "read_only": 1},
    {"fieldname": "rto_charges", "fieldtype": "Currency", "label": "RTO Charges", "fetch_from": "lr_number.rto_charges", "read_only": 1},
    {"fieldname": "other_charges", "fieldtype": "Currency", "label": "Other Charges", "fetch_from": "lr_number.other_charges", "read_only": 1},
    {"fieldname": "vehicle_number", "fieldtype": "Data", "label": "Vehicle Number", "fetch_from": "lr_number.vehicle_number", "read_only": 1, "in_list_view": 1}
]

existing_fields = [f["fieldname"] for f in data["fields"]]
for nf in new_fields:
    if nf["fieldname"] not in existing_fields:
        data["fields"].append(nf)

# Reorder
data["field_order"] = [
    "lr_number",
    "lr_date",
    "from_city",
    "to_city",
    "total_packages",
    "total_weight",
    "basic_freight",
    "hamali_charges",
    "detention_charges",
    "rto_charges",
    "other_charges",
    "total_amount",
    "vehicle_number"
]

with open(file_path, "w") as f:
    json.dump(data, f, indent=1)

print("Challan LR Item updated")
