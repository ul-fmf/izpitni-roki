from typing import List, Optional, Dict, Tuple
from datetime import datetime
import re
import os
from osnovno import (
    naredi_zapisnikarja,
    IzpitniRok,
    Koledar,
    Predmet,
    Program,
    Letnik,
    Rok,
    Izvajalec,
    IDTerIme
)


LOGGER = naredi_zapisnikarja(__file__)


def preberi_vrednosti(vrstice: List[str], nujni_kljuci: List[str]) -> Tuple[Dict[str, str], str]:
    kljucne_besede = [
        # dogodek
        "DTSTART;VALUE=DATE", "DTEND;VALUE=DATE", "DTSTAMP",
        "UID", "CREATED", "DESCRIPTION", "LAST-MODIFIED", "LOCATION",
        "SEQUENCE", "STATUS", "SUMMARY", "TRANSP",
        # koledar
        "PRODID", "VERSION", "CALSCALE", "METHOD", "X-WR-CALNAME",
        "X-WR-TIMEZONE"
    ]
    pari = {}
    zadnja = ""
    ics_raw = []
    for vrsta in vrstice:
        ics_raw.append(vrsta)
        if any(vrsta.startswith((zacetek := kljucna)) for kljucna in kljucne_besede):
            zadnja = zacetek
            pari[zadnja] = vrsta[len(zacetek) + 1:]
        elif re.match("^[A-Z]+:.+$", vrsta) is not None:
            LOGGER.warning(f"Neznana ključna beseda v vrstici {vrsta}, ignoriram")
            zadnja = ""
        elif zadnja:
            # prelom originalne vrste: se začne s presledkom
            assert vrsta[0] == " ", vrsta
            pari[zadnja] += vrsta[1:]
    for nujen in nujni_kljuci:
        if nujen not in pari:
            raise ValueError(f"Ključ {nujen} manjka v {vrstice}")
    return {n: pari[n] for n in nujni_kljuci}, "\n".join(ics_raw)


def sprocesiraj_dogodek(vrstice: List[str]) -> IzpitniRok:
    """
    Iz vrstic dogodka ustvari izpitni rok.

    Branje je bolj kot ne neposredno, le s poljem SUMMARY je nekaj dela, saj je njegova oblika
    npr.<br>
    "Uvod v programiranje (1Mate\\, 2PeMa\\, ni smeri)\\, prvi letnik\\,
    Prisojnik Matjaž\\, Perko Martin\\, Pletna Marija\\, 3. rok"<br>

    :param vrstice:
    :return:
    """
    def razbij_na_dele(niz: str, prepovedano=None):
        if prepovedano is None:
            prepovedano = []
        return list(
            filter(
                lambda delcek: delcek not in prepovedano and delcek,
                map(lambda kos: kos.strip(), niz.split("\\,"))
            )
        )
    zacetek = "DTSTART;VALUE=DATE"
    povzetek = "SUMMARY"
    vrednosti, ics_raw = preberi_vrednosti(vrstice, [zacetek, povzetek])
    datum = datetime.strptime(vrednosti[zacetek], "%Y%m%d")
    pricakovana_oblika = r"^(?P<predmet>[^(]+)\((?P<smeri>[^)]+)\)\\, ?" \
                         r"(?P<letnik>[^ ]+) letnik\\, " \
                         r"?(?P<izvajalci>([^\\]+\\, ?)+)" \
                         r"(?P<rok>\d+\.) rok ?$"
    izpit = re.match(pricakovana_oblika, vrednosti[povzetek])
    if izpit is None:
        raise ValueError(f"'{vrednosti[povzetek]}' ni izraz oblike {pricakovana_oblika}")
    predmet = izpit.group("predmet").strip()
    smeri = razbij_na_dele(izpit.group("smeri"), prepovedano=["ni smeri"])
    letnik = izpit.group("letnik")
    izvajalci = razbij_na_dele(izpit.group("izvajalci"))
    rok = izpit.group("rok")

    izpitni_rok = IzpitniRok(
        datum,
        IDTerIme.naredi_objekt(Predmet, predmet),
        [IDTerIme.naredi_objekt(Program, smer) for smer in smeri],
        IDTerIme.naredi_objekt(Letnik, letnik),
        IDTerIme.naredi_objekt(Rok, rok),
        [IDTerIme.naredi_objekt(Izvajalec, izvajalec) for izvajalec in izvajalci],
        "BEGIN:VEVENT\n" + ics_raw + "\nEND:VEVENT"
    )
    izpitni_rok.preveri()
    return izpitni_rok


def naredi_koledar(meta_vrstice_koledarja: List[str], izpitni_roki: List[IzpitniRok]) -> Koledar:
    """
    Iz meta-opisa koledarja prebere smer, doda še izpitne roke in ustvari nov objekt Koledar
    :param meta_vrstice_koledarja: vrstice v koledarju, ki niso del dogodka
    :param izpitni_roki: izpitni roki, ki smo jih prebrali iz dane ics datoteke
    :return: koledar z izpitnimi roki za dano smer
    """
    polje_smer = "X-WR-CALNAME"
    vrednosti, ics_vrstice = preberi_vrednosti(meta_vrstice_koledarja, [polje_smer])
    smer = vrednosti[polje_smer]
    return Koledar(smer, izpitni_roki, ics_vrstice)


def nalozi_ics(pot: str) -> Koledar:
    """
    Pričakovana oblika datoteke je

    BEGIN:VCALENDAR
    PRODID:-//Google Inc//Google Calendar 70.9054//EN
    VERSION:2.0
    CALSCALE:GREGORIAN
    METHOD:PUBLISH
    X-WR-CALNAME:Finančna matematika 2021/22
    X-WR-TIMEZONE:Europe/Belgrade
    [dogodki]
    END:VCALENDAR

    kjer so dogodki oblike

    BEGIN:VEVENT
    DTSTART;VALUE=DATE:20220629
    DTEND;VALUE=DATE:20220630
    DTSTAMP:20220209T150954Z
    UID:fdsfsdfsdfsd@google.com
    CREATED:20210325T080359Z
    DESCRIPTION:
    LAST-MODIFIED:20210913T125706Z
    LOCATION: morda kaj, a ni pomembno
    SEQUENCE:4
    STATUS:CONFIRMED
    SUMMARY:Uvod v programiranje (1Mate\\, 2PeMa\\, ni smeri)\\, prvi letnik\\, Pris
        ojnik Matjaž\\, Perko Martin\\, Pletna Marija\\, 3. rok
    TRANSP:TRANSPARENT
    END:VEVENT

    :param pot: pot do ics datoteke
    :return:
    """
    v_koledarju = False
    v_dogodku = False
    vrstice_koledarja = []
    vrstice_dogodka = []
    izpiti: List[IzpitniRok] = []
    koledar: Optional[Koledar] = None
    n_rokov = 0
    with open(pot, encoding="utf-8") as f:
        for vrsta in f:
            if vrsta.startswith("BEGIN:VEVENT"):
                v_dogodku = True
                n_rokov += 1
            elif vrsta.startswith("END:VEVENT"):
                izpiti.append(sprocesiraj_dogodek(vrstice_dogodka))
                vrstice_dogodka = []
                v_dogodku = False
            elif vrsta.startswith("BEGIN:VCALENDAR"):
                v_koledarju = True
            elif vrsta.startswith("END:VCALENDAR"):
                koledar = naredi_koledar(vrstice_koledarja, izpiti)
                v_koledarju = False
            elif v_dogodku:
                vrstice_dogodka.append(vrsta.replace("\n", ""))
            elif v_koledarju:  # mora biti za dogodkom
                vrstice_koledarja.append(vrsta.replace("\n", ""))
    if koledar is None:
        raise ValueError(f"Koledar ni bil ustvarjen pri branu iz {pot}")
    elif len(koledar.izpitni_roki) != n_rokov:
        raise ValueError(
            f"Število prebranih rokov ({len(koledar.izpitni_roki)}) se "
            f"ne ujema s številom rokov v datoteki ({n_rokov})."
        )
    return koledar


def test_nalozi_ics():
    testni_izpiti = ["1FiMa2122", "1Mate2PeMa2122", "1PrMa2122"]
    for izpiti in testni_izpiti:
        _ = nalozi_ics(os.path.join("data", f"{izpiti}.ics"))
        print("Prebral", izpiti)


if __name__ == "__main__":
    test_nalozi_ics()
