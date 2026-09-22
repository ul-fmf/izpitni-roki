"""Nalaganje prevodov (issue #9).

Prevodi so v mapi ``prevodi``:

- ``vmesnik.json``  - nizi vmesnika, imena programov, letnikov in obdobij,
- ``predmeti.tsv``  - imena predmetov (stolpci ``sl``, ``en``, ``de``).

Ključi so povsod **slovenski originali**, kot se pojavijo v ``.ics`` datotekah.
Isti ključi gredo v atribut ``data-ime`` na strani, zato permalink (issue #7)
deluje v vseh jezikih enako - povezava, narejena v angleščini, dela v slovenščini.
"""

import json
import os
from datetime import datetime
from typing import Dict, List

from izpitni_roki.osnovno import naredi_zapisnikarja

ZAPISNIKAR = naredi_zapisnikarja(__file__)

JEZIKI = ["sl", "en", "de"]
PRIVZETI_JEZIK = "sl"

MAPA_PREVODOV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prevodi"
)


def _nalozi_vmesnik() -> Dict[str, dict]:
    with open(os.path.join(MAPA_PREVODOV, "vmesnik.json"), encoding="utf-8") as f:
        return json.load(f)


def _nalozi_predmete() -> Dict[str, Dict[str, str]]:
    """
    Prebere ``predmeti.tsv`` v slovar ``{jezik: {slovensko ime: prevod}}``.
    Prazne celice preskočimo, da prevod pade nazaj na slovensko ime.
    """
    pot = os.path.join(MAPA_PREVODOV, "predmeti.tsv")
    po_jezikih: Dict[str, Dict[str, str]] = {j: {} for j in JEZIKI}
    with open(pot, encoding="utf-8") as f:
        glava = f.readline().rstrip("\n").split("\t")
        for stevilka, vrsta in enumerate(f, start=2):
            celice = vrsta.rstrip("\n").split("\t")
            if not celice[0]:
                continue
            if len(celice) != len(glava):
                raise ValueError(
                    f"predmeti.tsv, vrstica {stevilka}: pričakujem {len(glava)} "
                    f"stolpcev, dobil {len(celice)}"
                )
            slovensko = celice[0]
            for jezik, prevod in zip(glava, celice):
                if prevod and jezik in po_jezikih:
                    po_jezikih[jezik][slovensko] = prevod
    return po_jezikih


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
        """Niz vmesnika; če prevoda ni, pade nazaj na slovenskega."""
        vrednost = self._vmesnik.get(kljuc)
        if vrednost:
            return vrednost
        return _JEZIKI_PREDPOMNILNIK[PRIVZETI_JEZIK]._vmesnik.get(kljuc, "")

    def _iz_slovarja(self, skupina: str, kljuc: str) -> str:
        slovar = self._vmesnik.get(skupina) or {}
        prevod = slovar.get(kljuc)
        if prevod:
            return prevod
        privzeti = _JEZIKI_PREDPOMNILNIK[PRIVZETI_JEZIK]._vmesnik.get(skupina) or {}
        return privzeti.get(kljuc) or kljuc

    def program(self, ime: str) -> str:
        return self._iz_slovarja("programi", ime)

    def letnik(self, ime: str) -> str:
        return self._iz_slovarja("letniki", ime)

    def obdobje(self, ime: str) -> str:
        return self._iz_slovarja("obdobja", ime)

    def predmet(self, ime: str) -> str:
        """Predmet brez prevoda pustimo v slovenščini - bolje kot prazna celica."""
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


def nalozi_jezik(koda: str) -> Jezik:
    """
    Naloži prevode za dani jezik.

    :param koda: ``sl``, ``en`` ali ``de``
    :return: objekt :class:`Jezik`
    :raises: ValueError, če jezika ne poznamo
    """
    if koda not in JEZIKI:
        raise ValueError(f"Neznan jezik '{koda}'. Poznam {JEZIKI}.")
    if not _JEZIKI_PREDPOMNILNIK:
        vmesnik = _nalozi_vmesnik()
        predmeti = _nalozi_predmete()
        for j in JEZIKI:
            _JEZIKI_PREDPOMNILNIK[j] = Jezik(j, vmesnik.get(j, {}), predmeti[j])
    return _JEZIKI_PREDPOMNILNIK[koda]


def vsi_jeziki() -> List[Jezik]:
    return [nalozi_jezik(j) for j in JEZIKI]
