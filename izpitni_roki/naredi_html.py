import os
import re
from izpitni_roki.osnovno import (
    naredi_zapisnikarja,
    IzpitniRok,
    Koledar,
    HtmlPredloga,
    IDTerIme
)
from izpitni_roki.nalozi_ics import nalozi_ics
from typing import List, Callable, Dict, Tuple, Optional
from datetime import datetime


ZAPISNIKAR = naredi_zapisnikarja(__file__)
CRKE = "ABCČDEFGHIJKLMNOPRSŠTUVZŽ"
IZDODNA_MAPA = "out"


def nalozi_predmete_za_zduzevanje() -> Dict[str, List[str]]:
    """
    Naloži datoteko, ki opisuje, katere predmete je treba združiti. Izkaže se, da ni važno,
    ali je predmet voden ločeno ali ne, mi samo združimo :)

    :return: slovar, ki ima za ključe imena predmetov, in za vrednosti imena programov
    """
    predmet_smeri = {}
    datoteka = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "zdruzi.txt"
    )
    with open(datoteka, encoding="utf-8") as f:
        for vrsta in f:
            i = vrsta.find(",")
            predmet = vrsta[:i].strip()
            smeri = re.split(",| ?in ?", vrsta[i + 1:])
            assert predmet not in predmet_smeri
            predmet_smeri[predmet] = [smer.strip() for smer in smeri]
    return predmet_smeri


def zdruzi_roke(izpitni_roki: List[IzpitniRok]) -> List[IzpitniRok]:
    """
    Združi izpitne roke pri predmetih, ki se pojavijo v več programih.

    :param izpitni_roki: seznam ločenih rokov

    :return: seznam združenih rokov

    """
    def je_za_zdruzitev(izpit: IzpitniRok):
        ime_predmeta = izpit.predmet.ime
        if ime_predmeta not in predmeti_zdruzevanja:
            return False
        for program in izpit.programi:
            if program.ime not in predmeti_zdruzevanja[ime_predmeta]:
                return False
        return True

    predmeti_zdruzevanja = nalozi_predmete_za_zduzevanje()
    koncni_roki = []
    zdruzevani_predmeti: Dict[str, Dict[str, List[IzpitniRok]]] = {
        predmet: {} for predmet in predmeti_zdruzevanja
    }
    for izpitni_rok in izpitni_roki:
        if je_za_zdruzitev(izpitni_rok):
            ime = izpitni_rok.predmet.ime
            rok = izpitni_rok.rok.ime
            if rok not in zdruzevani_predmeti[ime]:
                zdruzevani_predmeti[ime][rok] = []
            zdruzevani_predmeti[ime][rok].append(izpitni_rok)
        else:
            koncni_roki.append(izpitni_rok)
    for rok_skupina in zdruzevani_predmeti.values():
        for skupina in rok_skupina.values():
            izpitni_rok = skupina[0]
            for se_en_rok in skupina[1:]:
                izpitni_rok = IzpitniRok.zdruzi_roka(izpitni_rok, se_en_rok)
            koncni_roki.append(izpitni_rok)
    return koncni_roki


def najdi_vse(
        koledarji: List[Koledar],
        izvleckar: Callable[[IzpitniRok], List[IDTerIme]]
) -> List[IDTerIme]:
    """
    Najde vse prisotne vrednosti danega polja izpitnega roka.

    :param koledarji: seznam objektov Koledar
    :param izvleckar: funkcija, ki iz objekta IzpitniRok izvčleče vrednost željenega polja,
        in ga vrne kot objekt IDTerIme

    :return: urejen seznam prisotnih vrednosti (brez ponovitev), ki smo jih izvlekli. Seznam
        je urejen glede na urejenost podrazreda IDTerIme.
    """
    izvlecki = map(izvleckar, [rok for koledar in koledarji for rok in koledar.izpitni_roki])
    vrednosti = set(vrednost for izvlecek in izvlecki for vrednost in izvlecek)
    return sorted(vrednosti)


def najdi_vse_programe(koledarji: List[Koledar]) -> List[IDTerIme]:
    """
    Najdemo vse programe, ki se pojavijo v izpiznih rokih v koledarju.

    :param koledarji: seznam koledarjev

    :return: (urejeni) programi (brez ponovitev)
    """
    return najdi_vse(koledarji, lambda rok: rok.programi)


def najdi_vse_letnike(koledarji: List[Koledar]) -> List[IDTerIme]:
    """
    Najdemo vse letnike, ki se pojavijo v izpiznih rokih v koledarju.

    :param koledarji: seznam koledarjev

    :return: (urejeni) letniki (brez ponovitev)
    """
    return najdi_vse(koledarji, lambda rok: rok.letniki)


def najdi_vse_roke(koledarji: List[Koledar]) -> List[IDTerIme]:
    """
    Najdemo vse roke (1., 2., ...), ki se pojavijo v izpiznih rokih v koledarju.

    :param koledarji: seznam rokov

    :return: (urejeni) roki (brez ponovitev)
    """
    return najdi_vse(koledarji, lambda rok: [rok.rok])


def najdi_vse_izvajalce(koledarji: List[Koledar]) -> List[IDTerIme]:
    """
    Najdemo vse izvajalce, ki se pojavijo v izpiznih rokih v koledarju.

    :param koledarji: seznam izvajalcev

    :return: (urejeni) izvajalci (brez ponovitev)
    """
    return najdi_vse(koledarji, lambda rok: rok.izvajalci)


def najdi_vse_predmete(koledarji: List[Koledar]) -> List[IDTerIme]:
    """
    Najdemo vse predmete, ki se pojavijo v izpiznih rokih v koledarju.

    :param koledarji: seznam predmetov

    :return: (urejeni) predmeti (brez ponovitev)
    """
    return najdi_vse(koledarji, lambda rok: [rok.predmet])


def najdi_vsa_obdobja(koledarji: List[Koledar]) -> List[IDTerIme]:
    """
    Najdemo vsa obdobja, ki se pojavijo v izpiznih rokih v koledarju.

    :param koledarji: seznam obdobij

    :return: (urejena) obdobja (brez ponovitev)
    """
    return najdi_vse(koledarji, lambda rok: [rok.obdobje])


def naredi_spustni_meni_po_crkah(
        ime_menija: str,
        html_razred: str,
        moznosti: List[IDTerIme]
) -> str:
    """
    Naredi dvonivojski spustni meni.

    :param ime_menija: napis na gumbu
    :param html_razred: razred, ki ga dodatmo v ``class`` atribut vseh možnosti
    :param moznosti: Urejen seznam moznosti.

    :return: str(html predloga za dvonivojski spustni meni)
    """
    skupine: List[List[IDTerIme]] = [[] for _ in CRKE]
    for moznost in moznosti:
        ime_skupine = moznost[0].upper()
        skupine[CRKE.index(ime_skupine)].append(moznost)
    elementi_nivo1 = []
    for crka, skupina in zip(CRKE, skupine):
        if not skupina:
            continue
        elementi_nivo2 = []
        for moznost in skupina:
            element = HtmlPredloga(
                "spustni_spustni_nivo2",
                razred=html_razred,
                besedilo=str(moznost),
                id=moznost.id
            )
            elementi_nivo2.append(str(element))
        elementi_nivo1.append(
            str(
                HtmlPredloga(
                    "spustni_spustni_nivo1",
                    ime_skupine=crka,
                    moznosti="\n".join(elementi_nivo2),
                    razred=html_razred
                )
            )
        )
    return str(
        HtmlPredloga(
            "spustni_spustni",
            ime_menija=ime_menija,
            razred=html_razred,
            skupine="\n".join(elementi_nivo1),
            vse=moznosti[0].vse_vsa()
        )
    )


def naredi_spustni_meni(ime_menija: str, html_razred: str, moznosti: List[IDTerIme]) -> str:
    """
    Naredi enonivojski spustni meni.

    :param ime_menija: napis na gumbu
    :param html_razred: razred, ki ga dodatmo v ``class`` atribut vseh možnosti
    :param moznosti: Urejen seznam moznosti.

    :return: str(html predloga enonivojski spustni meni)
    """
    elementi_nivo2 = []
    for moznost in moznosti:
        element = HtmlPredloga(
            "spustni_spustni_nivo2",
            razred=html_razred,
            besedilo=moznost.ime,
            id=moznost.id
        )
        elementi_nivo2.append(str(element))
    return str(
        HtmlPredloga(
            "spustni_spustni",
            ime_menija=ime_menija,
            razred=html_razred,
            skupine="\n".join(elementi_nivo2),
            vse=moznosti[0].vse_vsa()
        )
    )


def naredi_tabelo(koledarji: List[Koledar]) -> str:
    """
    Html koda za tabelo vseh izpitnih rokov

    :param koledarji: seznam objektov Koledar

    :return: str(html predloga za tabelo)
    """
    izpitni_roki = [rok for koledar in koledarji for rok in koledar.izpitni_roki]
    izpitni_roki = zdruzi_roke(izpitni_roki)
    izpitni_roki.sort()
    vrstice = []
    for izpitni_rok in izpitni_roki:
        vrstice.append(
            str(HtmlPredloga(
                "tabela_vrstica",
                id=izpitni_rok.id(),
                datum=izpitni_rok.prikazi_datum(),
                predmet=str(izpitni_rok.predmet),
                letnik=izpitni_rok.prikazi_smer_in_letnik(),
                rok=str(izpitni_rok.rok),
                izvajalci=izpitni_rok.prikazi_izvajalce(),
                ics_raw=izpitni_rok.ics_vrstice
            ))
        )
    # ics opis skupnega koledarja bomo naredili iz enega od ics opisov
    # koledarjev, pri čemer bomo ime koledarja zamenjali z generičnim imenom
    return str(
        HtmlPredloga(
            "tabela",
            ics_raw=koledarji[0].prilagodi_ics_opis("Izpitni roki"),
            vrstice="\n".join(vrstice)
        )
    )


def naredi_html(
        poti_do_koledarjev: List[str],
        naslov: str = "Naslov strani",
        opis_strani: str = "Opis strani",
        obdobja: Optional[Dict[str, Tuple[datetime, datetime]]] = None,
        oblika_summary: Optional[str] = None,
        oblika_datum: Optional[str] = None
):
    """
    Naredi celotno spletno stran.

    :param poti_do_koledarjev: seznam poti do .ics datotek, ki vsebujejo izpitne roke
    :param naslov: naslov spletne strani, npr.

        .. code-block:: text

            "Izpitni roki na Oddelku za matematiko FMF v študijskem letu 2022/23"

    :param opis_strani: Kratek opis strani (npr. katere izpitne roke vsebuje), npr.

        .. code-block:: text

            "Spodaj so prikazani izpitni roki na programih Finančna matematika (1FiMa),
            Matematika (1Mate) in Praktična matematika (1PrMa) in prvih treh letnikih programa
            Pedagoška matematika (2PeMa) na Oddelku za matematiko FMF v študijskem letu 2022/23,
            ki zadoščajo izbranim kriterijem."

    :param obdobja: slovar, ki podaja imena in intervale izpitnih obdobij, npr.
        ``{"zimsko izpitno obdobje": (datetime(2022, 1, 15), datetime(2022, 2, 15), ...}``.
        Izpiti, ki ne bodo padli v nobeno od naštetih obdobij, bodo imeli kategorijo
        ``izven izpitnega obdobja``.
    :param oblika_summary: regularni izraz, ki mu zadošča polje ``SUMMARY`` v ics datoteki.
    :param oblika_datum: format datuma (npr. ``%Y%m%D``), ki mu zadošča polje
        ``DTSTART;VALUE=DATE``.

    :return: Ne vrne ničesar, se pa str(predloga za stran) pojavi v izhodni mapi ``out``.
    """

    koledarji = [
        nalozi_ics(pot, obdobja, oblika_summary, oblika_datum) for pot in poti_do_koledarjev
    ]
    vsi_programi = najdi_vse_programe(koledarji)
    vsi_letniki = najdi_vse_letnike(koledarji)
    vsi_roki = najdi_vse_roke(koledarji)
    vsi_izvajalci = najdi_vse_izvajalce(koledarji)
    vsi_predmeti = najdi_vse_predmete(koledarji)
    vsa_obdobja = najdi_vsa_obdobja(koledarji)

    meni_programi = naredi_spustni_meni("Programi", "program", vsi_programi)
    meni_letniki = naredi_spustni_meni("Letniki", "letnik", vsi_letniki)
    meni_obdobja = naredi_spustni_meni("Obdobja", "obdobje", vsa_obdobja)
    meni_predmeti = naredi_spustni_meni_po_crkah("Predmeti", "predmet", vsi_predmeti)
    meni_izvajalci = naredi_spustni_meni_po_crkah("Izvajalci", "izvajalec", vsi_izvajalci)
    meni_roki = naredi_spustni_meni("Roki", "rok", vsi_roki)

    meniji = "\n\n".join(
        [
            meni_programi, meni_letniki, meni_obdobja, meni_predmeti, meni_izvajalci, meni_roki,
            str(HtmlPredloga("prenos"))
         ]
    )
    izpiti = naredi_tabelo(koledarji)

    html_stran = HtmlPredloga(
        "stran",
        naslov=naslov,
        opis_strani=opis_strani,
        spustni_meniji=meniji,
        izpiti=izpiti
    )
    os.makedirs(IZDODNA_MAPA, exist_ok=True)
    with open(os.path.join(IZDODNA_MAPA, "izpitni_roki.html"), "w", encoding="utf-8") as f:
        print(html_stran, file=f)
