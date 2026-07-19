import frappe
import csv

def execute():
    # The user explicitly requested to remove existing data.
    print("Deleting existing territories...")
    frappe.db.sql("DELETE FROM `tabTerritory`")
    frappe.db.commit()
    
    # Recreate Root Node
    print("Recreating root node 'All Territories'...")
    frappe.flags.in_import = True # bypass nested set updates during mass insert
    
    root = frappe.new_doc("Territory")
    root.territory_name = "All Territories"
    root.is_group = 1
    root.parent_territory = ""
    root.flags.ignore_mandatory = True
    root.insert(ignore_permissions=True)

    csv_path = frappe.get_app_path("mytransport", "data", "IndianCitiesGeoData.csv")
    
    states = set()
    locations = set()
    
    print("Reading CSV and inserting records...")
    with open(csv_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            state = row['State'].strip()
            location = row['Location'].strip()
            
            if state and state not in states:
                states.add(state)
                if not frappe.db.exists("Territory", state):
                    try:
                        s_doc = frappe.new_doc("Territory")
                        s_doc.territory_name = state
                        s_doc.is_group = 1
                        s_doc.parent_territory = "All Territories"
                        s_doc.flags.ignore_mandatory = True
                        s_doc.insert(ignore_permissions=True)
                    except Exception as e:
                        print(f"Error inserting State {state}: {e}")
            
            if location and location not in locations and location != state:
                locations.add(location)
                if not frappe.db.exists("Territory", location):
                    try:
                        l_doc = frappe.new_doc("Territory")
                        l_doc.territory_name = location
                        l_doc.is_group = 0
                        l_doc.parent_territory = state
                        l_doc.flags.ignore_mandatory = True
                        l_doc.insert(ignore_permissions=True)
                    except Exception as e:
                        print(f"Error inserting Location {location}: {e}")

    frappe.flags.in_import = False
    print("Rebuilding tree...")
    from frappe.utils.nestedset import rebuild_tree
    rebuild_tree("Territory")
    
    frappe.db.commit()
    print("Territories imported successfully!")
