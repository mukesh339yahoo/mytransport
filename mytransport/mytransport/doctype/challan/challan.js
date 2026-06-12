// Copyright (c) 2026, Shaily Sharma and contributors
// For license information, please see license.txt

frappe.ui.form.on("Challan", {
	total_hire_amount: function(frm) {
		calculate_balance(frm);
	},
	advance: function(frm) {
		calculate_balance(frm);
	},
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
	},
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
}

function calculate_balance(frm) {
	let total_hire_amount = flt(frm.doc.total_hire_amount);
	let advance = flt(frm.doc.advance);
	let balance = total_hire_amount - advance;
	
	frm.set_value('balance_amount', balance);
}
