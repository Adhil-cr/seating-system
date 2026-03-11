document.addEventListener("DOMContentLoaded", function () {

    const capacityDisplay = document.getElementById("capacity");
    const hallList = document.getElementById("hall-list");

    if (!capacityDisplay || !hallList) return;

    function calculateCapacity() {

        let total = 0;
        const halls = hallList.querySelectorAll(".hall-form");

        halls.forEach(form => {
            const rows = parseInt(form.querySelector(".hall-rows")?.value, 10) || 0;
            const cols = parseInt(form.querySelector(".hall-columns")?.value, 10) || 0;
            const seats = parseInt(form.querySelector(".hall-seats-per-bench")?.value, 10) || 0;
            total += rows * cols * seats;
        });

        capacityDisplay.innerText = total;
    }

    hallList.addEventListener("input", calculateCapacity);
    hallList.addEventListener("change", calculateCapacity);

    calculateCapacity();
});
