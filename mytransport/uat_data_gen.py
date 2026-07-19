import frappe

def get_or_create_customer(name):
    if not frappe.db.exists("Customer", name):
        doc = frappe.new_doc("Customer")
        doc.customer_name = name
        doc.customer_group = frappe.db.get_value("Customer Group", {}) or "Commercial"
        doc.territory = frappe.db.get_value("Territory", {}) or "All Territories"
        doc.insert(ignore_permissions=True, ignore_mandatory=True)
    return name

def get_or_create_supplier(name):
    if not frappe.db.exists("Supplier", name):
        doc = frappe.new_doc("Supplier")
        doc.supplier_name = name
        doc.supplier_group = frappe.db.get_value("Supplier Group", {}) or "Services"
        doc.insert(ignore_permissions=True, ignore_mandatory=True)
    return name

def execute():
    """
    End-to-End User Acceptance Test (UAT) Data Generation Script
    This script emulates an end-user creating documents via the UI.
    It inserts and submits documents natively, enforcing all standard validations.
    """
    print("Initializing UAT Data Generation...")

    # 1. Fetch mandatory default master data
    company = frappe.db.get_value("Company", {})
    if not company:
        frappe.throw("A Company is required in the system to run UAT.")

    branch = frappe.db.get_value("Branch", {}) 
    if not branch:
        b = frappe.new_doc("Branch")
        b.branch = "UAT Branch"
        b.insert(ignore_permissions=True, ignore_mandatory=True)
        branch = b.name

    consignor = get_or_create_customer("UAT Consignor")
    consignee = get_or_create_customer("UAT Consignee")
    transporter = get_or_create_supplier("UAT Transporter")

    cities = frappe.db.get_all("Territory", filters={"is_group": 0}, limit=2, pluck="name")
    if len(cities) < 2:
        frappe.throw("Please ensure at least two non-group Territories exist.")
    from_city, to_city = cities[0], cities[1]

    vehicle = frappe.db.get_value("Hired Vehicle", {})
    if not vehicle:
        v = frappe.new_doc("Hired Vehicle")
        v.vehicle_number = "MH-01-UAT-1234"
        v.vendor = transporter
        v.driver_name = "UAT Driver"
        v.insert(ignore_permissions=True, ignore_mandatory=True)
        vehicle = v.name

    # Helper to fetch accounts for financial docs
    def get_account(acct_type):
        acc = frappe.db.get_value("Account", {"account_type": acct_type, "company": company, "is_group": 0})
        if not acc:
            acc = frappe.db.get_value("Account", {"company": company, "is_group": 0})
        return acc

    cash_acc = get_account("Cash")
    receivable_acc = get_account("Receivable")
    payable_acc = get_account("Payable")
    income_acc = get_account("Income Account")

    try:
        # STEP 1: Lorry Receipt
        print("\nStep 1: Emulating Lorry Receipt creation...")
        lr = frappe.new_doc("Lorry Receipt")
        lr.branch = branch
        lr.date = frappe.utils.today()
        lr.payment_terms = "To Pay"
        lr.consignor = consignor
        lr.consignee = consignee
        lr.from_city = from_city
        lr.to_city = to_city
        lr.append("items", {
            "article": "Boxes",
            "qty": 10,
            "actual_weight": 100,
            "charged_weight": 100,
            "rate": 50,
            "lorry_freight": 5000,
        })
        lr.basic_freight = 5000
        lr.total_amount = 5000
        lr.insert()  # No ignore flags, emulates user save
        lr.submit()  # Emulates user submit
        print(f"✅ Success! Created Lorry Receipt: {lr.name}")

        # STEP 2: Challan
        print("\nStep 2: Emulating Challan creation (Linking LR)...")
        challan = frappe.new_doc("Challan")
        challan.branch = branch
        challan.date = frappe.utils.today()
        challan.from_location = from_city
        challan.to_location = to_city
        challan.vehicle_number = vehicle
        challan.vendor = transporter
        challan.driver_name = "UAT Driver"
        challan.total_freight = 4000
        challan.advance_amount = 4000
        challan.append("lrs", {
            "lr_number": lr.name,
            "basic_freight": 5000,
            "total_freight": 5000
        })
        challan.insert()
        challan.submit()
        print(f"✅ Success! Created Challan: {challan.name}")

        # STEP 3: Transport Invoice
        print("\nStep 3: Emulating Transport Invoice creation...")
        if not receivable_acc or not income_acc:
            print("⚠️ Skipping Invoice: Could not find default Receivable/Income accounts for Company.")
            invoice_name = None
        else:
            invoice = frappe.new_doc("Transport Invoice")
            invoice.branch = branch
            invoice.company = company
            invoice.date = frappe.utils.today()
            invoice.customer = consignor
            invoice.debit_to = receivable_acc
            invoice.income_account = income_acc
            invoice.append("items", {
                "lr_number": lr.name,
                "basic_freight": 5000,
                "total_amount": 5000
            })
            invoice.insert()
            invoice.submit()
            invoice_name = invoice.name
            print(f"✅ Success! Created Transport Invoice: {invoice.name}")

        # STEP 4: Expense Voucher (For Challan)
        print("\nStep 4: Emulating Expense Voucher creation...")
        if not cash_acc or not payable_acc:
            print("⚠️ Skipping Expense Voucher: Could not find default Cash/Payable accounts.")
        else:
            ev = frappe.new_doc("Expense Voucher")
            ev.branch = branch
            ev.company = company
            ev.date = frappe.utils.today()
            ev.party_type = "Supplier"
            ev.search_party = transporter
            ev.party = transporter
            ev.voucher_type = "Cash"
            ev.payment_account = cash_acc
            ev.debit_account = payable_acc
            ev.total_paid_amt = 4000
            ev.append("allocated_challans", {
                "challan": challan.name,
                "paid_amt": 4000
            })
            ev.insert()
            ev.submit()
            print(f"✅ Success! Created Expense Voucher: {ev.name}")

        # STEP 5: Money Receipt (For Invoice)
        print("\nStep 5: Emulating Money Receipt creation...")
        if not invoice_name or not cash_acc or not receivable_acc:
            print("⚠️ Skipping Money Receipt: Missing Invoice or Accounts.")
        else:
            mr = frappe.new_doc("Money Receipt")
            mr.branch = branch
            mr.company = company
            mr.date = frappe.utils.today()
            mr.party_type = "Customer"
            mr.search_party = consignor
            mr.party = consignor
            mr.payment_mode = "Cash"
            mr.deposit_account = cash_acc
            mr.credit_account = receivable_acc
            mr.total_amount = 5000
            mr.append("allocated_invoices", {
                "transport_invoice": invoice_name,
                "allocated_amount": 5000
            })
            mr.insert()
            mr.submit()
            print(f"✅ Success! Created Money Receipt: {mr.name}")

        frappe.db.commit()
        print("\n🎉 UAT End-to-End Cycle Completed Successfully!")

    except Exception as e:
        frappe.db.rollback()
        print(f"\n❌ UAT Failed: {str(e)}")
        raise e
