# CRM Optimed — Frappe CRM + Optimed Dashboard

Sistem CRM pentru **Optimed Toplița** — cabinet oftalmologic și magazin de optică.

Proiectul construiește un app Frappe custom (`optimed_crm`) pe deasupra Frappe CRM standard, cu un **Dashboard nou specific Optimed** care înlocuiește interfața default și oferă o vedere hibridă (admin / operator).

## Optimed Dashboard

Dashboard-ul nou (la `/app/optimed-dashboard`) e centrul operațional zilnic și se adaptează automat în funcție de rolul utilizatorului:

### Pentru admin (System Manager)
- **4 shortcut-uri sus** (acțiuni rapide):
  - De contactat azi (link la pagina contacts-today)
  - Programări viitoare
  - Deals luna curentă
  - Cumpărători noi (follow-up)
- **Performanța firmei** (luna curentă, după `pickup_date`): venit, comision, manoperă, deal-uri + **Top operator** (cine a vândut cel mai mult)
- **Status comision firmă** (banner colorat verde/portocaliu/roșu) cu prag configurabil per an
- **Segmente pacienți** (VIP, Fideli, Activi, Inactivi, Conversie %)
- **Total** (cifre globale): pacienți, programări, deals, venit, comision, manoperă
- **Evoluție venituri lunare** — grafic anual cu 12 bare:
  - Bare verzi pentru lunile peste prag, albastre sub prag, gri pentru viitor
  - Linie roșie întreruptă la pragul lunii respective
  - **Selector de an** (dropdown) cu toți anii care au date — admin poate compara
  - 4 statistici sub grafic (Total an, Medie lunară, Luni cu comision, Luna cea mai bună)

### Pentru operator (Optimed Operator — Ramona, Roxana, Eniko)
- Aceleași 4 shortcut-uri sus
- **Performanța firmei** — fără Top operator (anonim)
- **Performanța TA** (mov, evidențiat) — venitul, comisionul, manopera operatorului logat
- Status comision firmă, segmente pacienți
- **Fără** secțiunea Total și **fără** graficul anual (admin-only)

### Setări configurabile (`/app/optimed-crm-settings`)
- **Pragul comisionului lunar** (default 75.000 RON) + procentaj avertisment/deblocare
- **Praguri pe an** (child table) — override pragul global pentru ani anteriori
- **Logo firmă** (upload imagine, apare sus-stânga pe Dashboard)
- **Branding** — nume firmă, text greeting

## DocType-uri custom

| DocType | Rol |
|---|---|
| Patient | Pacient (~9.800) cu segmentare automată VIP/Fidel/Inactiv/etc. |
| Appointment | Programare (~13.300) — sincronizată cu Calendly în viitor |
| Deal | Vânzare (~9.567) cu calcul automat venit/manoperă/comision |
| Sales Operator | Operator vânzare/montare cu procent comision |
| Contact Log | Istoric contactări pacienți (zilnic) |
| Optimed CRM Settings | Setări singleton + tabel praguri pe an |
| Optimed CRM Yearly Threshold | Child — prag comision per an |

## Pagini custom

- `/app/optimed-dashboard` — Dashboard hibrid (descris mai sus)
- `/app/contacts-today` — Listă zilnică pacienți de contactat (4 categorii)
- `/app/optimed-crm-settings` — Setări configurabile

## Rapoarte (Script Reports)

- VIP Patients (287)
- Loyal Patients (422)
- Inactive Patients (4.460)
- Unconverted Patients (4.054)
- New Buyers (385)
- Operator Performance (cu filtre dată)
- Contact History (istoric contactări)

## Structura proiectului

```
crm-optimed/
├── frappe-crm/              # Instalare Frappe CRM (Docker)
│   ├── docker-compose.yml
│   ├── init.sh              # Bootstrap automat (instalează optimed_crm la prima pornire)
│   └── optimed_crm/         # App-ul custom
│       ├── optimed_crm/
│       │   ├── api/         # Endpoint-uri REST (dashboard_stats, contacts_today)
│       │   ├── optimed_crm/ # Modul Frappe (doctype/, page/, report/, workspace/)
│       │   ├── patches/     # Migrări versiuni (v1_0, v1_1)
│       │   ├── public/js/   # JS injectat global (Chart.js + redirects)
│       │   └── hooks.py
│       └── scripts/         # Scripturi de instalare/utilitare (~20 fișiere)
├── n8n/                     # Automatizări (Calendly + WhatsApp — viitor)
├── data/                    # Fișiere CSV pentru import
├── docs/                    # Documentație utilizatori
├── .gitignore
└── README.md
```

## Utilizatori

| Utilizator | Rol | Email |
|---|---|---|
| Administrator | System Manager | (login implicit) |
| Ramona | Optimed Operator | ramona@optimedtoplita.ro |
| Roxana | Optimed Operator | roxana@optimedtoplita.ro |
| Eniko | Optimed Operator | eniko@optimedtoplita.ro |

Operatorii văd **doar** workspace-ul Optimed CRM — toate workspace-urile sistem (Users, Website, Tools etc.) sunt restricționate la System Manager.

## Servicii

| Serviciu | URL | Port |
|---|---|---|
| Optimed Dashboard | http://localhost:8000/app/optimed-dashboard | 8000 |
| Frappe CRM (standard) | http://localhost:8000/crm | 8000 |
| n8n (viitor) | http://localhost:5678 | 5678 |

## Comenzi rapide

```bash
# Pornire
cd frappe-crm && docker compose up -d

# Oprire
cd frappe-crm && docker compose down

# Logs live
cd frappe-crm && docker compose logs -f

# Status containere
cd frappe-crm && docker compose ps

# Migrate (după modificări JSON DocType)
docker exec crm-frappe-1 bash -c "cd frappe-bench && bench --site crm.localhost migrate"

# Build assets (după modificări JS/CSS)
docker exec crm-frappe-1 bash -c "cd frappe-bench && bench build --app optimed_crm"
```

## Integrări planificate

- **Calendly** → programări automate (prin n8n)
- **WhatsApp Business API** → mesaje automate pacienți (prin n8n)
- **HubSpot** → sync contacte (deja importate one-shot din Excel)

## Credențiale default Frappe CRM

- URL: http://localhost:8000
- User: `Administrator`
- Parolă: `admin` *(schimbă imediat după primul login!)*
