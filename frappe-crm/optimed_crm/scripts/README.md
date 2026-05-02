# Etapa 6.1 — Workspace + Number Cards + Charts

Construiește Dashboard-ul nativ Frappe cu 12 statistici live, 3 grafice și layout structurat.

## Conținut

```
scripts/
├── create_number_cards.py    # 1. Creează cele 12 Number Cards
├── create_charts.py          # 2. Creează cele 3 grafice
└── create_workspace.py       # 3. Creează Workspace-ul cu layout
```

## Ordine de rulare (CRITICĂ)

Strict secvențial — fiecare script depinde de cele anterioare:

```python
# Pasul 1: Number Cards (cifrele mari)
exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/create_number_cards.py').read())
run()

# Pasul 2: Charts (graficele)
exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/create_charts.py').read())
run()

# Pasul 3: Workspace (layout-ul care le conține)
exec(open('/home/frappe/frappe-bench/apps/optimed_crm/scripts/create_workspace.py').read())
run()

# După rulare:
# bench --site [site] clear-cache
```

## Ce vei vedea în interfață

### În meniul stânga
Apare un nou item: **Optimed CRM** cu icoană dashboard.

### Pe pagina Dashboard
- **3 secțiuni** cu Number Cards: Volume, Financiar, Operațional
- **12 cifre live** care se actualizează automat
- **3 grafice**: Deal-uri/lună (linie), Venit/operator (bare), Segmente (donut)
- **Shortcut-uri colorate** sus pentru navigare rapidă
- **Link-uri** stânga către DocType-uri

### Cifrele așteptate
- Total pacienți: ~9.791
- Venit total: ~5.206.726 RON
- Pacienți VIP: ~366
- Pacienți inactivi: ~2.814
- Rată conversie: ~44%

## Idempotență

Toate scripturile sunt idempotente — le poți rula de mai multe ori.
- Number Cards existente sunt **actualizate**
- Workspace existent este **șters și recreat** (cel mai sigur pentru schimbări de layout)

## Probleme posibile

### "Number Card 'X' lipsă — rulează create_number_cards.py întâi"
Ai sărit peste pasul 1. Rulează scripturile în ordine.

### Workspace nu apare în meniu
- Rulează `bench --site [site] clear-cache`
- Reîncarcă browser-ul (Ctrl+Shift+R pentru hard refresh)
- Verifică că ai role-ul `System Manager` (workspace e public deci ar trebui să apară)

### Charts nu se încarcă (rotiță infinită)
Datele sunt prea mari pentru calcul on-the-fly. Pentru 9.567 deal-uri ar trebui să meargă, dar dacă persistă:
- Verifică `Error Log` în Frappe
- Probabil trebuie reconstruit cache-ul: `bench --site [site] build`

## Limitarea curentă

**"Pacienți de contactat azi"** este pentru moment un placeholder simplu.
Calculul exact (2 zile / 15 zile / 6 luni / 1 an post-ridicare) îl construim în Etapa 6.3 cu un Custom Report dedicat.
