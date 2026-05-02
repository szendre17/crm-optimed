"""
SCRIPT 4/4: verify_import.py
Optimed CRM — Etapa 5

ROL: Compară cifrele din Frappe cu cele din Dashboard-ul Excel-ului.
     Dacă totul e identic, importul e validat. Diferențele sunt afișate clar.

CIFRE DIN DASHBOARD EXCEL (referință):
  - Total pacienți: 9.791
  - Total programări: 13.300 (din care anulate: variabil)
  - Total deal-uri: 9.567
  - Venit total: 5.206.726 RON
  - Conversie: 44.2% (pacienți cu deal-uri / total pacienți)

  Distribuție segmente:
  - VIP: 366
  - Fidel: 1.798
  - Cumpărător nou: 576
  - Inactiv: 2.814
  - Neconvertit: 4.054
  - Doar contact: 183

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('apps/optimed_crm/scripts/verify_import.py').read())
  run()
"""

import frappe
from frappe.utils import flt


# Valorile din Dashboard Excel (referință pentru comparație)
EXPECTED = {
	"total_patients": 9791,
	"total_appointments": 13300,
	"total_deals": 9567,
	"total_revenue": 5206726,
	"segments": {
		"VIP": 366,
		"Fidel": 1798,
		"Cumpărător nou": 576,
		"Inactiv": 2814,
		"Neconvertit": 4054,
		"Doar contact": 183,
	},
}

# Toleranță pentru diferențe (din cauza rotunjirilor și a câtorva înregistrări cu erori)
TOLERANCE_COUNT = 50  # ±50 înregistrări per categorie e OK
TOLERANCE_REVENUE = 5000  # ±5.000 RON e OK


def check(label, actual, expected, tolerance=0, is_currency=False):
	"""Compară o valoare. Returnează True dacă e în toleranță."""
	diff = actual - expected
	abs_diff = abs(diff)
	is_ok = abs_diff <= tolerance

	icon = "✓" if is_ok else "✗"
	if is_currency:
		print(f"  {icon} {label}: {actual:,.2f} RON (Excel: {expected:,} RON, diff: {diff:+.2f})")
	else:
		print(f"  {icon} {label}: {actual:,} (Excel: {expected:,}, diff: {diff:+d})")

	return is_ok


def run():
	print("=" * 70)
	print("VERIFICARE IMPORT — Frappe vs Excel")
	print("=" * 70)

	all_ok = True

	# 1. Totaluri
	print("\n--- TOTALURI ---")
	patient_count = frappe.db.count("Patient")
	appointment_count = frappe.db.count("Appointment")
	deal_count = frappe.db.count("Deal")

	all_ok &= check("Pacienți", patient_count, EXPECTED["total_patients"], TOLERANCE_COUNT)
	all_ok &= check("Programări", appointment_count, EXPECTED["total_appointments"], TOLERANCE_COUNT)
	all_ok &= check("Deal-uri", deal_count, EXPECTED["total_deals"], TOLERANCE_COUNT)

	# 2. Venit total
	print("\n--- VENIT ---")
	total_revenue_result = frappe.db.sql("""
		SELECT SUM(revenue) as total FROM `tabDeal`
	""", as_dict=True)
	total_revenue = flt(total_revenue_result[0]["total"]) if total_revenue_result else 0
	all_ok &= check("Venit total", total_revenue, EXPECTED["total_revenue"], TOLERANCE_REVENUE, is_currency=True)

	# 3. Distribuție segmente
	print("\n--- DISTRIBUȚIE SEGMENTE ---")
	actual_segments = dict(frappe.db.sql("""
		SELECT segment, COUNT(*) FROM `tabPatient` GROUP BY segment
	"""))

	for segment, expected_count in EXPECTED["segments"].items():
		actual_count = actual_segments.get(segment, 0)
		all_ok &= check(f"  {segment}", actual_count, expected_count, TOLERANCE_COUNT)

	# 4. Conversie
	print("\n--- CONVERSIE ---")
	patients_with_purchase = frappe.db.count("Patient", filters={"total_purchases": [">", 0]})
	conversion_rate = (patients_with_purchase / patient_count * 100) if patient_count else 0
	expected_conversion = 44.2
	conversion_ok = abs(conversion_rate - expected_conversion) < 1.0
	icon = "✓" if conversion_ok else "✗"
	print(f"  {icon} Rata conversie: {conversion_rate:.1f}% (Excel: {expected_conversion}%)")
	all_ok &= conversion_ok

	# 5. Performanță operatori
	print("\n--- PERFORMANȚĂ OPERATORI ---")
	operator_stats = frappe.db.sql("""
		SELECT sales_operator,
		       COUNT(*) as deals_count,
		       SUM(revenue) as total_revenue,
		       SUM(commission_amount) as total_commission
		FROM `tabDeal`
		GROUP BY sales_operator
		ORDER BY total_revenue DESC
	""", as_dict=True)
	for op in operator_stats:
		print(f"  {op['sales_operator']}: {op['deals_count']} deal-uri, "
		      f"{flt(op['total_revenue']):,.0f} RON venit, "
		      f"{flt(op['total_commission']):,.2f} RON comision")

	# 6. Familii detectate
	print("\n--- FAMILII (telefon comun) ---")
	families_count = frappe.db.sql("""
		SELECT COUNT(DISTINCT family_group_id) as cnt
		FROM `tabPatient`
		WHERE family_group_id IS NOT NULL
	""")[0][0] or 0
	patients_in_families = frappe.db.count("Patient", filters={"family_group_id": ["!=", ""]})
	print(f"  Familii detectate: {families_count}")
	print(f"  Pacienți în familii: {patients_in_families}")

	# Concluzie
	print("\n" + "=" * 70)
	if all_ok:
		print("✓ TOATE VERIFICĂRILE TRECUTE — IMPORT VALIDAT CU SUCCES")
	else:
		print("✗ UNELE VERIFICĂRI AU EȘUAT — vezi diferențele de mai sus")
		print("\nCauze posibile:")
		print("  - Câteva înregistrări cu date invalide au fost sărite (vezi log import)")
		print("  - Diferențe în calcul: Excel rotunjește diferit decât Frappe")
		print("  - Date duplicate în Excel (același pacient apare de 2 ori)")
		print("\nDiferențele sub TOLERANCE_COUNT=50 sunt acceptabile.")
	print("=" * 70)


if __name__ == "__main__":
	run()
