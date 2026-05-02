# Copyright (c) 2026, Optimed Toplița and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class Appointment(Document):
	"""
	Programare oftalmologică sau optică pentru un pacient.

	Fluxul automat:
	- Când se creează/modifică/șterge → statisticile pacientului se recalculează
	- Când se atașează un Deal → has_purchase devine 1
	- Câmpul patient_name_display se completează automat din Patient (fetch_from)

	Sursa istorică: Calendly export (vezi calendly_event_id pentru deduplicare)
	"""

	def validate(self):
		"""Rulează la fiecare save — validări de business."""
		self._validate_cancellation()
		self._sync_has_purchase()

	def _validate_cancellation(self):
		"""Dacă e anulată, trebuie să aibă motiv. Dacă nu e anulată, ștergem motivul."""
		if self.is_cancelled and not self.cancellation_reason:
			frappe.throw("Pentru o programare anulată este obligatoriu să specifici motivul anulării.")
		if not self.is_cancelled:
			self.cancellation_reason = None

	def _sync_has_purchase(self):
		"""Setează has_purchase=1 dacă există un Deal legat."""
		self.has_purchase = 1 if self.linked_deal else 0

	def after_insert(self):
		"""După creare — actualizează statisticile pacientului."""
		self._refresh_patient_stats()

	def on_update(self):
		"""După update — actualizează statisticile pacientului."""
		self._refresh_patient_stats()

		# Dacă pacientul s-a schimbat (rar, dar posibil), actualizează și pacientul vechi
		if self.has_value_changed("patient"):
			old_patient = self.get_doc_before_save()
			if old_patient and old_patient.patient and old_patient.patient != self.patient:
				self._refresh_patient_stats(patient_name=old_patient.patient)

	def on_trash(self):
		"""După ștergere — actualizează statisticile pacientului."""
		self._refresh_patient_stats()

	def _refresh_patient_stats(self, patient_name=None):
		"""
		Recalculează statisticile de programări pentru pacient.

		Apelează metoda de pe Patient care va recalcula:
		- total_appointments
		- cancelled_appointments
		- first_appointment_date
		- last_appointment_date
		- consultation_types
		- segment (eventual se schimbă)
		"""
		patient_to_update = patient_name or self.patient
		if not patient_to_update:
			return

		try:
			patient_doc = frappe.get_doc("Patient", patient_to_update)
			patient_doc.refresh_appointment_stats()
		except frappe.DoesNotExistError:
			# Pacientul a fost șters — ignorăm
			pass
		except Exception as e:
			frappe.log_error(
				message=f"Eroare la actualizarea statisticilor pacientului {patient_to_update} "
				f"din programarea {self.name}: {str(e)}",
				title="Appointment → Patient Stats Update"
			)


@frappe.whitelist()
def get_appointments_for_patient(patient):
	"""
	Returnează toate programările unui pacient, ordonate descrescător după dată.

	Folosit pentru afișare rapidă în formularul Patient și în rapoarte.
	"""
	return frappe.get_all(
		"Appointment",
		filters={"patient": patient},
		fields=[
			"name",
			"appointment_datetime",
			"consultation_type",
			"is_cancelled",
			"cancellation_reason",
			"attended",
			"has_purchase",
			"linked_deal"
		],
		order_by="appointment_datetime DESC"
	)
