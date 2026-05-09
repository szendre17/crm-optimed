"""
Backfill pickup_date = creation_date pentru deal-urile fără pickup_date.

Logică:
- Pentru cele 967 deal-uri istorice fără pickup_date setat, folosim
  data de emitere ca aproximare a datei ridicării.
- Asta permite ca toate deal-urile să apară în statisticile lunare.

Idempotent — rulează doar pe deal-urile cu pickup_date = NULL.

Folosim SQL UPDATE direct (nu doc.save) ca să:
- evităm validările (data ridicare >= data emitere — care ar putea bloca dacă
  există date inconsistente)
- nu re-trigger-uim hook-urile pe Patient (refresh_deal_stats — costă mult)
"""

import frappe


def run():
	print("=" * 70)
	print("BACKFILL pickup_date = creation_date")
	print("=" * 70)

	# Numără deal-urile fără pickup_date
	missing_before = frappe.db.sql(
		"SELECT COUNT(*) FROM `tabDeal` WHERE pickup_date IS NULL"
	)[0][0]
	print(f"  Deal-uri fără pickup_date înainte: {missing_before:,}")

	# Numără și câte au creation_date setat (eligibile)
	eligible = frappe.db.sql(
		"SELECT COUNT(*) FROM `tabDeal` "
		"WHERE pickup_date IS NULL AND creation_date IS NOT NULL"
	)[0][0]
	print(f"  Eligibile (au creation_date):       {eligible:,}")

	if eligible == 0:
		print("\n  Nimic de făcut — toate deal-urile fără pickup_date au și creation_date NULL.")
		return

	# Backfill SQL direct
	frappe.db.sql("""
		UPDATE `tabDeal`
		SET pickup_date = creation_date
		WHERE pickup_date IS NULL
		  AND creation_date IS NOT NULL
	""")
	frappe.db.commit()

	# Verificare
	missing_after = frappe.db.sql(
		"SELECT COUNT(*) FROM `tabDeal` WHERE pickup_date IS NULL"
	)[0][0]
	updated = missing_before - missing_after
	print(f"\n  ✓ Updated: {updated:,} deal-uri")
	print(f"  Rămase fără pickup_date (creation_date și ele NULL): {missing_after:,}")

	# Recheck statistici globale
	with_pickup = frappe.db.sql(
		"SELECT COUNT(*) FROM `tabDeal` WHERE pickup_date IS NOT NULL"
	)[0][0]
	total = frappe.db.count("Deal")
	pct = (with_pickup / total * 100) if total else 0
	print(f"\n  Stare finală: {with_pickup:,}/{total:,} ({pct:.1f}%) deal-uri au pickup_date")
	print("=" * 70)
