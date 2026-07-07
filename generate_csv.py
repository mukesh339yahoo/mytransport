import json
import csv
import os

def generate_layout_csv(doctype_name, folder_name):
    base_dir = '/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport'
    json_path = os.path.join(base_dir, f'mytransport/mytransport/doctype/{folder_name}/{folder_name}.json')
    csv_path = os.path.join(base_dir, f'{folder_name}_layout.csv')
    
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    # Frappe v14+ uses field_order to determine actual sequence
    field_order = data.get('field_order', [])
    fields_dict = {f.get('fieldname'): f for f in data.get('fields', [])}
    
    # Sort fields according to field_order
    ordered_fields = []
    for fname in field_order:
        if fname in fields_dict:
            ordered_fields.append(fields_dict[fname])
    
    sections = []
    current_section = []
    current_column = []
    
    for field in ordered_fields:
        ftype = field.get('fieldtype')
        fname = field.get('fieldname')
        
        if ftype == 'Section Break':
            if current_column:
                current_section.append(current_column)
            if current_section:
                sections.append(current_section)
            current_section = []
            current_column = [f"--- SECTION: {field.get('label') or fname} ---"]
        elif ftype == 'Column Break':
            if current_column:
                current_section.append(current_column)
            current_column = []
        else:
            if not current_column and not current_section and not sections:
                current_column = ["--- SECTION: Default ---"]
            current_column.append(fname)
            
    if current_column:
        current_section.append(current_column)
    if current_section:
        sections.append(current_section)
        
    csv_rows = []
    max_cols = max(len(sec) for sec in sections) if sections else 2
    header = [f"column{i+1}" for i in range(max_cols)]
    csv_rows.append(header)
    
    for sec in sections:
        max_rows = max(len(col) for col in sec) if sec else 0
        for i in range(max_rows):
            row = []
            for col in sec:
                if i < len(col):
                    row.append(col[i])
                else:
                    row.append("")
            while len(row) < max_cols:
                row.append("")
            csv_rows.append(row)
            
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_rows)
        
    print(f"Generated {csv_path}")

if __name__ == '__main__':
    doctypes = [
        ("Lorry Receipt", "lorry_receipt"),
        ("Transport Invoice", "transport_invoice"),
        ("Money Receipt", "money_receipt"),
        ("Expense Voucher", "expense_voucher")
    ]
    
    for dt_name, folder_name in doctypes:
        generate_layout_csv(dt_name, folder_name)
