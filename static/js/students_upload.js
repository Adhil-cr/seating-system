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
    const fileInfo = document.getElementById("file-info");
    const previewContainer = document.getElementById("csv-preview");
    const previewEmpty = document.getElementById("preview-empty");
    const uploadStatus = document.getElementById("upload-status");
    const historyContainer = document.getElementById("upload-history");
    const historyEmpty = document.getElementById("history-empty");
    const csrfToken = getCookie("csrftoken");

    if (!uploadBtn || !fileInput) return;

    function parseCSV(text) {
        const rows = [];
        let current = "";
        let row = [];
        let inQuotes = false;

        for (let i = 0; i < text.length; i += 1) {
            const char = text[i];
            const nextChar = text[i + 1];

            if (char === "\"" && inQuotes && nextChar === "\"") {
                current += "\"";
                i += 1;
                continue;
            }

            if (char === "\"") {
                inQuotes = !inQuotes;
                continue;
            }

            if (char === "," && !inQuotes) {
                row.push(current);
                current = "";
                continue;
            }

            if ((char === "\n" || char === "\r") && !inQuotes) {
                if (current || row.length) {
                    row.push(current);
                    rows.push(row);
                    row = [];
                    current = "";
                }
                continue;
            }

            current += char;
        }

        if (current || row.length) {
            row.push(current);
            rows.push(row);
        }

        return rows;
    }

    function renderPreviewTable(rows) {
        if (!previewContainer) return;
        previewContainer.innerHTML = "";

        if (!rows.length) return;

        const table = document.createElement("table");
        table.className = "table";

        const headerRow = document.createElement("tr");
        rows[0].forEach(cell => {
            const th = document.createElement("th");
            th.textContent = cell.trim();
            headerRow.appendChild(th);
        });
        table.appendChild(headerRow);

        rows.slice(1).forEach(row => {
            const tr = document.createElement("tr");
            row.forEach(cell => {
                const td = document.createElement("td");
                td.textContent = cell.trim();
                tr.appendChild(td);
            });
            table.appendChild(tr);
        });

        previewContainer.appendChild(table);
    }

    async function loadUploadHistory() {
        if (!historyContainer) return;

        const response = await fetch("/api/students/upload-history/", {
            credentials: "same-origin"
        });
        const data = await response.json().catch(() => []);

        historyContainer.innerHTML = "";

        if (!Array.isArray(data) || data.length === 0) {
            if (historyEmpty) historyEmpty.style.display = "block";
            return;
        }

        if (historyEmpty) historyEmpty.style.display = "none";

        const table = document.createElement("table");
        table.className = "table";
        table.innerHTML = `
            <tr>
                <th>Date</th>
                <th>File Name</th>
                <th>Students Imported</th>
                <th>Uploaded By</th>
            </tr>
        `;

        data.forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${item.uploaded_at}</td>
                <td>${item.file_name}</td>
                <td>${item.students_count}</td>
                <td>${item.uploaded_by || "Me"}</td>
            `;
            table.appendChild(tr);
        });

        historyContainer.appendChild(table);
    }

    fileInput.addEventListener("change", function () {
        const file = fileInput.files[0];
        if (!file) return;

        if (fileInfo) {
            const sizeKb = (file.size / 1024).toFixed(1);
            fileInfo.innerHTML = `Selected File: <strong>${file.name}</strong> (${sizeKb} KB) <span style=\"color:#16a34a;\">&#10003;</span>`;
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            const text = e.target.result || "";
            const rows = parseCSV(text).slice(0, 11);
            if (previewEmpty) previewEmpty.style.display = "none";
            renderPreviewTable(rows);
        };
        reader.readAsText(file);
    });

    uploadBtn.addEventListener("click", async function () {

        const file = fileInput.files[0];

        if (!file) {
            alert("Please select a CSV file.");
            return;
        }

        uploadBtn.disabled = true;
        if (uploadStatus) uploadStatus.textContent = "Uploading...";

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
            if (uploadStatus) {
                uploadStatus.textContent = `Upload successful. ${data.total_students || 0} students imported.`;
            }
            await loadUploadHistory();
        } else {
            if (uploadStatus) {
                uploadStatus.textContent = data.error || `Upload failed (${response.status})`;
            }
        }

        uploadBtn.disabled = false;
    });

    loadUploadHistory();

});
