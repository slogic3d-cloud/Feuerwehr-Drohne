"""GPS-Empfaenger (NMEA 0183).

Gebraucht wird das GPS nur draussen: bei jedem Treffer werden Koordinaten
mitgeschrieben, damit die Fundstelle an die Einsatzleitung weitergegeben
werden kann. In Gebaeuden liefert der Empfaenger nichts - das ist erwartet
und kein Fehler, die Position wird dann einfach nicht gesetzt.
"""

import random
import time


class Position:
    __slots__ = ("breite", "laenge", "hoehe_m", "satelliten", "zeit")

    def __init__(self, breite, laenge, hoehe_m=None, satelliten=0, zeit=None):
        self.breite = breite
        self.laenge = laenge
        self.hoehe_m = hoehe_m
        self.satelliten = satelliten
        self.zeit = zeit if zeit is not None else time.time()

    def als_dict(self):
        return {
            "breite": round(self.breite, 6),
            "laenge": round(self.laenge, 6),
            "hoehe_m": self.hoehe_m,
            "satelliten": self.satelliten,
        }

    def __repr__(self):
        return "Position(%.6f, %.6f, %d Satelliten)" % (
            self.breite, self.laenge, self.satelliten)


def _grad(roh, richtung):
    """Wandelt das NMEA-Format ggmm.mmmm in Dezimalgrad."""
    if not roh:
        return None
    punkt = roh.find(".")
    if punkt < 3:
        return None
    grad = int(roh[:punkt - 2])
    minuten = float(roh[punkt - 2:])
    wert = grad + minuten / 60.0
    if richtung in ("S", "W"):
        wert = -wert
    return wert


def satz_auswerten(satz):
    """Wertet einen GGA-Satz aus. Gibt ``None``, wenn kein gueltiger Fix da ist."""
    if not satz.startswith("$") or "GGA" not in satz[:7]:
        return None
    if "*" in satz:
        satz = satz[:satz.index("*")]
    teile = satz.split(",")
    if len(teile) < 10:
        return None
    try:
        gueltig = int(teile[6] or 0)
    except ValueError:
        return None
    if gueltig == 0:
        return None
    breite = _grad(teile[2], teile[3])
    laenge = _grad(teile[4], teile[5])
    if breite is None or laenge is None:
        return None
    try:
        satelliten = int(teile[7] or 0)
    except ValueError:
        satelliten = 0
    try:
        hoehe = float(teile[9]) if teile[9] else None
    except ValueError:
        hoehe = None
    return Position(breite, laenge, hoehe, satelliten)


class NMEAEmpfaenger:
    def __init__(self, port, baud=9600):
        try:
            import serial
        except ImportError as fehler:
            raise RuntimeError("pyserial fehlt") from fehler
        self._port = serial.Serial(port, baud, timeout=0.1)
        self._letzte = None

    def lies(self):
        while self._port.in_waiting:
            zeile = self._port.readline().decode("ascii", "ignore").strip()
            position = satz_auswerten(zeile)
            if position is not None:
                self._letzte = position
        return self._letzte

    def schliessen(self):
        self._port.close()


class SimuliertesGPS:
    """Liefert eine langsam wandernde Position bei Ebersdorf bei Coburg."""

    def __init__(self, breite=50.2472, laenge=11.0361, saat=3):
        self._breite = breite
        self._laenge = laenge
        self._zufall = random.Random(saat)
        self._start = time.time()

    def lies(self):
        t = time.time() - self._start
        return Position(
            self._breite + t * 1e-6 + self._zufall.uniform(-2e-6, 2e-6),
            self._laenge + t * 1.4e-6 + self._zufall.uniform(-2e-6, 2e-6),
            342.0, 9)

    def schliessen(self):
        pass


def erzeuge(quelle, baud):
    if quelle == "simulation":
        return SimuliertesGPS()
    return NMEAEmpfaenger(quelle, baud)
