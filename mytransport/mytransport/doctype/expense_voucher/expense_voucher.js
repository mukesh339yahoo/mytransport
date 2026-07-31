// Copyright (c) 2026, Shaily Sharma and contributors
// For license information, please see license.txt

frappe.ui.form.on("Expense Voucher", {
    onload: function(frm) {
        if (frm.is_new() && !frm.doc.company) {
            frm.set_value("company", frappe.defaults.get_default("Company"));
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
        
        frm.set_df_property("total_paid_amt", "hidden", 0);
        frm.set_df_property("amount_in_words", "hidden", 0);
        
        frm.set_query("challan_ref", "expense_details", function(doc, cdt, cdn) {
            let filters = { "docstatus": 1 };
            if (frm.doc.party) {
                filters["broker"] = frm.doc.party;
            }
            return { filters: filters };
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
        if (!frm.doc.party || frm.doc.docstatus !== 0) {
            frappe.msgprint("Please select a Party first.");
            return;
        }

        frappe.call({
            method: "mytransport.mytransport.doctype.expense_voucher.expense_voucher.get_unpaid_challans_for_vendor",
            args: {
                party: frm.doc.party,
                current_voucher: frm.doc.name
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
                                    {fieldtype: 'Data', fieldname: 'name', label: 'Challan Ref', read_only: 1, in_list_view: 1, hidden: 1},
                                    {fieldtype: 'Data', fieldname: 'challan_number', label: 'Challan No', read_only: 1, in_list_view: 1},
                                    {fieldtype: 'Date', fieldname: 'date', label: 'Date', read_only: 1, in_list_view: 1},
                                    {fieldtype: 'Data', fieldname: 'vehicle_number', label: 'Vehicle No', read_only: 1, in_list_view: 1},
                                    {fieldtype: 'Currency', fieldname: 'total_hire_amount', label: 'Total Amount', read_only: 1, in_list_view: 1},
                                    {fieldtype: 'Currency', fieldname: 'adjusted_amt', label: 'Adjusted Amt', read_only: 1, in_list_view: 1},
                                    {fieldtype: 'Currency', fieldname: 'balance_amount', label: 'Balance', read_only: 1, in_list_view: 1},
                                    {fieldtype: 'Currency', fieldname: 'allocate', label: 'Pay Now', in_list_view: 1}
                                ],
                                data: challans.map(c => ({
                                    name: c.name,
                                    challan_number: c.challan_number,
                                    date: c.date,
                                    vehicle_number: c.vehicle_number,
                                    total_hire_amount: c.total_hire_amount,
                                    adjusted_amt: c.adjusted_amt,
                                    balance_amount: c.balance_amount,
                                    allocate: c.balance_amount
                                })),
                                get_data: () => d.fields_dict.challans.grid.get_data()
                            }
                        ],
                        primary_action_label: 'Add to Voucher',
                        primary_action(values) {
                            let selected = d.fields_dict.challans.grid.get_selected_children();
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
                                row.challan_date = sel.date;
                                row.vehicle_no = sel.vehicle_number;
                                row.vendor = frm.doc.party;
                                row.total_amt = sel.total_hire_amount;
                                row.adjusted_amt = sel.adjusted_amt;
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

frappe.ui.form.on("Expense Detail", {
    expense_amount: function(frm, cdt, cdn) {
        calculate_totals(frm);
    },
    challan_ref: function(frm, cdt, cdn) {
        calculate_totals(frm);
    },
    expense_details_remove: function(frm) {
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

    if (frm.doc.expense_details && frm.doc.expense_details.length > 0) {
        frm.doc.expense_details.forEach(row => {
            total_paid += flt(row.expense_amount);
        });
    }

    let on_account = flt(frm.doc.on_account) || 0;
    total_paid += on_account;

    frm.set_value("total_paid_amt", total_paid);
    fetch_previous_payments(frm);

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
        frm.set_value("amount_in_words", "Zero");
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
		peek_branch_number(frm, "Expense Voucher", "voucher_no");
		calculate_totals(frm);

		if (frm.fields_dict.search_party && frm.fields_dict.search_party.$input) {
            let $input = frm.fields_dict.search_party.$input;
            if (!$input.data("awesomplete-init")) {
                let party_map = {}; // store party_types
                
                let awesomplete = new Awesomplete($input[0], {
                    minChars: 0,
                    maxItems: 15,
                    autoFirst: true
                });

                function fetch_parties() {
                    let term = $input.val();
                    frappe.call({
                        method: "mytransport.mytransport.doctype.money_receipt.money_receipt.search_unified_party",
                        args: { query: term },
                        callback: function(r) {
                            if (r.message) {
                                awesomplete.list = r.message.map(d => {
                                    party_map[d.name] = d.party_type;
                                    return {
                                        label: d.name + " (" + d.party_type + ")",
                                        value: d.name
                                    };
                                });
                                awesomplete.evaluate();
                            }
                        }
                    });
                }

                $input.on("input focus click", function() {
                    fetch_parties();
                });
                
                $input[0].addEventListener("awesomplete-selectcomplete", function(e) {
                    let selected_party = e.text.value;
                    let p_type = party_map[selected_party];
                    
                    frm.set_value("search_party", e.text.label);
                    frm.set_value("party_type", p_type);
                    frm.set_value("party", selected_party);
                    
                    frappe.call({
                        method: "erpnext.accounts.party.get_party_account",
                        args: {
                            party_type: p_type,
                            party: selected_party,
                            company: frm.doc.company
                        },
                        callback: function(r) {
                            if (r.message) {
                                frm.set_value("debit_account", r.message);
                            }
                        }
                    });
                });
                $input.data("awesomplete-init", true);
            }
        }
	},
	branch: function(frm) {
		peek_branch_number(frm, "Expense Voucher", "voucher_no");
	},
	date: function(frm) {
		peek_branch_number(frm, "Expense Voucher", "voucher_no");
	}
});

function fetch_previous_payments(frm) {
    let challans = new Set();
    
    if (frm.doc.allocated_challans) {
        frm.doc.allocated_challans.forEach(row => {
            if (row.challan) challans.add(row.challan);
        });
    }
    
    if (frm.doc.expense_details) {
        frm.doc.expense_details.forEach(row => {
            if (row.challan_ref) challans.add(row.challan_ref);
        });
    }
    
    if (challans.size > 0) {
        frappe.call({
            method: "mytransport.mytransport.doctype.expense_voucher.expense_voucher.get_previous_payments",
            args: {
                challans: Array.from(challans),
                current_voucher: frm.doc.name
            },
            callback: function(r) {
                let existing = frm.doc.previous_payments || [];
                let incoming = r.message || [];
                
                let is_same = true;
                if (existing.length !== incoming.length) {
                    is_same = false;
                } else {
                    for (let i = 0; i < incoming.length; i++) {
                        let e = existing[i];
                        let p = incoming[i];
                        if (e.challan_no !== p.challan_no || e.voucher_no !== p.voucher_no || flt(e.amount) !== flt(p.amount)) {
                            is_same = false;
                            break;
                        }
                    }
                }
                
                if (!is_same) {
                    frm.clear_table("previous_payments");
                    incoming.forEach(pmt => {
                        let row = frm.add_child("previous_payments");
                        row.challan_no = pmt.challan_no;
                        row.voucher_no = pmt.voucher_no;
                        row.voucher_date = pmt.voucher_date;
                        row.amount = pmt.amount;
                        row.vendor = pmt.vendor;
                    });
                    frm.refresh_field("previous_payments");
                }
            }
        });
    } else {
        if (frm.doc.previous_payments && frm.doc.previous_payments.length > 0) {
            frm.clear_table("previous_payments");
            frm.refresh_field("previous_payments");
        }
    }
}

frappe.ui.form.on("Expense Voucher", {
	on_submit: function(frm) {
		setTimeout(() => {
			frappe.new_doc(frm.doctype);
		}, 500);
	}
});
