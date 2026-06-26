import frappe

def get_next_branch_number(branch, document_type, date):
    if not branch or not date:
        frappe.throw(f"Branch and Date are mandatory to generate {document_type} number.")
    
    # Simple logic to determine financial year from date. Assuming April to March.
    if isinstance(date, str):
        date = frappe.utils.getdate(date)
    else:
        date = date
        
    financial_year = frappe.db.get_value("Fiscal Year", 
        {"year_start_date": ("<=", date), "year_end_date": (">=", date)}, 
        "name"
    )
    
    if not financial_year:
        frappe.throw(f"No Fiscal Year configured in ERPNext for the date {date}")
    
    settings_name = f"{branch}-{document_type}-{financial_year}"
    
    if not frappe.db.exists("Branch Numbering Settings", settings_name):
        frappe.throw(f"Numbering sequence not configured for Branch '{branch}' and Year '{financial_year}' for {document_type}. Please configure it in Branch Numbering Settings.")
    
    # Lock the row for update to prevent race conditions
    frappe.db.sql("SELECT name FROM `tabBranch Numbering Settings` WHERE name=%s FOR UPDATE", settings_name)
    
    current_number = frappe.db.get_value("Branch Numbering Settings", settings_name, "current_number")
    next_number = (current_number or 0) + 1
    
    frappe.db.set_value("Branch Numbering Settings", settings_name, "current_number", next_number)
    
    return next_number
