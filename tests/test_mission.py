"""Tests der Missionsplanung."""

import unittest

import pfad  # noqa: F401
import konfig
import mission


class TestMissionsdatei(unittest.TestCase):

    WEGPUNKTE = [(50.2450, 11.0330), (50.2486, 11.0330), (50.2486, 11.0386)]

    def test_kopfzeile_und_spalten(self):
        text = mission.qgc_wpl(self.WEGPUNKTE, 40.0)
        zeilen = text.strip().split("\n")
        self.assertEqual(zeilen[0], "QGC WPL 110")
        for zeile in zeilen[1:]:
            self.assertEqual(len(zeile.split("\t")), 12,
                             "das Format verlangt genau zwölf Spalten")

    def test_reihenfolge_heimat_start_wegpunkte_rueckkehr(self):
        zeilen = mission.qgc_wpl(self.WEGPUNKTE, 40.0).strip().split("\n")[1:]
        befehle = [int(z.split("\t")[3]) for z in zeilen]
        self.assertEqual(befehle[0], mission.BEFEHL_WEGPUNKT, "Zeile 0 ist die Heimat")
        self.assertEqual(befehle[1], mission.BEFEHL_START)
        self.assertEqual(befehle[2:5], [mission.BEFEHL_WEGPUNKT] * 3)
        self.assertEqual(befehle[-1], mission.BEFEHL_HEIMKEHR)

    def test_indizes_laufen_fortlaufend(self):
        zeilen = mission.qgc_wpl(self.WEGPUNKTE, 40.0).strip().split("\n")[1:]
        self.assertEqual([int(z.split("\t")[0]) for z in zeilen],
                         list(range(len(zeilen))))

    def test_hoehe_steht_in_den_wegpunkten(self):
        zeilen = mission.qgc_wpl(self.WEGPUNKTE, 55.0).strip().split("\n")[1:]
        wegpunkte = [z for z in zeilen
                     if int(z.split("\t")[3]) == mission.BEFEHL_WEGPUNKT][1:]
        for z in wegpunkte:
            self.assertAlmostEqual(float(z.split("\t")[10]), 55.0)

    def test_startpunkt_wird_uebernommen(self):
        start = (50.1000, 11.1000)
        erste = mission.qgc_wpl(self.WEGPUNKTE, 40.0, start).strip().split("\n")[1]
        self.assertAlmostEqual(float(erste.split("\t")[8]), 50.1)
        self.assertAlmostEqual(float(erste.split("\t")[9]), 11.1)

    def test_ohne_wegpunkte_fehler(self):
        with self.assertRaises(ValueError):
            mission.qgc_wpl([], 40.0)

    def test_rueckkehr_kann_entfallen(self):
        zeilen = mission.qgc_wpl(self.WEGPUNKTE, 40.0,
                                 mit_heimkehr=False).strip().split("\n")[1:]
        self.assertNotIn(mission.BEFEHL_HEIMKEHR,
                         [int(z.split("\t")[3]) for z in zeilen])


class TestPlanung(unittest.TestCase):

    ECKE_A, ECKE_B = (50.2450, 11.0330), (50.2486, 11.0386)

    def test_eckwerte_sind_stimmig(self):
        plan = mission.planen(self.ECKE_A, self.ECKE_B, 40.0, konfig)
        self.assertGreater(plan["flaeche_ha"], 10)
        self.assertLess(plan["flaeche_ha"], 25)
        self.assertGreater(plan["bahnen"], 5)
        self.assertEqual(plan["anzahl_wegpunkte"], plan["bahnen"] * 2)
        self.assertGreater(plan["strecke_m"], 1000)
        self.assertGreaterEqual(plan["akkus"], 1)

    def test_hoeherer_flug_braucht_weniger_bahnen(self):
        tief = mission.planen(self.ECKE_A, self.ECKE_B, 25.0, konfig)
        hoch = mission.planen(self.ECKE_A, self.ECKE_B, 55.0, konfig)
        self.assertGreater(tief["bahnen"], hoch["bahnen"])
        self.assertGreater(tief["strecke_m"], hoch["strecke_m"])

    def test_langsamer_flug_dauert_laenger(self):
        schnell = mission.planen(self.ECKE_A, self.ECKE_B, 40.0, konfig, tempo_ms=10)
        langsam = mission.planen(self.ECKE_A, self.ECKE_B, 40.0, konfig, tempo_ms=5)
        self.assertGreater(langsam["dauer_min"], schnell["dauer_min"])

    def test_kurze_akkulaufzeit_braucht_mehr_akkus(self):
        lang = mission.planen(self.ECKE_A, self.ECKE_B, 40.0, konfig, flugzeit_min=40)
        kurz = mission.planen(self.ECKE_A, self.ECKE_B, 40.0, konfig, flugzeit_min=8)
        self.assertGreater(kurz["akkus"], lang["akkus"])

    def test_reserve_wird_beruecksichtigt(self):
        # Bei 22 min Akku und 25 % Reserve sind 16,5 min nutzbar - ein Flug von
        # rund 18 min muss deshalb zwei Akkus verlangen.
        plan = mission.planen(self.ECKE_A, self.ECKE_B, 40.0, konfig,
                              tempo_ms=6.3, flugzeit_min=22)
        self.assertGreater(plan["dauer_min"], 16.5)
        self.assertEqual(plan["akkus"], 2)

    def test_richtung_aendert_die_bahnen(self):
        nord = mission.planen(self.ECKE_A, self.ECKE_B, 40.0, konfig, richtung="nord")
        ost = mission.planen(self.ECKE_A, self.ECKE_B, 40.0, konfig, richtung="ost")
        self.assertNotEqual(nord["wegpunkte"][1], ost["wegpunkte"][1])

    def test_flaeche_stimmt_ungefaehr(self):
        # Rund 400 x 400 m sind etwa 16 ha.
        self.assertAlmostEqual(mission.flaeche_ha(self.ECKE_A, self.ECKE_B),
                               16.0, delta=2.0)

    def test_mission_ist_enthalten(self):
        plan = mission.planen(self.ECKE_A, self.ECKE_B, 40.0, konfig)
        self.assertTrue(plan["mission"].startswith("QGC WPL 110"))


if __name__ == "__main__":
    unittest.main()
