"""
SCRIPT: install_reports.py
Optimed CRM — Etapa 6.2

ROL: După ce fișierele de raport au fost plasate în apps/optimed_crm/optimed_crm/report/,
     acest script înregistrează rapoartele în Frappe (creează entry-urile DocType "Report").

Frappe descoperă automat rapoartele după bench migrate, dar uneori e nevoie de un sync explicit.

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/install_reports.py').read())
  run()
"""

import frappe


REPORTS = [
	# Numele Report.name TREBUIE să se mape exact pe folderul Python (după frappe.scrub).
	# De aceea folosim nume ASCII (vip_patients ↔ "VIP Patients").
	{
		"name": "VIP Patients",
		"ref_doctype": "Patient",
		"module": "Optimed CRM",
		"report_type": "Script Report",
	},
	{
		"name": "Loyal Patients",
		"ref_doctype": "Patient",
		"module": "Optimed CRM",
		"report_type": "Script Report",
	},
	{
		"name": "Inactive Patients",
		"ref_doctype": "Patient",
		"module": "Optimed CRM",
		"report_type": "Script Report",
	},
	{
		"name": "Unconverted Patients",
		"ref_doctype": "Patient",
		"module": "Optimed CRM",
		"report_type": "Script Report",
	},
	{
		"name": "New Buyers",
		"ref_doctype": "Patient",
		"module": "Optimed CRM",
		"report_type": "Script Report",
	},
	{
		"name": "Operator Performance",
		"ref_doctype": "Deal",
		"module": "Optimed CRM",
		"report_type": "Script Report",
	},
]


def run():
	print("=" * 60)
	print("ÎNREGISTRARE RAPOARTE — Optimed CRM")
	print("=" * 60)

	created = 0
	updated = 0
	errors = 0

	for r in REPORTS:
		try:
			name = r["name"]
			if frappe.db.exists("Report", name):
				print(f"  ℹ Există deja: {name}")
				updated += 1
			else:
				doc = frappe.new_doc("Report")
				doc.report_name = r["name"]
				doc.ref_doctype = r["ref_doctype"]
				doc.module = r["module"]
				doc.report_type = r["report_type"]
				doc.is_standard = "Yes"

				# Adaugă rolurile
				for role in ["System Manager", "Optimed Operator", "Optimed Viewer"]:
					doc.append("roles", {"role": role})

				doc.insert(ignore_permissions=True)
				print(f"  ✓ Creat: {name}")
				created += 1
		except Exception as e:
			errors += 1
			print(f"  ✗ EROARE la {r.get('name')}: {str(e)[:200]}")

	frappe.db.commit()

	print("\n" + "=" * 60)
	print(f"REZULTAT: {created} create, {updated} existente, {errors} erori")
	print("=" * 60)
	print("\nUrmători pași:")
	print("  1. bench --site [site] clear-cache")
	print("  2. Reîncarcă browser-ul")
	print("  3. Du-te la: Optimed CRM → meniu sus → Reports")
	print("  4. Vei vedea cele 6 rapoarte. Click pe oricare → vei vedea datele live.")


if __name__ == "__main__":
	run()
