"""Tests des lernenden Klassifikators."""

import random
import tempfile
import unittest

import pfad  # noqa: F401
import lernen


def beispiel(person, zufall):
    """Erzeugt ein kuenstliches Beispiel: Menschen heben sich staerker ab
    und sind kompakter als die typischen Fehlalarme."""
    if person:
        return {"abhebung_k": zufall.gauss(6.0, 1.0),
                "groessenverhaeltnis": zufall.gauss(0.0, 0.3),
                "seitenverhaeltnis": zufall.gauss(2.6, 0.5),
                "fuellung": zufall.gauss(0.70, 0.10),
                "spitzigkeit": zufall.gauss(1.8, 0.4),
                "bestaendigkeit": zufall.gauss(0.9, 0.1),
                "hintergrund_c": 8.0, "hoehe_m": 40.0}
    return {"abhebung_k": zufall.gauss(3.6, 1.2),
            "groessenverhaeltnis": zufall.gauss(-1.2, 0.9),
            "seitenverhaeltnis": zufall.gauss(4.6, 1.6),
            "fuellung": zufall.gauss(0.50, 0.20),
            "spitzigkeit": zufall.gauss(3.4, 1.2),
            "bestaendigkeit": zufall.gauss(0.4, 0.25),
            "hintergrund_c": 8.0, "hoehe_m": 40.0}


def datensatz(anzahl, saat=7):
    zufall = random.Random(saat)
    daten = [(beispiel(True, zufall), True) for _ in range(anzahl // 2)]
    daten += [(beispiel(False, zufall), False) for _ in range(anzahl // 2)]
    zufall.shuffle(daten)
    return daten


class TestTraining(unittest.TestCase):

    def test_trennt_die_beiden_gruppen(self):
        daten = datensatz(80)
        modell = lernen.trainieren(daten[:60])
        ergebnis = lernen.bericht(modell, daten[60:])
        self.assertGreater(ergebnis["trefferquote"], 0.85,
                           "auf ungesehenen Daten muss das Modell taugen")

    def test_ohne_beispiele_kein_modell(self):
        self.assertIsNone(lernen.trainieren([]))

    def test_gewichte_zeigen_in_die_richtige_richtung(self):
        modell = lernen.trainieren(datensatz(80))
        gewichte = dict(zip(lernen.MERKMALE, modell.gewichte))
        # Staerkere Abhebung spricht fuer einen Menschen ...
        self.assertGreater(gewichte["abhebung_k"], 0)
        # ... ein langgestreckter Fleck dagegen.
        self.assertLess(gewichte["seitenverhaeltnis"], 0)


class TestModell(unittest.TestCase):

    def test_wahrscheinlichkeit_bleibt_im_bereich(self):
        modell = lernen.trainieren(datensatz(40))
        zufall = random.Random(1)
        for _ in range(20):
            wert = modell.wahrscheinlichkeit(beispiel(zufall.random() > 0.5, zufall))
            self.assertGreaterEqual(wert, 0.0)
            self.assertLessEqual(wert, 1.0)

    def test_extremwerte_lassen_nichts_ueberlaufen(self):
        modell = lernen.Modell([1e6] * len(lernen.MERKMALE), 0.0,
                               [0.0] * len(lernen.MERKMALE),
                               [1.0] * len(lernen.MERKMALE), 10)
        werte = {name: 1e6 for name in lernen.MERKMALE}
        self.assertEqual(modell.wahrscheinlichkeit(werte), 1.0)
        werte = {name: -1e6 for name in lernen.MERKMALE}
        self.assertEqual(modell.wahrscheinlichkeit(werte), 0.0)

    def test_gewicht_waechst_mit_der_zahl_der_beispiele(self):
        wenig = lernen.trainieren(datensatz(10))
        viel = lernen.trainieren(datensatz(120))
        self.assertLess(wenig.gewicht(), viel.gewicht())
        self.assertLessEqual(viel.gewicht(), lernen.HOECHSTGEWICHT)

    def test_ohne_beispiele_entscheidet_allein_die_regel(self):
        leer = lernen.Modell()
        self.assertEqual(leer.gewicht(), 0.0)
        self.assertEqual(leer.mischen(0.42, {}), 0.42)

    def test_mischung_liegt_zwischen_regel_und_modell(self):
        modell = lernen.trainieren(datensatz(120))
        zufall = random.Random(3)
        werte = beispiel(True, zufall)
        regel = 0.30
        gemischt = modell.mischen(regel, werte)
        modellwert = modell.wahrscheinlichkeit(werte)
        self.assertGreaterEqual(gemischt, min(regel, modellwert) - 1e-9)
        self.assertLessEqual(gemischt, max(regel, modellwert) + 1e-9)

    def test_speichern_und_laden(self):
        modell = lernen.trainieren(datensatz(40))
        zufall = random.Random(5)
        werte = beispiel(True, zufall)
        with tempfile.NamedTemporaryFile(suffix=".json") as datei:
            modell.speichern(datei.name)
            geladen = lernen.Modell.laden(datei.name)
        self.assertIsNotNone(geladen)
        self.assertEqual(geladen.beispiele, modell.beispiele)
        self.assertAlmostEqual(geladen.wahrscheinlichkeit(werte),
                               modell.wahrscheinlichkeit(werte), places=4)

    def test_fehlende_datei_gibt_kein_modell(self):
        self.assertIsNone(lernen.Modell.laden("/gibt/es/nicht.json"))

    def test_erklaerung_nennt_die_staerksten_merkmale(self):
        modell = lernen.trainieren(datensatz(80))
        oben = modell.erklaerung(beispiel(True, random.Random(2)))
        self.assertEqual(len(oben), 3)
        for name, _ in oben:
            self.assertIn(name, lernen.MERKMALE)


if __name__ == "__main__":
    unittest.main()
