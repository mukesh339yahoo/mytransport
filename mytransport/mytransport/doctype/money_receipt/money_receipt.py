import frappe
from frappe.model.document import Document
from frappe.utils import flt, money_in_words

class MoneyReceipt(Document):
    def before_insert(self):
        from mytransport.mytransport.branch_numbering import get_next_branch_number
        if not self.mr_no:
            self.mr_no = get_next_branch_number(self.branch, "Money Receipt", self.date)

    def validate(self):
        pass

    def on_submit(self):
        # Create Payment Entry
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Receive"
        pe.party_type = "Customer"
        pe.party = self.customer
        pe.company = self.company
        pe.posting_date = self.date
        pe.mode_of_payment = self.payment_mode
        pe.paid_to = self.deposit_account
        pe.paid_amount = self.total_amount
        pe.received_amount = self.total_amount
        
        if getattr(self, "cheque_no", None):
            pe.reference_no = self.cheque_no
        if getattr(self, "cheque_date", None):
            pe.reference_date = self.cheque_date

        # Update Transport Invoices
        invoice_allocations = {}
        for item in self.get("allocated_invoices", []):
            inv_doc = frappe.get_doc("Transport Invoice", item.transport_invoice)
            new_paid = flt(inv_doc.paid_amount) + flt(item.paid_amt)
            new_out = flt(inv_doc.total_amount) - new_paid
            new_status = "Paid" if new_out <= 0 else "Partially Paid"
            
            frappe.db.set_value("Transport Invoice", item.transport_invoice, {
                "paid_amount": new_paid,
                "outstanding_amount": new_out,
                "status": new_status
            })
            
            invoice_allocations[item.transport_invoice] = item.paid_amt

        # Set Party Account
        from erpnext.accounts.party import get_party_account
        try:
            pe.paid_from = get_party_account("Customer", self.customer, self.company)
        except Exception:
            pe.paid_from = None
            
        if not pe.paid_from:
            # Fallback to fetching default receivable account for company
            pe.paid_from = frappe.db.get_value("Company", self.company, "default_receivable_account")

        pe.remarks = f"Payment received via Money Receipt: {self.name}"

        pe.insert(ignore_permissions=True)
        pe.submit()
        
        self.db_set("payment_entry", pe.name)
        frappe.msgprint(f"Payment Entry {pe.name} created successfully.")

    def on_cancel(self):
        if getattr(self, "payment_entry", None):
            pe = frappe.get_doc("Payment Entry", self.payment_entry)
            if pe.docstatus == 1:
                pe.cancel()
            frappe.msgprint(f"Payment Entry {self.payment_entry} cancelled.")
            
        # Revert Transport Invoice balances
        for item in self.get("allocated_invoices", []):
            inv_doc = frappe.get_doc("Transport Invoice", item.transport_invoice)
            new_paid = flt(inv_doc.paid_amount) - flt(item.paid_amt)
            new_out = flt(inv_doc.total_amount) - new_paid
            new_status = "Unpaid" if new_paid <= 0 else "Partially Paid"
            
            frappe.db.set_value("Transport Invoice", item.transport_invoice, {
                "paid_amount": new_paid,
                "outstanding_amount": new_out,
                "status": new_status
            })

@frappe.whitelist()
def get_money_in_words(amount, currency):
    return money_in_words(amount, currency)
