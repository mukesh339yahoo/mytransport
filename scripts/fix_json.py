import json
import os

file_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/expense_voucher/expense_voucher.json"

with open(file_path, 'r') as f:
    data = json.load(f)

# Move in field_order
if "voucher_no" in data.get("field_order", []):
    data["field_order"].remove("voucher_no")
    data["field_order"].insert(0, "voucher_no")

# Move in fields list
voucher_field = None
for f in data.get("fields", []):
    if f.get("fieldname") == "voucher_no":
        voucher_field = f
        break

if voucher_field:
    data["fields"].remove(voucher_field)
    data["fields"].insert(0, voucher_field)

with open(file_path, 'w') as f:
    json.dump(data, f, indent=1)

print("Modified expense_voucher.json")
