import os

file_path = "/Users/shailysharma/CursorAI/mytransport/development/frappe-bench/apps/mytransport/mytransport/mytransport/doctype/challan/challan.py"

new_code = """# Copyright (c) 2026, Shaily Sharma and contributors
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
"""

with open(file_path, "w") as f:
    f.write(new_code)

print("challan.py updated")
