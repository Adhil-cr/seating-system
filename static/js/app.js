/* =========================
   Initialize Lucide Icons
========================= */
document.addEventListener("DOMContentLoaded", function () {

    if (window.lucide) {
        lucide.createIcons();
    }

    setActiveSidebar();

});


/* =========================
   Page Navigation
========================= */

function showPage(page) {

    const routes = {
        dashboard: "../dashboard/dashboard.html",
        students: "../students/upload.html",
        config: "../exams/config.html",
        generate: "../seating/generate.html",
        viewer: "../seating/view.html",
        profile: "../profile/profile.html"
    };

    if (routes[page]) {
        window.location.href = routes[page];
    }

}


/* =========================
   Sidebar Active Highlight
========================= */

function setActiveSidebar() {

    const path = window.location.pathname;

    const map = {
        "dashboard": "dashboard",
        "upload": "students",
        "config": "config",
        "generate": "generate",
        "view": "viewer",
        "profile": "profile"
    };

    let current = "";

    Object.keys(map).forEach(key => {
        if (path.includes(key)) {
            current = map[key];
        }
    });

    const items = document.querySelectorAll(".menu-item");

    items.forEach(item => {

        if (item.dataset.page === current) {
            item.classList.add("active");
        }

    });

}


/* =========================
   Toast Notification
========================= */

function showToast(message) {

    const toast = document.getElementById("toast");

    if (!toast) return;

    toast.innerText = message;
    toast.classList.remove("hidden");
    toast.classList.add("show");

    setTimeout(() => {

        toast.classList.remove("show");
        toast.classList.add("hidden");

    }, 3000);

}