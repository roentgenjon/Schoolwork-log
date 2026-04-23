# Schoolwork Log Analyzer

Web-App zum Analysieren von iOS-Diagnoseprotokollen bei Schoolwork-Abstürzen auf Lehrer-iPads.

## Setup

```bash
# 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 2. API-Key setzen
cp .env.example .env
# .env bearbeiten und ANTHROPIC_API_KEY eintragen

# 3. App starten
python app.py
```

Dann im Browser öffnen: **http://localhost:5000**

## Funktionsweise

1. Log-Datei per Drag & Drop oder Dateiauswahl hochladen (`.log`, `.crash`, `.ips`, `.txt` usw.)
2. „Analyse starten" klicken
3. Die KI analysiert das Log in **drei unabhängigen Durchgängen**:
   - **Durchgang 1** – Crash-Muster, Exceptions, Speicherfehler, Watchdog-Timeouts
   - **Durchgang 2** – MDM-Konfiguration, iOS-Version, Netzwerk, Schoolwork/Classroom-Integration
   - **Durchgang 3** – Wurzelursachen-Synthese und konkreter Lösungsplan für den IT-Admin

Die Ergebnisse werden in Echtzeit gestreamt und direkt im Browser angezeigt.

## Voraussetzungen

- Python 3.10+
- Anthropic API Key (https://console.anthropic.com)
