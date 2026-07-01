import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "voucher_no", "label": _("Voucher No"), "fieldtype": "Link", "options": "Expense Voucher", "width": 120},
        {"fieldname": "date", "label": _("Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "branch", "label": _("Branch"), "fieldtype": "Link", "options": "Branch", "width": 120},
        {"fieldname": "vendor", "label": _("Vendor"), "fieldtype": "Link", "options": "Supplier", "width": 150},
        {"fieldname": "voucher_type", "label": _("Payment Mode"), "fieldtype": "Data", "width": 100},
        {"fieldname": "cheque_no", "label": _("Reference No"), "fieldtype": "Data", "width": 120},
        {"fieldname": "cheque_date", "label": _("Reference Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "total_paid_amt", "label": _("Total Paid Amount"), "fieldtype": "Currency", "width": 120}
    ]

def get_data(filters):
    conditions = []
    values = {}
    
    if filters.get("from_date"):
        conditions.append("date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")
        
    if filters.get("to_date"):
        conditions.append("date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")
        
    if filters.get("branch"):
        conditions.append("branch = %(branch)s")
        values["branch"] = filters.get("branch")
        
    if filters.get("vendor"):
        conditions.append("vendor = %(vendor)s")
        values["vendor"] = filters.get("vendor")

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    data = frappe.db.sql(f"""
        SELECT 
            name as voucher_no, date, branch, vendor, voucher_type, 
            cheque_no, cheque_date, total_paid_amt
        FROM `tabExpense Voucher`
        WHERE {where_clause} AND docstatus < 2
        ORDER BY date DESC, name DESC
    """, values, as_dict=1)
    
    return data
