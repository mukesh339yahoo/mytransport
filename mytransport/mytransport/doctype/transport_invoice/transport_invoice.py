# Copyright (c) 2026, Ridhira Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class TransportInvoice(Document):  # nosemgrep
    def autoname(self):
        from mytransport.branch_numbering import get_next_branch_number, update_branch_number_counter
        if not self.bill_no:
            self.bill_no = str(get_next_branch_number(self.branch, "Transport Invoice", self.date))
        else:
            update_branch_number_counter(self.branch, "Transport Invoice", self.date, self.bill_no)
        self.name = self.bill_no

    def validate(self):
        from frappe.utils import getdate, nowdate
        if self.date and getdate(self.date) > getdate(nowdate()):
            frappe.throw("Transport Invoice Date cannot be a future date")
            
        if self.bill_no:
            existing = frappe.db.exists("Transport Invoice", {
                "bill_no": self.bill_no,
                "name": ("!=", self.name),
                "docstatus": ("!=", 2)
            })
            if existing:
                frappe.throw(f"Transport Invoice with Bill No {self.bill_no} already exists")
        
        self.calculate_totals()
        if not self.company:
            frappe.throw("Company is mandatory for accounting entries")
        if not self.debit_to:
            frappe.throw("Debit To account is mandatory")
        if not self.income_account:
            frappe.throw("Income Account is mandatory")
        
    def calculate_totals(self):
        tf = 0.0
        ts = 0.0
        td = 0.0
        th = 0.0
        to = 0.0
        
        for item in self.get("items"):
            tf += flt(item.basic_freight)
            ts += flt(item.st_charge)
            td += flt(item.detention_charges)
            th += flt(item.hamali_charges)
            to += flt(item.other_charges)
            
        self.total_freight = tf
        self.total_st_charge = ts
        self.total_detention_charge = td
        self.total_hamali_charge = th
        self.total_other_charges = to
        
        self.total_amount = tf + ts + td + th + to
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

    def before_cancel(self):
        # Tell Frappe framework to ignore ALL linked doctypes when checking for cancel block
        self.flags.ignore_links = True

    def on_cancel(self):  # nosemgrep
        self.update_lorry_receipts(is_submit=False)
        self.status = "Cancelled"
        self.db_update()
        self.make_gl_entries(cancel=True)

    def update_lorry_receipts(self, is_submit):
        for item in self.get("items"):
            if item.lr_number:
                if is_submit:
                    frappe.db.set_value("Lorry Receipt", item.lr_number, {
                        "status": "Billed",
                        "transport_invoice": self.name,
                        "invoice_number": self.name,
                        "invoice_value": self.total_amount
                    })
                else:
                    frappe.db.set_value("Lorry Receipt", item.lr_number, {
                        "status": "Unbilled",
                        "transport_invoice": None,
                        "invoice_number": None,
                        "invoice_value": 0
                    })

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
                "credit": 0.0,
                "credit_in_account_currency": 0.0,
                "against": self.income_account
            })
        )
        
        # 2. Credit the Income Account
        gl_entries.append(
            self.get_gl_dict({
                "account": self.income_account,
                "debit": 0.0,
                "debit_in_account_currency": 0.0,
                "credit": self.total_amount,
                "credit_in_account_currency": self.total_amount,
                "against": self.debit_to
            })
        )
        
        make_gl_entries(gl_entries, cancel=cancel, update_outstanding="No", merge_entries=False)
        
    def get_gl_dict(self, args):
        cost_center = frappe.get_cached_value('Company', self.company, 'cost_center')
        
        gl_dict = frappe._dict({
            "posting_date": self.date,
            "transaction_date": self.date,
            "voucher_type": self.doctype,
            "voucher_no": self.name,
            "company": self.company,
            "remarks": self.remarks or f"Accounting Entry for Transport Invoice {self.name}",
            "is_opening": "No",
            "cost_center": cost_center
        })
        gl_dict.update(args)
        return gl_dict

@frappe.whitelist()
def get_unbilled_lrs(customer, invoice_name=None):
    # Fetch Lorry Receipts that are Unbilled and where Credit Account matches the customer
    lrs = frappe.get_all(
        "Lorry Receipt",
        filters={
            "status": "Unbilled",
            "docstatus": 1,
            "credit_account": customer
        },
        fields=[
            "name", "date", "from_city", "to_city", "total_packages", "total_weight",
            "basic_freight", "bilty_charges", "detention_narration", "detention_charges",
            "hamali_narration", "hamali_charges", "other_charge_narration", "other_charges"
        ]
    )
    
    for lr in lrs:
        items = frappe.get_all("LR Item", filters={"parent": lr.name}, fields=["charged_weight"])
        lr.total_charged_weight = sum(flt(item.charged_weight) for item in items)
        
    return lrs
