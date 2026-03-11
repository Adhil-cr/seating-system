document.addEventListener("DOMContentLoaded", function () {

    const generateBtn = document.getElementById("generate-btn");
    const examSelect = document.getElementById("exam-select");

    async function loadExams() {

        const response = await fetch("/api/exams/list/");
        const exams = await response.json();

        exams.forEach(exam => {
            const option = document.createElement("option");
            option.value = exam.id;
            option.textContent = exam.name;
            examSelect.appendChild(option);
        });
    }

    generateBtn.addEventListener("click", async function () {

        const examId = examSelect.value;

        const response = await fetch("/api/seating/generate/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                exam_id: examId
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert("Seating generated successfully");
        } else {
            alert(data.error || "Generation failed");
        }

    });

    loadExams();

});
