// Copyright (c) 2026, Shaily Sharma and contributors
// For license information, please see license.txt

frappe.ui.form.on("Challan", {
	onload: function(frm) {
		if (frm.is_new() && !frm.doc.branch) {
			frappe.call({
				method: "mytransport.branch_numbering.get_default_branch",
				callback: function(r) {
					if (r.message && !frm.doc.branch) {
						frm.set_value("branch", r.message);
					}
				}
			});
		}
	},
	get_unmapped_lrs: function(frm) {
		let msd = new frappe.ui.form.MultiSelectDialog({
			doctype: "Lorry Receipt",
			target: frm,
			setters: {
				from_city: frm.doc.from_location,
				to_city: frm.doc.to_location
			},
			add_filters_group: 1,
			date_field: "date",
			get_query() {
				let filters = {
					"challan_status": "Pending",
					"docstatus": 1
				};
				
				let existing_lrs = (frm.doc.lrs || []).map(row => row.lr_number).filter(Boolean);
				if (existing_lrs.length > 0) {
					filters["name"] = ["not in", existing_lrs];
				}
				
				return {
					filters: filters
				};
			},
			action(selections) {
				if (selections.length === 0) {
					return;
				}
				
				frappe.call({
					method: "mytransport.mytransport.doctype.challan.challan.get_lr_details",
					args: {
						lr_names: JSON.stringify(selections)
					},
					callback: function(r) {
						if (r.message && r.message.length > 0) {
							let vehicle_numbers = new Set();
							
							r.message.forEach(function(lr, index) {
								let row = frm.add_child("lrs");
								row.lr_number = lr.name;
								row.lr_date = lr.date;
								row.from_city = lr.from_city;
								row.to_city = lr.to_city;
								row.total_packages = lr.total_packages;
								row.total_weight = lr.total_weight;
								row.basic_freight = lr.basic_freight;
								row.hamali_charges = lr.hamali_charges;
								row.detention_charges = lr.detention_charges;
								row.rto_charges = lr.rto_charges;
								row.other_charges = lr.other_charges;
								row.total_amount = lr.total_amount;
								row.vehicle_number = lr.vehicle_number;
								
								if (lr.vehicle_number) {
									vehicle_numbers.add(lr.vehicle_number);
								}
								
								if (index === 0) {
									if (lr.from_city) frm.set_value("from_location", lr.from_city);
									if (lr.to_city) frm.set_value("to_location", lr.to_city);
									if (lr.vehicle_number) frm.set_value("vehicle_number", lr.vehicle_number);
									if (lr.driver_name) frm.set_value("driver_name", lr.driver_name);
								}
							});
							
							if (vehicle_numbers.size > 1) {
								frappe.msgprint({
									title: __('Warning'),
									indicator: 'orange',
									message: __('The selected LRs have different Vehicle Numbers! Please review them.')
								});
							}
							
							calculate_lr_totals(frm);
							frm.refresh_field("lrs");
							
							cur_dialog.hide();
						}
					}
				});
			}
		});
		
		// Frappe MultiSelectDialog bug workaround: 
		// if field is empty, it falls back to the initial setters object. 
		// We set them to empty string after initialization so manual clears actually work.
		msd.setters.from_city = '';
		msd.setters.to_city = '';
		
		msd.dialog.$wrapper.find('.clear-filters').on('click', function() {
			msd.dialog.set_value('from_city', '');
			msd.dialog.set_value('to_city', '');
		});
	},
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
							frm.set_value("tds_challan", "-");
						}
					} else {
						frm.set_value("tds_declaration", 0);
						frm.set_value("tds_percent", 1);
						frm.set_value("tds_challan", "-");
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
			frm.set_value("tds_challan", "-");
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
	let total_weight = 0;
	let total_packages = 0;


	if (frm.doc.lrs) {
		total_lrs = frm.doc.lrs.length;
		frm.doc.lrs.forEach(function(item) {
			basic_freight += flt(item.basic_freight);
			total_weight += flt(item.total_weight);
			total_packages += cint(item.total_packages);
		});
	}

	frm.set_value("total_lrs", total_lrs);
	frm.set_value("basic_freight", basic_freight);
	frm.set_value("total_weight", total_weight);
	frm.set_value("total_packages", total_packages);
	
	calculate_total_amount(frm);
}

function calculate_total_amount(frm) {
	let total_amount = flt(frm.doc.basic_freight) + flt(frm.doc.hamali_charges) + flt(frm.doc.detention_charges) + flt(frm.doc.rto_charges) + flt(frm.doc.other_charges);
	frm.set_value("total_amount", total_amount);
	calculate_tds(frm);
}

function calculate_tds(frm) {
	let total = flt(frm.doc.total_amount);
	let percent = flt(frm.doc.tds_percent);
	let tds = (total * percent) / 100;
	frm.set_value("total_tds", tds);
	
	frm.set_value("total_hire_amount", total - tds);
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

function peek_branch_number(frm, doc_type, fieldname) {
	if (frm.doc.__islocal && frm.doc.branch && frm.doc.date && !frm.doc[fieldname]) {
		frappe.call({
			method: "mytransport.branch_numbering.peek_next_branch_number",
			args: {
				branch: frm.doc.branch,
				document_type: doc_type,
				date: frm.doc.date
			},
			callback: function(r) {
				if (r.message) {
					frm.set_value(fieldname, String(r.message));
				}
			}
		});
	}
}

frappe.ui.form.on("Challan", {
	onload: function(frm) {
		if (frm.is_new() && !frm.doc.branch) {
			frappe.call({
				method: "mytransport.branch_numbering.get_default_branch",
				callback: function(r) {
					if (r.message && !frm.doc.branch) {
						frm.set_value("branch", r.message);
					}
				}
			});
		}
	},
	refresh: function(frm) {
		peek_branch_number(frm, "Challan", "challan_number");
	},
	branch: function(frm) {
		peek_branch_number(frm, "Challan", "challan_number");
	},
	date: function(frm) {
		peek_branch_number(frm, "Challan", "challan_number");
	},
	basic_freight: function(frm) {
		calculate_total_amount(frm);
	},
	hamali_charges: function(frm) {
		calculate_total_amount(frm);
	},
	detention_charges: function(frm) {
		calculate_total_amount(frm);
	},
	rto_charges: function(frm) {
		calculate_total_amount(frm);
	},
	other_charges: function(frm) {
		calculate_total_amount(frm);
	}
});

function calculate_delivery_days(frm) {
	if (frm.doc.date && frm.doc.dispatch_date) {
		frm.set_value("days_to_load", frappe.datetime.get_day_diff(frm.doc.dispatch_date, frm.doc.date));
	} else {
		frm.set_value("days_to_load", 0);
	}

	if (frm.doc.dispatch_date && frm.doc.delivery_date) {
		frm.set_value("days_to_deliver", frappe.datetime.get_day_diff(frm.doc.delivery_date, frm.doc.dispatch_date));
	} else {
		frm.set_value("days_to_deliver", 0);
	}

	if (frm.doc.delivery_date && frm.doc.unloading_date) {
		frm.set_value("days_to_unload", frappe.datetime.get_day_diff(frm.doc.unloading_date, frm.doc.delivery_date));
	} else {
		frm.set_value("days_to_unload", 0);
	}
}

frappe.ui.form.on("Challan", {
	dispatch_date: function(frm) {
		calculate_delivery_days(frm);
	},
	delivery_date: function(frm) {
		calculate_delivery_days(frm);
	},
	unloading_date: function(frm) {
		calculate_delivery_days(frm);
	},
	date: function(frm) {
		calculate_delivery_days(frm);
	}
});

frappe.ui.form.on("Challan", "refresh", function(frm) {
	if (frm.is_new() && frm.doc.date && !frm.doc.dispatch_date) {
		frm.set_value("dispatch_date", frm.doc.date);
	}
	calculate_delivery_days(frm);
});

frappe.ui.form.on("Challan", {
	on_submit: function(frm) {
		setTimeout(() => {
			frappe.new_doc(frm.doctype);
		}, 500);
	}
});
