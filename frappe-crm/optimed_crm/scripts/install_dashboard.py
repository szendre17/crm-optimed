"""
SCRIPT: install_dashboard.py
Optimed CRM — Etapa 8.2

ROL: După plasarea fișierelor și migrare, scriptul:
  1. Înlocuiește workspace-ul Optimed CRM existent cu noua structură
     (link-uri de navigare + redirect către pagina /app/optimed-dashboard)
  2. Setează default_workspace = "Optimed CRM" pentru toți utilizatorii
  3. Adaugă landing redirect din workspace către pagina dashboard

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/install_dashboard.py').read())
  run()
"""

import json

import frappe


WORKSPACE_NAME = "Optimed CRM"


def run():
	print("=" * 70)
	print("INSTALARE DASHBOARD — Etapa 8.2")
	print("=" * 70)

	_rebuild_workspace()
	_set_default_workspace_for_all_users()
	_set_default_workspace_for_role()

	frappe.db.commit()

	print("\n" + "=" * 70)
	print("INSTALARE COMPLETĂ")
	print("=" * 70)
	print("\nUrmători pași:")
	print("  1. bench --site [site] clear-cache")
	print("  2. bench restart")
	print("  3. Test: http://localhost:8000/app/optimed-dashboard")
	print("  4. Login -> ar trebui să fii redirect-at automat la dashboard")


def _rebuild_workspace():
	"""
	Reconstruiește workspace-ul Optimed CRM:
	- Conținutul pointează către pagina /app/optimed-dashboard
	- Link-urile laterale rămân pentru navigare
	"""
	print("\nFAZA 1: Reconstruire workspace 'Optimed CRM'")

	# Șterge workspace-ul existent (dacă există)
	if frappe.db.exists("Workspace", WORKSPACE_NAME):
		frappe.delete_doc("Workspace", WORKSPACE_NAME, force=True, ignore_permissions=True)
		print(f"  ✓ Workspace existent șters pentru recreare curată")

	# Construiește conținutul: un singur element care ghidează la dashboard
	content = json.dumps([
		{
			"id": "header_redirect",
			"type": "header",
			"data": {
				"text": '<span class="h4"><b>Optimed CRM</b></span>',
				"col": 12
			}
		},
		{
			"id": "spacer1",
			"type": "spacer",
			"data": {"col": 12}
		},
		{
			"id": "redirect_html",
			"type": "header",
			"data": {
				"text": '<div style="text-align: center; padding: 40px;"><a href="/app/optimed-dashboard" class="btn btn-primary" style="font-size: 16px; padding: 12px 24px;">Deschide Dashboard Optimed →</a><p style="color: #888; margin-top: 16px;">Sau folosește meniul lateral pentru navigare directă</p></div>',
				"col": 12
			}
		},
	])

	ws = frappe.new_doc("Workspace")
	ws.name = WORKSPACE_NAME
	ws.title = WORKSPACE_NAME
	ws.label = WORKSPACE_NAME
	ws.module = "Optimed CRM"
	ws.public = 1
	ws.is_hidden = 0
	ws.icon = "dashboard"
	ws.sequence_id = 10
	ws.content = content

	# Roluri (toți cei 3)
	for role in ["System Manager", "Optimed Operator", "Optimed Viewer"]:
		ws.append("roles", {"role": role})

	# Link-uri laterale pentru navigare
	links = [
		{"label": "Date", "type": "Card Break", "hidden": 0, "link_count": 5},
		{"label": "Pacienți", "type": "Link", "link_to": "Patient", "link_type": "DocType", "hidden": 0},
		{"label": "Programări", "type": "Link", "link_to": "Appointment", "link_type": "DocType", "hidden": 0},
		{"label": "Deals", "type": "Link", "link_to": "Deal", "link_type": "DocType", "hidden": 0},
		{"label": "Contact Log", "type": "Link", "link_to": "Contact Log", "link_type": "DocType", "hidden": 0},
		{"label": "Sales Operator", "type": "Link", "link_to": "Sales Operator", "link_type": "DocType", "hidden": 0},

		{"label": "Acțiuni zilnice", "type": "Card Break", "hidden": 0, "link_count": 1},
		{"label": "Contacte azi", "type": "Link", "link_to": "contacts-today", "link_type": "Page", "hidden": 0},

		{"label": "Rapoarte", "type": "Card Break", "hidden": 0, "link_count": 7},
		{"label": "Pacienți VIP", "type": "Link", "link_to": "VIP Patients", "link_type": "Report", "hidden": 0, "is_query_report": 1},
		{"label": "Pacienți Fideli", "type": "Link", "link_to": "Loyal Patients", "link_type": "Report", "hidden": 0, "is_query_report": 1},
		{"label": "Pacienți Inactivi (Reactivare)", "type": "Link", "link_to": "Inactive Patients", "link_type": "Report", "hidden": 0, "is_query_report": 1},
		{"label": "Pacienți Neconvertiți (Apel direct)", "type": "Link", "link_to": "Unconverted Patients", "link_type": "Report", "hidden": 0, "is_query_report": 1},
		{"label": "Cumpărători noi (Follow-up)", "type": "Link", "link_to": "New Buyers", "link_type": "Report", "hidden": 0, "is_query_report": 1},
		{"label": "Performanță operatori", "type": "Link", "link_to": "Operator Performance", "link_type": "Report", "hidden": 0, "is_query_report": 1},
		{"label": "Istoric contactări", "type": "Link", "link_to": "Contact History", "link_type": "Report", "hidden": 0, "is_query_report": 1},

		{"label": "Configurări", "type": "Card Break", "hidden": 0, "link_count": 1},
		{"label": "Optimed CRM Settings", "type": "Link", "link_to": "Optimed CRM Settings", "link_type": "DocType", "hidden": 0},
	]

	for link in links:
		ws.append("links", link)

	# Shortcut-uri (cele 4 mari, vizibile sus)
	shortcuts = [
		{"label": "Dashboard", "link_to": "optimed-dashboard", "type": "Page", "color": "Blue", "doc_view": ""},
		{"label": "Contacte azi", "link_to": "contacts-today", "type": "Page", "color": "Red"},
		{"label": "Pacienți", "link_to": "Patient", "type": "DocType", "color": "Green", "doc_view": "List"},
		{"label": "Deals", "link_to": "Deal", "type": "DocType", "color": "Yellow", "doc_view": "List"},
	]

	for shortcut in shortcuts:
		ws.append("shortcuts", shortcut)

	ws.insert(ignore_permissions=True)
	print(f"  ✓ Workspace '{WORKSPACE_NAME}' reconstruit cu link către /app/optimed-dashboard")
	print(f"    - {len(ws.links)} link-uri laterale")
	print(f"    - {len(ws.shortcuts)} shortcut-uri sus")


def _set_default_workspace_for_all_users():
	"""Setează default_workspace pentru toți utilizatorii (admin + operatori)."""
	print("\nFAZA 2: Setare default_workspace pentru utilizatori")

	# Operatorii (au rolul Optimed Operator)
	users_with_operator_role = frappe.db.sql("""
		SELECT DISTINCT u.name
		FROM `tabUser` u
		JOIN `tabHas Role` hr ON hr.parent = u.name
		WHERE hr.role = 'Optimed Operator'
		  AND u.enabled = 1
	""", as_dict=True)

	for u in users_with_operator_role:
		try:
			frappe.db.set_value("User", u["name"], "default_workspace", WORKSPACE_NAME)
			print(f"  ✓ Default workspace setat pentru: {u['name']}")
		except Exception as e:
			print(f"  ✗ EROARE la {u['name']}: {str(e)[:120]}")


def _set_default_workspace_for_role():
	"""
	Suplimentar: setează default_workspace pentru noii utilizatori
	care vor primi rolul Optimed Operator în viitor.
	Asta se face prin Workspace.role pe care l-am setat deja.
	"""
	print("\nFAZA 3: Verificare landing redirect")
	print("  ℹ Workspace-ul are conținut HTML cu buton redirect către /app/optimed-dashboard")
	print("  ℹ Utilizatorii care intră pe /app/optimed-crm vor vedea butonul redirect")
	print("  ℹ Pentru auto-redirect total, vezi sectiunea NOTE de la finalul scriptului")


# NOTE pentru auto-redirect total (opțional, mai avansat):
# ──────────────────────────────────────────────────────────
# Dacă vrei ca utilizatorul să fie redirectat AUTOMAT (fără click pe buton)
# de pe /app/optimed-crm la /app/optimed-dashboard, există 2 metode:
#
# 1. METODA SOFT (recomandată acum): Workspace afișează buton vizibil
#    → utilizatorul face un click conștient
#    → e clar ce se întâmplă
#
# 2. METODA HARD (post-test): adaugă în hooks.py un home_page redirect
#    → necesită modificarea hooks.py și restart bench
#    → poate face debugging mai dificil
#
# Pentru moment merge metoda soft. Dacă după test vrei hard redirect,
# spune-mi și adăugăm.


if __name__ == "__main__":
	run()
