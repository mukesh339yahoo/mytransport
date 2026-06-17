import frappe
import json

def run():
    doc = frappe.get_doc("DocType", "Transport Invoice")
    
    # Check if fields already exist
    existing_fields = [f.fieldname for f in doc.fields]
    
    fields_to_add = []
    if "accounting_section" not in existing_fields:
        fields_to_add.append({
            "fieldname": "accounting_section",
            "fieldtype": "Section Break",
            "label": "Accounting",
            "insert_after": "branch"
        })
    if "company" not in existing_fields:
        fields_to_add.append({
            "fieldname": "company",
            "fieldtype": "Link",
            "label": "Company",
            "options": "Company",
            "reqd": 1,
            "insert_after": "accounting_section"
        })
    if "debit_to" not in existing_fields:
        fields_to_add.append({
            "fieldname": "debit_to",
            "fieldtype": "Link",
            "label": "Debit To",
            "options": "Account",
            "reqd": 1,
            "insert_after": "company"
        })
    if "column_break_accounting" not in existing_fields:
        fields_to_add.append({
            "fieldname": "column_break_accounting",
            "fieldtype": "Column Break",
            "insert_after": "debit_to"
        })
    if "income_account" not in existing_fields:
        fields_to_add.append({
            "fieldname": "income_account",
            "fieldtype": "Link",
            "label": "Income Account",
            "options": "Account",
            "reqd": 1,
            "insert_after": "column_break_accounting"
        })

    if fields_to_add:
        # Since standard append doesn't auto-sort field_order perfectly via API sometimes without saving properly,
        # we can just append them to the fields table and let Frappe sort it if we set insert_after.
        for f in fields_to_add:
            doc.append("fields", f)
        doc.save()
        frappe.db.commit()
        print("Fields added successfully.")
    else:
        print("Fields already exist.")

