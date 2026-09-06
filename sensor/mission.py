"""Suchflug planen und als Missionsdatei ausgeben.

Die Geometrie steckt in ``suchflug.py`` - hier wird daraus ein Flugauftrag:
Wie viele Bahnen, wie lang, wie lange dauert das, wie viele Akkus braucht es,
und wie sieht die Datei aus, die Mission Planner laden kann.

Ausgegeben wird das Format **QGC WPL 110**. Es ist eine schlichte
tabulatorgetrennte Textdatei, die Mission Planner, QGroundControl und
ArduPilot gleichermassen lesen. Zwoelf Spalten je Zeile:

    Index · aktuell · Bezugssystem · Befehl · Parameter 1-4 ·
    Breite · Laenge · Hoehe · weiterfliegen

Bezugssystem 3 heisst "Hoehe ueber dem Startpunkt" - genau das, was fuer einen
Suchflug ueber welligem Gelaende gewuenscht ist. Die Befehlsnummern stammen aus
dem MAVLink-Standard: 16 Wegpunkt, 22 Start, 20 Rueckkehr zum Startpunkt.
"""

import math

import suchflug

BEFEHL_WEGPUNKT = 16
BEFEHL_START = 22
BEFEHL_HEIMKEHR = 20
SYSTEM_RELATIV = 3      # Hoehe relativ zum Startpunkt
SYSTEM_ABSOLUT = 0      # nur fuer die Heimatzeile

# Wie viel Akku als Reserve unangetastet bleibt.
RESERVE = 0.25


def _zeile(index, aktuell, system, befehl, breite, laenge, hoehe,
           p1=0.0, p2=0.0, p3=0.0, p4=0.0):
    return "\t".join([
        str(index), str(aktuell), str(system), str(befehl),
        "%.8f" % p1, "%.8f" % p2, "%.8f" % p3, "%.8f" % p4,
        "%.8f" % breite, "%.8f" % laenge, "%.6f" % hoehe, "1",
    ])


def qgc_wpl(wegpunkte, hoehe_m, startpunkt=None, mit_heimkehr=True):
    """Baut die Missionsdatei im Format QGC WPL 110.

    ``startpunkt`` ist der Ort, von dem gestartet wird. Fehlt er, wird der
    erste Wegpunkt genommen.
    """
    if not wegpunkte:
        raise ValueError("Ohne Wegpunkte laesst sich keine Mission bauen")

    heimat = startpunkt or wegpunkte[0]
    zeilen = ["QGC WPL 110"]
    # Zeile 0 ist immer die Heimatposition, sie zaehlt nicht als Wegpunkt.
    zeilen.append(_zeile(0, 1, SYSTEM_ABSOLUT, BEFEHL_WEGPUNKT,
                         heimat[0], heimat[1], 0.0))
    index = 1
    zeilen.append(_zeile(index, 0, SYSTEM_RELATIV, BEFEHL_START,
                         heimat[0], heimat[1], hoehe_m))
    for breite, laenge in wegpunkte:
        index += 1
        zeilen.append(_zeile(index, 0, SYSTEM_RELATIV, BEFEHL_WEGPUNKT,
                             breite, laenge, hoehe_m))
    if mit_heimkehr:
        index += 1
        zeilen.append(_zeile(index, 0, SYSTEM_RELATIV, BEFEHL_HEIMKEHR,
                             0.0, 0.0, 0.0))
    return "\n".join(zeilen) + "\n"


def flaeche_ha(ecke_a, ecke_b):
    """Flaeche des aufgespannten Rechtecks in Hektar."""
    breite_m = suchflug.abstand_m((ecke_a[0], ecke_a[1]), (ecke_a[0], ecke_b[1]))
    hoehe_m = suchflug.abstand_m((ecke_a[0], ecke_a[1]), (ecke_b[0], ecke_a[1]))
    return breite_m * hoehe_m / 10000.0


def planen(ecke_a, ecke_b, hoehe_m, konfig, tempo_ms=8.0, richtung="nord",
           flugzeit_min=22.0, startpunkt=None):
    """Rechnet einen kompletten Suchflug durch.

    Gibt ein Woerterbuch mit allen Zahlen fuers Tablet zurueck, dazu die
    Wegpunkte und die fertige Missionsdatei.
    """
    abstand = suchflug.streifenabstand(hoehe_m, konfig.BILDWINKEL_QUER,
                                       konfig.STREIFEN_UEBERLAPPUNG)
    wegpunkte = suchflug.maeander(ecke_a, ecke_b, abstand, richtung)
    strecke = suchflug.strecke_m(wegpunkte)
    dauer_s = strecke / tempo_ms if tempo_ms > 0 else 0.0

    nutzbar_s = flugzeit_min * 60.0 * (1.0 - RESERVE)
    akkus = int(math.ceil(dauer_s / nutzbar_s)) if nutzbar_s > 0 else 0

    gebiet = flaeche_ha(ecke_a, ecke_b)
    return {
        "wegpunkte": [{"breite": round(b, 6), "laenge": round(l, 6)}
                      for b, l in wegpunkte],
        "anzahl_wegpunkte": len(wegpunkte),
        "bahnen": max(0, len(wegpunkte) // 2),
        "hoehe_m": round(hoehe_m, 1),
        "richtung": richtung,
        "streifenbreite_m": round(
            suchflug.streifenbreite(hoehe_m, konfig.BILDWINKEL_QUER), 1),
        "bahnabstand_m": round(abstand, 1),
        "strecke_m": round(strecke),
        "dauer_min": round(dauer_s / 60.0, 1),
        "flaeche_ha": round(gebiet, 2),
        "akkus": akkus,
        "tempo_ms": tempo_ms,
        "flugzeit_min": flugzeit_min,
        "hoechste_sinnvolle_hoehe_m": round(suchflug.empfohlene_hoehe(
            konfig.MINDESTPIXEL_PERSON, konfig.BILDWINKEL_QUER,
            konfig.GITTER_BREITE), 1),
        "mission": qgc_wpl(wegpunkte, hoehe_m, startpunkt) if wegpunkte else "",
    }
