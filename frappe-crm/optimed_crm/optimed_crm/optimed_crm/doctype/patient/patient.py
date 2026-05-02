# Copyright (c) 2026, Optimed Toplița and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, flt, getdate, today


# Pragurile de segmentare — exact ca în Excel
VIP_MIN_PURCHASES = 3
VIP_MIN_REVENUE = 2000
FIDEL_MIN_PURCHASES = 2
INACTIVE_DAYS_THRESHOLD = 365


# Acțiunile recomandate pentru fiecare segment
SEGMENT_ACTIONS = {
	"VIP": "Mesaj personalizat anual + invitație la evenimente",
	"Fidel": "Reminder control + ofertă specială (a 2-a pereche, voucher)",
	"Cumpărător nou": "Verificare acomodare + ofertă a 2-a pereche",
	"Inactiv": "Campanie reactivare URGENT — WhatsApp/SMS cu ofertă",
	"Neconvertit": "Apel direct — ce nevoi are pacientul",
	"Doar contact": "Contact inițial sau marcare ca lead mort",
}


class Patient(Document):
	"""
	Pacient Optimed CRM.

	Câmpurile statistice sunt calculate automat din Appointment și Deal.
	NU trebuie modificate manual.

	Segmentarea (din CRM-ul Excel):
	- VIP: >=3 achiziții ȘI >=2000 RON
	- Fidel: >=2 achiziții (sub pragul VIP)
	- Cumpărător nou: 1 achiziție, în ultimul an
	- Inactiv: are achiziții, dar ultima >365 zile
	- Neconvertit: are programări, fără nicio achiziție
	- Doar contact: fără programări și fără achiziții
	"""

	def before_save(self):
		"""Înainte de save — recalculează segmentul și acțiunea."""
		self.calculate_segment()
		self.calculate_days_since_last_activity()

	def calculate_segment(self):
		"""Calculează segmentul pe baza statisticilor curente."""
		purchases = self.total_purchases or 0
		revenue = self.total_revenue or 0
		appointments = self.total_appointments or 0
		days_inactive = self._days_since_last_purchase()

		if purchases >= VIP_MIN_PURCHASES and revenue >= VIP_MIN_REVENUE:
			self.segment = "VIP"
		elif purchases >= 1 and days_inactive is not None and days_inactive > INACTIVE_DAYS_THRESHOLD:
			self.segment = "Inactiv"
		elif purchases >= FIDEL_MIN_PURCHASES:
			self.segment = "Fidel"
		elif purchases == 1:
			self.segment = "Cumpărător nou"
		elif appointments > 0 and purchases == 0:
			self.segment = "Neconvertit"
		else:
			self.segment = "Doar contact"

		self.recommended_action = SEGMENT_ACTIONS.get(self.segment, "")

	def calculate_days_since_last_activity(self):
		"""Calculează zilele de la ultima activitate."""
		dates = []
		if self.last_appointment_date:
			dates.append(getdate(self.last_appointment_date))
		if self.last_pickup_date:
			dates.append(getdate(self.last_pickup_date))
		if self.last_purchase_date:
			dates.append(getdate(self.last_purchase_date))

		if dates:
			most_recent = max(dates)
			self.days_since_last_activity = date_diff(today(), most_recent)
		else:
			self.days_since_last_activity = None

	def _days_since_last_purchase(self):
		if not self.last_purchase_date:
			return None
		return date_diff(today(), getdate(self.last_purchase_date))

	def refresh_appointment_stats(self):
		"""Recalculează statisticile de programări."""
		appointments = frappe.get_all(
			"Appointment",
			filters={"patient": self.name},
			fields=["appointment_datetime", "consultation_type", "is_cancelled"]
		)

		self.total_appointments = len(appointments)
		self.cancelled_appointments = sum(1 for a in appointments if a.is_cancelled)

		valid_appointments = [a for a in appointments if not a.is_cancelled]

		if valid_appointments:
			dates = [getdate(a.appointment_datetime) for a in valid_appointments]
			self.first_appointment_date = min(dates)
			self.last_appointment_date = max(dates)

			types = sorted(set(a.consultation_type for a in valid_appointments if a.consultation_type))
			self.consultation_types = ", ".join(types) if types else None
		else:
			self.first_appointment_date = None
			self.last_appointment_date = None
			self.consultation_types = None

		self.save(ignore_permissions=True)

	def refresh_deal_stats(self):
		"""
		Recalculează statisticile de deal-uri (vânzări) ale pacientului.

		Apelată automat din Deal.after_insert / on_update / on_trash.
		Calculează:
		- total_purchases (count)
		- total_revenue (sumă)
		- total_labor (sumă)
		- last_purchase_date (max data emiterii)
		- last_pickup_date (max data ridicării)

		Apoi salvează (declanșează before_save → calculate_segment).
		"""
		deals = frappe.get_all(
			"Deal",
			filters={"patient": self.name},
			fields=["creation_date", "pickup_date", "revenue", "labor"]
		)

		self.total_purchases = len(deals)
		self.total_revenue = sum(flt(d.revenue) for d in deals)
		self.total_labor = sum(flt(d.labor) for d in deals)

		if deals:
			creation_dates = [getdate(d.creation_date) for d in deals if d.creation_date]
			pickup_dates = [getdate(d.pickup_date) for d in deals if d.pickup_date]

			self.last_purchase_date = max(creation_dates) if creation_dates else None
			self.last_pickup_date = max(pickup_dates) if pickup_dates else None
		else:
			self.last_purchase_date = None
			self.last_pickup_date = None

		self.save(ignore_permissions=True)

	def refresh_all_statistics(self):
		"""Recalculează TOATE statisticile (programări + deal-uri)."""
		self.refresh_appointment_stats()
		self.refresh_deal_stats()


@frappe.whitelist()
def recalculate_all_segments():
	"""
	Recalculează segmentul pentru TOȚI pacienții.

	Se rulează zilnic (scheduled task) ca să prindem tranziția
	"Cumpărător nou" → "Inactiv" la 365 zile.

	Manual: bench --site [site] execute optimed_crm.optimed_crm.doctype.patient.patient.recalculate_all_segments
	"""
	patients = frappe.get_all("Patient", filters={"is_active": 1}, pluck="name")
	count = 0
	errors = 0
	for patient_name in patients:
		try:
			doc = frappe.get_doc("Patient", patient_name)
			doc.calculate_segment()
			doc.calculate_days_since_last_activity()
			doc.save(ignore_permissions=True)
			count += 1
		except Exception as e:
			errors += 1
			frappe.log_error(
				message=f"Eroare la recalcularea segmentului pentru {patient_name}: {str(e)}",
				title="Patient Segment Recalculation"
			)
	frappe.db.commit()
	return f"Recalculat segmentul pentru {count} pacienți. Erori: {errors}"


@frappe.whitelist()
def refresh_all_patient_statistics():
	"""
	FORȚEAZĂ recalcularea TUTUROR statisticilor (programări + deal-uri) pentru toți pacienții.

	Folosit:
	- După import masiv din Excel
	- Pentru sincronizare manuală dacă apar discrepanțe

	Atenție: pentru 9.791 pacienți poate dura 5-10 minute.

	Manual: bench --site [site] execute optimed_crm.optimed_crm.doctype.patient.patient.refresh_all_patient_statistics
	"""
	patients = frappe.get_all("Patient", pluck="name")
	count = 0
	errors = 0
	for i, patient_name in enumerate(patients):
		try:
			doc = frappe.get_doc("Patient", patient_name)
			doc.refresh_all_statistics()
			count += 1

			# Commit la fiecare 100 pacienți pentru a evita transaction prea mare
			if i > 0 and i % 100 == 0:
				frappe.db.commit()
				print(f"Procesat {i} pacienți...")
		except Exception as e:
			errors += 1
			frappe.log_error(
				message=f"Eroare la refresh statistici pentru {patient_name}: {str(e)}",
				title="Patient Full Statistics Refresh"
			)

	frappe.db.commit()
	return f"Recalculat TOATE statisticile pentru {count} pacienți. Erori: {errors}"
