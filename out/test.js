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
    if (potentialGroupParent.length === 0){
        return;
    }
    const nActiveInGroup = thisDropDownGroup.children(".active").length;
    if (nActiveInGroup > 0){
        potentialGroupParent.addClass("active");
    } else {
        potentialGroupParent.removeClass("active");
    }



});

$(".group-choice").on("click", function() {
    const classList = getClasses($(this).closest("li"));
    const pikaRazred = "." + $(this).attr("data-group");
    let isActive = contains(classList, 'active');
    if (isActive){
        $(pikaRazred).removeClass("active");
        $(this).text("Izberi vse");
    } else {
        $(pikaRazred).addClass("active");
        $(this).text("Odstrani vse");
    }
});

