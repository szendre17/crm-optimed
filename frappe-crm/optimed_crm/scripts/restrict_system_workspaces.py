"""
SCRIPT 2/4: restrict_system_workspaces.py
Optimed CRM — Etapa 7

ROL: Restricționează vizibilitatea workspace-urilor sistem astfel încât:
  - Optimed Operator vede DOAR Optimed CRM
  - System Manager (admin) vede TOT (neschimbat)

Workspace-uri restricționate:
  - CRM (Frappe CRM open source)
  - Users (administrare utilizatori)
  - Website
  - Tools
  - Integrations
  - Build
  - Settings
  - HR (dacă există)
  - Accounts (dacă există)

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/restrict_system_workspaces.py').read())
  run()
"""

import frappe


# Workspace-uri pe care le restricționăm la System Manager DOAR
# Operatorii NU le mai văd
SYSTEM_WORKSPACES_TO_RESTRICT = [
	"CRM",
	"Users",
	"Website",
	"Tools",
	"Integrations",
	"Build",
	"Settings",
	"HR",
	"Accounts",
	"Buying",
	"Selling",
	"Stock",
	"Manufacturing",
	"Projects",
	"Support",
	"Quality",
	"Education",
	"Healthcare",
	"Agriculture",
	"Non Profit",
	"Hospitality",
]


def run():
	print("=" * 70)
	print("RESTRICȚIONARE WORKSPACES SISTEM")
	print("=" * 70)
	print("Operatorii Optimed vor vedea DOAR workspace-ul Optimed CRM.\n")

	restricted = 0
	skipped = 0
	errors = 0

	for ws_name in SYSTEM_WORKSPACES_TO_RESTRICT:
		try:
			if not frappe.db.exists("Workspace", ws_name):
				print(f"  ⊘ Workspace '{ws_name}' nu există — sări peste")
				skipped += 1
				continue

			ws = frappe.get_doc("Workspace", ws_name)

			# Curăță rolurile existente
			ws.roles = []

			# Adaugă DOAR System Manager
			ws.append("roles", {"role": "System Manager"})

			ws.save(ignore_permissions=True)
			print(f"  ✓ Restricționat: '{ws_name}' → doar System Manager")
			restricted += 1

		except Exception as e:
			errors += 1
			print(f"  ✗ EROARE la '{ws_name}': {str(e)[:200]}")

	frappe.db.commit()

	# Asigură că Optimed CRM are rolul Optimed Operator
	_ensure_optimed_crm_access()

	print("\n" + "=" * 70)
	print(f"REZULTAT: {restricted} restricționate, {skipped} sărite, {errors} erori")
	print("=" * 70)
	print("\nOperatorii Optimed (Ramona, Roxana, Eniko) vor vedea DOAR Optimed CRM.")
	print("Tu (System Manager) continui să vezi TOATE workspace-urile.")


def _ensure_optimed_crm_access():
	"""Asigură că workspace-ul Optimed CRM e accesibil pentru ambele roluri."""
	if not frappe.db.exists("Workspace", "Optimed CRM"):
		print("  ⚠ ATENȚIE: Workspace-ul 'Optimed CRM' nu există!")
		return

	ws = frappe.get_doc("Workspace", "Optimed CRM")

	# Verifică ce roluri are deja
	existing_roles = [r.role for r in ws.roles]

	# Asigură System Manager
	if "System Manager" not in existing_roles:
		ws.append("roles", {"role": "System Manager"})

	# Asigură Optimed Operator
	if "Optimed Operator" not in existing_roles:
		ws.append("roles", {"role": "Optimed Operator"})

	# Asigură Optimed Viewer (pentru read-only access)
	if "Optimed Viewer" not in existing_roles:
		ws.append("roles", {"role": "Optimed Viewer"})

	ws.save(ignore_permissions=True)
	print(f"\n  ✓ Optimed CRM accesibil pentru: System Manager, Optimed Operator, Optimed Viewer")


if __name__ == "__main__":
	run()
