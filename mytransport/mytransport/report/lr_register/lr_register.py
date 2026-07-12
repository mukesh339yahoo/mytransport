import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "lr_number", "label": _("LR Number"), "fieldtype": "Link", "options": "Lorry Receipt", "width": 120},
        {"fieldname": "date", "label": _("Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "branch", "label": _("Branch"), "fieldtype": "Link", "options": "Branch", "width": 120},
        {"fieldname": "consignor", "label": _("Consignor"), "fieldtype": "Link", "options": "Customer", "width": 150},
        {"fieldname": "consignee", "label": _("Consignee"), "fieldtype": "Link", "options": "Customer", "width": 150},
        {"fieldname": "from_city", "label": _("From City"), "fieldtype": "Link", "options": "Territory", "width": 120},
        {"fieldname": "to_city", "label": _("To City"), "fieldtype": "Link", "options": "Territory", "width": 120},
        {"fieldname": "challan_number", "label": _("Challan Number"), "fieldtype": "Link", "options": "Challan", "width": 120},
        {"fieldname": "total_amount", "label": _("Total Freight"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "status", "label": _("Billed Status"), "fieldtype": "Data", "width": 100},
        {"fieldname": "receipt_status", "label": _("Receipt Status"), "fieldtype": "Data", "width": 120}
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
        
    if filters.get("party"):
        conditions.append("(consignor = %(party)s OR consignee = %(party)s)")
        values["party"] = filters.get("party")

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = """  # nosemgrep: frappe-sql-format-injection
        SELECT 
            name as lr_number, date, branch, consignor, consignee, 
            from_city, to_city, challan_number, total_amount, status, receipt_status
        FROM `tabLorry Receipt`
        WHERE {where_clause} AND docstatus < 2
        ORDER BY date DESC, name DESC
    """.format(where_clause=where_clause)
    
    data = frappe.db.sql(query, values, as_dict=1)  # nosemgrep: frappe-sql-format-injection
    
    return data
