# Copyright (c) 2026, Ridhira Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class TransportInvoice(Document):
    def validate(self):
        self.calculate_totals()
        
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

    def on_cancel(self):
        self.update_lorry_receipts(is_submit=False)
        self.status = "Cancelled"
        self.db_update()

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
