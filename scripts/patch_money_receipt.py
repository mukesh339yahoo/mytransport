import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def run():
    # 1. Create Child Table DocType 'Allocated Transport Invoice'
    if not frappe.db.exists("DocType", "Allocated Transport Invoice"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Allocated Transport Invoice",
            "module": "Mytransport",
            "custom": 0,
            "istable": 1,
            "editable_grid": 1,
            "fields": [
                {"fieldname": "bill_no", "fieldtype": "Link", "options": "Transport Invoice", "label": "Bill No", "in_list_view": 1, "reqd": 1},
                {"fieldname": "bill_date", "fieldtype": "Date", "label": "Bill Date", "in_list_view": 1, "fetch_from": "bill_no.date", "read_only": 1},
                {"fieldname": "total_amt", "fieldtype": "Currency", "label": "Total Amt", "in_list_view": 1, "fetch_from": "bill_no.total_amount", "read_only": 1},
                {"fieldname": "balance", "fieldtype": "Currency", "label": "Balance", "in_list_view": 1, "fetch_from": "bill_no.outstanding_amount", "read_only": 1},
                {"fieldname": "paid_amt", "fieldtype": "Currency", "label": "Paid Amt", "in_list_view": 1},
                {"fieldname": "deduct_amt", "fieldtype": "Currency", "label": "Deduct Amt", "in_list_view": 1},
                {"fieldname": "tds_amt", "fieldtype": "Currency", "label": "TDS Amt", "in_list_view": 1},
                {"fieldname": "outstanding_amt", "fieldtype": "Currency", "label": "Outstanding Amt", "in_list_view": 1, "read_only": 1}
            ]
        })
        doc.insert()
        frappe.db.commit()
        print("Created Allocated Transport Invoice")

    # 2. Update Money Receipt DocType
    mr = frappe.get_doc("DocType", "Money Receipt")
    
    # Remove payment_reference and allocated_lrs
    mr.fields = [f for f in mr.fields if f.fieldname not in ("payment_reference", "allocated_lrs")]

    # Check if new fields exist
    fieldnames = [f.fieldname for f in mr.fields]
    
    # Add new fields
    new_fields = [
        {"fieldname": "cheque_no", "fieldtype": "Data", "label": "Cheque No", "depends_on": "eval:in_list(['Cheque'], doc.payment_mode)", "insert_after": "payment_mode"},
        {"fieldname": "cheque_date", "fieldtype": "Date", "label": "Cheque Date", "depends_on": "eval:in_list(['Cheque'], doc.payment_mode)", "insert_after": "cheque_no"},
        {"fieldname": "on_account", "fieldtype": "Check", "label": "On Account", "insert_after": "date"},
        {"fieldname": "amount_in_words", "fieldtype": "Small Text", "label": "Amount in Words", "read_only": 1, "insert_after": "cheque_date"},
        
        {"fieldname": "get_unpaid_bills", "fieldtype": "Button", "label": "Get Unpaid Bills", "insert_after": "sb1"},
        {"fieldname": "allocated_invoices", "fieldtype": "Table", "options": "Allocated Transport Invoice", "label": "Allocated Transport Invoices", "insert_after": "get_unpaid_bills"},
        
        {"fieldname": "total_amount", "fieldtype": "Currency", "label": "Total Amount", "read_only": 1, "insert_after": "allocated_invoices"},
        {"fieldname": "remarks", "fieldtype": "Small Text", "label": "Remarks", "insert_after": "total_amount"}
    ]
    
    for f in new_fields:
        if f["fieldname"] not in fieldnames:
            # find insert_after index
            idx = 0
            for i, existing_f in enumerate(mr.fields):
                if existing_f.fieldname == f.get("insert_after"):
                    idx = i + 1
                    break
            if idx == 0:
                idx = len(mr.fields)
            
            mr.append("fields", {
                "fieldname": f["fieldname"],
                "fieldtype": f["fieldtype"],
                "label": f["label"],
                "options": f.get("options", ""),
                "depends_on": f.get("depends_on", ""),
                "read_only": f.get("read_only", 0),
                "insert_after": f.get("insert_after", "")
            })
            
    # Fix order
    mr.save()
    frappe.db.commit()
    print("Updated Money Receipt")

