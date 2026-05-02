# Copyright (c) 2026, Optimed Toplița and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate


class Deal(Document):
	"""
	Vânzare de ochelari/lentile/accesorii la Optimed.

	Logica financiară (din Excel):
	- revenue = (frame + lens1 + lens2 + sunglasses + accessories) - discount_amount
	- labor (manoperă) = preluată direct la import; pentru deal-uri noi se setează manual
	- commission_base = revenue - labor
	- commission_amount = commission_base × commission_percentage_used

	Triggers automate:
	- after_insert/on_update/on_trash → recalculează statisticile pacientului
	  (total_purchases, total_revenue, total_labor, last_purchase_date, segment)
	- before_save → recalculează toate sumele financiare
	- before_insert → preia procentul de comision al operatorului ca snapshot
	"""

	def before_insert(self):
		"""Înainte de creare — preia procentul de comision al operatorului."""
		self._snapshot_commission_percentage()

	def validate(self):
		"""Validări la fiecare save."""
		self._validate_dates()
		self._calculate_financials()

	def _validate_dates(self):
		"""Data ridicării nu poate fi înainte de data emiterii (warning only — date istorice pot avea inconsistențe)."""
		if self.creation_date and self.pickup_date:
			if getdate(self.pickup_date) < getdate(self.creation_date):
				# Soft warning în loc de throw — permite date istorice inconsistente
				frappe.msgprint(
					f"Atenție: data ridicării ({self.pickup_date}) e înainte de data emiterii ({self.creation_date})",
					alert=True,
					indicator="orange"
				)

	def _snapshot_commission_percentage(self):
		"""
		Salvează procentul curent al operatorului ca snapshot.
		Astfel, dacă modifici procentul operatorului mai târziu,
		deal-urile vechi rămân cu procentul lor original.
		"""
		if self.sales_operator and not self.commission_percentage_used:
			operator_doc = frappe.get_cached_doc("Sales Operator", self.sales_operator)
			self.commission_percentage_used = operator_doc.commission_percentage

	def _calculate_financials(self):
		"""
		Calculează automat toate câmpurile financiare derivate.

		Ordine de calcul:
		1. components_total = sum of all prices
		2. revenue = components_total - discount_amount
		3. labor (rămâne ce e — preluat la import sau setat manual)
		4. commission_base = revenue - labor
		5. commission_amount = commission_base × commission_percentage_used / 100
		"""
		# Total componente vândute
		components_total = (
			flt(self.frame_price)
			+ flt(self.lens1_price)
			+ flt(self.lens2_price)
			+ flt(self.sunglasses_price)
			+ flt(self.accessories_price)
		)

		# Venit = componente - reducere
		self.revenue = components_total - flt(self.discount_amount)

		# Bază comision = Venit - Manoperă
		self.commission_base = flt(self.revenue) - flt(self.labor)

		# Comision = Bază × Procent
		percentage = flt(self.commission_percentage_used) or 0
		self.commission_amount = flt(self.commission_base) * percentage / 100

	def after_insert(self):
		"""După creare — actualizează statisticile pacientului."""
		self._refresh_patient_stats()
		self._link_appointment_if_applicable()

	def on_update(self):
		"""După update — actualizează statisticile pacientului."""
		self._refresh_patient_stats()

		# Dacă pacientul s-a schimbat, actualizează și pacientul vechi
		if self.has_value_changed("patient"):
			old_doc = self.get_doc_before_save()
			if old_doc and old_doc.patient and old_doc.patient != self.patient:
				self._refresh_patient_stats(patient_name=old_doc.patient)

	def on_trash(self):
		"""După ștergere — actualizează statisticile pacientului."""
		self._refresh_patient_stats()

	def _refresh_patient_stats(self, patient_name=None):
		"""Recalculează statisticile de deal-uri pentru pacient."""
		patient_to_update = patient_name or self.patient
		if not patient_to_update:
			return

		try:
			patient_doc = frappe.get_doc("Patient", patient_to_update)
			patient_doc.refresh_deal_stats()
		except frappe.DoesNotExistError:
			pass
		except Exception as e:
			frappe.log_error(
				message=f"Eroare la actualizarea statisticilor pacientului {patient_to_update} "
				f"din deal-ul {self.name}: {str(e)}",
				title="Deal → Patient Stats Update"
			)

	def _link_appointment_if_applicable(self):
		"""
		Dacă deal-ul are o programare asociată, marchează programarea
		ca 'has_purchase=1' și salvează ID-ul deal-ului în programare.
		"""
		if not self.linked_appointment:
			return

		try:
			appt_doc = frappe.get_doc("Appointment", self.linked_appointment)
			if appt_doc.linked_deal != self.name:
				appt_doc.linked_deal = self.name
				appt_doc.has_purchase = 1
				appt_doc.save(ignore_permissions=True)
		except frappe.DoesNotExistError:
			pass


@frappe.whitelist()
def get_deals_for_patient(patient):
	"""Returnează toate deal-urile unui pacient, ordonate după dată descrescător."""
	return frappe.get_all(
		"Deal",
		filters={"patient": patient},
		fields=[
			"name",
			"creation_date",
			"pickup_date",
			"sales_operator",
			"revenue",
			"labor",
			"commission_base",
			"commission_amount",
			"discount_type",
			"is_paid"
		],
		order_by="creation_date DESC"
	)
