import frappe

def check():
    frappe.init(site="mytransport.localhost")
    frappe.connect()

    doctypes = ["Lorry Receipt", "Challan", "Transport Invoice", "Expense Voucher", "Money Receipt"]
    for dt in doctypes:
        meta = frappe.get_meta(dt)
        mandatory_fields = [f.fieldname for f in meta.fields if f.reqd]
        print(f"{dt}: {mandatory_fields}")

if __name__ == "__main__":
    check()
