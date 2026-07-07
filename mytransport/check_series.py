import frappe

def check_series():
    latest_inv = frappe.db.sql("SELECT name FROM `tabTransport Invoice` ORDER BY creation DESC LIMIT 5", as_dict=1)
    print("Latest Invoices:", latest_inv)
    
    series = frappe.db.sql("SELECT * FROM `tabSeries` WHERE name LIKE 'INV-%'", as_dict=1)
    print("tabSeries records for INV:", series)
