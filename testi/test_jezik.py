"""Testi za nalaganje prevodov (issue #9)."""

import json
import os
import unittest
from datetime import datetime

from izpitni_roki.jezik import JEZIKI, Jezik, NapakaVPrevodih, nalozi_jezik


class TestJezik(unittest.TestCase):
    def test_poznamo_tri_jezike(self):
        self.assertEqual(JEZIKI, ["sl", "en", "de"])

    def test_neznan_jezik_javi_napako(self):
        with self.assertRaises(ValueError):
            nalozi_jezik("fr")

    def test_slovenscina_ima_vse_nize(self):
        sl = nalozi_jezik("sl")
        for kljuc in ["title", "razdelek_o_strani", "stolpec_datum", "meni_program"]:
            with self.subTest(kljuc=kljuc):
                self.assertTrue(sl.niz(kljuc), f"manjka {kljuc}")

    def test_program_in_letnik(self):
        sl = nalozi_jezik("sl")
        self.assertEqual(sl.program("1ApMa"), "Aplikativna matematika")
        self.assertEqual(sl.letnik("prvi"), "1. letnik")

    def test_neznan_program_je_napaka(self):
        """Vsak program mora imeti vnos; tiho prikazana koda je napaka."""
        sl = nalozi_jezik("sl")
        with self.assertRaises(NapakaVPrevodih):
            sl.program("3XyZa")

    def test_predmet_je_preveden(self):
        self.assertEqual(nalozi_jezik("en").predmet("Logika"), "Logic")
        self.assertEqual(nalozi_jezik("de").predmet("Logika"), "Logik")

    def test_predmet_brez_prevoda_je_slovenski(self):
        """Jezik s praznim slovarjem predmetov: ali je ime slovensko, ne sme biti
        odvisno od tega, koliko je v resnici ze prevedeno."""
        nalozi_jezik("sl")  # napolni predpomnilnik
        prazen = Jezik("en", {}, {})
        self.assertEqual(prazen.predmet("Logika"), "Logika")

    def test_datum_sl(self):
        sl = nalozi_jezik("sl")
        self.assertEqual(sl.datum(datetime(2022, 1, 27)), "27. januar 2022 (četrtek)")

    def test_datum_en_je_en_gb(self):
        """en-GB: brez pike za dnevom, dan v tednu v oklepaju na koncu."""
        en = nalozi_jezik("en")
        self.assertEqual(en.datum(datetime(2022, 1, 27)), "27 January 2022 (Thursday)")

    def test_datum_de(self):
        de = nalozi_jezik("de")
        self.assertEqual(de.datum(datetime(2022, 1, 27)), "27. Januar 2022 (Donnerstag)")

    def test_jezik_ve_za_svojo_pot(self):
        """Slovenscina ostane na obstojecem url-ju, ostala dva sta v podmapi."""
        self.assertEqual(nalozi_jezik("sl").podmapa, "")
        self.assertEqual(nalozi_jezik("en").podmapa, "en")
        self.assertEqual(nalozi_jezik("sl").predpona_sredstev, "")
        self.assertEqual(nalozi_jezik("en").predpona_sredstev, "../")

    def test_zastave_se_ujemajo_z_jeziki(self):
        """Imena zastav (brez končnice) morajo biti natanko jeziki iz prevodov.

        Manjkajoča zastava podre generiranje, odvečna pa tiho leži v repozitoriju,
        zato preverimo obe smeri hkrati.
        """
        mapa = os.path.join("predloge", "zastave")
        zastave = {
            os.path.splitext(d)[0] for d in os.listdir(mapa) if d.endswith(".svg")
        }
        with open(os.path.join("prevodi", "vmesnik.json"), encoding="utf-8") as f:
            v_prevodih = set(json.load(f))
        self.assertEqual(zastave, v_prevodih)
        self.assertEqual(zastave, set(JEZIKI))

    def test_je_objekt_tipa_jezik(self):
        self.assertIsInstance(nalozi_jezik("sl"), Jezik)


if __name__ == "__main__":
    unittest.main()
