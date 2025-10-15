# WNGW-Test-Tool

Das WNGW-Test-Tool ist ein Monorepo zur Prüfung physischer Gateways über IEC 60870-5-104. Das Projekt liefert ein FastAPI-Backend und eine React/Vite-Frontend-Anwendung sowie grundlegende Tests und Entwickler-Tooling.

## Voraussetzungen
- Python 3.11
- Node.js 18+
- `pip`, `npm`

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
pip install -e backend/local_iec104_lib
cd frontend
npm install
```

## Entwicklung starten
### Manuell
In zwei Terminals:
```bash
# Terminal 1 – Backend
cd backend
uvicorn wngw_app.main:app --reload --port 8000

# Terminal 2 – Frontend
cd frontend
npm run dev
```
Backend läuft auf http://localhost:8000, Frontend auf http://localhost:5173.

### VS Code Launch-Konfiguration
Verwende die Compound-Konfiguration **All – Backend + Frontend** aus `.vscode/launch.json`, um beide Prozesse parallel zu starten.

## Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## IEC-104 Adapter
Die im Projekt verwendete IEC-104-Integration orientiert sich ausschließlich an der Datei `backend/local_iec104_lib/API_OVERVIEW.md`. Nicht dokumentierte Features – insbesondere General Interrogation (`C_IC_NA_1`) – sind absichtlich nicht implementiert und werden in der Codebasis mit `NotImplementedError` markiert.

## Grenzen & TODOs
- Sequenznummern (`vs`/`vr`) werden aktuell mit Platzhaltern gestreamt. Ein zukünftiges Update soll `decode_apdu` nutzen, sobald verfügbar.
- Die General Interrogation ist nicht verfügbar.
- Der IEC-104-Adapter dient als Ausgangspunkt und kann bei Verfügbarkeit echter Gateways erweitert werden.

