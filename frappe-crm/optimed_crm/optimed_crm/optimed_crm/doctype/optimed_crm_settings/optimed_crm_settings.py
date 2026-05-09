# Copyright (c) 2026, Optimed Toplița and contributors

import frappe
from frappe.model.document import Document


class OptimedCRMSettings(Document):
	"""Configurări globale pentru Optimed CRM (Single DocType)."""

	def validate(self):
		"""Validări la save."""
		if self.commission_warning_threshold_percent >= self.commission_critical_threshold_percent:
			frappe.throw(
				"Pragul de avertisment trebuie să fie mai mic decât pragul de deblocare."
			)


def get_settings():
	"""
	Helper pentru a obține setările curente.
	Cached automat de Frappe pentru performanță.
	"""
	return frappe.get_cached_doc("Optimed CRM Settings", "Optimed CRM Settings")
