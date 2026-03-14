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
    const form = document.getElementById("login-form");
    const usernameInput = document.getElementById("login-username");
    const passwordInput = document.getElementById("login-password");
    const csrfToken = getCookie("csrftoken");

    if (!form || !usernameInput || !passwordInput) return;

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const username = usernameInput.value.trim();
        const password = passwordInput.value;

        if (!username || !password) {
            alert("Please enter username and password");
            return;
        }

        try {
            const response = await fetch("/api/auth/login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                credentials: "same-origin",
                body: JSON.stringify({
                    username,
                    password
                })
            });

            const data = await response.json().catch(() => ({}));

            if (response.ok) {
                window.location.href = "/dashboard/";
            } else {
                alert(data.error || `Login failed (${response.status})`);
            }
        } catch (error) {
            console.error(error);
            alert("Login failed");
        }
    });
});
