document.addEventListener("DOMContentLoaded", function () {
    const logoutBtn = document.getElementById("logout-btn");
    if (!logoutBtn) return;

    logoutBtn.addEventListener("click", function () {
        const loginUrl = logoutBtn.dataset.loginUrl || "/";
        const nextParam = encodeURIComponent(loginUrl);
        window.location.href = `/api/auth/logout/?next=${nextParam}`;
    });
});
