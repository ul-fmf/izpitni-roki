# Zgenerira testno stran iz podatkov v mapi test_data.
#
# To stran objavimo na GitHub Pages, da je razvidno, kako je videti in deluje
# končni izdelek. Ne vsebuje pravih izpitnih rokov! Prave roke zgenerira
# pozeni.py iz podatkov v mapi letosnji_data.

from datetime import datetime

from izpitni_roki.naredi_html import naredi_html
from izpitni_roki.osnovno import naredi_zapisnikarja, preveri_ics_datoteke


ZAPISNIKAR = naredi_zapisnikarja(__file__)

VHODNA_MAPA = "test_data"
IME_IZHODNE = "testna_stran"

NASLOV = {
    "sl": "Izpitni roki: testna stran",
    "en": "",
    "de": "",
}

# Prazen prevod pomeni, da se uporabi slovenski.
OPIS = {
    "en": "",
    "de": "",
    "sl": (
        "<b>To je samo testna stran, ki prikazuje delovanje generatorja izpitnih "
        "rokov.</b> Zgenerirana je iz nekaj starih, vzorčnih podatkov in <b>ne "
        "vsebuje pravih izpitnih rokov</b>, zato razporeda izpitov tu ne iščite. "
        "Lahko pa preizkusite, kako delujejo filtri po programih, letnikih, "
        "izpitnih obdobjih, predmetih, izvajalcih in rokih ter kako je videti izvoz "
        "izbranih rokov v datoteko <code>.ics</code>."
    ),
}

# Izpitna obdobja za študijsko leto 2021/22, iz katerega so vzorčni podatki.
OBDOBJA = {
    "zimsko": (datetime(2022, 1, 24), datetime(2022, 2, 16)),
    "spomladansko": (datetime(2022, 6, 5), datetime(2022, 7, 5)),
    "jesensko": (datetime(2022, 8, 19), datetime(2022, 9, 13)),
}


if __name__ == "__main__":
    naredi_html(
        preveri_ics_datoteke(VHODNA_MAPA),
        naslov=NASLOV,
        opis_strani=OPIS,
        ime_izhodne=IME_IZHODNE,
        obdobja=OBDOBJA,
    )
    ZAPISNIKAR.info(f"Zgeneriral out/{IME_IZHODNE}.html")
