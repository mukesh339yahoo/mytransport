import json

file_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/challan/challan.json"
with open(file_path, "r") as f:
    data = json.load(f)

data["allow_attachments"] = 1

new_fields = [
    {"fieldname": "truck_freight_sec", "fieldtype": "Section Break", "label": "Truck Freight"},
    {"fieldname": "total_lrs", "fieldtype": "Int", "label": "Total LRs", "read_only": 1},
    {"fieldname": "basic_freight", "fieldtype": "Currency", "label": "Basic Freight", "read_only": 1},
    {"fieldname": "hamali_charges", "fieldtype": "Currency", "label": "Hamali Charges", "read_only": 1},
    {"fieldname": "detention_charges", "fieldtype": "Currency", "label": "Detention Charges", "read_only": 1},
    {"fieldname": "column_break_tf_1", "fieldtype": "Column Break"},
    {"fieldname": "rto_charges", "fieldtype": "Currency", "label": "RTO Charges", "read_only": 1},
    {"fieldname": "other_charges", "fieldtype": "Currency", "label": "Other Charges", "read_only": 1},
    {"fieldname": "total_amount", "fieldtype": "Currency", "label": "Total Amount", "read_only": 1},
    {"fieldname": "column_break_tf_2", "fieldtype": "Column Break"},
    {"fieldname": "total_weight", "fieldtype": "Float", "label": "Total Weight", "read_only": 1},
    {"fieldname": "total_packages", "fieldtype": "Int", "label": "Total Packages", "read_only": 1},
    
    {"fieldname": "advance_details_sec", "fieldtype": "Section Break", "label": "Advance Details"},
    {"fieldname": "pan_no", "fieldtype": "Data", "label": "PAN No"},
    {"fieldname": "name_field", "fieldtype": "Data", "label": "Name"},
    {"fieldname": "cheque_no", "fieldtype": "Data", "label": "Cheque No"},
    {"fieldname": "bank", "fieldtype": "Data", "label": "Bank"},
    {"fieldname": "cheque_date", "fieldtype": "Date", "label": "Cheque Date"},
    {"fieldname": "column_break_ad_1", "fieldtype": "Column Break"},
    {"fieldname": "cheque_amount", "fieldtype": "Currency", "label": "Cheque Amount"},
    {"fieldname": "voucher_no", "fieldtype": "Data", "label": "Voucher No"},
    {"fieldname": "cash_amount", "fieldtype": "Currency", "label": "Cash Amount"},
    {"fieldname": "utr_rtgs_no", "fieldtype": "Data", "label": "UTR/RTGS No"},
    {"fieldname": "e_pay_amount", "fieldtype": "Currency", "label": "E-Pay Amount"},
    {"fieldname": "column_break_ad_2", "fieldtype": "Column Break"},
    {"fieldname": "remarks", "fieldtype": "Small Text", "label": "Remarks"},

    {"fieldname": "tds_details_sec", "fieldtype": "Section Break", "label": "TDS Details"},
    {"fieldname": "tds_declaration", "fieldtype": "Check", "label": "TDS Declaration"},
    {"fieldname": "tds_challan", "fieldtype": "Data", "label": "TDS Challan", "read_only": 1},
    {"fieldname": "column_break_tds_1", "fieldtype": "Column Break"},
    {"fieldname": "tds_percent", "fieldtype": "Float", "label": "TDS %", "default": "1"},
    {"fieldname": "total_tds", "fieldtype": "Currency", "label": "Total TDS", "read_only": 1},
    {"fieldname": "column_break_tds_2", "fieldtype": "Column Break"},
    {"fieldname": "tds_payable_by", "fieldtype": "Select", "label": "TDS Payable By", "options": "Owner\nBroker\nCompany"}
]

existing_fields = [f["fieldname"] for f in data["fields"]]
for nf in new_fields:
    if nf["fieldname"] not in existing_fields:
        data["fields"].append(nf)

# Field order strategy: insert after lrs
fo = data["field_order"]
if "lrs" in fo:
    idx = fo.index("lrs")
    
    # insert truck freight
    tf_fields = ["truck_freight_sec", "total_lrs", "basic_freight", "hamali_charges", "detention_charges", "column_break_tf_1", "rto_charges", "other_charges", "total_amount", "column_break_tf_2", "total_weight", "total_packages"]
    
    # insert advance
    ad_fields = ["advance_details_sec", "pan_no", "name_field", "cheque_no", "bank", "cheque_date", "column_break_ad_1", "cheque_amount", "voucher_no", "cash_amount", "utr_rtgs_no", "e_pay_amount", "column_break_ad_2", "remarks"]
    
    # insert tds
    tds_fields = ["tds_details_sec", "tds_declaration", "tds_challan", "column_break_tds_1", "tds_percent", "total_tds", "column_break_tds_2", "tds_payable_by"]

    for i, f in enumerate(tf_fields + ad_fields + tds_fields):
        if f not in fo:
            fo.insert(idx + 1 + i, f)
        else:
            fo.remove(f)
            fo.insert(idx + 1 + i, f)

with open(file_path, "w") as f:
    json.dump(data, f, indent=1)

print("Challan updated")
