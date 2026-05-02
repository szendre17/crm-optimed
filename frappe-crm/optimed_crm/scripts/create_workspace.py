"""
SCRIPT 3/3: create_workspace.py
Optimed CRM — Etapa 6.1

ROL: Creează Workspace-ul "Optimed CRM" care apare în meniul stânga.
     Aranjează cele 12 Number Cards + 3 Charts într-un layout logic.

LAYOUT:
  ┌──────────────────────────────────────────────┐
  │ Optimed CRM — Dashboard                      │
  ├──────────────────────────────────────────────┤
  │ Volume                                        │
  │ [Total pac.] [Activi] [Programări] [Deal-uri]│
  ├──────────────────────────────────────────────┤
  │ Financiar                                     │
  │ [Venit total] [Luna] [Comision] [Manoperă]   │
  ├──────────────────────────────────────────────┤
  │ Operațional                                   │
  │ [Contactat azi] [Inactivi] [VIP] [Conversie] │
  ├──────────────────────────────────────────────┤
  │ Grafice                                       │
  │ [Deal-uri pe lună                          ] │
  │ [Venit operator]    [Distribuție segmente]   │
  └──────────────────────────────────────────────┘

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/create_workspace.py').read())
  run()
"""

import json

import frappe


WORKSPACE_NAME = "Optimed CRM"


def build_content():
	"""Construiește conținutul JSON al workspace-ului (layout-ul widget-urilor)."""
	content = []

	def add(item_id, item_type, data):
		content.append({"id": item_id, "type": item_type, "data": data})

	# Header principal
	add("hdr_title", "header", {
		"text": '<span class="h4"><b>Optimed CRM — Dashboard</b></span>',
		"col": 12
	})
	add("sp1", "spacer", {"col": 12})

	# === Bara de shortcuts (acces rapid la liste + rapoarte) ===
	add("hdr_shortcuts", "header", {
		"text": '<span class="h6"><b>Acces rapid</b></span>',
		"col": 12
	})
	add("sc_1", "shortcut", {"shortcut_name": "Toți pacienții", "col": 3})
	add("sc_2", "shortcut", {"shortcut_name": "Toate deal-urile", "col": 3})
	add("sc_3", "shortcut", {"shortcut_name": "Toate programările", "col": 3})
	add("sc_4", "shortcut", {"shortcut_name": "Pacienți VIP", "col": 3})
	add("sc_5", "shortcut", {"shortcut_name": "Pacienți Fideli", "col": 3})
	add("sc_6", "shortcut", {"shortcut_name": "Cumpărători noi", "col": 3})
	add("sc_7", "shortcut", {"shortcut_name": "Pacienți Inactivi (Reactivare)", "col": 3})
	add("sc_8", "shortcut", {"shortcut_name": "Pacienți Neconvertiți (Apel direct)", "col": 3})
	add("sc_9", "shortcut", {"shortcut_name": "Performanță operatori", "col": 3})
	add("sp_after_shortcuts", "spacer", {"col": 12})

	# === Grup 1: Volume ===
	add("hdr_volume", "header", {
		"text": '<span class="h6"><b>Volume</b></span>',
		"col": 12
	})
	add("nc_1", "number_card", {"number_card_name": "Total pacienți", "col": 3})
	add("nc_2", "number_card", {"number_card_name": "Pacienți activi (sub 1 an)", "col": 3})
	add("nc_3", "number_card", {"number_card_name": "Programări viitoare", "col": 3})
	add("nc_4", "number_card", {"number_card_name": "Deal-uri luna curentă", "col": 3})
	add("sp2", "spacer", {"col": 12})

	# === Grup 2: Financiar ===
	add("hdr_financial", "header", {
		"text": '<span class="h6"><b>Financiar</b></span>',
		"col": 12
	})
	add("nc_5", "number_card", {"number_card_name": "Venit total (RON)", "col": 3})
	add("nc_6", "number_card", {"number_card_name": "Venit luna curentă (RON)", "col": 3})
	add("nc_7", "number_card", {"number_card_name": "Comision total operatori (RON)", "col": 3})
	add("nc_8", "number_card", {"number_card_name": "Manoperă totală (RON)", "col": 3})
	add("sp3", "spacer", {"col": 12})

	# === Grup 3: Operațional ===
	add("hdr_operational", "header", {
		"text": '<span class="h6"><b>Operațional</b></span>',
		"col": 12
	})
	add("nc_9", "number_card", {"number_card_name": "Pacienți de contactat azi", "col": 3})
	add("nc_10", "number_card", {"number_card_name": "Pacienți inactivi (peste 365 zile)", "col": 3})
	add("nc_11", "number_card", {"number_card_name": "Pacienți VIP", "col": 3})
	add("nc_12", "number_card", {"number_card_name": "Rată conversie (% pacienți cu deal)", "col": 3})
	add("sp4", "spacer", {"col": 12})

	# === Grafice ===
	add("hdr_charts", "header", {
		"text": '<span class="h6"><b>Grafice</b></span>',
		"col": 12
	})
	add("ch_1", "chart", {"chart_name": "Deal-uri pe lună", "col": 12})
	add("ch_2", "chart", {"chart_name": "Venit pe operator", "col": 6})
	add("ch_3", "chart", {"chart_name": "Distribuție segmente", "col": 6})

	return json.dumps(content)


def get_links():
	"""Link-uri în meniul stânga sub workspace."""
	return [
		# Card 1: Date de bază
		{
			"label": "Date de bază",
			"type": "Card Break",
			"link_count": 4,
			"hidden": 0,
		},
		{"label": "Pacienți", "type": "Link", "link_to": "Patient", "link_type": "DocType", "hidden": 0},
		{"label": "Programări", "type": "Link", "link_to": "Appointment", "link_type": "DocType", "hidden": 0},
		{"label": "Deal-uri", "type": "Link", "link_to": "Deal", "link_type": "DocType", "hidden": 0},
		{"label": "Sales Operators", "type": "Link", "link_to": "Sales Operator", "link_type": "DocType", "hidden": 0},
	]


def get_shortcuts():
	"""Shortcut-uri colorate sus în workspace.
	Combinăm DocType lists + Reports — toate cu labels românești în UI."""
	return [
		# === Liste pacienți / deal-uri / programări ===
		{
			"label": "Toți pacienții",
			"link_to": "Patient",
			"type": "DocType",
			"color": "Blue",
			"doc_view": "List",
		},
		{
			"label": "Toate deal-urile",
			"link_to": "Deal",
			"type": "DocType",
			"color": "Green",
			"doc_view": "List",
		},
		{
			"label": "Toate programările",
			"link_to": "Appointment",
			"type": "DocType",
			"color": "Orange",
			"doc_view": "List",
		},
		# === Rapoarte segmente (Etapa 6.2) ===
		{
			"label": "Pacienți VIP",
			"link_to": "VIP Patients",
			"type": "Report",
			"color": "Purple",
		},
		{
			"label": "Pacienți Fideli",
			"link_to": "Loyal Patients",
			"type": "Report",
			"color": "Cyan",
		},
		{
			"label": "Cumpărători noi",
			"link_to": "New Buyers",
			"type": "Report",
			"color": "Green",
		},
		{
			"label": "Pacienți Inactivi (Reactivare)",
			"link_to": "Inactive Patients",
			"type": "Report",
			"color": "Red",
		},
		{
			"label": "Pacienți Neconvertiți (Apel direct)",
			"link_to": "Unconverted Patients",
			"type": "Report",
			"color": "Yellow",
		},
		{
			"label": "Performanță operatori",
			"link_to": "Operator Performance",
			"type": "Report",
			"color": "Pink",
		},
	]


def run():
	"""Creează (sau actualizează) workspace-ul Optimed CRM."""
	print("=" * 60)
	print("CREARE WORKSPACE — Optimed CRM Dashboard")
	print("=" * 60)

	try:
		# Șterge workspace-ul existent dacă există (mai sigur decât update)
		if frappe.db.exists("Workspace", WORKSPACE_NAME):
			frappe.delete_doc("Workspace", WORKSPACE_NAME, ignore_permissions=True, force=True)
			print(f"  Workspace existent șters pentru recreare curată")

		# Creează workspace-ul nou
		ws = frappe.new_doc("Workspace")
		ws.name = WORKSPACE_NAME
		ws.title = WORKSPACE_NAME
		ws.label = WORKSPACE_NAME
		ws.module = "Optimed CRM"
		ws.public = 1
		ws.is_hidden = 0
		ws.icon = "dashboard"
		ws.sequence_id = 50.0
		ws.content = build_content()

		# Adaugă link-urile
		for link in get_links():
			ws.append("links", link)

		# Adaugă shortcut-urile
		for shortcut in get_shortcuts():
			ws.append("shortcuts", shortcut)

		# Atașează number cards și charts
		_attach_number_cards(ws)
		_attach_charts(ws)

		ws.insert(ignore_permissions=True)
		frappe.db.commit()

		print(f"  ✓ Workspace creat: {WORKSPACE_NAME}")
		print(f"  ✓ Number Cards atașate: {len(ws.number_cards)}")
		print(f"  ✓ Charts atașate: {len(ws.charts)}")
		print(f"  ✓ Link-uri: {len(ws.links)}")
		print(f"  ✓ Shortcuts: {len(ws.shortcuts)}")

	except Exception as e:
		print(f"  ✗ EROARE: {str(e)[:300]}")
		import traceback
		traceback.print_exc()
		return

	print("\n" + "=" * 60)
	print("WORKSPACE CREAT CU SUCCES")
	print("=" * 60)
	print("\nUrmătorii pași:")
	print("  1. docker exec -it [container] bench --site [site] clear-cache")
	print("  2. Reîncarcă browser-ul")
	print("  3. Caută în meniul stânga: 'Optimed CRM'")
	print("  4. Click pe el — vei vedea Dashboard-ul cu cifrele live")
	print("=" * 60)


def _attach_number_cards(ws):
	"""Atașează cele 12 Number Cards la workspace."""
	cards = [
		"Total pacienți", "Pacienți activi (sub 1 an)", "Programări viitoare", "Deal-uri luna curentă",
		"Venit total (RON)", "Venit luna curentă (RON)", "Comision total operatori (RON)", "Manoperă totală (RON)",
		"Pacienți de contactat azi", "Pacienți inactivi (peste 365 zile)", "Pacienți VIP", "Rată conversie (% pacienți cu deal)",
	]
	for card_name in cards:
		if frappe.db.exists("Number Card", card_name):
			ws.append("number_cards", {
				"label": card_name,
				"number_card_name": card_name,
			})
		else:
			print(f"  ⚠ Number Card '{card_name}' lipsă — rulează create_number_cards.py întâi")


def _attach_charts(ws):
	"""Atașează cele 3 grafice."""
	charts = ["Deal-uri pe lună", "Venit pe operator", "Distribuție segmente"]
	for chart_name in charts:
		if frappe.db.exists("Dashboard Chart", chart_name):
			ws.append("charts", {
				"label": chart_name,
				"chart_name": chart_name,
			})
		else:
			print(f"  ⚠ Chart '{chart_name}' lipsă — rulează create_charts.py întâi")


if __name__ == "__main__":
	run()
