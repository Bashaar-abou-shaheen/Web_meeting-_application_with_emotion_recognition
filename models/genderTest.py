import cv2
import numpy as np
import pandas as pd
from keras.models import model_from_json

gender_dict = {0: "Male", 1: "Female"}

# Load JSON and create model
with open('gender_model.json', 'r') as json_file:
    loaded_model_json = json_file.read()
gender_model = model_from_json(loaded_model_json)

# Load weights into new model
gender_model.load_weights("gender_model.weights.h5")
print("Loaded model from disk")

# Start the webcam feed
cap = cv2.VideoCapture(0)

# Initialize results list
results = []
genders = []

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
        roi_color_frame = frame[y:y + h, x:x + w]
        cropped_img = cv2.resize(roi_color_frame, (48, 48))  # Resize to match LeNet-5 input
        cropped_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        cropped_img = np.expand_dims(cropped_img, axis=0) / 255.0  # Normalize and add batch dimension

        # Get the current timestamp
        timestamp = pd.Timestamp.now()

        # Predict the gender
        gender_prediction = gender_model.predict(cropped_img)
        predicted_gender = gender_dict[np.argmax(gender_prediction[0])]  # Get the class with highest probability
        cv2.putText(frame, predicted_gender, (x+5, y-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        results.append({"Gender": predicted_gender, "Timestamp": timestamp})
        genders.append(predicted_gender)
        
    cv2.imshow('Gender Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

male_percentage = (genders.count("Male") / len(genders)) * 100
female_percentage = (genders.count("Female") / len(genders)) * 100

print("Male:", round(male_percentage), "%")
print("Female:", round(female_percentage), "%")

# Convert results to DataFrame
# results_df = pd.DataFrame(results)

# Save the DataFrame to an Excel file
# results_df.to_excel("gender_results.xlsx", index=False)

cap.release()
cv2.destroyAllWindows()