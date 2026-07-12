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
        {"fieldname": "from_location", "label": _("From Location"), "fieldtype": "Link", "options": "Territory", "width": 120},
        {"fieldname": "to_location", "label": _("To Location"), "fieldtype": "Link", "options": "Territory", "width": 120},
        {"fieldname": "expected_revenue", "label": _("Expected Revenue"), "fieldtype": "Currency", "width": 140},
        {"fieldname": "received_revenue", "label": _("Received Revenue"), "fieldtype": "Currency", "width": 140},
        {"fieldname": "trip_expense", "label": _("Trip Expense"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "expected_profit", "label": _("Expected Profit"), "fieldtype": "Currency", "width": 130},
        {"fieldname": "real_net_profit", "label": _("Real Net Profit"), "fieldtype": "Currency", "width": 130}
    ]

def get_data(filters):
    conditions = []
    values = {}
    
    if filters.get("from_date"):
        conditions.append("c.date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")
        
    if filters.get("to_date"):
        conditions.append("c.date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")
        
    if filters.get("branch"):
        conditions.append("c.branch = %(branch)s")
        values["branch"] = filters.get("branch")

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = """
        SELECT 
            c.name as challan_number, 
            c.date, 
            c.from_location, 
            c.to_location,
            IFNULL(SUM(lr.total_amount), 0) as expected_revenue,
            IFNULL(SUM(lr.paid_amount), 0) as received_revenue,
            IFNULL(c.total_hire_amount, 0) as trip_expense,
            (IFNULL(SUM(lr.total_amount), 0) - IFNULL(c.total_hire_amount, 0)) as expected_profit,
            (IFNULL(SUM(lr.paid_amount), 0) - IFNULL(c.total_hire_amount, 0)) as real_net_profit
        FROM `tabChallan` c
        LEFT JOIN `tabLorry Receipt` lr ON lr.challan_number = c.name AND lr.docstatus < 2
        WHERE {where_clause} AND c.docstatus < 2
        GROUP BY c.name
        ORDER BY c.date DESC, c.name DESC
    """.format(where_clause=where_clause)
    
    data = frappe.db.sql(query, values, as_dict=1)
    
    return data
