# -*- coding: utf-8 -*-

import pandas as pd

import os
import re
import json

from izpitni_roki.osnovno import (
    IzpitniRok,
    datum_v_niz,
    naredi_zapisnikarja,
    Koledar,
    Letnik,
    niz_v_datum,
)


ZAPISNIKAR = naredi_zapisnikarja(__file__)


def nalozi_obvezne_predmete():
    ta_mapa = os.path.dirname(os.path.abspath(__file__))
    pot = os.path.join(ta_mapa, "obvezni_predmeti.json")
    with open(pot, encoding="utf-8") as f:
        obvezni_predmeti = json.load(f)
    return obvezni_predmeti


OBVEZNI_PREDMETI = nalozi_obvezne_predmete()


def razbij_po_program_letnikih(
    izpitni_roki: list[IzpitniRok],
) -> dict[tuple[str, int], list[IzpitniRok]]:
    """
    Razbije dane roke glede na program-letnik.

    :param izpitni_roki: izpitni roki vseh letnikov in programov
    :return: slovar koledarjev ``{ime1: roki1, ...}``, katerega ključi so imena
             program-letnikov (npr. ``1FiMa - 1. letnik``), vrednosti pa seznami
             izpitnih rokov, ki vsebujejo le izpite za dani program-letnik.
    """
    koledarji = {}
    for izpitni_rok in izpitni_roki:
        for program, letnik in zip(izpitni_rok.programi, izpitni_rok.letniki):
            program_letnik = (program.ime, Letnik.DOVOLJENI_LETNIKI[letnik.ime])
            if program_letnik not in koledarji:
                koledarji[program_letnik] = []
            koledarji[program_letnik].append(izpitni_rok)
    return koledarji


def preveri_predmet_letnik(
    program: str,
    letnik: int,
    izpitni_roki: list[IzpitniRok],
    obdobja: tuple[tuple[str, str], tuple[str, str], tuple[str, str]],
    prazniki: list[str],
):
    """
    Preveri, ali so razpisani roki za dani letnik (danega programa)
    skladni s pravili.

    :param program: npr. ``"1FiMa"``
    :param letnik: 1, 2, 3, 4 ali 5
    :param izpitni_roki: razpisani roki danega program-letnika
    :param obdobja: trojica intervalov, ki podaja zimsko, spomladansko in jesensko
                    izpitno obdobje. Vsak interval je podan s paroma datumov, npr.
                    ``("24. 1. 2024", "16. 2. 2024")``
    :param prazniki: seznam datumov (kot nizov, npr. ``25. 6. 2023``), na katere naj
                     ne bo izpitov
    :return: ne vrne ničesar, le izpiše opozorila, če so ta potrebna, sicer pa obvesti,
             da je vse v redu.
    """
    zimsko, spomladansko, jesensko = obdobja
    zimsko_zacetek, zimsko_konec = map(niz_v_datum, zimsko)
    spomladansko_zacetek, spomladansko_konec = map(niz_v_datum, spomladansko)
    jesensko_zacetek, jesensko_konec = map(niz_v_datum, jesensko)

    ZAPISNIKAR.info(f"Preverjam {program} ({letnik}. letnik)")
    opozorila = []
    # Shrani podatke v pandas dataframe
    datumi_imena = [[rok.datum, rok.predmet.ime] for rok in izpitni_roki]
    for i, (_, ime_predmeta) in enumerate(datumi_imena):
        if ime_predmeta.upper() in OBVEZNI_PREDMETI[program][letnik - 1]:
            datumi_imena[i][1] = ime_predmeta.upper()
    df = pd.DataFrame(datumi_imena, columns=["Datum", "Ime"])
    df = df.sort_values(by=["Datum", "Ime"])

    # Pomožne funkcije za pravilnost izpitov
    def je_v_izpitnem_obdobju(datum):
        return (
            zimsko_zacetek <= datum <= zimsko_konec
            or spomladansko_zacetek <= datum <= spomladansko_konec
            or jesensko_zacetek <= datum <= jesensko_konec
        )

    def je_na_delovni_dan(datum):
        return datum.weekday() <= 4

    # Pomembno je, da:
    # - je med izpitoma pri istem predmetu vsaj 10 dni

    def med_izpitoma_vsaj_10_dni(predmet):
        izpiti_pri_predmetu = df[df["Ime"] == predmet]
        datumi_izpitov = izpiti_pri_predmetu["Datum"]
        razlike_datumov = datumi_izpitov.diff().dropna()
        has_less_than_10_days_between = any(razlike_datumov.dt.days < 10)
        return not (has_less_than_10_days_between)

    # - da so pri vsakem predmetu (kjer so pisni izpiti) vsaj trije roki

    def vsaj_trije_roki_pri_predmetu(predmet):
        izpiti_pri_predmetu = df[df["Ime"] == predmet]
        return len(izpiti_pri_predmetu) >= 3

    # - da poleg obveznega predmeta ni drugih izpitov (obveznih ali izbirnih
    # predmetov) na isti dan, razen v jesenskem izpitnem obdobju, ko se tega
    # ne moremo držati; v jesenskem izpitnem obdobju naj ne bi bila na isti
    # dan izpita pri dveh obveznih predmetih

    def datumi_izpitov_na_isti_dan():
        stevec_izpitov = df.groupby("Datum").size()
        slabi_datumi = stevec_izpitov[stevec_izpitov >= 2].index.tolist()
        return sorted(set(slabi_datumi))

    izkljuceni_datumi = [niz_v_datum(d) for d in prazniki]

    # Končno preverimo veljavnost rokov

    datumi_izpitov = df["Datum"]  # .unique().tolist()
    predmeti = df["Ime"].unique().tolist()

    # datumi so v izpitnih obdobjih in ne na izključeni datum
    for datum in datumi_izpitov:
        d_str = datum_v_niz(datum)
        if not je_v_izpitnem_obdobju(datum):
            opozorila.append(f"{d_str} ni v izpitnem obdobju.")
        if not je_na_delovni_dan(datum):
            opozorila.append(f"{d_str} ni na delovni dan.")
        if datum in izkljuceni_datumi:
            opozorila.append(f"Na dan {d_str} je vsaj en izpit.")

    for predmet in predmeti:
        # je med izpitoma pri istem predmetu vsaj 10 dni
        if not med_izpitoma_vsaj_10_dni(predmet):
            opozorila.append(f"Med izpitoma pri predmetu {predmet} ni vsaj 10 dni.")

        # da so pri vsakem predmetu (kjer so pisni izpiti) vsaj trije roki
        if not vsaj_trije_roki_pri_predmetu(predmet):
            opozorila.append(f"Pri predmetu {predmet} ni vsaj treh izpitnih rokov.")

    # izpiti na isti dan, kjer je vsaj eden obvezen (obvezne izpiše z veliki tiskanimi črkami)
    datumi_z_vec_izpiti = datumi_izpitov_na_isti_dan()
    if len(datumi_z_vec_izpiti) > 0:
        vrstice = ["Obstajajo potencialni slabi datumi z več izpiti na ta datum:"]
        for d in datumi_z_vec_izpiti:
            if set(df[df["Datum"] == d]["Ime"].unique().tolist()) & set(
                OBVEZNI_PREDMETI[program][letnik - 1]
            ):
                d_str = datum_v_niz(d)
                imena = ", ".join(df[df["Datum"] == d]["Ime"].unique().tolist())
                vrstice.append(f"{d_str}: {imena}")
        opozorila.append("\n".join(vrstice))
    if opozorila:
        zdruzene_napake = "\n".join(opozorila)
        ZAPISNIKAR.warning(f"Pojavile so se naslednje napake:\n{zdruzene_napake}")
    else:
        ZAPISNIKAR.info("Brez napak.")


def preveri_vse(
    koledarji: list[Koledar],
    obdobja: tuple[tuple[str, str], tuple[str, str], tuple[str, str]],
    prazniki: list[str],
):
    """
    Preveri vse izpitne roke, tako da razbije dane koledarje na
    program-letnike in pokliče :func:`razbij_po_program_letnikih`
    na vseh.
    """
    for koledar in koledarji:
        razbito = razbij_po_program_letnikih(koledar.izpitni_roki)
        for (program, letnik), roki in razbito.items():
            preveri_predmet_letnik(program, letnik, roki, obdobja, prazniki)
            print()
