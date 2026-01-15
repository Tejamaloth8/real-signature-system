const API = "https://real-signature-system.onrender.com";
const token = localStorage.getItem("token");

// Store document ID globally after upload
let uploadedDocumentId = null;

function upload() {
    const fileInput = document.getElementById("file");

    if (!fileInput.files.length) {
        alert("Please choose a file first");
        return;
    }

    const form = new FormData();
    form.append("file", fileInput.files[0]);

    fetch(`${API}/upload`, {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + token
        },
        body: form
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Upload failed");
        }
        return res.json();
    })
    .then(data => {
        uploadedDocumentId = data.document_id;
        alert("Uploaded successfully.\nDocument ID: " + uploadedDocumentId);
    })
    .catch(err => {
        console.error(err);
        alert("Upload error. Check console.");
    });
}

function sign() {
    if (!uploadedDocumentId) {
        alert("Please upload a document first");
        return;
    }

    fetch(`${API}/sign/${uploadedDocumentId}`, {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Sign failed");
        }
        return res.json();
    })
    .then(data => {
        alert("Document signed successfully");
    })
    .catch(err => {
        console.error(err);
        alert("Sign error. Check console.");
    });
}
