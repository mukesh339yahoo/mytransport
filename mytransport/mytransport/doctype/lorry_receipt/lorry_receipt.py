# Copyright (c) 2026, Shaily Sharma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LorryReceipt(Document):
    def before_save(self):
        if not self.paid_amount:
            self.paid_amount = 0
        if not self.outstanding_amount and self.total_amount:
            self.outstanding_amount = self.total_amount - self.paid_amount
        elif self.total_amount:
            self.outstanding_amount = self.total_amount - self.paid_amount
            
        if self.paid_amount == 0:
            self.receipt_status = "Unpaid"
        elif self.outstanding_amount <= 0:
            self.receipt_status = "Paid"
        else:
            self.receipt_status = "Partially Paid"
