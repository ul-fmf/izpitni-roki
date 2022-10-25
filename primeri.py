from izpitni_roki.naredi_html import naredi_html
from datetime import datetime
from izpitni_roki.glasbene_zelje import prikazi_isrm_roke


# Ustvari spletno stran iz testnih podatkov
naredi_html(
    ["data/test1.ics", "data/test2.ics"],
    naslov="Izpitni roki na Oddelku za matematiko FMF v študijskem letu 2022/23",
    opis_strani="Spodaj so prikazani izpitni roki na programih Finančna matematika (1FiMa),"
    " Matematika (1Mate) in Praktična matematika (1PrMa) in "
    "prvih treh letnikih programa Pedagoška matematika (2PeMa) "
    "na Oddelku za matematiko FMF v študijskem letu 2022/23, ki zadoščajo izbranim kriterijem.",
    obdobja={
        "zimsko": (datetime(2022, 1, 15), datetime(2022, 2, 15)),
        "letno": (datetime(2022, 6, 15), datetime(2022, 7, 15)),
        "jesensko": (datetime(2022, 8, 15), datetime(2022, 9, 6))
    },
    oblika_summary=None,
    oblika_datum=None
)


# Glasbene želje
prikazi_isrm_roke(["data/1FiMa2122.ics", "data/1Mate2PeMa2122.ics", "data/1PrMa2122.ics"])
