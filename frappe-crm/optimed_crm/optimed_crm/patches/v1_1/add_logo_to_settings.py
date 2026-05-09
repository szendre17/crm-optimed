# Copyright (c) 2026, Optimed Toplița
# Patch: adaugă câmpul logo pe Optimed CRM Settings

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Adaugă câmp Attach Image pentru logo pe Optimed CRM Settings."""
	custom_fields = {
		"Optimed CRM Settings": [
			{
				"fieldname": "logo_url",
				"fieldtype": "Attach Image",
				"label": "Logo Optimed",
				"description": "Logo-ul afișat în Dashboard. Format recomandat: PNG cu fundal transparent, ~200x200px.",
				"insert_after": "company_name",
			},
		]
	}

	create_custom_fields(custom_fields, ignore_validate=True, update=True)
	frappe.db.commit()
	print("✓ Custom field logo_url adăugat pe Optimed CRM Settings")
