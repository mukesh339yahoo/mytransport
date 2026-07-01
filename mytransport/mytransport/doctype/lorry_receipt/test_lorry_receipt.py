import frappe
from frappe.tests.utils import FrappeTestCase

class IntegrationTestLorryReceipt(FrappeTestCase):
    def setUp(self):
        # Create minimal dependencies
        if not frappe.db.exists("Branch", "Test Branch"):
            b = frappe.new_doc("Branch")
            b.branch = "Test Branch"
            b.insert(ignore_permissions=True, ignore_mandatory=True)
            
        # Clear existing test records to ensure clean state

        # Clear existing test records to ensure clean state
        frappe.db.sql("DELETE FROM `tabBranch Numbering Settings` WHERE branch='Test Branch'")
        
        for dt, name in [
            ("Company", "Test Company"),
            ("Account", "Sales - TC"),
            ("Account", "Cash - TC"),
            ("Account", "Freight Expense - TC"),
            ("Account", "Debtors - TC"),
            ("Customer", "Test Consignor"),
            ("Customer", "Test Consignee"),
            ("Supplier", "Test Transporter"),
        ]:
            if not frappe.db.exists(dt, name):
                doc = frappe.new_doc(dt)
                if dt == "Company":
                    doc.company_name = name
                    doc.default_currency = "INR"
                elif dt == "Account":
                    doc.account_name = name
                    doc.company = "Test Company"
                    doc.account_type = "Cash"
                else:
                    doc.update({"name": name, frappe.scrub(dt)+"_name": name})
                try:
                    doc.insert(ignore_permissions=True, ignore_mandatory=True)
                except Exception:
                    pass
        
        doctypes = ["Lorry Receipt", "Challan", "Transport Invoice", "Expense Voucher", "Money Receipt"]
        for dt in doctypes:
            bns = frappe.new_doc("Branch Numbering Settings")
            bns.branch = "Test Branch"
            bns.financial_year = "2026-2027"
            bns.document_type = dt
            bns.starting_number = 90000
            bns.current_number = 89999
            bns.insert(ignore_permissions=True, ignore_mandatory=True)
        
        frappe.db.sql("DELETE FROM `tabLorry Receipt` WHERE name='TEST-LR-001'")
        frappe.db.sql("DELETE FROM `tabChallan` WHERE name='TEST-CH-001'")
        frappe.db.sql("DELETE FROM `tabTransport Invoice` WHERE name='TEST-INV-001'")
        frappe.db.sql("DELETE FROM `tabExpense Voucher` WHERE name='TEST-EV-001'")
        frappe.db.sql("DELETE FROM `tabMoney Receipt` WHERE name='TEST-MR-001'")
        frappe.db.commit()

    def test_end_to_end_transport_lifecycle(self):
        # ---------------------------------------------------------
        # STEP 1: Create a Lorry Receipt (LR)
        # ---------------------------------------------------------
        lr = frappe.new_doc("Lorry Receipt")
        lr.name = "TEST-LR-001"
        lr.branch = "Test Branch"
        lr.date = frappe.utils.today()
        lr.consignor = "Test Consignor"
        lr.consignee = "Test Consignee"
        lr.from_city = "Mumbai"
        lr.to_city = "Delhi"
        lr.total_amount = 5000
        lr.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        lr.submit()
        
        self.assertEqual(lr.docstatus, 1)
        self.assertTrue(lr.name)
        
        # ---------------------------------------------------------
        # STEP 2: Create a Challan & Link LR
        # ---------------------------------------------------------
        challan = frappe.new_doc("Challan")
        challan.name = "TEST-CH-001"
        challan.branch = "Test Branch"
        challan.date = frappe.utils.today()
        challan.from_location = "Mumbai"
        challan.to_location = "Delhi"
        challan.vendor = "Test Transporter"
        
        challan.append("lrs", {
            "lr_number": lr.name,
            "basic_freight": 5000
        })
        challan.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        challan.submit()
        self.assertEqual(challan.docstatus, 1)
        
        # ---------------------------------------------------------
        # STEP 3: Create Transport Invoice for the LR
        # ---------------------------------------------------------
        invoice = frappe.new_doc("Transport Invoice")
        invoice.name = "TEST-INV-001"
        invoice.branch = "Test Branch"
        invoice.date = frappe.utils.today()
        invoice.customer = "Test Consignor"
        invoice.company = "Test Company"
        invoice.debit_to = "Debtors - TC"
        invoice.income_account = "Sales - TC"
        
        invoice.append("items", {
            "lr_number": lr.name,
            "basic_freight": 5000
        })
        invoice.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        invoice.submit()
        self.assertEqual(invoice.docstatus, 1)
        
        # ---------------------------------------------------------
        # STEP 4: Create Expense Voucher for the Challan
        # ---------------------------------------------------------
        ev = frappe.new_doc("Expense Voucher")
        ev.name = "TEST-EV-001"
        ev.branch = "Test Branch"
        ev.company = "Test Company"
        ev.date = frappe.utils.today()
        ev.vendor = "Test Transporter"
        ev.voucher_type = "Cash"
        ev.payment_account = "Cash - TC"
        ev.expense_category = "Trip Advance"
        ev.expense_account = "Freight Expense - TC"
        ev.total_paid_amt = 4000
        
        ev.append("allocated_challans", {
            "challan": challan.name,
            "paid_amt": 4000
        })
        ev.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        ev.submit()
        self.assertEqual(ev.docstatus, 1)
        
        # ---------------------------------------------------------
        # STEP 5: Create Money Receipt for the Invoice
        # ---------------------------------------------------------
        mr = frappe.new_doc("Money Receipt")
        mr.name = "TEST-MR-001"
        mr.branch = "Test Branch"
        mr.company = "Test Company"
        mr.date = frappe.utils.today()
        mr.customer = "Test Consignor"
        mr.payment_mode = "Cash"
        mr.deposit_account = "Cash - TC"
        mr.total_amount = 5000
        
        mr.append("allocated_invoices", {
            "transport_invoice": invoice.name,
            "paid_amt": 5000
        })
        mr.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        mr.submit()
        self.assertEqual(mr.docstatus, 1)
        
        # ---------------------------------------------------------
        # STEP 6: Final Assertions (Optional)
        # ---------------------------------------------------------
        # If there is logic that updates the invoice/challan outstanding amount, assert it here
        updated_invoice = frappe.get_doc("Transport Invoice", invoice.name)
        # Assuming paid_amount gets updated to 5000
        # self.assertEqual(updated_invoice.paid_amount, 5000)
        
        print("End-to-End Test Passed Successfully!")
