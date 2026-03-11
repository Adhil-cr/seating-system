document.addEventListener("DOMContentLoaded", function () {

    const uploadBtn = document.getElementById("upload-btn");
    const fileInput = document.getElementById("csv-file");

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
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            alert("Students uploaded successfully");
        } else {
            alert(data.error || "Upload failed");
        }

    });

});
