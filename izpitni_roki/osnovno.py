import os
import re
import logging
from typing import List, Type, Union
from dataclasses import dataclass
from datetime import datetime


def naredi_zapisnikarja(name):
    """
    Naredi zapisnikarja oz. loggerja.

    :param name: ime zapisnikarja, po navadi kar ``__file__``
    :return: zapisnikar
    """
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


ZAPISNIKAR = naredi_zapisnikarja(__file__)


class IDGenerator:
    """Razred, s katerim polepšamo kodo in se izognemo dolgim guidom."""

    NASLEDNJI_ID = 0

    @staticmethod
    def generiraj_id() -> int:
        """
        Zgenerira naslednji id. Zaporedni klici vrnejo id-je 1, 2, 3 ...

        :return: naslednji id
        """
        IDGenerator.NASLEDNJI_ID += 1
        return IDGenerator.NASLEDNJI_ID


class IDTerIme:
    """
    Nadrazred za razna polja v razredu :meth:`izpitni_roki.osnovno.IzpitniRok`,
    ki poleg dejanske vrednosti (ime) potrbujejo še id.

    Implementira tudi leksikografsko urejenost nizov, ki upošteva slovensko abecedo,
    razširjeno s črkama `ć` in `đ` (a b c č ć d đ e f ...).
    """
    PRIPADNIKI = {}  # vsi elementi tega razreda, vsebuje pare ime: objekt

    def __init__(self, ime: str):
        """
        Konstruktor IDTerIme, ki mu podamo ime, :meth:`izpitni_roki.osnovno.IDGenerator`
        pa poskrbi za njegov id.

        :param ime: ime
        """
        self.ime = ime
        self.id = str(IDGenerator.generiraj_id())

    @staticmethod
    def vse_vsa() -> str:
        """
        Oblika besede "vse" glede na spol.

        :return: ``"vse"``
        """
        return "vse"

    def __str__(self):
        return self.ime

    def _normalna_oblika(self):
        """
        Uporabimo za urejanje po abecedi, ki vsebuje neangleške črke (č, ć, đ, š, ž).

        :return: normalizirana oblika imena, npr. ``Šečđežeć`` se normalizira v ``sseccddezzeccc``
        """
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
            podrazred: Type[Union['Predmet', 'Program', 'Letnik', 'Rok', 'Izvajalec', 'Obdobje']],
            ime: str,
            *args
    ):
        """
        Naredi objekt danega podrazreda razreda IDTerIme

        :param podrazred: izbrani podrazred
        :param ime: polje ime
        :param args: morebitni preostali parametri za konstruktor
        (npr. pri :meth:`izpitni_roki.osnovno.Obdobje`).

        :return: objekt danega podrazreda s podanim imenom
        """
        if ime not in IDTerIme.PRIPADNIKI:
            IDTerIme.PRIPADNIKI[ime] = podrazred(ime, *args)
        return IDTerIme.PRIPADNIKI[ime]


class Predmet(IDTerIme):
    pass


class Program(IDTerIme):
    pass


class Letnik(IDTerIme):
    DOVOLJENI_LETNIKI = {
        "prvi": 1,
        "drugi": 2,
        "tretji": 3,
        "četrti": 4,
        "peti": 5
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


def nalozi_problematicna_imena():
    slovarcek = {}
    problematicna_imena = os.path.join(os.path.dirname(__file__), "problematicna_imena.txt")
    with open(problematicna_imena, encoding="utf-8") as f:
        f.readline()
        for vrsta in f:
            grdo, lepo = vrsta.strip().split(";")
            slovarcek[grdo] = lepo
    return slovarcek


class Izvajalec(IDTerIme):
    PROBLEMATICNI = nalozi_problematicna_imena()
    IZDANA_OPOZORILA = set()

    def __str__(self):
        besede = self.ime.split(" ")
        ugib = " ".join(besede[-1:] + besede[:-1])
        if len(besede) > 2:
            if self.ime in Izvajalec.PROBLEMATICNI:
                return Izvajalec.PROBLEMATICNI[self.ime]
            elif self.ime not in Izvajalec.IZDANA_OPOZORILA:
                ZAPISNIKAR.warning(
                    f"Izvajalec '{self.ime}' bo predstavljen kot '{ugib}', a nismo prepričani, "
                    f"da je tako prav, saj skupno število imen in priimkov presega 2. "
                    f"Če ni prav (ali če tega opozorila nočete več videti), prosimo, "
                    f"dodajte vrstico '{self.ime};prava oblika' "
                    f"v datoteko 'izpitni_roki/problematicna_imena.txt'.\n"
                )
                Izvajalec.IZDANA_OPOZORILA.add(self.ime)
        return ugib


class Obdobje(IDTerIme):
    def __init__(self, ime: str, zacetek: datetime, konec: datetime):
        super().__init__(ime)
        self.zacetek = zacetek
        self.konec = konec

    def __lt__(self, other):
        if isinstance(other, Obdobje):
            return self.zacetek < other.zacetek
        else:
            raise ValueError(f"Obdobje je primerljivo le z Obdobje")

    @staticmethod
    def vse_vsa() -> str:
        return "vsa"

    @staticmethod
    def doloci_obdobje(datum: datetime, obdobja: List['Obdobje']) -> 'Obdobje':
        """
        Najde obdobje, v katero spada dani datum.

        :param datum: neki datum
        :param obdobja: seznam izpitnih obdobij
        :return: obdobje, v katerega spada datum. Če takega obdobja ni, potem vrnemo OBDOBJE_IZVEN.
        """
        for obdobje in obdobja:
            if obdobje.zacetek <= datum <= obdobje.konec:
                return obdobje
        return OBDOBJE_IZVEN


# Obdobje, ki ga uporabimo za roke izven uradnih izpitnih obdobij. Mora biti v prihodnosti,
# zato bo treba čez slabih 1000 let kodo popraviti.
OBDOBJE_IZVEN = Obdobje("izven izpitnih obdobij", datetime(3000, 1, 1), datetime(3000, 1, 1))


@dataclass
class IzpitniRok:
    """Osnovne informacije o izpitnem roku"""
    datum: datetime

    predmet: Predmet
    programi: List[Program]
    letnik: Letnik
    rok: Rok
    izvajalci: List[Izvajalec]
    obdobje: Obdobje

    ics_vrstice: str

    def preveri(self):
        """
        Preveri, ali so vsa polja neprazna.

        :return:

        :raises: ValueError, če je katero od polj prazno
        """
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

    def prikazi_datum(self) -> str:
        """
        Polje datum pretvori v berljiv niz. Tako se npr. 3. 10. 2022 pretvori v niz
        ``"3. oktober 2022 (ponedeljek)"``.

        :return: berljiva predstavitev datuma
        """
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

    def id(self) -> str:
        """
        Iz id-jev polj tega objekta ustvari id tega objekta. Vsebuje le knjižnici `jQuery` prijazne
        znake.

        :return: S podčrtaji ločeni id-ji polj predmet, programi, letnik, rok, izvajalci
            in obdobje. Id-ji za polja, ki so seznami (programi, izvajalci),
            so id-ji elementov danega seznama, ločeni z ``x``.
        """
        id_predmet = self.predmet.id
        id_programi = "x".join(map(lambda p: p.id, self.programi))
        id_letnik = self.letnik.id
        id_rok = self.rok.id
        id_izvajalci = "x".join(map(lambda i: i.id, self.izvajalci))
        id_obdobje = self.obdobje.id
        return "_".join([id_predmet, id_programi, id_letnik, id_rok, id_izvajalci, id_obdobje])

    @staticmethod
    def _prikazi_neprazen_seznam(seznam: List[IDTerIme]):
        """
        Nezadnje elemente seznama loči z znakoma ``, ``, zadnji element paod ostalih (če obstajajo)
        z `` in ``.

        :param seznam: seznam vredonsti, npr.
            ``[Izvajalec("Ana"), Izvajalec("Beno)", Izvajalec("Cene")]``

        :return: lepo oblikovan niz, ki našteje elemente seznama, npr.
            ``"Ana, Beno in Cene"``
        """
        if not seznam:
            raise ValueError(f"Portebujem vsaj en element v seznamu!")
        if len(seznam) == 1:
            return str(seznam[0])
        else:
            return ", ".join(map(str, seznam[:-1])) + f" in {seznam[-1]}"

    def prikazi_smer_in_letnik(self):
        """
        Prikaže smer(i) ter letnik v lepo berljivi obliki.

        :return: npr. ``"1FiMa, 2PeMa (3. letnik)"``
        """
        prikaz_smeri = IzpitniRok._prikazi_neprazen_seznam(self.programi)
        return f"{prikaz_smeri} ({self.letnik} letnik)"

    def prikazi_izvajalce(self):
        """
        Lepo prikaže izvajalce v skladu z
        :meth:`izpitni_roki.osnovno.IzpitniRok._prikazi_neprazen_seznam`

        :return: npr. ``"Ana, Beno in Cene"``

        """
        return IzpitniRok._prikazi_neprazen_seznam(self.izvajalci)

    def prilagodi_ics_opis(self) -> str:
        ena_vrsta = self.ics_vrstice.replace("\n", "@@@@")
        return re.sub("(\\\\, ?)?ni smeri", "", ena_vrsta)


@dataclass
class Koledar:
    """Osnovne informacije o koledarju"""
    smer: str
    izpitni_roki: List[IzpitniRok]

    ics_vrstice: str

    def prilagodi_ics_opis(self, nadomestno_ime: str) -> str:
        vrstice_drugo_ime = re.sub(
            "X-WR-CALNAME:.+(\\n)?( .+(\\n)?)*",   # poskrbimo za prelome vrstic
            f"X-WR-CALNAME:{nadomestno_ime}\n",
            self.ics_vrstice
        )
        return vrstice_drugo_ime.replace("\n", "@@@@")


class HtmlPredloga:
    """
    Predloga za html kodo, ki ji podamo parametre in jo lahko lepo oblikujemo. Pripadajoča
    html datoteka ``predloge/odstavek.html`` je npr.

    .. code-block:: html

        <div class="{{razred}}"> <p>{{besedilo}}</p> </div>

    Ključne besede (obdane z dvojnimi zavitimi oklepaji) kasneje nadomestimo z dejansko vsebino,
    npr.

    .. code-block:: python

        >>> str(HtmlPredloga("odstavek", razred="raz", besedilo="Hojla, bralec!"))
        <div class="raz"> <p>Hojla, bralec!</p> </div>

    """
    def __init__(self, ime_predloge, **kwargs):
        """
        Konstruktor za ta razred.

        :param ime_predloge: ime html datoteke (brez končnice) v mapi ``predloge``,
            npr. ``abc``, če želimo predlogo ``predloge/abc.html``
        :param kwargs: dovoljeni so tisti ključi, ki se pojavijo v predlogi.

        """
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
        """
        Prepiše trenutne vrednosti, ki pripadajo ključnim besedam, s podanimi.
        Pri nastavljanju parametrov poskrbimo, da se zamiki vrstic ohranjajo, tj.

        ``zamik vstavljene vrtice = zamik ključa + prejšnji zamik vstavljene vrstice``

        :param kwargs: (nekateri ali pa vsi) ključi, ki se pojavijo v predlogi

        :return:

        :raises: ValueError, če katerih od podanih kwargov ni med ključi v predlogi.

        """
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
