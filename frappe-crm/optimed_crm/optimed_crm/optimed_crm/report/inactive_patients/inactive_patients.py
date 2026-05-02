# Copyright (c) 2026, Optimed Toplița
# Raport: Pacienți Inactivi (Reactivare URGENTĂ)
# Cei care au cumpărat dar ultima achiziție a fost cu >365 zile în urmă.
# Sortați după valoare (cei mai valoroși inactivi sus = prioritate maximă reactivare).

import frappe
from frappe import _


# Praguri pentru colorarea coloanei "Zile inactiv"
URGENT_DAYS_THRESHOLD = 720  # >720 zile (>2 ani) = roșu
WARNING_DAYS_THRESHOLD = 365  # 365-720 zile = portocaliu


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
			"label": _("Zile inactiv"),
			"fieldname": "days_since_last_activity",
			"fieldtype": "Int",
			"width": 110,
		},
		{
			"label": _("Urgență"),
			"fieldname": "urgency",
			"fieldtype": "Data",
			"width": 100,
		},
		{"label": _("Total achiziții"), "fieldname": "total_purchases", "fieldtype": "Int", "width": 110},
		{
			"label": _("Venit total"),
			"fieldname": "total_revenue",
			"fieldtype": "Currency",
			"options": "RON",
			"width": 130,
		},
		{"label": _("Ultima achiziție"), "fieldname": "last_purchase_date", "fieldtype": "Date", "width": 130},
		{
			"label": _("Ultimul operator"),
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
	"""
	Returnează pacienții inactivi.

	Pentru fiecare, calculăm și ultimul operator care i-a făcut o vânzare,
	ca acel operator să-l recontacteze (relație personală).
	"""
	rows = frappe.db.sql("""
		SELECT
			p.name,
			p.patient_name,
			p.phone,
			p.email,
			p.days_since_last_activity,
			p.total_purchases,
			p.total_revenue,
			p.last_purchase_date,
			p.recommended_action,
			(
				SELECT d.sales_operator
				FROM `tabDeal` d
				WHERE d.patient = p.name
				ORDER BY d.creation_date DESC
				LIMIT 1
			) AS last_operator
		FROM `tabPatient` p
		WHERE p.segment = 'Inactiv'
		  AND p.is_active = 1
		ORDER BY p.total_revenue DESC
	""", as_dict=True)

	# Adaugă coloana de urgență cu colorare
	for row in rows:
		days = row.get("days_since_last_activity") or 0
		if days > URGENT_DAYS_THRESHOLD:
			row["urgency"] = """<span style="color: #c0392b; font-weight: 500;">URGENT</span>"""
		elif days > WARNING_DAYS_THRESHOLD:
			row["urgency"] = """<span style="color: #e67e22; font-weight: 500;">Atenție</span>"""
		else:
			row["urgency"] = """<span style="color: #95a5a6;">Normal</span>"""

	return rows
