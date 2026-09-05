"""Bildstabilisierung und Fleckverfolgung.

Wind ruettelt die Drohne, und jedes Ruetteln verschiebt und verschmiert das
Waermebild. Zwei Folgen hat das: Flecken wandern von Bild zu Bild, und aus
verschmierten Kanten entstehen Scheinflecken. Beides erzeugt Fehlalarme.

Wichtig zur Einordnung: **die Fluglage stabilisiert der Flugregler**, nicht
dieses Modul. Hier wird das *Bild* stabilisiert - der Versatz zwischen zwei
aufeinanderfolgenden Bildern wird geschaetzt und herausgerechnet. Damit laesst
sich derselbe Fleck ueber mehrere Bilder hinweg wiedererkennen, und nur was
mehrfach hintereinander an derselben Stelle auftaucht, gilt als echt.

Nebenbei faellt ein Mass fuer die Boeigkeit ab: der gleichmaessige Anteil des
Versatzes ist der Vorwaertsflug, der zappelnde Rest ist Wind.
"""

import math


def versatz_schaetzen(vorher, jetzt, breite, hoehe, weite=6):
    """Schaetzt die Verschiebung zwischen zwei Bildern in Bildpunkten.

    Verglichen wird die Summe der quadrierten Unterschiede fuer jede
    Verschiebung im Bereich +/- ``weite``. Das ist der einfachste brauchbare
    Weg und kommt ohne Fremdbibliothek aus; bei den kleinen Bildern hier ist
    er schnell genug, wenn vorher grob verkleinert wird.

    Gibt ``(dx, dy, guete)`` zurueck: **die Bewegung des Bildinhalts**, also
    um wie viel sich ein Fleck von ``vorher`` nach ``jetzt`` weiterbewegt hat.
    Wandert ein Fleck nach rechts, ist ``dx`` positiv. Die Guete liegt zwischen
    0 und 1 und sagt, wie eindeutig die Verschiebung war.

    Genauigkeit: rund +/- 1 Bildpunkt, weil aus Rechenzeitgruenden nur jeder
    zweite Punkt verglichen wird. Fuer die Fleckverfolgung und die
    Boeigkeitsmessung reicht das reichlich.
    """
    bester = None
    bestwert = float("inf")
    schlechtester = 0.0

    # Nur jeder zweite Punkt wird verglichen - das reicht und halbiert die
    # Rechenzeit. Entscheidend: das Stichprobenraster liegt **fest** im neuen
    # Bild (immer gerade Zeilen und Spalten) und wandert nicht mit der
    # geprueften Verschiebung mit. Sonst wuerden ungerade Verschiebungen ein
    # perfekt ausgerichtetes Teilraster vergleichen und faelschlich den Fehler
    # null ergeben - der Schaetzer haette dauerhaft +/-1 Pixel Rauschen geliefert.
    def aufs_raster(anfang):
        return anfang + (anfang % 2)

    for dy in range(-weite, weite + 1):
        y_von = aufs_raster(max(0, -dy))
        y_bis = min(hoehe, hoehe - dy)
        for dx in range(-weite, weite + 1):
            x_von = aufs_raster(max(0, -dx))
            x_bis = min(breite, breite - dx)
            summe = 0.0
            anzahl = 0
            for y in range(y_von, y_bis, 2):
                zeile_j = y * breite
                zeile_v = (y + dy) * breite
                for x in range(x_von, x_bis, 2):
                    unterschied = jetzt[zeile_j + x] - vorher[zeile_v + x + dx]
                    summe += unterschied * unterschied
                    anzahl += 1
            if anzahl == 0:
                continue
            wert = summe / anzahl
            if wert < bestwert:
                bestwert = wert
                bester = (dx, dy)
            if wert > schlechtester:
                schlechtester = wert

    if bester is None:
        return 0, 0, 0.0
    guete = 0.0 if schlechtester <= 0 else 1.0 - (bestwert / schlechtester)
    # Verglichen wurde jetzt(x) gegen vorher(x + dx). Ein Fleck, der nach
    # rechts gewandert ist, wird also bei negativem dx gefunden - fuer die
    # Aufrufer wird daraus die tatsaechliche Bewegungsrichtung.
    return -bester[0], -bester[1], max(0.0, min(1.0, guete))


class Bildstabilisator:
    """Verfolgt den Bildversatz und leitet daraus die Boeigkeit ab."""

    # So grob wird fuer die Versatzschaetzung verkleinert.
    GROB_BREITE = 48
    GROB_HOEHE = 36

    def __init__(self, glaettung=0.25):
        self._vorher = None
        self._glaettung = glaettung
        self.versatz = (0, 0)
        self.mittlerer_versatz = (0.0, 0.0)   # gleichmaessiger Flug
        self.boeigkeit_px = 0.0               # zappelnder Rest = Wind
        self.guete = 0.0

    def takt(self, rahmen):
        """Nimmt einen Waermerahmen entgegen und aktualisiert die Schaetzung."""
        grob = rahmen.verkleinern(self.GROB_BREITE, self.GROB_HOEHE)
        if self._vorher is None:
            self._vorher = grob
            return 0, 0

        dx, dy, guete = versatz_schaetzen(
            self._vorher.werte, grob.werte, grob.breite, grob.hoehe)
        self._vorher = grob
        self.guete = guete

        # Auf die volle Bildgroesse hochrechnen.
        faktor_x = rahmen.breite / float(grob.breite)
        faktor_y = rahmen.hoehe / float(grob.hoehe)
        vx, vy = dx * faktor_x, dy * faktor_y
        self.versatz = (vx, vy)

        # Gleitender Mittelwert = Vorwaertsflug, Abweichung davon = Boeen.
        mx, my = self.mittlerer_versatz
        mx += (vx - mx) * self._glaettung
        my += (vy - my) * self._glaettung
        self.mittlerer_versatz = (mx, my)
        zappeln = math.hypot(vx - mx, vy - my)
        self.boeigkeit_px += (zappeln - self.boeigkeit_px) * self._glaettung
        return vx, vy

    def ruhig(self, grenze_px=6.0):
        """Ist das Bild ruhig genug, um darauf zu vertrauen?"""
        return self.boeigkeit_px <= grenze_px

    def windstufe(self):
        """Umgangssprachliche Einordnung fuers Tablet."""
        if self.boeigkeit_px < 2.0:
            return "ruhig"
        if self.boeigkeit_px < 5.0:
            return "leichte Böen"
        if self.boeigkeit_px < 10.0:
            return "kräftige Böen"
        return "sehr unruhig"

    def als_dict(self):
        return {
            "versatz_x": round(self.versatz[0], 1),
            "versatz_y": round(self.versatz[1], 1),
            "boeigkeit_px": round(self.boeigkeit_px, 1),
            "windstufe": self.windstufe(),
            "ruhig": self.ruhig(),
            "guete": round(self.guete, 2),
        }


class Spur:
    """Ein ueber mehrere Bilder verfolgter Fleck."""

    __slots__ = ("nummer", "x", "y", "gesehen", "verpasst", "vertrauen_summe",
                 "letzte_zeit")

    def __init__(self, nummer, x, y, vertrauen, zeit):
        self.nummer = nummer
        self.x, self.y = x, y
        self.gesehen = 1
        self.verpasst = 0
        self.vertrauen_summe = vertrauen
        self.letzte_zeit = zeit

    @property
    def mittleres_vertrauen(self):
        return self.vertrauen_summe / max(1, self.gesehen)

    def bestaendigkeit(self, voll_ab=4):
        """0 bis 1: wie oft wurde der Fleck hintereinander gesehen?"""
        return min(1.0, self.gesehen / float(voll_ab))


class Fleckverfolgung:
    """Ordnet Flecken aufeinanderfolgender Bilder einander zu.

    Beruecksichtigt den geschaetzten Bildversatz: bei Seitenwind wandert ein
    liegender Mensch von Bild zu Bild durchs Bild, ist aber derselbe Mensch.
    """

    def __init__(self, hoechstabstand_px=18.0, hoechstens_verpasst=3):
        self.spuren = []
        self._naechste_nummer = 1
        self.hoechstabstand = hoechstabstand_px
        self.hoechstens_verpasst = hoechstens_verpasst

    def takt(self, flecken, versatz, zeit):
        """Ordnet die Flecken zu und haengt jedem seine Spur an.

        Gibt eine Liste von (Fleck, Spur) zurueck, in derselben Reihenfolge
        wie die uebergebenen Flecken.
        """
        vx, vy = versatz
        for spur in self.spuren:
            # Erwartete neue Lage: alte Lage plus Bildversatz.
            spur.x += vx
            spur.y += vy
            spur.verpasst += 1

        zuordnung = []
        vergeben = set()
        for fleck in flecken:
            fx, fy = fleck.mitte
            beste = None
            bester_abstand = self.hoechstabstand
            for spur in self.spuren:
                if id(spur) in vergeben:
                    continue
                abstand = math.hypot(spur.x - fx, spur.y - fy)
                if abstand < bester_abstand:
                    bester_abstand = abstand
                    beste = spur
            if beste is None:
                beste = Spur(self._naechste_nummer, fx, fy, fleck.vertrauen, zeit)
                self._naechste_nummer += 1
                self.spuren.append(beste)
            else:
                beste.x, beste.y = fx, fy
                beste.gesehen += 1
                beste.verpasst = 0
                beste.vertrauen_summe += fleck.vertrauen
                beste.letzte_zeit = zeit
            vergeben.add(id(beste))
            zuordnung.append((fleck, beste))

        self.spuren = [s for s in self.spuren if s.verpasst <= self.hoechstens_verpasst]
        return zuordnung
