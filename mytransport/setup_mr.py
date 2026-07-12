import frappe

def run():
    # Money Receipt Item
    if not frappe.db.exists("DocType", "Money Receipt Item"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Money Receipt Item",
            "module": "Mytransport",
            "custom": 0,
            "istable": 1,
            "fields": [
                {"fieldname": "lorry_receipt", "fieldtype": "Link", "options": "Lorry Receipt", "label": "Lorry Receipt", "reqd": 1, "in_list_view": 1},
                {"fieldname": "total_freight", "fieldtype": "Currency", "label": "Total Freight", "read_only": 1, "in_list_view": 1},
                {"fieldname": "outstanding_amount", "fieldtype": "Currency", "label": "Outstanding Amount", "read_only": 1, "in_list_view": 1},
                {"fieldname": "allocated_amount", "fieldtype": "Currency", "label": "Allocated Amount", "reqd": 1, "in_list_view": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("Money Receipt Item created.")
        
    # Money Receipt
    if not frappe.db.exists("DocType", "Money Receipt"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Money Receipt",
            "module": "Mytransport",
            "custom": 0,
            "is_submittable": 1,
            "autoname": "format:MR-.YYYY.-.#####",
            "fields": [
                {"fieldname": "company", "fieldtype": "Link", "options": "Company", "label": "Company", "reqd": 1, "default": "frappe.defaults.get_user_default('Company')"},
                {"fieldname": "customer", "fieldtype": "Link", "options": "Customer", "label": "Customer", "reqd": 1},
                {"fieldname": "date", "fieldtype": "Date", "label": "Date", "reqd": 1, "default": "Today"},
                {"fieldname": "cb1", "fieldtype": "Column Break"},
                {"fieldname": "payment_mode", "fieldtype": "Select", "options": "Cash\nBank\nCheque\nUPI", "label": "Payment Mode", "reqd": 1, "default": "Bank"},
                {"fieldname": "deposit_account", "fieldtype": "Link", "options": "Account", "label": "Deposit Account", "reqd": 1},
                {"fieldname": "payment_reference", "fieldtype": "Data", "label": "Payment Reference", "depends_on": "eval:in_list(['Bank', 'Cheque', 'UPI'], doc.payment_mode)"},
                
                {"fieldname": "sb1", "fieldtype": "Section Break", "label": "Allocation"},
                {"fieldname": "allocated_lrs", "fieldtype": "Table", "options": "Money Receipt Item", "label": "Allocated LRs"},
                
                {"fieldname": "sb2", "fieldtype": "Section Break", "label": "Totals"},
                {"fieldname": "total_amount_received", "fieldtype": "Currency", "label": "Total Amount Received", "reqd": 1},
                {"fieldname": "cb2", "fieldtype": "Column Break"},
                {"fieldname": "unallocated_amount", "fieldtype": "Currency", "label": "Unallocated Amount", "read_only": 1},
                
                {"fieldname": "payment_entry", "fieldtype": "Link", "options": "Payment Entry", "label": "Payment Entry", "read_only": 1, "print_hide": 1}
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1
                }
            ]
        })
        doc.insert(ignore_permissions=True)
        print("Money Receipt created.")
        
    frappe.db.commit()  # nosemgrep: required in standalone setup scripts
