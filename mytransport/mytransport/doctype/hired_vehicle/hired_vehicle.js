// Copyright (c) 2026, Shaily Sharma and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hired Vehicle", {
	vehicle_number: function(frm) {
		if (frm.doc.vehicle_number) {
			let cleaned = frm.doc.vehicle_number.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
			if (cleaned !== frm.doc.vehicle_number) {
				frm.set_value('vehicle_number', cleaned);
			}
		}
	}
});
