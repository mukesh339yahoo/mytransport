// Copyright (c) 2026, Ridhira Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lorry Receipt", {
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
	setup: function(frm) {
		// Calculate totals on setup if needed
		$('<style>').text(`
			div[data-fieldname="consignor_address"] textarea,
			div[data-fieldname="consignee_address"] textarea,
			div[data-fieldname="consignor_address"] .control-value,
			div[data-fieldname="consignee_address"] .control-value {
				height: 80px !important;
				max-height: 80px !important;
				min-height: 80px !important;
				resize: none !important;
				overflow-y: auto !important;
			}
		`).appendTo('head');
	},

	consignor: function(frm) {
		if (frm.doc.consignor && !frm.doc.credit_account) {
			frm.set_value("credit_account", frm.doc.consignor);
		}
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
	bilty_charges: function(frm) {
		calculate_total_amount(frm);
	},
	rto_charges: function(frm) {
		calculate_total_amount(frm);
	},
	other_charges: function(frm) {
		calculate_total_amount(frm);
	}
});

frappe.ui.form.on("LR Item", {
	lorry_freight: function(frm, cdt, cdn) {
		calculate_item_totals(frm);
	},
	qty: function(frm, cdt, cdn) {
		calculate_item_totals(frm);
	},
	actual_weight: function(frm, cdt, cdn) {
		calculate_item_totals(frm);
	},
	items_remove: function(frm) {
		calculate_item_totals(frm);
	}
});

function calculate_item_totals(frm) {
	let total_basic = 0;
	let total_weight = 0;
	let total_packages = 0;
	
	if (frm.doc.items) {
		frm.doc.items.forEach(function(item) {
			total_basic += flt(item.lorry_freight);
			total_weight += flt(item.actual_weight);
			total_packages += cint(item.qty);
		});
	}
	
	frm.set_value("basic_freight", total_basic);
	frm.set_value("total_weight", total_weight);
	frm.set_value("total_packages", total_packages);
	
	calculate_total_amount(frm);
}

function calculate_total_amount(frm) {
	let total = flt(frm.doc.basic_freight) + 
				flt(frm.doc.hamali_charges) + 
				flt(frm.doc.detention_charges) + 
				flt(frm.doc.bilty_charges) + 
				flt(frm.doc.rto_charges) + 
				flt(frm.doc.other_charges);
	frm.set_value("total_amount", total);
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

frappe.ui.form.on("Lorry Receipt", {
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
		peek_branch_number(frm, "Lorry Receipt", "lr_number");

		if (!frm.is_new()) {
			frm.add_custom_button(__('Print Copies'), function() {
				let dialog = new frappe.ui.Dialog({
					title: 'Select Copies to Print',
					fields: [
						{ fieldname: 'driver_copy', fieldtype: 'Check', label: 'Driver Copy', default: 1 },
						{ fieldname: 'consignor_copy', fieldtype: 'Check', label: 'Consignor Copy', default: 1 },
						{ fieldname: 'consignee_copy', fieldtype: 'Check', label: 'Consignee Copy', default: 1 },
						{ fieldname: 'office_copy', fieldtype: 'Check', label: 'Office Copy', default: 1 }
					],
					primary_action_label: 'Print',
					primary_action: function(values) {
						let selected_copies = [];
						if (values.driver_copy) selected_copies.push('Driver');
						if (values.consignor_copy) selected_copies.push('Consignor');
						if (values.consignee_copy) selected_copies.push('Consignee');
						if (values.office_copy) selected_copies.push('Office');

						if (selected_copies.length === 0) {
							frappe.msgprint(__('Please select at least one copy to print.'));
							return;
						}

						let copies_str = selected_copies.join(',');
						let print_format_name = encodeURIComponent("Lorry Receipt Custom");
						let url = `/printview?doctype=Lorry Receipt&name=${encodeURIComponent(frm.doc.name)}&format=${print_format_name}&print_copies=${copies_str}`;
						
						window.open(url, '_blank');
						dialog.hide();
					}
				});
				dialog.show();
			}, __("Print"));
		}
	},
	branch: function(frm) {
		peek_branch_number(frm, "Lorry Receipt", "lr_number");
	},
	date: function(frm) {
		peek_branch_number(frm, "Lorry Receipt", "lr_number");
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

frappe.ui.form.on("Lorry Receipt", {
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
		// Existing date hook is above, but frappe merges these on execution.
		calculate_delivery_days(frm);
	}
});

frappe.ui.form.on("Lorry Receipt", "refresh", function(frm) {
	if (frm.is_new() && frm.doc.date && !frm.doc.dispatch_date) {
		frm.set_value("dispatch_date", frm.doc.date);
	}
	calculate_delivery_days(frm);
});

frappe.ui.form.on("Lorry Receipt", {
	on_submit: function(frm) {
		setTimeout(() => {
			frappe.new_doc(frm.doctype);
		}, 500);
	}
});
