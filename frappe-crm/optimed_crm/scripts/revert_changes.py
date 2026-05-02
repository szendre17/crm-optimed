"""
SCRIPT 4/4: revert_changes.py
Optimed CRM — Etapa 7 (SIGURANȚĂ)

ROL: Revert all changes from Etapa 7. Recovery rapid dacă ceva nu îți place.

Restaurează:
  - Workspace-urile sistem la starea inițială (toate rolurile pot accesa)
  - Șterge parent-ul "Frappe System"
  - Restabilește parent_page = NULL pentru workspace-urile sistem

NU șterge utilizatorii creați (Ramona, Roxana, Eniko) — pentru asta există
secțiunea opțională la finalul scriptului, comentată.

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/revert_changes.py').read())
  run()
"""

import frappe


PARENT_WORKSPACE_NAME = "Frappe System"

WORKSPACES_TO_RESTORE = [
	"CRM",
	"Users",
	"Website",
	"Tools",
	"Integrations",
	"Build",
	"Settings",
	"HR",
	"Accounts",
]


def run():
	print("=" * 70)
	print("REVERT — Restaurare meniu original")
	print("=" * 70)

	# 1. Restaurează parent_page și roluri
	for ws_name in WORKSPACES_TO_RESTORE:
		try:
			if not frappe.db.exists("Workspace", ws_name):
				continue

			# Resetează parent_page
			frappe.db.set_value("Workspace", ws_name, "parent_page", "")

			# Curăță rolurile (lasă-le accesibile pentru toți)
			ws = frappe.get_doc("Workspace", ws_name)
			ws.roles = []
			ws.save(ignore_permissions=True)

			print(f"  ✓ Restaurat: '{ws_name}'")

		except Exception as e:
			print(f"  ✗ EROARE la '{ws_name}': {str(e)[:200]}")

	# 2. Șterge parent-ul "Frappe System"
	if frappe.db.exists("Workspace", PARENT_WORKSPACE_NAME):
		try:
			frappe.delete_doc("Workspace", PARENT_WORKSPACE_NAME, force=True, ignore_permissions=True)
			print(f"  ✓ Șters parent: '{PARENT_WORKSPACE_NAME}'")
		except Exception as e:
			print(f"  ✗ EROARE ștergere parent: {str(e)[:200]}")

	# 3. Restaurează Optimed CRM la sequence default
	if frappe.db.exists("Workspace", "Optimed CRM"):
		frappe.db.set_value("Workspace", "Optimed CRM", "sequence_id", 50)
		print("  ✓ Optimed CRM restaurat la sequence_id 50")

	frappe.db.commit()

	print("\n" + "=" * 70)
	print("REVERT COMPLET")
	print("=" * 70)
	print("\nMeniul tău original a fost restaurat.")
	print("Conturile create (Ramona, Roxana, Eniko) NU au fost șterse.")
	print("\nDacă vrei să ștergi și conturile, decomentează secțiunea de la finalul scriptului.")

	# OPȚIONAL: Decomentează ca să ștergi și conturile create
	# print("\nȘTERGERE CONTURI...")
	# for email in ["ramona@optimedtoplita.ro", "roxana@optimedtoplita.ro", "eniko@optimedtoplita.ro"]:
	#     if frappe.db.exists("User", email):
	#         frappe.delete_doc("User", email, force=True, ignore_permissions=True)
	#         print(f"  ✓ Șters cont: {email}")
	# frappe.db.commit()


if __name__ == "__main__":
	run()
