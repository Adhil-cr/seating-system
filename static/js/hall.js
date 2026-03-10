const rowsInput = document.getElementById("rows");
const colsInput = document.getElementById("cols");
const seatsBench = document.getElementById("seatsPerBench");
const capacityDisplay = document.getElementById("capacity");

function calculateCapacity() {

    const rows = parseInt(rowsInput.value) || 0;
    const cols = parseInt(colsInput.value) || 0;
    const seats = parseInt(seatsBench.value) || 0;

    const total = rows * cols * seats;

    capacityDisplay.innerText = total;
}

rowsInput.addEventListener("input", calculateCapacity);
colsInput.addEventListener("input", calculateCapacity);
seatsBench.addEventListener("change", calculateCapacity);