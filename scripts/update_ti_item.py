import json

file_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/transport_invoice_item/transport_invoice_item.json"
with open(file_path, "r") as f:
    data = json.load(f)

# Clear existing fields except lorry_receipt and date
# Wait, let's just rebuild the fields list to be perfectly clean and ordered
new_fields = [
    {"fieldname": "lr_number", "fieldtype": "Link", "label": "LR Number", "options": "Lorry Receipt", "in_list_view": 1, "reqd": 1},
    {"fieldname": "lr_date", "fieldtype": "Date", "label": "LR Date", "fetch_from": "lr_number.date", "read_only": 1, "in_list_view": 1},
    {"fieldname": "from_city", "fieldtype": "Data", "label": "From", "fetch_from": "lr_number.from_city", "read_only": 1, "in_list_view": 1},
    {"fieldname": "to_city", "fieldtype": "Data", "label": "To", "fetch_from": "lr_number.to_city", "read_only": 1, "in_list_view": 1},
    {"fieldname": "total_packages", "fieldtype": "Int", "label": "No of Pkgs", "fetch_from": "lr_number.total_packages", "read_only": 1, "in_list_view": 1},
    {"fieldname": "total_weight", "fieldtype": "Float", "label": "Weight", "fetch_from": "lr_number.total_weight", "read_only": 1, "in_list_view": 1},
    {"fieldname": "rate_per_mt", "fieldtype": "Select", "label": "Rate per MT", "options": "\nFix", "in_list_view": 1},
    {"fieldname": "basic_freight", "fieldtype": "Currency", "label": "Freight", "fetch_from": "lr_number.basic_freight", "read_only": 1},
    {"fieldname": "st_charge", "fieldtype": "Currency", "label": "St Charge", "fetch_from": "lr_number.bilty_charges", "read_only": 1},
    {"fieldname": "detention_narration", "fieldtype": "Small Text", "label": "Detention Narration", "fetch_from": "lr_number.detention_narration", "read_only": 1},
    {"fieldname": "detention_charges", "fieldtype": "Currency", "label": "Detention Amount", "fetch_from": "lr_number.detention_charges", "read_only": 1},
    {"fieldname": "hamali_narration", "fieldtype": "Small Text", "label": "Hamali Narration", "fetch_from": "lr_number.hamali_narration", "read_only": 1},
    {"fieldname": "hamali_charges", "fieldtype": "Currency", "label": "Hamali Amount", "fetch_from": "lr_number.hamali_charges", "read_only": 1},
    {"fieldname": "other_charge_narration", "fieldtype": "Small Text", "label": "Other Charge Narration", "fetch_from": "lr_number.other_charge_narration", "read_only": 1},
    {"fieldname": "other_charges", "fieldtype": "Currency", "label": "Other Charge Amount", "fetch_from": "lr_number.other_charges", "read_only": 1}
]

data["fields"] = new_fields
data["field_order"] = [f["fieldname"] for f in new_fields]

with open(file_path, "w") as f:
    json.dump(data, f, indent=1)

print("transport_invoice_item.json updated")
