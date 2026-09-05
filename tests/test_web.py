"""Tests der Bodenstation-Schnittstelle."""

import json
import unittest
import urllib.error
import urllib.request

import pfad  # noqa: F401
import web


class TestZustand(unittest.TestCase):

    def test_stand_zaehlt_hoch(self):
        zustand = web.Zustand()
        self.assertEqual(zustand.lage(), (None, 0))
        zustand.melden({"vertrauen": 0.5})
        lage, stand = zustand.lage()
        self.assertEqual(stand, 1)
        self.assertEqual(lage["vertrauen"], 0.5)

    def test_warten_kehrt_bei_neuem_stand_sofort_zurueck(self):
        zustand = web.Zustand()
        zustand.melden({"a": 1})
        lage, stand = zustand.warten(0, zeitgrenze=0.1)
        self.assertEqual(stand, 1)
        self.assertEqual(lage["a"], 1)


class TestServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.zustand = web.Zustand()
        cls.zustand.suchplan = {"hoehe_m": 40.0}
        cls.zustand.melden({"vertrauen": 0.9, "stufe": "sehr wahrscheinlich"})
        # Port 0: das Betriebssystem sucht einen freien aus.
        cls.server = web.starten(cls.zustand, 0)
        cls.adresse = "http://127.0.0.1:%d" % cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def hole(self, weg):
        with urllib.request.urlopen(self.adresse + weg, timeout=5) as antwort:
            return json.loads(antwort.read().decode("utf-8"))

    def test_lage_wird_geliefert(self):
        antwort = self.hole("/lage")
        self.assertEqual(antwort["lage"]["stufe"], "sehr wahrscheinlich")
        self.assertGreaterEqual(antwort["stand"], 1)

    def test_zustand_enthaelt_suchplan(self):
        self.assertEqual(self.hole("/zustand")["suchplan"]["hoehe_m"], 40.0)

    def test_treffer_ohne_verwaltung_ist_leer(self):
        self.assertEqual(self.hole("/treffer")["treffer"], [])

    def test_seite_wird_ausgeliefert(self):
        with urllib.request.urlopen(self.adresse + "/", timeout=5) as antwort:
            inhalt = antwort.read().decode("utf-8")
        self.assertIn("Personensuche", inhalt)
        self.assertIn("text/html", antwort.headers.get("Content-Type"))

    def test_unbekannter_weg_gibt_404(self):
        with self.assertRaises(urllib.error.HTTPError) as fehler:
            urllib.request.urlopen(self.adresse + "/gibtsnicht", timeout=5)
        self.assertEqual(fehler.exception.code, 404)

    def test_steuerung_wird_uebernommen(self):
        anfrage = urllib.request.Request(
            self.adresse + "/steuerung",
            data=json.dumps({"schub": 0.5, "nick": -0.25}).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(anfrage, timeout=5) as antwort:
            self.assertTrue(json.loads(antwort.read())["uebernommen"])
        self.assertAlmostEqual(self.zustand.steuerung["schub"], 0.5)
        self.assertAlmostEqual(self.zustand.steuerung["nick"], -0.25)

    def test_kaputter_koerper_stuerzt_nicht_ab(self):
        anfrage = urllib.request.Request(
            self.adresse + "/steuerung", data=b"kein json",
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(anfrage, timeout=5) as antwort:
            self.assertEqual(antwort.status, 200)


if __name__ == "__main__":
    unittest.main()
