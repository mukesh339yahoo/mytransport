import frappe

def run():
    doctype_name = "Allocated Challan"
    
    if frappe.db.exists("DocType", doctype_name):
        print(f"DocType {doctype_name} already exists.")
        return

    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": doctype_name,
        "module": "Mytransport",
        "custom": 0,
        "istable": 1,
        "editable_grid": 1,
        "fields": [
            {
                "fieldname": "challan",
                "fieldtype": "Link",
                "options": "Challan",
                "label": "Challan Ref",
                "in_list_view": 1,
                "reqd": 1
            },
            {
                "fieldname": "challan_no",
                "fieldtype": "Data",
                "label": "Challan No",
                "fetch_from": "challan.challan_number",
                "read_only": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "challan_date",
                "fieldtype": "Date",
                "label": "Challan Date",
                "fetch_from": "challan.date",
                "read_only": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "vehicle_no",
                "fieldtype": "Data",
                "label": "Vehicle No",
                "fetch_from": "challan.vehicle_number",
                "read_only": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "vendor",
                "fieldtype": "Data",
                "label": "Vendor",
                "fetch_from": "challan.broker",
                "read_only": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "total_amt",
                "fieldtype": "Currency",
                "label": "Total Amt",
                "fetch_from": "challan.total_hire_amount",
                "read_only": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "balance",
                "fieldtype": "Currency",
                "label": "Balance",
                "fetch_from": "challan.balance_amount",
                "read_only": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "paid_amt",
                "fieldtype": "Currency",
                "label": "Paid Amt",
                "in_list_view": 1,
                "reqd": 1
            }
        ]
    })
    
    doc.insert()
    frappe.db.commit()
    print(f"Created DocType {doctype_name} successfully.")
