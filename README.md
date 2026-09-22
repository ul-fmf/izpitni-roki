# Izpitni roki

Koda, ki zgenerira [spletno stran z izpitnimi roki](https://ul-fmf.github.io/izpitni-roki/testna-stran/). Zdaj tudi koda, ki preveri skladnost rokov s pravili.

# Dokumentacija

je dostopna [tukaj](https://ul-fmf.github.io/izpitni-roki/).

# Prevodi

Stran se zgenerira v vseh jezikih hkrati. Slovenščina ostane na dosedanjem naslovu,
drugi jeziki pa dobijo podmapo s svojo kodo:

```
out/testna_stran.html        slovensko
out/en/testna_stran.html     angleško
out/de/testna_stran.html     nemško
```

Prevodi so v mapi `prevodi`:

| datoteka | kaj je notri |
| --- | --- |
| `vmesnik.json` | napisi na strani, imena programov, letnikov, obdobij in rokov, dnevi in meseci |
| `predmeti.tsv` | imena predmetov, stolpec na jezik (ločilo je tabulator) |

Ključi so povsod **slovenski izvirniki**, natanko taki, kot se pojavijo v `.ics`
datotekah. Isti ključi gredo na strani v atribut `data-ime`, zato je povezava
s filtri (permalink) v vseh jezikih enaka: povezava, narejena v angleščini,
odpre isto izbiro na slovenski strani.

## Kaj je napaka in kaj ne

Da prevod ne more tiho izginiti, je generiranje strogo:

* **prazna vrednost ni napaka.** Namesto nje se izpiše slovenska, tako da je
  stran uporabna, še preden je vse prevedeno.
* **nepoznan ali manjkajoč ključ je napaka**, ki ustavi generiranje. Vsi jeziki
  morajo imeti v `vmesnik.json` natanko iste ključe, na vseh nivojih — tudi
  znotraj `programi`, `letniki`, `obdobja` in `roki`.
* **predmet, program, letnik ali obdobje brez vnosa je napaka.** Če se v koledarju
  pojavi nov predmet, generiranje pade, dokler ga ne dodate v `predmeti.tsv`.
  Prevod sme biti prazen, vrstica pa mora biti.
* **nezapolnjen ključ predloge je napaka**, da se na strani ne pojavi `{{gumb_prenos}}`.

Sporočila o napakah povedo, kateri ključ manjka in kje.

## Dodajanje novega jezika

Recimo, da dodajate italijanščino s kodo `it`.

1. **`izpitni_roki/jezik.py`** — kodo dodajte v seznam `JEZIKI`.

2. **`prevodi/vmesnik.json`** — dodajte blok `"it": { ... }` z **natanko istimi
   ključi kot `"sl"`**. Vrednosti so lahko prazni nizi, razen:

   * `dnevi` — sedem imen dni, od ponedeljka,
   * `meseci` — dvanajst imen mesecev,
   * `oblika_datuma` — npr. `{dan}. {mesec} {leto} ({dan_v_tednu})`; uporabite
     lahko le polja `dan`, `mesec`, `leto` in `dan_v_tednu`,
   * `znak_portreta` — znak, ki se pokaže ob postanku z miško na portretu.

3. **`prevodi/predmeti.tsv`** — dodajte stolpec. Pozor: **v glavo mora priti koda
   jezika** in glava mora biti natanko enaka seznamu `JEZIKI`, vključno z vrstnim
   redom. Vsaka vrstica mora imeti enako število stolpcev, celice pa smejo ostati
   prazne.

4. **`out/portreti/it.jpg`** — portret za gumb za preklop jezika. Imena portretov
   morajo biti natanko jeziki iz prevodov, sicer test pade.

5. **`testi/`** — nekaj testov si zapomni, da so jeziki trije; popravite jih, da
   bodo govorili o štirih (`test_poznamo_tri_jezike`, `test_vsak_portret_ima_znak`
   in pomožni `vmesnik()` v `test_preverjanje_prevodov.py`).

6. Neobvezno: **naslov in opis strani** sta lastna vsaki strani posebej, zato ju
   v `vmesnik.json` ni. Podata se kot slovar po jezikih v `naredi_testno_stran.py`
   in `pozeni.py`.

Nato poženite

```
python -m unittest discover -s testi -t .
python naredi_testno_stran.py
```

Če gre oboje skozi, se je pojavila nova mapa `out/it` in gumb za nov jezik.
V objavo na splet je ni treba dodajati posebej: `.github/workflows/pages.yml`
prekopira vse jezikovne podmape, ki jih najde.

# Prenos kode k sebi

Za elegantno pridobivanje posodobitev kode na lokalni računalnik ali objavljanje svojih posodobitev
kode na centralni repozitorij tukaj na githubu, potrebujete na računalniku nameščen [git](https://git-scm.com/downloads).

## Kloniranje repozitorija

Na osnovni strani projekta (`https://github.com/ul-fmf/izpitni-roki`) kliknite na gumb Code ter, **če se le da**, skopirajte povezavo in nato klonirajte repozitorij, tako da v ukazni vrstici izvedete ukaz

```
neka_mapa>git clone https://github.com/ul-fmf/izpitni-roki.git
```

Za ta ukaz je treba imeti nameščen `git`. To vam v mapi `neka_mapa` ustvari novo mapo `izpitni-roki`.

**Če se ne da**, si lahko kodo prenesete tudi kot `zip` arhiv, a v tem primeru velja enako opozorilo kot na strani z izpiti: morebitne kasnejše spremembe kode na tem repozitoriju se v vaši osebni kopiji ne bodo poznale, prav tako pa ne boste mogli tu objaviti svojih izboljšav.

## Nadaljnje pridobivanje posodobitev

Če ne uporabljate gita, morate ponovno prenesti `zip` arhiv in povoziti vse obstoječe datoteke. Če ga, je precej lažje.
V ukazni vrstici se premaknite v mapo, kjer se nahaja vaš lokalni klon repozitorija, in izvedite naslednji ukaz:

```
neka_mapa/izpitni-roki>git pull
```

To na vaš računalnik povleče vse posodobitve, ki so bile na centralnem repozitoriju objavljene v vmesnem času.
Če boste vmes spreminjali svojo kodo, ne da bi te spremembe zabeležili, boste naleteli na napako (glej spodaj).

# Pošiljanje lastnih posodobitev na centralni repozitorij

Ker ste nekoč med `problematicna_imena.txt` na svojem računalniku dodali Janeza Vajkarda Valvasorja,
je dobro, da to spremembo zabeležite. To storite tako, da v ukazni vrstici izvedete ukaza

```
neka_mapa/izpitni-roki>git add -A
neka_mapa/izpitni-roki>git commit -m "Posodobljena imena"
```

Prvi ukaz obvesti `git`, da želite dodati vse dosedanje spremembe (`A` kot `all`).
Namesto tega bi lahko rekli tudi `git add pot/do/popravljene/datoteke` za vsako datoteko posebej.

Drugi ukaz spremembo dejansko zabeleži, skupaj s kratkim opisom sprememb (`m` kot `message`).
Ko so spremembe zabeležene, izvedemo

```
neka_mapa/izpitni-roki>git push
```

kar potisne spremembe na cetralni repozitorij ...

## .. razen če ne

Lahko se namreč zgodi, da bo vaš potisk zavrnjen, saj je vmes nekdo drug na centralni repozitorij že potisnil svoje spremembe.
Ker `git` ne more čisto sam vedeti, kako naj združi vaše in tuje spremembe, morate to narediti sami. Zato je zdravo pred
`push`em izvesti preventivni `git pull`, ki bo s centralnega repozitorija pobral morebitne spremembe.

Ko se bo `pull` izvedel, bo - če se le da - git sam poskrbel za združevanje. Če ne bo vedel, kaj storiti, bo javil konflikt
(ang. _merge conflict_), ki ga morate razrešiti sami. To ni nič takega. Odprite problematično datoteko in jo uredite.

