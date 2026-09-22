"""Nalaganje prevodov (issue #9).

Prevodi so v mapi ``prevodi``:

- ``vmesnik.json``  - nizi vmesnika, imena programov, letnikov in obdobij,
- ``predmeti.tsv``  - imena predmetov (stolpci ``sl``, ``en``, ``de``).

Ključi so povsod **slovenski originali**, kot se pojavijo v ``.ics`` datotekah.
Isti ključi gredo v atribut ``data-ime`` na strani, zato permalink (issue #7)
deluje v vseh jezikih enako - povezava, narejena v angleščini, dela v slovenščini.

Glede strogosti velja razlika med vrednostjo in ključem:

- **prazna vrednost** ni napaka; namesto nje se uporabi slovenska, tako da je
  stran uporabna že pred prevajanjem,
- **ključi** pa morajo biti v vseh jezikih natanko isti, rekurzivno po vseh
  nivojih. Odvečen ključ je tipkarska napaka, manjkajoč pa pomeni, da prevajalec
  zanj sploh ne bo videl praznega mesta.

To velja tudi za ključe, ki prihajajo iz ``.ics`` datotek - predmete, programe,
letnike in obdobja. Nov predmet ali program, ki nima vnosa med prevodi, ustavi
generiranje: surova koda (``1ApMa`` namesto ``Aplikativna matematika``) na strani
ni sprejemljiv približek, temveč napaka, ki jo je treba opaziti.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List

JEZIKI = ["sl", "en", "de"]
PRIVZETI_JEZIK = "sl"

MAPA_PREVODOV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prevodi"
)

# Ključi, ki niso navadni nizi in jih preverimo posebej
SEZNAMI = {"dnevi": 7, "meseci": 12}
POLJA_DATUMA = {"dan", "mesec", "leto", "dan_v_tednu"}


class NapakaVPrevodih(Exception):
    """Prevodi niso v redu - generiranje strani prekinemo."""


def _napake_kljucev(kje: str, imamo: dict, merodajni: dict) -> List[str]:
    """
    Rekurzivno primerja zgradbo dveh slovarjev: imeti morata natanko iste ključe
    na vseh nivojih, vrednosti pa nas ne zanimajo (prazna je le manjkajoč prevod).

    Odvečen ključ je tipkarska napaka, manjkajoč pa pomeni, da prevajalec zanj
    sploh ne bo videl praznega mesta.

    :param kje: pot do tega slovarja za sporočilo o napaki, npr. ``en.obdobja``
    :param imamo: slovar, ki ga preverjamo
    :param merodajni: slovenski slovar, s katerim primerjamo

    :return: seznam opisov napak (prazen, če je zgradba enaka)
    """
    napake = [
        f"{kje}: odvečen ključ {kljuc} (slovenščina ga ne pozna - tipkarska napaka?)"
        for kljuc in sorted(set(imamo) - set(merodajni))
    ]
    napake += [
        f"{kje}: manjka ključ {kljuc} (vrednost sme biti prazna, ključ pa mora biti)"
        for kljuc in sorted(set(merodajni) - set(imamo))
    ]
    for kljuc in sorted(set(imamo) & set(merodajni)):
        nasa, njihova = imamo[kljuc], merodajni[kljuc]
        if isinstance(nasa, dict) and isinstance(njihova, dict):
            napake += _napake_kljucev(f"{kje}.{kljuc}", nasa, njihova)
        elif isinstance(nasa, dict) != isinstance(njihova, dict):
            napake.append(
                f"{kje}.{kljuc}: zgradba se ne ujema s slovensko "
                f"({type(nasa).__name__} proti {type(njihova).__name__})"
            )
    return napake


def _napake_seznamov(koda: str, slovar: dict) -> List[str]:
    """Dnevi in meseci morajo biti pravega števila, sicer datum pade ob izrisu."""
    napake = []
    for ime_seznama, dolzina in SEZNAMI.items():
        seznam = slovar.get(ime_seznama)
        if seznam is not None and len(seznam) != dolzina:
            napake.append(
                f"{koda}.{ime_seznama}: pričakujem {dolzina} vrednosti, "
                f"dobil {len(seznam)}"
            )
    return napake


def _napake_oblike_datuma(koda: str, slovar: dict) -> List[str]:
    """Oblika datuma sme uporabljati le polja, ki jih znamo napolniti."""
    oblika = slovar.get("oblika_datuma")
    if not oblika:
        return []
    neznana = set(re.findall(r"{(\w+)}", oblika)) - POLJA_DATUMA
    if not neznana:
        return []
    return [
        f"{koda}.oblika_datuma: nepoznana polja {sorted(neznana)}; "
        f"poznam {sorted(POLJA_DATUMA)}"
    ]


def preveri_vmesnik(vmesnik: Dict[str, dict]) -> None:
    """
    Preveri prevode vmesnika. Slovenščina je merodajna: vsi jeziki morajo imeti
    **natanko iste ključe** na vseh nivojih, vrednosti pa so lahko prazne.

    :param vmesnik: vsebina ``vmesnik.json``

    :raises NapakaVPrevodih: če kak jezik manjka ali je odveč, če se množici ključev
        ne ujemata (na katerem koli nivoju), če je seznam dni ali mesecev napačne
        dolžine ali če oblika datuma uporablja polje, ki ga ne poznamo
    """
    if PRIVZETI_JEZIK not in vmesnik:
        raise NapakaVPrevodih(f"V prevodih manjka privzeti jezik {PRIVZETI_JEZIK}.")
    merodajni = vmesnik[PRIVZETI_JEZIK]
    napake = [
        f"manjka cel jezik {koda} (tiho bi padel nazaj na slovenščino)"
        for koda in JEZIKI
        if koda not in vmesnik
    ]
    napake += [
        f"nepoznan jezik {koda}; poznam {JEZIKI}"
        for koda in vmesnik
        if koda not in JEZIKI
    ]
    for koda, slovar in vmesnik.items():
        napake += _napake_kljucev(koda, slovar, merodajni)
        napake += _napake_seznamov(koda, slovar)
        napake += _napake_oblike_datuma(koda, slovar)
    if napake:
        raise NapakaVPrevodih(
            "Napake v prevodi/vmesnik.json:\n  - " + "\n  - ".join(napake)
        )


def preveri_predmete(glava: List[str], videna: Dict[str, int]) -> None:
    """
    Preveri glavo in podvojene vrstice v ``predmeti.tsv``.

    :raises NapakaVPrevodih: če glava ni ``sl/en/de`` ali če se kako slovensko
        ime predmeta ponovi
    """
    if glava != JEZIKI:
        raise NapakaVPrevodih(f"predmeti.tsv: glava mora biti {JEZIKI}, dobil {glava}")
    podvojena = sorted(ime for ime, n in videna.items() if n > 1)
    if podvojena:
        raise NapakaVPrevodih(
            "predmeti.tsv: podvojena imena: " + ", ".join(podvojena)
        )


def _nalozi_vmesnik() -> Dict[str, dict]:
    with open(os.path.join(MAPA_PREVODOV, "vmesnik.json"), encoding="utf-8") as f:
        return json.load(f)


def _nalozi_predmete():
    """
    Prebere ``predmeti.tsv``.

    :return: par ``({jezik: {slovensko ime: prevod}}, {vsa slovenska imena})``.
        Prazne celice v prvem preskočimo, da se namesto njih uporabi slovensko ime;
        druga množica pa vsebuje vsa imena, tudi neprevedena, in služi za
        preverjanje, ali predmet sploh poznamo.
    """
    pot = os.path.join(MAPA_PREVODOV, "predmeti.tsv")
    po_jezikih: Dict[str, Dict[str, str]] = {j: {} for j in JEZIKI}
    videna: Dict[str, int] = {}
    with open(pot, encoding="utf-8") as f:
        glava = f.readline().rstrip("\n").split("\t")
        for stevilka, vrsta in enumerate(f, start=2):
            celice = vrsta.rstrip("\n").split("\t")
            if not celice[0]:
                continue
            if len(celice) != len(glava):
                raise NapakaVPrevodih(
                    f"predmeti.tsv, vrstica {stevilka}: pričakujem {len(glava)} "
                    f"stolpcev, dobil {len(celice)}"
                )
            slovensko = celice[0]
            videna[slovensko] = videna.get(slovensko, 0) + 1
            for jezik, prevod in zip(glava, celice):
                if prevod and jezik in po_jezikih:
                    po_jezikih[jezik][slovensko] = prevod
    preveri_predmete(glava, videna)
    return po_jezikih, set(videna)


class Jezik:
    """Prevodi za en jezik. Naredi ga :func:`nalozi_jezik`."""

    def __init__(self, koda: str, vmesnik: dict, predmeti: Dict[str, str]):
        self.koda = koda
        self._vmesnik = vmesnik
        self._predmeti = predmeti

    # -- kje na strani zivi ta jezik -----------------------------------------

    @property
    def podmapa(self) -> str:
        """Slovenščina ostane na obstoječem url-ju, ostali jeziki so v podmapi.

        Tako že deljeni permalinki (``.../testna-stran/#program=1Mate``) še naprej
        delujejo in jih ni treba loviti prek preusmeritve, ki fragmenta ne prenaša
        zanesljivo.
        """
        return "" if self.koda == PRIVZETI_JEZIK else self.koda

    @property
    def predpona_sredstev(self) -> str:
        """Predpona do ``dodatni.css`` in skript, ki so v korenu strani."""
        return "" if self.koda == PRIVZETI_JEZIK else "../"

    # -- posamezni nizi ------------------------------------------------------

    def niz(self, kljuc: str) -> str:
        """
        Niz vmesnika. Če prevoda ni, uporabimo slovenskega.

        :raises NapakaVPrevodih: če ključa ne pozna niti slovenščina - to je
            tipkarska napaka v kodi ali predlogi in ne sme tiho vrniti praznega niza
        """
        merodajni = _JEZIKI_PREDPOMNILNIK[PRIVZETI_JEZIK]._vmesnik
        if kljuc not in merodajni:
            raise NapakaVPrevodih(
                f"Nepoznan ključ {kljuc}. Dodajte ga v prevodi/vmesnik.json "
                f"(vsaj v {PRIVZETI_JEZIK})."
            )
        return self._vmesnik.get(kljuc) or merodajni[kljuc]

    def _iz_slovarja(self, skupina: str, kljuc: str) -> str:
        """Vrednost iz ugnezdenega slovarja (programi, letniki, obdobja ...).

        Ključ mora biti znan: tiho prikazana surova koda (``1ApMa`` namesto
        ``Aplikativna matematika``) je napaka, ne pa sprejemljiv približek.
        Prazen prevod pa pomeni le, da prevoda še ni, in uporabimo slovenskega.

        :raises NapakaVPrevodih: če skupine ali ključa ne poznamo
        """
        merodajni = _JEZIKI_PREDPOMNILNIK[PRIVZETI_JEZIK]._vmesnik
        if skupina not in merodajni:
            raise NapakaVPrevodih(f"Nepoznana skupina prevodov {skupina}.")
        privzeti = merodajni[skupina] or {}
        if kljuc not in privzeti:
            raise NapakaVPrevodih(
                f"Za {kljuc} ni vnosa med {skupina} v prevodi/vmesnik.json. "
                f"Dodajte ga (prevod sme biti zaenkrat prazen). "
                f"Poznam {sorted(privzeti)}."
            )
        return (self._vmesnik.get(skupina) or {}).get(kljuc) or privzeti[kljuc]

    def program(self, ime: str) -> str:
        return self._iz_slovarja("programi", ime)

    def letnik(self, ime: str) -> str:
        return self._iz_slovarja("letniki", ime)

    def obdobje(self, ime: str) -> str:
        return self._iz_slovarja("obdobja", ime)

    def rok(self, ime: str) -> str:
        """Oznaka roka, npr. ``1.`` v slovenščini in ``first`` v angleščini."""
        return self._iz_slovarja("roki", ime)

    def predmet(self, ime: str) -> str:
        """
        Ime predmeta v tem jeziku.

        Za razliko od programov in obdobij je tu vsak predmet obvezen: prevodi
        imen predmetov so bistvo večjezične strani, zato nov predmet, ki v
        ``predmeti.tsv`` še nima vrstice, ustavi generiranje. Prazna celica pa
        pomeni le, da prevoda še ni, in uporabimo slovensko ime.

        :raises NapakaVPrevodih: če predmeta ni med znanimi
        """
        if ime not in _ZNANI_PREDMETI:
            raise NapakaVPrevodih(
                f"Predmet {ime} nima vrstice v prevodi/predmeti.tsv. "
                f"Dodajte jo (prevod sme biti zaenkrat prazen)."
            )
        return self._predmeti.get(ime, ime)

    def gumb_skupine(self, razred: str, izbrano: bool) -> str:
        """Napis 'Izberi vse' oz. 'Odstrani vse' za dano skupino filtrov.

        Ločeno po skupinah zato, ker slovenščina loči spol (vse/vsa), drugi
        jeziki pa ne - tako noben jezik ni ujet v slovensko slovnico.
        """
        return self._iz_slovarja("odstrani_vse" if izbrano else "izberi_vse", razred)

    # -- datum ---------------------------------------------------------------

    def datum(self, kdaj: datetime) -> str:
        """Datum v obliki, ki jo predpisuje ta jezik."""
        return self.niz("oblika_datuma").format(
            dan=kdaj.day,
            mesec=self._vmesnik["meseci"][kdaj.month - 1],
            leto=kdaj.year,
            dan_v_tednu=self._vmesnik["dnevi"][kdaj.weekday()],
        )


_JEZIKI_PREDPOMNILNIK: Dict[str, Jezik] = {}
# Vsa slovenska imena predmetov iz predmeti.tsv, ne glede na to, ali so prevedena
_ZNANI_PREDMETI: set = set()


def nalozi_jezik(koda: str) -> Jezik:
    """
    Naloži prevode za dani jezik.

    :param koda: ``sl``, ``en`` ali ``de``
    :return: objekt :class:`Jezik`
    :raises ValueError: če jezika ne poznamo
    :raises NapakaVPrevodih: če so datoteke s prevodi pokvarjene
    """
    if koda not in JEZIKI:
        raise ValueError(f"Neznan jezik {koda}. Poznam {JEZIKI}.")
    if not _JEZIKI_PREDPOMNILNIK:
        vmesnik = _nalozi_vmesnik()
        preveri_vmesnik(vmesnik)
        predmeti, znani = _nalozi_predmete()
        _ZNANI_PREDMETI.update(znani)
        for j in JEZIKI:
            _JEZIKI_PREDPOMNILNIK[j] = Jezik(j, vmesnik.get(j, {}), predmeti[j])
    return _JEZIKI_PREDPOMNILNIK[koda]


def vsi_jeziki() -> List[Jezik]:
    return [nalozi_jezik(j) for j in JEZIKI]
