const API = "http://127.0.0.1:8000";
const token = localStorage.getItem("token");

function upload() {
    const form = new FormData();
    form.append("file", file.files[0]);

    fetch(`${API}/upload`, {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + token
        },
        body: form
    })
    .then(res => res.json())
    .then(data => {
        alert("Uploaded. Document ID: " + data.document_id);
    });
}

function sign() {
    fetch(`${API}/sign/${docId.value}`, {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(data => {
        alert("Document signed successfully");
    });
}
