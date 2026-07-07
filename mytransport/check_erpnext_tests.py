import frappe

def check():
    frappe.init(site="mytransport.localhost")
    frappe.connect()

    try:
        from erpnext.tests.utils import create_test_company
        print("create_test_company found in erpnext.tests.utils!")
    except ImportError:
        print("create_test_company NOT found.")

if __name__ == "__main__":
    check()
