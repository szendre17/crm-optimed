"""
SCRIPT 1/3: create_number_cards.py
Optimed CRM — Etapa 6.1

ROL: Creează cele 12 Number Cards din Dashboard (statistici live).

Fiecare Number Card e un widget care afișează o cifră calculată dinamic
din baza de date. Cifrele se actualizează automat la fiecare load al paginii.

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/create_number_cards.py').read())
  run()

DUPĂ ACEST SCRIPT:
  Rulezi create_charts.py care va crea graficele.
  Apoi create_workspace.py care le va aranja pe pagina Dashboard.
"""

import frappe


# Definițiile celor 12 Number Cards
# Fiecare card are: nume, etichetă, doctype-ul interogat, funcția (count/sum/avg), filtre
NUMBER_CARDS = [
	# ======== GRUP 1: VOLUME ========
	{
		"name": "Total pacienți",
		"label": "Total pacienți",
		"document_type": "Patient",
		"function": "Count",
		"filters_json": "[]",
		"color": "#3498db",  # blue
		"is_public": 1,
	},
	{
		"name": "Pacienți activi",
		"label": "Pacienți activi (sub 1 an)",
		"document_type": "Patient",
		"function": "Count",
		"filters_json": '[["Patient","is_active","=",1],["Patient","days_since_last_activity","<=",365]]',
		"color": "#27ae60",  # green
		"is_public": 1,
	},
	{
		"name": "Programări viitoare",
		"label": "Programări viitoare",
		"document_type": "Appointment",
		"function": "Count",
		"filters_json": '[["Appointment","is_cancelled","=",0],["Appointment","appointment_datetime","Timespan","next year"]]',
		"dynamic_filters_json": "",
		"color": "#e67e22",  # orange
		"is_public": 1,
	},
	{
		"name": "Deal-uri luna curentă",
		"label": "Deal-uri luna curentă",
		"document_type": "Deal",
		"function": "Count",
		"filters_json": '[["Deal","creation_date","Timespan","this month"]]',
		"dynamic_filters_json": "",
		"color": "#9b59b6",  # purple
		"is_public": 1,
	},

	# ======== GRUP 2: FINANCIAR ========
	{
		"name": "Venit total",
		"label": "Venit total (RON)",
		"document_type": "Deal",
		"function": "Sum",
		"aggregate_function_based_on": "revenue",
		"filters_json": "[]",
		"color": "#16a085",  # teal
		"is_public": 1,
	},
	{
		"name": "Venit luna curentă",
		"label": "Venit luna curentă (RON)",
		"document_type": "Deal",
		"function": "Sum",
		"aggregate_function_based_on": "revenue",
		"filters_json": '[["Deal","creation_date","Timespan","this month"]]',
		"dynamic_filters_json": "",
		"color": "#27ae60",
		"is_public": 1,
	},
	{
		"name": "Comision total operatori",
		"label": "Comision total operatori (RON)",
		"document_type": "Deal",
		"function": "Sum",
		"aggregate_function_based_on": "commission_amount",
		"filters_json": "[]",
		"color": "#f39c12",  # gold
		"is_public": 1,
	},
	{
		"name": "Manoperă totală",
		"label": "Manoperă totală (RON)",
		"document_type": "Deal",
		"function": "Sum",
		"aggregate_function_based_on": "labor",
		"filters_json": "[]",
		"color": "#34495e",  # dark
		"is_public": 1,
	},

	# ======== GRUP 3: OPERAȚIONAL ========
	{
		"name": "Pacienți de contactat azi",
		"label": "Pacienți de contactat azi",
		"document_type": "Patient",
		"function": "Count",
		# Pentru moment cardul afișează pacienții cu activitate la ziua 2/15/180/365
		# Calculul exact se face în Etapa 6.3 — aici doar un placeholder rezonabil
		"filters_json": '[["Patient","is_active","=",1],["Patient","days_since_last_activity","in","2,15,180,365"]]',
		"color": "#e74c3c",  # red
		"is_public": 1,
	},
	{
		"name": "Pacienți inactivi",
		"label": "Pacienți inactivi (peste 365 zile)",
		"document_type": "Patient",
		"function": "Count",
		"filters_json": '[["Patient","segment","=","Inactiv"]]',
		"color": "#c0392b",  # dark red
		"is_public": 1,
	},
	{
		"name": "Pacienți VIP",
		"label": "Pacienți VIP",
		"document_type": "Patient",
		"function": "Count",
		"filters_json": '[["Patient","segment","=","VIP"]]',
		"color": "#f1c40f",  # yellow gold
		"is_public": 1,
	},
	{
		"name": "Rată conversie",
		"label": "Rată conversie (% pacienți cu deal)",
		"document_type": "Patient",
		"function": "Count",
		"filters_json": '[["Patient","total_purchases",">",0]]',
		"color": "#2ecc71",  # bright green
		"is_public": 1,
	},
]


def run():
	"""Creează toate Number Cards. Idempotent — sare peste cele existente."""
	print("=" * 60)
	print("CREARE NUMBER CARDS — Optimed CRM Dashboard")
	print("=" * 60)

	created = 0
	updated = 0
	errors = 0

	for card_def in NUMBER_CARDS:
		try:
			label = card_def["label"]

			# Frappe v15 folosește `label` ca autoname → căutăm după label, nu după name
			existing = frappe.db.get_value("Number Card", {"label": label}, "name")
			if existing:
				doc = frappe.get_doc("Number Card", existing)
				_apply_card_definition(doc, card_def)
				doc.save(ignore_permissions=True)
				print(f"  ✓ Actualizat: {label}")
				updated += 1
			else:
				doc = frappe.new_doc("Number Card")
				_apply_card_definition(doc, card_def)
				doc.insert(ignore_permissions=True)
				print(f"  ✓ Creat: {label}")
				created += 1

		except Exception as e:
			errors += 1
			print(f"  ✗ EROARE la {card_def.get('label')}: {str(e)[:200]}")

	frappe.db.commit()

	print("\n" + "=" * 60)
	print(f"REZULTAT: {created} create, {updated} actualizate, {errors} erori")
	print("=" * 60)
	print("URMĂTORUL PAS: rulează create_charts.py")


def _apply_card_definition(doc, card_def):
	"""Aplică definiția cardului pe document."""
	doc.label = card_def["label"]
	doc.document_type = card_def["document_type"]
	doc.function = card_def["function"]
	doc.filters_json = card_def.get("filters_json", "[]")
	doc.dynamic_filters_json = card_def.get("dynamic_filters_json", "")
	doc.is_public = card_def.get("is_public", 1)
	doc.show_percentage_stats = 0
	doc.color = card_def.get("color")
	if card_def.get("aggregate_function_based_on"):
		doc.aggregate_function_based_on = card_def["aggregate_function_based_on"]


if __name__ == "__main__":
	run()
