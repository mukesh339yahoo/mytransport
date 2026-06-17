import os

file_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/challan/challan.js"

new_code = """
	tds_declaration: function(frm) {
		if (frm.doc.tds_declaration && !frm.doc.tds_challan) {
			frm.set_value("tds_percent", 0);
		} else if (!frm.doc.tds_declaration) {
			frm.set_value("tds_challan", "");
			frm.set_value("tds_percent", 1);
		}
	},
	before_submit: function(frm) {
		if (frm.doc.tds_declaration && frm.doc.vehicle_number) {
			return new Promise(resolve => {
				frappe.db.get_doc("Hired Vehicle", frm.doc.vehicle_number)
					.then(doc => {
						let current_fy = get_current_financial_year();
						let has_declaration = false;
						
						if (doc.tds_declarations) {
							for (let i = 0; i < doc.tds_declarations.length; i++) {
								if (doc.tds_declarations[i].financial_year == current_fy) {
									has_declaration = true;
									break;
								}
							}
						}
						
						if (!has_declaration) {
							frappe.confirm(
								'TDS Declaration is checked. Do you want to submit this TDS Declaration to the Hired Vehicle master record?',
								() => {
									frm.doc.update_vehicle_tds = 1;
									resolve();
								},
								() => {
									frm.doc.update_vehicle_tds = 0;
									resolve();
								}
							);
						} else {
							frm.doc.update_vehicle_tds = 0;
							resolve();
						}
					});
			});
		}
	},
"""

with open(file_path, "r") as f:
    content = f.read()

# find the last }); of the first block and replace with our new code
if "});" in content:
    idx = content.find("});")
    content = content[:idx] + new_code + "\n" + content[idx:]

with open(file_path, "w") as f:
    f.write(content)

print("challan.js updated")
