const API = "https://real-signature-system.onrender.com";
let uploadedDocumentId = null;

/* ---------------------------
   Helper: get token safely
---------------------------- */
function getTokenOrRedirect() {
    const token = localStorage.getItem("token");

    if (!token || token === "undefined" || token === "null") {
        alert("Session expired. Please login again.");
        window.location.href = "index.html";
        return null;
    }
    return token;
}

/* ---------------------------
   Upload file
---------------------------- */
async function upload() {
    const token = getTokenOrRedirect();
    if (!token) return;

    const fileInput = document.getElementById("file");

    if (!fileInput || !fileInput.files.length) {
        alert("Please choose a file first");
        return;
    }

    const form = new FormData();
    form.append("file", fileInput.files[0]);

    try {
        const res = await fetch(`${API}/upload`, {
            method: "POST",
            headers: {
                "Authorization": "Bearer " + token
            },
            body: form
        });

        if (!res.ok) {
            // Read backend error message if present
            let msg = "Upload failed";
            try {
                const err = await res.json();
                msg = err.detail || msg;
            } catch {}
            throw new Error(msg);
        }

        const data = await res.json();
        uploadedDocumentId = data.document_id;

        alert(`Uploaded successfully.\nDocument ID: ${uploadedDocumentId}`);

    } catch (err) {
        console.error("UPLOAD ERROR:", err);
        alert("Upload error: " + err.message);
    }
}

/* ---------------------------
   Sign document
---------------------------- */
async function sign() {
    const token = getTokenOrRedirect();
    if (!token) return;

    if (!uploadedDocumentId) {
        alert("Please upload a document first");
        return;
    }

    try {
        const res = await fetch(`${API}/sign/${uploadedDocumentId}`, {
            method: "POST",
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (!res.ok) {
            let msg = "Sign failed";
            try {
                const err = await res.json();
                msg = err.detail || msg;
            } catch {}
            throw new Error(msg);
        }

        alert("Document signed successfully");

    } catch (err) {
        console.error("SIGN ERROR:", err);
        alert("Sign error: " + err.message);
    }
}
