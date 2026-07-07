import frappe

def check():
    frappe.init(site="mytransport.localhost")
    frappe.connect()

    for dt in ["Company", "Customer", "Supplier", "Territory", "Account"]:
        val = frappe.db.get_value(dt)
        print(f"{dt}: {val}")

if __name__ == "__main__":
    check()
