# Copyright (c) 2026, Optimed Toplița
# Patch: adaugă câmpurile do_not_contact și do_not_contact_reason pe Patient

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Adaugă custom fields pe DocType-ul Patient pentru NU contacta."""
	custom_fields = {
		"Patient": [
			{
				"fieldname": "section_do_not_contact",
				"fieldtype": "Section Break",
				"label": "Preferințe contactare",
				"insert_after": "section_notes",
				"collapsible": 1,
			},
			{
				"fieldname": "do_not_contact",
				"fieldtype": "Check",
				"label": "NU contacta",
				"description": "Dacă e bifat, pacientul NU va apărea în listele de contactare automate.",
				"insert_after": "section_do_not_contact",
				"default": "0",
				"in_standard_filter": 1,
			},
			{
				"fieldname": "do_not_contact_reason",
				"fieldtype": "Small Text",
				"label": "Motiv NU contacta",
				"depends_on": "do_not_contact",
				"insert_after": "do_not_contact",
				"description": "Ex: 'A cerut explicit să nu fie sunat', 'Cont închis', 'Decedat', etc.",
			},
		]
	}

	create_custom_fields(custom_fields, ignore_validate=True, update=True)
	frappe.db.commit()
	print("✓ Custom fields do_not_contact adăugate pe Patient")
