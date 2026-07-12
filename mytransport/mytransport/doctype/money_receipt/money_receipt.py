import frappe
from frappe.model.document import Document
from frappe.utils import flt, money_in_words

class MoneyReceipt(Document):
    def autoname(self):
        from mytransport.branch_numbering import get_next_branch_number, update_branch_number_counter
        if not self.mr_no:
            self.mr_no = str(get_next_branch_number(self.branch, "Money Receipt", self.date))
        else:
            update_branch_number_counter(self.branch, "Money Receipt", self.date, self.mr_no)
        self.name = self.mr_no

    def validate(self):
        if flt(self.total_amount) <= 0:
            frappe.throw("Total Amount must be greater than 0")
            
        if getattr(self, "mr_no", None):
            existing = frappe.db.exists("Money Receipt", {
                "mr_no": self.mr_no,
                "name": ("!=", self.name),
                "docstatus": ("!=", 2)
            })
            if existing:
                frappe.throw(f"Money Receipt with MR No {self.mr_no} already exists")

    def on_submit(self):
        # Create Journal Entry
        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Journal Entry"
        je.company = self.company
        je.posting_date = self.date
        je.cheque_no = getattr(self, "cheque_no", None)
        je.cheque_date = getattr(self, "cheque_date", None)
        
        user_remark = self.remarks or ""
        je.user_remark = f"Money Receipt: {self.name}. {user_remark}"

        # Row 1: Debit the Bank/Cash Account
        je.append("accounts", {
            "account": self.deposit_account,
            "debit_in_account_currency": self.total_amount
        })

        # Row 2: Credit the Party Account
        je.append("accounts", {
            "account": self.credit_account,
            "credit_in_account_currency": self.total_amount,
            "party_type": self.party_type,
            "party": self.party,
            "is_advance": "Yes"
        })

        je.insert(ignore_permissions=True)
        je.submit()
        
        self.db_set("payment_entry", je.name)
        frappe.msgprint(f"Journal Entry {je.name} created successfully.")

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

    def on_cancel(self):
        if getattr(self, "payment_entry", None):
            je = frappe.get_doc("Journal Entry", self.payment_entry)
            if je.docstatus == 1:
                je.cancel()
            frappe.msgprint(f"Journal Entry {self.payment_entry} cancelled.")
            
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
def search_unified_party(query):
    customers = frappe.get_all("Customer", filters={"name": ["like", f"%{query}%"]}, limit=10, order_by="name asc")
    suppliers = frappe.get_all("Supplier", filters={"name": ["like", f"%{query}%"]}, limit=10, order_by="name asc")
    
    results = []
    for c in customers:
        results.append({"name": c.name, "party_type": "Customer"})
    for s in suppliers:
        results.append({"name": s.name, "party_type": "Supplier"})
        
    results.sort(key=lambda x: x["name"].lower())
    return results[:15]

@frappe.whitelist()
def get_money_in_words(amount, currency):
    return money_in_words(amount, currency)

@frappe.whitelist()
def get_previous_payments(invoices, current_receipt=None):
    if isinstance(invoices, str):
        import json
        invoices = json.loads(invoices)
        
    if not invoices:
        return []
        
    conditions = ""
    if current_receipt:
        conditions = " AND mr.name != %(current_receipt)s"
        
    sql = f"""
        SELECT 
            mr.mr_no as mr_no, 
            ati.bill_no as bill_no, 
            mr.cheque_no as cheque_no, 
            ati.paid_amt as paid_amt, 
            ati.deduct_amt as deduct_amt,
            ati.tds_amt as tds_amt
        FROM `tabAllocated Transport Invoice` ati
        JOIN `tabMoney Receipt` mr ON ati.parent = mr.name
        WHERE ati.transport_invoice IN %(invoices)s 
        AND mr.docstatus = 1 
        {conditions}
    """
    
    return frappe.db.sql(sql, {"invoices": tuple(invoices), "current_receipt": current_receipt}, as_dict=1)  # nosemgrep: frappe-sql-format-injection
