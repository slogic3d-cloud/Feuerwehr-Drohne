"""Bodenstation-Schnittstelle.

Ein kleiner HTTP-Server aus der Standardbibliothek - kein Flask, kein
Websocket-Paket, nichts nachzuinstallieren. Das Tablet holt sich die Seite und
haengt sich danach an einen Ereignisstrom (Server-Sent Events), ueber den
jedes neue Lagebild geschoben wird.

Warum kein Videostrom? Weil das Waermebild als Zahlengitter kleiner ist als
ein JPEG-Strom und der Browser daraus selbst ein Falschfarbenbild zeichnet -
mit echten Temperaturen beim Antippen. Ein Gitter von 128x96 Zehntelgrad-
Werten sind rund 40 kB je Bild, bei 8 Bildern je Sekunde etwa 2 Mbit/s. Das
schafft WLAN muehelos und LTE im Freien auch.
"""

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

SEITE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "bodenstation", "index.html")


class Zustand:
    """Gemeinsamer Zustand zwischen Auswerteschleife und Webserver."""

    def __init__(self):
        self._sperre = threading.Condition()
        self._lage = None
        self._stand = 0
        self.treffer_verwaltung = None
        self.steuerung = {"schub": 0.0, "nick": 0.0, "roll": 0.0, "gier": 0.0,
                          "zeit": 0.0}
        self.statistik = {"takte": 0, "laufzeit_s": 0.0, "bilder_je_s": 0.0}
        self.suchplan = {}

    def melden(self, lage_dict):
        with self._sperre:
            self._lage = lage_dict
            self._stand += 1
            self._sperre.notify_all()

    def lage(self):
        with self._sperre:
            return self._lage, self._stand

    def warten(self, letzter_stand, zeitgrenze=15.0):
        """Wartet auf ein neues Lagebild. Gibt (Lagebild, Stand) zurueck."""
        with self._sperre:
            if self._stand == letzter_stand:
                self._sperre.wait(zeitgrenze)
            return self._lage, self._stand


class Griff(BaseHTTPRequestHandler):
    zustand = None
    server_version = "Suchkopf/1.0"

    # Zugriffe nicht einzeln protokollieren - das Log liefe sonst voll.
    def log_message(self, format, *args):
        pass

    # -- Hilfen ----------------------------------------------------------
    def _json(self, inhalt, code=200):
        koerper = json.dumps(inhalt, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(koerper)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(koerper)

    def _koerper_lesen(self):
        laenge = int(self.headers.get("Content-Length") or 0)
        if not laenge:
            return {}
        try:
            return json.loads(self.rfile.read(laenge).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {}

    # -- GET -------------------------------------------------------------
    def do_GET(self):
        weg = urlparse(self.path)
        pfad = weg.path

        if pfad in ("/", "/index.html"):
            return self._seite()
        if pfad == "/lage":
            lage, stand = self.zustand.lage()
            return self._json({"stand": stand, "lage": lage})
        if pfad == "/strom":
            return self._strom()
        if pfad == "/treffer":
            v = self.zustand.treffer_verwaltung
            return self._json({"treffer": v.liste() if v else []})
        if pfad == "/zustand":
            return self._json({
                "statistik": self.zustand.statistik,
                "suchplan": self.zustand.suchplan,
                "steuerung": self.zustand.steuerung,
            })
        self.send_error(404, "Nicht gefunden")

    def _seite(self):
        try:
            with open(SEITE, "rb") as datei:
                inhalt = datei.read()
        except OSError:
            self.send_error(500, "Bodenstation-Seite nicht gefunden")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(inhalt)))
        self.end_headers()
        self.wfile.write(inhalt)

    def _strom(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        stand = -1
        try:
            while True:
                lage, stand_neu = self.zustand.warten(stand)
                if stand_neu == stand:
                    # Nichts Neues - Lebenszeichen schicken, damit das Tablet
                    # merkt, dass die Verbindung noch steht.
                    self.wfile.write(b": still\n\n")
                    self.wfile.flush()
                    continue
                stand = stand_neu
                v = self.zustand.treffer_verwaltung
                paket = {
                    "stand": stand,
                    "lage": lage,
                    "treffer": v.liste() if v else [],
                    "statistik": self.zustand.statistik,
                    "suchplan": self.zustand.suchplan,
                }
                daten = json.dumps(paket, ensure_ascii=False)
                self.wfile.write(("data: " + daten + "\n\n").encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass  # Tablet hat die Seite geschlossen

    # -- POST ------------------------------------------------------------
    def do_POST(self):
        pfad = urlparse(self.path).path

        if pfad == "/steuerung":
            daten = self._koerper_lesen()
            self.zustand.steuerung = {
                "schub": float(daten.get("schub", 0.0)),
                "nick": float(daten.get("nick", 0.0)),
                "roll": float(daten.get("roll", 0.0)),
                "gier": float(daten.get("gier", 0.0)),
                "zeit": time.time(),
            }
            # Hier wird spaeter der MAVLink-Befehl an den Flugregler gesetzt.
            return self._json({"uebernommen": True})

        if pfad == "/bewerten":
            daten = self._koerper_lesen()
            v = self.zustand.treffer_verwaltung
            if v is None:
                return self._json({"fehler": "keine Trefferverwaltung"}, 503)
            erfolg = v.bewerten(int(daten.get("nummer", 0)),
                                daten.get("bestaetigt"),
                                daten.get("verworfen"))
            return self._json({"erfolg": erfolg, "treffer": v.liste()})

        self.send_error(404, "Nicht gefunden")


def starten(zustand, port):
    """Startet den Webserver in einem eigenen Faden."""
    Griff.zustand = zustand
    server = ThreadingHTTPServer(("0.0.0.0", port), Griff)
    server.daemon_threads = True
    faden = threading.Thread(target=server.serve_forever, daemon=True)
    faden.start()
    return server
