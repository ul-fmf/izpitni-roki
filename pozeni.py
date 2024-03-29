# Najprej iz vseh .ics datotek, ki jih imamo na voljo, oblikujemo ločene
# sezname izpitnih rokov za vsak (program, letnik).
#
# Preverimo, ali so razpisani roki ustrezni (vsaj trije roki na predmet ipd.),
# nato pa zgeneriramo spletno stran.

import os

from izpitni_roki.nalozi_ics import nalozi_ics
from izpitni_roki.naredi_html import naredi_html, IZHODNA_MAPA
from izpitni_roki.glasbene_zelje import prikazi_isrm_roke
from izpitni_roki.preverjanje import preveri_vse
from izpitni_roki.osnovno import niz_v_datum, naredi_zapisnikarja, preveri_ics_datoteke


ZAPISNIKAR = naredi_zapisnikarja(__file__)


def poskrbi_za_izhodno_mapo():
    if not os.path.exists(IZHODNA_MAPA):
        return
    html_datoteke = []
    for dato in os.listdir(IZHODNA_MAPA):
        if dato.endswith("html"):
            html_datoteke.append(os.path.join(IZHODNA_MAPA, dato))
    if not html_datoteke:
        return
    odgovor = (
        input(
            f"V izhodni mapi ({IZHODNA_MAPA}) sem našel vsaj eno html datoteko.\n"
            f"Če nadaljujete, jo bom izbrisal. Želite nadaljevati? (j/n) "
        )
        .strip()
        .lower()
    )
    if odgovor == "j":
        for dato in html_datoteke:
            ZAPISNIKAR.info(f"Odstranjujem {dato}")
            os.remove(dato)
    else:
        ZAPISNIKAR.info("Niste dali soglasja za nadaljevanje. Prekinjamo izvedbo.")
        exit(0)





def glavna(
    ics_datoteke: str | list[str],
    naslov_strani: str,
    opis_strani: str,
    ime_html: str,
    obdobja: tuple[tuple[str, str]],
    prazniki: list[str],
    oblika_ics_summary: str | None = None,
    oblika_ics_datum: str | None = None,
):
    """
    Preveri ustreznost razpisanih rokov in zgenerira html.

    :param ics_datoteke: če je to niz, pričakujemo, da je to ime mape, v kateri
                         se nahajajo ics datoteke, npr. ``data``. Če je to seznam
                         nizov, je to seznam ics datotek, npr.
                         ``["data/test1.ics", "data/test2.ics"]``
    :param naslov_strani: Naslov spletne strani, npr.
                          ``"Izpitni roki na OM FMF v študijskem letu 2021/22"``
    :param opis_strani: Opis strani v zgornjem pravokotniku, npr.
            ``"Spodaj so prikazani izpitni roki na programih ... ki zadoščajo izbranim kriterijem."``
    :param ime_html: ime končne html datoteke (brez končnice html, npr. ``roki_2324``)
    :param obdobja: trojica parov datumov, ki opisujejo zimsko, spomladansko in jesensko obdobje,
                    npr. ``(("24. 1. 2024", "16. 2. 2024"), (...), (...))``
    :param prazniki: seznam datumov, na katere naj ne bo izpitov, npr.
                     ``["11. 6. 2024", "25. 6. 2024", "15. 8. 2024"]``
    :param oblika_ics_summary: glej :func:`izpitni_roki.naredi_html`
    :param oblika_ics_datum: glej :func:`izpitni_roki.naredi_html`
    """
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
        ime_izhodne=ime_html,
        obdobja=slo_obdobja,
        oblika_summary=None,
        oblika_datum=None,
    )
    ZAPISNIKAR.info("Konec.")


if __name__ == "__main__":
    poskrbi_za_izhodno_mapo()
    # Podamo
    leto_zacetka = 2023
    leto_konca = leto_zacetka + 1
    leto = f"{leto_zacetka}/{leto_konca % 100:02}"
    ime_koncne_datoteke = f"izpiti{leto_zacetka % 100:02}{leto_konca % 100:02}"
    # ics datoteke:
    # - lahko kot seznam datotek, npr. ["data/test1.ics", "data/test2.ics"]
    # - lahko kot ime mape, npr. "test_data"
    vhodne_datoteke = "letosnji_data"
    # naslov strani
    naslov_strani = (
        f"Izpitni roki na Oddelku za matematiko FMF v študijskem letu {leto}"
    )
    # opis strani: ker je dolg, ga zaradi berljivosti (v .py) prelomimo s pošenico
    opis_strani = f"Spodaj so prikazani izpitni roki na programih Finančna matematika (1FiMa), \
        Matematika (1Mate) in Praktična matematika (1PrMa) in \
        prvih treh letnikih programa Pedagoška matematika (2PeMa) \
        na Oddelku za matematiko FMF v študijskem letu {leto}, ki zadoščajo izbranim kriterijem."
    # uradna izpitna obdobja
    zimsko = (f"24. 1. {leto_konca}", f"16. 2. {leto_konca}")
    spomladansko = (f"5. 6. {leto_konca}", f"5. 7. {leto_konca}")
    jesensko = (f"19. 8. {leto_konca}", f"13. 9. {leto_konca}")
    # praznike in izlete:
    # - seznam prepovedanih dni v letošnjem letu (trenutno prazen),
    # - seznam prepovedanih dni v naslednjem letu (25. junij ipd.)
    prazniki = [f"{datum} {leto_zacetka}" for datum in []]
    prazniki += [
        f"{datum} {leto_konca}" for datum in ["11. 6.", "8. 2.", "25. 6.", "15. 8."]
    ]

    glavna(
        vhodne_datoteke,
        naslov_strani,
        opis_strani,
        ime_koncne_datoteke,
        (zimsko, spomladansko, jesensko),
        prazniki,
    )

    # Glasbene želje
    prikazi_isrm_roke(vhodne_datoteke)
