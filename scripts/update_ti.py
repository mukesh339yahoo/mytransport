import json

file_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/transport_invoice/transport_invoice.json"
with open(file_path, "r") as f:
    data = json.load(f)

# Fields to add
new_fields = [
    {"fieldname": "category", "fieldtype": "Select", "label": "Category", "options": "Freight\nOther"},
    {"fieldname": "bill_no", "fieldtype": "Data", "label": "Bill No"},
    {"fieldname": "customer_address", "fieldtype": "Small Text", "label": "Customer Address"},
    {"fieldname": "customer_gst_no", "fieldtype": "Data", "label": "Customer GST Number"},
    {"fieldname": "customer_reference", "fieldtype": "Data", "label": "Customer Reference"},
    
    # Totals
    {"fieldname": "total_freight", "fieldtype": "Currency", "label": "Total Freight", "read_only": 1},
    {"fieldname": "total_st_charge", "fieldtype": "Currency", "label": "Total St Charge", "read_only": 1},
    {"fieldname": "total_detention_charge", "fieldtype": "Currency", "label": "Total Detention Charge", "read_only": 1},
    {"fieldname": "column_break_totals_2", "fieldtype": "Column Break"},
    {"fieldname": "total_hamali_charge", "fieldtype": "Currency", "label": "Total Hamali Charge", "read_only": 1},
    {"fieldname": "total_other_charges", "fieldtype": "Currency", "label": "Total Other Charges", "read_only": 1}
]

existing_fields = [f["fieldname"] for f in data["fields"]]
for nf in new_fields:
    if nf["fieldname"] not in existing_fields:
        data["fields"].append(nf)

# Remove terms and conditions
data["fields"] = [f for f in data["fields"] if f["fieldname"] != "terms_and_conditions"]

# Organize field order
fo = data["field_order"]

# Insert new fields near top
if "date" in fo:
    idx = fo.index("date")
    # Add bill no, category, customer ref
    for f in ["bill_no", "category", "customer_reference"]:
        if f not in fo:
            fo.insert(idx, f)
        else:
            fo.remove(f)
            fo.insert(idx, f)

if "customer" in fo:
    idx = fo.index("customer")
    for f in ["customer_address", "customer_gst_no"]:
        if f not in fo:
            fo.insert(idx + 1, f)
        else:
            fo.remove(f)
            fo.insert(idx + 1, f)

if "terms_and_conditions" in fo:
    fo.remove("terms_and_conditions")

if "totals_section" in fo:
    idx = fo.index("totals_section")
    for i, f in enumerate(["total_freight", "total_st_charge", "total_detention_charge", "column_break_totals_2", "total_hamali_charge", "total_other_charges"]):
        if f not in fo:
            fo.insert(idx + 1 + i, f)
        else:
            fo.remove(f)
            fo.insert(idx + 1 + i, f)

with open(file_path, "w") as f:
    json.dump(data, f, indent=1)

print("transport_invoice.json updated")
