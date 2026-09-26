
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");        // "ctx" is the pen we draw with
const resultDigit = document.getElementById("resultDigit");
const confidenceText = document.getElementById("confidence");
const messageText = document.getElementById("message");
const clearBtn = document.getElementById("clearBtn");
const predictBtn = document.getElementById("predictBtn");

let isDrawing = false;
let hasDrawn = false;

function setupCanvas() {
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = "white";
    ctx.lineWidth = 28;
                                
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    hasDrawn = false;
}


function showMessage(text, type) {
    messageText.textContent = text;
    messageText.className = type;
}


function getPosition(event) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    let clientX, clientY;
    if (event.touches) {
        clientX = event.touches[0].clientX;
        clientY = event.touches[0].clientY;
    } else {
        clientX = event.clientX;
        clientY = event.clientY;
    }
    return {
        x: (clientX - rect.left) * scaleX,
        y: (clientY - rect.top) * scaleY
    };
}


function startDrawing(event) {
    event.preventDefault();
    isDrawing = true;
    ctx.beginPath();
    const pos = getPosition(event);
    ctx.moveTo(pos.x, pos.y);
    draw(event);
}

function draw(event) {
    if (!isDrawing) return;
    event.preventDefault();
    const pos = getPosition(event);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
    hasDrawn = true;
}

function stopDrawing() {
    isDrawing = false;
    ctx.beginPath();
}

function clearCanvas() {
    setupCanvas();
    resultDigit.textContent = "-";
    confidenceText.textContent = "";
    showMessage("", "info");
}


async function predictDigit() {
    if (!hasDrawn) {
        showMessage("Please draw a digit first.", "error");
        return;
    }

    const imageData = canvas.toDataURL("image/png");

    predictBtn.disabled = true;
    showMessage("Predicting...", "info");

    try {
        // Send the image to the Flask route /predict as JSON
        const response = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: imageData })
        });

        const data = await response.json();   // Flask's reply

        if (!response.ok) {
            // Flask sent an error (empty canvas, invalid image, model not found...)
            resultDigit.textContent = "-";
            confidenceText.textContent = "";
            showMessage(data.error || "Something went wrong.", "error");
            return;
        }

        // Success: show the predicted digit
        resultDigit.textContent = data.digit;
        confidenceText.textContent = "Confidence: " + data.confidence + "%";

        if (data.saved) {
            showMessage("Prediction saved to history.", "success");
        } else {
            showMessage(data.warning, "warning");
        }

    } catch (error) {
        // The server could not be reached
        showMessage("Could not connect to the server. Is Flask running?", "error");
    } finally {
        predictBtn.disabled = false;
    }
}


// ---- Connect events to functions ----
// Mouse support
canvas.addEventListener("mousedown", startDrawing);
canvas.addEventListener("mousemove", draw);
canvas.addEventListener("mouseup", stopDrawing);
canvas.addEventListener("mouseleave", stopDrawing);

// Touch support (optional, for phones/tablets)
canvas.addEventListener("touchstart", startDrawing, { passive: false });
canvas.addEventListener("touchmove", draw, { passive: false });
canvas.addEventListener("touchend", stopDrawing);

// Buttons
clearBtn.addEventListener("click", clearCanvas);
predictBtn.addEventListener("click", predictDigit);

// Prepare the canvas when the page loads
setupCanvas();
