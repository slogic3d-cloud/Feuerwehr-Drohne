"""Personenerkennung im Waermebild aus der Luft.

Aus 40 m Hoehe ist ein Mensch kein warmer 33-Grad-Koerper mehr, sondern ein
kleiner Fleck, der sich um wenige Kelvin vom Boden abhebt: Luft daempft, und
jeder Bildpunkt mischt Person und Untergrund. Absolute Temperaturschwellen
funktionieren hier nicht - bewertet wird der **Kontrast zum Untergrund**.

Drei Merkmale entscheiden:

* **Abhebung** - wie deutlich hebt sich der Fleck vom Boden ab? Zu wenig ist
  ein warmer Stein, zu viel ist Technik oder Feuer.
* **Groesse** - aus der Flughoehe laesst sich ausrechnen, wie viele Bildpunkte
  eine liegende Person haben *muss*. Alles deutlich Groessere ist Strasse,
  Dach oder ein Feld in der Abendsonne.
* **Form** - ein Mensch ist ein kompakter Klumpen. Lange duenne Streifen sind
  Wege, Mauern und Leitplanken, die die Sonne aufgeheizt hat.

Ehrlich dazugesagt: **Rehe, Wildschweine und Hunde erfuellen alle drei
Merkmale ebenfalls.** Die Software kann sie nicht sicher von Menschen
unterscheiden - das muss der Mensch am Tablet anhand des Bildes tun. Deshalb
traegt jeder Treffer seine Begruendung mit und wird mit Bild gespeichert.
"""

import math

import lernen
import suchflug


class Fleck:
    """Ein zusammenhaengender Bereich, der sich vom Untergrund abhebt."""

    __slots__ = ("zellen", "x0", "y0", "x1", "y1", "temperatur_mittel",
                 "temperatur_max", "abhebung_k", "anteil", "vertrauen",
                 "regelwert", "begruendung", "koordinate", "merkmale",
                 "bestaendigkeit")

    def __init__(self, zellen, x0, y0, x1, y1, mittel, hoechst, abhebung, anteil):
        self.zellen = zellen
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.temperatur_mittel = mittel
        self.temperatur_max = hoechst
        self.abhebung_k = abhebung
        self.anteil = anteil
        self.vertrauen = 0.0
        self.regelwert = 0.0          # Bewertung allein nach Regeln
        self.begruendung = []
        self.koordinate = None
        self.merkmale = None          # Eingangswerte fuer das lernende Modell
        self.bestaendigkeit = 0.0     # ueber wie viele Bilder gehalten

    @property
    def breite(self):
        return self.x1 - self.x0 + 1

    @property
    def hoehe(self):
        return self.y1 - self.y0 + 1

    @property
    def mitte(self):
        return ((self.x0 + self.x1) / 2.0, (self.y0 + self.y1) / 2.0)

    def als_dict(self):
        mx, my = self.mitte
        d = {
            "x0": self.x0, "y0": self.y0, "x1": self.x1, "y1": self.y1,
            "mitte_x": round(mx, 1), "mitte_y": round(my, 1),
            "zellen": len(self.zellen),
            "temperatur_max": round(self.temperatur_max, 1),
            "abhebung_k": round(self.abhebung_k, 1),
            "vertrauen": round(self.vertrauen, 2),
            "regelwert": round(self.regelwert, 2),
            "bestaendigkeit": round(self.bestaendigkeit, 2),
            "begruendung": self.begruendung,
        }
        if self.koordinate:
            d["breite_grad"] = round(self.koordinate[0], 6)
            d["laenge_grad"] = round(self.koordinate[1], 6)
        return d


def perzentil(sortiert, anteil):
    """Wert an der gegebenen Stelle einer bereits sortierten Liste."""
    if not sortiert:
        return 0.0
    i = int(anteil * (len(sortiert) - 1))
    return sortiert[max(0, min(len(sortiert) - 1, i))]


def spanne_fuer_anzeige(werte, unten=0.02, oben=0.995, mindestspanne=3.0):
    """Robuste Farbspanne fuers Waermebild.

    Die untersten und obersten Ausreisser werden abgeschnitten. Zusaetzlich
    wird eine Mindestspanne eingehalten, damit ein voellig gleichmaessiges
    Bild nicht zu wildem Rauschen aufgeblasen wird.
    """
    sortiert = sorted(werte)
    kalt = perzentil(sortiert, unten)
    heiss = perzentil(sortiert, oben)
    if heiss - kalt < mindestspanne:
        mitte = (heiss + kalt) / 2.0
        kalt, heiss = mitte - mindestspanne / 2.0, mitte + mindestspanne / 2.0
    return kalt, heiss


def median(werte):
    sortiert = sorted(werte)
    n = len(sortiert)
    if n == 0:
        return 0.0
    mitte = n // 2
    if n % 2:
        return sortiert[mitte]
    return (sortiert[mitte - 1] + sortiert[mitte]) / 2.0


def flecken_suchen(rahmen, schwelle):
    """Findet zusammenhaengende Zellen oberhalb der Schwelle (Flutfuellung)."""
    breite, hoehe = rahmen.breite, rahmen.hoehe
    werte = rahmen.werte
    gesehen = bytearray(breite * hoehe)
    gefunden = []

    for start in range(breite * hoehe):
        if gesehen[start] or werte[start] < schwelle:
            continue
        stapel = [start]
        gesehen[start] = 1
        zellen = []
        x0 = x1 = start % breite
        y0 = y1 = start // breite
        summe = 0.0
        hoechst = -999.0

        while stapel:
            i = stapel.pop()
            x, y = i % breite, i // breite
            zellen.append(i)
            summe += werte[i]
            if werte[i] > hoechst:
                hoechst = werte[i]
            if x < x0: x0 = x
            if x > x1: x1 = x
            if y < y0: y0 = y
            if y > y1: y1 = y
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < breite and 0 <= ny < hoehe:
                    j = ny * breite + nx
                    if not gesehen[j] and werte[j] >= schwelle:
                        gesehen[j] = 1
                        stapel.append(j)

        gefunden.append((zellen, x0, y0, x1, y1, summe / len(zellen), hoechst))
    return gefunden


def _abhebungsnote(abhebung, mindestens, hoechstens):
    """Wie gut passt der Temperaturunterschied zum Boden zu einem Koerper?"""
    if abhebung < mindestens:
        return 0.0
    if abhebung > hoechstens:
        # Motorhaube, Trafostation, Lagerfeuer - viel zu heiss fuer Haut.
        ueber = abhebung - hoechstens
        return max(0.0, 0.30 - ueber * 0.02)
    # Der beste Bereich liegt bei etwa dem Doppelten der Mindestabhebung:
    # deutlich sichtbar, aber nicht technisch heiss.
    ziel = mindestens * 2.5
    if abhebung <= ziel:
        return 0.55 + 0.45 * (abhebung - mindestens) / max(0.1, ziel - mindestens)
    rest = (abhebung - ziel) / max(0.1, hoechstens - ziel)
    return 1.0 - 0.35 * rest


def _groessennote(zellen, erwartet):
    """Vergleicht die gemessene Fleckgroesse mit der aus der Flughoehe erwarteten."""
    if erwartet <= 0:
        return 0.5
    verhaeltnis = zellen / float(erwartet)
    if verhaeltnis < 0.25:
        return 0.15          # zu klein: einzelner heisser Bildpunkt, Rauschen
    if verhaeltnis < 0.5:
        return 0.6
    if verhaeltnis <= 3.0:
        return 1.0           # passt zu einer Person, sitzend bis liegend
    if verhaeltnis <= 8.0:
        return 0.45          # deutlich zu gross: Tiergruppe, Auto, Mauerstueck
    return 0.1               # Strasse, Dach, besonntes Feld


def _formnote(breite, hoehe, zellen):
    """Kompakte Klumpen sind Koerper, lange Streifen sind Wege und Mauern."""
    laengs = max(breite, hoehe)
    quer = max(1, min(breite, hoehe))
    verhaeltnis = laengs / float(quer)
    if verhaeltnis > 6.0:
        return 0.15
    if verhaeltnis > 4.0:
        return 0.5
    fuellung = zellen / float(breite * hoehe)
    if fuellung < 0.35:
        return 0.6           # zerrissen: eher Bodenmuster als ein Koerper
    return 1.0


def erwartete_zellen(hoehe_m, konfig, gitter_breite):
    """Wie viele Gitterzellen sollte eine liegende Person belegen?

    Aus Flughoehe und Bildwinkel ergibt sich die Bodenaufloesung, daraus die
    Laenge in Pixeln. Als Flaeche wird eine Person mit rund einem Drittel
    ihrer Laenge als Breite angesetzt.
    """
    laenge_px = suchflug.pixel_je_person(
        hoehe_m, konfig.BILDWINKEL_QUER, gitter_breite)
    return max(1.0, laenge_px * laenge_px / 3.0)


class Lagebild:
    """Das Auswerteergebnis eines Takts."""

    def __init__(self, gitter, flecken, bester, hintergrund, hoehe_m,
                 position=None, kurs_grad=0.0, begruendung=None,
                 windlage=None, modellgewicht=0.0):
        self.gitter = gitter
        self.flecken = flecken
        self.bester_fleck = bester
        self.hintergrund_c = hintergrund
        self.hoehe_m = hoehe_m
        self.position = position
        self.kurs_grad = kurs_grad
        self.vertrauen = bester.vertrauen if bester else 0.0
        self.stufe = stufe(self.vertrauen)
        self.begruendung = begruendung or []
        self.windlage = windlage
        self.modellgewicht = modellgewicht
        self.zeit = gitter.zeit

    def als_dict(self, mit_bild=True):
        d = {
            "zeit": self.zeit,
            "vertrauen": round(self.vertrauen, 2),
            "stufe": self.stufe,
            "begruendung": self.begruendung,
            "hintergrund_c": round(self.hintergrund_c, 1),
            "hoehe_m": round(self.hoehe_m, 1),
            "kurs_grad": round(self.kurs_grad, 1),
            "flecken": [f.als_dict() for f in self.flecken[:6]],
            "position": self.position.als_dict() if self.position else None,
            "windlage": self.windlage,
            "modellgewicht": round(self.modellgewicht, 2),
        }
        if mit_bild:
            kalt, heiss, _ = self.gitter.kennwerte()
            # Fuer die Anzeige zaehlen nicht die Extremwerte, sondern die
            # Perzentile: eine heisse Motorhaube oder ein Lagerfeuer wuerde
            # sonst die ganze Farbskala stauchen und die Person, auf die es
            # ankommt, verschwaende im Dunkeln.
            anzeige_kalt, anzeige_heiss = spanne_fuer_anzeige(self.gitter.werte)
            d["bild"] = {
                "breite": self.gitter.breite,
                "hoehe": self.gitter.hoehe,
                "min": round(kalt, 1),
                "max": round(heiss, 1),
                "anzeige_min": round(anzeige_kalt, 1),
                "anzeige_max": round(anzeige_heiss, 1),
                # Zehntelgrad als ganze Zahlen: spart rund die Haelfte der
                # Bytes gegenueber Kommazahlen und reicht voellig aus.
                "werte": [int(round(w * 10)) for w in self.gitter.werte],
            }
        return d


STUFEN = (
    (0.80, "sehr wahrscheinlich"),
    (0.55, "wahrscheinlich"),
    (0.35, "moeglich"),
    (0.00, "kein Hinweis"),
)


def stufe(vertrauen):
    for grenze, name in STUFEN:
        if vertrauen >= grenze:
            return name
    return "kein Hinweis"


def auswerten(rahmen, konfig, hoehe_m=None, position=None, kurs_grad=0.0):
    """Wertet ein Waermebild aus und liefert das Lagebild."""
    gitter = rahmen.verkleinern(konfig.GITTER_BREITE, konfig.GITTER_HOEHE)
    if hoehe_m is None:
        hoehe_m = konfig.FLUGHOEHE_M

    hintergrund = median(gitter.werte)
    schwelle = hintergrund + konfig.ABHEBUNG_K
    zellen_gesamt = gitter.breite * gitter.hoehe
    soll = erwartete_zellen(hoehe_m, konfig, gitter.breite)

    flecken = []
    for zellen, x0, y0, x1, y1, mittel, hoechst in flecken_suchen(gitter, schwelle):
        anteil = len(zellen) / float(zellen_gesamt)
        if anteil > konfig.FLECK_MAX_ANTEIL:
            # Grossflaechig warm: besonntes Dach, Acker, Wasserflaeche.
            continue
        fleck = Fleck(zellen, x0, y0, x1, y1, mittel, hoechst,
                      mittel - hintergrund, anteil)

        note_a = _abhebungsnote(fleck.abhebung_k, konfig.ABHEBUNG_K,
                                konfig.ABHEBUNG_MAX_K)
        note_g = _groessennote(len(zellen), soll)
        note_f = _formnote(fleck.breite, fleck.hoehe, len(zellen))
        fleck.vertrauen = note_a * note_g * note_f
        fleck.regelwert = fleck.vertrauen

        gruende = ["%.1f K waermer als der Boden" % fleck.abhebung_k]
        if note_a < 0.4:
            gruende.append("Abhebung passt nicht zu Haut - eher Technik oder Feuer")
        if note_g >= 1.0:
            gruende.append("Groesse passt zu einer Person aus %.0f m Hoehe" % hoehe_m)
        elif note_g <= 0.2:
            gruende.append("Groesse passt nicht (%d statt rund %d Zellen)"
                           % (len(zellen), round(soll)))
        else:
            gruende.append("Groesse nur ungefaehr passend (%d statt rund %d Zellen)"
                           % (len(zellen), round(soll)))
        if note_f < 1.0:
            gruende.append("Form eher langgestreckt - moeglicherweise Weg oder Mauer")
        fleck.begruendung = gruende

        if position is not None:
            mx, my = fleck.mitte
            fleck.koordinate = suchflug.pixel_zu_koordinate(
                mx, my, gitter.breite, gitter.hoehe, hoehe_m, kurs_grad,
                (position.breite, position.laenge),
                konfig.BILDWINKEL_QUER, konfig.BILDWINKEL_HOCH)

        flecken.append(fleck)

    flecken.sort(key=lambda f: f.vertrauen, reverse=True)
    bester = flecken[0] if flecken and flecken[0].vertrauen >= 0.20 else None

    return Lagebild(gitter, flecken, bester, hintergrund, hoehe_m,
                    position, kurs_grad, begruendung_bauen(bester, flecken))


def begruendung_bauen(bester, flecken):
    """Baut die Klartextbegruendung fuer das Tablet."""
    if bester:
        gruende = list(bester.begruendung)
        gruende.append("Achtung: Wild und Haustiere sehen im Waermebild "
                       "aehnlich aus - Bild pruefen")
        return gruende
    if flecken:
        return ["%d Waermequelle(n) im Bild, aber keine passt zu einer Person"
                % len(flecken)]
    return ["Nichts, was sich vom Boden abhebt"]


def nachbewerten(lage, zuordnung, konfig, modell=None):
    """Verfeinert die Bewertung mit Fleckverfolgung und lernendem Modell.

    Zwei Dinge passieren hier:

    1. **Bestaendigkeit.** Ein Fleck, der nur in einem einzigen Bild auftaucht,
       ist bei Wind meist ein Verwackler. Je oefter derselbe Fleck ueber
       mehrere Bilder hinweg wiedergefunden wurde, desto mehr zaehlt er. Das
       wirkt auch ohne trainiertes Modell.
    2. **Modell.** Liegt ein trainiertes Modell vor, wird sein Urteil mit der
       Regelbewertung gemischt - gewichtet nach der Zahl der Beispiele, aus
       denen es gelernt hat.

    ``zuordnung`` ist die Liste aus ``Fleckverfolgung.takt``.
    """
    soll = erwartete_zellen(lage.hoehe_m, konfig, lage.gitter.breite)

    for fleck, spur in zuordnung:
        fleck.bestaendigkeit = spur.bestaendigkeit()
        fleck.merkmale = lernen.merkmale(
            fleck, lage.hintergrund_c, lage.hoehe_m, soll, fleck.bestaendigkeit)

        # Ein einmal gesehener Fleck wird gedaempft, ein oft gesehener nicht
        # angehoben - Vorsicht ist hier wichtiger als Empfindlichkeit.
        wert = fleck.regelwert * (0.55 + 0.45 * fleck.bestaendigkeit)

        if modell is not None:
            wert = modell.mischen(wert, fleck.merkmale)
        fleck.vertrauen = wert

        if fleck.bestaendigkeit < 0.5:
            fleck.begruendung = fleck.begruendung + [
                "erst in %d Bild(ern) gesehen - noch unsicher" % spur.gesehen]

    lage.flecken.sort(key=lambda f: f.vertrauen, reverse=True)
    bester = lage.flecken[0] if lage.flecken and lage.flecken[0].vertrauen >= 0.20 else None
    lage.bester_fleck = bester
    lage.vertrauen = bester.vertrauen if bester else 0.0
    lage.stufe = stufe(lage.vertrauen)
    lage.begruendung = begruendung_bauen(bester, lage.flecken)
    if modell is not None and modell.gewicht() > 0 and bester is not None:
        lage.modellgewicht = modell.gewicht()
        oben = modell.erklaerung(bester.merkmale)
        lage.begruendung.append(
            "Modell (%d Beispiele) stuetzt sich vor allem auf: %s"
            % (modell.beispiele, ", ".join(name for name, _ in oben)))
    return lage
