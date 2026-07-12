import frappe
import json
import os

def create():
    frappe.init(site="mytransport.localhost")
    frappe.connect()

    reports = [
        {
            "name": "Transport Invoice Register",
            "ref_doctype": "Transport Invoice",
            "columns": [
                {"fieldname": "bill_no", "label": "Bill No", "fieldtype": "Link", "options": "Transport Invoice", "width": 120},
                {"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 100},
                {"fieldname": "branch", "label": "Branch", "fieldtype": "Link", "options": "Branch", "width": 120},
                {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "width": 150},
                {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100},
                {"fieldname": "total_amount", "label": "Total Amount", "fieldtype": "Currency", "width": 120},
                {"fieldname": "paid_amount", "label": "Paid Amount", "fieldtype": "Currency", "width": 120},
                {"fieldname": "outstanding_amount", "label": "Outstanding Amount", "fieldtype": "Currency", "width": 120}
            ]
        },
        {
            "name": "Money Receipt Register",
            "ref_doctype": "Money Receipt",
            "columns": [
                {"fieldname": "mr_no", "label": "MR No", "fieldtype": "Link", "options": "Money Receipt", "width": 120},
                {"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 100},
                {"fieldname": "branch", "label": "Branch", "fieldtype": "Link", "options": "Branch", "width": 120},
                {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "width": 150},
                {"fieldname": "payment_mode", "label": "Payment Mode", "fieldtype": "Data", "width": 100},
                {"fieldname": "cheque_no", "label": "Reference No", "fieldtype": "Data", "width": 120},
                {"fieldname": "cheque_date", "label": "Reference Date", "fieldtype": "Date", "width": 100},
                {"fieldname": "total_amount", "label": "Amount", "fieldtype": "Currency", "width": 120}
            ]
        },
        {
            "name": "Expense Voucher Register",
            "ref_doctype": "Expense Voucher",
            "columns": [
                {"fieldname": "voucher_no", "label": "Voucher No", "fieldtype": "Link", "options": "Expense Voucher", "width": 120},
                {"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 100},
                {"fieldname": "branch", "label": "Branch", "fieldtype": "Link", "options": "Branch", "width": 120},
                {"fieldname": "vendor", "label": "Vendor", "fieldtype": "Link", "options": "Supplier", "width": 150},
                {"fieldname": "voucher_type", "label": "Payment Mode", "fieldtype": "Data", "width": 100},
                {"fieldname": "cheque_no", "label": "Reference No", "fieldtype": "Data", "width": 120},
                {"fieldname": "cheque_date", "label": "Reference Date", "fieldtype": "Date", "width": 100},
                {"fieldname": "total_paid_amt", "label": "Total Paid Amount", "fieldtype": "Currency", "width": 120}
            ]
        }
    ]

    for report in reports:
        if not frappe.db.exists("Report", report["name"]):
            doc = frappe.new_doc("Report")
            doc.report_name = report["name"]
            doc.ref_doctype = report["ref_doctype"]
            doc.report_type = "Script Report"
            doc.is_standard = "Yes"
            doc.module = "Mytransport"
            doc.insert(ignore_permissions=True)
            print(f"Created {report['name']} Report record.")
            
            # Since it's is_standard, Frappe will generate the folders.
            # We will overwrite the .py and .js files.
        else:
            print(f"Report {report['name']} already exists.")

    frappe.db.commit()  # nosemgrep: required in standalone setup scripts

if __name__ == "__main__":
    create()
