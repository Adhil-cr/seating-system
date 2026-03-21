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
    const modal = document.getElementById("alloc-modal");
    const modalSubject = document.getElementById("alloc-modal-subject");
    const modalError = document.getElementById("alloc-modal-error");
    const modalIssue = document.getElementById("alloc-modal-issue");
    const modalSubjects = document.getElementById("alloc-modal-subjects");
    const modalSubjectCount = document.getElementById("alloc-modal-subject-count");
    const modalLimit = document.getElementById("alloc-modal-limit");
    const modalApply = document.getElementById("alloc-modal-apply");
    const modalClose = document.getElementById("alloc-modal-close");
    const modalLast = document.getElementById("alloc-modal-last");
    const modalRec = document.getElementById("alloc-modal-rec");
    const modalReset = document.getElementById("alloc-modal-reset");
    const modalSubjectCap = document.getElementById("alloc-modal-subject-cap");
    let examsCache = [];
    let lastPayload = null;
    let lastExamId = null;

    function limitStorageKey(examId) {
        return `seating_limit_exam_${examId}`;
    }

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

    function openModal(subjectCode, errorMessage, subjectCodes, subjectCounts, examId) {
        if (!modal) return;
        if (modalSubject) {
            modalSubject.textContent = subjectCode || "this subject";
        }
        if (modalIssue) {
            modalIssue.textContent = errorMessage || "Seating allocation failed. Please review the subject distribution limit.";
        }
        if (modalSubjects) {
            modalSubjects.innerHTML = "";
            if (Array.isArray(subjectCodes) && subjectCodes.length) {
                const label = document.createElement("div");
                label.style.fontSize = "12px";
                label.style.color = "#6b6b6b";
                label.style.marginBottom = "4px";
                label.textContent = "Session subjects:";
                modalSubjects.appendChild(label);

                const chips = document.createElement("div");
                chips.className = "alloc-modal-subjects";
                subjectCodes.forEach(code => {
                    const chip = document.createElement("span");
                    chip.className = "alloc-subject-chip";
                    if (subjectCode && String(code) === String(subjectCode)) {
                        chip.classList.add("danger");
                    }
                    const count = subjectCounts && typeof subjectCounts[String(code)] === "number"
                        ? subjectCounts[String(code)]
                        : null;
                    chip.textContent = count !== null ? `${code} (${count})` : code;
                    chips.appendChild(chip);
                });
                modalSubjects.appendChild(chips);
            } else {
                modalSubjects.textContent = "Session subjects: —";
            }
        }
        const subjectCount = subjectCounts && typeof subjectCounts[String(subjectCode)] === "number"
            ? subjectCounts[String(subjectCode)]
            : null;
        if (modalSubjectCount) {
            modalSubjectCount.textContent = subjectCount !== null
                ? `Students in subject ${subjectCode}: ${subjectCount}`
                : "";
        }
        if (modalError) {
            modalError.textContent = errorMessage || "";
        }
        if (modalLimit) {
            const saved = examId ? localStorage.getItem(limitStorageKey(examId)) : "";
            modalLimit.value = saved || "";
        }
        if (modalLast) {
            const saved = examId ? localStorage.getItem(limitStorageKey(examId)) : "";
            modalLast.textContent = saved ? `Last tried limit: ${saved}` : "";
        }
        if (modalRec) {
            const hallsSelected = lastPayload?.selected_halls?.length || 0;
            if (subjectCount !== null && hallsSelected > 0) {
                const recommended = Math.ceil(subjectCount / hallsSelected);
                modalRec.innerHTML = `Recommended limit: <span>${recommended}</span> (based on ${hallsSelected} halls)`;
            } else {
                modalRec.textContent = "";
            }
        }
        if (modalSubjectCap) {
            const hallsSelected = lastPayload?.selected_halls?.length || 0;
            if (subjectCount !== null && hallsSelected > 0) {
                const perHall = Math.ceil(subjectCount / hallsSelected);
                modalSubjectCap.textContent = `Hall capacity per subject (est.): ${perHall}`;
            } else {
                modalSubjectCap.textContent = "";
            }
        }
        modal.classList.add("open");
    }

    function closeModal() {
        modal?.classList.remove("open");
        if (modalError) modalError.textContent = "";
    }

    async function submitGenerate(extraPayload) {
        if (!lastPayload) return;
        const payload = { ...lastPayload, ...extraPayload };
        const response = await fetch("/api/seating/generate/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            credentials: "same-origin",
            body: JSON.stringify(payload)
        });

        const data = await response.json().catch(() => ({}));
        if (response.ok) {
            closeModal();
            alert("Seating generated successfully");
            return;
        }

        if (modalError) {
            modalError.textContent = data.error || `Generation failed (${response.status})`;
        } else {
            alert(data.error || `Generation failed (${response.status})`);
        }
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

            lastPayload = {
                exam_id: examId,
                selected_halls: selectedHalls
            };
            lastExamId = examId;

            const response = await fetch("/api/seating/generate/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                credentials: "same-origin",
                body: JSON.stringify(lastPayload)
            });

            const data = await response.json().catch(() => ({}));

            if (response.ok) {
                alert("Seating generated successfully");
                return;
            }

            const errorMessage = data.error || `Generation failed (${response.status})`;
            if (errorMessage.toLowerCase().includes("constraints too strict")) {
                const match = errorMessage.match(/subject\s+([A-Za-z0-9]+)/i);
                const subjectCode = match ? match[1] : "this subject";
                const selectedId = String(examId || "");
                const exam = examsCache.find(e => String(e.id) === selectedId);
                const subjectCodes = exam && Array.isArray(exam.subject_codes) ? exam.subject_codes : [];
                const subjectCounts = exam && exam.subject_counts ? exam.subject_counts : {};
                const friendlyMessage = `Subject-per-hall limit is too strict for ${subjectCode}. We'll still try best‑effort placement if seats are available. You can increase the limit for better distribution.`;
                openModal(subjectCode, friendlyMessage, subjectCodes, subjectCounts, examId);
            } else {
                alert(errorMessage);
            }
        });
    }

    modalClose?.addEventListener("click", closeModal);
    modal?.addEventListener("click", (event) => {
        if (event.target?.dataset?.close === "true") {
            closeModal();
        }
    });
    modalApply?.addEventListener("click", () => {
        const limit = parseInt(modalLimit?.value || "", 10);
        if (!limit || limit <= 0) {
            if (modalError) modalError.textContent = "Enter a valid limit.";
            return;
        }
        if (lastExamId) {
            localStorage.setItem(limitStorageKey(lastExamId), String(limit));
            if (modalLast) modalLast.textContent = `Last tried limit: ${limit}`;
        }
        submitGenerate({ max_subject_per_hall: limit });
    });

    modalReset?.addEventListener("click", () => {
        if (!lastExamId) return;
        localStorage.removeItem(limitStorageKey(lastExamId));
        if (modalLimit) modalLimit.value = "";
        if (modalLast) modalLast.textContent = "";
    });

    loadExams();
    loadHalls();

});
