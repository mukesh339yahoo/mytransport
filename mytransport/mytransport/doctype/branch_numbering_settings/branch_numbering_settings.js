// Copyright (c) 2026, Shaily Sharma and contributors
// For license information, please see license.txt

frappe.ui.form.on("Branch Numbering Settings", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.set_df_property("starting_number", "read_only", 1);
		}
	},
});
