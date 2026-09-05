"""Zentrale Einstellungen des Suchkopfs.

Alle Werte lassen sich beim Start ueber Umgebungsvariablen ueberschreiben,
damit an der Einsatzstelle nichts umprogrammiert werden muss:

    WAERMEBILD_TYP=infiray FLUGHOEHE_M=45 python3 suchkopf.py
"""

import os


def _text(name, standard):
    return os.environ.get(name, standard)


def _zahl(name, standard):
    try:
        return float(os.environ[name])
    except (KeyError, ValueError):
        return standard


def _ganz(name, standard):
    try:
        return int(os.environ[name])
    except (KeyError, ValueError):
        return standard


# --- Geraete -------------------------------------------------------------
# "simulation" laesst den Suchkopf ohne angeschlossene Hardware laufen.
WAERMEBILD_TYP    = _text("WAERMEBILD_TYP", "simulation")   # infiray | mlx90640 | simulation
WAERMEBILD_QUELLE = _text("WAERMEBILD_QUELLE", "/dev/video0")

GPS_QUELLE = _text("GPS_QUELLE", "simulation")              # z. B. /dev/ttyAMA0
GPS_BAUD   = _ganz("GPS_BAUD", 9600)

# --- Kamera und Flug -----------------------------------------------------
# Bildwinkel der Waermebildkamera in Grad, quer und hoch.
# InfiRay P2 Pro / Topdon TC001: 256x192 Pixel, 56 Grad diagonal.
BILDWINKEL_QUER = _zahl("BILDWINKEL_QUER", 45.6)
BILDWINKEL_HOCH = _zahl("BILDWINKEL_HOCH", 35.4)

# Flughoehe ueber Grund. Wird vom Flugregler geliefert; der Wert hier ist der
# Rueckfall, solange keine Hoehe anliegt.
FLUGHOEHE_M = _zahl("FLUGHOEHE_M", 40.0)

# So viele Pixel muss eine liegende Person mindestens lang sein, damit die
# Erkennung eine Chance hat. Daraus wird die groesste sinnvolle Suchhoehe
# berechnet (siehe suchflug.empfohlene_hoehe).
MINDESTPIXEL_PERSON = _zahl("MINDESTPIXEL_PERSON", 8.0)

# Ueberlappung benachbarter Suchstreifen.
STREIFEN_UEBERLAPPUNG = _zahl("STREIFEN_UEBERLAPPUNG", 0.25)

# --- Auswertung ----------------------------------------------------------
# Analysegitter. Steht es auf der vollen Kameraaufloesung, wird gar nicht
# verkleinert - gemessen kostet das Verkleinern sogar mehr Rechenzeit, als es
# bei der Fleckensuche spart, und aus der Luft ist jedes Pixel wertvoll:
# 256 statt 128 Zellen quer verdoppeln die hoechste sinnvolle Flughoehe.
# Fuer den MLX90640 (32x24) bleibt der Wert wirkungslos.
GITTER_BREITE = _ganz("GITTER_BREITE", 256)
GITTER_HOEHE  = _ganz("GITTER_HOEHE", 192)

# Aus der Luft zaehlt der Kontrast zum Boden, nicht die absolute Temperatur:
# eine Person in 40 m Hoehe erscheint durch Luft und Mischpixel deutlich
# kuehler als 33 Grad. Ein Mensch hebt sich nachts aber klar vom Boden ab.
ABHEBUNG_K = _zahl("ABHEBUNG_K", 2.5)

# Obergrenze der Abhebung: alles, was viel heisser als der Boden ist, ist
# Technik oder Feuer - Auspuff, Trafohaeuschen, Lagerfeuer, Glutnest.
ABHEBUNG_MAX_K = _zahl("ABHEBUNG_MAX_K", 18.0)

# Groesse eines Flecks in Prozent der Bildflaeche. Aus 40 m ist eine Person
# winzig; alles Grosse ist Strasse, Dach oder Feld in der Abendsonne.
FLECK_MIN_ANTEIL = _zahl("FLECK_MIN_ANTEIL", 0.00015)
FLECK_MAX_ANTEIL = _zahl("FLECK_MAX_ANTEIL", 0.030)

# Ab diesem Vertrauenswert wird ein Treffer gemeldet und gespeichert.
TREFFER_SCHWELLE = _zahl("TREFFER_SCHWELLE", 0.55)
# So lange muss ein Verdacht bestehen bleiben, bevor Alarm ausgeloest wird.
TREFFER_HALTEZEIT_S = _zahl("TREFFER_HALTEZEIT_S", 0.8)
# Treffer naeher als dieser Abstand gelten als dieselbe Fundstelle.
TREFFER_ZUSAMMENFASSEN_M = _zahl("TREFFER_ZUSAMMENFASSEN_M", 15.0)
# Ohne GPS-Position wird stattdessen zeitlich zusammengefasst.
TREFFER_ZUSAMMENFASSEN_S = _zahl("TREFFER_ZUSAMMENFASSEN_S", 8.0)

# --- Betrieb -------------------------------------------------------------
TAKT_HZ        = _zahl("TAKT_HZ", 8.0)
WEB_PORT       = _ganz("WEB_PORT", 8080)
TREFFER_ORDNER = _text("TREFFER_ORDNER", "treffer")
