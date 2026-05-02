"""
Detectare familii — versiune corectă conform GHID_UTILIZARE.xlsx.

Conform documentației originale:
> "Unii pacienți includ de fapt MAI MULTE persoane din aceeași familie
>  (sotie programează pentru soț, părinte pentru copii, telefon comun de casă).
>  Numele real al fiecărui deal e în coloana Associated_Contact_Original din DEALS."

Logica: pentru fiecare Patient, mă uit în deal-urile lui la `original_associated_contact`.
Dacă există ≥2 nume distincte → pacientul e un GRUP DE FAMILIE.

Marchează acești pacienți cu un family_group_id unic (FAM-XXXXX).
Așteptat: ~855 pacienți-familie:
  - 646 grupuri de 2 persoane
  - 158 grupuri de 3 persoane
  - 31 grupuri de 4 persoane
  - 18 grupuri de 5 persoane
  - 2 grupuri mari (7 și 9 persoane)
"""

import re
import frappe
from collections import defaultdict


def normalize_name(s):
	"""Normalizează un nume pentru comparație: uppercase, spațiile compactate."""
	if not s:
		return None
	cleaned = re.sub(r"\s+", " ", s.strip().upper())
	return cleaned or None


def run():
	print("=" * 70)
	print("DETECTARE FAMILII — Optimed CRM (per pacient)")
	print("=" * 70)

	# Reset family_group_id existent
	frappe.db.sql("UPDATE `tabPatient` SET family_group_id = NULL")
	frappe.db.commit()
	print("Reset family_group_id pentru toți pacienții.\n")

	# Pentru fiecare pacient, colectez Original_Associated_Contact unice din deal-uri
	patients = frappe.db.sql("SELECT name, patient_name FROM `tabPatient`", as_dict=True)
	print(f"Total pacienți: {len(patients)}")

	deals = frappe.db.sql("""
		SELECT patient, original_associated_contact
		FROM `tabDeal`
		WHERE original_associated_contact IS NOT NULL AND original_associated_contact != ''
	""", as_dict=True)
	print(f"Total deal-uri cu original_associated_contact: {len(deals)}\n")

	# Grupez deal-urile pe pacient
	patient_to_contacts = defaultdict(set)
	for d in deals:
		nm = normalize_name(d["original_associated_contact"])
		if nm:
			patient_to_contacts[d["patient"]].add(nm)

	# Detectez pacienții-familie: au ≥2 nume distincte în deal-uri
	family_patients = {}
	size_distribution = defaultdict(int)
	for patient_name, contacts in patient_to_contacts.items():
		if len(contacts) >= 2:
			family_patients[patient_name] = contacts
			size_distribution[len(contacts)] += 1

	print(f"Pacienți-familie detectați: {len(family_patients)}")
	print()
	print("Distribuție după mărimea familiei:")
	for size in sorted(size_distribution.keys()):
		print(f"  Familii de {size} persoane: {size_distribution[size]}")
	print()

	# Asignează family_group_id (FAM-00001, ...) — fiecare pacient-familie primește propriul ID
	family_counter = 0
	for patient_name in sorted(family_patients.keys()):
		family_counter += 1
		family_id = f"FAM-{str(family_counter).zfill(5)}"
		frappe.db.set_value(
			"Patient", patient_name, "family_group_id", family_id, update_modified=False
		)

	frappe.db.commit()

	print("=" * 70)
	print(f"FAMILII MARCATE: {family_counter}")
	print(f"TOTAL PERSOANE ÎN FAMILII: {sum(len(c) for c in family_patients.values())}")
	print("=" * 70)

	# Top 10 cele mai mari familii
	top = sorted(family_patients.items(), key=lambda x: -len(x[1]))[:10]
	print("Top 10 pacienți-familie (după număr de persoane):")
	for pname, contacts in top:
		patient_doc = next((p for p in patients if p["name"] == pname), None)
		display_name = patient_doc["patient_name"] if patient_doc else pname
		print(f"  {pname} ({display_name}): {len(contacts)} persoane")
		preview = sorted(contacts)[:4]
		for ct in preview:
			print(f"    - {ct}")
		if len(contacts) > 4:
			print(f"    ... și încă {len(contacts) - 4}")
	print("=" * 70)

	return family_counter
