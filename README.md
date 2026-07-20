# SARAwater – App Streamlit

App web interattiva per l'analisi di scenari di astrazione idrica su tratti fluviali, basata sulla libreria [SARAwater](https://github.com/sara-acqua/sarawater).

## Installazione

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Avvio

```bash
bash start.sh
```

Oppure direttamente:

```bash
venv/bin/python3 -m streamlit run app.py
```

L'app sarà disponibile su http://localhost:8501

> **Nota**: su volumi SMB (NAS/server) usare sempre `python3 -m streamlit` anziché l'eseguibile `streamlit` direttamente, per evitare errori di permessi.

## Funzionalità

- **Sidebar**: configura il tratto fluviale (portata media, ampiezza stagionale, anni di simulazione) e aggiungi scenari di tipo costante o proporzionale
- **Tab Portate**: grafico delle portate naturali vs. rilasciate per ogni scenario
- **Tab Scenari**: riepilogo parametri e volumi mensili astratti
- **Tab Indici IHA**: indici IARI aggregati e per gruppo
- **Tab Export**: download del riepilogo in formato CSV
