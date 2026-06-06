// Copyright (c) 2026, Shaily Sharma and contributors
// For license information, please see license.txt

frappe.ui.form.on("Challan", {
	total_hire_amount: function(frm) {
		calculate_balance(frm);
	},
	advance: function(frm) {
		calculate_balance(frm);
	}
});

function calculate_balance(frm) {
	let total_hire_amount = flt(frm.doc.total_hire_amount);
	let advance = flt(frm.doc.advance);
	let balance = total_hire_amount - advance;
	
	frm.set_value('balance_amount', balance);
}
