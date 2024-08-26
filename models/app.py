from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
from keras.models import model_from_json

emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}
gender_dict = {0: "Male", 1: "Female"}

app = Flask(__name__)

# Load JSON and create models
with open('emotion_model.json', 'r') as json_file:
    loaded_model_json = json_file.read()
emotion_model = model_from_json(loaded_model_json)
emotion_model.load_weights("emotion_model.weights.h5")
print("Loaded emotion model from disk")

with open('gender_model.json', 'r') as json_file:
    loaded_model_json = json_file.read()
gender_model = model_from_json(loaded_model_json)
gender_model.load_weights("gender_model.weights.h5")
print("Loaded gender model from disk")

@app.route('/process', methods=['POST'])
def process_emotion_frame():  # Renamed function for emotion prediction
    data = request.json['image']
    img_data = base64.b64decode(data.split(',')[1])
    img_array = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (48, 48))
    img = np.expand_dims(img, axis=-1)
    img = np.expand_dims(img, axis=0)
    img = img / 255.0

    # Predict emotion
    emotion_prediction = emotion_model.predict(img)
    maxindex = int(np.argmax(emotion_prediction))
    predicted_emotion = emotion_dict[maxindex]

    return jsonify({'emotion': predicted_emotion})

@app.route('/gender', methods=['POST'])
def process_gender_frame():  # Renamed function for gender prediction
    data = request.json['image']
    img_data = base64.b64decode(data.split(',')[1])
    img_array = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (48, 48))
    img = np.expand_dims(img, axis=-1)
    img = np.expand_dims(img, axis=0)
    img = img / 255.0

    # Predict gender
    gender_prediction = gender_model.predict(img)
    maxindex = int(np.argmax(gender_prediction))
    predicted_gender = gender_dict[maxindex]

    return jsonify({'gender': predicted_gender})

if __name__ == '__main__':
    app.run(port=5000)