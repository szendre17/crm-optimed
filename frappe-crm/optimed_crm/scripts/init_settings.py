"""
SCRIPT: init_settings.py
Optimed CRM — Etapa 8.1

ROL: Inițializează DocType-ul Single "Optimed CRM Settings" cu valorile default.
     Trebuie rulat o singură dată după migrate.

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/init_settings.py').read())
  run()
"""

import frappe


DEFAULT_SETTINGS = {
	"commission_threshold": 75000,
	"commission_warning_threshold_percent": 70,
	"commission_critical_threshold_percent": 100,
	"show_top_operator_to_admin_only": 1,
	"show_total_section_to_admin_only": 1,
	"company_name": "Optimed Toplița",
	"greeting_text": "Bună dimineața",
}


def run():
	print("=" * 60)
	print("INIȚIALIZARE OPTIMED CRM SETTINGS")
	print("=" * 60)

	# Single DocType — apelăm get_single_doc
	doc = frappe.get_doc("Optimed CRM Settings")

	for field, value in DEFAULT_SETTINGS.items():
		current_value = doc.get(field)
		if current_value is None or current_value == "" or current_value == 0:
			doc.set(field, value)
			print(f"  ✓ Setat {field} = {value}")
		else:
			print(f"  ℹ {field} = {current_value} (păstrat)")

	doc.save(ignore_permissions=True)
	frappe.db.commit()

	print("\n" + "=" * 60)
	print("SETĂRI INIȚIALIZATE")
	print("=" * 60)
	print(f"\nPragul comisionului: {doc.commission_threshold:,.0f} RON")
	print(f"Prag avertisment: {doc.commission_warning_threshold_percent}%")
	print(f"Prag deblocare: {doc.commission_critical_threshold_percent}%")
	print(f"\nAccesibil în UI: /app/optimed-crm-settings")


if __name__ == "__main__":
	run()
