document.addEventListener("DOMContentLoaded", function () {
    const totalStudentsEl = document.getElementById("dash-total-students");
    const totalHallsEl = document.getElementById("dash-total-halls");
    const pendingEl = document.getElementById("dash-pending");
    const lastStatusEl = document.getElementById("dash-last-status");
    const alertsEl = document.getElementById("dashboard-alerts");

    function renderAlerts(alerts) {
        if (!alertsEl) return;
        alertsEl.innerHTML = "";
        if (!alerts || alerts.length === 0) {
            alertsEl.innerHTML = '<div class="alert success">No alerts.</div>';
            return;
        }
        alerts.forEach(alert => {
            const div = document.createElement("div");
            div.className = `alert ${alert.level || "warning"}`;
            div.textContent = alert.message || "Alert";
            alertsEl.appendChild(div);
        });
    }

    async function loadDashboard() {
        try {
            const res = await fetch("/api/dashboard/summary/");
            const data = await res.json();

            if (totalStudentsEl) totalStudentsEl.textContent = data.total_students ?? "0";
            if (totalHallsEl) totalHallsEl.textContent = data.total_halls ?? "0";
            if (pendingEl) pendingEl.textContent = data.pending_allocations ?? "0";
            if (lastStatusEl) {
                lastStatusEl.textContent = data.last_status ?? "Not Generated";
                lastStatusEl.className = `card-status ${data.last_status_class || "warning"}`;
            }

            renderAlerts(data.alerts);
        } catch (err) {
            renderAlerts([{ level: "error", message: "Failed to load dashboard data." }]);
        }
    }

    loadDashboard();
});
