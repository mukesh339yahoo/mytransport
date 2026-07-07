import re

with open("apps/mytransport/mytransport/mytransport/doctype/lorry_receipt/test_lorry_receipt.py", "r") as f:
    content = f.read()

patch = """
        # Clear existing test records to ensure clean state
        frappe.db.sql("DELETE FROM `tabBranch Numbering Settings` WHERE branch='Test Branch'")
        
        bns = frappe.new_doc("Branch Numbering Settings")
        bns.branch = "Test Branch"
        bns.financial_year = "2026-2027"
        doctypes = ["Lorry Receipt", "Challan", "Transport Invoice", "Expense Voucher", "Money Receipt"]
        for dt in doctypes:
            bns.append("numbering_details", {
                "document_type": dt,
                "prefix": "TEST-" + "".join([w[0] for w in dt.split()]),
                "starting_number": 1,
                "current_number": 0
            })
        bns.insert(ignore_permissions=True, ignore_mandatory=True)
        
        frappe.db.sql("DELETE FROM `tabLorry Receipt`"""

content = content.replace('        frappe.db.sql("DELETE FROM `tabLorry Receipt`', patch)

with open("apps/mytransport/mytransport/mytransport/doctype/lorry_receipt/test_lorry_receipt.py", "w") as f:
    f.write(content)
