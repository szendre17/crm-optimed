# Copyright (c) 2026, Optimed Toplița
# Raport: Performanță operatori
# Agregare deal-uri per operator, cu filtre de perioadă (zi/săptămână/lună/trimestru/an).

import frappe
from frappe import _
from frappe.utils import getdate, today


def execute(filters=None):
	"""
	Filters disponibile:
	  - from_date: data de început (default: începutul lunii curente)
	  - to_date: data de sfârșit (default: azi)
	  - operator: filtrare la un singur operator (opțional)
	"""
	if not filters:
		filters = {}

	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"label": _("Operator"),
			"fieldname": "sales_operator",
			"fieldtype": "Link",
			"options": "Sales Operator",
			"width": 150,
		},
		{
			"label": _("Nr. deal-uri"),
			"fieldname": "deals_count",
			"fieldtype": "Int",
			"width": 110,
		},
		{
			"label": _("Venit total"),
			"fieldname": "total_revenue",
			"fieldtype": "Currency",
			"options": "RON",
			"width": 140,
		},
		{
			"label": _("Manoperă totală"),
			"fieldname": "total_labor",
			"fieldtype": "Currency",
			"options": "RON",
			"width": 140,
		},
		{
			"label": _("Bază comision"),
			"fieldname": "total_commission_base",
			"fieldtype": "Currency",
			"options": "RON",
			"width": 140,
		},
		{
			"label": _("Comision câștigat"),
			"fieldname": "total_commission",
			"fieldtype": "Currency",
			"options": "RON",
			"width": 140,
		},
		{
			"label": _("Venit mediu/deal"),
			"fieldname": "avg_revenue",
			"fieldtype": "Currency",
			"options": "RON",
			"width": 140,
		},
	]


def get_data(filters):
	"""
	Agregare per operator cu filtre de perioadă.

	Default: luna curentă (de la ziua 1 până azi).
	"""
	from_date = filters.get("from_date") or _first_day_of_current_month()
	to_date = filters.get("to_date") or today()
	operator_filter = filters.get("sales_operator")

	conditions = ["d.creation_date BETWEEN %(from_date)s AND %(to_date)s"]
	params = {"from_date": from_date, "to_date": to_date}

	if operator_filter:
		conditions.append("d.sales_operator = %(sales_operator)s")
		params["sales_operator"] = operator_filter

	where_clause = " AND ".join(conditions)

	rows = frappe.db.sql(f"""
		SELECT
			d.sales_operator,
			COUNT(*) AS deals_count,
			COALESCE(SUM(d.revenue), 0) AS total_revenue,
			COALESCE(SUM(d.labor), 0) AS total_labor,
			COALESCE(SUM(d.commission_base), 0) AS total_commission_base,
			COALESCE(SUM(d.commission_amount), 0) AS total_commission,
			COALESCE(AVG(d.revenue), 0) AS avg_revenue
		FROM `tabDeal` d
		WHERE {where_clause}
		GROUP BY d.sales_operator
		ORDER BY total_revenue DESC
	""", params, as_dict=True)

	return rows


def get_filters_config():
	"""Definește filtrele disponibile în UI-ul raportului."""
	return [
		{
			"fieldname": "from_date",
			"label": _("De la data"),
			"fieldtype": "Date",
			"default": _first_day_of_current_month(),
			"reqd": 1,
		},
		{
			"fieldname": "to_date",
			"label": _("Până la data"),
			"fieldtype": "Date",
			"default": today(),
			"reqd": 1,
		},
		{
			"fieldname": "sales_operator",
			"label": _("Operator"),
			"fieldtype": "Link",
			"options": "Sales Operator",
		},
	]


def _first_day_of_current_month():
	"""Returnează data primei zile din luna curentă."""
	t = getdate(today())
	return t.replace(day=1)
