/* ==============================================================================
   BenchMap Global Application Script (app.js)
   ============================================================================== */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Initialize Lucide Icons
    if (window.lucide) {
        lucide.createIcons();
    }

    // 2. Set active sidebar menu item
    setActiveSidebar();

    // 3. Setup Mobile Drawer Navigation
    setupMobileDrawer();
});

/* ==============================================================================
   Sidebar Active State Detection
   ============================================================================== */
function setActiveSidebar() {
    const path = window.location.pathname;

    const map = {
        "dashboard": "dashboard",
        "upload": "students",
        "students": "students",
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
        } else {
            item.classList.remove("active");
        }
    });
}

/* ==============================================================================
   Mobile Off-Canvas Drawer Navigation
   ============================================================================== */
function setupMobileDrawer() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebar-overlay");
    const toggleBtn = document.getElementById("mobile-nav-toggle");
    const closeBtn = document.getElementById("sidebar-close-btn");

    if (!sidebar || !toggleBtn) return;

    function openDrawer() {
        sidebar.classList.add("open");
        if (overlay) overlay.classList.add("active");
        document.body.classList.add("drawer-open");
    }

    function closeDrawer() {
        sidebar.classList.remove("open");
        if (overlay) overlay.classList.remove("active");
        document.body.classList.remove("drawer-open");
    }

    toggleBtn.addEventListener("click", openDrawer);

    if (closeBtn) {
        closeBtn.addEventListener("click", closeDrawer);
    }

    if (overlay) {
        overlay.addEventListener("click", closeDrawer);
    }

    // Close drawer on escape key
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && sidebar.classList.contains("open")) {
            closeDrawer();
        }
    });

    // Close drawer when clicking a navigation link on mobile
    const menuLinks = sidebar.querySelectorAll(".menu-item, .sb-brand-link");
    menuLinks.forEach(link => {
        link.addEventListener("click", function () {
            if (window.innerWidth <= 900) {
                closeDrawer();
            }
        });
    });
}

/* ==============================================================================
   Global Toast Notification
   ============================================================================== */
function showToast(message, type = "info") {
    const toast = document.getElementById("toast");
    if (!toast) return;

    toast.innerText = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove("show");
        toast.classList.add("hidden");
    }, 3200);
}
