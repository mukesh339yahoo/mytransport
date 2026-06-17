import frappe
def run():
    frappe.flags.in_test = True
    frappe.get_doc("DocType", "TDS Declaration Item").save()
    print("Saved")
