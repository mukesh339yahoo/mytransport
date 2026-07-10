import json
import csv

def rebuild_layout():
    json_path = '/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/transport_invoice/transport_invoice.json'
    csv_path = '/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/transport_invoice_layout.csv'

    with open(json_path, 'r') as f:
        doc = json.load(f)

    # Store all existing fields by fieldname for easy lookup
    # We will reuse Section Breaks and Column Breaks if possible, but mostly we care about data fields.
    existing_fields = {f.get('fieldname'): f for f in doc.get('fields', [])}

    # Helper to generate unique fieldnames for layout elements if needed
    layout_counter = 1
    def get_new_break(ftype, label=None):
        nonlocal layout_counter
        prefix = "section_break" if ftype == "Section Break" else "column_break"
        fname = f"{prefix}_{layout_counter}"
        layout_counter += 1
        # ensure no collision (highly unlikely but safe)
        while fname in existing_fields:
            fname = f"{prefix}_{layout_counter}"
            layout_counter += 1
        
        f = {"fieldname": fname, "fieldtype": ftype}
        if label:
            f["label"] = label
        return f

    # Parse CSV into: [ { section_name: str, columns: [ [field1, field2], [field3], ... ] } ]
    sections = []
    current_section = None

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader) # skip column1, column2...
        
        for row in reader:
            if not row:
                continue
                
            first_cell = row[0].strip()
            
            # Check if it's a section header
            if first_cell.startswith("--- SECTION:") and first_cell.endswith("---"):
                sec_name = first_cell.replace("--- SECTION:", "").replace("---", "").strip()
                current_section = {"name": sec_name, "columns": []}
                # Initialize columns based on how many elements are in this row (or just handle dynamically)
                sections.append(current_section)
                continue
            
            if not current_section:
                # Should not happen with valid CSV from our generator
                current_section = {"name": "Default", "columns": []}
                sections.append(current_section)
                
            # Add fields to their respective columns
            for col_idx, cell in enumerate(row):
                fname = cell.strip()
                if fname:
                    # ensure columns list is long enough
                    while len(current_section["columns"]) <= col_idx:
                        current_section["columns"].append([])
                    
                    current_section["columns"][col_idx].append(fname)

    # Now rebuild the fields array
    new_fields = []
    
    # We want to reuse existing section/column breaks if possible to prevent diff noise,
    # but since the layout changed significantly, creating new ones is safer for column breaks.
    # We will try to find an existing section break by label.
    
    for sec in sections:
        sec_name = sec["name"]
        
        # Add Section Break (unless it's the very first section and named "Default")
        if not (len(new_fields) == 0 and sec_name == "Default"):
            # Try to find an existing section break with this label
            existing_sec = next((f for f in existing_fields.values() if f.get("fieldtype") == "Section Break" and f.get("label") == sec_name), None)
            if existing_sec:
                new_fields.append(existing_sec)
                # mark as used so we don't accidentally reuse it for something else
                del existing_fields[existing_sec['fieldname']]
            else:
                new_fields.append(get_new_break("Section Break", sec_name))
                
        # Now add columns
        for col_idx, col_fields in enumerate(sec["columns"]):
            if col_idx > 0:
                # Need a column break before the 2nd, 3rd, etc. column
                new_fields.append(get_new_break("Column Break"))
                
            for fname in col_fields:
                if fname in existing_fields:
                    new_fields.append(existing_fields[fname])
                    del existing_fields[fname]
                else:
                    # If field doesn't exist, we skip or print warning
                    print(f"WARNING: Field '{fname}' found in CSV but not in original JSON schema.")

    # There might be some fields left in existing_fields that were NOT in the CSV (e.g. old column breaks, hidden fields).
    # We should definitely KEEP hidden system fields or things that the user might have accidentally dropped from the CSV,
    # but we drop old Section/Column breaks.
    for fname, f in existing_fields.items():
        if f.get("fieldtype") not in ["Section Break", "Column Break"]:
            # Append orphaned data fields to the bottom so data is not lost
            print(f"WARNING: Field '{fname}' was not in CSV. Appending to bottom of schema.")
            new_fields.append(f)

    # Update JSON
    doc['fields'] = new_fields
    doc['field_order'] = [f['fieldname'] for f in new_fields]
    
    with open(json_path, 'w') as f:
        json.dump(doc, f, indent=1)
        f.write('\n')

    print(f"Successfully rebuilt challan.json with {len(new_fields)} fields.")

if __name__ == '__main__':
    rebuild_layout()
