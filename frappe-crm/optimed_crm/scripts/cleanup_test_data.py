"""
SCRIPT 1/4: cleanup_test_data.py
Optimed CRM — Etapa 5

ROL: Șterge datele de test create în Etapele 1-4 (PAT-00001, APP-00001, DEAL-00001).

Ordine de ștergere (INVERS față de creare, din cauza dependențelor):
  1. Deal     (referențiază Patient și Operator)
  2. Appointment (referențiază Patient)
  3. Patient

Operatorii (Ramona, Roxana, Eniko) RĂMÂN — sunt date reale, nu de test.

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('apps/optimed_crm/scripts/cleanup_test_data.py').read())

Sau direct:
  docker exec -it [container] bench --site [site] execute \\
    optimed_crm.scripts.cleanup_test_data.run
"""

import frappe


def run():
	"""Rulează cleanup-ul în ordinea corectă."""
	print("=" * 60)
	print("CLEANUP DATE DE TEST — Optimed CRM")
	print("=" * 60)

	# 1. Deal-uri de test
	test_deals = frappe.get_all("Deal", filters={"created_via": "Manual"}, pluck="name")
	for deal_name in test_deals:
		try:
			frappe.delete_doc("Deal", deal_name, ignore_permissions=True, force=True)
			print(f"  ✓ Șters Deal: {deal_name}")
		except Exception as e:
			print(f"  ✗ EROARE Deal {deal_name}: {e}")

	# 2. Programări de test
	test_appointments = frappe.get_all(
		"Appointment", filters={"created_via": "Manual"}, pluck="name"
	)
	for appt_name in test_appointments:
		try:
			frappe.delete_doc("Appointment", appt_name, ignore_permissions=True, force=True)
			print(f"  ✓ Șters Appointment: {appt_name}")
		except Exception as e:
			print(f"  ✗ EROARE Appointment {appt_name}: {e}")

	# 3. Pacienți de test (cei cu created_via = Manual)
	test_patients = frappe.get_all("Patient", filters={"created_via": "Manual"}, pluck="name")
	for patient_name in test_patients:
		try:
			frappe.delete_doc("Patient", patient_name, ignore_permissions=True, force=True)
			print(f"  ✓ Șters Patient: {patient_name}")
		except Exception as e:
			print(f"  ✗ EROARE Patient {patient_name}: {e}")

	frappe.db.commit()

	# Raport final
	print("\n" + "=" * 60)
	print("STARE FINALĂ")
	print("=" * 60)
	print(f"  Pacienți rămași: {frappe.db.count('Patient')}")
	print(f"  Programări rămase: {frappe.db.count('Appointment')}")
	print(f"  Deal-uri rămase: {frappe.db.count('Deal')}")
	print(f"  Operatori rămași: {frappe.db.count('Sales Operator')} (trebuie 3: Ramona, Roxana, Eniko)")
	print("=" * 60)
	print("Cleanup complet. Poți rula importul real.")


if __name__ == "__main__":
	run()
