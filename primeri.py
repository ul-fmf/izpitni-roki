from izpitni_roki.naredi_html import naredi_html
from datetime import datetime
from izpitni_roki.glasbene_zelje import prikazi_isrm_roke

leto = 2023

leto0 = str(leto % 100) + str((leto + 1) % 100)
leto1 = str(leto) + "/" + str((leto + 1) % 100)

print(leto0)


# Ustvari spletno stran iz testnih podatkov
naredi_html(
    ["data/1FiMa" + leto0 + ".ics", "data/1Mate2PeMa" + leto0 + ".ics", "data/1PrMa" + leto0 + ".ics"],
    naslov="Izpitni roki na Oddelku za matematiko FMF v študijskem letu " + leto1,
    opis_strani="""Spodaj so prikazani izpitni roki na programih Finančna matematika (1FiMa), Matematika (1Mate) in Praktična matematika (1PrMa) in prvih treh letnikih programa Pedagoška matematika (2PeMa) na Oddelku za matematiko FMF v študijskem letu """ + leto1 + """, ki zadoščajo izbranim kriterijem.""",

#Izbrane izpitne roke lahko prenesete kot .ics datoteko in jih nato dodate v svoj osebni koledar, vendar pozor: morebitne kasnejše spremembe izpitnih rokov se v vašem osebnem koledarju ne bodo poznale.""",
    obdobja={
        "zimsko": (datetime(2024, 1, 1), datetime(2024, 3, 1)),
        "letno": (datetime(2024, 6, 1), datetime(2024, 8,1)),
        "jesensko": (datetime(2024, 8, 11), datetime(2024, 10, 1))
    },
    oblika_summary=None,
    oblika_datum=None
)


# Glasbene želje
prikazi_isrm_roke(["data/1FiMa" + leto0 + ".ics", "data/1Mate2PeMa" + leto0 + ".ics", "data/1PrMa" + leto0 + ".ics"])
