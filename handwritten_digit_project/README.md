<<<<<<< HEAD
# Handwritten_digit
=======
# Handwritten Digit Recognition Using MNIST

Draw a digit (0-9) in the browser -> Flask preprocesses it -> a Keras neural network predicts it -> the result is saved in SQLite and shown on a History page.

## Folder structure

```
handwritten_digit_project/
├── app.py              Flask backend (routes, preprocessing, prediction, SQLite)
├── train_model.py      Trains the model and creates mnist_model.h5
├── requirements.txt    Libraries to install
├── templates/
│   ├── index.html      Home page (canvas + buttons)
│   └── history.html    History table page
└── static/
    ├── style.css       Styling
    └── script.js       Canvas drawing + fetch() to Flask

(created automatically when you run the project)
├── mnist_model.h5      Created by train_model.py
└── predictions.db      Created by app.py on first start
```

## IMPORTANT: never open the HTML files directly

The files in `templates/` are **Flask templates**. They contain tags like `{% if error %}` and `{{ row[0] }}` that only Flask can turn into a real page.

- Do NOT double-click `index.html` / `history.html`
- Do NOT use the "Live Server" extension or "Open with browser" on them
- ALWAYS run `python app.py` and open **http://127.0.0.1:5000** (the address must start with `http://127.0.0.1:5000`, not `file:///` and not `:5500`)

If you open them directly you will see raw `{% ... %}` text, no colors, no canvas, and a red "This page was opened the wrong way" box.

## Run it in VS Code (step by step, with what you should see)

### 1. Open the folder
`File > Open Folder...` and choose `handwritten_digit_project`.
Open a terminal: `Terminal > New Terminal`.

### 2. Create and activate a virtual environment

Windows:
```
python -m venv venv
venv\Scripts\activate
```
macOS / Linux:
```
python3 -m venv venv
source venv/bin/activate
```
**Check:** the terminal line now starts with `(venv)`.

Then in VS Code press `Ctrl+Shift+P`, choose **Python: Select Interpreter**, and pick the one inside `venv`.

> TensorFlow needs a supported Python version. Python 3.10, 3.11 or 3.12 is a safe choice.

### 3. Install the libraries
```
pip install -r requirements.txt
```
**Check:** run `python -c "import flask, tensorflow, numpy, PIL; print('All libraries OK')"`. It should print `All libraries OK`.

### 4. Train the model (only once)
```
python train_model.py
```
**Check (progress you will see):**
- `STEP 1/5` ... `STEP 5/5` messages
- `Training images: (60000, 28, 28)`
- 5 lines like `Epoch 1/5 ... accuracy: ...`
- `Test accuracy: XX.XX%`  <- write this number in your report
- `Model saved as: ...mnist_model.h5`
- A new file `mnist_model.h5` appears in the VS Code file list

(A warning about the "legacy HDF5 format" is harmless.)

### 5. Start the website
```
python app.py
```
**Check:**
```
Database ready.
Model loaded successfully.
 * Running on http://127.0.0.1:5000
```
A new file `predictions.db` appears in the folder.

### 6. Open the browser
Go to **http://127.0.0.1:5000**

**Check:**
1. You see the title, instructions, a black canvas, and Clear / Predict Digit / View History buttons.
2. Draw a big, thick digit in the middle and click **Predict Digit**. The digit and a confidence % appear, plus "Prediction saved to history."
3. The terminal prints `Prediction saved: <digit> <date time>`.
4. Click **View History**. Your prediction is in the table.

Stop the server with `Ctrl + C`.

## Quick checks for the error handling

| Try this | You should see |
|---|---|
| Click Predict with nothing drawn | "Please draw a digit first." |
| Rename `mnist_model.h5`, restart, predict | "Model not found. Please run 'python train_model.py' first." |
| Delete `predictions.db` while the app runs, then predict | Digit still shown, with a warning that it was not saved |
| Open History right after deleting `predictions.db` | "Could not read the prediction history from the database." (restart the app to recreate the table) |

## Tips for good predictions
Draw one digit, big and in the middle, in the normal way you would write it on paper. The model is a simple dense network trained on MNIST, so unusual shapes can be predicted wrongly. For example, a 7 drawn as a top bar plus a perfectly straight vertical line looks different from the 7s in MNIST, which have a diagonal stroke. Try a 7 with a slanted stroke. That is normal behaviour and a good limitation to mention in your report.

## Common problems

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Activate the venv, then `pip install -r requirements.txt` |
| `pip install tensorflow` fails | Use Python 3.10-3.12 and recreate the venv |
| `Address already in use` | Change the last line of `app.py` to `app.run(debug=True, use_reloader=False, port=5001)` and open `:5001` |
| Raw `{% if %}` text, no styling, no canvas | You opened the HTML file directly. Run `python app.py` and use http://127.0.0.1:5000 |
| Red underlines inside `history.html` in VS Code | Only the editor not understanding Jinja tags. Optional: install the **Better Jinja** extension. It does not affect running |
| Page looks old after editing | Hard refresh with `Ctrl + F5` |
| `TemplateNotFound` | Folder must be named `templates` (next to `app.py`) |
>>>>>>> 3c4d8df (Initial commit)
