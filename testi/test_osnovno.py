"""Testi za determinističnost id-jev (glej issue #7: permalinki morajo preživeti
ponovno generiranje strani)."""

import unittest

from izpitni_roki.nalozi_ics import nalozi_ics
from izpitni_roki.osnovno import IDTerIme, Letnik, Predmet, Program

from testi.pomozno import OBDOBJA, TESTNE, pozabi_vse


def imena_in_idji(poti):
    """Zemljevid ime -> id za vse programe, letnike in predmete v danih koledarjih."""
    pozabi_vse()
    zemljevid = {}
    for pot in poti:
        for rok in nalozi_ics(pot, obdobja=OBDOBJA).izpitni_roki:
            for polje in list(rok.programi) + list(rok.letniki) + [rok.predmet]:
                zemljevid[polje.ime] = polje.id
    return zemljevid


class TestDeterministicniIdji(unittest.TestCase):
    def test_isto_ime_isti_id(self):
        pozabi_vse()
        prvi = Program("1Mate")
        pozabi_vse()
        drugi = Program("1Mate")
        self.assertEqual(prvi.id, drugi.id)

    def test_razlicna_imena_razlicni_idji(self):
        pozabi_vse()
        idji = {Predmet(ime).id for ime in ["Logika", "Analiza 1", "Algebra 3"]}
        self.assertEqual(len(idji), 3)

    def test_id_je_prijazen_jqueryju(self):
        """Id ne sme imeti locil, ki ju uporablja IzpitniRok.id (``_`` in ``x``),
        in se ne sme zaceti s stevko, sicer ni veljaven css selektor."""
        pozabi_vse()
        imena = ["1Mate", "Verjetnost 2", "Šestković Matej", "prvi", "3."]
        for ime in imena:
            with self.subTest(ime=ime):
                self.assertRegex(IDTerIme(ime).id, r"^[a-z][a-z0-9]*$")

    def test_sentinel_brez_letnika_ohrani_svoj_id(self):
        pozabi_vse()
        self.assertEqual(Letnik(Letnik.BREZ_LETNIKA).id, Letnik.ID_BREZ_LETNIKA)

    def test_idji_prezivijo_drug_vrstni_red_datotek(self):
        """Prav to je pokvarilo permalinke: id-ji so bili zaporedne stevilke,
        zato je drugacen vrstni red branja dal drugacne id-je."""
        prvic = imena_in_idji(TESTNE)
        drugic = imena_in_idji(list(reversed(TESTNE)))
        self.assertEqual(prvic, drugic)

    def test_idji_prezivijo_izpad_datoteke(self):
        """Ko se podatki spremenijo, morajo id-ji preostalih imen ostati enaki."""
        vse = imena_in_idji(TESTNE)
        manj = imena_in_idji(TESTNE[:2])
        for ime, id_ in manj.items():
            with self.subTest(ime=ime):
                self.assertEqual(vse[ime], id_)


if __name__ == "__main__":
    unittest.main()
