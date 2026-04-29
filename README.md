# CRM Optimed — Frappe CRM

Sistem CRM pentru **Optimed Toplița** — cabinet oftalmologic și magazin de optică.

## Structura proiectului

```
crm-optimed/
├── frappe-crm/     # Instalare Frappe CRM (Docker)
├── n8n/            # Automatizări (Calendly + WhatsApp Business API)
├── data/           # Fișiere CSV pentru import pacienți (~9.791 înregistrări)
├── docs/           # Documentație internă și ghiduri utilizatori
├── .gitignore
└── README.md
```

## Utilizatori

| Utilizator | Rol |
|------------|-----|
| Administrator | Admin (proprietar) |
| Ramona | Operator |
| Roxana | Operator |
| Eniko | Operator |

## Servicii

| Serviciu | URL | Port |
|----------|-----|------|
| Frappe CRM | http://crm.localhost:8000/crm | 8000 |
| n8n (viitor) | http://localhost:5678 | 5678 |

## Comenzi rapide Frappe CRM

```bash
# Pornire
cd frappe-crm && docker compose up -d

# Oprire
cd frappe-crm && docker compose down

# Logs live
cd frappe-crm && docker compose logs -f

# Status containere
cd frappe-crm && docker compose ps
```

## Integrări planificate

- **Calendly** → programări automate (prin n8n)
- **WhatsApp Business API** → mesaje automate pacienți (prin n8n)
- **Import pacienți** → ~9.791 pacienți din Excel via CSV

## Credențiale default Frappe CRM

- URL: http://crm.localhost:8000/crm
- User: `Administrator`
- Parolă: `admin` *(schimbă imediat după primul login!)*
