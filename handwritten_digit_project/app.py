# app.py
# Flask backend: shows pages, receives the drawing, predicts the digit,
# and stores each prediction in SQLite.

import base64
import io
import os
import sqlite3
from datetime import datetime

import numpy as np
from flask import Flask, jsonify, render_template, request
from PIL import Image
from tensorflow import keras

# ---------------------------------------------------------------
# 1. INITIALIZE FLASK AND SET FILE PATHS
# ---------------------------------------------------------------
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "mnist_model.h5")
DB_PATH = os.path.join(BASE_DIR, "predictions.db")


# ---------------------------------------------------------------
# 2. DATABASE: CREATE THE TABLE IF IT DOES NOT EXIST
# ---------------------------------------------------------------
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)   # creates predictions.db if missing
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                predicted_digit INTEGER NOT NULL,
                prediction_time TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print("Database ready.")
    except sqlite3.Error as error:
        print("Database error while creating table:", error)


init_db()


# ---------------------------------------------------------------
# 3. LOAD THE TRAINED MODEL (only once, when the server starts)
# ---------------------------------------------------------------
model = None
if os.path.exists(MODEL_PATH):
    try:
        model = keras.models.load_model(MODEL_PATH, compile=False)
        print("Model loaded successfully.")
    except Exception as error:
        print("Could not load the model:", error)
else:
    print("ERROR: mnist_model.h5 not found. Run 'python train_model.py' first.")


# ---------------------------------------------------------------
# 4. IMAGE PREPROCESSING
# Input : Base64 text from the browser (data URL)
# Output: NumPy array of shape (1, 28, 28), or None if canvas is empty
# ---------------------------------------------------------------
def preprocess_image(data_url):
    # The data URL looks like: "data:image/png;base64,iVBORw0KGgo..."
    # We keep only the part after the comma.
    encoded = data_url.split(",")[1]

    # Decode Base64 text back into image bytes, then open as an image
    image_bytes = base64.b64decode(encoded)

    # Convert to GRAYSCALE ("L" = one channel, values 0-255)
    img = Image.open(io.BytesIO(image_bytes)).convert("L")

    # Find the box around the white drawing. If there is no white
    # pixel at all, the canvas is empty.
    mask = img.point(lambda pixel: 255 if pixel > 50 else 0)
    box = mask.getbbox()
    if box is None:
        return None

    # Crop to the digit, then shrink it so its longer side is 20 pixels.
    # (MNIST digits are about 20x20 pixels, centered in a 28x28 image.)
    img = img.crop(box)
    width, height = img.size
    scale = 20.0 / max(width, height)
    new_width = max(1, int(round(width * scale)))
    new_height = max(1, int(round(height * scale)))
    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Paste the small digit into the middle of a black 28 x 28 image
    final_img = Image.new("L", (28, 28), 0)
    final_img.paste(img, ((28 - new_width) // 2, (28 - new_height) // 2))

    # MNIST digits are centered by their "center of mass" (the average position
    # of the white pixels), not by their box. We do the same: find the center of
    # mass and slide the digit so that it sits at the middle (14, 14).
    pixels = np.array(final_img, dtype="float32")
    total = pixels.sum()
    if total > 0:
        rows, cols = np.indices(pixels.shape)
        center_y = (rows * pixels).sum() / total
        center_x = (cols * pixels).sum() / total
        shift_x = int(round(14 - center_x))
        shift_y = int(round(14 - center_y))
        final_img = final_img.transform(
            (28, 28), Image.AFFINE, (1, 0, -shift_x, 0, 1, -shift_y)
        )

    # NORMALIZE: convert pixels from 0-255 to 0.0-1.0 (same as training)
    pixels = np.array(final_img, dtype="float32") / 255.0

    # Reshape to the model's input format: (1 image, 28, 28)
    return pixels.reshape(1, 28, 28)


# ---------------------------------------------------------------
# 5. ROUTES (web addresses of our app)
# ---------------------------------------------------------------

# Home page
@app.route("/")
def index():
    return render_template("index.html")


# Prediction: the browser sends the drawing here using fetch()
@app.route("/predict", methods=["POST"])
def predict():
    # Error handling: model not found
    if model is None:
        return jsonify({
            "error": "Model not found. Please run 'python train_model.py' first."
        }), 500

    # Read the JSON sent by JavaScript: {"image": "data:image/png;base64,..."}
    data = request.get_json(silent=True)
    if not data or "image" not in data:
        return jsonify({"error": "No image received."}), 400

    # Preprocess the image
    try:
        image_array = preprocess_image(data["image"])
    except Exception:
        # Error handling: invalid image
        return jsonify({"error": "Invalid image. Please draw the digit again."}), 400

    # Error handling: empty canvas
    if image_array is None:
        return jsonify({"error": "Canvas is empty. Please draw a digit first."}), 400

    # Predict: the model returns 10 probabilities (one per digit)
    probabilities = model.predict(image_array, verbose=0)[0]
    digit = int(np.argmax(probabilities))                    # index of the biggest value
    confidence = round(float(probabilities[digit]) * 100, 2)

    # Save the prediction and current date/time in SQLite
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response = {"digit": digit, "confidence": confidence, "saved": True}

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO predictions (predicted_digit, prediction_time) VALUES (?, ?)",
            (digit, current_time)
        )
        conn.commit()
        conn.close()
        print("Prediction saved:", digit, current_time)
    except sqlite3.Error:
        # Error handling: database problem (we still show the prediction)
        response["saved"] = False
        response["warning"] = "Digit predicted, but it could not be saved to the database."

    return jsonify(response)


# History page: shows all saved predictions
@app.route("/history")
def history():
    records = []
    error = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute(
            "SELECT id, predicted_digit, prediction_time FROM predictions ORDER BY id DESC"
        )
        records = cursor.fetchall()
        conn.close()
    except sqlite3.Error:
        # Error handling: database problem
        error = "Could not read the prediction history from the database."

    return render_template("history.html", records=records, error=error)


# ---------------------------------------------------------------
# 6. RUN THE APP
# use_reloader=False stops Flask from loading the model twice.
# ---------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
