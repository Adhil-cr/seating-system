document.addEventListener("DOMContentLoaded", function () {

    const saveBtn = document.getElementById("save-exam-btn");

    if (!saveBtn) return;

    saveBtn.addEventListener("click", async function () {

        const name = document.getElementById("exam-name").value;
        const date = document.getElementById("exam-date").value;
        const subjects = document.getElementById("subject-codes").value;

        if (!name || !date || !subjects) {
            alert("Please fill all fields");
            return;
        }

        const subjectList = subjects.split(",").map(s => s.trim());

        try {

            const response = await fetch("/api/exams/create/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: name,
                    date: date,
                    subjects: subjectList
                })
            });

            const data = await response.json();

            if (response.ok) {
                alert("Exam created successfully");
            } else {
                alert(data.error || "Failed to create exam");
            }

        } catch (error) {
            console.error(error);
            alert("Server error");
        }

    });

});
