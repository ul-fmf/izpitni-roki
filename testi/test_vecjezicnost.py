"""Testi za večjezičnost (issue #9)."""

import os
import re
import unittest

from izpitni_roki.jezik import JEZIKI, nalozi_jezik
from izpitni_roki.naredi_html import IZHODNA_MAPA, naredi_html

from testi.pomozno import OBDOBJA, TESTNE, pozabi_vse

IME = "_test_vecjezicnost"
MOZNOST = re.compile(r'<li class="(\w+) moznost active" id="([\w-]+)" data-ime="([^"]*)">')
VRSTICA = re.compile(r'<tr class="izpitna-vrstica" id="([\w_x-]+)"')


def pot_strani(koda):
    jezik = nalozi_jezik(koda)
    mapa = os.path.join(IZHODNA_MAPA, jezik.podmapa) if jezik.podmapa else IZHODNA_MAPA
    return os.path.join(mapa, f"{IME}.html")


class TestVecjezicnost(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pozabi_vse()
        naredi_html(TESTNE, naslov="test", opis_strani="test",
                    ime_izhodne=IME, obdobja=OBDOBJA)
        cls.strani = {}
        for koda in JEZIKI:
            with open(pot_strani(koda), encoding="utf-8") as f:
                cls.strani[koda] = f.read()

    @classmethod
    def tearDownClass(cls):
        for koda in JEZIKI:
            if os.path.exists(pot_strani(koda)):
                os.remove(pot_strani(koda))

    def test_zgeneriramo_stran_za_vsak_jezik(self):
        self.assertEqual(sorted(self.strani), sorted(JEZIKI))

    def test_id_ji_so_v_vseh_jezikih_enaki(self):
        """Od tega je odvisen permalink: povezava iz angleščine mora delati
        v slovenščini in obratno (issue #7)."""
        referenca = VRSTICA.findall(self.strani["sl"])
        for koda in JEZIKI:
            with self.subTest(jezik=koda):
                self.assertEqual(VRSTICA.findall(self.strani[koda]), referenca)

    def test_kljuci_data_ime_so_v_vseh_jezikih_enaki(self):
        referenca = {(r, i, ime) for r, i, ime in MOZNOST.findall(self.strani["sl"])}
        for koda in JEZIKI:
            with self.subTest(jezik=koda):
                self.assertEqual(
                    {(r, i, ime) for r, i, ime in MOZNOST.findall(self.strani[koda])},
                    referenca,
                )

    def test_atribut_lang(self):
        for koda in JEZIKI:
            with self.subTest(jezik=koda):
                self.assertIn(f'<html lang="{koda}">', self.strani[koda])

    def test_predpona_do_sredstev(self):
        self.assertIn('href="dodatni.css"', self.strani["sl"])
        for koda in ["en", "de"]:
            with self.subTest(jezik=koda):
                self.assertIn('href="../dodatni.css"', self.strani[koda])

    def test_povezave_na_druge_jezike_kazejo_na_obstojece_datoteke(self):
        for koda in JEZIKI:
            mapa = os.path.dirname(pot_strani(koda))
            for pot in re.findall(r'class="povezava-jezik[^"]*" href="([^"#]+)"',
                                  self.strani[koda]):
                with self.subTest(jezik=koda, pot=pot):
                    self.assertTrue(os.path.exists(os.path.join(mapa, pot)), pot)

    def test_preklop_jezika_ima_zastave(self):
        """Zastave so vrisane, ne slike z omrežja, ime jezika pa ostane dostopno."""
        for koda in JEZIKI:
            with self.subTest(jezik=koda):
                blok = re.search(
                    r'<div class="preklop-jezika">.*?</div>', self.strani[koda], re.S
                ).group(0)
                self.assertEqual(blok.count('class="zastava"'), len(JEZIKI))
                self.assertEqual(blok.count("<svg "), len(JEZIKI))
                self.assertNotIn("<img", blok)
                for ime in ["Slovensko", "English", "Deutsch"]:
                    self.assertIn(f'title="{ime}"', blok)
                    self.assertIn(f'aria-label="{ime}"', blok)

    def test_datumi_so_po_jezikih_razlicni(self):
        datumi = {
            koda: re.findall(r'<td scope="row">([^<]+)</td>', h)[0]
            for koda, h in self.strani.items()
        }
        self.assertEqual(datumi["sl"], "27. januar 2022 (četrtek)")
        self.assertEqual(datumi["en"], "27 January 2022 (Thursday)")
        self.assertEqual(datumi["de"], "27. Januar 2022 (Donnerstag)")

    def test_strani_so_res_prevedene(self):
        for koda, pricakovano in [
            ("sl", "O strani"), ("en", "About this page"), ("de", "Über diese Seite"),
        ]:
            with self.subTest(jezik=koda):
                self.assertIn(pricakovano, self.strani[koda])

    def test_roki_so_besede_v_en_in_de(self):
        """Issue #9: 'rok' je v anglescini 'sitting' z besedno obliko stevila."""
        self.assertIn("<td>first</td>", self.strani["en"])
        self.assertIn("<td>erster</td>", self.strani["de"])
        self.assertIn("<td>1.</td>", self.strani["sl"])

    def test_meniji_kazejo_lepa_imena_ne_kod(self):
        moznosti = {
            besedilo.strip()
            for razred, besedilo in re.findall(
                r'<li class="(letnik) moznost active"[^>]*>\s*<a[^>]*>([^<]+)</a>',
                self.strani["sl"],
            )
        }
        self.assertIn("1. letnik", moznosti)
        self.assertNotIn("prvi", moznosti)


if __name__ == "__main__":
    unittest.main()
