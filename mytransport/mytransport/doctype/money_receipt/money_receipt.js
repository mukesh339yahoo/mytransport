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

    total_amount_received: function(frm) {
        calculate_unallocated(frm);
    },

    refresh: function(frm) {
        if (!frm.doc.customer || frm.doc.docstatus !== 0) return;

        frm.add_custom_button(__('Get Billed LRs'), function() {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Lorry Receipt",
                    filters: [
                        ["status", "=", "Billed"],
                        ["receipt_status", "!=", "Paid"],
                        ["docstatus", "=", 1]
                    ],
                    or_filters: [
                        ["consignor", "=", frm.doc.customer],
                        ["consignee", "=", frm.doc.customer]
                    ],
                    fields: ["name", "date", "from_city", "to_city", "outstanding_amount", "total_amount"]
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        let lrs = r.message;
                        
                        let d = new frappe.ui.Dialog({
                            title: 'Select Unpaid LRs',
                            fields: [
                                {
                                    fieldtype: 'Table',
                                    fieldname: 'lrs',
                                    fields: [
                                        {fieldtype: 'Check', fieldname: 'select', label: 'Select', in_list_view: 1},
                                        {fieldtype: 'Data', fieldname: 'lr_number', label: 'LR Number', read_only: 1, in_list_view: 1},
                                        {fieldtype: 'Currency', fieldname: 'total_amount', label: 'Total Freight', read_only: 1, in_list_view: 1},
                                        {fieldtype: 'Currency', fieldname: 'outstanding_amount', label: 'Outstanding Amount', read_only: 1, in_list_view: 1},
                                        {fieldtype: 'Currency', fieldname: 'allocate', label: 'Allocate Now', in_list_view: 1}
                                    ],
                                    data: lrs.map(lr => ({
                                        lr_number: lr.name,
                                        total_amount: lr.total_amount,
                                        outstanding_amount: lr.outstanding_amount,
                                        allocate: lr.outstanding_amount,
                                        select: 0
                                    })),
                                    get_data: () => d.fields_dict.lrs.grid.get_data()
                                }
                            ],
                            primary_action_label: 'Add to Receipt',
                            primary_action(values) {
                                let selected = values.lrs.filter(d => d.select);
                                if (!selected.length) {
                                    frappe.msgprint("Please select at least one Lorry Receipt.");
                                    return;
                                }

                                selected.forEach(sel => {
                                    if (sel.allocate > sel.outstanding_amount) {
                                        frappe.msgprint("Cannot allocate more than outstanding amount for LR " + sel.lr_number);
                                        return;
                                    }
                                    let row = frm.add_child("allocated_lrs");
                                    row.lorry_receipt = sel.lr_number;
                                    row.total_freight = sel.total_amount;
                                    row.outstanding_amount = sel.outstanding_amount;
                                    row.allocated_amount = sel.allocate;
                                });
                                
                                frm.refresh_field("allocated_lrs");
                                calculate_unallocated(frm);
                                d.hide();
                            }
                        });
                        
                        d.show();
                    } else {
                        frappe.msgprint("No unpaid billed LRs found for this customer.");
                    }
                }
            });
        }, __('Get Items From'));
    }
});

frappe.ui.form.on('Money Receipt Item', {
    allocated_amount: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.allocated_amount > row.outstanding_amount) {
            frappe.msgprint("Allocated amount cannot exceed Outstanding Amount.");
            frappe.model.set_value(cdt, cdn, "allocated_amount", row.outstanding_amount);
        }
        calculate_unallocated(frm);
    },
    allocated_lrs_remove: function(frm) {
        calculate_unallocated(frm);
    }
});

function calculate_unallocated(frm) {
    let total_allocated = 0;
    if (frm.doc.allocated_lrs) {
        frm.doc.allocated_lrs.forEach(row => {
            total_allocated += row.allocated_amount;
        });
    }
    
    let total_received = frm.doc.total_amount_received || 0;
    frm.set_value("unallocated_amount", total_received - total_allocated);
}
