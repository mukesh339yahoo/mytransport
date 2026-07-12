import frappe

def run():
    if not frappe.db.exists("DocType", "Hired Vehicle"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "Mytransport",
            "custom": 0,
            "name": "Hired Vehicle",
            "naming_rule": "By fieldname",
            "autoname": "field:vehicle_number",
            "title_field": "vehicle_number",
            "search_fields": "owner_name",
            "allow_attach": 1,
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1, "write": 1, "create": 1, "delete": 1,
                    "submit": 0, "cancel": 0, "amend": 0
                }
            ],
            "fields": [
                {
                    "fieldname": "vehicle_number",
                    "label": "Vehicle Number",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1
                },
                {
                    "fieldname": "vehicle_type",
                    "label": "Vehicle Type",
                    "fieldtype": "Data",
                    "in_list_view": 1
                },
                {
                    "fieldname": "owner_details",
                    "label": "Owner Details",
                    "fieldtype": "Section Break"
                },
                {
                    "fieldname": "owner_name",
                    "label": "Owner Name",
                    "fieldtype": "Data",
                    "in_list_view": 1
                },
                {
                    "fieldname": "owner_mobile_no",
                    "label": "Owner Mobile No",
                    "fieldtype": "Data"
                },
                {
                    "fieldname": "owner_phone_no",
                    "label": "Owner Phone No",
                    "fieldtype": "Data"
                },
                {
                    "fieldname": "owner_address",
                    "label": "Owner Address",
                    "fieldtype": "Small Text"
                },
                {
                    "fieldname": "owner_pan_no",
                    "label": "Owner PAN No",
                    "fieldtype": "Data"
                },
                {
                    "fieldname": "tds_exemption",
                    "label": "TDS Exemption",
                    "fieldtype": "Check",
                    "default": "0"
                },
                {
                    "fieldname": "driver_details",
                    "label": "Driver Details",
                    "fieldtype": "Section Break"
                },
                {
                    "fieldname": "driver_name",
                    "label": "Driver Name",
                    "fieldtype": "Data",
                    "in_list_view": 1
                },
                {
                    "fieldname": "driver_mobile_no",
                    "label": "Driver Mobile No",
                    "fieldtype": "Data"
                }
            ]
        })
        doc.insert()
        frappe.db.commit()  # nosemgrep: required in standalone setup scripts
        print("Hired Vehicle Doctype created successfully.")
    else:
        print("Hired Vehicle Doctype already exists.")
