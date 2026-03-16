document.addEventListener("DOMContentLoaded", function () {

    const examSelect = document.getElementById("exam-select");
    const hallTabs = document.getElementById("hall-tabs");
    const seatingGrid = document.getElementById("seatingGrid");
    const messageEl = document.getElementById("viewer-message");
    const legendEl = document.getElementById("legend");
    const exportPdfBtn = document.getElementById("export-pdf-btn");
    const exportExcelBtn = document.getElementById("export-excel-btn");
    const printBtn = document.getElementById("print-btn");

    if (!examSelect || !hallTabs || !seatingGrid) return;

    let seatingData = null;
    let currentExamId = "";
    const colorClasses = [
        "subject-color-1",
        "subject-color-2",
        "subject-color-3",
        "subject-color-4",
        "subject-color-5",
        "subject-color-6"
    ];
    const departmentColors = {};

    function setMessage(text) {
        if (messageEl) {
            messageEl.textContent = text || "";
        }
    }

    function getDepartmentColor(dept) {
        if (!dept) return "";
        if (!departmentColors[dept]) {
            const index = Object.keys(departmentColors).length % colorClasses.length;
            departmentColors[dept] = colorClasses[index];
        }
        return departmentColors[dept];
    }

    function renderLegend(departments) {
        if (!legendEl) return;
        legendEl.innerHTML = "";
        const unique = Array.from(new Set(departments)).filter(Boolean);
        unique.forEach(dept => {
            const item = document.createElement("div");
            item.className = "legend-item";
            const color = document.createElement("span");
            color.className = `legend-color ${getDepartmentColor(dept)}`;
            item.appendChild(color);
            item.append(` ${dept}`);
            legendEl.appendChild(item);
        });
    }

    function renderHallTabs(halls) {
        hallTabs.innerHTML = "";
        const hallNames = Object.keys(halls);
        if (hallNames.length === 0) {
            setMessage("No seating data available.");
            return;
        }
        hallNames.forEach((name, index) => {
            const btn = document.createElement("button");
            btn.className = `tab${index === 0 ? " active" : ""}`;
            btn.textContent = name;
            btn.addEventListener("click", function () {
                hallTabs.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
                btn.classList.add("active");
                renderHall(name);
            });
            hallTabs.appendChild(btn);
        });
        renderHall(hallNames[0]);
    }

    function renderHall(hallName) {
        if (!seatingData || !seatingData.halls || !seatingData.halls[hallName]) return;
        const hall = seatingData.halls[hallName];
        seatingGrid.innerHTML = "";

        const seatsByPos = {};
        const departments = [];
        hall.seats.forEach(seat => {
            const key = `${seat.row}-${seat.column}`;
            seatsByPos[key] = seat;
            if (seat.department) departments.push(seat.department);
        });

        renderLegend(departments);

        for (let r = 1; r <= hall.rows; r += 1) {
            for (let c = 1; c <= hall.columns; c += 1) {
                const key = `${r}-${c}`;
                const seat = seatsByPos[key];
                const card = document.createElement("div");
                if (seat) {
                    card.className = `seat ${getDepartmentColor(seat.department)}`;
                    card.innerHTML = `
                        ${seat.register_no}<br>
                        <span>${seat.name}</span><br>
                        <small>${seat.department || ""}</small>
                    `;
                } else {
                    card.className = "seat empty";
                    card.textContent = "Empty";
                }
                seatingGrid.appendChild(card);
            }
        }
    }

    async function loadSeating(examId) {
        if (!examId) return;
        currentExamId = examId;
        setMessage("Loading seating...");
        seatingGrid.innerHTML = "";
        hallTabs.innerHTML = "";

        const response = await fetch(`/api/seating/view/?exam_id=${examId}`, {
            credentials: "same-origin"
        });
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            setMessage(data.error || "No seating generated yet.");
            seatingData = null;
            return;
        }

        seatingData = data;
        setMessage("");
        renderHallTabs(data.halls || {});
    }

    async function loadExams() {
        const response = await fetch("/api/exams/list/", {
            credentials: "same-origin"
        });
        const exams = await response.json().catch(() => []);
        examSelect.innerHTML = "";

        if (!Array.isArray(exams) || exams.length === 0) {
            const option = document.createElement("option");
            option.value = "";
            option.textContent = "No exams available";
            examSelect.appendChild(option);
            setMessage("No exams available.");
            return;
        }

        exams.forEach(exam => {
            const option = document.createElement("option");
            option.value = exam.id;
            option.textContent = exam.name;
            examSelect.appendChild(option);
        });

        loadSeating(exams[0].id);
    }

    examSelect.addEventListener("change", function () {
        loadSeating(examSelect.value);
    });

    if (exportPdfBtn) {
        exportPdfBtn.addEventListener("click", function () {
            if (!currentExamId) return;
            window.location.href = `/api/seating/export/pdf/?exam_id=${currentExamId}`;
        });
    }

    if (exportExcelBtn) {
        exportExcelBtn.addEventListener("click", function () {
            if (!currentExamId) return;
            window.location.href = `/api/seating/export/excel/?exam_id=${currentExamId}`;
        });
    }

    if (printBtn) {
        printBtn.addEventListener("click", function () {
            window.print();
        });
    }

    loadExams();

});
