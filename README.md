# SARAwater – App Streamlit

App web interattiva per l'analisi di scenari di astrazione idrica su tratti fluviali, basata sulla libreria [SARAwater](https://github.com/sara-acqua/sarawater).

## Requisiti

- Python ≥ 3.11 (in uso: 3.14.6 da Homebrew, `/opt/homebrew/opt/python@3.14`)
- macOS su Apple Silicon; compatibile con qualsiasi OS con Python e accesso di rete
- Connessione internet per l'installazione (sarawater si installa da GitHub)
- `git` installato (richiesto da pip per installare sarawater dal fork)
- Mount NFS `/Volumes/PyLab` attivo (gestito dal LaunchDaemon `com.enrico.nfs-pylab`)

## Struttura del progetto

Il codice risiede su NFS, il virtual environment è **sempre locale** (convenzione PyLab):

```
/Volumes/PyLab/projects/SaraWater Astrazione idrica/
├── app.py                # App Streamlit principale
├── requirements.txt      # Dipendenze pip
├── start.sh              # Script di avvio (verifica mount NFS + venv)
├── README.md             # Questa documentazione
├── SESSION_SUMMARY.md    # Riepilogo tecnico della sessione di installazione
└── .gitignore

~/PyLab-venvs/sarawater/  # Virtual environment (locale, fuori da NFS)
```

## Installazione

```bash
# 1. Installa Python 3.14 (se non presente)
brew install python@3.14

# 2. Crea il virtual environment LOCALE (mai su NFS)
/opt/homebrew/opt/python@3.14/bin/python3.14 -m venv ~/PyLab-venvs/sarawater

# 3. Installa le dipendenze
~/PyLab-venvs/sarawater/bin/python3 -m pip install --upgrade pip
~/PyLab-venvs/sarawater/bin/python3 -m pip install \
  -r "/Volumes/PyLab/projects/SaraWater Astrazione idrica/requirements.txt"
```

> **Nota sui volumi di rete:** i mount NFS/SMB non preservano in modo affidabile i bit di
> esecuzione degli script. Il venv è per questo tenuto in locale in `~/PyLab-venvs/`; usare
> comunque `python3 -m <modulo>` al posto degli eseguibili diretti (`pip`, `streamlit`).

## Avvio

### Metodo 1 — script (raccomandato)

```bash
bash "/Volumes/PyLab/projects/SaraWater Astrazione idrica/start.sh"
```

Lo script verifica che il mount NFS e il venv siano presenti, poi lancia l'app con il Python
del venv tramite `python3 -m streamlit`.

### Metodo 2 — comando diretto

```bash
cd "/Volumes/PyLab/projects/SaraWater Astrazione idrica"
~/PyLab-venvs/sarawater/bin/python3 -m streamlit run app.py
```

### Metodo 3 — con porta personalizzata

```bash
~/PyLab-venvs/sarawater/bin/python3 -m streamlit run app.py --server.port 8502
```

## Configurazione del deployment attuale

| Parametro | Valore |
|-----------|--------|
| Host macchina | MacBook Pro — IP `192.168.88.230` |
| Percorso progetto | `/Volumes/PyLab/projects/SaraWater Astrazione idrica/` |
| Mount progetti | NFS `/Volumes/PyLab` (LaunchDaemon `com.enrico.nfs-pylab`) |
| Percorso venv | `~/PyLab-venvs/sarawater/` (locale) |
| URL locale | http://localhost:8501 |
| URL rete LAN | http://192.168.88.230:8501 |
| Python | 3.14.6 (Homebrew, `/opt/homebrew/opt/python@3.14`) |
| Porta Streamlit | 8501 (default) |

L'app è accessibile da qualsiasi device sulla rete locale (telefono, tablet, altri computer) puntando a **http://192.168.88.230:8501**.

> **Nota:** l'IP LAN è assegnato via DHCP e può cambiare. Verificarlo con `ipconfig getifaddr en0`
> oppure leggendo la *Network URL* stampata da Streamlit all'avvio.

## Dipendenze (`requirements.txt`)

| Pacchetto | Versione | Note |
|-----------|----------|------|
| `sarawater` | 2.0.0 + patch | Fork `EnricoTalpa/sarawater`, branch `fix/pandas3-groupby-observed` |
| `streamlit` | ultima stabile | Framework web UI |
| `matplotlib` | ultima stabile | Grafici |
| `pandas` | 3.0.5 | Elaborazione dati |
| `watchdog` | 6.0.0 | Hot-reload nativo macOS via FSEvents |

> **Nota su sarawater:** la versione su PyPI (2.0.0) contiene un bug con pandas ≥ 2.0.
> Il `requirements.txt` punta al fork fixato. Quando la PR [#18](https://github.com/sara-acqua/sarawater/pull/18)
> verrà mergiata, aggiornare con:
> ```bash
> # In requirements.txt, sostituire la riga sarawater con:
> sarawater>=2.0.1
> # Poi reinstallare:
> ~/PyLab-venvs/sarawater/bin/python3 -m pip install --upgrade sarawater
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
~/PyLab-venvs/sarawater/bin/python3 -m pip install --upgrade \
  -r "/Volumes/PyLab/projects/SaraWater Astrazione idrica/requirements.txt"

# Aggiornare solo streamlit
~/PyLab-venvs/sarawater/bin/python3 -m pip install --upgrade streamlit

# Ricreare il venv da zero
rm -rf ~/PyLab-venvs/sarawater
/opt/homebrew/opt/python@3.14/bin/python3.14 -m venv ~/PyLab-venvs/sarawater

# Verificare che l'app risponda
curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/healthz
# Atteso: 200
```

## Repository

- **App (questo repo):** https://github.com/EnricoTalpa/sarawater-app
- **Libreria sarawater (upstream):** https://github.com/sara-acqua/sarawater
- **Fork con bugfix pandas 3.0:** https://github.com/EnricoTalpa/sarawater/tree/fix/pandas3-groupby-observed
- **PR bugfix:** https://github.com/sara-acqua/sarawater/pull/18
