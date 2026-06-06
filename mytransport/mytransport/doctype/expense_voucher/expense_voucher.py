import frappe
from frappe.model.document import Document

class ExpenseVoucher(Document):
    def on_submit(self):
        # Create Journal Entry
        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Cash Entry" if self.voucher_type == "Cash" else "Bank Entry"
        je.company = self.company
        je.posting_date = self.date
        je.cheque_no = self.payment_reference
        if self.voucher_type == "Bank" and self.date:
            je.cheque_date = self.date
        
        user_remark = self.remarks or ""
        je.user_remark = f"Expense Voucher: {self.name}. {user_remark}"
        
        # Credit the payment account (Bank/Cash)
        je.append("accounts", {
            "account": self.payment_account,
            "credit_in_account_currency": self.amount,
            "reference_type": "Expense Voucher",
            "reference_name": self.name
        })
        
        # Debit the expense account
        je.append("accounts", {
            "account": self.expense_account,
            "debit_in_account_currency": self.amount,
            "reference_type": "Expense Voucher",
            "reference_name": self.name
        })
        
        je.insert(ignore_permissions=True)
        je.submit()
        
        self.db_set("journal_entry", je.name)
        frappe.msgprint(f"Journal Entry {je.name} created successfully.")

    def on_cancel(self):
        if self.journal_entry:
            je = frappe.get_doc("Journal Entry", self.journal_entry)
            if je.docstatus == 1:
                je.cancel()
            frappe.msgprint(f"Journal Entry {je.name} cancelled.")
