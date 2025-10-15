# IEC 60870-5-104 Webtester

Eine browserbasierte, Windows-freundliche Prüfoberfläche für physische IEC 60870-5-104 Gateways. Die Anwendung setzt vollständig auf WebSockets und verwendet Ihre lokal installierte Python-Bibliothek `iec104`.

## Inhalt
- [Funktionsumfang](#funktionsumfang)
- [Systemvoraussetzungen](#systemvoraussetzungen)
- [Download & Projektstruktur](#download--projektstruktur)
- [Virtuelle Umgebung unter Windows](#virtuelle-umgebung-unter-windows)
- [Visual-Studio-Code-Konfiguration](#visual-studio-code-konfiguration)
- [Installation der Abhängigkeiten](#installation-der-abhängigkeiten)
- [Start der Anwendung mit Hypercorn](#start-der-anwendung-mit-hypercorn)
- [Benutzung der Weboberfläche](#benutzung-der-weboberfläche)
- [Signallisten importieren und exportieren](#signallisten-importieren-und-exportieren)
- [Docker (optional)](#docker-optional)
- [Firewall- und Netzwerkeinstellungen](#firewall--und-netzwerkeinstellungen)
- [Troubleshooting](#troubleshooting)
- [Tests & Code-Qualität](#tests--code-qualität)
- [Lizenz](#lizenz)

## Funktionsumfang
- IEC-104 Client- und Server-Modus in einer Anwendung.
- Live-Stream aller IEC-104 Frames über einen dedizierten WebSocket (`/stream`).
- Start-/Prüfungs-/Signallisten-/Admin-Ansichten mit separater Navigation.
- Konfigurierbarer Ringpuffer (Drop-Oldest), um bis zu 10.000 IEC-Frames vorzuhalten.
- CSV/JSON-basierter Import und Export von Signallisten (persistiert in SQLite via SQLAlchemy).
- Szenario-Verwaltung für vorgefertigte Testsequenzen.
- Vollständig lokale Assets (TailwindCSS, JavaScript) ohne CDN.
- Logging via `logging`-Modul mit strukturierbaren `extra`-Feldern.

## Systemvoraussetzungen
- Windows 10 oder Windows 11 (64 Bit).
- [Python 3.11](https://www.python.org/downloads/windows/) (Installationsoption "Add python.exe to PATH" aktivieren).
- [Visual Studio Code](https://code.visualstudio.com/) mit Erweiterungen *Python* und *Pylance*.
- Git (optional, für `git clone`).
- Lokale IEC-104-Bibliothek im Nachbarverzeichnis: `pip install -e ../iec104`.
- Optional: [Docker Desktop](https://www.docker.com/products/docker-desktop/) für Containerbetrieb.

## Download & Projektstruktur
1. Projekt per `git clone` beziehen:
   ```powershell
   git clone https://example.com/iec104-webtester.git
   cd iec104-webtester
   ```
   Alternativ: ZIP herunterladen und entpacken.
2. Wichtige Dateien:
   - `app/` – Quart-Anwendung, Services, Templates, Static Assets.
   - `tests/` – Pytest-Suite inkl. IEC-Loopback-Test.
   - `pyproject.toml` – Projekt- und Tooling-Konfiguration.
   - `.env.example` – Beispielkonfiguration (kopieren zu `.env`).

## Virtuelle Umgebung unter Windows
### PowerShell
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```
Sollte PowerShell das Skript blockieren, Ausführungsrichtlinie temporär anpassen:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Eingabeaufforderung (CMD)
```cmd
py -3.11 -m venv .venv
.\.venv\Scripts\activate.bat
```

## Visual-Studio-Code-Konfiguration
1. Projektordner in VS Code öffnen (`Datei > Ordner öffnen`).
2. Command Palette (`Strg+Shift+P`) öffnen und **Python: Interpreter auswählen** wählen.
3. Interpreter aus `.venv` auswählen (`.venv\Scripts\python.exe`).
4. Bei Interpreterwechsel VS Code ggf. neu starten.

## Installation der Abhängigkeiten
1. Abhängigkeiten des Webtesters:
   ```powershell
   pip install -e .
   ```
2. Lokale IEC-104-Bibliothek (aus Nachbarverzeichnis):
   ```powershell
   pip install -e ..\iec104
   ```
   > **Wichtig:** Falls die Bibliothek fehlt, beendet sich die Anwendung mit einer klaren Fehlermeldung („`pip install -e ../iec104`“).
3. Optionale Dev-Tools (Black, Ruff, Mypy, Pytest):
   ```powershell
   pip install -e .[dev]
   ```

## Start der Anwendung mit Hypercorn
1. `.env` erzeugen (optional):
   ```powershell
   Copy-Item .env.example .env
   ```
2. Anwendung starten:
   ```powershell
   python -m hypercorn app.main:app --bind 127.0.0.1:8080 --workers 1 --access-log -
   ```
3. Beim ersten Start Windows-Firewall-Eingabe bestätigen (Hypercorn/IEC-Port erlauben).
4. Browser öffnen: [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
5. IEC-104 Standardports: 2404 (Client & Server). Anpassbar über UI und `.env`.

## Benutzung der Weboberfläche
- **Start**: Überblick, Schnellstart-Hinweise.
- **Prüfung**: Tabs für Verbindungssteuerung, Senden von ASDUs, Sequenzen, Monitor.
  - Linke Sidebar bietet Kontextnavigation.
  - Rechte Sidebar zeigt Live-Frames mit Filtern (Rolle, Richtung, TI, COT, IOA, Volltext).
  - Filter wirken ohne Reload (max. 30 fps dank `requestAnimationFrame`).
- **Signallisten**: Import/Export von CSV/JSON.
- **Administration**: Anzeige der aktuellen Konfiguration, Hinweis auf reinen WebSocket-Betrieb.

### IEC-104 Client bedienen
1. Unter *Prüfung > Verbindungen* Zielhost/Port und Protokollparameter (k, w, T0…T3) eintragen.
2. **Verbinden** klicken. Die Statusanzeige in der Kopfzeile leuchtet grün.
3. Einzel-ASDUs über *Prüfung > Sende-Vorlagen* auswählen (z. B. TI=1) und auf **Senden** klicken.
4. Gesendete/empfangene Frames erscheinen rechts mit APCI/ASDU-Hex und JSON-Dekodierung.

### IEC-104 Server bedienen
1. Unter *Prüfung > Verbindungen* Bind-Adresse/Port setzen.
2. **Starten** klicken – der Server lauscht auf eingehende Verbindungen und führt STARTDT automatisch aus.
3. Eingehende Kommandos (z. B. `C_SC_NA_1`) können per Handler beantwortet werden (Erweiterungspunkt in `app/services/iec_server.py`).

## Signallisten importieren und exportieren
1. Unter *Signallisten > Import* CSV oder JSON hochladen.
2. Erwartete Spalten:
   ```
name,ti,ioa,scale,unit,default,description
Spannung,13,1001,1.0,V,0,Messwert Spannung L1
   ```
3. Bei Fehlern wird ein detaillierter Bericht angezeigt. Erfolgreiche Einträge landen in SQLite (`sqlite+aiosqlite`).
4. Export erfolgt zukünftig als CSV/JSON über denselben Bereich (Erweiterungspunkt).

## Docker (optional)
1. Image bauen:
   ```powershell
   docker build -t iec104-webtester .
   ```
2. Starten:
   ```powershell
   docker run --rm -p 8080:8080 -p 2404:2404 iec104-webtester
   ```
3. Für Zugriff auf physische Gateways Portweiterleitungen prüfen.

## Firewall- und Netzwerkeinstellungen
- Beim ersten Start fragt Windows-Firewall nach Erlaubnis für Python/Hypercorn. Für lokale Tests "Privates Netzwerk" erlauben.
- IEC-104 nutzt TCP 2404. Stellen Sie sicher, dass Gateway/IP erreichbar ist.
- Bei Einsatz in abgeschotteten Netzen gegebenenfalls Ausnahmen für eingehende Verbindungen konfigurieren.

## Troubleshooting
| Problem | Ursache | Lösung |
| --- | --- | --- |
| `iec104` nicht gefunden | Virtuelle Umgebung kennt Paket nicht | `pip install -e ..\iec104`, VS-Code-Interpreter kontrollieren |
| Port 8080 bereits belegt | Anderer Dienst nutzt Port | `.env` bearbeiten (`APP_PORT`), Hypercorn mit anderem Port starten |
| WebSocket verbindet nicht | Firewall blockiert, falsche URL | Firewall-Regeln prüfen, Browser auf `http://127.0.0.1:8080` richten |
| `sqlite3.OperationalError` | Pfad nicht beschreibbar | Projektordner ohne Admin-Rechte in Benutzerverzeichnis verschieben |
| Pytest findet kein Event-Loop | Falsche Python-Version/Interpreter | Sicherstellen, dass Python 3.11 aus `.venv` genutzt wird |

## Tests & Code-Qualität
- Testlauf: `pytest`
- Linting: `ruff check .`
- Formatierung: `black .`
- Typprüfung: `mypy .`
- Alle Tools funktionieren ohne zusätzliche Linux-Abhängigkeiten auf Windows.

## Lizenz
MIT-Lizenz – siehe `pyproject.toml`.
