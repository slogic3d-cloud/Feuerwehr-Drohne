"""Tests der Personenerkennung im Waermebild."""

import unittest

import pfad  # noqa: F401
import erkennung
import konfig
from geraete.waermebild import SimulierterSuchflug, Waermerahmen


def rahmen_mit(breite, hoehe, grund, objekte=()):
    """Baut einen Waermerahmen mit Rechtecken: (x, y, breite, hoehe, temperatur)."""
    werte = [grund] * (breite * hoehe)
    for x0, y0, b, h, temperatur in objekte:
        for y in range(y0, min(y0 + h, hoehe)):
            for x in range(x0, min(x0 + b, breite)):
                werte[y * breite + x] = temperatur
    return Waermerahmen(breite, hoehe, werte)


class TestFleckensuche(unittest.TestCase):

    def test_findet_zusammenhaengenden_bereich(self):
        rahmen = rahmen_mit(20, 20, 10.0, [(5, 5, 4, 4, 20.0)])
        flecken = erkennung.flecken_suchen(rahmen, 15.0)
        self.assertEqual(len(flecken), 1)
        zellen, x0, y0, x1, y1, mittel, hoechst = flecken[0]
        self.assertEqual(len(zellen), 16)
        self.assertEqual((x0, y0, x1, y1), (5, 5, 8, 8))
        self.assertAlmostEqual(mittel, 20.0)

    def test_trennt_zwei_getrennte_bereiche(self):
        rahmen = rahmen_mit(20, 20, 10.0, [(2, 2, 3, 3, 20.0), (14, 14, 3, 3, 20.0)])
        self.assertEqual(len(erkennung.flecken_suchen(rahmen, 15.0)), 2)

    def test_findet_nichts_unter_der_schwelle(self):
        rahmen = rahmen_mit(20, 20, 10.0, [(5, 5, 4, 4, 12.0)])
        self.assertEqual(erkennung.flecken_suchen(rahmen, 15.0), [])


class TestAnzeigespanne(unittest.TestCase):

    def test_ausreisser_stauchen_die_spanne_nicht(self):
        werte = [10.0] * 999 + [80.0]      # eine sehr heisse Motorhaube
        kalt, heiss = erkennung.spanne_fuer_anzeige(werte)
        self.assertLess(heiss, 20.0, "Ausreisser darf die Skala nicht bestimmen")

    def test_mindestspanne_wird_eingehalten(self):
        kalt, heiss = erkennung.spanne_fuer_anzeige([10.0] * 100)
        self.assertGreaterEqual(heiss - kalt, 2.99)


class TestBewertung(unittest.TestCase):

    def setUp(self):
        self.kamera = SimulierterSuchflug()

    def _lage(self, **schalter):
        for name, wert in schalter.items():
            setattr(self.kamera, name, wert)
        return erkennung.auswerten(self.kamera.lies(), konfig, hoehe_m=40)

    def test_person_auf_kalter_wiese_wird_gefunden(self):
        lage = self._lage(person_sichtbar=True, reh_sichtbar=False)
        self.assertGreaterEqual(lage.vertrauen, 0.75)
        self.assertEqual(lage.stufe, "sehr wahrscheinlich")

    def test_leere_szene_meldet_nichts(self):
        lage = self._lage(person_sichtbar=False, reh_sichtbar=False,
                          weg_sichtbar=False, auto_sichtbar=False,
                          steine_sichtbar=False)
        self.assertEqual(lage.vertrauen, 0.0)
        self.assertEqual(lage.stufe, "kein Hinweis")

    def test_heisse_motorhaube_loest_keinen_alarm_aus(self):
        lage = self._lage(person_sichtbar=False, reh_sichtbar=False,
                          weg_sichtbar=False, steine_sichtbar=False,
                          auto_sichtbar=True)
        self.assertLess(lage.vertrauen, konfig.TREFFER_SCHWELLE,
                        "zu heisse Technik darf keinen Treffer ausloesen")

    def test_person_liefert_koordinate_wenn_gps_anliegt(self):
        from geraete.gps import SimuliertesGPS
        self.kamera.person_sichtbar = True
        lage = erkennung.auswerten(self.kamera.lies(), konfig, hoehe_m=40,
                                   position=SimuliertesGPS().lies())
        self.assertIsNotNone(lage.bester_fleck)
        self.assertIsNotNone(lage.bester_fleck.koordinate)

    def test_begruendung_warnt_vor_wild(self):
        lage = self._lage(person_sichtbar=True)
        self.assertTrue(any("Wild" in g for g in lage.begruendung),
                        "die Verwechslungsgefahr muss im Klartext dabeistehen")


class TestErwarteteGroesse(unittest.TestCase):

    def test_person_wird_mit_der_hoehe_kleiner(self):
        nah = erkennung.erwartete_zellen(20, konfig, 256)
        fern = erkennung.erwartete_zellen(60, konfig, 256)
        self.assertGreater(nah, fern)

    def test_mindestens_eine_zelle(self):
        self.assertGreaterEqual(erkennung.erwartete_zellen(5000, konfig, 256), 1.0)


class TestStufen(unittest.TestCase):

    def test_stufen_sind_aufsteigend(self):
        self.assertEqual(erkennung.stufe(0.0), "kein Hinweis")
        self.assertEqual(erkennung.stufe(0.4), "moeglich")
        self.assertEqual(erkennung.stufe(0.6), "wahrscheinlich")
        self.assertEqual(erkennung.stufe(0.95), "sehr wahrscheinlich")


if __name__ == "__main__":
    unittest.main()
