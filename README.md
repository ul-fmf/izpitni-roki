# Izpitni roki

Koda, ki zgenerira spletno stran z izpitnimi roki. Zdaj tudi koda, ki preveri skladnost rokov s pravili.

# Dokumentacija

je dostopna [tukaj](https://ul-fmf.github.io/izpitni-roki/).

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

