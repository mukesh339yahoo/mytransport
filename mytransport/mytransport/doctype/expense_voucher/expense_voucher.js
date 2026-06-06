// Copyright (c) 2026, Shaily Sharma and contributors
// For license information, please see license.txt

frappe.ui.form.on("Expense Voucher", {
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

    challan: function(frm) {
        if (frm.doc.challan) {
            frappe.db.get_value("Challan", frm.doc.challan, "driver_name", function(r) {
                if (r && r.driver_name && !frm.doc.paid_to) {
                    frm.set_value("paid_to", r.driver_name);
                }
            });
        }
    }
});
