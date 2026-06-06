frappe.ui.form.on('Sales Invoice', {
    refresh(frm) {
        if (!frm.doc.customer || frm.doc.docstatus !== 0) return;

        frm.add_custom_button(__('Unbilled Lorry Receipts'), function() {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Lorry Receipt",
                    filters: [
                        ["status", "=", "Unbilled"],
                        ["docstatus", "=", 1] // Only fetch submitted LRs
                    ],
                    or_filters: [
                        ["consignor", "=", frm.doc.customer],
                        ["consignee", "=", frm.doc.customer]
                    ],
                    fields: ["name", "date", "from_city", "to_city", "total_amount", "consignor", "consignee"]
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        let lrs = r.message;
                        
                        let d = new frappe.ui.Dialog({
                            title: 'Select Lorry Receipts',
                            fields: [
                                {
                                    fieldtype: 'Table',
                                    fieldname: 'lrs',
                                    fields: [
                                        {fieldtype: 'Check', fieldname: 'select', label: 'Select', in_list_view: 1, default: 0},
                                        {fieldtype: 'Data', fieldname: 'lr_number', label: 'LR Number', read_only: 1, in_list_view: 1},
                                        {fieldtype: 'Date', fieldname: 'date', label: 'Date', read_only: 1, in_list_view: 1},
                                        {fieldtype: 'Currency', fieldname: 'amount', label: 'Amount', read_only: 1, in_list_view: 1},
                                        {fieldtype: 'Data', fieldname: 'from', label: 'From', read_only: 1, in_list_view: 1},
                                        {fieldtype: 'Data', fieldname: 'to', label: 'To', read_only: 1, in_list_view: 1}
                                    ],
                                    data: lrs.map(lr => ({
                                        lr_number: lr.name,
                                        date: lr.date,
                                        amount: lr.total_amount,
                                        from: lr.from_city,
                                        to: lr.to_city,
                                        select: 0
                                    })),
                                    get_data: () => { return d.fields_dict.lrs.grid.get_data(); }
                                }
                            ],
                            primary_action_label: 'Add to Invoice',
                            primary_action(values) {
                                let selected = values.lrs.filter(d => d.select);
                                if (!selected.length) {
                                    frappe.msgprint("Please select at least one Lorry Receipt.");
                                    return;
                                }

                                selected.forEach(sel => {
                                    let row = frm.add_child("items");
                                    row.lorry_receipt = sel.lr_number;
                                    row.qty = 1;
                                    row.rate = sel.amount;
                                    row.amount = sel.amount;
                                    row.description = "Freight Charges for LR: " + sel.lr_number + " from " + sel.from + " to " + sel.to;
                                    // Item code left blank intentionally so the user can select their specific item code
                                });
                                
                                frm.refresh_field("items");
                                d.hide();
                            }
                        });
                        
                        d.show();
                    } else {
                        frappe.msgprint("No unbilled submitted Lorry Receipts found for this customer.");
                    }
                }
            });
        }, __('Get Items From'));
    }
});
