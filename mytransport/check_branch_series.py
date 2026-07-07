import frappe

def check_branch_series():
    series = frappe.db.sql("SELECT name, current_number FROM `tabBranch Numbering Settings`", as_dict=1)
    print("Branch Numbering Settings:", series)
