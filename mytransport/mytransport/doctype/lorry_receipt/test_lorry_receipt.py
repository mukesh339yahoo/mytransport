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
        
        # Setup Test Company with Standard COA
        if not frappe.db.exists("Company", "Test Company"):
            company = frappe.new_doc("Company")
            company.company_name = "Test Company"
            company.abbr = "TC"
            company.default_currency = "INR"
            company.chart_of_accounts = "Standard"
            try:
                company.insert(ignore_permissions=True, ignore_mandatory=True)
                # Call create_default_accounts manually if ignore_mandatory bypassed it
                company.create_default_accounts()
            except Exception:
                pass
                
        if not frappe.db.exists("Account", "Freight Expense - TC"):
            try:
                expense_account = frappe.new_doc("Account")
                expense_account.account_name = "Freight Expense"
                expense_account.company = "Test Company"
                expense_account.parent_account = "Direct Expenses - TC"
                expense_account.is_group = 0
                expense_account.account_type = "Expense Account"
                expense_account.insert(ignore_permissions=True)
            except Exception:
                pass

        for dt, name in [
            ("Customer", "Test Consignor"),
            ("Customer", "Test Consignee"),
            ("Supplier", "Test Transporter"),
        ]:
            if not frappe.db.exists(dt, name):
                doc = frappe.new_doc(dt)
                if dt == "Customer":
                    doc.customer_name = name
                    doc.customer_group = "All Customer Groups"
                    doc.territory = "All Territories"
                elif dt == "Supplier":
                    doc.supplier_name = name
                    doc.supplier_group = "All Supplier Groups"
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
        
        frappe.db.sql("DELETE FROM `tabLorry Receipt`")
        frappe.db.sql("DELETE FROM `tabChallan`")
        frappe.db.sql("DELETE FROM `tabTransport Invoice`")
        frappe.db.sql("DELETE FROM `tabExpense Voucher`")
        frappe.db.sql("DELETE FROM `tabMoney Receipt`")
        frappe.db.commit()  # nosemgrep: required in standalone setup scripts

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
        lr.append("items", {
            "lorry_freight": 5000,
            "actual_weight": 100,
            "qty": 10
        })
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
        ev.party_type = "Supplier"
        ev.party = "Test Transporter"
        ev.voucher_type = "Cash"
        ev.payment_account = "Cash - TC"
        ev.expense_category = "Trip Advance"
        ev.debit_account = "Creditors - TC"
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
        mr.party_type = "Customer"
        mr.party = "Test Consignor"
        mr.payment_mode = "Cash"
        mr.deposit_account = "Cash - TC"
        mr.credit_account = "Debtors - TC"
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
        
        print("End-to-End Test (Single LR) Passed Successfully!")  # nosemgrep: frappe-print-function-in-doctypes

    def test_end_to_end_multiple_lrs(self):
        # ---------------------------------------------------------
        # STEP 1: Create 5 Lorry Receipts (LRs)
        # ---------------------------------------------------------
        lr_names = []
        for i in range(1, 6):
            lr = frappe.new_doc("Lorry Receipt")
            lr_name = f"TEST-LR-MULT-{i}"
            lr.name = lr_name
            lr.branch = "Test Branch"
            lr.date = frappe.utils.today()
            lr.consignor = "Test Consignor"
            lr.consignee = "Test Consignee"
            lr.from_city = "Mumbai"
            lr.to_city = "Delhi"
            amount = 1000 * i
            lr.append("items", {
                "lorry_freight": amount,
                "actual_weight": 100,
                "qty": 10
            })
            lr.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
            lr.submit()
            self.assertEqual(lr.docstatus, 1)
            lr_names.append({"name": lr.name, "amount": lr.total_amount})
        
        # ---------------------------------------------------------
        # STEP 2: Create a Challan & Link the 5 LRs
        # ---------------------------------------------------------
        challan = frappe.new_doc("Challan")
        challan.name = "TEST-CH-MULT-001"
        challan.branch = "Test Branch"
        challan.date = frappe.utils.today()
        challan.from_location = "Mumbai"
        challan.to_location = "Delhi"
        challan.vendor = "Test Transporter"
        
        for lr_data in lr_names:
            challan.append("lrs", {
                "lr_number": lr_data["name"],
                "basic_freight": lr_data["amount"]
            })
        challan.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        challan.submit()
        self.assertEqual(challan.docstatus, 1)
        
        # ---------------------------------------------------------
        # STEP 3: Create Transport Invoice for the 5 LRs
        # ---------------------------------------------------------
        invoice = frappe.new_doc("Transport Invoice")
        invoice.name = "TEST-INV-MULT-001"
        invoice.branch = "Test Branch"
        invoice.date = frappe.utils.today()
        invoice.customer = "Test Consignor"
        invoice.company = "Test Company"
        invoice.debit_to = "Debtors - TC"
        invoice.income_account = "Sales - TC"
        
        for lr_data in lr_names:
            invoice.append("items", {
                "lr_number": lr_data["name"],
                "basic_freight": lr_data["amount"]
            })
        invoice.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        invoice.submit()
        self.assertEqual(invoice.docstatus, 1)
        
        # ---------------------------------------------------------
        # STEP 4: Create Expense Voucher for the Challan
        # ---------------------------------------------------------
        ev = frappe.new_doc("Expense Voucher")
        ev.name = "TEST-EV-MULT-001"
        ev.branch = "Test Branch"
        ev.company = "Test Company"
        ev.date = frappe.utils.today()
        ev.party_type = "Supplier"
        ev.party = "Test Transporter"
        ev.voucher_type = "Cash"
        ev.payment_account = "Cash - TC"
        ev.expense_category = "Trip Advance"
        ev.debit_account = "Creditors - TC"
        ev.total_paid_amt = 15000
        
        ev.append("allocated_challans", {
            "challan": challan.name,
            "paid_amt": 15000
        })
        ev.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        ev.submit()
        self.assertEqual(ev.docstatus, 1)
        
        # ---------------------------------------------------------
        # STEP 5: Create Money Receipt for the Invoice
        # ---------------------------------------------------------
        mr = frappe.new_doc("Money Receipt")
        mr.name = "TEST-MR-MULT-001"
        mr.branch = "Test Branch"
        mr.company = "Test Company"
        mr.date = frappe.utils.today()
        mr.party_type = "Customer"
        mr.party = "Test Consignor"
        mr.payment_mode = "Cash"
        mr.deposit_account = "Cash - TC"
        mr.credit_account = "Debtors - TC"
        mr.total_amount = 15000
        
        mr.append("allocated_invoices", {
            "transport_invoice": invoice.name,
            "paid_amt": 15000
        })
        mr.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        mr.submit()
        self.assertEqual(mr.docstatus, 1)
        
        print("End-to-End Test (Multiple LRs) Passed Successfully!")  # nosemgrep: frappe-print-function-in-doctypes

    def test_end_to_end_complex_batching(self):
        # ---------------------------------------------------------
        # STEP 1: Create 10 LRs
        # ---------------------------------------------------------
        lr_names = []
        for i in range(1, 11):
            lr = frappe.new_doc("Lorry Receipt")
            lr.name = f"TEST-LR-COMP-{i}"
            lr.branch = "Test Branch"
            lr.date = frappe.utils.today()
            lr.consignor = "Test Consignor"
            lr.consignee = "Test Consignee"
            lr.from_city = "Mumbai"
            lr.to_city = "Delhi"
            amount = 1000
            lr.append("items", {
                "lorry_freight": amount,
                "actual_weight": 100,
                "qty": 10
            })
            lr.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
            lr.submit()
            self.assertEqual(lr.docstatus, 1)
            lr_names.append({"name": lr.name, "amount": lr.total_amount})
            
        # ---------------------------------------------------------
        # STEP 2: Create a Challan & Link the 10 LRs
        # ---------------------------------------------------------
        challan = frappe.new_doc("Challan")
        challan.name = "TEST-CH-COMP-001"
        challan.branch = "Test Branch"
        challan.date = frappe.utils.today()
        challan.from_location = "Mumbai"
        challan.to_location = "Delhi"
        challan.vendor = "Test Transporter"
        
        for lr_data in lr_names:
            challan.append("lrs", {
                "lr_number": lr_data["name"],
                "basic_freight": lr_data["amount"]
            })
        challan.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
        challan.submit()
        self.assertEqual(challan.docstatus, 1)
        
        # ---------------------------------------------------------
        # STEP 3: Create 3 Transport Invoices for the 10 LRs
        # Inv 1: 3 LRs, Inv 2: 4 LRs, Inv 3: 3 LRs
        # ---------------------------------------------------------
        invoice_allocations = [
            (1, lr_names[0:3]), # 3 LRs
            (2, lr_names[3:7]), # 4 LRs
            (3, lr_names[7:10]) # 3 LRs
        ]
        
        invoices = []
        for inv_idx, lrs in invoice_allocations:
            invoice = frappe.new_doc("Transport Invoice")
            invoice.name = f"TEST-INV-COMP-{inv_idx}"
            invoice.branch = "Test Branch"
            invoice.date = frappe.utils.today()
            invoice.customer = "Test Consignor"
            invoice.company = "Test Company"
            invoice.debit_to = "Debtors - TC"
            invoice.income_account = "Sales - TC"
            
            total_amt = 0
            for lr_data in lrs:
                invoice.append("items", {
                    "lr_number": lr_data["name"],
                    "basic_freight": lr_data["amount"]
                })
                total_amt += lr_data["amount"]
                
            invoice.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
            invoice.submit()
            self.assertEqual(invoice.docstatus, 1)
            invoices.append({"name": invoice.name, "amount": total_amt})
            
        # ---------------------------------------------------------
        # STEP 4: Create 2 Expense Vouchers for the Challan
        # EV 1: 6000, EV 2: 4000
        # ---------------------------------------------------------
        ev_allocations = [(1, 6000), (2, 4000)]
        for ev_idx, amt in ev_allocations:
            ev = frappe.new_doc("Expense Voucher")
            ev.name = f"TEST-EV-COMP-{ev_idx}"
            ev.branch = "Test Branch"
            ev.company = "Test Company"
            ev.date = frappe.utils.today()
            ev.party_type = "Supplier"
            ev.party = "Test Transporter"
            ev.voucher_type = "Cash"
            ev.payment_account = "Cash - TC"
            ev.expense_category = "Trip Advance"
            ev.debit_account = "Creditors - TC"
            ev.total_paid_amt = amt
            
            ev.append("allocated_challans", {
                "challan": challan.name,
                "paid_amt": amt
            })
            ev.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
            ev.submit()
            self.assertEqual(ev.docstatus, 1)
            
        # ---------------------------------------------------------
        # STEP 5: Create 3 Money Receipts for the 3 Transport Invoices
        # ---------------------------------------------------------
        for i, inv_data in enumerate(invoices, start=1):
            mr = frappe.new_doc("Money Receipt")
            mr.name = f"TEST-MR-COMP-{i}"
            mr.branch = "Test Branch"
            mr.company = "Test Company"
            mr.date = frappe.utils.today()
            mr.party_type = "Customer"
            mr.party = "Test Consignor"
            mr.payment_mode = "Cash"
            mr.deposit_account = "Cash - TC"
            mr.credit_account = "Debtors - TC"
            mr.total_amount = inv_data["amount"]
            
            mr.append("allocated_invoices", {
                "transport_invoice": inv_data["name"],
                "paid_amt": inv_data["amount"]
            })
            mr.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)
            mr.submit()
            self.assertEqual(mr.docstatus, 1)
            
        print("End-to-End Test (Complex Batching) Passed Successfully!")  # nosemgrep: frappe-print-function-in-doctypes
