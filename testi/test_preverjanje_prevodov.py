"""Prevodi se morajo ob nalaganju preveriti: nepoznan ključ je napaka,
manjkajoč prevod pa ne (issue #9)."""

import copy
import unittest

from izpitni_roki import jezik as modul_jezik
from izpitni_roki.jezik import Jezik, NapakaVPrevodih, preveri_vmesnik
from izpitni_roki.osnovno import NezapolnjenaPredloga, preveri_zapolnjeno


def vmesnik(**popravki):
    """Veljaven vmesnik s tremi jeziki, ki ga test po potrebi pokvari."""
    osnova = {
        "sl": {
            "ime_jezika": "Slovensko",
            "title": "Izpitni roki",
            "programi": {"1Mate": "Matematika"},
            "dnevi": ["po", "to", "sr", "če", "pe", "so", "ne"],
            "meseci": [str(i) for i in range(1, 13)],
            "oblika_datuma": "{dan}. {mesec} {leto} ({dan_v_tednu})",
        },
        "en": {
            "ime_jezika": "English",
            "title": "",
            "programi": {"1Mate": ""},
            "dnevi": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
            "meseci": [str(i) for i in range(1, 13)],
            "oblika_datuma": "{dan} {mesec} {leto} ({dan_v_tednu})",
        },
        "de": {
            "ime_jezika": "Deutsch",
            "title": "",
            "programi": {"1Mate": ""},
            "dnevi": ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
            "meseci": [str(i) for i in range(1, 13)],
            "oblika_datuma": "{dan}. {mesec} {leto} ({dan_v_tednu})",
        },
    }
    d = copy.deepcopy(osnova)
    for jezik, sprememba in popravki.items():
        d.setdefault(jezik, {}).update(sprememba)
    return d


class TestPreverjanjeVmesnika(unittest.TestCase):
    def test_veljaven_vmesnik_gre_skozi(self):
        preveri_vmesnik(vmesnik())

    def test_prazen_prevod_ni_napaka(self):
        """Manjkajoč prevod je v redu - pade nazaj na slovenščino."""
        preveri_vmesnik(vmesnik(en={"title": ""}))

    def test_nepoznan_kljuc_v_prevodu_je_napaka(self):
        with self.assertRaises(NapakaVPrevodih) as e:
            preveri_vmesnik(vmesnik(en={"titel": "Exam dates"}))
        self.assertIn("titel", str(e.exception))

    def test_nepoznan_kljuc_v_ugnezdenem_slovarju_je_napaka(self):
        with self.assertRaises(NapakaVPrevodih) as e:
            preveri_vmesnik(vmesnik(en={"programi": {"1Mate": "", "1XyZa": "Nekaj"}}))
        self.assertIn("1XyZa", str(e.exception))

    def test_manjkajoc_kljuc_v_prevodu_je_napaka(self):
        """Jeziki morajo imeti natanko iste ključe; vrednost sme biti prazna."""
        d = vmesnik()
        del d["en"]["title"]
        with self.assertRaises(NapakaVPrevodih) as e:
            preveri_vmesnik(d)
        self.assertIn("title", str(e.exception))

    def test_manjkajoc_kljuc_v_ugnezdenem_slovarju_je_napaka(self):
        d = vmesnik()
        d["en"]["programi"] = {}
        with self.assertRaises(NapakaVPrevodih) as e:
            preveri_vmesnik(d)
        self.assertIn("1Mate", str(e.exception))

    def test_manjkajoc_jezik_je_napaka(self):
        """Cel manjkajoc jezik bi tiho padel nazaj na slovenscino."""
        d = vmesnik()
        del d["de"]
        with self.assertRaises(NapakaVPrevodih) as e:
            preveri_vmesnik(d)
        self.assertIn("de", str(e.exception))

    def test_prazne_vrednosti_povsod_gredo_skozi(self):
        """Neprevedeno, a strukturno popolno - tako je datoteka zdaj."""
        preveri_vmesnik(vmesnik(en={"title": "", "programi": {"1Mate": ""}}))

    def test_napacno_stevilo_dni_ali_mesecev_je_napaka(self):
        with self.assertRaises(NapakaVPrevodih):
            preveri_vmesnik(vmesnik(en={"dnevi": ["Mo", "Tu"]}))
        with self.assertRaises(NapakaVPrevodih):
            preveri_vmesnik(vmesnik(en={"meseci": ["Jan"]}))

    def test_slaba_oblika_datuma_je_napaka(self):
        with self.assertRaises(NapakaVPrevodih) as e:
            preveri_vmesnik(vmesnik(en={"oblika_datuma": "{dann} {mesec}"}))
        self.assertIn("dann", str(e.exception))


class TestStrogoIskanjeKljucev(unittest.TestCase):
    def test_nepoznan_kljuc_pri_branju_javi_napako(self):
        """Tipkarska napaka v kodi ne sme tiho vrniti praznega niza."""
        sl = modul_jezik.nalozi_jezik("sl")
        with self.assertRaises(NapakaVPrevodih):
            sl.niz("tega_kljuca_ni")

    def test_poznan_kljuc_brez_prevoda_pade_nazaj(self):
        en = modul_jezik.nalozi_jezik("en")
        self.assertEqual(en.niz("razdelek_o_strani"), "O strani")

    def test_je_razred_jezik(self):
        self.assertIsInstance(modul_jezik.nalozi_jezik("sl"), Jezik)


class TestNepoznanPredmet(unittest.TestCase):
    """Predmet brez vrstice v predmeti.tsv mora ustaviti generiranje: prevodi
    predmetov so obvezni, zato nočemo, da se nov predmet tiho prikaže po slovensko."""

    def test_predmet_iz_tsv_gre_skozi(self):
        en = modul_jezik.nalozi_jezik("en")
        self.assertEqual(en.predmet("Logika"), "Logika")

    def test_nepoznan_predmet_je_napaka(self):
        en = modul_jezik.nalozi_jezik("en")
        with self.assertRaises(NapakaVPrevodih) as e:
            en.predmet("Tega predmeta ni v tsv")
        self.assertIn("Tega predmeta ni v tsv", str(e.exception))
        self.assertIn("predmeti.tsv", str(e.exception))

    def test_tudi_slovenscina_zahteva_vrstico(self):
        sl = modul_jezik.nalozi_jezik("sl")
        with self.assertRaises(NapakaVPrevodih):
            sl.predmet("Tega predmeta tudi ni")


class TestStrogiPodatkovniKljuci(unittest.TestCase):
    """Programi, letniki in obdobja so enako obvezni kot predmeti."""

    def test_nepoznan_program_letnik_obdobje_so_napake(self):
        sl = modul_jezik.nalozi_jezik("sl")
        for metoda, vrednost in [
            (sl.program, "3XyZa"),
            (sl.letnik, "sesti"),
            (sl.obdobje, "pomladansko"),
        ]:
            with self.subTest(vrednost=vrednost):
                with self.assertRaises(NapakaVPrevodih) as e:
                    metoda(vrednost)
                self.assertIn(vrednost, str(e.exception))

    def test_poznani_gredo_skozi(self):
        sl = modul_jezik.nalozi_jezik("sl")
        self.assertEqual(sl.program("1Mate"), "Matematika")
        self.assertEqual(sl.letnik("prvi"), "1. letnik")
        self.assertEqual(sl.obdobje("zimsko"), "zimsko")

    def test_prazen_prevod_pade_nazaj(self):
        en = modul_jezik.nalozi_jezik("en")
        self.assertEqual(en.program("1Mate"), "Matematika")


class TestZapolnjenostPredloge(unittest.TestCase):
    def test_zapolnjena_predloga_gre_skozi(self):
        self.assertEqual(preveri_zapolnjeno("<p>Datum</p>", "test"), "<p>Datum</p>")

    def test_nezapolnjen_kljuc_je_napaka(self):
        """Brez tega bi se na strani pojavil napis {{gumb_prenos}}."""
        with self.assertRaises(NezapolnjenaPredloga) as e:
            preveri_zapolnjeno("<p>{{gumb_prenos}}</p>", "test")
        self.assertIn("gumb_prenos", str(e.exception))

    def test_prava_stran_nima_nezapolnjenih_kljucev(self):
        import os

        from izpitni_roki.naredi_html import IZHODNA_MAPA, naredi_html

        from testi.pomozno import OBDOBJA, TESTNE, pozabi_vse

        pozabi_vse()
        poti = naredi_html(TESTNE, naslov="t", opis_strani="t",
                           ime_izhodne="_test_zapolnjenost", obdobja=OBDOBJA)
        try:
            for pot in poti:
                with open(pot, encoding="utf-8") as f:
                    preveri_zapolnjeno(f.read(), pot)
        finally:
            for pot in poti:
                if os.path.exists(pot):
                    os.remove(pot)


if __name__ == "__main__":
    unittest.main()
