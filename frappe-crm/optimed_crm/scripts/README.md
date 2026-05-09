# Etapa 8.2 — Frontend Dashboard hibrid

UI-ul nou pentru Dashboard care apelează API-ul din 8.1 și afișează vizualizare per rol.

## Conținut

```
optimed_crm/optimed_crm/
├── page/optimed_dashboard/         # Pagina nouă cu UI custom
│   ├── __init__.py
│   ├── optimed_dashboard.json      # Definiție pagină
│   ├── optimed_dashboard.py        # Backend (gol)
│   ├── optimed_dashboard.css       # Stiluri custom
│   └── optimed_dashboard.js        # JS — apelează API + render
├── patches.txt                     # Listă patch-uri (UPDATE — adaugă v1_1)
└── patches/v1_1/
    └── add_logo_to_settings.py     # Patch pentru câmp logo

scripts/
├── README.md
├── install_dashboard.py            # Script principal — workspace + landing
└── patch_dashboard_stats_for_logo.py  # Patch automat pentru API
```

## Ce face Dashboard-ul nou

### Pentru tine (admin)
- 4 shortcut-uri sus (De contactat, Programări, Deals, Cumpărători noi)
- **Performanța firmei** — Venit, Comision, Manoperă, Top operator
- **Status comision firmă** (banner colorat 91% / 75.000 RON)
- **Pacienți** + **Conversie** (mare, centrată)
- **Total** — secțiune cu 6 metrici globale

### Pentru operator (Ramona/Roxana/Eniko)
- 4 shortcut-uri sus (la fel)
- **Performanța TA** (mov, evidențiat) — Venitul TĂU, Comisionul TĂU, Manopera TA
- **Performanța firmei** (gri, neutru) — Venit, Comision, Manoperă (FĂRĂ Top operator)
- **Status comision firmă** (la fel)
- **Pacienți** + **Conversie**
- ❌ Secțiunea Total nu e vizibilă

## Funcționalități

✅ **Auto-refresh la 5 minute** — datele se actualizează singure
✅ **Buton Refresh manual** — sus dreapta, lângă dată
✅ **Logo customizabil** — upload prin Optimed CRM Settings
✅ **Greeting personalizat** — "Bună dimineața, Ramona"
✅ **Format românesc pentru numere** — 5.206.726 RON (separator românesc)
✅ **Mobile responsive** — funcționează și pe mobil
✅ **Click pe shortcut-uri** → te duce la pagina/lista relevantă

## Instalare

```bash
# 1. Plasare fișiere
# Copiază optimed_crm/* peste apps/optimed_crm/optimed_crm/
# Copiază scripts/*.py în apps/optimed_crm/scripts/

# IMPORTANT — patches.txt va fi suprascris (e versiune nouă cu v1_1)

# 2. Patch automat dashboard_stats.py (adaugă logo_url în răspuns)
docker exec -it [container] python3 /home/frappe/frappe-bench/apps/optimed_crm/scripts/patch_dashboard_stats_for_logo.py

# 3. Migrare (creează pagina + aplică patch logo)
docker exec -it [container] bench --site [site] migrate

# 4. Instalare dashboard (workspace replacement + landing setup)
docker exec -it [container] bench --site [site] console
exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/install_dashboard.py').read())
run()
exit()

# 5. Clear cache + restart
docker exec -it [container] bench --site [site] clear-cache
docker exec -it [container] bench restart
```

## Logo upload

După instalare:
1. Accesează: `http://localhost:8000/app/optimed-crm-settings`
2. Câmpul "Logo Optimed" — click pentru upload
3. Selectează PNG sau JPG (recomandat: PNG transparent ~200x200px)
4. Salvează
5. Reîncarcă Dashboard-ul → logo-ul apare sus stânga

## Test funcțional

### Ca admin:
1. Login → ar trebui să fii pe /app/optimed-crm
2. Click pe butonul "Deschide Dashboard Optimed →"
3. Vezi toate secțiunile inclusiv Total
4. Click pe shortcut "De contactat" → te duce la /app/contacts-today
5. Click Refresh → datele se actualizează

### Ca Ramona:
1. Login → te duce automat la workspace Optimed CRM
2. Click pe Dashboard
3. Vezi "Performanța TA" cu cifrele Ramonei
4. NU vezi Top operator
5. NU vezi secțiunea Total

## Limitarea curentă

Auto-redirect ÎN TIMPUL LOGIN-ULUI nu se face direct la /app/optimed-dashboard
(workspace-ul Optimed CRM e landing-ul, dar utilizatorul vede butonul redirect).

Pentru auto-redirect 100% (fără click), e o modificare suplimentară în hooks.py.
Pentru moment merge varianta cu buton — e mai sigur și clar pentru utilizator.
