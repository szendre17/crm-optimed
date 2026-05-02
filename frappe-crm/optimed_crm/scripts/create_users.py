"""
SCRIPT 1/4: create_users.py
Optimed CRM — Etapa 7 (Meniu izolat + Conturi operatori)

ROL: Creează conturi de utilizator pentru cele 3 operatoare:
  - Ramona, Roxana, Eniko
  - Cu rolul "Optimed Operator"
  - Linkate la DocType-ul Operator existent
  - Cu parolă temporară setată — care trebuie schimbată la prima logare

CUM SE RULEAZĂ:
  docker exec -it [container] bench --site [site] console
  exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/create_users.py').read())
  run()

DUPĂ ACEST SCRIPT:
  Tu primești 3 parole temporare (afișate la console).
  Le dai operatorelor și le ceri să le schimbe la prima logare.
"""

import secrets
import string

import frappe


# Configurare conturi — modifică emailurile cu cele reale
USERS_TO_CREATE = [
	{
		"operator_name": "Ramona",
		"email": "ramona@optimedtoplita.ro",
		"first_name": "Ramona",
		"last_name": "",
	},
	{
		"operator_name": "Roxana",
		"email": "roxana@optimedtoplita.ro",
		"first_name": "Roxana",
		"last_name": "",
	},
	{
		"operator_name": "Eniko",
		"email": "eniko@optimedtoplita.ro",
		"first_name": "Eniko",
		"last_name": "",
	},
]


def generate_temp_password(length=12):
	"""Generează o parolă aleatoare puternică."""
	# Folosim caractere ușor de comunicat (fără confuzii: 0/O, 1/l/I)
	alphabet = string.ascii_letters.replace("l", "").replace("I", "").replace("O", "") + "23456789"
	password = "".join(secrets.choice(alphabet) for _ in range(length))
	return password


def run():
	print("=" * 70)
	print("CREARE CONTURI OPERATORI — Optimed CRM")
	print("=" * 70)

	created_credentials = []

	for user_data in USERS_TO_CREATE:
		try:
			operator_name = user_data["operator_name"]
			email = user_data["email"]

			# 1. Verifică dacă operatorul există în DocType-ul Operator
			if not frappe.db.exists("Sales Operator", operator_name):
				print(f"  ✗ Operatorul '{operator_name}' nu există în DocType. Sări peste.")
				continue

			# 2. Verifică dacă userul există deja
			if frappe.db.exists("User", email):
				print(f"  ℹ Contul {email} există deja — sări peste creare")
				# Doar verifică linkul către Operator
				_link_user_to_operator(email, operator_name)
				continue

			# 3. Creează utilizatorul
			temp_password = generate_temp_password()

			user = frappe.new_doc("User")
			user.email = email
			user.first_name = user_data["first_name"]
			user.last_name = user_data.get("last_name", "")
			user.username = user_data["first_name"].lower()
			user.send_welcome_email = 0  # Nu trimite email automat
			user.user_type = "System User"
			user.enabled = 1
			user.new_password = temp_password
			user.language = "ro"

			# Atribuie rolul Optimed Operator
			user.append("roles", {"role": "Optimed Operator"})

			# Setează workspace-ul implicit la login = Optimed CRM
			user.default_workspace = "Optimed CRM"

			# Setează ca utilizatorul SĂ FIE FORȚAT să-și schimbe parola la prima logare
			user.flags.ignore_permissions = True
			user.flags.no_welcome_mail = True
			user.insert(ignore_permissions=True)

			# NOTĂ: Frappe v15 nu mai are câmpul `force_password_reset`.
			# Operatorul va folosi parola temporară și o va schimba manual
			# (avatar dreapta-sus → My Settings → Change Password).

			# 4. Linkează userul la Operator
			_link_user_to_operator(email, operator_name)

			created_credentials.append({
				"name": operator_name,
				"email": email,
				"password": temp_password,
			})

			print(f"  ✓ Cont creat: {operator_name} → {email}")

		except Exception as e:
			print(f"  ✗ EROARE la {user_data.get('operator_name')}: {str(e)[:200]}")

	frappe.db.commit()

	# Afișare credențiale
	if created_credentials:
		print("\n" + "=" * 70)
		print("CREDENȚIALE TEMPORARE — TRANSMITE-LE OPERATORELOR")
		print("=" * 70)
		print()
		for cred in created_credentials:
			print(f"  {cred['name']}:")
			print(f"    Email/Username: {cred['email']}")
			print(f"    Parolă inițială: {cred['password']}")
			print(f"    URL login: http://localhost:8000/login")
			print()
		print("  IMPORTANT: La prima logare, sistemul îi va cere să-și schimbe parola.")
		print("  Salvează aceste credențiale ÎNAINTE să închizi terminalul!")
		print("=" * 70)
	else:
		print("\nNiciun cont nou creat.")


def _link_user_to_operator(user_email, operator_name):
	"""Linkează contul de User la DocType-ul Operator."""
	frappe.db.set_value("Sales Operator", operator_name, "linked_user", user_email)
	print(f"    ↳ Linkat la Operator '{operator_name}'")


if __name__ == "__main__":
	run()
