import os
import re
import html
import unicodedata
from izpitni_roki.osnovno import (
    preveri_zapolnjeno,
    naredi_zapisnikarja,
    IzpitniRok,
    Koledar,
    HtmlPredloga,
    IDTerIme
)
from izpitni_roki.nalozi_ics import nalozi_ics
from izpitni_roki.jezik import JEZIKI, PRIVZETI_JEZIK, nalozi_jezik
from typing import List, Callable, Dict, Tuple, Optional
from datetime import datetime


ZAPISNIKAR = naredi_zapisnikarja(__file__)
CRKE = "ABCČDEFGHIJKLMNOPRSŠTUVZŽ"
IZHODNA_MAPA = "out"


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
    Nadomestni letnik programov, ki letnikov nimajo (npr. magistrski študij),
    izpustimo, saj v spustni meni ne sodi: roki takih programov filtra po
    letnikih ne upoštevajo.

    :param koledarji: seznam koledarjev

    :return: (urejeni) letniki (brez ponovitev in brez Letnik.BREZ_LETNIKA)
    """
    letniki = najdi_vse(koledarji, lambda rok: rok.letniki)
    return [letnik for letnik in letniki if not letnik.je_brez_letnika()]


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


def doloci_skupinsko_crko(moznost: IDTerIme) -> str:
    """
    Pove, pod katero črko v dvonivojskem spustnem meniju sodi dana možnost.

    :param moznost: možnost, npr. ``Izvajalec("Álvarez Román")``

    :return: črka iz ``CRKE``. Tuje črke, ki jih ``CRKE`` ne pozna (npr. ``Á``),
        uvrstimo k osnovni črki (``A``).
    """
    crka = moznost[0].upper()
    if crka in CRKE:
        return crka
    osnovna_crka = unicodedata.normalize("NFD", crka)[0]
    if osnovna_crka in CRKE:
        return osnovna_crka
    ZAPISNIKAR.warning(
        f"Črke '{crka}' (na začetku '{moznost.ime}') ne poznam, "
        f"zato možnost uvrščam pod '{CRKE[0]}'."
    )
    return CRKE[0]


def prevedi_moznost(jezik, html_razred: str, moznost: IDTerIme) -> str:
    """
    Besedilo, s katerim je možnost prikazana v spustnem meniju, v danem jeziku.

    Imena izvajalcev se ne prevajajo (so imena, ne besedilo), vse ostalo pa gre
    skozi slovar prevodov.

    :param jezik: objekt :class:`izpitni_roki.jezik.Jezik`
    :param html_razred: skupina filtra, npr. ``program``
    :param moznost: možnost, npr. ``Program("1ApMa")``

    :return: npr. ``"Aplikativna matematika"``
    """
    prevajalci = {
        "program": jezik.program,
        "letnik": jezik.letnik,
        "obdobje": jezik.obdobje,
        "predmet": jezik.predmet,
        "rok": jezik.rok,
    }
    if html_razred in prevajalci:
        return prevajalci[html_razred](moznost.ime)
    return str(moznost)


def _ovoj_menija(jezik, ime_menija: str, html_razred: str, skupine: str) -> str:
    """Skupni ovoj obeh vrst spustnih menijev."""
    return str(
        HtmlPredloga(
            "spustni_spustni",
            ime_menija=ime_menija,
            razred=html_razred,
            skupine=skupine,
            izberi_vse=jezik.gumb_skupine(html_razred, izbrano=False),
            odstrani_vse=jezik.gumb_skupine(html_razred, izbrano=True),
        )
    )


def _moznost_html(jezik, html_razred: str, moznost: IDTerIme) -> str:
    return str(
        HtmlPredloga(
            "spustni_spustni_nivo2",
            razred=html_razred,
            besedilo=html.escape(prevedi_moznost(jezik, html_razred, moznost)),
            id=moznost.id,
            ime=html.escape(moznost.ime, quote=True),
        )
    )


def naredi_spustni_meni_po_crkah(
        jezik,
        ime_menija: str,
        html_razred: str,
        moznosti: List[IDTerIme]
) -> str:
    """
    Naredi dvonivojski spustni meni.

    Skupine črk se ravnajo po **slovenskem** imenu, tudi v prevedenih različicah,
    da je vrstni red v vseh jezikih enak in da se ujema z razvrstitvijo.

    :param jezik: objekt :class:`izpitni_roki.jezik.Jezik`
    :param ime_menija: napis na gumbu
    :param html_razred: razred, ki ga dodatmo v ``class`` atribut vseh možnosti
    :param moznosti: Urejen seznam moznosti.

    :return: str(html predloga za dvonivojski spustni meni), oz. prazen niz,
        če ni nobene možnosti
    """
    if not moznosti:
        return ""
    skupine: List[List[IDTerIme]] = [[] for _ in CRKE]
    for moznost in moznosti:
        skupine[CRKE.index(doloci_skupinsko_crko(moznost))].append(moznost)
    elementi_nivo1 = []
    for crka, skupina in zip(CRKE, skupine):
        if not skupina:
            continue
        elementi_nivo1.append(
            str(
                HtmlPredloga(
                    "spustni_spustni_nivo1",
                    ime_skupine=crka,
                    moznosti="\n".join(
                        _moznost_html(jezik, html_razred, m) for m in skupina
                    ),
                    razred=html_razred
                )
            )
        )
    return _ovoj_menija(jezik, ime_menija, html_razred, "\n".join(elementi_nivo1))


def naredi_spustni_meni(
        jezik,
        ime_menija: str,
        html_razred: str,
        moznosti: List[IDTerIme]
) -> str:
    """
    Naredi enonivojski spustni meni.

    :param jezik: objekt :class:`izpitni_roki.jezik.Jezik`
    :param ime_menija: napis na gumbu
    :param html_razred: razred, ki ga dodatmo v ``class`` atribut vseh možnosti
    :param moznosti: Urejen seznam moznosti.

    :return: str(html predloga enonivojski spustni meni), oz. prazen niz,
        če ni nobene možnosti (npr. meni letnikov, kadar prikazujemo le
        programe brez letnikov)
    """
    if not moznosti:
        return ""
    elementi = [_moznost_html(jezik, html_razred, m) for m in moznosti]
    return _ovoj_menija(jezik, ime_menija, html_razred, "\n".join(elementi))


def naredi_tabelo(koledarji: List[Koledar], jezik) -> str:
    """
    Html koda za tabelo vseh izpitnih rokov

    :param koledarji: seznam objektov Koledar
    :param jezik: objekt :class:`izpitni_roki.jezik.Jezik`

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
                datum=izpitni_rok.prikazi_datum(jezik),
                predmet=html.escape(jezik.predmet(izpitni_rok.predmet.ime)),
                letnik=izpitni_rok.prikazi_smer_in_letnik(jezik),
                rok=jezik.rok(izpitni_rok.rok.ime),
                izvajalci=izpitni_rok.prikazi_izvajalce(),
                ics_raw=izpitni_rok.ics_vrstice(jezik)
            ))
        )
    # ics opis skupnega koledarja bomo naredili iz enega od ics opisov
    # koledarjev, pri čemer bomo ime koledarja zamenjali z generičnim imenom
    return str(
        HtmlPredloga(
            "tabela",
            ics_raw=koledarji[0].prilagodi_ics_opis(jezik.niz("ics_ime_koledarja")),
            ics_datoteka=jezik.niz("ics_ime_datoteke"),
            stolpec_datum=jezik.niz("stolpec_datum"),
            stolpec_predmet=jezik.niz("stolpec_predmet"),
            stolpec_program_letnik=jezik.niz("stolpec_program_letnik"),
            stolpec_rok=jezik.niz("stolpec_rok"),
            stolpec_izvajalci=jezik.niz("stolpec_izvajalci"),
            vrstice="\n".join(vrstice)
        )
    )


MAPA_PORTRETOV = "portreti"


def pot_do_portreta(trenutni, koda: str) -> str:
    """
    Pot do portreta matematika, ki predstavlja dani jezik.

    Slike so v ``out/portreti`` in se objavijo skupaj s stranjo, zato jih naslovimo
    glede na to, v kateri mapi je stran, ki povezavo vsebuje.

    :param trenutni: jezik strani, na kateri je povezava
    :param koda: jezik, ki ga povezava ponuja
    :return: npr. ``../portreti/sl.jpg``
    """
    return f"{trenutni.predpona_sredstev}{MAPA_PORTRETOV}/{koda}.jpg"


def naredi_preklop_jezika(trenutni, ime_izhodne: str) -> str:
    """
    Povezave na isto stran v drugih jezikih.

    Fragment (permalink, issue #7) je v vseh jezikih enak, ker so ključi slovenski
    originali; ``posodabljanje.js`` ga tem povezavam doda ob vsaki spremembi izbire,
    da izbira preživi preklop jezika.

    :param trenutni: jezik te strani
    :param ime_izhodne: ime html datoteke brez končnice

    :return: html s povezavami na vse jezike
    """
    from izpitni_roki.jezik import vsi_jeziki

    povezave = []
    # Portret namesto napisa; ime jezika ostane v title in aria-label, da je
    # povezava razumljiva tudi bralniku zaslona in ob postanku z miško.
    for jezik in vsi_jeziki():
        if jezik.koda == trenutni.koda:
            pot = "#"
        elif jezik.podmapa:
            pot = f"{trenutni.predpona_sredstev}{jezik.podmapa}/{ime_izhodne}.html"
        else:
            pot = f"{trenutni.predpona_sredstev}{ime_izhodne}.html"
        povezave.append(
            str(
                HtmlPredloga(
                    "jezik_povezava",
                    razred="btn-primary" if jezik.koda == trenutni.koda else "btn-light",
                    pot=pot,
                    koda=jezik.koda,
                    ime=html.escape(jezik.niz("ime_jezika") or jezik.koda, quote=True),
                    portret=pot_do_portreta(trenutni, jezik.koda),
                    znak=html.escape(jezik.niz("znak_portreta")),
                )
            )
        )
    return "\n".join(povezave)


def _za_jezik(vrednost, koda: str) -> str:
    """Besedilo, ki ga je klicatelj podal bodisi kot niz bodisi kot slovar po jezikih."""
    if isinstance(vrednost, dict):
        return vrednost.get(koda) or vrednost.get(PRIVZETI_JEZIK, "")
    return vrednost


def naredi_stran_za_jezik(
        koledarji: List[Koledar],
        jezik,
        naslov,
        opis_strani,
        ime_izhodne: str
) -> str:
    """
    Sestavi eno html stran v danem jeziku in jo zapiše v izhodno mapo.

    :param koledarji: naloženi koledarji
    :param jezik: objekt :class:`izpitni_roki.jezik.Jezik`
    :param naslov: naslov strani (niz ali slovar po jezikih)
    :param opis_strani: opis strani (niz ali slovar po jezikih)
    :param ime_izhodne: ime datoteke brez končnice

    :return: pot do zapisane datoteke
    """
    meniji = [
        naredi_spustni_meni(jezik, jezik.niz("meni_program"), "program",
                            najdi_vse_programe(koledarji)),
        naredi_spustni_meni(jezik, jezik.niz("meni_letnik"), "letnik",
                            najdi_vse_letnike(koledarji)),
        naredi_spustni_meni(jezik, jezik.niz("meni_obdobje"), "obdobje",
                            najdi_vsa_obdobja(koledarji)),
        naredi_spustni_meni_po_crkah(jezik, jezik.niz("meni_predmet"), "predmet",
                                     najdi_vse_predmete(koledarji)),
        naredi_spustni_meni_po_crkah(jezik, jezik.niz("meni_izvajalec"), "izvajalec",
                                     najdi_vse_izvajalce(koledarji)),
        naredi_spustni_meni(jezik, jezik.niz("meni_rok"), "rok",
                            najdi_vse_roke(koledarji)),
        str(HtmlPredloga("prenos", gumb_prenos=jezik.niz("gumb_prenos"))),
    ]

    html_stran = HtmlPredloga(
        "stran",
        koda_jezika=jezik.koda,
        predpona=jezik.predpona_sredstev,
        title=jezik.niz("title"),
        naslov=_za_jezik(naslov, jezik.koda),
        jeziki=naredi_preklop_jezika(jezik, ime_izhodne),
        razdelek_o_strani=jezik.niz("razdelek_o_strani"),
        razdelek_izbira=jezik.niz("razdelek_izbira"),
        razdelek_izbrani=jezik.niz("razdelek_izbrani"),
        opis_strani=_za_jezik(opis_strani, jezik.koda),
        odstavek_ics=jezik.niz("odstavek_ics"),
        gumb_komentar=jezik.niz("gumb_komentar"),
        spustni_meniji="\n\n".join(meni for meni in meniji if meni),
        izpiti=naredi_tabelo(koledarji, jezik),
    )
    mapa = os.path.join(IZHODNA_MAPA, jezik.podmapa) if jezik.podmapa else IZHODNA_MAPA
    os.makedirs(mapa, exist_ok=True)
    pot = os.path.join(mapa, f"{ime_izhodne}.html")
    besedilo = preveri_zapolnjeno(str(html_stran), f"strani {pot}")
    with open(pot, "w", encoding="utf-8") as f:
        print(besedilo, file=f)
    return pot


def naredi_html(
        poti_do_koledarjev: List[str],
        naslov = "Naslov strani",
        opis_strani: str = "Opis strani",
        ime_izhodne: str = "izpitni_roki",
        obdobja: Optional[Dict[str, Tuple[datetime, datetime]]] = None,
        oblika_summary: Optional[str] = None,
        oblika_datum: Optional[str] = None,
        jeziki: Optional[List[str]] = None
) -> List[str]:
    """
    Naredi celotno spletno stran, v vsakem od želenih jezikov po eno.

    Slovenska različica pristane v izhodni mapi, ostale v podmapi s kodo jezika
    (``out/en/...``), tako da že deljene povezave na slovensko stran še naprej
    delujejo.

    :param poti_do_koledarjev: seznam poti do .ics datotek, ki vsebujejo izpitne roke
    :param naslov: naslov spletne strani; niz ali slovar ``{"sl": ..., "en": ...}``
    :param opis_strani: kratek opis strani; niz ali slovar po jezikih
    :param ime_izhodne: ime izhodne datoteke, npr. ``izpitni_roki``
    :param obdobja: slovar, ki podaja imena in intervale izpitnih obdobij
    :param oblika_summary: regularni izraz, ki mu zadošča polje ``SUMMARY`` v ics datoteki
    :param oblika_datum: format datuma (npr. ``%Y%m%D``)
    :param jeziki: kode jezikov, ki naj jih zgeneriramo; privzeto vsi znani

    :return: seznam poti do zgeneriranih datotek
    """
    koledarji = [
        nalozi_ics(pot, obdobja, oblika_summary, oblika_datum) for pot in poti_do_koledarjev
    ]
    poti = []
    for koda in (jeziki if jeziki is not None else JEZIKI):
        jezik = nalozi_jezik(koda)
        poti.append(
            naredi_stran_za_jezik(koledarji, jezik, naslov, opis_strani, ime_izhodne)
        )
        ZAPISNIKAR.info(f"Zgeneriral {poti[-1]}")
    return poti
