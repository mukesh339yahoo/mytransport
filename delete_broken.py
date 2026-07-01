import frappe

def execute():
    for dt in ["Expense Voucher", "Money Receipt"]:
        bad_name = "EV-.YYYY.-.#####" if dt == "Expense Voucher" else "MR-.YYYY.-.#####"
        if frappe.db.exists(dt, bad_name):
            try:
                frappe.delete_doc(dt, bad_name, force=1)
                print(f"Deleted broken {dt} {bad_name}")
            except Exception as e:
                print(f"Failed to delete {dt}: {e}")
