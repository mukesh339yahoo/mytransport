import frappe

def sync_counters():
    doctypes = [
        ("Lorry Receipt", "lr_number"),
        ("Challan", "challan_number"),
        ("Transport Invoice", "bill_no"),
        ("Money Receipt", "mr_no"),
        ("Expense Voucher", "voucher_no")
    ]
    
    for dt, fn in doctypes:
        # Get max number per branch
        # Bill numbers might be formatted, but usually they are sequential integers in our setup.
        # We try to cast to unsigned and get the max.
        query = f"""
            SELECT branch, MAX(CAST(TRIM({fn}) AS UNSIGNED)) as max_num
            FROM `tab{dt}`
            WHERE docstatus < 2 AND branch IS NOT NULL
            GROUP BY branch
        """
        results = frappe.db.sql(query, as_dict=1)
        
        for row in results:
            if not row.max_num:
                continue
            
            # Find the financial year. Since we don't have the exact date of the max invoice easily in this simple query,
            # we'll just query the Branch Numbering Settings directly for this branch and doctype and update all years where current < max.
            settings = frappe.db.sql(
                "SELECT name, current_number FROM `tabBranch Numbering Settings` WHERE name LIKE %s", 
                (f"{row.branch}-{dt}-%",), 
                as_dict=1
            )
            
            for s in settings:
                if row.max_num > (s.current_number or 0):
                    print(f"Updating {s.name} from {s.current_number} to {row.max_num}")
                    frappe.db.set_value("Branch Numbering Settings", s.name, "current_number", int(row.max_num))
                    frappe.db.commit()  # nosemgrep: required in standalone setup scripts

sync_counters()
