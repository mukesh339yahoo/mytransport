import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "bill_no", "label": _("Bill No"), "fieldtype": "Link", "options": "Transport Invoice", "width": 120},
        {"fieldname": "date", "label": _("Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "branch", "label": _("Branch"), "fieldtype": "Link", "options": "Branch", "width": 120},
        {"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link", "options": "Customer", "width": 150},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
        {"fieldname": "total_amount", "label": _("Total Amount"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "paid_amount", "label": _("Paid Amount"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "outstanding_amount", "label": _("Outstanding Amount"), "fieldtype": "Currency", "width": 120}
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
    
    data = frappe.db.sql(f"""
        SELECT 
            name as bill_no, date, branch, customer, status, 
            total_amount, paid_amount, outstanding_amount
        FROM `tabTransport Invoice`
        WHERE {where_clause} AND docstatus < 2
        ORDER BY date DESC, name DESC
    """, values, as_dict=1)
    
    return data
