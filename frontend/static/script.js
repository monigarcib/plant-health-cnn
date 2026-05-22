const imageInput = document.getElementById("imageInput");
const predictButton = document.getElementById("predictButton");
const preview = document.getElementById("preview");
const emptyPreview = document.getElementById("emptyPreview");

const resultBox = document.getElementById("result");
const resultIcon = document.getElementById("resultIcon");
const resultTitle = document.getElementById("resultTitle");
const confidence = document.getElementById("confidence");
const message = document.getElementById("message");
const progressBar = document.getElementById("progressBar");

imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];

    if (file) {
        preview.src = URL.createObjectURL(file);
        preview.style.display = "block";
        emptyPreview.style.display = "none";
        resultBox.classList.add("hidden");
    }
});

predictButton.addEventListener("click", async () => {
    const file = imageInput.files[0];

    if (!file) {
        showError("Selecciona una imagen antes de analizar.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    resultBox.classList.remove("hidden");
    resultIcon.textContent = "⏳";
    resultTitle.textContent = "Analizando imagen...";
    confidence.textContent = "";
    message.textContent = "El modelo está procesando la imagen.";
    progressBar.style.width = "0%";

    try {
        const response = await fetch("/predict", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Error al procesar la imagen.");
        }

        const data = await response.json();

        const isHealthy = data.clase === "sana";

        resultIcon.textContent = isHealthy ? "🌿" : "🥀";
        resultTitle.textContent = isHealthy ? "Planta sana" : "Planta marchita";
        confidence.textContent = `Confianza del modelo: ${data.confianza}%`;
        message.textContent = data.mensaje;
        progressBar.style.width = `${data.confianza}%`;
        progressBar.style.background = isHealthy ? "#4f7d32" : "#8a4b2b";

    } catch (error) {
        showError("Ocurrió un error al analizar la imagen.");
    }
});

function showError(text) {
    resultBox.classList.remove("hidden");
    resultIcon.textContent = "⚠️";
    resultTitle.textContent = "Error";
    confidence.textContent = "";
    message.textContent = text;
    progressBar.style.width = "0%";
}