# Najprej iz vseh .ics datotek, ki jih imamo na voljo, oblikujemo ločene
# sezname izpitnih rokov za vsak (program, letnik).
#
# Preverimo, ali so razpisani roki ustrezni (vsaj trije roki na predmet ipd.),
# nato pa zgeneriramo spletno stran.

import os

from izpitni_roki.nalozi_ics import nalozi_ics
from izpitni_roki.naredi_html import naredi_html
from izpitni_roki.glasbene_zelje import prikazi_isrm_roke
from izpitni_roki.preverjanje import preveri_vse
from izpitni_roki.osnovno import niz_v_datum, naredi_zapisnikarja


ZAPISNIKAR = naredi_zapisnikarja(__file__)


def najdi_vse_ics(mapa: str) -> list[str]:
    """
    Najdi vse ics datoteke v dani mapi.

    :param mapa: pot do mape
    :return: seznam vseh ics datotek v mapi
    """
    vse = []
    for dato in os.listdir(mapa):
        pot = os.path.join(mapa, dato)
        if os.path.isfile(pot) and pot.endswith(".ics"):
            vse.append(pot)
    return vse


def preveri_ics_datoteke(ics_datoteke: str | list[str]) -> list[str]:
    if isinstance(ics_datoteke, str):
        # pričakujemo, da je mapa
        if os.path.isdir(ics_datoteke):
            ics_datoteke = najdi_vse_ics(ics_datoteke)
        else:
            ZAPISNIKAR.error(
                "Če je argument ics_datoteke niz, potem mora biti to mapa, "
                f"a mapa {ics_datoteke} ne obstaja."
            )
            exit(1)
    else:
        for datoteka in ics_datoteke:
            if not os.path.exists(datoteka):
                ZAPISNIKAR.error(f"Iskana ics datoteka {datoteka} ne obstaja.")
                exit(2)
    return ics_datoteke


def glavna(
    ics_datoteke: str | list[str],
    naslov_strani: str,
    opis_strani: str,
    obdobja: tuple[tuple[str, str]],
    prazniki: list[str],
    oblika_ics_summary: str | None = None,
    oblika_ics_datum: str | None = None,
):
    # pretvori obdobja
    imena_obdobij = ["zimsko", "spomladansko", "jesensko"]
    obdobja_datumi = tuple((niz_v_datum(d0), niz_v_datum(d1)) for d0, d1 in obdobja)
    slo_obdobja = {ime: datuma for ime, datuma in zip(imena_obdobij, obdobja_datumi)}
    # preveri obstoj ipd. ics datotek
    ics_datoteke = preveri_ics_datoteke(ics_datoteke)
    # preveri skladnost
    vsi_koledarji = [
        nalozi_ics(
            dato,
            obdobja=slo_obdobja,
            oblika_summary=oblika_ics_summary,
            oblika_datum=oblika_ics_datum,
        )
        for dato in ics_datoteke
    ]
    preveri_vse(vsi_koledarji, obdobja, prazniki)
    ali_naj_nadaljujem = input("Nadaljujem s pretvorbo? [j/n] ").lower().strip()
    if ali_naj_nadaljujem.strip().lower() != "j":
        ZAPISNIKAR.info(f"Ker ste vnesli '{ali_naj_nadaljujem}' in ne 'j', končujem")
        exit(0)
    # Ustvari spletno stran iz testnih podatkov
    naredi_html(
        ics_datoteke,
        naslov=naslov_strani,
        opis_strani=opis_strani,
        obdobja=slo_obdobja,
        oblika_summary=None,
        oblika_datum=None,
    )
    ZAPISNIKAR.info("Konec.")


if __name__ == "__main__":
    korenska_mapa = os.path.dirname(os.path.abspath(__file__))
    ics_test = os.path.join(korenska_mapa, "data", "test1.ics")
    # koledar = nalozi_ics(ics_test)

    # Podamo

    # ics datoteke:
    # - lahko kot seznam datotek, npr. ["data/test1.ics", "data/test2.ics"]
    # - lahko kot ime mape, npr. "data"
    vhodne_datoteke = [
        "data/izbrani_izpiti.ics"
    ]  # ["data/test1.ics", "data/test2.ics"]
    # naslov strani
    naslov_strani = (
        "Izpitni roki na Oddelku za matematiko FMF v študijskem letu 2021/22"
    )
    # opis strani: ker je dolg, ga zaradi berljivosti (v .py) prelomimo s pošenico
    opis_strani = "Spodaj so prikazani izpitni roki na programih Finančna matematika (1FiMa), \
        Matematika (1Mate) in Praktična matematika (1PrMa) in \
        prvih treh letnikih programa Pedagoška matematika (2PeMa) \
        na Oddelku za matematiko FMF v študijskem letu 2021/22, ki zadoščajo izbranim kriterijem."
    # uradna izpitna obdobja
    zimsko = ("24. 1. 2024", "16. 2. 2024")
    spomladansko = ("5. 6. 2024", "5. 7. 2024")
    jesensko = ("19. 8. 2024", "13. 9. 2024")
    # praznike in izlete
    prazniki = ["11. 6. 2024", "8. 2. 2024", "25. 6. 2024", "15. 8. 2024"]

    glavna(
        vhodne_datoteke,
        naslov_strani,
        opis_strani,
        (zimsko, spomladansko, jesensko),
        prazniki,
    )

    # Glasbene želje
    # prikazi_isrm_roke(
    #     ["data/1FiMa2223.ics", "data/1Mate2PeMa2223.ics", "data/1PrMa2223.ics"]
    # )
