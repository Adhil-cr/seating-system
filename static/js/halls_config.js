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

    const addBtn = document.getElementById("save-hall-btn");
    const saveAllBtn = document.getElementById("save-halls-btn");
    const hallList = document.getElementById("hall-list");
    const csrfToken = getCookie("csrftoken");

    if (!addBtn || !saveAllBtn || !hallList) return;

    function getHallData(form) {
        const name = form.querySelector(".hall-name")?.value?.trim();
        const rows = form.querySelector(".hall-rows")?.value;
        const columns = form.querySelector(".hall-columns")?.value;
        const seatsPerBench = form.querySelector(".hall-seats-per-bench")?.value;

        return { name, rows, columns, seatsPerBench };
    }

    function clearHallData(form) {
        form.querySelector(".hall-name").value = "";
        form.querySelector(".hall-rows").value = "";
        form.querySelector(".hall-columns").value = "";
        form.querySelector(".hall-seats-per-bench").value = "1";
    }

    function cloneHallForm() {
        const templateItem = hallList.querySelector(".hall-item");
        if (!templateItem) return;

        const clone = templateItem.cloneNode(true);
        const cloneForm = clone.querySelector(".hall-form");

        clone.querySelectorAll("[id]").forEach(el => {
            el.removeAttribute("id");
        });

        clearHallData(cloneForm);
        hallList.appendChild(clone);
        updateHallTitles();
    }

    addBtn.addEventListener("click", function () {
        cloneHallForm();
    });

    function updateHallTitles() {
        const items = hallList.querySelectorAll(".hall-item");
        items.forEach((item, index) => {
            const title = item.querySelector(".hall-item-title");
            if (title) {
                title.textContent = `Hall ${index + 1}`;
            }
        });
    }

    updateHallTitles();

    saveAllBtn.addEventListener("click", async function () {

        const forms = Array.from(hallList.querySelectorAll(".hall-form"));
        if (forms.length === 0) {
            alert("Please add at least one hall");
            return;
        }

        const payloads = [];
        for (const form of forms) {
            const { name, rows, columns, seatsPerBench } = getHallData(form);
            if (!name || !rows || !columns || !seatsPerBench) {
                alert("Please fill all fields");
                return;
            }
            payloads.push({
                name,
                rows,
                columns,
                seats_per_bench: seatsPerBench
            });
        }

        let successCount = 0;
        for (const payload of payloads) {
            try {
                const response = await fetch("/api/halls/create/", {
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
                    successCount += 1;
                } else {
                    alert(data.error || `Failed to create hall (${response.status})`);
                    return;
                }
            } catch (error) {
                console.error(error);
                alert("Server error");
                return;
            }
        }

        alert(`Saved ${successCount} hall(s) successfully`);
    });

});
