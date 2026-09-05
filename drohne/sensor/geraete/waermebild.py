"""Waermebildkameras.

Alle Kameras liefern dasselbe: ein ``Waermerahmen`` mit einer Liste von
Temperaturen in Grad Celsius, zeilenweise von links oben nach rechts unten.
Damit ist die Auswertung von der konkreten Kamera unabhaengig, und der
Simulator laesst sich ohne jede Hardware benutzen.
"""

import math
import random
import time


class Waermerahmen:
    """Ein Waermebild in Grad Celsius."""

    __slots__ = ("breite", "hoehe", "werte", "zeit")

    def __init__(self, breite, hoehe, werte, zeit=None):
        self.breite = breite
        self.hoehe = hoehe
        self.werte = werte
        self.zeit = zeit if zeit is not None else time.time()

    def bei(self, x, y):
        return self.werte[y * self.breite + x]

    def verkleinern(self, neue_breite, neue_hoehe):
        """Rechnet den Rahmen auf ein groeberes Gitter herunter.

        Es wird der Mittelwert jedes Kaestchens gebildet, nicht der naechste
        Nachbar: eine liegende Person darf beim Verkleinern nicht verschwinden.
        """
        if neue_breite >= self.breite and neue_hoehe >= self.hoehe:
            return self
        neu = [0.0] * (neue_breite * neue_hoehe)
        for zy in range(neue_hoehe):
            y0 = zy * self.hoehe // neue_hoehe
            y1 = max(y0 + 1, (zy + 1) * self.hoehe // neue_hoehe)
            for zx in range(neue_breite):
                x0 = zx * self.breite // neue_breite
                x1 = max(x0 + 1, (zx + 1) * self.breite // neue_breite)
                summe = 0.0
                anzahl = 0
                for y in range(y0, y1):
                    zeile = y * self.breite
                    for x in range(x0, x1):
                        summe += self.werte[zeile + x]
                        anzahl += 1
                neu[zy * neue_breite + zx] = summe / anzahl
        return Waermerahmen(neue_breite, neue_hoehe, neu, self.zeit)

    def kennwerte(self):
        w = self.werte
        return min(w), max(w), sum(w) / len(w)


class WaermebildFehler(Exception):
    pass


# ---------------------------------------------------------------------------
# InfiRay P2 Pro / Topdon TC001 (USB, 256x192)
# ---------------------------------------------------------------------------

class InfiRayP2Pro:
    """USB-Waermebildkamera der P2-Pro-Familie.

    Die Kamera meldet sich als gewoehnliche UVC-Kamera mit 256x384 Pixeln:
    die obere Haelfte ist das sichtbare Falschfarbenbild, die untere Haelfte
    enthaelt die Rohtemperaturen. Je Pixel stehen zwei Bytes bereit, der Wert
    ist die Temperatur in 1/64 Kelvin:

        Grad Celsius = (hoch * 256 + niedrig) / 64 - 273.15

    Gelesen wird ueber OpenCV, weil das auf dem Pi ohne Zusatzarbeit an den
    UVC-Strom kommt. OpenCV ist die einzige Stelle im ganzen Projekt, die eine
    Fremdbibliothek braucht - faellt sie aus, laeuft alles andere weiter.
    """

    BREITE = 256
    HOEHE = 192

    def __init__(self, quelle="/dev/video0"):
        try:
            import cv2  # nur hier, damit der Rest ohne OpenCV laeuft
        except ImportError as fehler:
            raise WaermebildFehler(
                "OpenCV fehlt - 'sudo apt install python3-opencv' oder "
                "WAERMEBILD_TYP=simulation setzen") from fehler
        self._cv2 = cv2
        self._quelle = cv2.VideoCapture(quelle, cv2.CAP_V4L2)
        if not self._quelle.isOpened():
            raise WaermebildFehler("Waermebildkamera %s nicht gefunden" % quelle)
        # Rohdaten anfordern - sonst wandelt der Treiber nach BGR um und die
        # Temperaturhaelfte waere zerstoert.
        self._quelle.set(cv2.CAP_PROP_CONVERT_RGB, 0)

    def lies(self):
        erfolg, rahmen = self._quelle.read()
        if not erfolg:
            raise WaermebildFehler("Kein Bild von der Waermebildkamera")
        roh = rahmen.reshape(-1)
        # Untere Bildhaelfte = Temperaturdaten, zwei Bytes je Pixel.
        anzahl = self.BREITE * self.HOEHE
        start = anzahl * 2
        werte = [0.0] * anzahl
        for i in range(anzahl):
            niedrig = int(roh[start + i * 2])
            hoch = int(roh[start + i * 2 + 1])
            werte[i] = ((hoch << 8) | niedrig) / 64.0 - 273.15
        return Waermerahmen(self.BREITE, self.HOEHE, werte)

    def schliessen(self):
        self._quelle.release()


# ---------------------------------------------------------------------------
# MLX90640 (I2C, 32x24) - die guenstige Rueckfallebene
# ---------------------------------------------------------------------------

class MLX90640:
    """32x24-Sensor am I2C-Bus. Braucht die Adafruit-Bibliothek."""

    BREITE = 32
    HOEHE = 24

    def __init__(self):
        try:
            import board
            import adafruit_mlx90640
        except ImportError as fehler:
            raise WaermebildFehler(
                "adafruit-circuitpython-mlx90640 fehlt") from fehler
        self._sensor = adafruit_mlx90640.MLX90640(board.I2C())
        self._sensor.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_8_HZ
        self._puffer = [0.0] * (self.BREITE * self.HOEHE)

    def lies(self):
        self._sensor.getFrame(self._puffer)
        return Waermerahmen(self.BREITE, self.HOEHE, list(self._puffer))

    def schliessen(self):
        pass


# ---------------------------------------------------------------------------
# Simulation eines Suchflugs
# ---------------------------------------------------------------------------

class SimulierterSuchflug:
    """Erzeugt ein glaubwuerdiges Waermebild eines naechtlichen Suchflugs.

    Die Szene enthaelt absichtlich mehr als nur die gesuchte Person, damit die
    Erkennung beweisen muss, dass sie die Stoerer aussortiert:

    * kalte Wiese als Untergrund, mit Rauschen
    * ein Feldweg, den die Sonne tagsueber aufgeheizt hat (langer Streifen)
    * ein aufgewaermter Steinhaufen (zu klein)
    * ein abgestelltes Auto mit warmer Motorhaube (viel zu heiss)
    * ein Reh (menschenaehnlich - die ehrliche Schwaeche des Verfahrens)
    * die gesuchte Person

    Ueber die Schalter lassen sich alle Objekte einzeln ein- und ausblenden.
    """

    BREITE = 256
    HOEHE = 192

    def __init__(self, bodentemperatur=8.0, saat=1):
        self.bodentemperatur = bodentemperatur
        self.person_sichtbar = True
        self.reh_sichtbar = False
        self.weg_sichtbar = True
        self.auto_sichtbar = True
        self.steine_sichtbar = True
        # Wie stark hebt sich die Person ab? Nachts auf kalter Wiese sind
        # 6 bis 9 Kelvin realistisch, bei Tageswaerme deutlich weniger.
        self.person_abhebung_k = 7.0
        self._zufall = random.Random(saat)
        self._start = time.time()

    def lies(self):
        t = time.time() - self._start
        b, h = self.BREITE, self.HOEHE
        grund = self.bodentemperatur
        werte = [0.0] * (b * h)
        for i in range(b * h):
            werte[i] = grund + self._zufall.uniform(-0.45, 0.45)

        # Die Drohne fliegt: alles wandert langsam durchs Bild.
        versatz = int((t * 9) % (h + 120)) - 60

        if self.weg_sichtbar:
            # Feldweg quer durchs Bild, tagsueber aufgeheizt.
            self._streifen(werte, 40 + int(6 * math.sin(t * 0.2)), 9, grund + 3.4)

        if self.steine_sichtbar:
            self._ellipse(werte, 205, (150 - versatz) % h, 3, 3, grund + 4.0)

        if self.auto_sichtbar:
            # Motorhaube: klein, aber viel zu heiss fuer einen Koerper.
            self._ellipse(werte, 60, (30 + versatz) % h, 7, 5, grund + 26.0)

        if self.reh_sichtbar:
            self._koerper(werte, 96, (120 - versatz) % h, 5, 9, grund + 6.2)

        if self.person_sichtbar:
            # Liegende Person, quer zur Flugrichtung.
            mx = 150 + int(4 * math.sin(t * 0.5))
            my = (90 + versatz) % h
            self._koerper(werte, mx, my, 4, 12, grund + self.person_abhebung_k)

        return Waermerahmen(b, h, werte)

    def _streifen(self, werte, x_mitte, halbbreite, temperatur):
        for y in range(self.HOEHE):
            zeile = y * self.BREITE
            versatz = int(18 * math.sin(y / 30.0))
            for x in range(max(0, x_mitte + versatz - halbbreite),
                           min(self.BREITE, x_mitte + versatz + halbbreite)):
                werte[zeile + x] = temperatur + self._zufall.uniform(-0.4, 0.4)

    def _ellipse(self, werte, mx, my, halbbreite, halbhoehe, temperatur):
        for y in range(max(0, my - halbhoehe), min(self.HOEHE, my + halbhoehe + 1)):
            zeile = y * self.BREITE
            dy = (y - my) / float(halbhoehe)
            for x in range(max(0, mx - halbbreite), min(self.BREITE, mx + halbbreite + 1)):
                dx = (x - mx) / float(halbbreite)
                if dx * dx + dy * dy <= 1.0:
                    werte[zeile + x] = temperatur + self._zufall.uniform(-0.3, 0.3)

    def _koerper(self, werte, mx, my, halbbreite, halbhoehe, temperatur):
        """Ein Koerper ist in der Mitte am waermsten und zum Rand hin kuehler."""
        for y in range(max(0, my - halbhoehe), min(self.HOEHE, my + halbhoehe + 1)):
            zeile = y * self.BREITE
            dy = (y - my) / float(halbhoehe)
            for x in range(max(0, mx - halbbreite), min(self.BREITE, mx + halbbreite + 1)):
                dx = (x - mx) / float(halbbreite)
                abstand = dx * dx + dy * dy
                if abstand <= 1.0:
                    anteil = 1.0 - 0.4 * abstand
                    werte[zeile + x] = (temperatur * anteil
                                        + self.bodentemperatur * (1 - anteil)
                                        + self._zufall.uniform(-0.2, 0.2))

    def schliessen(self):
        pass


def erzeuge(typ, quelle):
    """Baut die passende Kamera. ``simulation`` laeuft ohne jede Hardware."""
    if typ == "infiray":
        return InfiRayP2Pro(quelle)
    if typ == "mlx90640":
        return MLX90640()
    return SimulierterSuchflug()
