"""
SCRIPT: patch_dashboard_stats_for_logo.py
Optimed CRM — Etapa 8.2

ROL: Modifică dashboard_stats.py pentru a include logo_url în răspuns.

Această modificare e mică și manuală — alternativa ar fi să livrez tot
fișierul rescris, dar e mai sigur să-l corectăm direct.

CUM SE RULEAZĂ:
  Manual — modifici apps/optimed_crm/optimed_crm/api/dashboard_stats.py
  
  Găsește în funcția get_dashboard_data() linia:
  
      "settings": {
          "company_name": settings.company_name,
          "greeting_text": settings.greeting_text,
      },
  
  Înlocuiește cu:
  
      "settings": {
          "company_name": settings.company_name,
          "greeting_text": settings.greeting_text,
          "logo_url": settings.get("logo_url") or None,
      },
"""

# Acest fișier e doar documentație. Modificarea se face manual.
# Sau alternativ rulează scriptul Python de mai jos pentru patch automat:

import os
import re


def patch_dashboard_stats():
	"""Adaugă logo_url în răspunsul settings din get_dashboard_data."""
	bench_path = "/home/frappe/frappe-bench/apps/optimed_crm"
	file_path = os.path.join(bench_path, "optimed_crm/api/dashboard_stats.py")

	if not os.path.exists(file_path):
		print(f"✗ Fișierul nu există: {file_path}")
		return

	with open(file_path, "r", encoding="utf-8") as f:
		content = f.read()

	# Verifică dacă patch-ul a fost deja aplicat
	if "logo_url" in content:
		print("ℹ Patch-ul e deja aplicat (logo_url există în fișier)")
		return

	# Caută blocul settings și adaugă logo_url
	old_block = '''		"settings": {
			"company_name": settings.company_name,
			"greeting_text": settings.greeting_text,
		},'''

	new_block = '''		"settings": {
			"company_name": settings.company_name,
			"greeting_text": settings.greeting_text,
			"logo_url": settings.get("logo_url") or None,
		},'''

	if old_block in content:
		new_content = content.replace(old_block, new_block)
		with open(file_path, "w", encoding="utf-8") as f:
			f.write(new_content)
		print(f"✓ Patch aplicat: {file_path}")
	else:
		print("⚠ Nu am găsit blocul exact de înlocuit. Aplică manual.")
		print("   Vezi instrucțiunile din capul fișierului.")


if __name__ == "__main__":
	patch_dashboard_stats()
