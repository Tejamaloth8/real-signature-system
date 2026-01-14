const API = "https://real-signature-system.onrender.com";

function verify() {
    fetch(`${API}/verify/${docId.value}`)
    .then(res => res.json())
    .then(data => {
        result.textContent = JSON.stringify(data, null, 2);
    });
}
