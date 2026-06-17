import json

file_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/challan/challan.json"
with open(file_path, "r") as f:
    data = json.load(f)

for field in data["fields"]:
    if field["fieldname"] == "vehicle_number":
        field["fieldtype"] = "Link"
        field["options"] = "Hired Vehicle"
        break

with open(file_path, "w") as f:
    json.dump(data, f, indent=1)

print("challan.json updated")
