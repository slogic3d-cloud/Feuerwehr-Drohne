"""Trefferverwaltung.

Ein einzelner Takt mit hohem Vertrauen ist noch kein Fund - Bildrauschen,
ein Ruckeln der Drohne oder ein kurz angeschnittener Warmbereich erzeugen
Ausschlaege. Erst wenn der Verdacht ueber eine Haltezeit bestehen bleibt,
wird er zum Treffer. Umgekehrt soll dieselbe Person nicht zwanzigmal in der
Liste stehen: liegen zwei Treffer naeher beieinander als die eingestellte
Zusammenfassungsstrecke, gelten sie als dieselbe Fundstelle.

Gespeichert wird jeder Treffer zweifach: als JSON mit allen Messwerten und
als PGM-Bild des Waermebilds. PGM, weil es sich ohne jede Zusatzbibliothek
schreiben laesst und von jedem Bildbetrachter geoeffnet wird.
"""

import json
import os
import time

import suchflug


class Treffer:
    def __init__(self, nummer, lagebild):
        self.nummer = nummer
        self.zeit = lagebild.zeit
        self.vertrauen = lagebild.vertrauen
        self.stufe = lagebild.stufe
        self.begruendung = list(lagebild.begruendung)
        self.position = lagebild.position          # Standort der Drohne
        self.fundort = None                        # gerechneter Ort am Boden
        self.hoehe_m = lagebild.hoehe_m
        fleck = lagebild.bester_fleck
        self.fundort = fleck.koordinate if fleck else None
        self.abhebung_k = fleck.abhebung_k if fleck else None
        self.temperatur = fleck.temperatur_max if fleck else None
        self.dateiname = None
        self.bestaetigt = False
        self.verworfen = False

    def anheben(self, lagebild):
        """Uebernimmt ein besseres Lagebild in einen bestehenden Treffer."""
        if lagebild.vertrauen <= self.vertrauen:
            return False
        self.vertrauen = lagebild.vertrauen
        self.stufe = lagebild.stufe
        self.begruendung = list(lagebild.begruendung)
        if lagebild.position:
            self.position = lagebild.position
        if lagebild.bester_fleck:
            self.fundort = lagebild.bester_fleck.koordinate or self.fundort
            self.abhebung_k = lagebild.bester_fleck.abhebung_k
            self.temperatur = lagebild.bester_fleck.temperatur_max
        return True

    def als_dict(self):
        return {
            "nummer": self.nummer,
            "zeit": self.zeit,
            "uhrzeit": time.strftime("%H:%M:%S", time.localtime(self.zeit)),
            "vertrauen": round(self.vertrauen, 2),
            "stufe": self.stufe,
            "begruendung": self.begruendung,
            "position": self.position.als_dict() if self.position else None,
            "fundort": ({"breite": round(self.fundort[0], 6),
                         "laenge": round(self.fundort[1], 6)}
                        if self.fundort else None),
            "hoehe_m": round(self.hoehe_m, 1),
            "abhebung_k": round(self.abhebung_k, 1) if self.abhebung_k else None,
            "temperatur": round(self.temperatur, 1) if self.temperatur else None,
            "datei": self.dateiname,
            "bestaetigt": self.bestaetigt,
            "verworfen": self.verworfen,
        }


def pgm_schreiben(pfad, gitter):
    """Schreibt das Waermebild als Graustufenbild (PGM, Binaerformat P5)."""
    kalt, heiss, _ = gitter.kennwerte()
    spanne = max(0.1, heiss - kalt)
    zeilen = bytearray()
    for wert in gitter.werte:
        zeilen.append(min(255, max(0, int((wert - kalt) / spanne * 255))))
    with open(pfad, "wb") as datei:
        datei.write(b"P5\n# Waermebild, %.1f bis %.1f Grad Celsius\n%d %d\n255\n"
                    % (kalt, heiss, gitter.breite, gitter.hoehe))
        datei.write(bytes(zeilen))


class Trefferverwaltung:
    def __init__(self, konfig):
        self.konfig = konfig
        self.treffer = []
        self._verdacht_seit = None
        self._letzter = None
        self._naechste_nummer = 1
        os.makedirs(konfig.TREFFER_ORDNER, exist_ok=True)

    def takt(self, lagebild):
        """Verarbeitet ein Lagebild. Gibt einen neuen Treffer zurueck oder None."""
        jetzt = lagebild.zeit

        if lagebild.vertrauen < self.konfig.TREFFER_SCHWELLE:
            self._verdacht_seit = None
            return None

        if self._verdacht_seit is None:
            self._verdacht_seit = jetzt
            return None
        if jetzt - self._verdacht_seit < self.konfig.TREFFER_HALTEZEIT_S:
            return None

        # Verdacht haelt lange genug an - jetzt ist es ein Treffer.
        vorheriger = self._gleiche_fundstelle(lagebild, jetzt)
        if vorheriger is not None:
            if vorheriger.anheben(lagebild):
                self._speichern(vorheriger, lagebild)
            return None

        treffer = Treffer(self._naechste_nummer, lagebild)
        self._naechste_nummer += 1
        self.treffer.append(treffer)
        self._letzter = treffer
        self._speichern(treffer, lagebild)
        return treffer

    def _gleiche_fundstelle(self, lagebild, jetzt):
        """Gehoert dieser Verdacht zu einem Treffer, den es schon gibt?

        Mit GPS entscheidet der Abstand am Boden, ohne GPS die Zeit seit dem
        letzten Treffer. So erzeugt ein Ueberflug ueber dieselbe Person einen
        Eintrag statt dreissig.
        """
        neuer_ort = (lagebild.bester_fleck.koordinate
                     if lagebild.bester_fleck else None)
        if neuer_ort is not None:
            for treffer in reversed(self.treffer):
                if treffer.fundort is None:
                    continue
                if (suchflug.abstand_m(treffer.fundort, neuer_ort)
                        <= self.konfig.TREFFER_ZUSAMMENFASSEN_M):
                    return treffer
            return None
        if (self._letzter is not None
                and jetzt - self._letzter.zeit < self.konfig.TREFFER_ZUSAMMENFASSEN_S):
            return self._letzter
        return None

    def _speichern(self, treffer, lagebild):
        stempel = time.strftime("%Y%m%d-%H%M%S", time.localtime(treffer.zeit))
        name = "treffer-%03d-%s" % (treffer.nummer, stempel)
        treffer.dateiname = name
        ordner = self.konfig.TREFFER_ORDNER
        try:
            pgm_schreiben(os.path.join(ordner, name + ".pgm"), lagebild.gitter)
            with open(os.path.join(ordner, name + ".json"), "w") as datei:
                json.dump({
                    "treffer": treffer.als_dict(),
                    # Die Merkmale stehen bewusst obenauf: aus ihnen und der
                    # spaeteren Bewertung am Tablet lernt das Modell.
                    "merkmale": (lagebild.bester_fleck.merkmale
                                 if lagebild.bester_fleck else None),
                    "lagebild": lagebild.als_dict(mit_bild=True),
                }, datei, indent=1, ensure_ascii=False)
        except OSError as fehler:
            # Ein voller oder fehlender Datentraeger darf den Flug nicht stoppen.
            print("Treffer konnte nicht gespeichert werden: %s" % fehler)

    def liste(self):
        return [t.als_dict() for t in reversed(self.treffer)]

    def bewerten(self, nummer, bestaetigt=None, verworfen=None):
        """Der Mensch am Tablet entscheidet: Person, oder doch nur ein Reh?

        Die Entscheidung wandert zurueck in die gespeicherte Datei - genau
        daraus lernt spaeter das Modell (siehe lernen.py).
        """
        for t in self.treffer:
            if t.nummer == nummer:
                if bestaetigt is not None:
                    t.bestaetigt = bool(bestaetigt)
                    if t.bestaetigt:
                        t.verworfen = False
                if verworfen is not None:
                    t.verworfen = bool(verworfen)
                    if t.verworfen:
                        t.bestaetigt = False
                self._bewertung_nachtragen(t)
                return True
        return False

    def _bewertung_nachtragen(self, treffer):
        """Schreibt die Bewertung in die bereits gespeicherte Trefferdatei."""
        if not treffer.dateiname:
            return
        pfad = os.path.join(self.konfig.TREFFER_ORDNER, treffer.dateiname + ".json")
        try:
            with open(pfad) as datei:
                inhalt = json.load(datei)
            inhalt["treffer"] = treffer.als_dict()
            with open(pfad, "w") as datei:
                json.dump(inhalt, datei, indent=1, ensure_ascii=False)
        except (OSError, ValueError) as fehler:
            print("Bewertung konnte nicht gespeichert werden: %s" % fehler)
