$(document).on('click', '.allow-focus', function (e) {
  e.stopPropagation();
});

$(".opcija").on("click", function() {
   $(this).closest("li").toggleClass("active");
});

$(".group-choice").on("click", function() {
    const classList = $(this).closest("li").attr("class").split(/\s+/);
    const pikaRazred = "." + $(this).attr("data-group");
    let isActive = false;
    for (let i = 0; i < classList.length; i++) {
        if (classList[i] === 'active') {
            isActive = true;
            break;
        }
    }
    if (isActive){
        $(pikaRazred).removeClass("active");
        $(this).text("Izberi vse");
    } else {
        $(pikaRazred).addClass("active");
        $(this).text("Odstrani vse");
    }
});

