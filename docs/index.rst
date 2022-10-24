.. Izpitni roki documentation master file, created by
   sphinx-quickstart on Mon Oct 24 08:59:42 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Dokumentacija za projekr Izpitni roki!
======================================

Tu in tam se bo znašla v navodilih kakšna angleška beseda,
za kar se opravičujemo.

Uporaba
=======

Uporaba kode, ki se skriva na repozitoriju, je prikazana spodaj::

   from izpitni_roki.naredi_html import naredi_html
   from datetime import datetime


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
       }
   )

Načeloma je funkcija ``naredi_html`` edina, ki bi jo moral uporabnik
kadarkoli uporabiti.

V primeru, da vaši opisi rokov ne sledijo regularnemu izrazu, ki ga
uporablja Oddelek za matematiko Univerze v Ljubljani, boste morali popraviti
tudi to. Enako velja za format datumov, ki je v vašem ics.
V tem primeru je treba funkciji ``naredi_html`` podati še ustrezna formata,
ki sta natančneje opisana v dokumentaciji.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   izpitni_roki

Indeksi in tabele
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
