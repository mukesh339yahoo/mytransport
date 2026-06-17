import frappe
def run():
    frappe.flags.in_test = True
    doc = frappe.get_doc("DocType", "TDS Declaration Item")
    doc.custom = 0
    doc.save()
    print("Made TDS Declaration Item standard")
