document.addEventListener("DOMContentLoaded", function () {

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

    const uploadBtn = document.getElementById("upload-btn");
    const fileInput = document.getElementById("csv-file");
    const csrfToken = getCookie("csrftoken");

    if (!uploadBtn || !fileInput) return;

    uploadBtn.addEventListener("click", async function () {

        const file = fileInput.files[0];

        if (!file) {
            alert("Please select a CSV file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("/api/students/upload/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken
            },
            credentials: "same-origin",
            body: formData
        });

        const data = await response.json().catch(() => ({}));

        if (response.ok) {
            if (typeof data.total_students === "number") {
                alert(`Students uploaded successfully. Total: ${data.total_students}`);
            } else {
                alert("Students uploaded successfully");
            }
        } else {
            alert(data.error || `Upload failed (${response.status})`);
        }

    });

});
