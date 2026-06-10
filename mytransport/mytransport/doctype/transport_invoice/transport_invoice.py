# Copyright (c) 2026, Ridhira Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class TransportInvoice(Document):
    def validate(self):
        self.calculate_totals()
        if not self.company:
            frappe.throw("Company is mandatory for accounting entries")
        if not self.debit_to:
            frappe.throw("Debit To account is mandatory")
        if not self.income_account:
            frappe.throw("Income Account is mandatory")
        
    def calculate_totals(self):
        total = 0.0
        for item in self.get("items"):
            total += flt(item.amount)
            
        self.total_amount = total
        self.outstanding_amount = self.total_amount - flt(self.paid_amount)
        
        if self.paid_amount == 0:
            self.status = "Draft" if self.docstatus == 0 else "Unpaid"
        elif self.outstanding_amount <= 0:
            self.status = "Paid"
        else:
            self.status = "Partially Paid"

    def on_submit(self):
        self.update_lorry_receipts(is_submit=True)
        self.calculate_totals()
        self.db_update()
        self.make_gl_entries()

    def on_cancel(self):
        self.update_lorry_receipts(is_submit=False)
        self.status = "Cancelled"
        self.db_update()
        self.make_gl_entries(cancel=True)

    def update_lorry_receipts(self, is_submit):
        for item in self.get("items"):
            if item.lorry_receipt:
                lr = frappe.get_doc("Lorry Receipt", item.lorry_receipt)
                if is_submit:
                    lr.status = "Billed"
                    lr.sales_invoice = self.name
                    lr.invoice_number = self.name
                    lr.invoice_value = self.total_amount
                else:
                    lr.status = "Unbilled"
                    lr.sales_invoice = None
                    lr.invoice_number = None
                    lr.invoice_value = 0
                lr.save(ignore_permissions=True)

    def make_gl_entries(self, cancel=False):
        if not self.total_amount:
            return
            
        from erpnext.accounts.general_ledger import make_gl_entries
        
        gl_entries = []
        
        # 1. Debit the Customer Account (Accounts Receivable)
        gl_entries.append(
            self.get_gl_dict({
                "account": self.debit_to,
                "party_type": "Customer",
                "party": self.customer,
                "debit": self.total_amount,
                "debit_in_account_currency": self.total_amount,
                "against": self.income_account
            })
        )
        
        # 2. Credit the Income Account
        gl_entries.append(
            self.get_gl_dict({
                "account": self.income_account,
                "credit": self.total_amount,
                "credit_in_account_currency": self.total_amount,
                "against": self.debit_to
            })
        )
        
        make_gl_entries(gl_entries, cancel=cancel, update_outstanding="No", merge_entries=False)
        
    def get_gl_dict(self, args):
        gl_dict = frappe._dict({
            "posting_date": self.date,
            "transaction_date": self.date,
            "voucher_type": self.doctype,
            "voucher_no": self.name,
            "company": self.company,
            "remarks": self.remarks or f"Accounting Entry for Transport Invoice {self.name}",
            "is_opening": "No"
        })
        gl_dict.update(args)
        return gl_dict

@frappe.whitelist()
def get_unbilled_lrs(customer, invoice_name=None):
    # Fetch Lorry Receipts that are Unbilled and belong to this customer
    # The customer could be Consignor or Consignee, we check either
    lrs = frappe.get_all(
        "Lorry Receipt",
        filters={
            "status": "Unbilled",
            "docstatus": 1
        },
        or_filters={
            "consignor": customer,
            "consignee": customer
        },
        fields=["name", "date", "from_city", "to_city", "vehicle_number", "total_amount"]
    )
    return lrs
