import os

file_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/expense_voucher/expense_voucher.py"

with open(file_path, "r") as f:
    content = f.read()

new_logic = """
        # Update Challan Advance Details
        if self.challan:
            challan_doc = frappe.get_doc("Challan", self.challan)
            challan_doc.db_set("voucher_no", self.name)
            challan_doc.db_set("name_field", self.paid_to)
            challan_doc.db_set("remarks", self.remarks)
            
            if self.voucher_type == "Cash":
                challan_doc.db_set("cash_amount", self.amount)
            else:
                challan_doc.db_set("cheque_amount", self.amount)
                challan_doc.db_set("cheque_no", self.payment_reference)
                challan_doc.db_set("cheque_date", self.date)
                challan_doc.db_set("bank", self.payment_account)
"""

if "Update Challan Advance Details" not in content:
    idx = content.find("je.insert(ignore_permissions=True)")
    content = content[:idx] + new_logic + "\n        " + content[idx:]
    with open(file_path, "w") as f:
        f.write(content)
    print("Updated Expense Voucher")
else:
    print("Already updated")

