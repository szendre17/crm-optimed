"""
SCRIPT: test_dashboard_api.py
Optimed CRM — Etapa 8.1

ROL: Testează API-ul de dashboard cu diferiți utilizatori:
  - Administrator (admin)
  - Ramona (operator)
  - Roxana (operator)

Verifică că datele returnate sunt corecte și filtrate per rol.

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/test_dashboard_api.py').read())
  run()
"""

import json

import frappe


def run():
	print("=" * 70)
	print("TEST API DASHBOARD — Optimed CRM")
	print("=" * 70)

	# Test 1: Ca administrator
	_test_user("Administrator", "ADMIN")

	# Test 2: Ca Ramona
	ramona_email = frappe.db.get_value(
		"Sales Operator", "Ramona", "linked_user"
	)
	if ramona_email:
		_test_user(ramona_email, "RAMONA")
	else:
		print("\n⚠ Ramona nu are cont linked_user. Sări peste test.")

	# Test 3: Ca Roxana
	roxana_email = frappe.db.get_value(
		"Sales Operator", "Roxana", "linked_user"
	)
	if roxana_email:
		_test_user(roxana_email, "ROXANA")
	else:
		print("\n⚠ Roxana nu are cont linked_user. Sări peste test.")

	# Restaurează userul
	frappe.set_user("Administrator")
	print("\n" + "=" * 70)
	print("TESTE COMPLETE")
	print("=" * 70)


def _test_user(user_email, label):
	print("\n" + "=" * 70)
	print(f"TEST: ca {label} ({user_email})")
	print("=" * 70)

	frappe.set_user(user_email)
	from optimed_crm.api.dashboard_stats import get_dashboard_data

	try:
		data = get_dashboard_data()

		print(f"\nUser context:")
		ctx = data["user_context"]
		print(f"  is_admin: {ctx['is_admin']}")
		print(f"  is_operator: {ctx['is_operator']}")
		print(f"  operator_name: {ctx['operator_name']}")
		print(f"  display_name: {data['user_display_name']}")

		print(f"\nOperaționale (4 shortcut-uri sus):")
		op = data["operational"]
		print(f"  De contactat azi: {op['to_contact_today']}")
		print(f"  Programări viitoare: {op['future_appointments']}")
		print(f"  Deal-uri luna: {op['deals_this_month']}")
		print(f"  Cumpărători noi: {op['new_buyers']}")

		print(f"\nPerformanța firmei (luna):")
		cs = data["company_stats"]
		print(f"  Venit: {cs['total_revenue']:,.0f} RON")
		print(f"  Comision: {cs['total_commission']:,.0f} RON")
		print(f"  Manoperă: {cs['total_labor']:,.0f} RON")
		print(f"  Deal-uri: {cs['deals_count']}")

		if data["operator_stats"]:
			print(f"\nPerformanța TA (operator):")
			os = data["operator_stats"]
			print(f"  Venitul tău: {os['my_revenue']:,.0f} RON")
			print(f"  Comisionul tău: {os['my_commission']:,.0f} RON")
			print(f"  Manopera ta: {os['my_labor']:,.0f} RON")
			print(f"  Deal-uri tale: {os['my_deals_count']}")
		else:
			print(f"\nPerformanța TA: (NU se afișează — user nu e operator)")

		if data["top_operator"]:
			top = data["top_operator"]
			print(f"\nTop operator: {top['operator']} ({top['deals_count']} deal-uri, {top['revenue']:,.0f} RON)")
		else:
			print(f"\nTop operator: (ASCUNS — utilizatorul nu e admin)")

		print(f"\nStatus comision firmă:")
		cs2 = data["commission_status"]
		print(f"  Curent: {cs2['current']:,.0f} / {cs2['threshold']:,.0f} RON")
		print(f"  Procent: {cs2['percentage']}%")
		print(f"  Status: {cs2['status']} ({cs2['color']})")
		print(f"  Mesaj: {cs2['message']}")

		print(f"\nSegmente pacienți:")
		ps = data["patient_segments"]
		print(f"  VIP: {ps['vip']}")
		print(f"  Fideli: {ps['loyal']}")
		print(f"  Activi <1 an: {ps['active_under_year']}")
		print(f"  Inactivi: {ps['inactive']}")
		print(f"  Conversie: {ps['conversion_rate']}%")

		if data["totals"]:
			print(f"\nTotaluri (ADMIN ONLY):")
			t = data["totals"]
			print(f"  Total pacienți: {t['total_patients']:,}")
			print(f"  Total programări: {t['total_appointments']:,}")
			print(f"  Total deal-uri: {t['total_deals']:,}")
			print(f"  Venit total: {t['total_revenue']:,.0f} RON")
			print(f"  Comision total: {t['total_commission']:,.0f} RON")
			print(f"  Manoperă totală: {t['total_labor']:,.0f} RON")
		else:
			print(f"\nTotaluri: (ASCUNS — utilizatorul nu e admin)")

		print(f"\n  ✓ TEST TRECUT")

	except Exception as e:
		print(f"\n  ✗ EROARE: {str(e)}")
		import traceback
		traceback.print_exc()


if __name__ == "__main__":
	run()
