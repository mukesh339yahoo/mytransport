import frappe

def run():
    if frappe.db.exists("DocType", "Expense Voucher"):
        print("Expense Voucher already exists.")
        return

    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": "Expense Voucher",
        "module": "Mytransport",
        "custom": 0,
        "is_submittable": 1,
        "autoname": "format:EV-.YYYY.-.#####",
        "fields": [
            {"fieldname": "company", "fieldtype": "Link", "options": "Company", "label": "Company", "reqd": 1, "default": "frappe.defaults.get_user_default('Company')"},
            {"fieldname": "date", "fieldtype": "Date", "label": "Date", "reqd": 1, "default": "Today"},
            {"fieldname": "cb1", "fieldtype": "Column Break"},
            {"fieldname": "voucher_type", "fieldtype": "Select", "options": "Cash\nBank", "label": "Voucher Type", "reqd": 1, "default": "Cash"},
            {"fieldname": "payment_account", "fieldtype": "Link", "options": "Account", "label": "Payment Account", "reqd": 1},
            
            {"fieldname": "sb1", "fieldtype": "Section Break", "label": "Expense Details"},
            {"fieldname": "expense_category", "fieldtype": "Select", "options": "Trip Advance\nTrip Balance\nOffice Stationary\nMiscellaneous", "label": "Expense Category", "reqd": 1},
            {"fieldname": "expense_account", "fieldtype": "Link", "options": "Account", "label": "Expense Account", "reqd": 1},
            {"fieldname": "challan", "fieldtype": "Link", "options": "Challan", "label": "Challan", "depends_on": "eval:in_list(['Trip Advance', 'Trip Balance'], doc.expense_category)"},
            {"fieldname": "cb2", "fieldtype": "Column Break"},
            {"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "reqd": 1},
            {"fieldname": "paid_to", "fieldtype": "Data", "label": "Paid To"},
            {"fieldname": "payment_reference", "fieldtype": "Data", "label": "Payment Reference", "depends_on": "eval:doc.voucher_type=='Bank'"},
            
            {"fieldname": "sb2", "fieldtype": "Section Break"},
            {"fieldname": "remarks", "fieldtype": "Small Text", "label": "Remarks"},
            
            {"fieldname": "journal_entry", "fieldtype": "Link", "options": "Journal Entry", "label": "Journal Entry", "read_only": 1, "print_hide": 1}
        ],
        "permissions": [
            {
                "role": "System Manager",
                "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1
            }
        ]
    })
    
    doc.insert(ignore_permissions=True)
    frappe.db.commit()  # nosemgrep: required in standalone setup scripts
    print("Expense Voucher created successfully.")
