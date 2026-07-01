import frappe
from frappe.model.document import Document

class ExpenseVoucher(Document):
    def before_insert(self):
        from mytransport.branch_numbering import get_next_branch_number, update_branch_number_counter
        if not self.voucher_no:
            self.voucher_no = get_next_branch_number(self.branch, "Expense Voucher", self.date)
        else:
            update_branch_number_counter(self.branch, "Expense Voucher", self.date, self.voucher_no)

    def on_submit(self):
        # Create Journal Entry
        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Cash Entry" if self.voucher_type == "Cash" else "Bank Entry"
        je.company = self.company
        je.posting_date = self.date
        je.cheque_no = getattr(self, "cheque_no", None)
        if self.voucher_type in ["Bank", "Cheque", "UPI"] and getattr(self, "cheque_date", None):
            je.cheque_date = self.cheque_date
        
        user_remark = self.remarks or ""
        je.user_remark = f"Expense Voucher: {self.name}. {user_remark}"
        
        # Credit the payment account (Bank/Cash)
        je.append("accounts", {
            "account": self.payment_account,
            "credit_in_account_currency": self.total_paid_amt
        })
        
        # Debit the expense account
        je.append("accounts", {
            "account": self.expense_account,
            "debit_in_account_currency": self.total_paid_amt
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

@frappe.whitelist()
def get_previous_payments(challans, current_voucher=None):
    if isinstance(challans, str):
        import json
        challans = json.loads(challans)
        
    if not challans:
        return []
        
    conditions = ""
    if current_voucher:
        conditions = " AND ev.name != %(current_voucher)s"
        
    # Query 1: Payments from Allocated Challans
    sql1 = f"""
        SELECT 
            ac.challan_no as challan_no, 
            ev.voucher_no as voucher_no, 
            ev.date as voucher_date, 
            ac.paid_amt as amount, 
            ev.vendor as vendor 
        FROM `tabAllocated Challan` ac
        JOIN `tabExpense Voucher` ev ON ac.parent = ev.name
        WHERE ac.challan IN %(challans)s 
        AND ev.docstatus = 1 
        {conditions}
    """
    
    # Query 2: Payments from Expense Details
    sql2 = f"""
        SELECT 
            ch.challan_number as challan_no, 
            ev.voucher_no as voucher_no, 
            ev.date as voucher_date, 
            ed.expense_amount as amount, 
            ev.vendor as vendor 
        FROM `tabExpense Detail` ed
        JOIN `tabExpense Voucher` ev ON ed.parent = ev.name
        JOIN `tabChallan` ch ON ed.challan_ref = ch.name
        WHERE ed.challan_ref IN %(challans)s 
        AND ev.docstatus = 1 
        {conditions}
    """
    
    res1 = frappe.db.sql(sql1, {"challans": tuple(challans), "current_voucher": current_voucher}, as_dict=1)
    res2 = frappe.db.sql(sql2, {"challans": tuple(challans), "current_voucher": current_voucher}, as_dict=1)
    
    return res1 + res2
