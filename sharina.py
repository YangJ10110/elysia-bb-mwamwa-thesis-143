import numpy as np
import tensorflow as tf
import cv2
import os
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.applications.vgg16 import VGG16
import torch
from transformers import ViTImageProcessor, ViTForImageClassification

# DEVICE CONFIGURATION
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# LOAD ViT MODEL
vit_model_name = "facebook/dino-vits16"
vit_processor = ViTImageProcessor.from_pretrained(vit_model_name)
vit_model = ViTForImageClassification.from_pretrained(vit_model_name, num_labels=4).to(device)

# ViT FORWARD FUNCTION
def vit_forward(image_batch):
    def process_images(images):
        images = images.numpy()  # Convert TF tensor to NumPy
        images = (images * 255).astype(np.uint8)  # Convert back to [0,255]
        inputs = vit_processor(images=images, return_tensors="pt").to(device)
        outputs = vit_model(**inputs)
        features = torch.nn.functional.softmax(outputs.logits, dim=1).cpu().detach().numpy()
        return np.expand_dims(features, axis=-1)  # Reshape to (batch, 3, 1)
    
    return tf.py_function(func=process_images, inp=[image_batch], Tout=tf.float32)

# LOAD VGG MODEL
vgg_base = VGG16(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
vgg_model = Model(inputs=vgg_base.input, outputs=Flatten()(vgg_base.output))  # Shape: (batch, 25088)

# HYBRID MODEL CLASS
class HybridModel(Model):
    def __init__(self, vgg_model, vit_forward, name="hybrid_model", **kwargs):
        super(HybridModel, self).__init__(name=name, **kwargs)
        self.vgg_model = Model(inputs=vgg_model.input, outputs=vgg_model.output)
        self.vgg_fc = Dense(512, activation="relu")
        self.vit_forward = vit_forward
        self.vit_fc = Dense(512, activation="relu")
        self.fc = Dense(4, activation="softmax")

    def call(self, inputs, training=False):
        vgg_features = self.vgg_model(inputs)
        vgg_features = self.vgg_fc(vgg_features)

        vit_features = self.vit_forward(inputs)
        vit_features = tf.reshape(vit_features, (-1, 4))
        vit_features = self.vit_fc(vit_features)

        merged_features = (vgg_features + vit_features) / 2
        return self.fc(merged_features)

# RECREATE MODEL
hybrid_model = HybridModel(vgg_model, vit_forward)

# 🔹 BUILD MODEL BEFORE LOADING WEIGHTS
dummy_input = tf.random.normal((1, 224, 224, 3))
_ = hybrid_model(dummy_input)
hybrid_model.build(input_shape=(None, 224, 224, 3))

# LOAD WEIGHTS
weights_path = r"C:\Users\Sharina Evangelista\Documents\GitHub\Thesis\model_checkpoints\hybrid_best_model.weights.h5"
hybrid_model.load_weights(weights_path)
print("\n Model loaded successfully!")

# DEFINE CLASS LABELS
class_labels = {0: "Bacterial Pneumonia", 1: "Normal",  2: "Other Pathological Findings", 3: "Viral Pneumonia"}

# ADD BRIGHTNESS ADJUSTMENT FUNCTION
def adjust_brightness(image_tensor, delta=0.2):
    return tf.image.random_brightness(image_tensor, max_delta=delta)

# IMAGE PREPROCESSING FUNCTION
def preprocess_image(img_path, apply_brightness=True):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0  # Normalize

    img_tensor = tf.convert_to_tensor(img_array, dtype=tf.float32)

    if apply_brightness:
        img_tensor = adjust_brightness(img_tensor)

    return img_tensor.numpy()

# CLASSIFICATION FUNCTION
def classify_pneumonia(img_path):
    img_array = preprocess_image(img_path, apply_brightness=True)
    predictions = hybrid_model.predict(img_array)
    class_probs = predictions[0]
    class_index = np.argmax(class_probs)

    print("\n Classification Confidence Levels:")
    for idx, label in class_labels.items():
        print(f"   {label}: {class_probs[idx] * 100:.2f}%")
    
    print(f"\n Final Prediction: {class_labels[class_index]} with {class_probs[class_index] * 100:.2f}% confidence.\n")
    return class_labels[class_index]

# CAMERA SCANNER FUNCTION
def camera_scan():
    cap = cv2.VideoCapture(0)  # Open webcam
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        cv2.imshow("Press 's' to scan | Press 'q' to quit", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):  # Press 's' to capture and classify
            img_path = "captured_image.jpg"
            cv2.imwrite(img_path, frame)
            label = classify_pneumonia(img_path)
            print(f" Predicted: {label}")

        elif key == ord("q"):  # Press 'q' to quit
            break

    cap.release()
    cv2.destroyAllWindows()

# AUTO-SCAN FOLDER FUNCTION
def scan_folder(folder_path):
    print(f" Scanning folder: {folder_path}")
    processed_images = set()

    while True:
        for filename in os.listdir(folder_path):
            img_path = os.path.join(folder_path, filename)

            if img_path not in processed_images and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                label = classify_pneumonia(img_path)
                print(f"🖼 {filename} → {label}")
                processed_images.add(img_path)

# CHOOSE MODE: CAMERA OR FOLDER
mode = input("Choose mode: [1] Camera Scan | [2] Folder Auto-Scan: ")

if mode == "1":
    camera_scan()
elif mode == "2":
    folder_path = r"C:\Users\Sharina Evangelista\Documents\GitHub\Thesis\Test"
    scan_folder(folder_path)