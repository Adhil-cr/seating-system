function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i += 1) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === `${name}=`) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", function () {

    const generateBtn = document.getElementById("generate-btn");
    const examSelect = document.getElementById("exam-select");
    const csrfToken = getCookie("csrftoken");
    const hallList = document.getElementById("hall-list");
    const totalSeatsEl = document.getElementById("total-seats");
    const totalStudentsEl = document.getElementById("total-students");
    const studentCountDiv = document.getElementById("student-count");
    let examsCache = [];

    async function loadExams() {
        const response = await fetch("/api/exams/list/", {
            credentials: "same-origin"
        });
        const exams = await response.json().catch(() => []);
        examsCache = Array.isArray(exams) ? exams : [];

        examSelect.innerHTML = "";

        if (examsCache.length === 0) {
            const option = document.createElement("option");
            option.value = "";
            option.textContent = "No exams available";
            examSelect.appendChild(option);
        } else {
            examsCache.forEach(exam => {
                const option = document.createElement("option");
                option.value = exam.id;
                option.textContent = exam.name;
                examSelect.appendChild(option);
            });
        }

        updateStudentCount();
    }

    async function loadHalls() {
        if (!hallList) return;

        const response = await fetch("/api/halls/list/", {
            credentials: "same-origin"
        });
        const halls = await response.json().catch(() => []);

        hallList.innerHTML = "";

        if (!Array.isArray(halls) || halls.length === 0) {
            const empty = document.createElement("div");
            empty.className = "capacity-text";
            empty.textContent = "No halls configured yet.";
            hallList.appendChild(empty);
            updateTotalSeats();
            return;
        }

        halls.forEach(hall => {
            const label = document.createElement("label");
            const input = document.createElement("input");
            input.type = "checkbox";
            input.value = hall.id;
            input.dataset.capacity = hall.capacity || (hall.rows * hall.columns * hall.seats_per_bench);
            input.checked = true;
            label.appendChild(input);
            label.append(` ${hall.name}`);
            hallList.appendChild(label);
        });
        updateTotalSeats();
    }

    function updateStudentCount() {
        const selectedId = String(examSelect.value || "");
        const exam = examsCache.find(e => String(e.id) === selectedId);
        const count = exam && typeof exam.student_count === "number" ? exam.student_count : 0;

        if (studentCountDiv) {
            studentCountDiv.innerText = `Total Students: ${count}`;
        }
        if (totalStudentsEl) {
            totalStudentsEl.textContent = count;
        }
    }

    function updateTotalSeats() {
        if (!hallList || !totalSeatsEl) return;
        let totalSeats = 0;
        const inputs = hallList.querySelectorAll("input[type=\"checkbox\"]");
        inputs.forEach(input => {
            if (input.checked) {
                totalSeats += parseInt(input.dataset.capacity || "0", 10);
            }
        });
        totalSeatsEl.textContent = totalSeats;
    }

    if (examSelect) {
        examSelect.addEventListener("change", updateStudentCount);
    }

    if (hallList) {
        hallList.addEventListener("change", updateTotalSeats);
    }

    if (generateBtn) {
        generateBtn.addEventListener("click", async function () {

            const examId = examSelect.value;
            if (!examId) {
                alert("Please select an exam.");
                return;
            }
            const selectedHalls = [];
            if (hallList) {
                hallList.querySelectorAll("input[type=\"checkbox\"]:checked").forEach(input => {
                    selectedHalls.push(parseInt(input.value, 10));
                });
            }
            if (selectedHalls.length === 0) {
                alert("Please select at least one hall.");
                return;
            }

            const response = await fetch("/api/seating/generate/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                credentials: "same-origin",
                body: JSON.stringify({
                    exam_id: examId,
                    selected_halls: selectedHalls
                })
            });

            const data = await response.json().catch(() => ({}));

            if (response.ok) {
                alert("Seating generated successfully");
            } else {
                alert(data.error || `Generation failed (${response.status})`);
            }
        });
    }

    loadExams();
    loadHalls();

});
