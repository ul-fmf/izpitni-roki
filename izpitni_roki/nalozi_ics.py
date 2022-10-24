from typing import List, Optional, Dict, Tuple
from datetime import datetime
from collections import Counter
import re
from izpitni_roki.osnovno import (
    naredi_zapisnikarja,
    IzpitniRok,
    Koledar,
    Predmet,
    Program,
    Letnik,
    Rok,
    Obdobje,
    Izvajalec,
    IDTerIme
)

OBLIKA_SUMMARY = r"^(?P<predmet>[^(]+)\((?P<smeri>[^)]+)\)\\, ?" \
                 r"(?P<letnik>[^ ]+) letnik\\, " \
                 r"?(?P<izvajalci>([^\\]+\\, ?)+)" \
                 r"(?P<rok>\d+\.) rok ?$"
OBLIKA_DATUM = "%Y%m%d"


def doloci_leto(pot: str, oblika_datuma: Optional[str] = None) -> int:
    oblika_datuma = OBLIKA_DATUM if oblika_datuma is None else oblika_datuma
    leta = []
    kljuc = "DTSTART;VALUE=DATE:"
    with open(pot, encoding="utf-8") as f:
        for vrsta in f:
            if vrsta.startswith(kljuc):
                datum = datetime.strptime(vrsta[len(kljuc):-1], oblika_datuma)
                leta.append(datum.year)
    return Counter(leta).most_common(1)[0][0]


def naredi_izpitna_obdobja(leto: int) -> Dict[str, Tuple[datetime, datetime]]:
    """
    Naredi osnovna izpitna obdobja, ki jih uporabimo, če niso podana ročno.

    :param leto: leto, za katerega delamo izpitna obdobja, npr. 2022
    :return: Vrnemo slovar, ki pravi, da je zimsko januarja in februarja,
        spomladansko junija in julija, ter jesensko avgusta in septembra:

        .. code-block:: python

            {
               "zimsko": (datetime(leto, 1, 1), zadnji_februar),
               "spomladansko": (datetime(leto, 6, 1), datetime(leto, 7, 31)),
               "jesensko": (datetime(leto, 8, 1), datetime(leto, 9, 30))
            }

    """
    je_prestopno = leto % 4 == 0 and (leto % 100 != 0 or leto % 400 == 0)
    zadnji_februar = datetime(leto, 2, 28 + int(je_prestopno))
    return {
        "zimsko": (datetime(leto, 1, 1), zadnji_februar),
        "spomladansko": (datetime(leto, 6, 1), datetime(2022, 7, 31)),
        "jesensko": (datetime(leto, 8, 1), datetime(leto, 9, 30))
    }


ZAPISNIKAR = naredi_zapisnikarja(__file__)


def preberi_vrednosti(vrstice: List[str], nujni_kljuci: List[str]) -> Tuple[Dict[str, str], str]:
    """
    Vrstice, ki opisujejo dogodek (izpitni rok) ali pa koledar predela tako, da odstrani
        morebitne prelome vrstic in jih združi v slovar {kljuc: vrednost, ...}, kjer so ključi
        ključne besede iz .ics formata, npr. ``DTSTART;VALUE=DATE`` ali ``X-WR-TIMEZONE``.

    :param vrstice: zaporedne vrstice iz ics datoteke, ki opisujejo dogodek ali koledar.
        Seznam ne vsebuje ne začetne vrstice (BEGIN:VCALENDAR ali BEGIN:VEVENT) ne končne
        vrstice (END:VCALENDAR ali END:VEVENT).
    :param nujni_kljuci: ključi, ki jih nujno potrebujemo, da bi lahko kasneje ustvarili
        IzpitniRok ali Koledar

    :return: par (slovar, združene vrstice), kjer slovar podaja pare
        ključna beseda iz ics: pripadajoča vrednost (v pripadajoči vrednosti so
        bili odstranjeni prelomi vrstic), združene vrstice pa so dobljene
        kot ``"\\n".join(vrstice)``.
    """
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
    for vrsta in vrstice:
        if any(vrsta.startswith((zacetek := kljucna)) for kljucna in kljucne_besede):
            zadnja = zacetek
            pari[zadnja] = vrsta[len(zacetek) + 1:]
        elif re.match("^[A-Z]+:.+$", vrsta) is not None:
            ZAPISNIKAR.warning(f"Neznana ključna beseda v vrstici {vrsta}, ignoriram")
            zadnja = ""
        elif zadnja:
            # prelom originalne vrste: se začne s presledkom
            assert vrsta[0] == " ", vrsta
            pari[zadnja] += vrsta[1:]
    for nujen in nujni_kljuci:
        if nujen not in pari:
            raise ValueError(f"Ključ {nujen} manjka v {vrstice}")
    return {n: pari[n] for n in nujni_kljuci}, "\n".join(vrstice)


def sprocesiraj_dogodek(
        vrstice: List[str],
        obdobja: List[Obdobje],
        oblika_summary: Optional[str],
        oblika_datum: Optional[str]
) -> IzpitniRok:
    """
    Iz vrstic dogodka ustvari izpitni rok.

    Branje je bolj kot ne neposredno, le s poljem ``SUMMARY`` je nekaj dela, saj je njegova
    vsebina npr.

    .. code-block:: text

        Uvod v junaštva (Smer1\, Smer2\, Smer3)\, prvi letnik\,
         Klepec Peter\, Krpan Martin\, Kekec Kekec\, 3. rok

    (prelom za vejico smo dodali zaradi berljivosti: sledi ji presledek v naslednji vrsti).

    Če oblika datumov (pri ``DTSTART;VALUE=DATE``) ni ``%Y%m%d``
    (npr. ``20231225`` za 25. 12. 2023), jo je treba podati.

    :param vrstice: surove vrstice, kot jih preberemo v ics datoteki. Opisujejo
        koledar ali dogodek, v njih nista prisotna začena in končna vrstica
        (``[BEGIN oz. END]:VEVENT``). Nujno morata biti v njih prisotna ključa
        ``SUMARY`` in ``DTSTART;VALUE=DATE``.
    :param obdobja: seznam izpitnih obdobij
    :param oblika_summary: regularni izraz, ki mu zadošča vrednost polja ``SUMMARY``.
        Vsebovati mora iste poimenovane skupine, kot jih (prednastavljeni)

        .. code-block:: python

            r"^(?P<predmet>[^(]+)\((?P<smeri>[^)]+)\)\\, ?" \\
            r"(?P<letnik>[^ ]+) letnik\\, " \\
            r"?(?P<izvajalci>([^\\]+\\, ?)+)" \\
            r"(?P<rok>\d+\.) rok ?$"

    :param oblika_datum: pythonov format za datum, npr. ``%Y%m%d``

    :return: IzpitniRok, ki ga opisujejo vrstice

    :raises: ValueError če ``SUMMARY`` dogodka ni predpisane oblike.

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
    if oblika_summary is None:
        pricakovana_oblika = OBLIKA_SUMMARY
    else:
        pricakovana_oblika = oblika_summary
    if oblika_datum is None:
        oblika_datum = OBLIKA_DATUM

    zacetek = "DTSTART;VALUE=DATE"
    povzetek = "SUMMARY"
    vrednosti, ics_raw = preberi_vrednosti(vrstice, [zacetek, povzetek])
    datum = datetime.strptime(vrednosti[zacetek], oblika_datum)

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
        Obdobje.doloci_obdobje(datum, obdobja),
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


def nalozi_ics(
        pot: str,
        obdobja: Optional[Dict[str, Tuple[datetime, datetime]]] = None,
        oblika_summary: Optional[str] = None,
        oblika_datum: Optional[str] = None
) -> Koledar:
    """
    Naloži ics datoteko v Koledar. Pričakovana oblika vsebine datoteke je


    .. code-block:: text

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

    .. code-block:: text

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
    :param obdobja: slovar izpitnih obdobij (s ključi zimsko, spomladansko in jesensko)
        in vrednostnmi (zacetek, konec), kjer sta obe krajišči vključeni in tipa ``datetime``.
        Izpitni roki, ki so izven vseh, bodo v posebni kategoriji.
    :param oblika_summary: regularni izraz, ki naj mu zadošča polje ``SUMMARY`` v datoteki
    :param oblika_datum: pythonov format za datum (npr. ``%Y%m%D``).

    :return: Koledar, ki vsebuje vse dogodke v ics datoteki.
    """

    if obdobja is None:
        leto = doloci_leto(pot, oblika_datum)
        ZAPISNIKAR.info(f"Iz datumov sklepam, da gre za leto {leto}.")
        obdobja = naredi_izpitna_obdobja(leto)
    seznam_obdobij = []
    for ime_obdobja, (zacetek, konec) in obdobja.items():
        seznam_obdobij.append(IDTerIme.naredi_objekt(Obdobje, ime_obdobja, zacetek, konec))
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
                izpiti.append(
                    sprocesiraj_dogodek(
                        vrstice_dogodka, seznam_obdobij, oblika_summary, oblika_datum
                    )
                )
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
