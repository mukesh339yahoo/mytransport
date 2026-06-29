import json
import os

base_path = "apps/mytransport/mytransport/mytransport/doctype"

# 1. Create Expense Detail doctype JSON
expense_detail_dir = os.path.join(base_path, "expense_detail")
os.makedirs(expense_detail_dir, exist_ok=True)

expense_detail_json = {
    "actions": [],
    "allow_rename": 1,
    "creation": "2026-06-28 12:00:00.000000",
    "doctype": "DocType",
    "editable_grid": 1,
    "engine": "InnoDB",
    "field_order": [
        "expense_item",
        "expense_amount",
        "challan_ref"
    ],
    "fields": [
        {
            "fieldname": "expense_item",
            "fieldtype": "Select",
            "in_list_view": 1,
            "label": "Expense Item",
            "options": "Detention Charge\nHamali Charge\nAdvance\nBalance\nMiscellaneous",
            "reqd": 1
        },
        {
            "fieldname": "expense_amount",
            "fieldtype": "Currency",
            "in_list_view": 1,
            "label": "Expense Amount",
            "reqd": 1
        },
        {
            "fieldname": "challan_ref",
            "fieldtype": "Link",
            "in_list_view": 1,
            "label": "Challan Ref No",
            "options": "Challan"
        }
    ],
    "index_web_pages_for_search": 1,
    "istable": 1,
    "links": [],
    "modified": "2026-06-28 12:00:00.000000",
    "modified_by": "Administrator",
    "module": "Mytransport",
    "name": "Expense Detail",
    "owner": "Administrator",
    "permissions": [],
    "sort_field": "creation",
    "sort_order": "DESC",
    "states": []
}

with open(os.path.join(expense_detail_dir, "expense_detail.json"), "w") as f:
    json.dump(expense_detail_json, f, indent=1)

with open(os.path.join(expense_detail_dir, "expense_detail.py"), "w") as f:
    f.write("import frappe\nfrom frappe.model.document import Document\n\nclass ExpenseDetail(Document):\n\tpass\n")

with open(os.path.join(expense_detail_dir, "__init__.py"), "w") as f:
    f.write("")

# 2. Update Expense Voucher JSON
ev_path = os.path.join(base_path, "expense_voucher", "expense_voucher.json")
with open(ev_path, "r") as f:
    ev_data = json.load(f)

has_expense_details = any(field.get("fieldname") == "expense_details" for field in ev_data.get("fields", []))

if not has_expense_details:
    new_fields = [
        {
            "fieldname": "expense_details_section",
            "fieldtype": "Section Break",
            "label": "Expense Details"
        },
        {
            "fieldname": "expense_details",
            "fieldtype": "Table",
            "label": "Expense Details",
            "options": "Expense Detail"
        }
    ]
    
    # Insert right after allocated_challans
    insert_idx = len(ev_data["fields"])
    for i, field in enumerate(ev_data["fields"]):
        if field.get("fieldname") == "allocated_challans":
            insert_idx = i + 1
            break
            
    ev_data["fields"].insert(insert_idx, new_fields[0])
    ev_data["fields"].insert(insert_idx + 1, new_fields[1])
    
    # Update field_order
    field_order_idx = len(ev_data["field_order"])
    for i, field in enumerate(ev_data["field_order"]):
        if field == "allocated_challans":
            field_order_idx = i + 1
            break
            
    ev_data["field_order"].insert(field_order_idx, "expense_details_section")
    ev_data["field_order"].insert(field_order_idx + 1, "expense_details")
    
    with open(ev_path, "w") as f:
        json.dump(ev_data, f, indent=1)
    print("Updated Expense Voucher JSON")
else:
    print("Expense Voucher already has expense details")

