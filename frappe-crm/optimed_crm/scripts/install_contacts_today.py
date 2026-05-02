"""
SCRIPT: install_contacts_today.py
Optimed CRM — Etapa 6.3

ROL: După ce DocType + Page + Reports sunt instalate, acest script:
  1. Actualizează Number Card-ul "Pacienți de contactat azi" cu logica reală
  2. Adaugă shortcut "Contacte azi" în workspace
  3. Înregistrează raportul "Istoric contactări"

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/install_contacts_today.py').read())
  run()
"""

import frappe


def run():
	print("=" * 60)
	print("INSTALARE CONTACTS-TODAY — Optimed CRM")
	print("=" * 60)

	_register_report()
	_update_number_card()
	_add_workspace_shortcut()

	frappe.db.commit()
	print("\n" + "=" * 60)
	print("INSTALARE COMPLETĂ")
	print("=" * 60)
	print("\nUrmători pași:")
	print("  1. bench --site [site] clear-cache")
	print("  2. Reîncarcă browser-ul")
	print("  3. Acces direct: http://localhost:8000/app/contacts-today")
	print("  4. SAU prin shortcut: Optimed CRM workspace → Contacte azi")


def _register_report():
	"""Înregistrează raportul Istoric contactări."""
	if not frappe.db.exists("Report", "Istoric contactări"):
		doc = frappe.new_doc("Report")
		doc.report_name = "Istoric contactări"
		doc.ref_doctype = "Contact Log"
		doc.module = "Optimed CRM"
		doc.report_type = "Script Report"
		doc.is_standard = "Yes"
		for role in ["System Manager", "Optimed Operator", "Optimed Viewer"]:
			doc.append("roles", {"role": role})
		doc.insert(ignore_permissions=True)
		print("  ✓ Raport 'Istoric contactări' înregistrat")
	else:
		print("  ℹ Raport 'Istoric contactări' există deja")


def _update_number_card():
	"""
	Înlocuiește Number Card-ul placeholder pentru "Pacienți de contactat azi"
	cu unul care folosește logica reală din API.

	Pentru asta, schimbăm tipul cardului în "Custom" cu o funcție server.
	"""
	card_name = "Pacienți de contactat azi"
	if not frappe.db.exists("Number Card", card_name):
		print(f"  ⚠ Number Card '{card_name}' nu există — sări peste")
		return

	doc = frappe.get_doc("Number Card", card_name)
	# Actualizăm metoda — folosim funcția dinamică
	doc.type = "Custom"
	doc.method = "optimed_crm.api.contacts_today.get_contacts_count_for_card"
	doc.save(ignore_permissions=True)
	print(f"  ✓ Number Card '{card_name}' actualizat cu logica reală")


def _add_workspace_shortcut():
	"""Adaugă shortcut 'Contacte azi' în workspace."""
	ws_name = "Optimed CRM"
	if not frappe.db.exists("Workspace", ws_name):
		print(f"  ⚠ Workspace '{ws_name}' nu există — rulează create_workspace.py întâi")
		return

	ws = frappe.get_doc("Workspace", ws_name)

	# Verifică dacă shortcut-ul există deja
	existing = [s for s in ws.shortcuts if s.label == "Contacte azi"]
	if existing:
		print("  ℹ Shortcut 'Contacte azi' există deja în workspace")
		return

	# Adaugă shortcut nou
	ws.append("shortcuts", {
		"label": "Contacte azi",
		"link_to": "contacts-today",
		"type": "Page",
		"color": "Red",
	})
	ws.save(ignore_permissions=True)
	print("  ✓ Shortcut 'Contacte azi' adăugat în workspace")
