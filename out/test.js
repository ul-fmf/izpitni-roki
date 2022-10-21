const ODSTRANI_VSE = "Odstrani vse";
const IZBERI_VSE = "Izberi vse";

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
    if ($(this).text() === ODSTRANI_VSE){
        $(pikaRazred).removeClass("active");
        $(this).text(IZBERI_VSE);
    } else {
        $(pikaRazred).addClass("active");
        $(this).text(ODSTRANI_VSE);
    }
    posodobiGrupnoIzbiro(razred);
    posodobiTabeloIzbranih();
});


function najPrikazem(seznamSkupinID) {
    for (let i = 0; i < seznamSkupinID.length; i++){
        let vsajEn = false;
        let skupina = seznamSkupinID[i].split("x");
        for (let j = 0; j < skupina.length; j++){
            let kandidat = skupina[j];
            if(contains(getClasses($("#" + kandidat)), "active")){
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
    const filter = "." + razred + ".active";
    const n = $(filter).length;
    const gumbID = "#gumb_" + razred;
    const grupaID = "#grupa_" + razred;
    if (n > 0){
        $(grupaID).text(ODSTRANI_VSE);
        $(gumbID).removeClass("btn-secondary");
        $(gumbID).addClass("btn-success");
    } else{
        $(grupaID).text(IZBERI_VSE);
        $(gumbID).removeClass("btn-success");
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

    // window.open( "data:text/calendar;charset=utf8," + escape(icsVsebina), "abc");
});

