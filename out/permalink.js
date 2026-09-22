// Kodiranje in dekodiranje izbire filtrov v url (issue #7).
//
// Zapis je oblike ``program=1Mate&letnik-skip=prvi``, pri čemer
//
//   - ``skupina=a,b``      pomeni, da sta izbrana natanko a in b,
//   - ``skupina-skip=a,b`` pomeni, da je izbrano vse razen a in b,
//   - odsotna skupina      pomeni, da je izbrano vse (privzeto stanje).
//
// Ker je izbrano vse, kar ni odkljukano, in obratno, pri vsaki skupini zapišemo
// tisto od obojega, česar je manj - tako je povezava krajša.
//
// Imena (ne id-jev!) uporabljamo zato, da je povezava berljiva. Id-ji so sicer
// od issue #7 naprej deterministični, a so za človeka nepovedni.

(function (globalni) {
  "use strict";

  var PRIPONA_PRESKOKA = "-skip";

  function kodirajImena(imena) {
    return imena.map(encodeURIComponent).join(",");
  }

  function dekodirajImena(niz) {
    if (niz === "") {
      return [];
    }
    return niz.split(",").map(decodeURIComponent);
  }

  /**
   * Izbiro filtrov zapiše v niz, primeren za url.
   *
   * @param skupine seznam objektov ``{razred, izbrani, neizbrani}``, kjer sta
   *                ``izbrani`` in ``neizbrani`` seznama imen
   * @return npr. ``"program=1Mate&letnik-skip=prvi"``; prazen niz pomeni, da je
   *         povsod izbrano vse
   */
  function zakodiraj(skupine) {
    var deli = [];
    skupine.forEach(function (skupina) {
      if (skupina.neizbrani.length === 0) {
        // privzeto stanje, ni ga treba zapisati
        return;
      }
      if (skupina.izbrani.length <= skupina.neizbrani.length) {
        deli.push(skupina.razred + "=" + kodirajImena(skupina.izbrani));
      } else {
        deli.push(
          skupina.razred + PRIPONA_PRESKOKA + "=" + kodirajImena(skupina.neizbrani)
        );
      }
    });
    return deli.join("&");
  }

  /**
   * Obratna operacija od :js:func:`zakodiraj`. Neveljavne dele niza tiho spusti,
   * da pokvarjena povezava ne pokvari strani.
   *
   * @param niz npr. ``"program=1Mate&letnik-skip=prvi"``
   * @return npr. ``{program: {preskoci: false, imena: ["1Mate"]}, ...}``
   */
  function odkodiraj(niz) {
    var stanje = {};
    (niz || "").split("&").forEach(function (del) {
      var meja = del.indexOf("=");
      if (meja <= 0) {
        return;
      }
      var kljuc = del.slice(0, meja);
      var preskoci = kljuc.slice(-PRIPONA_PRESKOKA.length) === PRIPONA_PRESKOKA;
      if (preskoci) {
        kljuc = kljuc.slice(0, -PRIPONA_PRESKOKA.length);
      }
      if (kljuc === "") {
        return;
      }
      try {
        stanje[kljuc] = { preskoci: preskoci, imena: dekodirajImena(del.slice(meja + 1)) };
      } catch (e) {
        // npr. pokvarjeno %-ubežanje; tako skupino spustimo
      }
    });
    return stanje;
  }

  var izvoz = { zakodiraj: zakodiraj, odkodiraj: odkodiraj };
  if (typeof module !== "undefined" && module.exports) {
    module.exports = izvoz;
  } else {
    globalni.Permalink = izvoz;
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
