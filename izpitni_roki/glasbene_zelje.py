from izpitni_roki.osnovno import Koledar, IzpitniRok, naredi_zapisnikarja, preveri_ics_datoteke
from izpitni_roki.nalozi_ics import nalozi_ics
from typing import List, Callable


ZAPISNIKAR = naredi_zapisnikarja(__file__)


IZBIRNI_PREDMETI_TUDI_ZA_ISRM = [
    ("Teorija iger", "1FiMa"),
    ("Splošna topologija", "1Mate"),
    ("Algebraične krivulje", "1Mate"),
    ("Teorija kodiranja in kriptografija", "1Mate"),
    ("Matematično modeliranje", "1Mate"),
    ("Numerične metode 2", "1FiMa"),
    ("Finančna matematika 1", "1FiMa"),
    ("Uvod v geometrijsko topologijo", "1Mate"),
    ("Afina in projektivna geometrija", "1Mate")
]


def ustrezni_izpitni_roki(
        koledarji: List[Koledar],
        pogoj: Callable[[IzpitniRok], bool]
) -> List[IzpitniRok]:
    """
    Vrne roke v koledarjih, ki ustrezajo filtrirnemu pogoju.

    :param koledarji: seznam koledarjev
    :param pogoj: funkcija, ki oceni primernost roka

    :return: urejen seznam ustreznih rokov
    """

    ustrezni_roki = []
    for koledar in koledarji:
        for izpitni_rok in koledar.izpitni_roki:
            if pogoj(izpitni_rok):
                ustrezni_roki.append(izpitni_rok)
    ustrezni_roki.sort()
    return ustrezni_roki


def _filter_za_isrm(rok: IzpitniRok):
    for predmet, smer in IZBIRNI_PREDMETI_TUDI_ZA_ISRM:
        if rok.predmet.ime == predmet and any(smer == program.ime for program in rok.programi):
            return True
    return False


def prikazi_isrm_roke(poti_do_ics: str | list[str]):
    """
    Prikaže roke za predmete, ki jih ponujamo IŠRM. Izda opozorilo, če za kakšnega od predmetov
    ni bil najden noben rok.

    :param poti_do_ics: poti do ics datotek kot a) niz, ki predstavlja ime mape, npr. ``letosnji_data``
                        (najdemo vse ics datoteke v dani mapi), ali b) seznam ics datotek, npr.
                        ``["letosnji_data/test1.ics", "letosnji_data/test2.ics"]``
    :return: ne vrne ničesar, samo izpiše ustrezne vrstice
    """
    poti_do_ics = preveri_ics_datoteke(poti_do_ics)
    koledarji = [nalozi_ics(pot) for pot in poti_do_ics]
    ustrezni_roki = ustrezni_izpitni_roki(koledarji, _filter_za_isrm)
    print("Roki za predmete, ki jih ponudimo IŠRM:")
    for rok in ustrezni_roki:
        print(rok.osnovni_opis())
    # preverimo, da se je vsak predmet pojavil vsaj enkrat
    najdeni = {par: False for par in IZBIRNI_PREDMETI_TUDI_ZA_ISRM}
    for rok in ustrezni_roki:
        for smer in rok.programi:
            par = (rok.predmet.ime, smer.ime)
            if par not in najdeni:
                continue
            else:
                najdeni[par] = True
    izgubljeni = list(filter(lambda p: not najdeni[p], najdeni))
    for par in izgubljeni:
        ZAPISNIKAR.warning(f"Za {par} nismo našli nobenega izpitnega roka.")
