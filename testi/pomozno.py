"""Skupni pripomočki za teste."""

import os
from datetime import datetime

from izpitni_roki.osnovno import IDTerIme

OBDOBJA = {
    "zimsko": (datetime(2022, 1, 24), datetime(2022, 2, 16)),
    "spomladansko": (datetime(2022, 6, 5), datetime(2022, 7, 5)),
    "jesensko": (datetime(2022, 8, 19), datetime(2022, 9, 13)),
}
TESTNE = [
    os.path.join("test_data", f"test{i}.ics") for i in (1, 2, 3)
]


def pozabi_vse():
    """Pozabi doslej ustvarjene objekte, kot da bi stran generirali na novo."""
    IDTerIme.PRIPADNIKI.clear()
    IDTerIme.ZASEDENI_IDJI.clear()
