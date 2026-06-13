// Copyright (c) 2026, Ridhira Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Transport Invoice", {
	setup: function(frm) {
		frm.set_query("debit_to", function() {
			return {
				filters: {
					"company": frm.doc.company,
					"account_type": "Receivable",
					"is_group": 0
				}
			};
		});
		frm.set_query("income_account", function() {
			return {
				filters: {
					"company": frm.doc.company,
					"root_type": "Income",
					"is_group": 0
				}
			};
		});
	},

	onload: function(frm) {
		if (frm.is_new() && frm.doc.date && !frm.doc.due_date) {
			frm.set_value("due_date", frappe.datetime.add_days(frm.doc.date, 30));
		}
	},

	date: function(frm) {
		if (frm.doc.date && !frm.doc.due_date) {
			frm.set_value("due_date", frappe.datetime.add_days(frm.doc.date, 30));
		}
	},

	refresh(frm) {
		if (frm.doc.docstatus === 0 && !frm.is_new()) {
			frm.add_custom_button(__("Get Unbilled LRs"), function() {
				frm.events.get_unbilled_lrs(frm);
			});
		}
	},
	
	customer: function(frm) {
		if (frm.doc.customer) {
			frappe.db.get_value("Customer", frm.doc.customer, ["customer_primary_address", "gstin"])
				.then(r => {
					if (r.message) {
						if (r.message.gstin) {
							frm.set_value("customer_gst_no", r.message.gstin);
						}
						if (r.message.customer_primary_address) {
							frappe.call({
								method: 'frappe.contacts.doctype.address.address.get_address_display',
								args: { address_dict: r.message.customer_primary_address }
							}).then(res => {
								if (res.message) {
									frm.set_value("customer_address", res.message);
								}
							});
						}
					}
				});
		}
	},

	company: function(frm) {
		if (frm.doc.company) {
			frappe.db.get_value('Company', frm.doc.company, 'default_receivable_account')
			.then(r => {
				if (r.message && !frm.doc.debit_to) {
					frm.set_value('debit_to', r.message.default_receivable_account);
				}
			});
			frappe.db.get_value('Company', frm.doc.company, 'default_income_account')
			.then(r => {
				if (r.message && !frm.doc.income_account) {
					frm.set_value('income_account', r.message.default_income_account);
				}
			});
		}
	},
	
	get_unbilled_lrs: function(frm) {
		if (!frm.doc.customer) {
			frappe.msgprint(__("Please select a Customer first."));
			return;
		}
		
		frappe.call({
			method: "mytransport.mytransport.doctype.transport_invoice.transport_invoice.get_unbilled_lrs",
			args: {
				customer: frm.doc.customer,
				invoice_name: frm.doc.name
			},
			callback: function(r) {
				if (r.message && r.message.length > 0) {
					frm.clear_table("items");
					r.message.forEach(function(lr) {
						let row = frm.add_child("items");
						row.lr_number = lr.name;
					});
					frm.refresh_field("items");
					frappe.msgprint(__("Successfully fetched {0} Lorry Receipts.", [r.message.length]));
				} else {
					frappe.msgprint(__("No unbilled Lorry Receipts found for this customer."));
				}
			}
		});
	}
});

frappe.ui.form.on("Transport Invoice Item", {
	lr_number: function(frm, cdt, cdn) {
		calculate_totals(frm);
	},
	items_remove: function(frm) {
		calculate_totals(frm);
	}
});

function calculate_totals(frm) {
	let tf = 0, ts = 0, td = 0, th = 0, to = 0;
	if (frm.doc.items) {
		frm.doc.items.forEach(function(item) {
			tf += flt(item.basic_freight);
			ts += flt(item.st_charge);
			td += flt(item.detention_charges);
			th += flt(item.hamali_charges);
			to += flt(item.other_charges);
		});
	}
	frm.set_value("total_freight", tf);
	frm.set_value("total_st_charge", ts);
	frm.set_value("total_detention_charge", td);
	frm.set_value("total_hamali_charge", th);
	frm.set_value("total_other_charges", to);
	
	let total = tf + ts + td + th + to;
	frm.set_value("total_amount", total);
	frm.set_value("outstanding_amount", total - flt(frm.doc.paid_amount));
}
