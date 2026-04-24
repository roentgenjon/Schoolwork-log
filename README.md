# Schoolwork Log Analyzer

Web-App zum Analysieren von iOS-Diagnoseprotokollen bei Schoolwork-Abstürzen auf Lehrer-iPads.

## GitHub Pages (empfohlen)

Die App läuft komplett im Browser — kein Server nötig.

1. Repository forken oder Settings → Pages → Branch: `main` / Ordner: `/ (root)` aktivieren
2. Seite öffnen: `https://<dein-username>.github.io/<repo-name>/`
3. Anthropic API Key eingeben ([console.anthropic.com](https://console.anthropic.com))
4. Log-Datei hochladen → Analyse starten

Der API Key wird nur im Browser (sessionStorage) gehalten und nie irgendwo gespeichert.

## Lokale Python-Version (optional)

```bash
pip install -r requirements.txt
cp .env.example .env   # API Key eintragen
python app.py          # http://localhost:5000
```

## Analyse-Durchgänge

| Durchgang | Fokus |
|---|---|
| 1 | Crash-Muster, Exceptions, Stack Traces, Watchdog-Timeouts |
| 2 | MDM, iOS-Version, Netzwerk, Schoolwork/Classroom-Integration |
| 3 | Wurzelursachen-Synthese + Lösungsplan für den IT-Admin |
