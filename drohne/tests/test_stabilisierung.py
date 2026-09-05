"""Tests der Bildstabilisierung und Fleckverfolgung."""

import unittest

import pfad  # noqa: F401
import stabilisierung
from geraete.waermebild import Waermerahmen


def bild_mit_fleck(breite, hoehe, x, y, groesse=6, grund=10.0, warm=25.0):
    werte = [grund] * (breite * hoehe)
    for dy in range(groesse):
        for dx in range(groesse):
            px, py = x + dx, y + dy
            if 0 <= px < breite and 0 <= py < hoehe:
                werte[py * breite + px] = warm
    return Waermerahmen(breite, hoehe, werte)


class TestVersatzschaetzung(unittest.TestCase):

    def test_erkennt_verschiebung_nach_rechts(self):
        a = bild_mit_fleck(48, 36, 10, 10)
        b = bild_mit_fleck(48, 36, 14, 10)
        dx, dy, guete = stabilisierung.versatz_schaetzen(
            a.werte, b.werte, 48, 36)
        self.assertEqual((dx, dy), (4, 0), "Bewegungsrichtung, nicht ihr Gegenteil")
        self.assertGreater(guete, 0.5)

    def test_erkennt_verschiebung_nach_links(self):
        a = bild_mit_fleck(48, 36, 14, 10)
        b = bild_mit_fleck(48, 36, 10, 10)
        dx, dy, _ = stabilisierung.versatz_schaetzen(a.werte, b.werte, 48, 36)
        self.assertEqual((dx, dy), (-4, 0))

    def test_erkennt_verschiebung_nach_unten(self):
        a = bild_mit_fleck(48, 36, 10, 8)
        b = bild_mit_fleck(48, 36, 10, 12)
        dx, dy, _ = stabilisierung.versatz_schaetzen(a.werte, b.werte, 48, 36)
        self.assertEqual((dx, dy), (0, 4))

    def test_ungerade_verschiebung_auf_einen_punkt_genau(self):
        # Es wird nur jeder zweite Punkt verglichen - ungerade Verschiebungen
        # duerfen deshalb um einen Bildpunkt danebenliegen, mehr nicht.
        a = bild_mit_fleck(48, 36, 10, 10)
        b = bild_mit_fleck(48, 36, 13, 10)
        dx, dy, _ = stabilisierung.versatz_schaetzen(a.werte, b.werte, 48, 36)
        self.assertAlmostEqual(dx, 3, delta=1)
        self.assertAlmostEqual(dy, 0, delta=1)

    def test_ohne_bewegung_kein_versatz(self):
        a = bild_mit_fleck(48, 36, 10, 10)
        dx, dy, _ = stabilisierung.versatz_schaetzen(a.werte, a.werte, 48, 36)
        self.assertEqual((dx, dy), (0, 0))


class TestBildstabilisator(unittest.TestCase):

    def test_erstes_bild_liefert_keinen_versatz(self):
        stab = stabilisierung.Bildstabilisator()
        self.assertEqual(stab.takt(bild_mit_fleck(96, 72, 20, 20)), (0, 0))

    def test_gleichmaessiger_flug_gilt_nicht_als_boeig(self):
        stab = stabilisierung.Bildstabilisator()
        # Immer derselbe Versatz je Bild = gleichmaessiger Vorwaertsflug.
        for i in range(14):
            stab.takt(bild_mit_fleck(96, 72, 20, 10 + i * 4))
        self.assertTrue(stab.ruhig(), "gleichmaessiger Flug darf nicht als Boe zaehlen")

    def test_zappeln_erhoeht_die_boeigkeit(self):
        stab = stabilisierung.Bildstabilisator()
        ruhig = stabilisierung.Bildstabilisator()
        for i in range(14):
            # Sprunghaft hin und her statt gleichmaessig.
            stab.takt(bild_mit_fleck(96, 72, 20 + (12 if i % 2 else 0), 20))
            ruhig.takt(bild_mit_fleck(96, 72, 20, 20))
        self.assertGreater(stab.boeigkeit_px, ruhig.boeigkeit_px)

    def test_windstufe_ist_beschriftet(self):
        stab = stabilisierung.Bildstabilisator()
        self.assertEqual(stab.windstufe(), "ruhig")
        stab.boeigkeit_px = 7.0
        self.assertEqual(stab.windstufe(), "kräftige Böen")
        stab.boeigkeit_px = 20.0
        self.assertFalse(stab.ruhig())


class HilfsFleck:
    """Nachbildung eines Flecks - die Verfolgung braucht nur Mitte und Wert."""

    def __init__(self, x, y, vertrauen=0.8):
        self._mitte = (x, y)
        self.vertrauen = vertrauen

    @property
    def mitte(self):
        return self._mitte


class TestFleckverfolgung(unittest.TestCase):

    def test_derselbe_fleck_behaelt_seine_spur(self):
        verfolgung = stabilisierung.Fleckverfolgung()
        erste = verfolgung.takt([HilfsFleck(50, 50)], (0, 0), 1.0)[0][1]
        zweite = verfolgung.takt([HilfsFleck(52, 51)], (0, 0), 1.1)[0][1]
        self.assertIs(erste, zweite)
        self.assertEqual(zweite.gesehen, 2)

    def test_bildversatz_wird_beruecksichtigt(self):
        verfolgung = stabilisierung.Fleckverfolgung()
        erste = verfolgung.takt([HilfsFleck(50, 50)], (0, 0), 1.0)[0][1]
        # Fleck wandert um 15 px, aber das Bild hat sich um 15 px verschoben.
        zweite = verfolgung.takt([HilfsFleck(65, 50)], (15, 0), 1.1)[0][1]
        self.assertIs(erste, zweite, "Versatz muss herausgerechnet werden")

    def test_weit_entfernter_fleck_bekommt_eigene_spur(self):
        verfolgung = stabilisierung.Fleckverfolgung()
        erste = verfolgung.takt([HilfsFleck(20, 20)], (0, 0), 1.0)[0][1]
        zweite = verfolgung.takt([HilfsFleck(200, 150)], (0, 0), 1.1)[0][1]
        self.assertIsNot(erste, zweite)

    def test_bestaendigkeit_waechst_und_deckelt_bei_eins(self):
        verfolgung = stabilisierung.Fleckverfolgung()
        werte = []
        for _ in range(8):
            spur = verfolgung.takt([HilfsFleck(50, 50)], (0, 0), 1.0)[0][1]
            werte.append(spur.bestaendigkeit())
        self.assertLess(werte[0], werte[3])
        self.assertEqual(werte[-1], 1.0)

    def test_verschwundene_spur_wird_aufgeraeumt(self):
        verfolgung = stabilisierung.Fleckverfolgung(hoechstens_verpasst=2)
        verfolgung.takt([HilfsFleck(50, 50)], (0, 0), 1.0)
        for _ in range(5):
            verfolgung.takt([], (0, 0), 1.0)
        self.assertEqual(verfolgung.spuren, [])


if __name__ == "__main__":
    unittest.main()
