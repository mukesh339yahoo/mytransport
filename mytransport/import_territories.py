import frappe
import requests

def run():
    url = "https://raw.githubusercontent.com/sab99r/Indian-States-And-Districts/master/states-and-districts.json"
    print("Fetching territory data...")
    response = requests.get(url)
    data = response.json()
    
    # Ensure "All Territories" exists just in case
    if not frappe.db.exists("Territory", "All Territories"):
        frappe.get_doc({
            "doctype": "Territory",
            "territory_name": "All Territories",
            "is_group": 1
        }).insert(ignore_permissions=True)

    # Ensure "India" exists under "All Territories"
    if not frappe.db.exists("Territory", "India"):
        frappe.get_doc({
            "doctype": "Territory",
            "territory_name": "India",
            "parent_territory": "All Territories",
            "is_group": 1
        }).insert(ignore_permissions=True)
        frappe.db.commit()  # nosemgrep: required in standalone setup scripts
        print("Created India territory")

    # Iterate states
    for state_data in data.get("states", []):
        state_name = state_data.get("state")
        if not state_name: continue
        
        # In Frappe, the ID is the territory name itself.
        if not frappe.db.exists("Territory", state_name):
            try:
                frappe.get_doc({
                    "doctype": "Territory",
                    "territory_name": state_name,
                    "parent_territory": "India",
                    "is_group": 1
                }).insert(ignore_permissions=True)
                print(f"Created state: {state_name}")
            except frappe.exceptions.DuplicateEntryError:
                pass
            
        for district in state_data.get("districts", []):
            if not frappe.db.exists("Territory", district):
                try:
                    frappe.get_doc({
                        "doctype": "Territory",
                        "territory_name": district,
                        "parent_territory": state_name,
                        "is_group": 0
                    }).insert(ignore_permissions=True)
                except frappe.exceptions.DuplicateEntryError:
                    # Handle duplicate territory names across different states
                    district_unique = f"{district} ({state_name})"
                    if not frappe.db.exists("Territory", district_unique):
                        frappe.get_doc({
                            "doctype": "Territory",
                            "territory_name": district_unique,
                            "parent_territory": state_name,
                            "is_group": 0
                        }).insert(ignore_permissions=True)
        
        frappe.db.commit()  # nosemgrep: required in standalone setup scripts
    
    print("Done importing territories.")
