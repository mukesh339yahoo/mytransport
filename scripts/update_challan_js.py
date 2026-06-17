import os

file_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/challan/challan.js"

new_code = """
	vehicle_number: function(frm) {
		if (frm.doc.vehicle_number) {
			frappe.db.get_doc("Hired Vehicle", frm.doc.vehicle_number)
				.then(doc => {
					if (doc && doc.tds_declarations) {
						let current_fy = get_current_financial_year();
						let has_declaration = false;
						let challan_no = "";
						
						for (let i = 0; i < doc.tds_declarations.length; i++) {
							if (doc.tds_declarations[i].financial_year == current_fy) {
								has_declaration = true;
								challan_no = doc.tds_declarations[i].tds_declaration_challan || "";
								break;
							}
						}
						
						if (has_declaration) {
							frm.set_value("tds_declaration", 1);
							frm.set_value("tds_percent", 0);
							frm.set_value("tds_challan", challan_no);
						} else {
							frm.set_value("tds_declaration", 0);
							frm.set_value("tds_percent", 1);
							frm.set_value("tds_challan", "");
						}
					} else {
						frm.set_value("tds_declaration", 0);
						frm.set_value("tds_percent", 1);
						frm.set_value("tds_challan", "");
					}
				});
		}
	},
	tds_percent: function(frm) {
		calculate_tds(frm);
	}
});

frappe.ui.form.on("Challan LR Item", {
	lr_number: function(frm, cdt, cdn) {
		calculate_lr_totals(frm);
	},
	lrs_remove: function(frm, cdt, cdn) {
		calculate_lr_totals(frm);
	}
});

function calculate_lr_totals(frm) {
	let total_lrs = 0;
	let basic_freight = 0;
	let hamali_charges = 0;
	let detention_charges = 0;
	let rto_charges = 0;
	let other_charges = 0;
	let total_amount = 0;
	let total_weight = 0;
	let total_packages = 0;

	if (frm.doc.lrs) {
		total_lrs = frm.doc.lrs.length;
		frm.doc.lrs.forEach(function(item) {
			basic_freight += flt(item.basic_freight);
			hamali_charges += flt(item.hamali_charges);
			detention_charges += flt(item.detention_charges);
			rto_charges += flt(item.rto_charges);
			other_charges += flt(item.other_charges);
			total_amount += flt(item.total_amount);
			total_weight += flt(item.total_weight);
			total_packages += cint(item.total_packages);
		});
	}

	frm.set_value("total_lrs", total_lrs);
	frm.set_value("basic_freight", basic_freight);
	frm.set_value("hamali_charges", hamali_charges);
	frm.set_value("detention_charges", detention_charges);
	frm.set_value("rto_charges", rto_charges);
	frm.set_value("other_charges", other_charges);
	frm.set_value("total_amount", total_amount);
	frm.set_value("total_weight", total_weight);
	frm.set_value("total_packages", total_packages);
	
	calculate_tds(frm);
}

function calculate_tds(frm) {
	let total = flt(frm.doc.total_amount);
	let percent = flt(frm.doc.tds_percent);
	frm.set_value("total_tds", (total * percent) / 100);
}

function get_current_financial_year() {
	let today = new Date();
	let year = today.getFullYear();
	let month = today.getMonth() + 1; // 1-12
	
	let start_year = year;
	let end_year = year + 1;
	
	if (month < 4) {
		start_year = year - 1;
		end_year = year;
	}
	
	return start_year + "-" + end_year;
"""

with open(file_path, "r") as f:
    content = f.read()

# find the last }); of the first block and replace with our new code
if "});" in content:
    idx = content.rfind("});")
    content = content[:idx] + new_code + "\n}\n" + content[idx+3:]

with open(file_path, "w") as f:
    f.write(content)

print("challan.js updated")
