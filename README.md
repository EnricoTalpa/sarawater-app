# SARAwater – App Streamlit

App web interattiva per l'analisi di scenari di astrazione idrica su tratti fluviali, basata sulla libreria [SARAwater](https://github.com/sara-acqua/sarawater).

## Requisiti

- Python ≥ 3.11
- macOS (testato su 3.14.3); compatibile con qualsiasi OS con Python e accesso di rete
- Connessione internet per l'installazione (sarawater si installa da GitHub)
- `git` installato (richiesto da pip per installare sarawater dal fork)

## Struttura del progetto

```
SaraWater Astrazione idrica/
├── app.py                # App Streamlit principale
├── requirements.txt      # Dipendenze pip
├── start.sh              # Script di avvio (workaround permessi SMB)
├── README.md             # Questa documentazione
├── SESSION_SUMMARY.md    # Riepilogo tecnico della sessione di installazione
├── .gitignore
└── venv/                 # Virtual environment (non versionato)
```

## Installazione

```bash
# 1. Clona il repository
git clone https://github.com/EnricoTalpa/sarawater-app.git
cd sarawater-app

# 2. Crea il virtual environment
python3 -m venv venv

# 3. Installa le dipendenze
#    Su macOS standard:
venv/bin/pip install -r requirements.txt

#    Su volumi SMB (NAS/server) — usare python3 -m pip:
venv/bin/python3 -m pip install -r requirements.txt
```

> **Nota su SMB:** i volumi SMB non preservano i bit di esecuzione degli script.
> Usare sempre `venv/bin/python3 -m <modulo>` al posto degli eseguibili diretti (`pip`, `streamlit`).

## Avvio

### Metodo 1 — script (raccomandato)

```bash
bash start.sh
```

Lo script rileva automaticamente la propria directory e usa il Python del venv con `python3 -m streamlit`, compatibile sia con path locali sia con mount SMB.

### Metodo 2 — comando diretto

```bash
venv/bin/python3 -m streamlit run app.py
```

### Metodo 3 — con porta personalizzata

```bash
venv/bin/python3 -m streamlit run app.py --server.port 8502
```

## Configurazione del deployment attuale

| Parametro | Valore |
|-----------|--------|
| Host macchina | MacBook Pro — IP `192.168.88.33` |
| Percorso progetto | `/Volumes/Storage/Script Project/SaraWater Astrazione idrica/` |
| Mount NAS | `smb://192.168.88.201/Storage` |
| URL locale | http://localhost:8501 |
| URL rete LAN | http://192.168.88.33:8501 |
| Python | 3.14.3 |
| Porta Streamlit | 8501 (default) |
| Processo verificato | PID 15158 — HTTP 200 su `/` e `/healthz` |

L'app è accessibile da qualsiasi device sulla rete locale (telefono, tablet, altri computer) puntando a **http://192.168.88.33:8501**.

## Dipendenze (`requirements.txt`)

| Pacchetto | Versione | Note |
|-----------|----------|------|
| `sarawater` | 2.0.0 + patch | Fork `EnricoTalpa/sarawater`, branch `fix/pandas3-groupby-observed` |
| `streamlit` | ultima stabile | Framework web UI |
| `matplotlib` | ultima stabile | Grafici |
| `pandas` | 3.0.3 | Elaborazione dati |
| `watchdog` | 6.0.0 | Hot-reload nativo macOS via FSEvents |

> **Nota su sarawater:** la versione su PyPI (2.0.0) contiene un bug con pandas ≥ 2.0.
> Il `requirements.txt` punta al fork fixato. Quando la PR [#18](https://github.com/sara-acqua/sarawater/pull/18)
> verrà mergiata, aggiornare con:
> ```bash
> # In requirements.txt, sostituire la riga sarawater con:
> sarawater>=2.0.1
> # Poi reinstallare:
> venv/bin/python3 -m pip install --upgrade sarawater
> ```

## Funzionalità

- **Sidebar** — configura il tratto fluviale (nome, portata media, ampiezza stagionale, anni, Qabs_max) e aggiungi scenari tramite form interattivo
- **Tab Portate** — grafico matplotlib Qnat vs. Qrel per ogni scenario + tabella statistiche (media, min, max)
- **Tab Scenari** — riepilogo `export_scenarios_summary()` + bar chart volumi mensili astratti
- **Tab Indici IHA** — tabella e bar chart IARI aggregato e per gruppo (soglia 0.5 evidenziata)
- **Tab Export** — download del riepilogo completo in formato CSV

### Tipi di scenario

**Costante (`ConstScenario`):** portate mensili richieste fisse (12 valori in m³/s).

**Proporzionale (`PropScenario`):** astrazione proporzionale alla portata in ingresso, con parametri:
- `Qbase` — portata base garantita (m³/s)
- `c_Qin` — coefficiente proporzionale (0–1)
- `Qreq_min` / `Qreq_max` — limiti di portata richiesta (m³/s)

## Aggiornamento e manutenzione

```bash
# Aggiornare tutte le dipendenze
venv/bin/python3 -m pip install --upgrade -r requirements.txt

# Aggiornare solo streamlit
venv/bin/python3 -m pip install --upgrade streamlit

# Verificare che l'app risponda
curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/healthz
# Atteso: 200
```

## Repository

- **App (questo repo):** https://github.com/EnricoTalpa/sarawater-app
- **Libreria sarawater (upstream):** https://github.com/sara-acqua/sarawater
- **Fork con bugfix pandas 3.0:** https://github.com/EnricoTalpa/sarawater/tree/fix/pandas3-groupby-observed
- **PR bugfix:** https://github.com/sara-acqua/sarawater/pull/18
