const API = "http://127.0.0.1:8000";

function verify() {
    fetch(`${API}/verify/${docId.value}`)
    .then(res => res.json())
    .then(data => {
        result.textContent = JSON.stringify(data, null, 2);
    });
}
