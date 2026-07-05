(function () {
    "use strict";

    var list = document.getElementById("shutdown-order");
    if (!list || typeof Sortable === "undefined") {
        return;
    }

    Sortable.create(list, {
        animation: 150,
        handle: ".drag-handle",
        ghostClass: "operations-sort-ghost",
        chosenClass: "operations-sort-chosen",
        touchStartThreshold: 4,
    });
})();
