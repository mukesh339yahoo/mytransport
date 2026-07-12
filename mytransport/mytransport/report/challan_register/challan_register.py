import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "challan_number", "label": _("Challan Number"), "fieldtype": "Link", "options": "Challan", "width": 120},
        {"fieldname": "date", "label": _("Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "branch", "label": _("Branch"), "fieldtype": "Link", "options": "Branch", "width": 120},
        {"fieldname": "broker", "label": _("Broker"), "fieldtype": "Link", "options": "Supplier", "width": 150},
        {"fieldname": "vehicle_number", "label": _("Vehicle Number"), "fieldtype": "Data", "width": 120},
        {"fieldname": "driver_name", "label": _("Driver Name"), "fieldtype": "Data", "width": 120},
        {"fieldname": "from_location", "label": _("From Location"), "fieldtype": "Link", "options": "Territory", "width": 120},
        {"fieldname": "to_location", "label": _("To Location"), "fieldtype": "Link", "options": "Territory", "width": 120},
        {"fieldname": "total_hire_amount", "label": _("Total Hire Amount"), "fieldtype": "Currency", "width": 130},
        {"fieldname": "advance", "label": _("Advance Amount"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "balance_amount", "label": _("Balance Amount"), "fieldtype": "Currency", "width": 120}
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
        
    if filters.get("broker"):
        conditions.append("broker = %(broker)s")
        values["broker"] = filters.get("broker")

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = """
        SELECT 
            name as challan_number, date, branch, broker, vehicle_number, driver_name,
            from_location, to_location, total_hire_amount, advance, balance_amount
        FROM `tabChallan`
        WHERE {where_clause} AND docstatus < 2
        ORDER BY date DESC, name DESC
    """.format(where_clause=where_clause)
    
    data = frappe.db.sql(query, values, as_dict=1)
    
    return data
