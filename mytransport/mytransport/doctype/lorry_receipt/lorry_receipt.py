# Copyright (c) 2026, Ridhira Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class LorryReceipt(Document):
    def autoname(self):
        from mytransport.branch_numbering import get_next_branch_number, update_branch_number_counter
        if not self.lr_number:
            self.lr_number = str(get_next_branch_number(self.branch, "Lorry Receipt", self.date))
        else:
            update_branch_number_counter(self.branch, "Lorry Receipt", self.date, self.lr_number)
        self.name = self.lr_number

    def validate(self):
        if getattr(self, "lr_number", None):
            existing = frappe.db.exists("Lorry Receipt", {
                "lr_number": self.lr_number,
                "name": ("!=", self.name),
                "docstatus": ("!=", 2)
            })
            if existing:
                frappe.throw(f"Lorry Receipt with LR Number {self.lr_number} already exists")

    def before_save(self):
        # Calculate totals from items
        self.basic_freight = sum([flt(item.lorry_freight) for item in self.get("items")])
        self.total_weight = sum([flt(item.actual_weight) for item in self.get("items")])
        self.total_packages = sum([frappe.utils.cint(item.qty) for item in self.get("items")])
        
        # Calculate Total Amount from freight charges
        self.total_amount = (
            flt(self.basic_freight) +
            flt(self.hamali_charges) +
            flt(self.detention_charges) +
            flt(self.bilty_charges) +
            flt(self.rto_charges) +
            flt(self.other_charges)
        )

        if not self.paid_amount:
            self.paid_amount = 0
            
        self.outstanding_amount = self.total_amount - self.paid_amount
            
        if self.paid_amount == 0:
            self.receipt_status = "Unpaid"
        elif self.outstanding_amount <= 0:
            self.receipt_status = "Paid"
        else:
            self.receipt_status = "Partially Paid"
