# Copyright (c) 2026, Optimed Toplița
# Raport: Pacienți Fideli (≥2 achiziții, sub pragul VIP)

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
		{"label": _("Achiziții"), "fieldname": "total_purchases", "fieldtype": "Int", "width": 90},
		{"label": _("Venit total"), "fieldname": "total_revenue", "fieldtype": "Currency", "options": "RON", "width": 130},
		{"label": _("Ultima achiziție"), "fieldname": "last_purchase_date", "fieldtype": "Date", "width": 130},
		{"label": _("Zile inactiv"), "fieldname": "days_since_last_activity", "fieldtype": "Int", "width": 110},
		{"label": _("Tipuri consultații"), "fieldname": "consultation_types", "fieldtype": "Small Text", "width": 200},
		{"label": _("Acțiune recomandată"), "fieldname": "recommended_action", "fieldtype": "Small Text", "width": 280},
	]


def get_data(filters):
	return frappe.db.sql("""
		SELECT
			name,
			patient_name,
			phone,
			email,
			total_purchases,
			total_revenue,
			last_purchase_date,
			days_since_last_activity,
			consultation_types,
			recommended_action
		FROM `tabPatient`
		WHERE segment = 'Fidel'
		  AND is_active = 1
		ORDER BY total_revenue DESC
	""", as_dict=True)
