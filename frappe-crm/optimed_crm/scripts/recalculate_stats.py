"""
SCRIPT 3/4: recalculate_stats.py
Optimed CRM — Etapa 5

ROL: După importul masiv, recalculează pentru fiecare pacient:
  - total_appointments, cancelled_appointments
  - first_appointment_date, last_appointment_date, consultation_types
  - total_purchases, total_revenue, total_labor
  - last_purchase_date, last_pickup_date
  - days_since_last_activity
  - segment + recommended_action

DURATĂ: ~5-10 minute pentru 9.791 pacienți (depinde de hardware)

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('apps/optimed_crm/scripts/recalculate_stats.py').read())
  run()
"""

import frappe


def run():
	"""Recalculează statisticile pentru toți pacienții."""
	print("=" * 70)
	print("RECALCULARE STATISTICI PACIENȚI")
	print("=" * 70)

	patients = frappe.get_all("Patient", pluck="name")
	total = len(patients)
	print(f"Pacienți de procesat: {total}")
	print(f"Estimare durată: {total // 1000 * 1} - {total // 1000 * 2} minute\n")

	processed = 0
	errors = 0

	for i, patient_name in enumerate(patients):
		try:
			doc = frappe.get_doc("Patient", patient_name)
			doc.refresh_all_statistics()
			# Atenție: refresh_all_statistics deja face save() — care apelează
			# before_save → calculate_segment + calculate_days_since_last_activity
			processed += 1

			if (i + 1) % 200 == 0:
				frappe.db.commit()
				pct = (i + 1) / total * 100
				print(f"  Progres: {i + 1}/{total} ({pct:.1f}%) — procesați: {processed}, erori: {errors}")

		except Exception as e:
			errors += 1
			frappe.log_error(
				message=f"Eroare la recalcularea {patient_name}: {str(e)}",
				title="Bulk Patient Stats Recalculation"
			)

	frappe.db.commit()

	print("\n" + "=" * 70)
	print("RECALCULARE COMPLETĂ")
	print("=" * 70)
	print(f"Procesați cu succes: {processed}/{total}")
	print(f"Erori: {errors}")
	if errors > 0:
		print(f"Detalii erori: vezi Error Log în Frappe (sau /api/method/frappe.client.get_list?doctype=Error Log)")

	# Distribuție segmente
	print("\n--- DISTRIBUȚIE SEGMENTE ---")
	segments = frappe.db.sql("""
		SELECT segment, COUNT(*) as cnt
		FROM `tabPatient`
		GROUP BY segment
		ORDER BY cnt DESC
	""", as_dict=True)
	for s in segments:
		print(f"  {s['segment'] or '(nedefinit)'}: {s['cnt']}")

	print("=" * 70)
	print("URMĂTORUL PAS: rulează verify_import.py pentru validare")


if __name__ == "__main__":
	run()
