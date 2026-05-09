# Copyright (c) 2026, Optimed Toplița
# API pentru Dashboard-ul hibrid (admin vs. operator)
#
# IMPORTANT: Statisticile "luna curentă" folosesc PICKUP_DATE (data ridicării),
# NU creation_date (data emiterii deal-ului).

from datetime import date

import frappe
from frappe.utils import flt, getdate, today


# ============================================================================
# HELPER: Detectarea rolului utilizatorului curent
# ============================================================================

def get_current_user_context():
	user = frappe.session.user
	roles = frappe.get_roles(user)

	is_admin = "System Manager" in roles
	is_operator = "Optimed Operator" in roles

	operator_name = None
	if user and user != "Administrator":
		operator_name = frappe.db.get_value(
			"Sales Operator",
			{"linked_user": user, "is_active": 1},
			"name"
		)

	return {
		"user": user,
		"is_admin": is_admin,
		"is_operator": is_operator,
		"operator_name": operator_name,
	}


# ============================================================================
# HELPER: Date de calcul
# ============================================================================

def _first_day_of_current_month():
	t = getdate(today())
	return t.replace(day=1)


def _last_day_of_current_month():
	from calendar import monthrange
	t = getdate(today())
	last_day = monthrange(t.year, t.month)[1]
	return t.replace(day=last_day)


# ============================================================================
# CIFRE FIRMĂ — pentru toți utilizatorii
# ============================================================================

def get_company_monthly_stats():
	from_date = _first_day_of_current_month()
	to_date = _last_day_of_current_month()

	result = frappe.db.sql("""
		SELECT
			COALESCE(SUM(revenue), 0) AS total_revenue,
			COALESCE(SUM(commission_amount), 0) AS total_commission,
			COALESCE(SUM(labor), 0) AS total_labor,
			COUNT(*) AS deals_count
		FROM `tabDeal`
		WHERE pickup_date BETWEEN %(from_date)s AND %(to_date)s
	""", {"from_date": from_date, "to_date": to_date}, as_dict=True)

	stats = result[0] if result else {}
	return {
		"total_revenue": flt(stats.get("total_revenue", 0)),
		"total_commission": flt(stats.get("total_commission", 0)),
		"total_labor": flt(stats.get("total_labor", 0)),
		"deals_count": int(stats.get("deals_count", 0)),
	}


def get_top_operator_this_month():
	from_date = _first_day_of_current_month()
	to_date = _last_day_of_current_month()

	result = frappe.db.sql("""
		SELECT
			sales_operator AS operator,
			SUM(revenue) AS total_revenue,
			COUNT(*) AS deals_count
		FROM `tabDeal`
		WHERE pickup_date BETWEEN %(from_date)s AND %(to_date)s
		  AND sales_operator IS NOT NULL
		GROUP BY sales_operator
		ORDER BY total_revenue DESC
		LIMIT 1
	""", {"from_date": from_date, "to_date": to_date}, as_dict=True)

	if not result:
		return {"operator": None, "deals_count": 0, "revenue": 0}

	return {
		"operator": result[0]["operator"],
		"deals_count": int(result[0]["deals_count"]),
		"revenue": flt(result[0]["total_revenue"]),
	}


# ============================================================================
# CIFRE PER OPERATOR
# ============================================================================

def get_operator_monthly_stats(operator_name):
	if not operator_name:
		return None

	from_date = _first_day_of_current_month()
	to_date = _last_day_of_current_month()

	result = frappe.db.sql("""
		SELECT
			COALESCE(SUM(revenue), 0) AS my_revenue,
			COALESCE(SUM(commission_amount), 0) AS my_commission,
			COALESCE(SUM(labor), 0) AS my_labor,
			COUNT(*) AS my_deals_count
		FROM `tabDeal`
		WHERE sales_operator = %(operator)s
		  AND pickup_date BETWEEN %(from_date)s AND %(to_date)s
	""", {
		"operator": operator_name,
		"from_date": from_date,
		"to_date": to_date,
	}, as_dict=True)

	stats = result[0] if result else {}
	return {
		"my_revenue": flt(stats.get("my_revenue", 0)),
		"my_commission": flt(stats.get("my_commission", 0)),
		"my_labor": flt(stats.get("my_labor", 0)),
		"my_deals_count": int(stats.get("my_deals_count", 0)),
	}


# ============================================================================
# STATUS COMISION FIRMĂ
# ============================================================================

def get_threshold_for_year(year):
	"""
	Returnează pragul de comision pentru un an dat.
	Caută întâi în child table-ul `yearly_thresholds` (override per an);
	dacă nu există, folosește pragul global ca fallback.
	"""
	from optimed_crm.optimed_crm.doctype.optimed_crm_settings.optimed_crm_settings import get_settings

	year = int(year)
	settings = get_settings()

	# Caută override pentru anul respectiv
	for row in (settings.get("yearly_thresholds") or []):
		try:
			if int(row.year) == year:
				val = flt(row.threshold)
				if val > 0:
					return val
		except (TypeError, ValueError, AttributeError):
			continue

	# Fallback la pragul global
	return flt(settings.commission_threshold) or 75000


def get_commission_status():
	from optimed_crm.optimed_crm.doctype.optimed_crm_settings.optimed_crm_settings import get_settings

	settings = get_settings()
	current_year = getdate(today()).year
	threshold = get_threshold_for_year(current_year)
	warning_pct = flt(settings.commission_warning_threshold_percent) or 70
	critical_pct = flt(settings.commission_critical_threshold_percent) or 100

	company_stats = get_company_monthly_stats()
	current = company_stats["total_revenue"]
	percentage = (current / threshold * 100) if threshold > 0 else 0

	if percentage >= critical_pct:
		status = "unlocked"
		color = "green"
		message = "Comision activ pentru toți operatorii"
	elif percentage >= warning_pct:
		status = "warning"
		color = "amber"
		remaining = threshold - current
		message = f"Mai e nevoie de {remaining:,.0f} RON".replace(",", ".")
	else:
		status = "critical"
		color = "coral"
		remaining = threshold - current
		message = f"Mai e nevoie de {remaining:,.0f} RON".replace(",", ".")

	return {
		"threshold": threshold,
		"current": current,
		"percentage": round(percentage, 1),
		"status": status,
		"color": color,
		"message": message,
	}


# ============================================================================
# CIFRE OPERAȚIONALE
# ============================================================================

def get_operational_counts():
	from optimed_crm.api.contacts_today import get_contacts_count_for_card
	to_contact_today = get_contacts_count_for_card()

	future_appointments = frappe.db.count("Appointment", filters={
		"appointment_datetime": [">=", today()],
		"is_cancelled": 0,
	})

	from_date = _first_day_of_current_month()
	to_date = _last_day_of_current_month()
	deals_this_month = frappe.db.count("Deal", filters={
		"pickup_date": ["between", [from_date, to_date]],
	})

	new_buyers = frappe.db.count("Patient", filters={
		"segment": "Cumpărător nou",
		"is_active": 1,
	})

	return {
		"to_contact_today": to_contact_today,
		"future_appointments": future_appointments,
		"deals_this_month": deals_this_month,
		"new_buyers": new_buyers,
		"month_start": str(from_date),
		"month_end": str(to_date),
	}


# ============================================================================
# SEGMENTE PACIENȚI
# ============================================================================

def get_patient_segments():
	vip = frappe.db.count("Patient", filters={"segment": "VIP", "is_active": 1})
	loyal = frappe.db.count("Patient", filters={"segment": "Fidel", "is_active": 1})
	inactive = frappe.db.count("Patient", filters={"segment": "Inactiv", "is_active": 1})

	active_under_year = frappe.db.count("Patient", filters={
		"is_active": 1,
		"days_since_last_activity": ["<=", 365],
	})

	total_patients = frappe.db.count("Patient", filters={"is_active": 1})
	patients_with_purchase = frappe.db.count("Patient", filters={
		"is_active": 1,
		"total_purchases": [">", 0],
	})
	conversion_rate = (
		round(patients_with_purchase / total_patients * 100, 1)
		if total_patients > 0 else 0
	)

	return {
		"vip": vip,
		"loyal": loyal,
		"active_under_year": active_under_year,
		"inactive": inactive,
		"conversion_rate": conversion_rate,
		"total_patients": total_patients,
	}


# ============================================================================
# TOTALURI GLOBALE — DOAR PENTRU ADMIN
# ============================================================================

def get_total_section():
	total_patients = frappe.db.count("Patient", filters={"is_active": 1})
	total_appointments = frappe.db.count("Appointment")
	total_deals = frappe.db.count("Deal")

	totals = frappe.db.sql("""
		SELECT
			COALESCE(SUM(revenue), 0) AS total_revenue,
			COALESCE(SUM(commission_amount), 0) AS total_commission,
			COALESCE(SUM(labor), 0) AS total_labor
		FROM `tabDeal`
	""", as_dict=True)

	t = totals[0] if totals else {}

	return {
		"total_patients": total_patients,
		"total_appointments": total_appointments,
		"total_deals": total_deals,
		"total_revenue": flt(t.get("total_revenue", 0)),
		"total_commission": flt(t.get("total_commission", 0)),
		"total_labor": flt(t.get("total_labor", 0)),
	}


# ============================================================================
# GRAFIC EVOLUȚIE VENITURI ANUALE — DOAR PENTRU ADMIN
# ============================================================================

MONTH_NAMES_RO = [
	"Ian", "Feb", "Mar", "Apr", "Mai", "Iun",
	"Iul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

MONTH_NAMES_RO_FULL = [
	"Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie",
	"Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie"
]


def get_available_years():
	"""
	Returnează lista anilor cu date (deal-uri cu pickup_date setat).

	Întotdeauna include anul curent, chiar dacă nu există încă date.
	Sortat descrescător (cel mai recent primul).
	"""
	rows = frappe.db.sql("""
		SELECT DISTINCT YEAR(pickup_date) AS year
		FROM `tabDeal`
		WHERE pickup_date IS NOT NULL
		ORDER BY year DESC
	""", as_dict=True)

	years = [int(r["year"]) for r in rows if r["year"]]

	current_year = getdate(today()).year
	if current_year not in years:
		years.insert(0, current_year)

	return years


def get_yearly_revenue_chart(year=None):
	"""
	Returnează datele pentru graficul de venituri lunare pentru un an dat.

	Folosește PICKUP_DATE pentru consistență cu restul Dashboard-ului.
	"""
	if year is None:
		year = getdate(today()).year
	else:
		year = int(year)

	threshold = get_threshold_for_year(year)

	# Ia toate veniturile grupate pe lună pentru anul cerut
	rows = frappe.db.sql("""
		SELECT
			MONTH(pickup_date) AS month,
			COALESCE(SUM(revenue), 0) AS revenue
		FROM `tabDeal`
		WHERE YEAR(pickup_date) = %(year)s
		  AND pickup_date IS NOT NULL
		GROUP BY MONTH(pickup_date)
		ORDER BY month
	""", {"year": year}, as_dict=True)

	revenue_by_month = {int(r["month"]): flt(r["revenue"]) for r in rows}

	current_year = getdate(today()).year
	current_month = getdate(today()).month

	# Construiește array cu 12 luni
	months_data = []
	for m in range(1, 13):
		is_current = (year == current_year and m == current_month)
		is_future = (year > current_year) or (year == current_year and m > current_month)

		months_data.append({
			"month": m,
			"name": MONTH_NAMES_RO[m - 1],
			"name_full": MONTH_NAMES_RO_FULL[m - 1],
			"revenue": revenue_by_month.get(m, 0),
			"is_future": is_future,
			"is_current": is_current,
		})

	# Calculează statistici
	# Pentru anul curent: "luni complete" = lunile trecute (NU includ luna curentă)
	# Pentru anii trecuți: "luni complete" = toate cele 12 (toate sunt trecute)
	if year == current_year:
		completed_months = [m for m in months_data if not m["is_future"] and not m["is_current"]]
	else:
		# An trecut — toate lunile sunt "complete"
		completed_months = months_data

	total_year = sum(m["revenue"] for m in months_data)
	months_completed_count = len(completed_months)
	average_monthly = (
		sum(m["revenue"] for m in completed_months) / months_completed_count
		if months_completed_count > 0 else 0
	)
	months_with_commission = sum(
		1 for m in completed_months if m["revenue"] >= threshold
	)

	# Cea mai bună lună (din toate care nu sunt viitoare)
	non_future_months = [m for m in months_data if not m["is_future"]]
	if non_future_months:
		best_month = max(non_future_months, key=lambda x: x["revenue"])
		best_month_name = best_month["name"]
		best_month_revenue = best_month["revenue"]
	else:
		best_month_name = "—"
		best_month_revenue = 0

	return {
		"year": year,
		"is_current_year": (year == current_year),
		"current_month": current_month if year == current_year else None,
		"months": months_data,
		"stats": {
			"total_year": total_year,
			"average_monthly": round(average_monthly),
			"months_with_commission": months_with_commission,
			"months_completed": months_completed_count,
			"best_month_name": best_month_name,
			"best_month_revenue": best_month_revenue,
		},
		"threshold": threshold,
		"available_years": get_available_years(),
	}


@frappe.whitelist()
def get_yearly_chart_for_year(year):
	"""
	Endpoint pentru schimbarea anului în grafic (apelat din UI prin AJAX).

	Returnează doar datele graficului pentru anul cerut, fără restul Dashboard-ului.

	IMPORTANT: Numai admin (System Manager) poate apela.
	"""
	context = get_current_user_context()
	if not context["is_admin"]:
		frappe.throw("Doar administratorii pot accesa această funcție.", frappe.PermissionError)

	return get_yearly_revenue_chart(year)


# ============================================================================
# ENDPOINT PRINCIPAL — funcția care întoarce TOATE datele pentru Dashboard
# ============================================================================

@frappe.whitelist()
def get_dashboard_data():
	"""
	Endpoint principal — returnează toate datele pentru Dashboard,
	personalizate per rol.
	"""
	from optimed_crm.optimed_crm.doctype.optimed_crm_settings.optimed_crm_settings import get_settings

	settings = get_settings()
	context = get_current_user_context()

	response = {
		"user_context": context,
		"operational": get_operational_counts(),
		"company_stats": get_company_monthly_stats(),
		"commission_status": get_commission_status(),
		"patient_segments": get_patient_segments(),
		"settings": {
			"company_name": settings.company_name,
			"greeting_text": settings.greeting_text,
			"logo_url": settings.get("logo_url") or None,
		},
		"user_display_name": _get_user_display_name(context),
	}

	# Operator stats — doar pentru operator
	if context["is_operator"] and context["operator_name"]:
		response["operator_stats"] = get_operator_monthly_stats(context["operator_name"])
	else:
		response["operator_stats"] = None

	# Top operator — vizibilitate condițională
	if context["is_admin"] or not settings.show_top_operator_to_admin_only:
		response["top_operator"] = get_top_operator_this_month()
	else:
		response["top_operator"] = None

	# Totals + Yearly revenue chart — DOAR pentru admin
	if context["is_admin"] or not settings.show_total_section_to_admin_only:
		response["totals"] = get_total_section()
		response["yearly_chart"] = get_yearly_revenue_chart()
	else:
		response["totals"] = None
		response["yearly_chart"] = None

	return response


def _get_user_display_name(context):
	if context["operator_name"]:
		return context["operator_name"]

	user = context["user"]
	if user == "Administrator":
		return "Admin"

	first_name = frappe.db.get_value("User", user, "first_name")
	return first_name or user.split("@")[0].title()
