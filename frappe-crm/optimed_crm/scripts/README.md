# Etapa 7 — Meniu izolat + Conturi operatori

Configurează Optimed CRM ca aplicație izolată: operatorii văd doar Optimed CRM, tu vezi tot dar curat.

## Conținut

```
scripts/
├── create_users.py                  # 1. Creare conturi Ramona, Roxana, Eniko
├── restrict_system_workspaces.py    # 2. Restricționare CRM, Users, Website, etc.
├── reorganize_admin_menu.py         # 3. Reorganizare vizuală meniu admin
└── revert_changes.py                # 4. Recovery (dacă ceva merge prost)
```

## Ordine de rulare (CRITICĂ)

Strict secvențial:

```python
# Pasul 1: Conturi (PRIMUL — restul scripturilor depind de roluri existente)
exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/create_users.py').read())
run()

# Pasul 2: Restricționare workspace-uri sistem
exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/restrict_system_workspaces.py').read())
run()

# Pasul 3: Reorganizare meniu admin (opțional dar recomandat)
exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/reorganize_admin_menu.py').read())
run()

# După rulare:
# bench --site [site] clear-cache
# bench restart
```

## CONTURI — Important!

În `create_users.py`, modifică emailurile cu cele reale ÎNAINTE de a rula:

```python
USERS_TO_CREATE = [
    {"operator_name": "Ramona", "email": "ramona@optimedtoplita.ro", ...},
    {"operator_name": "Roxana", "email": "roxana@optimedtoplita.ro", ...},
    {"operator_name": "Eniko",  "email": "eniko@optimedtoplita.ro", ...},
]
```

**La rulare**, scriptul va afișa parolele temporare. Salvează-le ÎNAINTE să închizi terminalul!

Operatoarele vor fi forțate să-și schimbe parola la prima logare.

## Rezultatul final

### Pentru Ramona/Roxana/Eniko (rolul Optimed Operator):
```
🏠 Home
📊 Optimed CRM
   ├── Pacienți
   ├── Programări
   ├── Deal-uri
   ├── Operatori (read-only)
   ├── Contacte azi
   └── Rapoarte
```

### Pentru tine (rolul System Manager):
```
🏠 Home
📊 Optimed CRM         ← primul, mereu vizibil
📁 Frappe System       ← grupat, colapsibil
   ├── CRM
   ├── Users
   ├── Website
   ├── Tools
   ├── Integrations
   ├── Build
   └── Settings
```

## Test funcțional

După rulare:

1. **Test ca admin (tine):** logare normală, verifică că vezi Optimed CRM + Frappe System
2. **Test ca operator:** logare cu Ramona (parolă temporară), verifică că vede DOAR Optimed CRM
3. **Test acces direct URL:** ca operator, încearcă să accesezi `http://localhost:8000/app/user-list` → trebuie să dea Forbidden

## Recovery dacă ceva nu funcționează

Rulează `revert_changes.py`. Restaurează workspace-urile la starea inițială.

Conturile create NU sunt șterse automat — pentru asta, decomentează secțiunea finală în script.

## Securitate

Operatorii NU pot:
- Accesa Users (creare conturi)
- Accesa Settings (configurări sistem)
- Vedea Frappe CRM (workspace-ul original)
- Modifica DocType-uri (structura aplicației)
- Accesa Tools (cod custom, etc.)

Operatorii POT:
- Vedea/edita pacienți, programări, deal-uri
- Crea Contact Logs (marca contactări)
- Genera rapoarte și export Excel
- Modifica propria parolă și profil
