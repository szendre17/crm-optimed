# Copyright (c) 2026, Optimed Toplița and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesOperator(Document):
	"""
	SalesOperator (consultant de vânzări) la Optimed.

	Exemple curente: Ramona, Roxana, Eniko.

	Fiecare sales_operator are propriul procent de comision (default 1.5%, modificabil).
	Folosit ca Link în Deal — în loc de text liber pentru numele sales_operatorului.
	"""

	def validate(self):
		"""Validări la save."""
		if self.commission_percentage is None or self.commission_percentage < 0:
			frappe.throw("Procentul de comision trebuie să fie un număr pozitiv.")


@frappe.whitelist()
def get_sales_operator_stats(sales_operator_name, from_date=None, to_date=None):
	"""
	Returnează statistici agregate pentru un sales_operator.

	Folosit pentru dashboard-ul de performanță sales_operatori (Etapa 6).
	"""
	filters = {"sales_operator": sales_operator_name}
	if from_date:
		filters["creation_date"] = [">=", from_date]
	if to_date:
		if "creation_date" in filters:
			filters["creation_date"] = ["between", [from_date, to_date]]
		else:
			filters["creation_date"] = ["<=", to_date]

	deals = frappe.get_all(
		"Deal",
		filters=filters,
		fields=["revenue", "labor", "commission_base", "commission_amount"]
	)

	return {
		"sales_operator": sales_operator_name,
		"total_deals": len(deals),
		"total_revenue": sum(d.revenue or 0 for d in deals),
		"total_labor": sum(d.labor or 0 for d in deals),
		"total_commission_base": sum(d.commission_base or 0 for d in deals),
		"total_commission": sum(d.commission_amount or 0 for d in deals),
	}
