# IEC 60870-5-104 Testbench

Eine modulare Flask-Anwendung für funktionale Tests von IEC 60870-5-104 Gateways. Die Anwendung bietet sowohl Client- als auch Server-Funktionalität, verwaltet Signallisten und stellt einen Live-WebSocket-Strom aller Frames bereit.

## Projektparameter

| Parameter | Wert |
| --- | --- |
| OS/Python | Debian/Ubuntu · Python 3.11 |
| HTTP-Port | 5000 |
| IEC104 Server | 0.0.0.0:2404 |
| IEC104 Client-Ziel | 127.0.0.1:2404 |
| k/w/T0/T1/T2/T3 | 12 / 8 / 30s / 15s / 10s / 20s |
| Authentifizierung | none |
| Persistenz | sqlite:///app.db |
| Frontend | Jinja + HTMX-ready (klassisches Jinja Layout) |

## Features

- IEC-104 Client und Server auf Basis des lokalen `iec104` Pakets
- Live-WebSocket-Stream (nur WebSocket-Transport) mit Filterung und Ringpuffer (10k Einträge)
- Tailwind-inspirierte Oberfläche mit Tabs, Seitenleisten und Live-Monitoring
- Signallistenverwaltung mit JSON/CSV-Import und Export sowie SQLite-Speicherung
- Administrationsbereich mit Logging-Einstellungen und WebSocket-Diagnose
- Makefile-Workflows und Entwicklungscontainer (Docker & Compose)
- Umfangreiche Tests (pytest) inklusive Loopback-Szenario und WebSocket-Checks

## Schnellstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
python -m app
```

Die Anwendung läuft anschließend unter `http://localhost:5000`. Der IEC-104 Server lauscht auf `0.0.0.0:2404`.

## Docker

```bash
docker compose up --build
```

## Makefile

- `make run` – Startet die Anwendung (`python -m app`)
- `make lint` – Ruff Linting
- `make format` – Black Formatierung
- `make typecheck` – mypy --strict
- `make test` – pytest
- `make dev-install` – Installiert Projekt inkl. Dev-Abhängigkeiten

## Tests

```bash
pytest
```

Die Tests umfassen Konfigurationsprüfungen, WebSocket-Endpunkte, Signallistenvalidierung und einen Loopback-Test des Stream-Busses.

## Struktur

```
app/
  __init__.py             # App Factory & Bootstrap
  config.py               # Einstellungen über Env/YAML
  socketio.py             # Socket.IO Setup (nur WebSocket)
  blueprints/             # Start, Prüfung, Signallisten, Administration
  services/               # IEC-Client/Server, Szenarien, Stream-Bus
  models/                 # SQLAlchemy Modelle (Signale)
  templates/              # Jinja2 Templates mit Tailwind-Layout
  static/                 # CSS & JS (WebSocket Frontend)
  utils/                  # Validierung & Hilfsfunktionen
```

## Hinweise

- Die Anwendung nutzt ausschließlich WebSockets (keine Long-Polling Fallbacks).
- Das lokale `iec104` Paket wird erwartet und muss die Klassen `IEC104Client` und `IEC104Server` bereitstellen.
- Standarddatenbank ist `sqlite:///app.db` (Datei wird beim ersten Start erstellt).

