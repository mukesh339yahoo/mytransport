// Copyright (c) 2026, Ridhira Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lorry Receipt", {
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
	refresh: function(frm) {
		peek_branch_number(frm, "Lorry Receipt", "lr_number");
	},
	branch: function(frm) {
		peek_branch_number(frm, "Lorry Receipt", "lr_number");
	},
	date: function(frm) {
		peek_branch_number(frm, "Lorry Receipt", "lr_number");
	}
});
