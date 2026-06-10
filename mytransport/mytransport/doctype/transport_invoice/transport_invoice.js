// Copyright (c) 2026, Ridhira Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Transport Invoice", {
	refresh(frm) {
		if (frm.doc.docstatus === 0 && !frm.is_new()) {
			frm.add_custom_button(__("Get Unbilled LRs"), function() {
				frm.events.get_unbilled_lrs(frm);
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
						row.lorry_receipt = lr.name;
						row.date = lr.date;
						row.from_city = lr.from_city;
						row.to_city = lr.to_city;
						row.vehicle_number = lr.vehicle_number;
						row.amount = lr.total_amount;
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
	amount: function(frm, cdt, cdn) {
		calculate_totals(frm);
	},
	items_remove: function(frm) {
		calculate_totals(frm);
	}
});

function calculate_totals(frm) {
	let total = 0;
	if (frm.doc.items) {
		frm.doc.items.forEach(function(item) {
			total += flt(item.amount);
		});
	}
	frm.set_value("total_amount", total);
	frm.set_value("outstanding_amount", total - flt(frm.doc.paid_amount));
}
