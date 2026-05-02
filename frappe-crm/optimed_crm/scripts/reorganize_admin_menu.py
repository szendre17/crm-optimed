"""
SCRIPT 3/4: reorganize_admin_menu.py
Optimed CRM — Etapa 7

ROL: Pentru tine (admin), reorganizează meniul stâng astfel încât:
  - Optimed CRM să fie pe primul loc, vizibil mare (sequence 10)
  - Workspace-urile sistem (CRM, Users, etc.) să fie grupate sub un parent "Frappe System"
    care e colapsibil și mai jos în meniu (sequence 100+)

Asta îți păstrează acces la TOT, dar vizual e mai curat.

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/reorganize_admin_menu.py').read())
  run()
"""

import frappe


PARENT_WORKSPACE_NAME = "Frappe System"

# Workspace-urile sistem care devin copii ai parent-ului
CHILD_WORKSPACES = [
	"CRM",
	"Users",
	"Website",
	"Tools",
	"Integrations",
	"Build",
	"Settings",
]


def run():
	print("=" * 70)
	print("REORGANIZARE MENIU ADMIN")
	print("=" * 70)

	# 1. Asigură ordinea Optimed CRM sus
	_set_optimed_crm_priority()

	# 2. Creează parent-ul "Frappe System"
	_create_parent_workspace()

	# 3. Mută workspace-urile sub parent
	_assign_children_to_parent()

	frappe.db.commit()

	print("\n" + "=" * 70)
	print("REORGANIZARE COMPLETĂ")
	print("=" * 70)
	print("\nÎn meniul stâng (ca admin) vei vedea:")
	print("  📊 Optimed CRM            ← primul, mereu vizibil")
	print("  📁 Frappe System          ← grupat, colapsibil")
	print("     ├── CRM")
	print("     ├── Users")
	print("     ├── Website")
	print("     ├── Tools")
	print("     ├── Integrations")
	print("     ├── Build")
	print("     └── Settings")


def _set_optimed_crm_priority():
	"""Setează Optimed CRM cu sequence_id 10 (primul în listă)."""
	if not frappe.db.exists("Workspace", "Optimed CRM"):
		print("  ⚠ Optimed CRM nu există — nu pot seta prioritate")
		return

	frappe.db.set_value("Workspace", "Optimed CRM", {
		"sequence_id": 10,
		"icon": "dashboard",
	})
	print("  ✓ Optimed CRM setat cu prioritate 10 (primul în meniu)")


def _create_parent_workspace():
	"""Creează workspace-ul parent 'Frappe System' pentru gruparea celor sistem."""
	if frappe.db.exists("Workspace", PARENT_WORKSPACE_NAME):
		print(f"  ℹ Parent workspace '{PARENT_WORKSPACE_NAME}' există deja")
		return

	try:
		ws = frappe.new_doc("Workspace")
		ws.name = PARENT_WORKSPACE_NAME
		ws.title = PARENT_WORKSPACE_NAME
		ws.label = PARENT_WORKSPACE_NAME
		ws.module = ""  # Nu aparține unui modul specific
		ws.public = 1
		ws.is_hidden = 0
		ws.icon = "setting"
		ws.sequence_id = 100  # Mai jos în listă
		ws.content = ""

		# DOAR System Manager îl vede (operatorii nu)
		ws.append("roles", {"role": "System Manager"})

		ws.insert(ignore_permissions=True)
		print(f"  ✓ Parent workspace creat: '{PARENT_WORKSPACE_NAME}'")
	except Exception as e:
		print(f"  ✗ EROARE creare parent: {str(e)[:200]}")


def _assign_children_to_parent():
	"""Setează parent_page pentru workspace-urile copil."""
	for ws_name in CHILD_WORKSPACES:
		try:
			if not frappe.db.exists("Workspace", ws_name):
				continue

			# Setează parent_page
			frappe.db.set_value("Workspace", ws_name, "parent_page", PARENT_WORKSPACE_NAME)

			# Asigură-te că e accesibil doar System Manager (defensiv)
			ws = frappe.get_doc("Workspace", ws_name)
			has_sys_mgr = any(r.role == "System Manager" for r in ws.roles)
			if not has_sys_mgr:
				ws.append("roles", {"role": "System Manager"})
				ws.save(ignore_permissions=True)

			print(f"    ↳ '{ws_name}' mutat sub '{PARENT_WORKSPACE_NAME}'")

		except Exception as e:
			print(f"    ✗ EROARE la '{ws_name}': {str(e)[:200]}")


if __name__ == "__main__":
	run()
