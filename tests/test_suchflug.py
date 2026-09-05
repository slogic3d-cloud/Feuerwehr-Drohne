"""Tests der Suchflug-Geometrie."""

import math
import unittest

import pfad  # noqa: F401  - setzt den Suchpfad
import suchflug


class TestGeometrie(unittest.TestCase):

    def test_streifenbreite_waechst_mit_der_hoehe(self):
        self.assertAlmostEqual(suchflug.streifenbreite(40, 45.6), 33.6, delta=0.2)
        self.assertAlmostEqual(suchflug.streifenbreite(80, 45.6),
                               2 * suchflug.streifenbreite(40, 45.6), delta=0.01)

    def test_streifenbreite_bei_null_hoehe_ist_null(self):
        self.assertEqual(suchflug.streifenbreite(0, 45.6), 0.0)

    def test_person_wird_mit_der_hoehe_kleiner(self):
        nah = suchflug.pixel_je_person(20, 45.6, 256)
        fern = suchflug.pixel_je_person(80, 45.6, 256)
        self.assertGreater(nah, fern)
        self.assertAlmostEqual(nah, 4 * fern, delta=0.01)

    def test_empfohlene_hoehe_ist_umkehrung_von_pixel_je_person(self):
        hoehe = suchflug.empfohlene_hoehe(8, 45.6, 256)
        self.assertAlmostEqual(
            suchflug.pixel_je_person(hoehe, 45.6, 256), 8.0, delta=0.01)


class TestGeoreferenzierung(unittest.TestCase):

    ORT = (50.2472, 11.0361)

    def test_bildmitte_liegt_unter_der_drohne(self):
        ziel = suchflug.pixel_zu_koordinate(
            128, 96, 256, 192, 40, 0, self.ORT, 45.6, 35.4)
        self.assertLess(suchflug.abstand_m(self.ORT, ziel), 0.2)

    def test_oberer_bildrand_liegt_bei_kurs_null_noerdlich(self):
        ziel = suchflug.pixel_zu_koordinate(
            128, 0, 256, 192, 40, 0, self.ORT, 45.6, 35.4)
        self.assertGreater(ziel[0], self.ORT[0], "muss noerdlicher liegen")
        self.assertAlmostEqual(ziel[1], self.ORT[1], places=5)

    def test_kurs_dreht_das_bild_mit(self):
        # Derselbe Bildpunkt bei Kurs Ost muss oestlich statt noerdlich liegen.
        ziel = suchflug.pixel_zu_koordinate(
            128, 0, 256, 192, 40, 90, self.ORT, 45.6, 35.4)
        self.assertGreater(ziel[1], self.ORT[1], "muss oestlicher liegen")
        self.assertAlmostEqual(ziel[0], self.ORT[0], places=5)

    def test_abstand_bleibt_bei_drehung_gleich(self):
        abstaende = []
        for kurs in (0, 45, 90, 180, 270):
            ziel = suchflug.pixel_zu_koordinate(
                200, 40, 256, 192, 40, kurs, self.ORT, 45.6, 35.4)
            abstaende.append(suchflug.abstand_m(self.ORT, ziel))
        self.assertLess(max(abstaende) - min(abstaende), 0.05)

    def test_versatz_nach_norden(self):
        ziel = suchflug.versatz_zu_koordinate(self.ORT, 100.0, 0.0)
        self.assertAlmostEqual(suchflug.abstand_m(self.ORT, ziel), 100.0, delta=0.5)


class TestSuchmuster(unittest.TestCase):

    def test_maeander_deckt_das_gebiet_ab(self):
        ecke_a, ecke_b = (50.2450, 11.0330), (50.2486, 11.0386)
        wegpunkte = suchflug.maeander(ecke_a, ecke_b, 25.0)
        self.assertGreater(len(wegpunkte), 8)
        breiten = [w[0] for w in wegpunkte]
        laengen = [w[1] for w in wegpunkte]
        self.assertAlmostEqual(min(breiten), 50.2450, places=4)
        self.assertAlmostEqual(max(breiten), 50.2486, places=4)
        self.assertLessEqual(min(laengen), 11.0330 + 1e-6)
        self.assertGreaterEqual(max(laengen), 11.0386 - 0.001)

    def test_maeander_fliegt_jede_zweite_bahn_rueckwaerts(self):
        wegpunkte = suchflug.maeander((50.245, 11.033), (50.2486, 11.0386), 40.0)
        # Bahn 1 nach Norden, Bahn 2 nach Sueden.
        self.assertLess(wegpunkte[0][0], wegpunkte[1][0])
        self.assertGreater(wegpunkte[2][0], wegpunkte[3][0])

    def test_maeander_ohne_abstand_liefert_nichts(self):
        self.assertEqual(suchflug.maeander((50.245, 11.033), (50.246, 11.034), 0), [])

    def test_engere_bahnen_bedeuten_mehr_strecke(self):
        weit = suchflug.maeander((50.245, 11.033), (50.2486, 11.0386), 40.0)
        eng = suchflug.maeander((50.245, 11.033), (50.2486, 11.0386), 15.0)
        self.assertGreater(suchflug.strecke_m(eng), suchflug.strecke_m(weit))

    def test_flaechenleistung(self):
        # 8 m/s auf 25 m Bahnabstand sind 200 m² je Sekunde = 1,2 ha je Minute.
        self.assertAlmostEqual(
            suchflug.flaechenleistung_ha_min(8.0, 25.0), 1.2, delta=0.01)


if __name__ == "__main__":
    unittest.main()
