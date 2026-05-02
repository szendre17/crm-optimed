# Copyright (c) 2026, Optimed Toplița
# API backend pentru pagina "Contacte de făcut azi"

import frappe
from frappe.utils import getdate, today


# Configurarea celor 4 categorii de contactări
# Fiecare are: zile minime și maxime de la ridicare (fereastra ±1)
CONTACT_CATEGORIES = [
	{
		"key": "2_days",
		"label": "2 zile (trimitere ebook)",
		"icon": "📩",
		"days_min": 1,
		"days_max": 3,
		"contact_type": "2 zile (ebook)",
		"action_description": "Trimite ebook cu ghidul de întreținere a ochelarilor",
		"color": "#3498db",
	},
	{
		"key": "15_days",
		"label": "15 zile (check confort)",
		"icon": "📞",
		"days_min": 14,
		"days_max": 16,
		"contact_type": "15 zile (check confort)",
		"action_description": "Întreabă cum se simte cu ochelarii, cere review pe Google/Facebook",
		"color": "#16a085",
	},
	{
		"key": "6_months",
		"label": "6 luni (curățare)",
		"icon": "🔧",
		"days_min": 175,
		"days_max": 185,
		"contact_type": "6 luni (curățare)",
		"action_description": "Invită la curățarea profesională gratuită cu ultrasunete",
		"color": "#e67e22",
	},
	{
		"key": "1_year",
		"label": "1 an (control + ofertă)",
		"icon": "🎯",
		"days_min": 360,
		"days_max": 370,
		"contact_type": "1 an (control + ofertă)",
		"action_description": "Programează control oftalmologic + ofertă reducere a 2-a pereche",
		"color": "#9b59b6",
	},
]

# Câte zile considerăm un Contact Log "valid" pentru a exclude un pacient
# (dacă l-am sunat acum 5 zile, nu-l mai sunăm încă o dată azi)
CONTACT_LOG_LOOKBACK_DAYS = 7


@frappe.whitelist()
def get_contacts_for_today():
	"""
	Returnează lista pacienților de contactat azi, grupați pe categorii.

	Pentru fiecare categorie (2 zile, 15 zile, 6 luni, 1 an):
	- Caută pacienții cu data ridicării (last_pickup_date) în fereastra corespunzătoare
	- Exclude cei marcați do_not_contact = 1
	- Exclude cei deja contactați pentru tipul respectiv în ultimele 7 zile

	Returnează un dicționar cu structura:
	{
		"2_days": {"label": "...", "patients": [...], "count": N},
		"15_days": {...},
		"6_months": {...},
		"1_year": {...},
		"total": N
	}
	"""
	result = {"categories": [], "total": 0, "today": str(today())}

	for category in CONTACT_CATEGORIES:
		patients = _get_patients_for_category(category)
		category_result = {
			"key": category["key"],
			"label": category["label"],
			"icon": category["icon"],
			"color": category["color"],
			"action_description": category["action_description"],
			"contact_type": category["contact_type"],
			"patients": patients,
			"count": len(patients),
		}
		result["categories"].append(category_result)
		result["total"] += len(patients)

	return result


def _get_patients_for_category(category):
	"""Returnează pacienții care intră în fereastra unei categorii."""
	rows = frappe.db.sql("""
		SELECT
			p.name AS patient_id,
			p.patient_name,
			p.phone,
			p.email,
			p.last_pickup_date,
			p.last_purchase_date,
			DATEDIFF(CURDATE(), p.last_pickup_date) AS days_since_pickup,
			(
				SELECT d.name
				FROM `tabDeal` d
				WHERE d.patient = p.name
				ORDER BY d.creation_date DESC
				LIMIT 1
			) AS last_deal,
			(
				SELECT d.sales_operator
				FROM `tabDeal` d
				WHERE d.patient = p.name
				ORDER BY d.creation_date DESC
				LIMIT 1
			) AS last_operator
		FROM `tabPatient` p
		WHERE p.is_active = 1
		  AND COALESCE(p.do_not_contact, 0) = 0
		  AND p.last_pickup_date IS NOT NULL
		  AND DATEDIFF(CURDATE(), p.last_pickup_date) BETWEEN %(days_min)s AND %(days_max)s
		  AND NOT EXISTS (
			  SELECT 1 FROM `tabContact Log` cl
			  WHERE cl.patient = p.name
			    AND cl.contact_type = %(contact_type)s
			    AND DATEDIFF(CURDATE(), cl.contact_date) <= %(lookback)s
		  )
		ORDER BY p.last_pickup_date ASC
	""", {
		"days_min": category["days_min"],
		"days_max": category["days_max"],
		"contact_type": category["contact_type"],
		"lookback": CONTACT_LOG_LOOKBACK_DAYS,
	}, as_dict=True)

	return rows


@frappe.whitelist()
def mark_as_contacted(patient_id, contact_type, contact_status, notes=None,
                      follow_up_required=0, follow_up_date=None, linked_deal=None):
	"""
	Creează un Contact Log pentru pacient.

	Apelat de pagina "Contacte azi" când utilizatorul apasă "Marchează ca sunat".
	După apelare, pacientul nu mai apare în lista pentru acea categorie 7 zile.
	"""
	# Validări de bază
	if not frappe.db.exists("Patient", patient_id):
		frappe.throw(f"Pacientul {patient_id} nu există")

	# Determină data ridicării referință (din ultimul deal)
	pickup_date = None
	if linked_deal:
		pickup_date = frappe.db.get_value("Deal", linked_deal, "pickup_date")
	else:
		# Ia ultimul deal al pacientului
		last_deal = frappe.db.sql("""
			SELECT name, pickup_date
			FROM `tabDeal`
			WHERE patient = %s
			ORDER BY creation_date DESC
			LIMIT 1
		""", patient_id, as_dict=True)
		if last_deal:
			linked_deal = last_deal[0].name
			pickup_date = last_deal[0].pickup_date

	# Creează Contact Log
	doc = frappe.new_doc("Contact Log")
	doc.patient = patient_id
	doc.contact_type = contact_type
	doc.contact_date = today()
	doc.contact_status = contact_status
	doc.linked_deal = linked_deal
	doc.linked_pickup_date = pickup_date
	doc.notes = notes
	doc.follow_up_required = int(follow_up_required) if follow_up_required else 0
	doc.follow_up_date = follow_up_date

	doc.insert(ignore_permissions=False)
	frappe.db.commit()

	return {
		"success": True,
		"contact_log_id": doc.name,
		"message": f"Contactare înregistrată pentru {patient_id}"
	}


@frappe.whitelist()
def mark_do_not_contact(patient_id, reason=None):
	"""Marchează un pacient ca 'NU contacta'. Nu va mai apărea în liste."""
	if not frappe.db.exists("Patient", patient_id):
		frappe.throw(f"Pacientul {patient_id} nu există")

	frappe.db.set_value("Patient", patient_id, {
		"do_not_contact": 1,
		"do_not_contact_reason": reason or "Marcat din pagina Contacte azi"
	})
	frappe.db.commit()

	return {
		"success": True,
		"message": f"Pacientul {patient_id} marcat ca 'NU contacta'"
	}


@frappe.whitelist()
def get_contacts_count_for_card():
	"""
	Returnează doar numărul de pacienți de contactat azi.

	Folosit de Number Card-ul din Dashboard ca să afișeze cifra live.
	"""
	total = 0
	for category in CONTACT_CATEGORIES:
		patients = _get_patients_for_category(category)
		total += len(patients)
	return total


@frappe.whitelist()
def get_today_summary():
	"""
	Returnează un sumar pentru ziua curentă:
	- Contactări făcute azi (per status)
	- Pacienți care necesită încă contactare azi
	"""
	contacts_made = frappe.db.sql("""
		SELECT contact_status, COUNT(*) AS cnt
		FROM `tabContact Log`
		WHERE contact_date = %s
		GROUP BY contact_status
	""", today(), as_dict=True)

	remaining = get_contacts_for_today()

	return {
		"contacts_made_today": contacts_made,
		"contacts_remaining": remaining["total"],
		"date": str(today()),
	}
