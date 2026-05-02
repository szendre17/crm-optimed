# Copyright (c) 2026, Optimed Toplița and contributors

import frappe
from frappe.model.document import Document


class ContactLog(Document):
	"""
	Înregistrare a unei contactări către un pacient.

	Folosit pentru:
	- Tracking-ul contactărilor post-ridicare (2 zile, 15 zile, 6 luni, 1 an)
	- Reactivare pacienți inactivi
	- Follow-up general

	Pagina "Contacte de făcut azi" exclude pacienții cu un Contact Log
	pentru tipul respectiv în ultimele 7 zile (ca să nu apară duplicat).
	"""

	def validate(self):
		"""Validări la save."""
		self._populate_pickup_date()
		self._auto_set_operator()

	def _populate_pickup_date(self):
		"""Dacă e legat de un deal, ia data ridicării din el."""
		if self.linked_deal and not self.linked_pickup_date:
			pickup = frappe.db.get_value("Deal", self.linked_deal, "pickup_date")
			if pickup:
				self.linked_pickup_date = pickup

	def _auto_set_operator(self):
		"""Dacă nu e setat operator manual, încearcă să-l ia din linked_user."""
		if not self.operator:
			# Caută operatorul asociat utilizatorului curent
			user = frappe.session.user
			operator = frappe.db.get_value(
				"Sales Operator",
				{"linked_user": user, "is_active": 1},
				"name"
			)
			if operator:
				self.operator = operator
