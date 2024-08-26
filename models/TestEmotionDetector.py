import cv2
import numpy as np
import pandas as pd
from keras.models import model_from_json

emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}

# Load JSON and create model
with open('emotion_model.json', 'r') as json_file:
    loaded_model_json = json_file.read()
emotion_model = model_from_json(loaded_model_json)

# Load weights into new model
emotion_model.load_weights("emotion_model.weights.h5")
print("Loaded model from disk")

# Start the webcam feed
cap = cv2.VideoCapture(0)

# Initialize results list
results = []
emotions = []

while True:
    # Find haar cascade to draw bounding box around face
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (1280, 720))

    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces available on camera
    num_faces = face_detector.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)

    # Take each face available on the camera and preprocess it
    for (x, y, w, h) in num_faces:
        cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (0, 255, 0), 4)
        roi_gray_frame = gray_frame[y:y + h, x:x + w]
        cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame, (48, 48)), -1), 0)

        # Get the current timestamp
        timestamp = pd.Timestamp.now()

        # Predict the emotions
        emotion_prediction = emotion_model.predict(cropped_img)
        maxindex = int(np.argmax(emotion_prediction))
        predicted_emotion = emotion_dict[maxindex]
        cv2.putText(frame, predicted_emotion, (x+5, y-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        results.append({"Emotion": predicted_emotion, "Timestamp": timestamp})
        emotions.append(predicted_emotion)
    cv2.imshow('Emotion Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break



Angry =( emotions.count("Angry") / len(emotions))   *100
Disgusted = (emotions.count("Disgusted")/ len(emotions))*100
Fearful = (emotions.count("Fearful")/ len(emotions))*100
Happy = (emotions.count("Happy")/ len(emotions))*100
Neutral = (emotions.count("Neutral")/ len(emotions))*100
Sad = (emotions.count("Sad")/ len(emotions))*100
Surprised =( emotions.count("Surprised")/ len(emotions))*100

print ("Angry :" ,round(Angry) ,"%")
print ("Disgusted :" ,round(Disgusted),"%")
print ("Fearful :" ,round(Fearful),"%")
print ("Happy :" ,round(Happy),"%")
print ("Neutral :" ,round(Neutral),"%")
print ("Sad :" ,round(Sad),"%")
print ("Surprised :" ,round(Surprised),"%")


cap.release()
cv2.destroyAllWindows()