frappe.query_reports["LR Status Report"] = {
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
            "fieldname": "status",
            "label": __("Billed Status"),
            "fieldtype": "Select",
            "options": "\nUnbilled\nBilled\nCancelled"
        },
        {
            "fieldname": "receipt_status",
            "label": __("Receipt Status"),
            "fieldtype": "Select",
            "options": "\nUnpaid\nPartially Paid\nPaid"
        }
    ]
};
