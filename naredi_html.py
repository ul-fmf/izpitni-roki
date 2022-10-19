import os
from osnovno import create_logger, IzpitniRok, Koledar, HtmlPredloga, IDTerIme
from nalozi_ics import nalozi_ics
from typing import List, Callable


LOGGER = create_logger(__file__)


CRKE = "ABCČDEFGHIJKLMNOPRSŠTUVZŽ"
HTML_MAPA = "out"


def najdi_vse(koledarji: List[Koledar], izvleckar: Callable[[IzpitniRok], List[IDTerIme]]) -> List[IDTerIme]:
    def oblika_za_primerjanje(niz):
        posebni = {"č": "cc", "ć": "ccc", "đ": "dd", "š": "ss", "ž": "zz"}
        return "".join([crka if crka not in posebni else posebni[crka] for crka in niz]).lower()

    izvlecki = map(izvleckar, [rok for koledar in koledarji for rok in koledar.izpitni_roki])
    vrednosti = set(vrednost for izvlecek in izvlecki for vrednost in izvlecek)
    return sorted(vrednosti, key=oblika_za_primerjanje)


def najdi_vse_programe(koledarji: List[Koledar]) -> List[IDTerIme]:
    return najdi_vse(koledarji, lambda rok: rok.programi)


def najdi_vse_letnike(koledarji: List[Koledar]) -> List[IDTerIme]:
    return najdi_vse(koledarji, lambda rok: [rok.letnik])


def najdi_vse_roke(koledarji: List[Koledar]) -> List[IDTerIme]:
    return najdi_vse(koledarji, lambda rok: [rok.rok])


def najdi_vse_izvajalce(koledarji: List[Koledar]) -> List[IDTerIme]:
    return najdi_vse(koledarji, lambda rok: rok.izvajalci)


def najdi_vse_predmete(koledarji: List[Koledar]) -> List[IDTerIme]:
    return najdi_vse(koledarji, lambda rok: [rok.predmet])


def naredi_spustni_meni_po_crkah(ime_menija: str, html_razred: str, moznosti: List[IDTerIme]) -> str:
    """
    Naredi dvonivojski spustni meni.

    :param ime_menija: napis na gumbu
    :param html_razred: razred, ki ga dodatmo v class atribut vseh možnosti
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
                besedilo=moznost.ime,
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
            skupine="\n".join(elementi_nivo1)
        )
    )


def naredi_spustni_meni(ime_menija: str, html_razred: str, moznosti: List[IDTerIme]) -> str:
    """
    Naredi enonivojski spustni meni.

    :param ime_menija: napis na gumbu
    :param html_razred: razred, ki ga dodatmo v class atribut vseh možnosti
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
            skupine="\n".join(elementi_nivo2)
        )
    )


def naredi_tabelo(izpitni_roki: List[IzpitniRok]) -> str:
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
                izvajalci=izpitni_rok.prikazi_izvajalce()
            ))
        )
    return str(HtmlPredloga("tabela", vrstice="\n".join(vrstice)))


def naredi_html(poti_do_urnikov: List[str], naslov: str):
    koledarji = [nalozi_ics(pot) for pot in poti_do_urnikov]
    vsi_programi = najdi_vse_programe(koledarji)
    vsi_letniki = najdi_vse_letnike(koledarji)
    vsi_roki = najdi_vse_roke(koledarji)
    vsi_izvajalci = najdi_vse_izvajalce(koledarji)
    vsi_predmeti = najdi_vse_predmete(koledarji)

    meni_programi = naredi_spustni_meni("Programi", "program", vsi_programi)
    meni_letniki = naredi_spustni_meni("Letniki", "letnik", vsi_letniki)
    meni_roki = naredi_spustni_meni("Roki", "rok", vsi_roki)
    meni_izvajalci = naredi_spustni_meni_po_crkah("Izvajalci", "izvajalec", vsi_izvajalci)
    meni_predmeti = naredi_spustni_meni_po_crkah("Predmeti", "predmet", vsi_predmeti)

    meniji = "\n\n".join(
        [meni_programi, meni_letniki, meni_roki, meni_izvajalci, meni_predmeti]
    )
    izpiti = naredi_tabelo([rok for koledar in koledarji for rok in koledar.izpitni_roki])

    html_stran = HtmlPredloga("stran", naslov=naslov, spustni_meniji=meniji, izpiti=izpiti)
    with open("out/izpitni_roki.html", "w", encoding="utf-8") as f:
        print(html_stran, file=f)


if __name__ == "__main__":
    naredi_html(
        ["data/test.ics", "data/1FiMa2122.ics", "data/1Mate2PeMa2122.ics"][:1],
        "Izpiti 2022/2023"
    )


