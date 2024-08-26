import cv2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Initialize image data generator with rescaling
# train_data_gen = ImageDataGenerator(rescale=1./255)
# validation_data_gen = ImageDataGenerator(rescale=1./255)
train_data_gen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)
validation_data_gen = ImageDataGenerator(rescale=1./255)

def preprocess_image(image):
    """Converts an image to grayscale and normalizes it."""
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_image = gray_image.astype("float") / 255.0
    return gray_image

# Preprocess all test images
train_generator = train_data_gen.flow_from_directory(
    'gender/train',
    target_size=(48, 48),
    batch_size=64,
    class_mode='categorical',
    color_mode='grayscale'  # Set color mode here
)

# Preprocess all train images
validation_generator = validation_data_gen.flow_from_directory(
    'gender/test',
    target_size=(48, 48),
    batch_size=64,
    class_mode='categorical',
    color_mode='grayscale'  # Set color mode here
)

# Apply preprocessing to the generators
train_generator.preprocessing_function = preprocess_image
validation_generator.preprocessing_function = preprocess_image



# Create LeNet-5 model
gender_model = Sequential()

# Convolutional layer 1
gender_model.add(Conv2D(6, kernel_size=(5, 5), activation='relu', input_shape=(48, 48, 1)))
gender_model.add(MaxPooling2D(pool_size=(2, 2)))

# Convolutional layer 2
gender_model.add(Conv2D(16, kernel_size=(5, 5), activation='relu'))
gender_model.add(MaxPooling2D(pool_size=(2, 2)))

# Flatten the output
gender_model.add(Flatten())

# Fully connected layer 1
gender_model.add(Dense(120, activation='relu'))

# Fully connected layer 2
gender_model.add(Dense(84, activation='relu'))

# Output layer
gender_model.add(Dense(2, activation='softmax'))  # 2 classes for gender classification

cv2.ocl.setUseOpenCL(False)

gender_model.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=0.0001, decay=1e-6), metrics=['accuracy'])

# Train the model
gender_model_info = gender_model.fit(
        train_generator,
        steps_per_epoch=28709 // 64,  # Adjust based on your dataset size
        epochs=50,
        validation_data=validation_generator,
        validation_steps=7178 // 64  # Adjust based on your dataset size
)

# Save the model structure and weights
model_json = gender_model.to_json()
with open("gender_model.json", "w") as json_file:
    json_file.write(model_json)

gender_model.save_weights('gender_model.weights.h5')