# Copyright (c) 2026, Shaily Sharma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import re

class HiredVehicle(Document):
	def validate(self):
		if self.vehicle_number:
			# Strip special characters and spaces, then convert to uppercase
			cleaned = re.sub(r'[^a-zA-Z0-9]', '', self.vehicle_number)
			self.vehicle_number = cleaned.upper()
