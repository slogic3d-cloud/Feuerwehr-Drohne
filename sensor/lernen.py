"""Lernender Klassifikator - die "KI" des Suchkopfs.

Was hier **nicht** steht: ein neuronales Netz. Auf einem Raspberry Pi Zero 2 W
laeuft kein Bilderkennungsnetz in Echtzeit, und ein Netz, das Reh von Mensch
im Waermebild trennt, braeuchte Tausende beschrifteter Aufnahmen, die es fuer
diesen Zweck nicht frei gibt.

Was stattdessen hier steht, ist das, was tatsaechlich funktioniert und mit
jedem Einsatz besser wird: eine **logistische Regression** ueber die Merkmale,
die die Regelauswertung ohnehin berechnet. Trainiert wird sie mit genau den
Klicks, die der Bediener am Tablet macht - "Person" oder "Fehlalarm". Nach ein
paar Uebungsfluegen ueber bekannte Ziele kennt das Modell die oertlichen
Verhaeltnisse besser als jede von Hand gesetzte Schwelle.

Das Modell ist absichtlich klein und nachvollziehbar: acht Gewichte, die man
sich ansehen kann. Es ersetzt die Regelauswertung nicht, sondern wird mit ihr
gemischt - und zwar umso staerker, je mehr Beispiele es gesehen hat. Mit drei
Beispielen entscheidet weiter die Regel.
"""

import glob
import json
import math
import os
import sys

# Reihenfolge ist Teil des Dateiformats - neue Merkmale nur hinten anhaengen.
MERKMALE = (
    "abhebung_k",          # wie deutlich hebt sich der Fleck vom Boden ab
    "groessenverhaeltnis", # gemessene zu erwarteter Groesse (logarithmisch)
    "seitenverhaeltnis",   # lang und duenn oder kompakt
    "fuellung",            # wie gut fuellt der Fleck sein Rechteck
    "spitzigkeit",         # Unterschied zwischen Spitzen- und Mittelwert
    "bestaendigkeit",      # ueber wie viele Bilder gehalten
    "hintergrund_c",       # Bodentemperatur - trennt Nacht- von Tagfluegen
    "hoehe_m",             # Flughoehe
)

STANDARDDATEI = "modell.json"

# Ab dieser Zahl von Beispielen bekommt das Modell sein volles Gewicht.
VOLLES_GEWICHT_AB = 60
HOECHSTGEWICHT = 0.6


def merkmale(fleck, hintergrund_c, hoehe_m, erwartete_zellen, bestaendigkeit=0.0):
    """Rechnet einen Fleck in den Merkmalsvektor um."""
    zellen = len(fleck.zellen)
    laengs = max(fleck.breite, fleck.hoehe)
    quer = max(1, min(fleck.breite, fleck.hoehe))
    return {
        "abhebung_k": fleck.abhebung_k,
        "groessenverhaeltnis": math.log(max(0.05, zellen / max(1.0, erwartete_zellen))),
        "seitenverhaeltnis": laengs / float(quer),
        "fuellung": zellen / float(fleck.breite * fleck.hoehe),
        "spitzigkeit": fleck.temperatur_max - fleck.temperatur_mittel,
        "bestaendigkeit": bestaendigkeit,
        "hintergrund_c": hintergrund_c,
        "hoehe_m": hoehe_m,
    }


def als_liste(werte):
    return [float(werte.get(name, 0.0)) for name in MERKMALE]


class Modell:
    """Logistische Regression mit Standardisierung der Eingangswerte."""

    def __init__(self, gewichte=None, achsenabschnitt=0.0, mittel=None,
                 streuung=None, beispiele=0):
        anzahl = len(MERKMALE)
        self.gewichte = gewichte or [0.0] * anzahl
        self.achsenabschnitt = achsenabschnitt
        self.mittel = mittel or [0.0] * anzahl
        self.streuung = streuung or [1.0] * anzahl
        self.beispiele = beispiele

    # -- Anwenden --------------------------------------------------------
    def _standardisieren(self, vektor):
        return [(v - m) / (s if s > 1e-9 else 1.0)
                for v, m, s in zip(vektor, self.mittel, self.streuung)]

    def wahrscheinlichkeit(self, werte):
        """Gibt die geschaetzte Wahrscheinlichkeit zurueck, dass es ein Mensch ist."""
        x = self._standardisieren(als_liste(werte))
        z = self.achsenabschnitt + sum(g * xi for g, xi in zip(self.gewichte, x))
        # Ueberlauf vermeiden, sonst wirft exp bei grossen Werten.
        if z < -35:
            return 0.0
        if z > 35:
            return 1.0
        return 1.0 / (1.0 + math.exp(-z))

    def gewicht(self):
        """Wie stark darf das Modell mitreden? Waechst mit der Zahl der Beispiele."""
        if self.beispiele <= 0:
            return 0.0
        return HOECHSTGEWICHT * min(1.0, self.beispiele / float(VOLLES_GEWICHT_AB))

    def mischen(self, regelwert, werte):
        """Mischt Regelauswertung und Modell."""
        g = self.gewicht()
        if g <= 0.0:
            return regelwert
        return (1.0 - g) * regelwert + g * self.wahrscheinlichkeit(werte)

    def erklaerung(self, werte):
        """Welche Merkmale sprechen am staerksten fuer oder gegen einen Menschen?"""
        x = self._standardisieren(als_liste(werte))
        anteile = [(MERKMALE[i], self.gewichte[i] * x[i]) for i in range(len(MERKMALE))]
        anteile.sort(key=lambda p: abs(p[1]), reverse=True)
        return anteile[:3]

    # -- Speichern -------------------------------------------------------
    def als_dict(self):
        return {
            "merkmale": list(MERKMALE),
            "gewichte": [round(g, 5) for g in self.gewichte],
            "achsenabschnitt": round(self.achsenabschnitt, 5),
            "mittel": [round(m, 5) for m in self.mittel],
            "streuung": [round(s, 5) for s in self.streuung],
            "beispiele": self.beispiele,
        }

    def speichern(self, pfad=STANDARDDATEI):
        with open(pfad, "w") as datei:
            json.dump(self.als_dict(), datei, indent=1)

    @staticmethod
    def laden(pfad=STANDARDDATEI):
        """Laedt ein Modell. Gibt ``None``, wenn keins da oder es unpassend ist."""
        try:
            with open(pfad) as datei:
                d = json.load(datei)
        except (OSError, ValueError):
            return None
        if d.get("merkmale") != list(MERKMALE):
            # Merkmalssatz hat sich geaendert - altes Modell waere falsch.
            print("Modell passt nicht mehr zum Merkmalssatz, wird ignoriert.")
            return None
        return Modell(d.get("gewichte"), d.get("achsenabschnitt", 0.0),
                      d.get("mittel"), d.get("streuung"), d.get("beispiele", 0))


def trainieren(beispiele, durchlaeufe=400, lernrate=0.25, straf=0.01):
    """Trainiert ein Modell.

    ``beispiele`` ist eine Liste von ``(merkmale, ist_person)``.
    Gewichtsverfall (``straf``) haelt die Gewichte klein, damit das Modell bei
    wenigen Beispielen nicht ueberdreht.
    """
    if not beispiele:
        return None
    anzahl = len(MERKMALE)
    matrix = [als_liste(m) for m, _ in beispiele]
    ziele = [1.0 if z else 0.0 for _, z in beispiele]

    # Standardisieren: sonst dominiert die Flughoehe alle anderen Merkmale.
    mittel, streuung = [], []
    for i in range(anzahl):
        spalte = [zeile[i] for zeile in matrix]
        m = sum(spalte) / len(spalte)
        s = math.sqrt(sum((w - m) ** 2 for w in spalte) / len(spalte)) or 1.0
        mittel.append(m)
        streuung.append(s)
    x = [[(zeile[i] - mittel[i]) / streuung[i] for i in range(anzahl)]
         for zeile in matrix]

    gewichte = [0.0] * anzahl
    abschnitt = 0.0
    n = float(len(x))

    for _ in range(durchlaeufe):
        gradient = [0.0] * anzahl
        gradient_abschnitt = 0.0
        for zeile, ziel in zip(x, ziele):
            z = abschnitt + sum(g * xi for g, xi in zip(gewichte, zeile))
            z = max(-35.0, min(35.0, z))
            fehler = 1.0 / (1.0 + math.exp(-z)) - ziel
            for i in range(anzahl):
                gradient[i] += fehler * zeile[i]
            gradient_abschnitt += fehler
        for i in range(anzahl):
            gewichte[i] -= lernrate * (gradient[i] / n + straf * gewichte[i])
        abschnitt -= lernrate * (gradient_abschnitt / n)

    return Modell(gewichte, abschnitt, mittel, streuung, len(beispiele))


def beispiele_aus_ordner(ordner):
    """Liest alle bewerteten Treffer eines Ordners als Trainingsbeispiele.

    Nur Treffer, die am Tablet ausdruecklich als "Person" oder "Fehlalarm"
    markiert wurden, zaehlen. Unbewertete bleiben aussen vor - eine Vermutung
    als Wahrheit zu trainieren waere schlimmer als gar nicht zu trainieren.
    """
    beispiele = []
    for pfad in sorted(glob.glob(os.path.join(ordner, "*.json"))):
        try:
            with open(pfad) as datei:
                d = json.load(datei)
        except (OSError, ValueError):
            continue
        treffer = d.get("treffer", {})
        werte = d.get("merkmale")
        if not werte:
            continue
        if treffer.get("bestaetigt"):
            beispiele.append((werte, True))
        elif treffer.get("verworfen"):
            beispiele.append((werte, False))
    return beispiele


def bericht(modell, beispiele):
    """Wie gut trifft das Modell auf den eigenen Trainingsdaten?"""
    if not beispiele:
        return {}
    richtig = 0
    for werte, ziel in beispiele:
        geschaetzt = modell.wahrscheinlichkeit(werte) >= 0.5
        if geschaetzt == bool(ziel):
            richtig += 1
    return {
        "beispiele": len(beispiele),
        "personen": sum(1 for _, z in beispiele if z),
        "fehlalarme": sum(1 for _, z in beispiele if not z),
        "trefferquote": round(richtig / float(len(beispiele)), 3),
        "gewicht_im_betrieb": round(modell.gewicht(), 2),
    }


def main(argumente=None):
    argumente = argumente if argumente is not None else sys.argv[1:]
    ordner = argumente[0] if argumente else "treffer"
    ziel = argumente[1] if len(argumente) > 1 else STANDARDDATEI

    beispiele = beispiele_aus_ordner(ordner)
    if len(beispiele) < 6:
        print("Zu wenige bewertete Treffer in '%s' (%d gefunden, mindestens 6 noetig)."
              % (ordner, len(beispiele)))
        print("Am Tablet Fundstellen als 'Person' oder 'Fehlalarm' markieren,")
        print("dann noch einmal trainieren.")
        return 1

    modell = trainieren(beispiele)
    modell.speichern(ziel)
    print("Modell aus %d Beispielen trainiert und in '%s' gespeichert." % (len(beispiele), ziel))
    for name, wert in bericht(modell, beispiele).items():
        print("  %-20s %s" % (name, wert))
    print("\n  Gewichte (positiv spricht fuer 'Person'):")
    for name, gewicht in sorted(zip(MERKMALE, modell.gewichte),
                                key=lambda p: abs(p[1]), reverse=True):
        print("    %-22s %+.3f" % (name, gewicht))
    return 0


if __name__ == "__main__":
    sys.exit(main())
