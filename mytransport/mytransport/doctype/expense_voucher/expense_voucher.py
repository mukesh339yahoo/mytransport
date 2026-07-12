import frappe
from frappe.model.document import Document

class ExpenseVoucher(Document):
    def autoname(self):
        from mytransport.branch_numbering import get_next_branch_number, update_branch_number_counter
        if not self.voucher_no:
            self.voucher_no = str(get_next_branch_number(self.branch, "Expense Voucher", self.date))
        else:
            update_branch_number_counter(self.branch, "Expense Voucher", self.date, self.voucher_no)
        self.name = self.voucher_no

    def validate(self):
        if getattr(self, "voucher_no", None):
            existing = frappe.db.exists("Expense Voucher", {
                "voucher_no": self.voucher_no,
                "name": ("!=", self.name),
                "docstatus": ("!=", 2)
            })
            if existing:
                frappe.throw(f"Expense Voucher with Voucher No {self.voucher_no} already exists")

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
        
        # Debit the party account
        je.append("accounts", {
            "account": self.debit_account,
            "debit_in_account_currency": self.total_paid_amt,
            "party_type": self.party_type,
            "party": self.party,
            "is_advance": "Yes"
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
            ch.challan_number as challan_no, 
            ev.voucher_no as voucher_no, 
            ev.date as voucher_date, 
            ac.paid_amt as amount, 
            ev.party as vendor 
        FROM `tabAllocated Challan` ac
        JOIN `tabExpense Voucher` ev ON ac.parent = ev.name
        JOIN `tabChallan` ch ON ac.challan = ch.name
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
            ev.party as vendor 
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

@frappe.whitelist()
def get_unpaid_challans_for_vendor(party, current_voucher=None):
    challans = frappe.get_all("Challan", filters={"docstatus": 1, "broker": party}, 
                              fields=["name", "challan_number", "date", "vehicle_number", "broker", "total_hire_amount"],
                              order_by="challan_number asc")
    
    if not challans:
        return []
        
    challan_names = [c.name for c in challans]
    payments = get_previous_payments(challan_names, current_voucher)
    
    payment_map = {}
    for p in payments:
        c_no = p.get("challan_no")
        payment_map[c_no] = payment_map.get(c_no, 0) + float(p.get("amount") or 0)
        
    result = []
    for c in challans:
        adjusted_amt = payment_map.get(c.challan_number, 0)
        balance_amount = float(c.total_hire_amount) - adjusted_amt
        
        if balance_amount > 0:
            c.adjusted_amt = adjusted_amt
            c.balance_amount = balance_amount
            result.append(c)
            
    return result
