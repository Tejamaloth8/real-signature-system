const API = "https://real-signature-system.onrender.com";

function register() {
    fetch(`${API}/register`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            email: email.value,
            password: password.value
        })
    })
    .then(res => res.json())
    .then(data => {
        alert("Registered successfully");
        window.location.href = "index.html";
    });
}

function login() {
    fetch(`${API}/login`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            email: email.value,
            password: password.value
        })
    })
    .then(res => res.json())
    .then(data => {
        localStorage.setItem("token", data.access_token);
        window.location.href = "dashboard.html";
    });
}
