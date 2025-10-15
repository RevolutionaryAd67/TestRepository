# WNGW-Test-Tool

Das WNGW-Test-Tool ist ein Monorepo zur Prüfung physischer Gateways über IEC 60870-5-104. Das Projekt liefert ein FastAPI-Backend und eine React/Vite-Frontend-Anwendung sowie grundlegende Tests und Entwickler-Tooling.

## Voraussetzungen
- Python 3.11
- Node.js 18+
- `pip`, `npm`

## Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
pip install -e backend/local_iec104_lib
Set-Location frontend
npm install
Set-Location ..
```

## Entwicklung starten

### Schritt-für-Schritt-Anleitung
1. **Virtuelle Python-Umgebung aktivieren** (falls noch nicht geschehen):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
2. **Backend-Entwicklungsserver starten**:
   ```powershell
   Set-Location backend
   uvicorn wngw_app.main:app --reload --port 8000
   ```
   Der FastAPI-Server läuft danach unter http://localhost:8000.
3. **Neues PowerShell-Fenster für das Frontend öffnen** und ins Repository wechseln:
   ```powershell
   Set-Location C:\Pfad\zum\Projekt\wngw-test-tool
   ```
4. **Frontend-Entwicklungsserver starten**:
   ```powershell
   Set-Location frontend
   npm run dev
   ```
   Die React/Vite-Anwendung ist anschließend unter http://localhost:5173 erreichbar.

### Manuell (Kurzfassung)
In zwei Terminals:
```powershell
# PowerShell 1 – Backend
Set-Location backend
uvicorn wngw_app.main:app --reload --port 8000

# PowerShell 2 – Frontend
Set-Location frontend
npm run dev
```

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

