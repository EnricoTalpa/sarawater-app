#!/bin/bash
# Avvia l'app SARAwater dalla directory del progetto.
# Usa 'python3 -m streamlit' per evitare problemi di permessi sullo share SMB.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$SCRIPT_DIR/venv/bin/python3"

cd "$SCRIPT_DIR"
"$PYTHON" -m streamlit run app.py
