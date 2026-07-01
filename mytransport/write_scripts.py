import os

# Transport Invoice Register
tir_py = """import frappe
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
    
    data = frappe.db.sql(f\"\"\"
        SELECT 
            name as bill_no, date, branch, customer, status, 
            total_amount, paid_amount, outstanding_amount
        FROM `tabTransport Invoice`
        WHERE {where_clause} AND docstatus < 2
        ORDER BY date DESC, name DESC
    \"\"\", values, as_dict=1)
    
    return data
"""

tir_js = """frappe.query_reports["Transport Invoice Register"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch"
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		}
	]
};
"""

# Money Receipt Register
mrr_py = """import frappe
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
    
    data = frappe.db.sql(f\"\"\"
        SELECT 
            name as mr_no, date, branch, customer, payment_mode, 
            cheque_no, cheque_date, total_amount
        FROM `tabMoney Receipt`
        WHERE {where_clause} AND docstatus < 2
        ORDER BY date DESC, name DESC
    \"\"\", values, as_dict=1)
    
    return data
"""

mrr_js = """frappe.query_reports["Money Receipt Register"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch"
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		}
	]
};
"""

# Expense Voucher Register
evr_py = """import frappe
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
    
    data = frappe.db.sql(f\"\"\"
        SELECT 
            name as voucher_no, date, branch, vendor, voucher_type, 
            cheque_no, cheque_date, total_paid_amt
        FROM `tabExpense Voucher`
        WHERE {where_clause} AND docstatus < 2
        ORDER BY date DESC, name DESC
    \"\"\", values, as_dict=1)
    
    return data
"""

evr_js = """frappe.query_reports["Expense Voucher Register"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch"
		},
		{
			"fieldname": "vendor",
			"label": __("Vendor"),
			"fieldtype": "Link",
			"options": "Supplier"
		}
	]
};
"""

with open("apps/mytransport/mytransport/mytransport/report/transport_invoice_register/transport_invoice_register.py", "w") as f:
    f.write(tir_py)
with open("apps/mytransport/mytransport/mytransport/report/transport_invoice_register/transport_invoice_register.js", "w") as f:
    f.write(tir_js)

with open("apps/mytransport/mytransport/mytransport/report/money_receipt_register/money_receipt_register.py", "w") as f:
    f.write(mrr_py)
with open("apps/mytransport/mytransport/mytransport/report/money_receipt_register/money_receipt_register.js", "w") as f:
    f.write(mrr_js)

with open("apps/mytransport/mytransport/mytransport/report/expense_voucher_register/expense_voucher_register.py", "w") as f:
    f.write(evr_py)
with open("apps/mytransport/mytransport/mytransport/report/expense_voucher_register/expense_voucher_register.js", "w") as f:
    f.write(evr_js)

print("Report files written successfully!")
