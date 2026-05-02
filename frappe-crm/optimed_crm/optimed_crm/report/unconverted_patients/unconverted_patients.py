# Copyright (c) 2026, Optimed Toplița
# Raport: Pacienți Neconvertiți
# Au fost la consultație, dar nu au cumpărat nimic. Trebuie sunați direct.

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": _("ID"), "fieldname": "name", "fieldtype": "Link", "options": "Patient", "width": 110},
		{"label": _("Nume"), "fieldname": "patient_name", "fieldtype": "Data", "width": 200},
		{"label": _("Telefon"), "fieldname": "phone", "fieldtype": "Data", "width": 140},
		{"label": _("Email"), "fieldname": "email", "fieldtype": "Data", "width": 200},
		{
			"label": _("Programări"),
			"fieldname": "total_appointments",
			"fieldtype": "Int",
			"width": 100,
		},
		{
			"label": _("Anulate"),
			"fieldname": "cancelled_appointments",
			"fieldtype": "Int",
			"width": 90,
		},
		{
			"label": _("Prima programare"),
			"fieldname": "first_appointment_date",
			"fieldtype": "Date",
			"width": 130,
		},
		{
			"label": _("Ultima programare"),
			"fieldname": "last_appointment_date",
			"fieldtype": "Date",
			"width": 130,
		},
		{
			"label": _("Zile de la ultima programare"),
			"fieldname": "days_since_last_activity",
			"fieldtype": "Int",
			"width": 130,
		},
		{
			"label": _("Tipuri consultații"),
			"fieldname": "consultation_types",
			"fieldtype": "Small Text",
			"width": 250,
		},
		{
			"label": _("Acțiune"),
			"fieldname": "recommended_action",
			"fieldtype": "Small Text",
			"width": 280,
		},
	]


def get_data(filters):
	"""Pacienții cu segment = Neconvertit, sortați după ultima programare (cei mai recenți primii)."""
	return frappe.db.sql("""
		SELECT
			name,
			patient_name,
			phone,
			email,
			total_appointments,
			cancelled_appointments,
			first_appointment_date,
			last_appointment_date,
			days_since_last_activity,
			consultation_types,
			recommended_action
		FROM `tabPatient`
		WHERE segment = 'Neconvertit'
		  AND is_active = 1
		ORDER BY last_appointment_date DESC
	""", as_dict=True)
