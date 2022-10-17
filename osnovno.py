import re
import logging
from typing import List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class IzpitniRok:
    """Osnovne informacije o izpitnem roku"""
    programi: List[str]
    letnik: str
    predmet: str
    izvajalci: List[str]
    rok: str
    datum: datetime


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
        self._nalozi()
        self.nastavi_parametre(**kwargs)

    def _nalozi(self):
        with open(self.pot, encoding="utf-8") as f:
            self.predloga = "".join(f.readlines())
        for zadetek in re.findall("{{[^}]+}}", self.predloga):
            self.parametri[zadetek] = None

    def nastavi_parametre(self, **kwargs):
        for kljuc, vrednost in kwargs.items():
            parameter = "{{" + kljuc + "}}"
            if parameter not in self.parametri:
                raise ValueError(
                    f"Neznani parameter {parameter}. Dovoljeno: {list(self.parametri)}"
                )
            self.parametri[parameter] = vrednost

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
    p.nastavi_parametre(crka="E", imena="Bla, bla, bla")
    print(p)


if __name__ == "__main__":
    test_predloga()
