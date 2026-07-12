import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "mr_no", "label": _("MR No"), "fieldtype": "Link", "options": "Money Receipt", "width": 120},
        {"fieldname": "date", "label": _("Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "branch", "label": _("Branch"), "fieldtype": "Link", "options": "Branch", "width": 120},
        {"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link", "options": "Customer", "width": 150},
        {"fieldname": "payment_mode", "label": _("Payment Mode"), "fieldtype": "Data", "width": 100},
        {"fieldname": "cheque_no", "label": _("Reference No"), "fieldtype": "Data", "width": 120},
        {"fieldname": "cheque_date", "label": _("Reference Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "total_amount", "label": _("Amount"), "fieldtype": "Currency", "width": 120}
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
        
    if filters.get("customer"):
        conditions.append("customer = %(customer)s")
        values["customer"] = filters.get("customer")

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    data = frappe.db.sql(f"""  # nosemgrep: frappe-sql-format-injection
        SELECT 
            name as mr_no, date, branch, customer, payment_mode, 
            cheque_no, cheque_date, total_amount
        FROM `tabMoney Receipt`
        WHERE {where_clause} AND docstatus < 2
        ORDER BY date DESC, name DESC
    """, values, as_dict=1)
    
    return data
