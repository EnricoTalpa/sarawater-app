#!/bin/bash
# Avvia l'app SARAwater dalla directory del progetto.
# Progetto:  /Volumes/PyLab/projects/SaraWater Astrazione idrica/
# Venv:      ~/PyLab-venvs/sarawater/  (locale, non su NFS)

PROJECT_DIR="/Volumes/PyLab/projects/SaraWater Astrazione idrica"
VENV_DIR="$HOME/PyLab-venvs/sarawater"
PYTHON="$VENV_DIR/bin/python3"

# Verifica mount NFS
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ /Volumes/PyLab non montato. Attendi il mount automatico o esegui:"
    echo "   sudo launchctl start com.enrico.nfs-pylab"
    exit 1
fi

# Verifica venv
if [ ! -x "$PYTHON" ]; then
    echo "❌ Venv non trovato: $VENV_DIR"
    echo "   Ricrea con: python3.14 -m venv ~/PyLab-venvs/sarawater"
    exit 1
fi

cd "$PROJECT_DIR"
"$PYTHON" -m streamlit run app.py
