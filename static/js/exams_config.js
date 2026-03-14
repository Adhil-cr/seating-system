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

    const saveBtn = document.getElementById("save-exam-btn");
    const csrfToken = getCookie("csrftoken");

    if (!saveBtn) return;

    saveBtn.addEventListener("click", async function () {

        const name = document.getElementById("exam-name").value;
        const date = document.getElementById("exam-date").value;
        const session = document.getElementById("exam-session").value;
        const subjects = document.getElementById("subject-codes").value;

        if (!name || !date || !session || !subjects) {
            alert("Please fill all fields");
            return;
        }

        const subjectList = subjects
            .split(",")
            .map(s => s.trim())
            .filter(Boolean);

        try {

            const response = await fetch("/api/exams/create/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                credentials: "same-origin",
                body: JSON.stringify({
                    name: name,
                    date: date,
                    session: session,
                    subject_codes: subjectList
                })
            });

            const data = await response.json().catch(() => ({}));

            if (response.ok) {
                if (typeof data.total_students === "number") {
                    alert(`Exam created successfully. Total students: ${data.total_students}`);
                } else {
                    alert("Exam created successfully");
                }
            } else {
                alert(data.error || `Failed to create exam (${response.status})`);
            }

        } catch (error) {
            console.error(error);
            alert("Server error");
        }

    });

});
