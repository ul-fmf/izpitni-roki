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

function contains(list, element){
    for (let i = 0; i < list.length; i++) {
        if (list[i] === element) {
            return true;
        }
    }
    return false;
}


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
                // preveri tudi letnik
                dopolniloOK = contains(getClasses($("#" + razbiteSkupine[2][j])), "active");
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
    const vsi = $("." + razred);
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

