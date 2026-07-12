import frappe

def run():
    frappe.init(site="mytransport.localhost")
    frappe.connect()

    frappe.db.sql("DELETE FROM `tabCompany` WHERE name='Test Company 2'")
    frappe.db.commit()  # nosemgrep: required in standalone setup scripts

    try:
        company = frappe.new_doc("Company")
        company.company_name = "Test Company 2"
        company.abbr = "TC2"
        company.default_currency = "INR"
        company.chart_of_accounts = "Standard"
        company.insert(ignore_permissions=True)
        
        accounts = frappe.get_all("Account", filters={"company": "Test Company 2"}, fields=["name", "account_type", "root_type", "parent_account"])
        print(f"Created {len(accounts)} accounts for Test Company 2")
        for acc in accounts:
            if "Cash" in acc.name or "Sales" in acc.name or "Debtor" in acc.name or "Expense" in acc.name:
                print(acc)
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        frappe.db.rollback()

if __name__ == "__main__":
    run()
