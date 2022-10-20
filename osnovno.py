import re
import logging
from typing import List, Type, Union
from dataclasses import dataclass
from datetime import datetime


class IDGenerator:
    """Polepšajmo kodo in se izognimo dolgim guidom."""
    NASLEDNJI_ID = 0

    @staticmethod
    def generiraj_id():
        IDGenerator.NASLEDNJI_ID += 1
        return IDGenerator.NASLEDNJI_ID


class IDTerIme:
    PRIPADNIKI = {}

    def __init__(self, ime: str):
        self.ime = ime
        self.id = str(IDGenerator.generiraj_id())

    def __str__(self):
        return self.ime

    def _normalna_oblika(self):
        posebni = {"č": "cc", "ć": "ccc", "đ": "dd", "š": "ss", "ž": "zz"}
        return "".join(
            [crka if crka not in posebni else posebni[crka] for crka in self.ime.lower()]
        )

    def __lt__(self, other):
        if isinstance(other, IDTerIme):
            return self._normalna_oblika() < other._normalna_oblika()
        else:
            raise ValueError(f"IDTerIme ni primerljiv z {type(other).__name__}")

    def __eq__(self, other):
        if isinstance(other, IDTerIme):
            return self.id == other.id
        else:
            raise ValueError(f"IDTerIme ni primerljiv z {type(other).__name__}")

    def __hash__(self):
        return hash(self.id)

    def __iter__(self):
        return iter(self.ime)

    def __getitem__(self, i):
        return self.ime[i]

    @staticmethod
    def naredi_objekt(
            podrazred: Type[Union['Predmet', 'Program', 'Letnik', 'Rok', 'Izvajalec']],
            ime: str
    ):
        if ime not in IDTerIme.PRIPADNIKI:
            IDTerIme.PRIPADNIKI[ime] = podrazred(ime)
        return IDTerIme.PRIPADNIKI[ime]


class Predmet(IDTerIme):
    pass


class Program(IDTerIme):
    pass


class Letnik(IDTerIme):
    DOVOLJENI_LETNIKI = {
        "1.": 1, "prvi": 1,
        "2.": 2, "drugi": 2,
        "3.": 3, "tretji": 3,
        "4.": 4, "četrti": 4,
        "5.": 5, "peti": 5
    }

    def __init__(self, ime):
        super().__init__(ime)
        if self.ime not in Letnik.DOVOLJENI_LETNIKI:
            raise ValueError(
                f"Nepravilen letnik: '{self.ime}'. Dovoljeni: {list(Letnik.DOVOLJENI_LETNIKI)}"
            )

    def __lt__(self, other):
        if isinstance(other, IDTerIme):
            return Letnik.DOVOLJENI_LETNIKI[self.ime] < Letnik.DOVOLJENI_LETNIKI[other.ime]
        else:
            raise ValueError(f"IDTerIme ni primerljiv z {type(other).__name__}")


class Rok(IDTerIme):
    pass


class Izvajalec(IDTerIme):
    pass


@dataclass
class IzpitniRok:
    """Osnovne informacije o izpitnem roku"""
    datum: datetime
    predmet: Predmet
    programi: List[Program]
    letnik: Letnik
    rok: Rok
    izvajalci: List[Izvajalec]

    def preveri(self):
        for kljuc, vrednost in self.__dict__.items():
            if not vrednost:
                raise ValueError(f"Atribut {kljuc} je prazen v {self}")

    def _terica(self):
        return tuple(self.__dict__.values())

    def __lt__(self, other):
        if isinstance(other, IzpitniRok):
            return self._terica() < other._terica()
        else:
            raise ValueError(f"IzpitniRok ni primerljiv z {type(other).__name__}")

    def prikazi_datum(self):
        dnevi = ["ponedeljek", "torek", "sreda", "četrtek", "petek", "sobota", "nedelja"]
        meseci = [
            "januar", "februar", "marec", "april",
            "maj", "junij", "julij", "avgust",
            "september", "oktober", "november", "december"

        ]
        dan = dnevi[self.datum.weekday()]
        mesec = meseci[self.datum.month - 1]
        oblikovan_datum = self.datum.strftime(f"{self.datum.day}. {mesec} {self.datum.year}")
        return f"{oblikovan_datum} ({dan})"

    def id(self):
        id_predmet = self.predmet.id
        id_programi = "x".join(map(lambda p: p.id, self.programi))
        id_letnik = self.letnik.id
        id_rok = self.rok.id
        id_izvajalci = "x".join(map(lambda i: i.id, self.izvajalci))
        return "_".join([id_predmet, id_programi, id_letnik, id_rok, id_izvajalci])

    @staticmethod
    def _prikazi_neprazen_seznam(seznam: List[IDTerIme]):
        if not seznam:
            raise ValueError(f"Portebujem vsaj en element v seznamu!")
        if len(seznam) == 1:
            return str(seznam[0])
        else:
            return ", ".join(map(str, seznam[:-1])) + f" in {seznam[-1]}"

    def prikazi_smer_in_letnik(self):
        prikaz_smeri = IzpitniRok._prikazi_neprazen_seznam(self.programi)
        return f"{prikaz_smeri} ({self.letnik} letnik)"

    def prikazi_izvajalce(self):
        return IzpitniRok._prikazi_neprazen_seznam(self.izvajalci)


@dataclass
class Koledar:
    """Osnovne informacije o koledarju"""
    smer: str
    izpitni_roki: List[IzpitniRok]


class HtmlPredloga:
    def __init__(self, ime_predloge, **kwargs):
        self.pot = f"predloge/{ime_predloge}.html"
        self.predloga = ""
        self.parametri = {}
        self.zamiki = {}
        self._nalozi()
        self.nastavi_parametre(**kwargs)

    def _nalozi(self):
        with open(self.pot, encoding="utf-8") as f:
            self.predloga = "".join(f.readlines())
        for zadetek in re.findall(" *{{[^}]+}}", self.predloga):
            zamik = zadetek.find("{")
            zadetek = zadetek.strip()
            self.parametri[zadetek] = None
            self.zamiki[zadetek] = zamik

    def nastavi_parametre(self, **kwargs):
        for kljuc, vrednost in kwargs.items():
            parameter = "{{" + kljuc + "}}"
            if parameter not in self.parametri:
                raise ValueError(
                    f"Neznani parameter {parameter}. Dovoljeno: {list(self.parametri)}"
                )
            vrstice = vrednost.split("\n")
            zamik = self.zamiki[parameter]
            zamaknjene_vrstice = [vrstice[0]]
            for vrsta in vrstice[1:]:
                zamaknjene_vrstice.append(zamik * " " + vrsta)
            self.parametri[parameter] = "\n".join(zamaknjene_vrstice)

    def __str__(self):
        niz = self.predloga
        for parameter, vrednost in self.parametri.items():
            if vrednost is None:
                vrednost = parameter
            niz = niz.replace(parameter, vrednost)
        return niz


def create_logger(name):
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(filename)s:%(funcName)s:%(lineno)d]:  %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    ch.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)
    return logger


def test_predloga():
    p = HtmlPredloga("spustni_spustni_nivo1")
    print(p)
    p.nastavi_parametre(razred="E", ime_skupine="Bla, bla, bla", moznosti="xyz")
    print(p)


if __name__ == "__main__":
    test_predloga()
    a = Izvajalec("Jan")
