# train_model.py
# This script trains a simple neural network on the MNIST dataset
# and saves the trained model as "mnist_model.h5".
# Run it ONE time before starting the website:  python train_model.py

import os
from tensorflow import keras

# Save the model in the same folder as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "mnist_model.h5")

print("=" * 50)
print("STEP 1/5: Loading the MNIST dataset...")
print("=" * 50)

# ---------------------------------------------------------------
# 1. LOAD THE MNIST DATASET
# (It is downloaded automatically the first time you run this.)
# x = images (28x28 pixels), y = labels (digits 0-9)
# ---------------------------------------------------------------
(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
print("Training images:", x_train.shape)   # (60000, 28, 28)
print("Testing images :", x_test.shape)    # (10000, 28, 28)

# ---------------------------------------------------------------
# 2. NORMALIZE THE IMAGES
# Pixels are 0-255. Dividing by 255 makes them 0.0-1.0,
# which helps the network learn faster.
# ---------------------------------------------------------------
print("\nSTEP 2/5: Normalizing the images...")
x_train = x_train / 255.0
x_test = x_test / 255.0

# ---------------------------------------------------------------
# 3. CREATE THE SIMPLE NEURAL NETWORK
# ---------------------------------------------------------------
print("\nSTEP 3/5: Building the neural network...")
model = keras.Sequential([
    keras.Input(shape=(28, 28)),                     # input: a 28x28 image
    keras.layers.Flatten(),                          # 28x28 -> 784 numbers in a row
    keras.layers.Dense(128, activation="relu"),      # hidden layer: 128 neurons
    keras.layers.Dense(10, activation="softmax")     # output: 10 probabilities (digits 0-9)
])

# Tell Keras how to learn:
# - optimizer "adam"  : the method used to adjust the weights
# - loss              : how wrong the model is (used for labels like 0,1,2...)
# - metrics "accuracy": what we want to measure
model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()   # prints the layers of the model

# ---------------------------------------------------------------
# 4. TRAIN THE MODEL (5 epochs = 5 passes over the training data)
# You will see the progress and accuracy for each epoch below.
# ---------------------------------------------------------------
print("\nSTEP 4/5: Training the model (5 epochs)...")
model.fit(x_train, y_train, epochs=5)

# ---------------------------------------------------------------
# 5. EVALUATE ON TEST DATA (images the model has never seen)
# ---------------------------------------------------------------
print("\nSTEP 5/5: Evaluating the model on test data...")
test_loss, test_accuracy = model.evaluate(x_test, y_test, verbose=0)

# 6. PRINT THE TEST ACCURACY
print("\nTest accuracy: {:.2f}%".format(test_accuracy * 100))

# ---------------------------------------------------------------
# 7. SAVE THE MODEL
# ---------------------------------------------------------------
model.save(MODEL_PATH)
print("Model saved as:", MODEL_PATH)
print("Training finished. Now run:  python app.py")
