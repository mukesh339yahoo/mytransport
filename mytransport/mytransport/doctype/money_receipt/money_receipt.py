import frappe
from frappe.model.document import Document

class MoneyReceipt(Document):
    def validate(self):
        if self.unallocated_amount < 0:
            frappe.throw("Unallocated amount cannot be negative. Please check your allocations.")

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
        pe.paid_amount = self.total_amount_received
        pe.received_amount = self.total_amount_received
        pe.reference_no = self.payment_reference
        if self.date:
            pe.reference_date = self.date

        # Group allocations by Sales Invoice
        invoice_allocations = {}
        for item in self.allocated_lrs:
            lr_doc = frappe.get_doc("Lorry Receipt", item.lorry_receipt)
            
            # Update LR balances
            lr_doc.paid_amount += item.allocated_amount
            lr_doc.save(ignore_permissions=True)
            
            if not lr_doc.sales_invoice:
                frappe.throw(f"LR {lr_doc.name} is not associated with a Sales Invoice. Cannot allocate payment.")
                
            if lr_doc.sales_invoice not in invoice_allocations:
                invoice_allocations[lr_doc.sales_invoice] = 0
            invoice_allocations[lr_doc.sales_invoice] += item.allocated_amount

        # Set Party Account
        pe.paid_from = frappe.db.get_value("Customer", self.customer, "default_account")
        if not pe.paid_from:
            # Fallback to fetching default receivable account for company
            pe.paid_from = frappe.db.get_value("Company", self.company, "default_receivable_account")

        # Add references to Payment Entry
        for inv, amount in invoice_allocations.items():
            pe.append("references", {
                "reference_doctype": "Sales Invoice",
                "reference_name": inv,
                "allocated_amount": amount
            })

        pe.insert(ignore_permissions=True)
        pe.submit()
        
        self.db_set("payment_entry", pe.name)
        frappe.msgprint(f"Payment Entry {pe.name} created successfully.")

    def on_cancel(self):
        if self.payment_entry:
            pe = frappe.get_doc("Payment Entry", self.payment_entry)
            if pe.docstatus == 1:
                pe.cancel()
            frappe.msgprint(f"Payment Entry {pe.name} cancelled.")
            
        # Revert LR balances
        for item in self.allocated_lrs:
            lr_doc = frappe.get_doc("Lorry Receipt", item.lorry_receipt)
            lr_doc.paid_amount -= item.allocated_amount
            lr_doc.save(ignore_permissions=True)
