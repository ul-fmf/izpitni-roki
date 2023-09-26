.. Izpitni roki documentation master file, created by
   sphinx-quickstart on Mon Oct 24 08:59:42 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Dokumentacija za projekt Izpitni roki
=====================================

Dobrodošli! Uporaba kode, ki se skriva na repozitoriju, je prikazana v datoteki `pozeni.py` in spodaj::

   glavna(
        vhodne_datoteke,
        naslov_strani,
        opis_strani,
        (zimsko, spomladansko, jesensko),
        prazniki,
    )

Načeloma je ta funkcija edina, ki bi jo moral uporabnik kadarkoli uporabiti, saj 

- preveri, ali so razpisani roki v skladu s pravili in
- zgenerira končni html.

V primeru, da vaši opisi rokov v `.ics` datoteki ne sledijo regularnemu izrazu, ki ga
uporablja Oddelek za matematiko Univerze v Ljubljani, boste morali podati še neobvezna argumenta

- ``oblika_ics_summary`` in/ali
- ``oblika_ics_datum``,

ki sta natančneje opisana v dokumentaciji za :meth:`pozeni.glavna` oz. :meth:`izpitni_roki.naredi_html.naredi_html`.

Tu in tam se bo znašla v tem dokumentu kakšna angleška beseda,
za kar se opravičujemo.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   izpitni_roki

Indeksi in tabele
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
