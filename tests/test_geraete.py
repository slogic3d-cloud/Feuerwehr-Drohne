"""Tests der Sensortreiber und ihrer Simulationen."""

import unittest

import pfad  # noqa: F401
from geraete import gps, waermebild


class TestNMEA(unittest.TestCase):

    GUELTIG = "$GPGGA,123519,5014.8320,N,01102.1660,E,1,09,0.9,342.0,M,46.9,M,,*47"

    def test_gueltiger_satz(self):
        position = gps.satz_auswerten(self.GUELTIG)
        self.assertIsNotNone(position)
        self.assertAlmostEqual(position.breite, 50.2472, places=4)
        self.assertAlmostEqual(position.laenge, 11.0361, places=4)
        self.assertEqual(position.satelliten, 9)
        self.assertAlmostEqual(position.hoehe_m, 342.0)

    def test_ohne_fix_keine_position(self):
        self.assertIsNone(gps.satz_auswerten(
            "$GPGGA,123519,,,,,0,00,,,M,,M,,*66"))

    def test_anderer_satztyp_wird_uebergangen(self):
        self.assertIsNone(gps.satz_auswerten(
            "$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,,*6A"))

    def test_muell_stuerzt_nicht_ab(self):
        for satz in ("", "abc", "$GPGGA", "$GPGGA,,,,,,,,,", "$$$$"):
            self.assertIsNone(gps.satz_auswerten(satz))

    def test_suedliche_und_westliche_richtung_sind_negativ(self):
        satz = "$GPGGA,123519,5014.8320,S,01102.1660,W,1,09,0.9,342.0,M,,M,,*47"
        position = gps.satz_auswerten(satz)
        self.assertLess(position.breite, 0)
        self.assertLess(position.laenge, 0)


class TestWaermerahmen(unittest.TestCase):

    def test_verkleinern_mittelt_und_verliert_die_person_nicht(self):
        kamera = waermebild.SimulierterSuchflug()
        kamera.person_sichtbar = True
        voll = kamera.lies()
        klein = voll.verkleinern(64, 48)
        self.assertEqual((klein.breite, klein.hoehe), (64, 48))
        # Die warme Stelle muss auch im kleinen Bild noch herausstechen.
        _, heiss_voll, _ = voll.kennwerte()
        _, heiss_klein, _ = klein.kennwerte()
        self.assertGreater(heiss_klein, klein.kennwerte()[2] + 3.0)
        self.assertLessEqual(heiss_klein, heiss_voll + 0.01)

    def test_verkleinern_auf_gleiche_groesse_gibt_dasselbe_bild(self):
        rahmen = waermebild.SimulierterSuchflug().lies()
        self.assertIs(rahmen.verkleinern(256, 192), rahmen)

    def test_bei_zugriff(self):
        rahmen = waermebild.Waermerahmen(3, 2, [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        self.assertEqual(rahmen.bei(0, 0), 1.0)
        self.assertEqual(rahmen.bei(2, 1), 6.0)

    def test_kennwerte(self):
        rahmen = waermebild.Waermerahmen(2, 2, [1.0, 2.0, 3.0, 4.0])
        self.assertEqual(rahmen.kennwerte(), (1.0, 4.0, 2.5))


class TestSimulation(unittest.TestCase):

    def test_person_veraendert_das_bild(self):
        kamera = waermebild.SimulierterSuchflug()
        kamera.person_sichtbar = False
        kamera.reh_sichtbar = False
        kamera.auto_sichtbar = False
        kamera.weg_sichtbar = False
        kamera.steine_sichtbar = False
        _, ohne, _ = kamera.lies().kennwerte()
        kamera.person_sichtbar = True
        _, mit, _ = kamera.lies().kennwerte()
        self.assertGreater(mit, ohne + 3.0)

    def test_erzeuge_faellt_auf_simulation_zurueck(self):
        kamera = waermebild.erzeuge("simulation", "")
        self.assertIsInstance(kamera, waermebild.SimulierterSuchflug)
        kamera.schliessen()

    def test_gps_simulation_liefert_position(self):
        position = gps.erzeuge("simulation", 9600).lies()
        self.assertGreater(position.satelliten, 0)
        self.assertIn("breite", position.als_dict())


if __name__ == "__main__":
    unittest.main()
