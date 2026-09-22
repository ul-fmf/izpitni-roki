// Letnik rokov pri programih, ki letnikov nimajo (npr. magistrski študij).
// Ujemati se mora z Letnik.ID_BREZ_LETNIKA v izpitni_roki/osnovno.py.
const ID_BREZ_LETNIKA = "brezletnika";

// Vse skupine filtrov, po vrsti, kot nastopajo v id-ju izpitne vrstice.
const SKUPINE = ["predmet", "program", "letnik", "rok", "izvajalec", "obdobje"];

const ODSTRANI_VSE = "Odstrani vse";
const ODSTRANI_VSA = "Odstrani vsa";
const IZBERI_VSE = "Izberi vse";
const IZBERI_VSA = "Izberi vsa";

$(document).on('click', '.allow-focus', function (e) {
  e.stopPropagation();
});

function getClasses(node){
    return node.attr("class").split(/\s+/);
}

// V dvonivojskih menijih ima razred skupine (npr. .predmet) tudi <li> vsake
// crke, ne le posamezne moznosti. Kadar nas zanimajo moznosti, moramo zato
// dodati se .moznost, sicer jih presteje prevec.
function moznosti(razred){
    return $("li." + razred + ".moznost");
}

// <li> crke je aktiven natanko tedaj, ko je aktivna vsaj ena moznost v njem.
function osveziSkupineCrk(razred){
    $("li." + razred + ":not(.moznost)").each(function(){
        const imaAktivne = $(this).find("li." + razred + ".moznost.active").length > 0;
        $(this).toggleClass("active", imaAktivne);
    });
}

function contains(list, element){
    for (let i = 0; i < list.length; i++) {
        if (list[i] === element) {
            return true;
        }
    }
    return false;
}


// Sidra v menijih imajo href="#!" le zaradi videza; podmeniji se odpirajo na
// :hover. Brez preventDefault bi klik nastavil fragment na "#!" in povozil
// permalink, ki smo ga pravkar zapisali (issue #7).
$(".dropdown-menu a[href='#!']").on("click", function(e) {
    e.preventDefault();
});

$(".opcija").on("click", function() {
    $(this).closest("li").toggleClass("active");
    // aktivnost grupe
    const thisDropDownGroup = $(this).closest("li").closest("ul.dropdown-menu");
    const potentialGroupParent = thisDropDownGroup.closest("li");
    if (potentialGroupParent.length > 0){
        const nActiveInGroup = thisDropDownGroup.children(".active").length;
        if (nActiveInGroup > 0){
            potentialGroupParent.addClass("active");
        } else {
            potentialGroupParent.removeClass("active");
        }
    }
    posodobiGrupnoIzbiro($(this).attr("data-group"));
    posodobiTabeloIzbranih();
    zapisiStanjeVUrl();
});

$(".group-choice").on("click", function() {
    const razred = $(this).attr("data-group");
    const pikaRazred = "." + razred;
    const trenutniNapis = $(this).text();
    if (trenutniNapis === ODSTRANI_VSE || trenutniNapis === ODSTRANI_VSA){
        $(pikaRazred).removeClass("active");
        if (trenutniNapis === ODSTRANI_VSE){
            $(this).text(IZBERI_VSE);
        } else {
            $(this).text(IZBERI_VSA);
        }

    } else {
        $(pikaRazred).addClass("active");
        if (trenutniNapis === IZBERI_VSE){
            $(this).text(ODSTRANI_VSE);
        } else {
            $(this).text(ODSTRANI_VSA);
        }
    }
    posodobiGrupnoIzbiro(razred);
    posodobiTabeloIzbranih();
    zapisiStanjeVUrl();
});


function najPrikazem(seznamSkupinID) {
    // Skupin je šest [id_predmet, id_programi, id_letniki, id_rok, id_izvajalci, id_obdobje]
    // npr. [38, 6x122x123, 7x45x7, 20, 39x40x24, 2]
    // Pri preverjanju je treba programe in letnike preverjati hkrati, saj je
    // npr. Programiranje 1 v 3. letniku Pedagoške matematike in 2. letniku Matematike.
    let razbiteSkupine = [];
    for (let i = 0; i < seznamSkupinID.length; i++){
        razbiteSkupine.push(seznamSkupinID[i].split("x"));
    }
    for (let i = 0; i < seznamSkupinID.length; i++){
        if (i == 2){
            // letnike preverjamo s programi
            continue;
        }
        let vsajEn = false;
        let skupina = razbiteSkupine[i];
        for (let j = 0; j < skupina.length; j++){
            let kandidat = skupina[j];
            let kandidatOK = contains(getClasses($("#" + kandidat)), "active");
            let dopolniloOK = true;
            if (i == 1){
                // preveri tudi letnik, razen pri programih brez letnikov
                // (ti filtra po letnikih ne upoštevajo)
                let idLetnika = razbiteSkupine[2][j];
                dopolniloOK = idLetnika === ID_BREZ_LETNIKA
                    || contains(getClasses($("#" + idLetnika)), "active");
            }
            if(kandidatOK && dopolniloOK){
                vsajEn = true;
                break;
            }
        }
        if (! vsajEn){
            return false;
        }
    }
    return true;
}

function posodobiTabeloIzbranih(){
    let idIzpitnihVrstic = $.map($(".izpitna-vrstica"), function(vrsta){return $(vrsta).attr("id")});
    for (let i = 0; i < idIzpitnihVrstic.length; i++){
        let zdaj = "#" + idIzpitnihVrstic[i];
        if (najPrikazem(idIzpitnihVrstic[i].split("_"))){
            $(zdaj).removeAttr("hidden");
        } else {
            $(zdaj).attr("hidden", "");
        }
    }
}

function posodobiGrupnoIzbiro(razred) {
    const vsi = moznosti(razred);
    const nVsi = vsi.length;
    const nAktivni = vsi.filter(".active").length;
    const gumbID = "#gumb_" + razred;
    const grupaID = "#grupa_" + razred;
    const srednjiSpol = $(grupaID).text().endsWith("a");
    if (nAktivni > 0){
        if (srednjiSpol){
            // Odstrani/dodaj vsa
            $(grupaID).text(ODSTRANI_VSA);
        } else {
            // ... vse
            $(grupaID).text(ODSTRANI_VSE);
        }

        $(gumbID).removeClass("btn-secondary");
        if (nAktivni < nVsi){
            $(gumbID).removeClass("btn-success");
            $(gumbID).addClass("btn-warning");
        } else {
            $(gumbID).removeClass("btn-warning");
            $(gumbID).addClass("btn-success");
        }
    } else{
        if (srednjiSpol){
            $(grupaID).text(IZBERI_VSA);
        } else {
            $(grupaID).text(IZBERI_VSE);
        }
        $(gumbID).removeClass("btn-success");
        $(gumbID).removeClass("btn-warning");
        $(gumbID).addClass("btn-secondary");
    }
}

$(".izvoz-koledarja").on("click", function() {
    let opisDogodkov = $.map(
        $(".izpitna-vrstica:visible"),
        function(vrsta){
            return $(vrsta).attr("data-ics").split("@@@@");
        }
        ).join("\n");
    let opisKoledarja = $(".table.izpiti").attr("data-ics").replaceAll("@@@@", "\n") + "\n";
    let icsVsebina = "BEGIN:VCALENDAR\n" + opisKoledarja + opisDogodkov + "\nEND:VCALENDAR\n";

    var element = document.createElement('a');
    element.setAttribute('href', "data:text/calendar;charset=utf8," + encodeURIComponent(icsVsebina));
    element.setAttribute('download', "izbrani_izpiti.ics");
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
});


// --- Permalinki (issue #7) ---------------------------------------------------

// Trenutno izbiro zapisemo v fragment url-ja (za #). Fragment nikoli ne potuje do
// streznika, zato deluje tudi na GitHub Pages in ne vpliva na predpomnjenje.

function imeMoznosti(){
    return $(this).attr("data-ime");
}

function zapisiStanjeVUrl(){
    const skupine = SKUPINE.map(function(razred){
        const vse = moznosti(razred);
        return {
            razred: razred,
            izbrani: vse.filter(".active").map(imeMoznosti).get(),
            neizbrani: vse.not(".active").map(imeMoznosti).get()
        };
    });
    const zapis = Permalink.zakodiraj(skupine);
    // Vedno gradimo iz same poti: tako morebitni query string iz vhodne
    // povezave ne prezivi in ne prepise izbire ob ponovnem nalaganju.
    const naslov = zapis ? location.pathname + "#" + zapis : location.pathname;
    try {
        history.replaceState(null, "", naslov);
    } catch (e) {
        // npr. file:// v nekaterih brskalnikih: permalink ne deluje, stran pa se vedno
    }
}

// Preberemo fragment; ce ga ni, poskusimo se z query stringom, da delujejo tudi
// povezave oblike ".../?program=1Mate".
function stanjeIzUrl(){
    const izFragmenta = location.hash.replace(/^#/, "");
    return Permalink.odkodiraj(izFragmenta || location.search.replace(/^\?/, ""));
}

function uveljaviStanjeIzUrl(){
    const stanje = stanjeIzUrl();
    SKUPINE.forEach(function(razred){
        const zapis = stanje[razred];
        if (zapis !== undefined){
            moznosti(razred).each(function(){
                const jeNasteta = contains(zapis.imena, $(this).attr("data-ime"));
                $(this).toggleClass("active", zapis.preskoci ? !jeNasteta : jeNasteta);
            });
            osveziSkupineCrk(razred);
        }
        posodobiGrupnoIzbiro(razred);
    });
    posodobiTabeloIzbranih();
    zapisiStanjeVUrl();
}

$(uveljaviStanjeIzUrl);
