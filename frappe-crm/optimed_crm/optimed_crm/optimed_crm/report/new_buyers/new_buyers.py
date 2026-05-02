# Copyright (c) 2026, Optimed Toplița
# Raport: Cumpărători noi (Follow-up)
# Pacienți cu exact 1 achiziție în ultimul an.
# Oportunitate pentru a 2-a pereche, voucher, ofertă specială.

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
			"label": _("Data achiziției"),
			"fieldname": "last_purchase_date",
			"fieldtype": "Date",
			"width": 130,
		},
		{
			"label": _("Data ridicării"),
			"fieldname": "last_pickup_date",
			"fieldtype": "Date",
			"width": 130,
		},
		{
			"label": _("Zile de la ridicare"),
			"fieldname": "days_since_pickup",
			"fieldtype": "Int",
			"width": 130,
		},
		{
			"label": _("Venit"),
			"fieldname": "total_revenue",
			"fieldtype": "Currency",
			"options": "RON",
			"width": 110,
		},
		{
			"label": _("Operator vânzare"),
			"fieldname": "last_operator",
			"fieldtype": "Link",
			"options": "Sales Operator",
			"width": 130,
		},
		{
			"label": _("Acțiune"),
			"fieldname": "recommended_action",
			"fieldtype": "Small Text",
			"width": 300,
		},
	]


def get_data(filters):
	"""Cumpărătorii noi (1 achiziție), cei mai recenți primii."""
	rows = frappe.db.sql("""
		SELECT
			p.name,
			p.patient_name,
			p.phone,
			p.email,
			p.last_purchase_date,
			p.last_pickup_date,
			p.total_revenue,
			p.recommended_action,
			DATEDIFF(CURDATE(), p.last_pickup_date) AS days_since_pickup,
			(
				SELECT d.sales_operator
				FROM `tabDeal` d
				WHERE d.patient = p.name
				ORDER BY d.creation_date DESC
				LIMIT 1
			) AS last_operator
		FROM `tabPatient` p
		WHERE p.segment = 'Cumpărător nou'
		  AND p.is_active = 1
		ORDER BY p.last_purchase_date DESC
	""", as_dict=True)

	return rows
