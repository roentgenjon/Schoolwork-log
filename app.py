import os
import json
from flask import Flask, render_template, request, Response, stream_with_context
import anthropic
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB max

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

ANALYSIS_PASSES = [
    {
        "id": "pass1",
        "title": "1. Durchgang: Crash-Muster & Fehler",
        "icon": "🔍",
        "system": (
            "Du bist ein erfahrener iOS-Crash-Analyst. Analysiere Apple-Diagnoseprotokolle "
            "auf Abstürze, Exceptions, Speicherfehler und kritische Fehlermuster. "
            "Antworte auf Deutsch. Sei präzise und technisch detailliert."
        ),
        "prompt": (
            "Analysiere dieses iOS-Diagnoseprotokoll EXTREM GRÜNDLICH auf:\n"
            "1. Exception-Typen (EXC_BAD_ACCESS, SIGABRT, SIGSEGV, etc.)\n"
            "2. Stack Traces und fehlerhafte Methoden\n"
            "3. Speicherprobleme (Memory Pressure, OOM, Retain Cycles)\n"
            "4. Deadlocks und Threading-Probleme\n"
            "5. Watchdog-Timeouts (0x8badf00d)\n"
            "6. Spezifische Schoolwork-App-Fehler\n\n"
            "Liste ALLE gefundenen Probleme mit Zeilennummern/Adressen auf. "
            "Priorisiere nach Schweregrad (KRITISCH/HOCH/MITTEL/NIEDRIG).\n\n"
            "LOG:\n{log}"
        ),
    },
    {
        "id": "pass2",
        "title": "2. Durchgang: System & Infrastruktur",
        "icon": "🔬",
        "system": (
            "Du bist ein Apple-MDM- und iOS-Systemexperte für Schulumgebungen. "
            "Analysiere Diagnoseprotokolle auf MDM-Konfigurationsprobleme, "
            "iOS-Versionsinkompatibilitäten, Netzwerkfehler und "
            "Classroom/Schoolwork-spezifische Infrastrukturprobleme. "
            "Antworte auf Deutsch mit konkreten technischen Details."
        ),
        "prompt": (
            "Führe einen zweiten, unabhängigen Analysedurchgang durch. Fokussiere auf:\n"
            "1. iOS/iPadOS-Versionsprobleme und Inkompatibilitäten\n"
            "2. MDM-Konfigurationsfehler (Profil, Policies, Restrictions)\n"
            "3. Netzwerk- und iCloud-Verbindungsfehler\n"
            "4. Apple School Manager / Classroom-Integration\n"
            "5. Berechtigungs- und Entitlement-Probleme\n"
            "6. Speicherplatz und Ressourcenengpässe auf dem iPad\n"
            "7. Background-Task- und App-Lifecycle-Probleme\n"
            "8. Corrupted Caches oder beschädigte Konfigurationsdateien\n\n"
            "Identifiziere ALLE Systemfaktoren die den Absturz verursacht haben könnten. "
            "Nenne konkrete Werte aus dem Log (Prozesse, Versionen, Adressen).\n\n"
            "LOG:\n{log}"
        ),
    },
    {
        "id": "pass3",
        "title": "3. Durchgang: Synthese & Lösungsplan",
        "icon": "📋",
        "system": (
            "Du bist ein Senior Apple-IT-Berater für Bildungseinrichtungen. "
            "Basierend auf einer vollständigen Log-Analyse erstellst du einen "
            "klaren, umsetzbaren Lösungsplan für IT-Administratoren. "
            "Antworte auf Deutsch. Sei praktisch und lösungsorientiert."
        ),
        "prompt": (
            "Führe den dritten und finalen Analysedurchgang durch. Erstelle:\n\n"
            "**WURZELURSACHEN-ANALYSE:**\n"
            "Identifiziere die 1-3 wahrscheinlichsten Hauptursachen des Absturzes "
            "mit Begründung aus dem Log.\n\n"
            "**SOFORTMASSNAHMEN** (kann IT-Admin heute tun):\n"
            "- Konkrete Schritte mit Settings/Pfaden\n\n"
            "**MITTELFRISTIGE MASSNAHMEN** (diese Woche):\n"
            "- Updates, Rekonfigurationen, MDM-Änderungen\n\n"
            "**LANGFRISTIGE EMPFEHLUNGEN**:\n"
            "- Infrastruktur- und Policy-Verbesserungen\n\n"
            "**WEITERE INFORMATIONEN die benötigt werden:**\n"
            "- Was sollte der IT-Admin noch liefern um die Diagnose zu verbessern?\n\n"
            "**SCHWEREGRAD:** [KRITISCH/HOCH/MITTEL]\n"
            "**GESCHÄTZTE LÖSUNGSZEIT:**\n\n"
            "LOG:\n{log}"
        ),
    },
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "logfile" not in request.files:
        return {"error": "Keine Datei hochgeladen"}, 400

    file = request.files["logfile"]
    if file.filename == "":
        return {"error": "Keine Datei ausgewählt"}, 400

    try:
        log_content = file.read().decode("utf-8", errors="replace")
    except Exception as e:
        return {"error": f"Datei konnte nicht gelesen werden: {e}"}, 400

    if len(log_content) > 200_000:
        log_content = log_content[:200_000] + "\n\n[... Log gekürzt auf 200.000 Zeichen ...]"

    def generate():
        for pass_config in ANALYSIS_PASSES:
            yield f"data: {json.dumps({'type': 'pass_start', 'pass_id': pass_config['id'], 'title': pass_config['title'], 'icon': pass_config['icon']})}\n\n"

            prompt = pass_config["prompt"].format(log=log_content)

            try:
                with client.messages.stream(
                    model="claude-sonnet-4-6",
                    max_tokens=2048,
                    system=pass_config["system"],
                    messages=[{"role": "user", "content": prompt}],
                ) as stream:
                    for text in stream.text_stream:
                        yield f"data: {json.dumps({'type': 'text', 'pass_id': pass_config['id'], 'content': text})}\n\n"

            except anthropic.APIError as e:
                yield f"data: {json.dumps({'type': 'error', 'pass_id': pass_config['id'], 'message': str(e)})}\n\n"

            yield f"data: {json.dumps({'type': 'pass_end', 'pass_id': pass_config['id']})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
