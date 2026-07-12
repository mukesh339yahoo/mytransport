import frappe

def execute():
    modes = ["Bank", "Cheque", "UPI", "Cash"]
    for mode in modes:
        if not frappe.db.exists("Mode of Payment", mode):
            doc = frappe.new_doc("Mode of Payment")
            doc.mode_of_payment = mode
            doc.type = "Bank" if mode != "Cash" else "Cash"
            doc.insert(ignore_permissions=True)
            print(f"Created Mode of Payment: {mode}")
        else:
            print(f"Mode of Payment {mode} already exists")
    frappe.db.commit()  # nosemgrep: required in standalone setup scripts

