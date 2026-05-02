# Copyright (c) 2026, Optimed Toplița
# Raport: Istoric contactări — pentru analiza retroactivă a activității

import frappe
from frappe import _
from frappe.utils import add_days, today


def execute(filters=None):
	if not filters:
		filters = {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": _("Data"), "fieldname": "contact_date", "fieldtype": "Date", "width": 110},
		{"label": _("ID Contact"), "fieldname": "name", "fieldtype": "Link", "options": "Contact Log", "width": 160},
		{"label": _("Pacient"), "fieldname": "patient", "fieldtype": "Link", "options": "Patient", "width": 110},
		{"label": _("Nume"), "fieldname": "patient_name_display", "fieldtype": "Data", "width": 200},
		{"label": _("Tip contact"), "fieldname": "contact_type", "fieldtype": "Data", "width": 200},
		{"label": _("Status"), "fieldname": "contact_status", "fieldtype": "Data", "width": 200},
		{"label": _("Operator"), "fieldname": "operator", "fieldtype": "Link", "options": "Sales Operator", "width": 110},
		{"label": _("Revenire?"), "fieldname": "follow_up_required", "fieldtype": "Check", "width": 100},
		{"label": _("Data revenire"), "fieldname": "follow_up_date", "fieldtype": "Date", "width": 120},
		{"label": _("Note"), "fieldname": "notes", "fieldtype": "Small Text", "width": 250},
	]


def get_data(filters):
	from_date = filters.get("from_date") or add_days(today(), -30)
	to_date = filters.get("to_date") or today()

	conditions = ["cl.contact_date BETWEEN %(from_date)s AND %(to_date)s"]
	params = {"from_date": from_date, "to_date": to_date}

	if filters.get("operator"):
		conditions.append("cl.operator = %(operator)s")
		params["operator"] = filters["operator"]

	if filters.get("contact_type"):
		conditions.append("cl.contact_type = %(contact_type)s")
		params["contact_type"] = filters["contact_type"]

	where_clause = " AND ".join(conditions)

	return frappe.db.sql(f"""
		SELECT
			cl.name,
			cl.contact_date,
			cl.patient,
			cl.patient_name_display,
			cl.contact_type,
			cl.contact_status,
			cl.operator,
			cl.follow_up_required,
			cl.follow_up_date,
			cl.notes
		FROM `tabContact Log` cl
		WHERE {where_clause}
		ORDER BY cl.contact_date DESC, cl.creation DESC
	""", params, as_dict=True)


def get_filters_config():
	return [
		{
			"fieldname": "from_date",
			"label": _("De la"),
			"fieldtype": "Date",
			"default": add_days(today(), -30),
			"reqd": 1,
		},
		{
			"fieldname": "to_date",
			"label": _("Până la"),
			"fieldtype": "Date",
			"default": today(),
			"reqd": 1,
		},
		{
			"fieldname": "operator",
			"label": _("Operator"),
			"fieldtype": "Link",
			"options": "Sales Operator",
		},
		{
			"fieldname": "contact_type",
			"label": _("Tip contact"),
			"fieldtype": "Select",
			"options": "\n2 zile (ebook)\n15 zile (check confort)\n6 luni (curățare)\n1 an (control + ofertă)\nReactivare (inactiv)\nFollow-up\nAlt motiv",
		},
	]
