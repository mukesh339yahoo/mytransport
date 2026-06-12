# Copyright (c) 2026, Shaily Sharma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint

class Challan(Document):
	def before_save(self):
		self.calculate_lr_totals()
		self.calculate_tds()
		
	def calculate_lr_totals(self):
		self.total_lrs = len(self.get("lrs"))
		self.basic_freight = sum([flt(item.basic_freight) for item in self.get("lrs")])
		self.hamali_charges = sum([flt(item.hamali_charges) for item in self.get("lrs")])
		self.detention_charges = sum([flt(item.detention_charges) for item in self.get("lrs")])
		self.rto_charges = sum([flt(item.rto_charges) for item in self.get("lrs")])
		self.other_charges = sum([flt(item.other_charges) for item in self.get("lrs")])
		self.total_amount = sum([flt(item.total_amount) for item in self.get("lrs")])
		self.total_weight = sum([flt(item.total_weight) for item in self.get("lrs")])
		self.total_packages = sum([cint(item.total_packages) for item in self.get("lrs")])
		
	def calculate_tds(self):
		self.total_tds = (flt(self.total_amount) * flt(self.tds_percent)) / 100.0

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
