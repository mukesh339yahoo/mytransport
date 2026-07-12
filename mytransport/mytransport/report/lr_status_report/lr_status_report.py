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
        {"fieldname": "consignor", "label": _("Consignor"), "fieldtype": "Link", "options": "Customer", "width": 150},
        {"fieldname": "consignee", "label": _("Consignee"), "fieldtype": "Link", "options": "Customer", "width": 150},
        {"fieldname": "challan_number", "label": _("Challan Number"), "fieldtype": "Link", "options": "Challan", "width": 120},
        {"fieldname": "transport_invoice", "label": _("Transport Invoice"), "fieldtype": "Link", "options": "Transport Invoice", "width": 120},
        {"fieldname": "status", "label": _("Billed Status"), "fieldtype": "Data", "width": 100},
        {"fieldname": "receipt_status", "label": _("Receipt Status"), "fieldtype": "Data", "width": 120},
        {"fieldname": "total_amount", "label": _("Total Freight"), "fieldtype": "Currency", "width": 120},
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
        
    if filters.get("status"):
        conditions.append("status = %(status)s")
        values["status"] = filters.get("status")
        
    if filters.get("receipt_status"):
        conditions.append("receipt_status = %(receipt_status)s")
        values["receipt_status"] = filters.get("receipt_status")

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = """
        SELECT 
            name as lr_number, date, consignor, consignee, challan_number, transport_invoice,
            status, receipt_status, total_amount, paid_amount, outstanding_amount
        FROM `tabLorry Receipt`
        WHERE {where_clause} AND docstatus < 2
        ORDER BY date DESC, name DESC
    """.format(where_clause=where_clause)
    
    data = frappe.db.sql(query, values, as_dict=1)
    
    return data
