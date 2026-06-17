import json

file_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/challan/challan.json"
with open(file_path, "r") as f:
    data = json.load(f)

new_field = {"fieldname": "update_vehicle_tds", "fieldtype": "Check", "label": "Update Vehicle TDS", "hidden": 1}

existing_fields = [f["fieldname"] for f in data["fields"]]
if "update_vehicle_tds" not in existing_fields:
    data["fields"].append(new_field)
    data["field_order"].append("update_vehicle_tds")

with open(file_path, "w") as f:
    json.dump(data, f, indent=1)

print("challan.json updated")
