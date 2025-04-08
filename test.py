import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.applications.vgg16 import VGG16
import torch
from transformers import ViTImageProcessor, ViTForImageClassification
from tensorflow.keras.preprocessing import image

class PneumoniaClassifier:
    def __init__(self, weights_path):
        self.weights_path = weights_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.class_labels = {
            0: "Bacterial Pneumonia",
            1: "Normal",
            2: "Other Pathological Findings",
            3: "Viral Pneumonia"
        }

        # Load ViT model
        self.vit_model_name = "facebook/dino-vits16"
        self.vit_processor = ViTImageProcessor.from_pretrained(self.vit_model_name)
        self.vit_model = ViTForImageClassification.from_pretrained(self.vit_model_name, num_labels=4).to(self.device)

        # Load VGG model
        vgg_base = VGG16(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
        self.vgg_model = Model(inputs=vgg_base.input, outputs=Flatten()(vgg_base.output))

        # Define hybrid model
        class HybridModel(Model):
            def __init__(self, vgg_model, vit_forward, **kwargs):
                super(HybridModel, self).__init__(**kwargs)
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

        def vit_forward(image_batch):
            def process_images(images):
                images = images.numpy()
                images = (images * 255).astype(np.uint8)
                inputs = self.vit_processor(images=images, return_tensors="pt").to(self.device)
                outputs = self.vit_model(**inputs)
                features = torch.nn.functional.softmax(outputs.logits, dim=1).cpu().detach().numpy()
                return np.expand_dims(features, axis=-1)

            return tf.py_function(func=process_images, inp=[image_batch], Tout=tf.float32)

        self.hybrid_model = HybridModel(self.vgg_model, vit_forward)
        dummy_input = tf.random.normal((1, 224, 224, 3))
        _ = self.hybrid_model(dummy_input)
        self.hybrid_model.build(input_shape=(None, 224, 224, 3))
        self.hybrid_model.load_weights(self.weights_path)
        print("✅ Model loaded.")

    def preprocess_image(self, img):
        img = cv2.resize(img, (224, 224))
        img_array = np.expand_dims(img, axis=0) / 255.0
        return img_array

    def classify_folder(self, folder_path):
        result_folder = os.path.join(folder_path, "Results_Relabeled")
        os.makedirs(result_folder, exist_ok=True)

        result_file_path = os.path.join(folder_path, "classification_results.txt")
        with open(result_file_path, "w") as result_file:
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(".jpg"):
                    file_path = os.path.join(folder_path, filename)
                    image_cv = cv2.imread(file_path)
                    if image_cv is None:
                        continue

                    img_array = self.preprocess_image(image_cv)
                    predictions = self.hybrid_model.predict(img_array)
                    class_probs = predictions[0]

                    # Extract confidence values
                    bacterial_conf = class_probs[0] * 100
                    normal_conf = class_probs[1] * 100
                    other_conf = class_probs[2] * 100
                    viral_conf = class_probs[3] * 100

                    # Write to text file
                    result_file.write(f"File Name: {filename}\n")
                    result_file.write(f"Normal Confidence: {normal_conf:.2f}%\n")
                    result_file.write(f"Viral Confidence: {viral_conf:.2f}%\n")
                    result_file.write(f"Bacterial Confidence: {bacterial_conf:.2f}%\n")
                    result_file.write(f"Other Confidence: {other_conf:.2f}%\n\n")

                    # Rename image based on viral vs bacterial only
                    new_suffix = "viral" if viral_conf > bacterial_conf else "bacterial"
                    new_filename = f"{os.path.splitext(filename)[0]}_{new_suffix}.jpg"
                    new_file_path = os.path.join(result_folder, new_filename)
                    cv2.imwrite(new_file_path, image_cv)

        print(f"\n📁 Done! Results saved to:\n- {result_file_path}\n- {result_folder}")

# --- RUNNING THE CLASSIFIER ---
if __name__ == "__main__":
    folder = input("📂 Enter path to folder containing images: ")
    weights = r"C:\Users\CHEXRAY\elysia-bb-mwamwa-thesis-143\System Model\hybrid_best_model.weights.h5"
    classifier = PneumoniaClassifier(weights)
    classifier.classify_folder(folder)
