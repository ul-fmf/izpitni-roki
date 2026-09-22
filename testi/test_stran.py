"""Testi za zgenerirano stran: preverjajo dogovor med generatorjem (python)
in skriptama out/permalink.js ter out/posodabljanje.js."""

import os
import re
import unittest

from izpitni_roki.naredi_html import IZHODNA_MAPA, naredi_html
from izpitni_roki.osnovno import Letnik

from testi.pomozno import OBDOBJA, TESTNE, pozabi_vse

IME_IZHODNE = "_test_stran"
POT = os.path.join(IZHODNA_MAPA, f"{IME_IZHODNE}.html")

# <li> z razredom moznost je posamezna izbira, <li> brez njega je skupina črk
MOZNOST = re.compile(r'<li class="(\w+) moznost active" id="([\w-]+)" data-ime="([^"]*)">')
SKUPINA_CRK = re.compile(r'<li class="(\w+) active">')
VRSTICA = re.compile(r'<tr class="izpitna-vrstica" id="([\w_x-]+)"')


def zgeneriraj(poti=None):
    pozabi_vse()
    naredi_html(
        poti or TESTNE,
        naslov="test",
        opis_strani="test",
        ime_izhodne=IME_IZHODNE,
        obdobja=OBDOBJA,
    )
    with open(POT, encoding="utf-8") as f:
        return f.read()


class TestZgenerirenaStran(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = zgeneriraj()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(POT):
            os.remove(POT)

    def test_vsaka_moznost_ima_ime_in_id(self):
        """Permalink išče možnosti po data-ime, filter pa po id."""
        moznosti = MOZNOST.findall(self.html)
        self.assertGreater(len(moznosti), 0)
        for razred, ident, ime in moznosti:
            with self.subTest(ime=ime):
                self.assertTrue(ime, f"prazen data-ime pri {razred}")
                self.assertRegex(ident, r"^[a-z][a-z0-9]*$")

    def test_skupine_crk_niso_moznosti(self):
        """Prav to je bila napaka: <li> črke je imel isti razred kot možnosti,
        zato jih je posodobiGrupnoIzbiro preveč preštel."""
        for vrsta in SKUPINA_CRK.findall(self.html):
            with self.subTest(razred=vrsta):
                self.assertIn(vrsta, {"predmet", "izvajalec"})
        # menija po črkah imata skupine, enonivojski meniji pa ne
        self.assertGreater(len(SKUPINA_CRK.findall(self.html)), 0)

    def test_stevilo_moznosti_na_skupino(self):
        """posodobiGrupnoIzbiro primerja število aktivnih z vsemi možnostmi;
        če bi se skupine črk štele zraven, gumb nikoli ne bi bil zelen."""
        po_razredih = {}
        for razred, _, _ in MOZNOST.findall(self.html):
            po_razredih[razred] = po_razredih.get(razred, 0) + 1
        self.assertEqual(
            sorted(po_razredih),
            ["izvajalec", "letnik", "obdobje", "predmet", "program", "rok"],
        )

    def test_imena_v_data_ime_so_unikatna_znotraj_skupine(self):
        """Permalink naslavlja možnosti po imenu, zato se imena ne smejo ponavljati."""
        videna = {}
        for razred, _, ime in MOZNOST.findall(self.html):
            videna.setdefault(razred, []).append(ime)
        for razred, imena in videna.items():
            with self.subTest(razred=razred):
                self.assertEqual(len(imena), len(set(imena)))

    def test_vrstice_kazejo_na_obstojece_idje(self):
        idji = {ident for _, ident, _ in MOZNOST.findall(self.html)}
        idji.add(Letnik.ID_BREZ_LETNIKA)
        for vrstica in VRSTICA.findall(self.html):
            for skupina in vrstica.split("_"):
                for ident in skupina.split("x"):
                    with self.subTest(vrstica=vrstica, ident=ident):
                        self.assertIn(ident, idji)

    def test_magistrski_roki_imajo_sentinel_namesto_letnika(self):
        """Issue #6: roki brez letnika morajo imeti v mestu letnika sentinel,
        na katerem filter po letnikih ne prime."""
        letniki = [v.split("_")[2].split("x") for v in VRSTICA.findall(self.html)]
        s_sentinelom = [l for l in letniki if Letnik.ID_BREZ_LETNIKA in l]
        self.assertEqual(len(s_sentinelom), 6, "test3.ics ima 6 magistrskih rokov")
        # sentinel ni v meniju letnikov
        v_meniju = {ime for razred, _, ime in MOZNOST.findall(self.html) if razred == "letnik"}
        self.assertNotIn(Letnik.BREZ_LETNIKA, v_meniju)

    def test_idji_so_enaki_ob_ponovnem_generiranju(self):
        """Permalinki (issue #7) ostanejo veljavni tudi po vnovični generaciji."""
        prvic = {(r, i) for r, _, i in MOZNOST.findall(self.html)}
        drugic_html = zgeneriraj(list(reversed(TESTNE)))
        drugic = {(r, i) for r, _, i in MOZNOST.findall(drugic_html)}
        self.assertEqual(prvic, drugic)
        idji_prvic = {i: d for _, d, i in MOZNOST.findall(self.html)}
        idji_drugic = {i: d for _, d, i in MOZNOST.findall(drugic_html)}
        self.assertEqual(idji_prvic, idji_drugic)

    def test_stran_nalozi_permalink_skripto(self):
        self.assertIn('<script src="permalink.js"></script>', self.html)
        self.assertLess(
            self.html.index('src="permalink.js"'),
            self.html.index('src="posodabljanje.js"'),
            "permalink.js mora biti naložen pred posodabljanje.js",
        )


if __name__ == "__main__":
    unittest.main()
