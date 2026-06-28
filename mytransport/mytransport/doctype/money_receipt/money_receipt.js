// Copyright (c) 2026, Shaily Sharma and contributors
// For license information, please see license.txt

frappe.ui.form.on('Money Receipt', {
    onload: function(frm) {
        if (frm.is_new() && !frm.doc.company) {
            frm.set_value("company", frappe.defaults.get_default("Company"));
        }
    },
    setup: function(frm) {
        frm.set_query("deposit_account", function() {
            let ac_type = frm.doc.payment_mode === "Cash" ? "Cash" : "Bank";
            return {
                filters: {
                    "account_type": ac_type,
                    "is_group": 0,
                    "company": frm.doc.company
                }
            };
        });
    },
    
    payment_mode: function(frm) {
        frm.set_value("deposit_account", null);
    },

    get_unpaid_bills: function(frm) {
        if (!frm.doc.customer || frm.doc.docstatus !== 0) {
            frappe.msgprint("Please select a customer first.");
            return;
        }

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Transport Invoice",
                filters: [
                    ["status", "in", ["Unpaid", "Partially Paid"]],
                    ["docstatus", "=", 1],
                    ["customer", "=", frm.doc.customer]
                ],
                fields: ["name", "bill_no", "date", "total_amount", "outstanding_amount"]
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    let bills = r.message;
                    
                    let d = new frappe.ui.Dialog({
                        title: 'Select Unpaid Bills',
                        fields: [
                            {
                                fieldtype: 'Table',
                                fieldname: 'bills',
                                fields: [
                                    {fieldtype: 'Check', fieldname: 'select', label: 'Select', in_list_view: 1},
                                    {fieldtype: 'Data', fieldname: 'name', label: 'Invoice Ref', read_only: 1, in_list_view: 1, hidden: 1},
                                    {fieldtype: 'Data', fieldname: 'manual_bill_no', label: 'Bill No', read_only: 1, in_list_view: 1},
                                    {fieldtype: 'Date', fieldname: 'bill_date', label: 'Bill Date', read_only: 1, in_list_view: 1},
                                    {fieldtype: 'Currency', fieldname: 'total_amount', label: 'Total Amount', read_only: 1, in_list_view: 1},
                                    {fieldtype: 'Currency', fieldname: 'outstanding_amount', label: 'Balance', read_only: 1, in_list_view: 1},
                                    {fieldtype: 'Currency', fieldname: 'allocate', label: 'Pay Now', in_list_view: 1}
                                ],
                                data: bills.map(b => ({
                                    name: b.name,
                                    manual_bill_no: b.bill_no,
                                    bill_date: b.date,
                                    total_amount: b.total_amount,
                                    outstanding_amount: b.outstanding_amount,
                                    allocate: b.outstanding_amount,
                                    select: 0
                                })),
                                get_data: () => d.fields_dict.bills.grid.get_data()
                            }
                        ],
                        primary_action_label: 'Add to Receipt',
                        primary_action(values) {
                            let selected = values.bills.filter(b => b.select);
                            if (!selected.length) {
                                frappe.msgprint("Please select at least one Bill.");
                                return;
                            }

                            selected.forEach(sel => {
                                if (sel.allocate > sel.outstanding_amount) {
                                    frappe.msgprint("Cannot allocate more than outstanding amount for Bill " + (sel.manual_bill_no || sel.name));
                                    return;
                                }
                                let row = frm.add_child("allocated_invoices");
                                row.transport_invoice = sel.name;
                                row.bill_no = sel.manual_bill_no;
                                row.bill_date = sel.bill_date;
                                row.total_amt = sel.total_amount;
                                row.balance = sel.outstanding_amount;
                                row.paid_amt = sel.allocate;
                                row.deduct_amt = 0;
                                row.tds_amt = 0;
                            });
                            
                            frm.refresh_field("allocated_invoices");
                            calculate_totals(frm);
                            d.hide();
                        }
                    });
                    
                    d.show();
                } else {
                    frappe.msgprint("No unpaid bills found for this customer.");
                }
            }
        });
    }
});

frappe.ui.form.on('Allocated Transport Invoice', {
    paid_amt: function(frm, cdt, cdn) {
        validate_and_calculate(frm, cdt, cdn);
    },
    deduct_amt: function(frm, cdt, cdn) {
        validate_and_calculate(frm, cdt, cdn);
    },
    tds_amt: function(frm, cdt, cdn) {
        validate_and_calculate(frm, cdt, cdn);
    },
    allocated_invoices_remove: function(frm) {
        calculate_totals(frm);
    }
});

function validate_and_calculate(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    let total_deductions = flt(row.paid_amt) + flt(row.deduct_amt) + flt(row.tds_amt);
    
    if (total_deductions > flt(row.balance)) {
        frappe.msgprint("Total applied amount (Paid + Deduct + TDS) cannot exceed the Balance.");
        frappe.model.set_value(cdt, cdn, "paid_amt", 0);
        frappe.model.set_value(cdt, cdn, "deduct_amt", 0);
        frappe.model.set_value(cdt, cdn, "tds_amt", 0);
    } else {
        frappe.model.set_value(cdt, cdn, "outstanding_amt", flt(row.balance) - total_deductions);
    }
    calculate_totals(frm);
}

function calculate_totals(frm) {
    let total_paid = 0;
    if (frm.doc.allocated_invoices) {
        frm.doc.allocated_invoices.forEach(row => {
            total_paid += flt(row.paid_amt);
        });
    }
    
    frm.set_value("total_amount", total_paid);
    
    // Convert to words if frappe has the utility, sometimes frappe.utils.money_in_words is available
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

frappe.ui.form.on("Money Receipt", {
	refresh: function(frm) {
		peek_branch_number(frm, "Money Receipt", "money_receipt_number");
	},
	branch: function(frm) {
		peek_branch_number(frm, "Money Receipt", "mr_no");
	},
	date: function(frm) {
		peek_branch_number(frm, "Money Receipt", "mr_no");
	}
});
