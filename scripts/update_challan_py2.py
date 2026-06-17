import os

file_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/challan/challan.py"

new_code = """
	def on_submit(self):
		if self.update_vehicle_tds and self.tds_declaration and self.vehicle_number:
			vehicle = frappe.get_doc("Hired Vehicle", self.vehicle_number)
			
			import datetime
			today = datetime.date.today()
			year = today.year
			month = today.month
			
			start_year = year
			end_year = year + 1
			if month < 4:
				start_year = year - 1
				end_year = year
				
			current_fy = f"{start_year}-{end_year}"
			
			has_decl = False
			for d in vehicle.get("tds_declarations", []):
				if d.financial_year == current_fy:
					has_decl = True
					break
					
			if not has_decl:
				vehicle.append("tds_declarations", {
					"financial_year": current_fy,
					"tds_declaration_challan": self.name,
					"tds_challan_date": self.date
				})
				vehicle.save(ignore_permissions=True)
				
			# Also set tds_challan locally so the form is completely accurate upon submit
			self.db_set('tds_challan', self.name)
"""

with open(file_path, "r") as f:
    content = f.read()

content += new_code

with open(file_path, "w") as f:
    f.write(content)

print("challan.py updated")
