const API = "https://real-signature-system.onrender.com";

async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch(`${API}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        // 🚨 IMPORTANT CHECK
        if (!response.ok) {
            const err = await response.json();
            alert("Login failed: " + err.detail);
            return;
        }

        const data = await response.json();

        // ✅ Store token ONLY on success
        localStorage.setItem("token", data.access_token);

        alert("Login successful");
        window.location.href = "dashboard.html";

    } catch (e) {
        console.error(e);
        alert("Network error during login");
    }
}

async function register() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch(`${API}/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const err = await response.json();
            alert("Registration failed: " + err.detail);
            return;
        }

        alert("Registration successful. Please login.");

    } catch (e) {
        console.error(e);
        alert("Network error during registration");
    }
}
