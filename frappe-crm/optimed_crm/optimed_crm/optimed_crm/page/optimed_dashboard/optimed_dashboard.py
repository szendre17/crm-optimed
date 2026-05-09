# Copyright (c) 2026, Optimed Toplița
# Backend Python pentru pagina Dashboard
# (toate operațiunile prin API-ul optimed_crm.api.dashboard_stats)

import frappe


def get_context(context):
	"""Context pentru pagină — gol, totul e în JS."""
	context.no_cache = 1
	return context
