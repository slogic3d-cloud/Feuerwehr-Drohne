#!/usr/bin/env python3
"""Suchkopf - Hauptprogramm auf der Drohne.

Liest im Takt das Waermebild, wertet es aus, verwaltet Treffer und stellt
alles der Bodenstation bereit. Ohne angeschlossene Hardware laeuft alles im
Simulationsmodus weiter, sodass sich Auswertung und Oberflaeche am Schreibtisch
entwickeln lassen.

    python3 suchkopf.py                 # Simulation, Oberflaeche auf Port 8080
    WAERMEBILD_TYP=infiray python3 suchkopf.py
    python3 suchkopf.py --pruefen       # einmal auswerten und Ergebnis zeigen
"""

import argparse
import sys
import time

import konfig
import erkennung
import lernen
import stabilisierung
import suchflug
import web
from geraete import gps as gps_modul
from geraete import waermebild as waermebild_modul
from treffer import Trefferverwaltung


def suchplan_bauen(hoehe_m, tempo_ms=8.0):
    return suchflug.suchplan(
        hoehe_m, konfig.BILDWINKEL_QUER, 256, konfig.GITTER_BREITE,
        konfig.STREIFEN_UEBERLAPPUNG, tempo_ms, konfig.MINDESTPIXEL_PERSON)


def einmal_pruefen():
    """Wertet ein einzelnes Bild aus und schreibt das Ergebnis auf die Konsole."""
    kamera = waermebild_modul.erzeuge(konfig.WAERMEBILD_TYP, konfig.WAERMEBILD_QUELLE)
    empfaenger = gps_modul.erzeuge(konfig.GPS_QUELLE, konfig.GPS_BAUD)
    lage = erkennung.auswerten(kamera.lies(), konfig,
                               hoehe_m=konfig.FLUGHOEHE_M,
                               position=empfaenger.lies())
    modell = lernen.Modell.laden()
    print("Lernendes Modell: %s"
          % ("%d Beispiele, Gewicht %.2f" % (modell.beispiele, modell.gewicht())
             if modell else "keins vorhanden - es entscheiden die Regeln"))
    print("Untergrund %.1f Grad, Flughoehe %.0f m" % (lage.hintergrund_c, lage.hoehe_m))
    print("Bewertung: %.2f - %s" % (lage.vertrauen, lage.stufe))
    for grund in lage.begruendung:
        print("  -", grund)
    for fleck in lage.flecken[:5]:
        ort = ("%.6f, %.6f" % fleck.koordinate) if fleck.koordinate else "ohne GPS"
        print("  Fleck: %3d Zellen, +%.1f K, Vertrauen %.2f, Fundort %s"
              % (len(fleck.zellen), fleck.abhebung_k, fleck.vertrauen, ort))
    print("\nSuchplan:")
    for schluessel, wert in suchplan_bauen(konfig.FLUGHOEHE_M).items():
        print("  %-28s %s" % (schluessel, wert))
    kamera.schliessen()
    empfaenger.schliessen()
    return 0


def hauptschleife(port, takt_hz, laufzeit=None):
    kamera = waermebild_modul.erzeuge(konfig.WAERMEBILD_TYP, konfig.WAERMEBILD_QUELLE)
    empfaenger = gps_modul.erzeuge(konfig.GPS_QUELLE, konfig.GPS_BAUD)
    verwaltung = Trefferverwaltung(konfig)
    stabilisator = stabilisierung.Bildstabilisator()
    verfolgung = stabilisierung.Fleckverfolgung()

    modell = lernen.Modell.laden()
    if modell is not None:
        print("Lernendes Modell geladen: %d Beispiele, Gewicht %.2f"
              % (modell.beispiele, modell.gewicht()))
    else:
        print("Kein trainiertes Modell - es entscheiden die Regeln. "
              "Nach ein paar bewerteten Fluegen: python3 lernen.py")

    zustand = web.Zustand()
    zustand.treffer_verwaltung = verwaltung
    zustand.suchplan = suchplan_bauen(konfig.FLUGHOEHE_M)
    server = web.starten(zustand, port)

    print("Suchkopf laeuft. Bodenstation: http://<Adresse der Drohne>:%d/" % port)
    print("Waermebild: %s | GPS: %s | Takt: %.0f Hz"
          % (konfig.WAERMEBILD_TYP, konfig.GPS_QUELLE, takt_hz))

    pause = 1.0 / max(0.5, takt_hz)
    begonnen = time.time()
    takte = 0
    kurs = 0.0

    try:
        while True:
            runde = time.time()
            try:
                rahmen = kamera.lies()
            except Exception as fehler:          # Kamera darf den Flug nicht stoppen
                print("Waermebild gestoert: %s" % fehler)
                time.sleep(0.5)
                continue

            versatz = stabilisator.takt(rahmen)
            position = empfaenger.lies()
            lage = erkennung.auswerten(rahmen, konfig,
                                       hoehe_m=konfig.FLUGHOEHE_M,
                                       position=position, kurs_grad=kurs)
            zuordnung = verfolgung.takt(lage.flecken, versatz, lage.zeit)
            erkennung.nachbewerten(lage, zuordnung, konfig, modell)
            lage.windlage = stabilisator.als_dict()
            if not stabilisator.ruhig():
                lage.begruendung.append(
                    "Bild unruhig (%s) - Bewertung vorsichtiger lesen"
                    % stabilisator.windstufe())
            neuer = verwaltung.takt(lage)
            if neuer is not None:
                ort = ("%.6f, %.6f" % neuer.fundort) if neuer.fundort else "ohne GPS"
                print("TREFFER %d  %s  Vertrauen %.2f  Fundort %s"
                      % (neuer.nummer, neuer.stufe, neuer.vertrauen, ort))

            takte += 1
            laufzeit_s = time.time() - begonnen
            zustand.statistik = {
                "takte": takte,
                "laufzeit_s": round(laufzeit_s, 1),
                "bilder_je_s": round(takte / laufzeit_s, 1) if laufzeit_s > 0 else 0.0,
                "treffer": len(verwaltung.treffer),
                "modell_beispiele": modell.beispiele if modell else 0,
            }
            zustand.melden(lage.als_dict(mit_bild=True))

            if laufzeit is not None and laufzeit_s >= laufzeit:
                break
            rest = pause - (time.time() - runde)
            if rest > 0:
                time.sleep(rest)
    except KeyboardInterrupt:
        print("\nBeendet.")
    finally:
        server.shutdown()
        kamera.schliessen()
        empfaenger.schliessen()
    return 0


def main(argumente=None):
    zerleger = argparse.ArgumentParser(description="Suchkopf der Personensuchdrohne")
    zerleger.add_argument("--port", type=int, default=konfig.WEB_PORT,
                          help="Port der Bodenstation (Standard %d)" % konfig.WEB_PORT)
    zerleger.add_argument("--takt", type=float, default=konfig.TAKT_HZ,
                          help="Auswertungen je Sekunde")
    zerleger.add_argument("--hoehe", type=float, default=None,
                          help="Flughoehe in Metern (solange keine vom Flugregler kommt)")
    zerleger.add_argument("--laufzeit", type=float, default=None,
                          help="nach so vielen Sekunden beenden (fuer Tests)")
    zerleger.add_argument("--pruefen", action="store_true",
                          help="einmal auswerten und beenden")
    werte = zerleger.parse_args(argumente)

    if werte.hoehe is not None:
        konfig.FLUGHOEHE_M = werte.hoehe
    if werte.pruefen:
        return einmal_pruefen()
    return hauptschleife(werte.port, werte.takt, werte.laufzeit)


if __name__ == "__main__":
    sys.exit(main())
