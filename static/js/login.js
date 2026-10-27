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
    const submitBtn = document.getElementById("btn-login-submit");
    const submitBtnText = document.getElementById("login-btn-text");
    const btnQuickDemo = document.getElementById("btn-quick-demo");
    const btnQuickDemoMobile = document.getElementById("btn-quick-demo-mobile");
    const csrfToken = getCookie("csrftoken");

    function fillAndLoginDemo() {
        if (!usernameInput || !passwordInput || !form) return;
        usernameInput.value = "admin";
        passwordInput.value = "admin123";

        // Add subtle animation / focus
        usernameInput.classList.add("input-highlight");
        passwordInput.classList.add("input-highlight");
        setTimeout(() => {
            usernameInput.classList.remove("input-highlight");
            passwordInput.classList.remove("input-highlight");
        }, 800);

        if (submitBtnText) {
            submitBtnText.textContent = "Logging in as Inspector...";
        }
        if (submitBtn) {
            submitBtn.disabled = true;
        }

        // Trigger submit
        form.dispatchEvent(new Event("submit", { cancelable: true }));
    }

    if (btnQuickDemo) {
        btnQuickDemo.addEventListener("click", fillAndLoginDemo);
    }
    if (btnQuickDemoMobile) {
        btnQuickDemoMobile.addEventListener("click", fillAndLoginDemo);
    }

    if (!form || !usernameInput || !passwordInput) return;

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const username = usernameInput.value.trim();
        const password = passwordInput.value;

        if (!username || !password) {
            alert("Please enter username/email and password");
            if (submitBtn) submitBtn.disabled = false;
            if (submitBtnText) submitBtnText.textContent = "Sign In";
            return;
        }

        if (submitBtnText && !submitBtn.disabled) {
            submitBtnText.textContent = "Signing In...";
            submitBtn.disabled = true;
        }

        try {
            const response = await fetch("/api/auth/login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken || ""
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
                if (submitBtn) submitBtn.disabled = false;
                if (submitBtnText) submitBtnText.textContent = "Sign In";
            }
        } catch (error) {
            console.error(error);
            alert("Network error during login. Please try again.");
            if (submitBtn) submitBtn.disabled = false;
            if (submitBtnText) submitBtnText.textContent = "Sign In";
        }
    });
});
