import os

py_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/transport_invoice/transport_invoice.py"
js_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/transport_invoice/transport_invoice.js"

with open(py_path, "r") as f:
    py_code = f.read()

# Replace the fields list in python
old_fields = 'fields=["name"]'
new_fields = '''fields=[
            "name", "date", "from_city", "to_city", "total_packages", "total_weight",
            "basic_freight", "bilty_charges", "detention_narration", "detention_charges",
            "hamali_narration", "hamali_charges", "other_charge_narration", "other_charges"
        ]'''
py_code = py_code.replace(old_fields, new_fields)

with open(py_path, "w") as f:
    f.write(py_code)


with open(js_path, "r") as f:
    js_code = f.read()

# Replace the row assignment in js
old_js = '''					r.message.forEach(function(lr) {
						let row = frm.add_child("items");
						row.lr_number = lr.name;
					});'''

new_js = '''					r.message.forEach(function(lr) {
						let row = frm.add_child("items");
						row.lr_number = lr.name;
						row.lr_date = lr.date;
						row.from_city = lr.from_city;
						row.to_city = lr.to_city;
						row.total_packages = lr.total_packages;
						row.total_weight = lr.total_weight;
						row.basic_freight = lr.basic_freight;
						row.st_charge = lr.bilty_charges;
						row.detention_narration = lr.detention_narration;
						row.detention_charges = lr.detention_charges;
						row.hamali_narration = lr.hamali_narration;
						row.hamali_charges = lr.hamali_charges;
						row.other_charge_narration = lr.other_charge_narration;
						row.other_charges = lr.other_charges;
					});
					
					calculate_totals(frm);'''

js_code = js_code.replace(old_js, new_js)

with open(js_path, "w") as f:
    f.write(js_code)

print("Files updated")
