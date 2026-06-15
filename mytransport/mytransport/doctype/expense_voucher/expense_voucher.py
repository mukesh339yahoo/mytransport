import frappe
from frappe.model.document import Document

class ExpenseVoucher(Document):
    def on_submit(self):
        # Create Journal Entry
        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Cash Entry" if self.voucher_type == "Cash" else "Bank Entry"
        je.company = self.company
        je.posting_date = self.date
        je.cheque_no = getattr(self, "cheque_no", None)
        if self.voucher_type == "Bank" and getattr(self, "cheque_date", None):
            je.cheque_date = self.cheque_date
        
        user_remark = self.remarks or ""
        je.user_remark = f"Expense Voucher: {self.name}. {user_remark}"
        
        # Credit the payment account (Bank/Cash)
        je.append("accounts", {
            "account": self.payment_account,
            "credit_in_account_currency": self.total_paid_amt,
            "reference_type": "Expense Voucher",
            "reference_name": self.name
        })
        
        # Debit the expense account
        je.append("accounts", {
            "account": self.expense_account,
            "debit_in_account_currency": self.total_paid_amt,
            "reference_type": "Expense Voucher",
            "reference_name": self.name
        })
        
        # Update Challan Advance Details
        for item in self.get("allocated_challans", []):
            challan_doc = frappe.get_doc("Challan", item.challan)
            
            # Increase the advance amount by the paid amount
            current_advance = frappe.utils.flt(challan_doc.advance)
            new_advance = current_advance + frappe.utils.flt(item.paid_amt)
            
            # Recalculate balance
            total_hire = frappe.utils.flt(challan_doc.total_hire_amount)
            new_balance = total_hire - new_advance
            
            frappe.db.set_value("Challan", item.challan, {
                "advance": new_advance,
                "balance_amount": new_balance
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
            
        # Revert Challan Advance Details
        for item in self.get("allocated_challans", []):
            challan_doc = frappe.get_doc("Challan", item.challan)
            
            # Decrease the advance amount by the paid amount
            current_advance = frappe.utils.flt(challan_doc.advance)
            new_advance = current_advance - frappe.utils.flt(item.paid_amt)
            
            # Recalculate balance
            total_hire = frappe.utils.flt(challan_doc.total_hire_amount)
            new_balance = total_hire - new_advance
            
            frappe.db.set_value("Challan", item.challan, {
                "advance": new_advance,
                "balance_amount": new_balance
            })
