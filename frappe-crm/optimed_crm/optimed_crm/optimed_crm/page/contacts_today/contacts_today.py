# Copyright (c) 2026, Optimed Toplița
# Backend Python pentru pagina Contacte azi
# (toate operațiunile se fac prin API-ul din optimed_crm.api.contacts_today)

import frappe


def get_context(context):
	"""Context pentru pagină — momentan gol, totul e în JS."""
	context.no_cache = 1
	return context
