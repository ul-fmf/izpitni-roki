# -*- coding: utf-8 -*-

import pandas as pd

import os
import re
from datetime import datetime


# Pomožne funkcije za datume


def niz_v_datum(niz):
    return datetime.strptime(niz, "%d. %m. %Y")


def datum_v_niz(d):
    return d.strftime("%d. %m. %Y")


obvezni_predmeti = {
    "1FiMa": [
        [
            "ALGEBRA 1",
            "ANALIZA 1",
            "ANALIZA 2",
            "DISKRETNE STRUKTURE",
            "MIKROEKONOMIJA",
            "OPTIMIZACIJSKE METODE",
            "PROSEMINAR",
            "RAČUNALNIŠKI PRAKTIKUM",
            "UVOD V PROGRAMIRANJE",
        ],
        [
            "ANALIZA 3",
            "ANALIZA PODATKOV S PROGRAMOM R",
            "DENAR IN FINANCE",
            "FINANČNA MATEMATIKA 1",
            "MAKROEKONOMIJA",
            "NUMERIČNE METODE 1",
            "NUMERIČNE METODE 2",
            "OPERACIJSKE RAZISKAVE",
            "SEMINAR",
            "VERJETNOST 1",
            "VERJETNOST IN STATISTIKA",
        ],
        [
            "DIPLOMSKI SEMINAR",
            "FINANČNI PRAKTIKUM",
            "FINANČNI TRGI IN INŠTITUCIJE",
            "SLUČAJNI PROCESI 1",
            "STATISTIKA 1",
            "TEORIJA IGER",
            "VERJETNOST Z MERO",
        ],
    ],
    "1Mate": [
        [
            "ALGEBRA 1",
            "ANALIZA 1",
            "FIZIKA 1",
            "LOGIKA IN MNOŽICE",
            "RAČUNALNIŠKI PRAKTIKUM",
            "UVOD V PROGRAMIRANJE",
        ],
        [
            "ALGEBRA 2",
            "ANALIZA 2A",
            "ANALIZA 2B",
            "DISKRETNA MATEMATIKA 1",
            "FIZIKA 2",
            "PROGRAMIRANJE 1",
            "SEMINAR",
            "SPLOŠNA TOPOLOGIJA",
        ],
        [
            "ANALIZA 3",
            "ANALIZA 4",
            "DIPLOMSKI SEMINAR",
            "MEHANIKA 1",
            "STATISTIKA",
            "UVOD V NUMERIČNE METODE",
            "VERJETNOST",
        ],
    ],
    "2PeMa": [
        [
            "ALGEBRA 1",
            "ANALIZA 1",
            "FIZIKA 1",
            "LOGIKA IN MNOŽICE",
            "RAČUNALNIŠKI PRAKTIKUM",
            "UVOD V PROGRAMIRANJE",
        ],
        [
            "AFINA IN PROJEKTIVNA GEOMETRIJA ",
            "ALGEBRA 2",
            "ANALIZA 2A",
            "ANALIZA 2B",
            "ASTRONOMIJA",
            "DISKRETNA MATEMATIKA 1",
            "ELEMENTARNA GEOMETRIJA",
            "FIZIKA 2",
            "PROGRAMSKA OPREMA PRI POUKU",
            "SPLOŠNA TOPOLOGIJA",
        ],
        [
            "ANALIZA 3",
            "ASTRONOMIJA",
            "DIDAKTIKA 1",
            "DIDAKTIKA MATEMATIKE 1",
            "DIDAKTIKA MATEMATIKE 2",
            "ELEMENTARNA TEORIJA ŠTEVIL",
            "PEDAGOGIKA Z ANDRAGOGIKO",
            "PEDAGOŠKA PRAKSA 1",
            "PROGRAMSKA OPREMA PRI POUKU",
            "PSIHOLOGIJA UČENJA IN POUKA",
            "SEMINAR 1",
            "STATISTIKA",
            "UVOD V NUMERIČNE METODE",
            "VERJETNOST",
        ],
    ],
    "1PrMa": [
        [
            "LINEARNA ALGEBRA",
            "MATEMATIKA 1",
            "MATEMATIKA V PRAKSI",
            "PROGRAMIRANJE 1",
            "RAČUNALNIŠKA ORODJA V MATEMATIKI",
            "RAČUNALNIŠKI PRAKTIKUM",
            "UVOD V FIZIKO",
        ],
        [
            "ALGEBRA IN DISKRETNA MATEMATIKA",
            "DIFERENCIALNE ENAČBE",
            "FIZIKALNI PRAKTIKUM",
            "KOMUNICIRANJE V MATEMATIKI",
            "MATEMATIČNA ORODJA V FIZIKI",
            "MATEMATIKA 2",
            "NUMERIČNE METODE 1",
            "PROGRAMIRANJE 2",
            "STATISTIKA",
            "VERJETNOST",
        ],
        [
            "MEHANIKA",
            "OPTIMIZACIJA",
            "PARCIALNE DIFERENCIALNE ENAČBE",
            "PODATKOVNE BAZE 1",
            "PRAKTIČNO USPOSABLJANJE",
            "RAČUNALNIŠTVO 1",
        ],
    ],
}


# Podatki
zimsko_zacetek = niz_v_datum("24. 1. 2024")
zimsko_konec = niz_v_datum("16. 2. 2024")
spomladansko_zacetek = niz_v_datum("5. 6. 2024")
spomladansko_konec = niz_v_datum("5. 7. 2024")
jesensko_zacetek = niz_v_datum("19. 8. 2024")
jesensko_konec = niz_v_datum("13. 9. 2024")

# Poleg praznikov je izpitov prost dan tudi 11. 6., ki je rezerviran za izlet.
prazniki = ["11. 6. 2024", "8. 2. 2024", "25. 6. 2024", "15. 8. 2024"]

for program in ["1FiMa", "1Mate", "1PrMa", "2PeMa"]:
    for letnik in range(1, 4):
        print(program, " ", letnik)
        ime_datoteke = program + str(letnik) + ".ics"
        # Procesiraj ics datoteko
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path_to_file = os.path.join(script_dir, ime_datoteke)
        with open(path_to_file, "r") as content_file:
            content = content_file.read()

        zacetek = "BEGIN:VEVENT"
        datum1 = "DTSTART;VALUE=DATE:"
        datum2 = "DTSTART:"
        predmet1 = "SUMMARY:"
        predmet2 = "TRANSP:"
        tokens = content.split(zacetek)
        izpiti_data = []
        for izpit in tokens[1:]:
            if "izpitnega obdobja" not in izpit:
                # Izvleci datum
                pattern = r"(?:" + datum1 + "|" + datum2 + r")(\d{8})"
                match = re.search(pattern, izpit)
                if match:
                    date_string = match.group(1)
                    date = datetime.strptime(date_string, "%Y%m%d")
                    # print(type(date))

                # Izvleči podatke o izpitu
                exam = (
                    izpit[izpit.index(predmet1) + len(predmet1) : izpit.index(predmet2)]
                    .replace("\\", "")
                    .replace("\n ", "")
                )
                pattern = r"^(?P<name>.*?) \((?P<programmes>.*?)\), (?P<professors>.*?), (?P<attempt>\d+\.\srok)$"
                match = re.match(pattern, exam)
                if match:
                    ime = match.group("name")
                    if ime.upper() in obvezni_predmeti[program][letnik - 1]:
                        ime = ime.upper()
                    izpiti_data.append([date, ime])

        # Shrani podatke v pandas dataframe
        df = pd.DataFrame(izpiti_data, columns=["Datum", "Ime"])
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
        # print(df)
        # print(df["Datum"].unique())
        # print(df["Datum"])

        datumi_izpitov = df["Datum"]  # .unique().tolist()

        predmeti = df["Ime"].unique().tolist()

        # print(datumi_izpitov)
        # datumi so v izpitnih obdobjih in ne na izključeni datum

        for datum in datumi_izpitov:
            if not je_v_izpitnem_obdobju(datum):
                print("{} ni v izpitnem obdobju.".format(datum_v_niz(datum)))
            if not je_na_delovni_dan(datum):
                print("{} ni na delovni dan.".format(datum_v_niz(datum)))
            if datum in izkljuceni_datumi:
                print("Na dan {} je vsaj en izpit.".format(datum_v_niz(datum)))

        for predmet in predmeti:
            # je med izpitoma pri istem predmetu vsaj 10 dni
            if not med_izpitoma_vsaj_10_dni(predmet):
                print("Med izpitoma pri predmetu {} ni vsaj 10 dni.".format(predmet))

            # da so pri vsakem predmetu (kjer so pisni izpiti) vsaj trije roki
            if not vsaj_trije_roki_pri_predmetu(predmet):
                print("Pri predmetu {} ni vsaj treh izpitnih rokov.".format(predmet))

        # izpiti na isti dan, kjer je vsaj eden obvezen (obvezne izpiše z veliki tiskanimi črkami)
        datumi_z_vec_izpiti = datumi_izpitov_na_isti_dan()
        if len(datumi_z_vec_izpiti) > 0:
            print("Obstajajo potencialni slabi datumi z več izpiti na ta datum:")
            for d in datumi_z_vec_izpiti:
                if set(df[df["Datum"] == d]["Ime"].unique().tolist()) & set(
                    obvezni_predmeti[program][letnik - 1]
                ):
                    print(
                        "{}: {}".format(
                            datum_v_niz(d),
                            ", ".join(df[df["Datum"] == d]["Ime"].unique().tolist()),
                        )
                    )

        input()
