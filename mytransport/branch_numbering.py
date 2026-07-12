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
    
    # Use direct SQL update to bypass cache and avoid race conditions
    frappe.db.sql("""
        UPDATE `tabBranch Numbering Settings`
        SET current_number = COALESCE(current_number, 0) + 1
        WHERE name = %s
    """, settings_name)
    
    next_number = frappe.db.sql("SELECT current_number FROM `tabBranch Numbering Settings` WHERE name = %s", settings_name)[0][0]
    
    return str(next_number)

@frappe.whitelist()
def peek_next_branch_number(branch, document_type, date):
    if not branch or not date:
        return ""
        
    if isinstance(date, str):
        date = frappe.utils.getdate(date)
        
    financial_year = frappe.db.get_value("Fiscal Year", 
        {"year_start_date": ("<=", date), "year_end_date": (">=", date)}, 
        "name"
    )
    
    if not financial_year:
        return ""
        
    settings_name = f"{branch}-{document_type}-{financial_year}"
    
    if not frappe.db.exists("Branch Numbering Settings", settings_name):
        return ""
        
    current_number = frappe.db.get_value("Branch Numbering Settings", settings_name, "current_number")
    return (current_number or 0) + 1

def update_branch_number_counter(branch, document_type, date, assigned_number):
    if not assigned_number:
        return
        
    try:
        assigned_int = int(str(assigned_number).strip())
    except ValueError:
        return
        
    if isinstance(date, str):
        date = frappe.utils.getdate(date)
        
    financial_year = frappe.db.get_value("Fiscal Year", 
        {"year_start_date": ("<=", date), "year_end_date": (">=", date)}, 
        "name"
    )
    
    if not financial_year:
        return
        
    settings_name = f"{branch}-{document_type}-{financial_year}"
    
    if frappe.db.exists("Branch Numbering Settings", settings_name):
        frappe.db.sql("SELECT name FROM `tabBranch Numbering Settings` WHERE name=%s FOR UPDATE", settings_name)
        current_number = frappe.db.get_value("Branch Numbering Settings", settings_name, "current_number") or 0
        if assigned_int > current_number:
            frappe.db.set_value("Branch Numbering Settings", settings_name, "current_number", assigned_int)

@frappe.whitelist()
def get_default_branch():
	user = frappe.session.user
	# First check user permissions directly to bypass Administrator limitations
	default_branch = frappe.db.get_value("User Permission", {
		"user": user,
		"allow": "Branch",
		"is_default": 1
	}, "for_value")
	
	if not default_branch:
		# Fallback to standard defaults
		default_branch = frappe.db.get_default("Branch") or frappe.db.get_default("branch")
		
	return default_branch
