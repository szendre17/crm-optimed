"""
SCRIPT 2/3: create_charts.py
Optimed CRM — Etapa 6.1

ROL: Creează 3 grafice (Dashboard Charts) pentru workspace-ul Optimed CRM.

GRAFICE:
  1. Deal-uri pe lună — line chart cu trendul vânzărilor pe ultimele 12 luni
  2. Venit pe operator — bar chart cu performanța Ramonei/Roxanei/Eniko
  3. Distribuție segmente — donut chart cu cele 6 segmente de pacienți

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/create_charts.py').read())
  run()
"""

import frappe


CHARTS = [
	{
		"name": "Deal-uri pe lună",
		"chart_name": "Deal-uri pe lună",
		"chart_type": "Sum",
		"document_type": "Deal",
		"based_on": "creation_date",
		"value_based_on": "revenue",
		"timespan": "Last Year",
		"time_interval": "Monthly",
		"type": "Line",
		"is_public": 1,
		"is_standard": 0,
		"timeseries": 1,
	},
	{
		"name": "Venit pe operator",
		"chart_name": "Venit pe operator",
		"chart_type": "Group By",
		"document_type": "Deal",
		"group_by_based_on": "sales_operator",
		"group_by_type": "Sum",
		"aggregate_function_based_on": "revenue",
		"type": "Bar",
		"is_public": 1,
		"is_standard": 0,
		"timeseries": 0,
		"number_of_groups": 10,
	},
	{
		"name": "Distribuție segmente",
		"chart_name": "Distribuție segmente",
		"chart_type": "Group By",
		"document_type": "Patient",
		"group_by_based_on": "segment",
		"group_by_type": "Count",
		"type": "Donut",
		"is_public": 1,
		"is_standard": 0,
		"timeseries": 0,
		"number_of_groups": 6,
	},
]


def run():
	print("=" * 60)
	print("CREARE DASHBOARD CHARTS — Optimed CRM")
	print("=" * 60)

	created = 0
	updated = 0
	errors = 0

	for chart_def in CHARTS:
		try:
			name = chart_def["name"]

			if frappe.db.exists("Dashboard Chart", name):
				doc = frappe.get_doc("Dashboard Chart", name)
				_apply_chart_definition(doc, chart_def)
				doc.save(ignore_permissions=True)
				print(f"  ✓ Actualizat: {name}")
				updated += 1
			else:
				doc = frappe.new_doc("Dashboard Chart")
				doc.name = name
				_apply_chart_definition(doc, chart_def)
				doc.insert(ignore_permissions=True)
				print(f"  ✓ Creat: {name}")
				created += 1

		except Exception as e:
			errors += 1
			print(f"  ✗ EROARE la {chart_def.get('name')}: {str(e)[:200]}")

	frappe.db.commit()

	print("\n" + "=" * 60)
	print(f"REZULTAT: {created} create, {updated} actualizate, {errors} erori")
	print("=" * 60)
	print("URMĂTORUL PAS: rulează create_workspace.py")


def _apply_chart_definition(doc, chart_def):
	"""Aplică definiția pe document."""
	doc.chart_name = chart_def["chart_name"]
	doc.chart_type = chart_def["chart_type"]
	doc.document_type = chart_def["document_type"]
	doc.type = chart_def["type"]
	doc.is_public = chart_def.get("is_public", 1)
	doc.timeseries = chart_def.get("timeseries", 0)
	# filters_json e mandatory în Frappe v15 — gol = no filters
	doc.filters_json = chart_def.get("filters_json", "[]")

	if chart_def.get("based_on"):
		doc.based_on = chart_def["based_on"]
	if chart_def.get("value_based_on"):
		doc.value_based_on = chart_def["value_based_on"]
	if chart_def.get("timespan"):
		doc.timespan = chart_def["timespan"]
	if chart_def.get("time_interval"):
		doc.time_interval = chart_def["time_interval"]
	if chart_def.get("group_by_based_on"):
		doc.group_by_based_on = chart_def["group_by_based_on"]
	if chart_def.get("group_by_type"):
		doc.group_by_type = chart_def["group_by_type"]
	if chart_def.get("aggregate_function_based_on"):
		doc.aggregate_function_based_on = chart_def["aggregate_function_based_on"]
	if chart_def.get("number_of_groups"):
		doc.number_of_groups = chart_def["number_of_groups"]


if __name__ == "__main__":
	run()
