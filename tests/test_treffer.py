"""Tests der Trefferverwaltung."""

import json
import os
import shutil
import tempfile
import time
import unittest

import pfad  # noqa: F401
import erkennung
import konfig
from geraete.gps import Position
from geraete.waermebild import SimulierterSuchflug
from treffer import Trefferverwaltung, pgm_schreiben


class Einstellungen:
    """Eigene Einstellungen je Test, damit sich die Tests nicht stoeren."""

    def __init__(self, ordner):
        for name in dir(konfig):
            if name.isupper():
                setattr(self, name, getattr(konfig, name))
        self.TREFFER_ORDNER = ordner
        self.TREFFER_HALTEZEIT_S = 0.0
        self.TREFFER_ZUSAMMENFASSEN_M = 15.0


class TestTrefferverwaltung(unittest.TestCase):

    def setUp(self):
        self.ordner = tempfile.mkdtemp()
        self.einstellungen = Einstellungen(self.ordner)
        self.kamera = SimulierterSuchflug()

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)

    def _lage(self, person=True, position=None):
        self.kamera.person_sichtbar = person
        return erkennung.auswerten(self.kamera.lies(), konfig, hoehe_m=40,
                                   position=position)

    def test_ohne_person_kein_treffer(self):
        verwaltung = Trefferverwaltung(self.einstellungen)
        lage = self._lage(person=False)
        lage.vertrauen = 0.1
        self.assertIsNone(verwaltung.takt(lage))
        self.assertEqual(verwaltung.treffer, [])

    def test_haltezeit_muss_abgewartet_werden(self):
        self.einstellungen.TREFFER_HALTEZEIT_S = 5.0
        verwaltung = Trefferverwaltung(self.einstellungen)
        for _ in range(4):
            self.assertIsNone(verwaltung.takt(self._lage()),
                              "vor Ablauf der Haltezeit darf nichts melden")

    def test_treffer_nach_haltezeit(self):
        verwaltung = Trefferverwaltung(self.einstellungen)
        verwaltung.takt(self._lage())          # setzt den Verdacht
        treffer = verwaltung.takt(self._lage())
        self.assertIsNotNone(treffer)
        self.assertEqual(treffer.nummer, 1)

    def test_dieselbe_stelle_wird_zusammengefasst(self):
        verwaltung = Trefferverwaltung(self.einstellungen)
        ort = Position(50.2472, 11.0361, 340.0, 9)
        verwaltung.takt(self._lage(position=ort))
        erster = verwaltung.takt(self._lage(position=ort))
        self.assertIsNotNone(erster)
        for _ in range(5):
            verwaltung.takt(self._lage(position=ort))
        self.assertEqual(len(verwaltung.treffer), 1,
                         "ein Ueberflug ueber dieselbe Person ist eine Fundstelle")

    def test_weit_entfernte_stelle_wird_neu_gezaehlt(self):
        verwaltung = Trefferverwaltung(self.einstellungen)
        verwaltung.takt(self._lage(position=Position(50.2472, 11.0361)))
        verwaltung.takt(self._lage(position=Position(50.2472, 11.0361)))
        # rund 500 m weiter noerdlich
        weit = Position(50.2517, 11.0361)
        verwaltung.takt(self._lage(position=weit))
        verwaltung.takt(self._lage(position=weit))
        self.assertEqual(len(verwaltung.treffer), 2)

    def test_treffer_wird_gespeichert(self):
        verwaltung = Trefferverwaltung(self.einstellungen)
        verwaltung.takt(self._lage())
        treffer = verwaltung.takt(self._lage())
        dateien = sorted(os.listdir(self.ordner))
        self.assertEqual(len(dateien), 2, "JSON und Bild")
        self.assertTrue(any(d.endswith(".pgm") for d in dateien))
        with open(os.path.join(self.ordner, treffer.dateiname + ".json")) as datei:
            inhalt = json.load(datei)
        self.assertIn("lagebild", inhalt)
        self.assertIn("treffer", inhalt)

    def test_bewertung_landet_in_der_datei(self):
        verwaltung = Trefferverwaltung(self.einstellungen)
        verwaltung.takt(self._lage())
        treffer = verwaltung.takt(self._lage())
        self.assertTrue(verwaltung.bewerten(treffer.nummer, bestaetigt=True))
        with open(os.path.join(self.ordner, treffer.dateiname + ".json")) as datei:
            inhalt = json.load(datei)
        self.assertTrue(inhalt["treffer"]["bestaetigt"],
                        "aus dieser Bewertung lernt spaeter das Modell")

    def test_bestaetigen_und_verwerfen_schliessen_sich_aus(self):
        verwaltung = Trefferverwaltung(self.einstellungen)
        verwaltung.takt(self._lage())
        treffer = verwaltung.takt(self._lage())
        verwaltung.bewerten(treffer.nummer, bestaetigt=True)
        verwaltung.bewerten(treffer.nummer, verworfen=True)
        self.assertFalse(treffer.bestaetigt)
        self.assertTrue(treffer.verworfen)

    def test_unbekannte_nummer_wird_abgelehnt(self):
        verwaltung = Trefferverwaltung(self.einstellungen)
        self.assertFalse(verwaltung.bewerten(999, bestaetigt=True))

    def test_liste_zeigt_den_neuesten_zuerst(self):
        verwaltung = Trefferverwaltung(self.einstellungen)
        for _ in range(2):
            verwaltung.takt(self._lage(position=Position(50.2472, 11.0361)))
        for _ in range(2):
            verwaltung.takt(self._lage(position=Position(50.2600, 11.0361)))
        liste = verwaltung.liste()
        self.assertEqual(len(liste), 2)
        self.assertEqual(liste[0]["nummer"], 2)


class TestBildschreiben(unittest.TestCase):

    def test_pgm_hat_gueltigen_kopf(self):
        kamera = SimulierterSuchflug()
        gitter = kamera.lies().verkleinern(32, 24)
        pfad_datei = os.path.join(tempfile.mkdtemp(), "bild.pgm")
        pgm_schreiben(pfad_datei, gitter)
        with open(pfad_datei, "rb") as datei:
            inhalt = datei.read()
        self.assertTrue(inhalt.startswith(b"P5\n"))
        self.assertIn(b"32 24", inhalt)
        # Kopf plus ein Byte je Bildpunkt
        self.assertGreaterEqual(len(inhalt), 32 * 24)


if __name__ == "__main__":
    unittest.main()
