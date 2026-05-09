"""
SCRIPT: check_pickup_dates.py
Optimed CRM — Verificare integritate date

ROL: Analizează deal-urile din baza de date și raportează:
  - Câte au pickup_date setat
  - Câte NU au pickup_date (NULL)
  - Distribuția pe ani (pentru a înțelege impactul pe luna curentă vs. istorice)
  - Câteva exemple concrete de deal-uri fără pickup_date

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/check_pickup_dates.py').read())
  run()

NU MODIFICĂ NIMIC — doar analizează și raportează.
"""

import frappe
from frappe.utils import getdate, today


def run():
	print("=" * 75)
	print("VERIFICARE PICKUP_DATE — Optimed CRM")
	print("=" * 75)

	_check_overall_stats()
	_check_distribution_by_year()
	_check_current_month_impact()
	_show_examples_without_pickup()
	_recommendation()


def _check_overall_stats():
	"""Statisticile globale despre pickup_date."""
	print("\n[1] STATISTICI GLOBALE")
	print("-" * 75)

	total = frappe.db.count("Deal")
	with_pickup = frappe.db.sql("""
		SELECT COUNT(*) FROM `tabDeal` WHERE pickup_date IS NOT NULL
	""")[0][0]
	without_pickup = frappe.db.sql("""
		SELECT COUNT(*) FROM `tabDeal` WHERE pickup_date IS NULL
	""")[0][0]

	pct_with = (with_pickup / total * 100) if total > 0 else 0
	pct_without = (without_pickup / total * 100) if total > 0 else 0

	print(f"  Total deal-uri în baza de date:           {total:,}")
	print(f"  Cu pickup_date setat:                     {with_pickup:,}  ({pct_with:.1f}%)")
	print(f"  FĂRĂ pickup_date (NULL):                  {without_pickup:,}  ({pct_without:.1f}%)")


def _check_distribution_by_year():
	"""Distribuția deal-urilor fără pickup_date pe ani de creare."""
	print("\n[2] DISTRIBUȚIA DEAL-URILOR FĂRĂ PICKUP_DATE — PE AN DE CREARE")
	print("-" * 75)

	rows = frappe.db.sql("""
		SELECT 
			YEAR(creation_date) AS year,
			COUNT(*) AS without_pickup,
			(SELECT COUNT(*) FROM `tabDeal` d2 
			 WHERE YEAR(d2.creation_date) = YEAR(d.creation_date)) AS total_in_year
		FROM `tabDeal` d
		WHERE pickup_date IS NULL
		GROUP BY YEAR(creation_date)
		ORDER BY year DESC
	""", as_dict=True)

	if not rows:
		print("  ✅ Nu există deal-uri fără pickup_date — toate sunt OK!")
		return

	print(f"  {'An':<8} {'Fără pickup':<14} {'Total în an':<14} {'Procent':<10}")
	print(f"  {'-'*8} {'-'*14} {'-'*14} {'-'*10}")
	for r in rows:
		year = r.get("year") or "?"
		without = r.get("without_pickup") or 0
		total = r.get("total_in_year") or 1
		pct = (without / total * 100) if total > 0 else 0
		print(f"  {year:<8} {without:<14,} {total:<14,} {pct:<10.1f}%")


def _check_current_month_impact():
	"""Impact specific pe luna curentă."""
	print("\n[3] IMPACT PE LUNA CURENTĂ (creation_date vs pickup_date)")
	print("-" * 75)

	t = getdate(today())
	from calendar import monthrange
	first_day = t.replace(day=1)
	last_day = t.replace(day=monthrange(t.year, t.month)[1])

	# Deal-uri create luna curentă
	created_this_month = frappe.db.sql("""
		SELECT COUNT(*) FROM `tabDeal`
		WHERE creation_date BETWEEN %s AND %s
	""", (first_day, last_day))[0][0]

	# Deal-uri create luna curentă FĂRĂ pickup_date
	created_no_pickup = frappe.db.sql("""
		SELECT COUNT(*) FROM `tabDeal`
		WHERE creation_date BETWEEN %s AND %s
		  AND pickup_date IS NULL
	""", (first_day, last_day))[0][0]

	# Deal-uri cu pickup_date în luna curentă
	picked_up_this_month = frappe.db.sql("""
		SELECT COUNT(*) FROM `tabDeal`
		WHERE pickup_date BETWEEN %s AND %s
	""", (first_day, last_day))[0][0]

	print(f"  Luna curentă: {first_day} → {last_day}")
	print()
	print(f"  Deal-uri create luna curentă:                  {created_this_month:,}")
	print(f"    └─ din care fără pickup_date:                {created_no_pickup:,}")
	print(f"  Deal-uri cu pickup_date luna curentă:          {picked_up_this_month:,}")
	print()
	print(f"  ► Dashboard-ul afișează: {picked_up_this_month:,} deal-uri (după pickup_date)")
	print(f"  ► Dashboard-ul VECHI afișa: {created_this_month:,} deal-uri (după creation_date)")

	if picked_up_this_month != created_this_month:
		diff = abs(picked_up_this_month - created_this_month)
		print(f"  ► Diferența: {diff:,} deal-uri")


def _show_examples_without_pickup():
	"""Arată câteva exemple concrete pentru context."""
	print("\n[4] EXEMPLE DE DEAL-URI FĂRĂ PICKUP_DATE (primele 5)")
	print("-" * 75)

	rows = frappe.db.sql("""
		SELECT name, patient, creation_date, sales_operator, revenue
		FROM `tabDeal`
		WHERE pickup_date IS NULL
		ORDER BY creation_date DESC
		LIMIT 5
	""", as_dict=True)

	if not rows:
		print("  Nu există deal-uri fără pickup_date.")
		return

	for r in rows:
		name = r.get("name", "?")
		patient = r.get("patient") or "?"
		creation = r.get("creation_date") or "?"
		operator = r.get("sales_operator") or "—"
		revenue = r.get("revenue") or 0
		print(f"  {name}  |  {creation}  |  {operator:<10}  |  {revenue:,.0f} RON  |  {patient}")


def _recommendation():
	"""Recomandare bazată pe rezultate."""
	print("\n[5] RECOMANDARE")
	print("-" * 75)

	without_pickup = frappe.db.sql("""
		SELECT COUNT(*) FROM `tabDeal` WHERE pickup_date IS NULL
	""")[0][0]
	total = frappe.db.count("Deal")

	pct = (without_pickup / total * 100) if total > 0 else 0

	if without_pickup == 0:
		print("  ✅ EXCELENT! Toate deal-urile au pickup_date setat.")
		print("     Dashboard-ul reflectă corect realitatea financiară.")
	elif pct < 5:
		print(f"  ✅ OK — doar {without_pickup:,} deal-uri ({pct:.1f}%) fără pickup_date.")
		print("     Impact minim. Continuă să setezi pickup_date pentru deal-uri noi.")
	elif pct < 30:
		print(f"  ⚠ ATENȚIE — {without_pickup:,} deal-uri ({pct:.1f}%) fără pickup_date.")
		print("     Pentru date istorice, ai 2 opțiuni:")
		print("     A) Acceptă că aceste deal-uri NU se numără în statisticile lunare")
		print("     B) Rulează un script de backfill: pickup_date = creation_date")
		print()
		print("     Spune-i lui Claude dacă vrei opțiunea B — îți pregătesc scriptul.")
	else:
		print(f"  🚨 IMPACT SEMNIFICATIV — {without_pickup:,} deal-uri ({pct:.1f}%) fără pickup_date!")
		print("     Aproape JUMĂTATE din date sunt invizibile în statistici lunare.")
		print()
		print("     RECOMANDAT: rulează script de backfill care setează")
		print("     pickup_date = creation_date pentru deal-urile istorice.")
		print("     Spune-i lui Claude pentru a primi scriptul.")

	print()
	print("=" * 75)


if __name__ == "__main__":
	run()
