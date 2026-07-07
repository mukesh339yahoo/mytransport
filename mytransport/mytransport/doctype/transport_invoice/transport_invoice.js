// Copyright (c) 2026, Ridhira Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Transport Invoice", {
	setup: function(frm) {
		frm.ignore_doctypes_on_cancel_all = ["Lorry Receipt"];
		
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

	date: function(frm) {
		if (frm.doc.date > frappe.datetime.get_today()) {
			frappe.msgprint(__("Transport Invoice Date cannot be a future date."));
			frm.set_value("date", frappe.datetime.get_today());
		}
		if (frm.doc.date && !frm.doc.due_date) {
			frm.set_value("due_date", frappe.datetime.add_days(frm.doc.date, 30));
		}
	},

	validate: function(frm) {
		if (frm.doc.date > frappe.datetime.get_today()) {
			frappe.msgprint(__("Transport Invoice Date cannot be a future date."));
			frappe.validated = false;
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
			// First clear the fields so they update immediately
			frm.set_value("customer_address", "");
			frm.set_value("customer_gst_no", "");
			
			frappe.db.get_value("Customer", frm.doc.customer, ["customer_primary_address", "tax_id"])
				.then(r => {
					if (r.message) {
						if (r.message.tax_id) {
							frm.set_value("customer_gst_no", r.message.tax_id);
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
		} else {
			frm.set_value("customer_address", "");
			frm.set_value("customer_gst_no", "");
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
					let lrs = r.message;
					
					let d = new frappe.ui.Dialog({
						title: 'Select Unbilled LRs',
						fields: [
							{
								fieldtype: 'Table',
								fieldname: 'lrs',
								fields: [
									{fieldtype: 'Check', fieldname: 'select', label: 'Select', in_list_view: 1},
									{fieldtype: 'Data', fieldname: 'name', label: 'LR No', read_only: 1, in_list_view: 1},
									{fieldtype: 'Date', fieldname: 'date', label: 'LR Date', read_only: 1, in_list_view: 1},
									{fieldtype: 'Data', fieldname: 'from_city', label: 'From', read_only: 1, in_list_view: 1},
									{fieldtype: 'Data', fieldname: 'to_city', label: 'To', read_only: 1, in_list_view: 1},
									{fieldtype: 'Float', fieldname: 'total_charged_weight', label: 'Chrg Wgt', read_only: 1, in_list_view: 1},
									{fieldtype: 'Currency', fieldname: 'basic_freight', label: 'Basic Freight', read_only: 1, in_list_view: 1}
								],
								data: lrs.map(lr => ({
									name: lr.name,
									date: lr.date,
									from_city: lr.from_city,
									to_city: lr.to_city,
									total_charged_weight: lr.total_charged_weight,
									basic_freight: lr.basic_freight,
									select: 0
								})),
								get_data: () => d.fields_dict.lrs.grid.get_data()
							}
						],
						primary_action_label: 'Add to Invoice',
						primary_action(values) {
							let selected = values.lrs.filter(b => b.select);
							if (!selected.length) {
								frappe.msgprint("Please select at least one LR.");
								return;
							}

							selected.forEach(sel => {
								let lr = lrs.find(x => x.name === sel.name);
								if(lr) {
									let row = frm.add_child("items");
									row.lr_number = lr.name;
									row.lr_date = lr.date;
									row.from_city = lr.from_city;
									row.to_city = lr.to_city;
									row.total_packages = lr.total_packages;
									row.total_weight = lr.total_charged_weight;
									row.rate_type = "Fix";
									row.rate_per_mt = 0;
									row.st_charge = 0;
									row.detention_narration = "";
									row.detention_charges = 0;
									row.hamali_narration = "";
									row.hamali_charges = 0;
									row.other_charge_narration = "";
									row.other_charges = 0;
								}
							});
							
							calculate_totals(frm);
							frm.refresh_field("items");
							d.hide();
						}
					});
					
					d.show();
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
	},
	rate_type: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.rate_type === "Fix") {
			frappe.model.set_value(cdt, cdn, "rate_per_mt", 0);
		} else if (row.rate_type === "Per MT") {
			let rate = flt(row.rate_per_mt);
			if (rate > 0) {
				frappe.model.set_value(cdt, cdn, "basic_freight", rate * flt(row.total_weight));
			}
		}
	},
	rate_per_mt: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.rate_type === "Per MT") {
			let rate = flt(row.rate_per_mt);
			if (rate > 0) {
				frappe.model.set_value(cdt, cdn, "basic_freight", rate * flt(row.total_weight));
			}
		}
	},
	basic_freight: function(frm, cdt, cdn) {
		calculate_totals(frm);
	},
	st_charge: function(frm, cdt, cdn) {
		calculate_totals(frm);
	},
	detention_charges: function(frm, cdt, cdn) {
		calculate_totals(frm);
	},
	hamali_charges: function(frm, cdt, cdn) {
		calculate_totals(frm);
	},
	other_charges: function(frm, cdt, cdn) {
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

frappe.ui.form.on("Transport Invoice", {
	refresh: function(frm) {
		peek_branch_number(frm, "Transport Invoice", "bill_no");
	},
	branch: function(frm) {
		peek_branch_number(frm, "Transport Invoice", "bill_no");
	},
	date: function(frm) {
		peek_branch_number(frm, "Transport Invoice", "bill_no");
	}
});

frappe.ui.form.on("Transport Invoice", {
	on_submit: function(frm) {
		setTimeout(() => {
			frappe.new_doc(frm.doctype);
		}, 500);
	}
});
