// Copyright (c) 2026, Shaily Sharma and contributors
// For license information, please see license.txt

frappe.ui.form.on("Expense Voucher", {
    onload: function(frm) {
        if (frm.is_new() && !frm.doc.company) {
            frm.set_value("company", frappe.defaults.get_default("Company"));
        }
        if (frm.is_new() && !frm.doc.branch) {
            let default_branch = frappe.defaults.get_default("branch") || frappe.defaults.get_default("Branch");
            if (default_branch) {
                frm.set_value("branch", default_branch);
            }
        }
    },
    setup: function(frm) {
        frm.set_query("payment_account", function() {
            return {
                filters: {
                    "account_type": frm.doc.voucher_type,
                    "is_group": 0,
                    "company": frm.doc.company
                }
            };
        });
        
        frm.set_query("expense_account", function() {
            return {
                filters: {
                    "report_type": "Profit and Loss",
                    "is_group": 0,
                    "company": frm.doc.company
                }
            };
        });
    },

    voucher_type: function(frm) {
        // Reset the payment account when voucher type changes
        frm.set_value('payment_account', null);
    },

    on_account: function(frm) {
        calculate_totals(frm);
    },

    get_unpaid_challans: function(frm) {
        if (!frm.doc.vendor || frm.doc.docstatus !== 0) {
            frappe.msgprint("Please select a Vendor first.");
            return;
        }

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Challan",
                filters: [
                    ["balance_amount", ">", 0],
                    ["docstatus", "=", 1],
                    ["broker", "=", frm.doc.vendor]
                ],
                fields: ["name", "challan_number", "date", "vehicle_number", "broker", "total_hire_amount", "balance_amount"]
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    let challans = r.message;
                    
                    let d = new frappe.ui.Dialog({
                        title: 'Select Unpaid Challans',
                        fields: [
                            {
                                fieldtype: 'Table',
                                fieldname: 'challans',
                                fields: [
                                    {fieldtype: 'Check', fieldname: 'select', label: 'Select', in_list_view: 1},
                                    {fieldtype: 'Data', fieldname: 'name', label: 'Challan Ref', read_only: 1, in_list_view: 1, hidden: 1},
                                    {fieldtype: 'Data', fieldname: 'challan_number', label: 'Challan No', read_only: 1, in_list_view: 1},
                                    {fieldtype: 'Date', fieldname: 'date', label: 'Date', read_only: 1, in_list_view: 1},
                                    {fieldtype: 'Data', fieldname: 'vehicle_number', label: 'Vehicle No', read_only: 1, in_list_view: 1},
                                    {fieldtype: 'Currency', fieldname: 'total_hire_amount', label: 'Total Amount', read_only: 1, in_list_view: 1},
                                    {fieldtype: 'Currency', fieldname: 'balance_amount', label: 'Balance', read_only: 1, in_list_view: 1},
                                    {fieldtype: 'Currency', fieldname: 'allocate', label: 'Pay Now', in_list_view: 1}
                                ],
                                data: challans.map(c => ({
                                    name: c.name,
                                    challan_number: c.challan_number,
                                    date: c.date,
                                    vehicle_number: c.vehicle_number,
                                    total_hire_amount: c.total_hire_amount,
                                    balance_amount: c.balance_amount,
                                    allocate: c.balance_amount,
                                    select: 0
                                })),
                                get_data: () => d.fields_dict.challans.grid.get_data()
                            }
                        ],
                        primary_action_label: 'Add to Voucher',
                        primary_action(values) {
                            let selected = values.challans.filter(b => b.select);
                            if (!selected.length) {
                                frappe.msgprint("Please select at least one Challan.");
                                return;
                            }

                            selected.forEach(sel => {
                                if (sel.allocate > sel.balance_amount) {
                                    frappe.msgprint("Cannot allocate more than balance amount for Challan " + sel.challan_number);
                                    return;
                                }
                                let row = frm.add_child("allocated_challans");
                                row.challan = sel.name;
                                row.challan_no = sel.challan_number;
                                row.challan_date = sel.date;
                                row.vehicle_no = sel.vehicle_number;
                                row.vendor = frm.doc.vendor;
                                row.total_amt = sel.total_hire_amount;
                                row.balance = sel.balance_amount;
                                row.paid_amt = sel.allocate;
                            });
                            
                            frm.refresh_field("allocated_challans");
                            calculate_totals(frm);
                            d.hide();
                        }
                    });
                    
                    d.show();
                } else {
                    frappe.msgprint("No unpaid challans found for this vendor.");
                }
            }
        });
    }
});

frappe.ui.form.on("Allocated Challan", {
    paid_amt: function(frm, cdt, cdn) {
        calculate_totals(frm);
    },
    allocated_challans_remove: function(frm) {
        calculate_totals(frm);
    }
});

function calculate_totals(frm) {
    let total_paid = 0;
    
    if (frm.doc.allocated_challans && frm.doc.allocated_challans.length > 0) {
        frm.doc.allocated_challans.forEach(row => {
            total_paid += flt(row.paid_amt);
        });
    }

    let on_account = flt(frm.doc.on_account) || 0;
    total_paid += on_account;

    frm.set_value("total_paid_amt", total_paid);

    if (total_paid > 0) {
        frappe.call({
            method: 'mytransport.mytransport.doctype.money_receipt.money_receipt.get_money_in_words',
            args: {
                amount: total_paid,
                currency: frappe.defaults.get_default("Currency") || "INR"
            },
            callback: function(r) {
                if(r.message) {
                    frm.set_value("amount_in_words", r.message);
                }
            }
        });
    } else {
        frm.set_value("amount_in_words", "");
    }
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

frappe.ui.form.on("Expense Voucher", {
	refresh: function(frm) {
		peek_branch_number(frm, "Expense Voucher", "expense_voucher_number");
	},
	branch: function(frm) {
		peek_branch_number(frm, "Expense Voucher", "voucher_no");
	},
	date: function(frm) {
		peek_branch_number(frm, "Expense Voucher", "voucher_no");
	}
});
