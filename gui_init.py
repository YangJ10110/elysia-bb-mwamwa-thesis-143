import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2

import os
import ssl
import threading

# Use the certifi path for SSL
os.environ['SSL_CERT_FILE'] = r'C:\Users\CHEXRAY\elysia-bb-mwamwa-thesis-143\chexray_env\Lib\site-packages\certifi\cacert.pem'
ssl._create_default_https_context = ssl._create_unverified_context


from reportlab.pdfgen import canvas
import smtplib
import ssl
from email.message import EmailMessage
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import tempfile
import numpy as np

# original_width, original_height = 1080, 1920
# scale_steps = 50
# scale_factor = 0.02  # 5% decrease per step

# scaled_sizes = [
#     (int(original_width * (1 - scale_factor * step)), 
#      int(original_height * (1 - scale_factor * step)))
#     for step in range(scale_steps + 1)
# ]

# print(scaled_sizes)

# 1440

import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.applications.vgg16 import VGG16
import torch
from transformers import ViTImageProcessor, ViTForImageClassification

# 810
class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(False)  # Remove title bar
        self.root.geometry("1100x800")  # Set to landscape
        self.root.configure(bg="#171d29")
        #center-top the window
        self.processed_image_preview = None
        self.current_frame = None
        self.captured_image = None
        self.filename = None
        self.patient_name = ""
        self.normal_confidence = "0"
        self.viral_confidence = "0"
        self.bacterial_confidence = "0"
        self.age = "0"
        self.address = ""
        self.contact = ""
        self.sex = ""
        self.active_entry = None
        self.others_confidence = "0"
        self.priority_level = ""
        self.cap = None
        self.image = None
        self.facility_name = ""
        self.facility_email = ""    
        self.brightness_value = 50  # For live camera feed

        # self.weights_path = r"C:\Users\CHEXRAY\elysia-bb-mwamwa-thesis-143\System Model\hybrid_best_model.weights.h5"


        # self.create_patient_info_page()
        self.initial_front_page()
        # showing the result page immediately for testing
        # self.show_result_page()
    def classify_pneumonia(self):
        # DEVICE CONFIGURATION
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # LOAD ViT MODEL
        vit_model_name = "facebook/dino-vits16"
        vit_processor = ViTImageProcessor.from_pretrained(vit_model_name)
        vit_model = ViTForImageClassification.from_pretrained(vit_model_name, num_labels=4).to(device)

        def vit_forward(image_batch):
            def process_images(images):
                images = images.numpy()
                images = (images * 255).astype(np.uint8)
                inputs = vit_processor(images=images, return_tensors="pt").to(device)
                outputs = vit_model(**inputs)
                features = torch.nn.functional.softmax(outputs.logits, dim=1).cpu().detach().numpy()
                return np.expand_dims(features, axis=-1)

            return tf.py_function(func=process_images, inp=[image_batch], Tout=tf.float32)

        # LOAD VGG MODEL
        vgg_base = VGG16(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
        vgg_model = Model(inputs=vgg_base.input, outputs=Flatten()(vgg_base.output))

        # HYBRID MODEL CLASS
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

        # RECREATE MODEL
        hybrid_model = HybridModel(vgg_model, vit_forward)

        # INITIALIZE MODEL
        dummy_input = tf.random.normal((1, 224, 224, 3))
        _ = hybrid_model(dummy_input)
        hybrid_model.build(input_shape=(None, 224, 224, 3))

        # LOAD WEIGHTS
        hybrid_model.load_weights(self.weights_path)
        print("\n✅ Model loaded successfully!")

        # DEFINE CLASS LABELS
        class_labels = {0: "Bacterial Pneumonia", 1: "Normal", 2: "Other Pathological Findings", 3: "Viral Pneumonia"}

        def preprocess_image(cv_image):
            img = cv2.resize(cv_image, (224, 224))
            img_array = np.expand_dims(img, axis=0) / 255.0
            return img_array

        # PREDICTION
        img_array = preprocess_image(self.captured_image)
        predictions = hybrid_model.predict(img_array)
        class_probs = predictions[0]
        class_index = np.argmax(class_probs)

        # Extract confidence levels
        normal_confidence = f"{class_probs[1] * 100:.2f}"
        bacterial_confidence = f"{class_probs[0] * 100:.2f}"
        viral_confidence = f"{class_probs[3] * 100:.2f}"
        other_confidence = f"{class_probs[2] * 100:.2f}"


        print("\n📊 Classification Confidence Levels:")
        for idx, label in class_labels.items():
            print(f"   {label}: {class_probs[idx] * 100:.2f}%")

        final_prediction = f"\n✅ Final Prediction: {class_labels[class_index]} with {class_probs[class_index] * 100:.2f}% confidence.\n"
        print(final_prediction)

        return class_labels[class_index], normal_confidence, bacterial_confidence, viral_confidence, other_confidence

   
    def initial_front_page(self):
        """Setup front page with delayed Proceed button"""
        self.exit_button = tk.Button(
            self.root, text="✕", command=self.root.quit,
            fg="red", font=("Comfortaa", 24, "bold"), bd=0,
            bg="#171d29", activebackground="#171d29", activeforeground="white"
        )
        self.exit_button.place(x=1030, y=31, width=24, height=24)

        # Load and store image to prevent garbage collection
        # front_page_logo = Image.open('front-page.png')
        front_page_logo = Image.open('CheXray_Colored.png')

        front_page_logo = front_page_logo.resize((320, 320), Image.Resampling.LANCZOS)  # Resize with high quality

        self.front_page_logo = ImageTk.PhotoImage(front_page_logo)  # Store as instance variable

        # Display image in a label
        self.logo_label = tk.Label(self.root, image=self.front_page_logo, bg="#171d29")
        self.logo_label.place(x=390, y=100)

        # Load dependencies in background, then enable the Proceed button
        self.show_proceed_button()

    def show_proceed_button(self):
        """Display Proceed button after dependencies are loaded"""
        self.proceed_button = tk.Button(
            self.root, text="Start", command=self.create_patient_info_page,
            bg="#1a80e6", fg="white", font=("Google Sans", 16, "bold")
        )
        self.proceed_button.place(x=475, y=430, width=150, height=62)

    def create_patient_info_page(self):
        self.clear_frame()
        self.close_camera()

        self.exit_button = tk.Button(self.root, text="✕", command=self.root.quit, fg="red", font=("Comfortaa", 24, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=930, y=31, width=24, height=24)

        tk.Label(self.root, text="Hello!", font=("Google Sans", 40), bg="#171d29", fg="white").place(x=503, y=40)

        tk.Label(self.root, text="Patient's Name:", font=("Google Sans", 20), bg="#171d29", fg="white").place(x=172, y=118)
        tk.Label(self.root, text="Age:", font=("Google Sans", 20), bg="#171d29", fg="white").place(x=697, y=118)
        tk.Label(self.root, text="Sex:", font=("Google Sans", 20), bg="#171d29", fg="white").place(x=870, y=118)

        self.name_entry = tk.Entry(self.root, font=("Google Sans", 15), width=35, relief="flat", highlightthickness=1, highlightbackground="gray", bd=6)
        self.name_entry.place(x=172, y=152)
        self.name_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.name_entry))


        self.age_entry = tk.Entry(self.root, font=("Google Sans", 15), width=5, relief="flat", highlightthickness=1, highlightbackground="gray", bd=6)
        self.age_entry.place(x=697, y=152)
        self.age_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.age_entry))


        self.sex_entry = tk.Entry(self.root, font=("Google Sans", 15), width=5, relief="flat", highlightthickness=1, highlightbackground="gray", bd=6)
        self.sex_entry.place(x=870, y=152)
        self.sex_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.sex_entry))


        tk.Label(self.root, text="Address:", font=("Google Sans", 20), bg="#171d29", fg="white").place(x=172, y=211)
        tk.Label(self.root, text="Contact Number:", font=("Google Sans", 20), bg="#171d29", fg="white").place(x=695, y=211)

        self.address_entry = tk.Entry(self.root, font=("Google Sans", 15), width=35, relief="flat", highlightthickness=1, highlightbackground="gray", bd=6)
        self.address_entry.place(x=172, y=246)
        self.address_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.address_entry))


        self.contact_entry = tk.Entry(self.root, font=("Google Sans", 15), width=18, relief="flat", highlightthickness=1, highlightbackground="gray", bd=6)
        self.contact_entry.place(x=697, y=246)
        self.contact_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.contact_entry))


        self.keyboard_frame = tk.Frame(self.root, bg="#171d29")
        self.keyboard_frame.place(x=165, y=320)
        self.create_keyboard()


        self.done_button = tk.Button(self.root, text="Done", command=self.create_facility_info_page, bg="#4CAF50", fg="white", font=("Google Sans", 16, "bold"))
        self.done_button.place(x=765, y=460, width=194, height=82)

    def create_facility_info_page(self):
        if hasattr(self, 'name_entry') and self.name_entry.winfo_exists():
            self.patient_name = self.name_entry.get()
        if hasattr(self, 'age_entry') and self.age_entry.winfo_exists():
            self.age = self.age_entry.get()
        if hasattr(self, 'address_entry') and self.address_entry.winfo_exists():
            self.address = self.address_entry.get()
        if hasattr(self, 'contact_entry') and self.contact_entry.winfo_exists():
            self.contact = self.contact_entry.get()
        if hasattr(self, 'sex_entry') and self.sex_entry.winfo_exists():
            self.sex = self.sex_entry.get()

        print('Patient Name:', self.patient_name)
        print('Age:', self.age)
        print('Address:', self.address)
        print('Contact Number:', self.contact)
        print('Sex:', self.sex )        
        self.clear_frame()

        self.exit_button = tk.Button(self.root, text="✕", command=self.root.quit, fg="red", font=("Comfortaa", 24, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=930, y=31, width=24, height=24)

        tk.Label(self.root, text="Facility Information", font=("Google Sans", 40), bg="#171d29", fg="white").place(x=330, y=40)

        tk.Label(self.root, text="Facility Name", font=("Google Sans", 20), bg="#171d29", fg="white").place(x=460, y=118)

        self.facility_name_entry = tk.Entry(self.root, font=("Google Sans", 20), width=25, relief="flat", highlightthickness=1, highlightbackground="gray", bd=6)
        self.facility_name_entry.place(x=330, y=152)
        self.facility_name_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.facility_name_entry))


        tk.Label(self.root, text="Email", font=("Google Sans", 20), bg="#171d29", fg="white").place(x=500, y=211)

        self.facility_email_entry = tk.Entry(self.root, font=("Google Sans", 20), width=25, relief="flat", highlightthickness=1, highlightbackground="gray", bd=6)
        self.facility_email_entry.place(x=330, y=246)
        self.facility_email_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.facility_email_entry))
        self.facility_email = self.facility_email_entry.get()
        print(self.address)


        self.keyboard_frame = tk.Frame(self.root, bg="#171d29")
        self.keyboard_frame.place(x=165, y=320)
        self.create_keyboard()


        self.done_button = tk.Button(self.root, text="Done", command=self.create_initial_page, bg="#4CAF50", fg="white", font=("Google Sans", 16, "bold"))
        self.done_button.place(x=765, y=460, width=194, height=82)
    
    def create_keyboard(self):
        keys = [
            "1234567890",
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNÑM",
            "._-@"
        ]
        
        for row_index, row in enumerate(keys):
            for col_index, key in enumerate(row):
                button = tk.Button(self.keyboard_frame, text=key, font=("Google Sans", 12), width=6, height=2,
                                   command=lambda k=key: self.insert_character(k))
                button.grid(row=row_index, column=col_index)
                
        backspace_button = tk.Button(self.keyboard_frame, text="Backspace", font=("Google Sans", 12), width=16, height=2, command=self.backspace_character)
        backspace_button.grid(row=0, column=16, columnspan=16)

        space_button = tk.Button(self.keyboard_frame, text="Space", font=("Google Sans", 12), width=16, height=2, command=lambda: self.insert_character(" "))
        space_button.grid(row=1, column=16, columnspan=16)
    
    def backspace_character(self):
        if self.active_entry:
            current_text = self.active_entry.get()
            self.active_entry.delete(len(current_text) - 1, tk.END)


    def set_active_entry(self, entry):
        """ Set the active entry field. """
        self.active_entry = entry

    def insert_character(self, char):
        """ Insert character into the active entry field. """
        if self.active_entry:
            self.active_entry.insert(tk.END, char)



    def capture_image(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                # frame = self.apply_gamma_correction(frame, gamma=0.5)  # Adjust gamma as needed

                self.captured_image = frame
                self.cap.release()
                self.show_preview_page()
                

    def upload_image(self):
        self.filename = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if self.filename:
            self.captured_image = cv2.imread(self.filename)
            self.show_preview_page()
        if self.captured_image is not None:
            self.image = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2RGB)
            self.image = cv2.resize(self.image, (720, 860))
            self.image = ImageTk.PhotoImage(Image.fromarray(self.image))
        else:
            self.image = ImageTk.PhotoImage(Image.new('RGB', (720, 860), 'black'))
        return self.image
    




    def update_camera_feed(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

                # Apply camera brightness adjustment
                brightness_scale = self.brightness_value / 50.0  # 0 to 2 range
                frame = np.clip(frame * brightness_scale, 0, 255).astype(np.uint8)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (515, 615), interpolation=cv2.INTER_LINEAR)

                self.current_frame = ImageTk.PhotoImage(Image.fromarray(frame))
                if self.camera_label.winfo_exists():
                    self.camera_label.config(image=self.current_frame)

            self.root.after(10, self.update_camera_feed)

    def update_camera_brightness(self, value):
        self.brightness_value = int(value)

    def create_initial_page(self):
        if hasattr(self, 'facility_name_entry') and self.facility_name_entry.winfo_exists():
            self.facility_name = self.facility_name_entry.get()
        if hasattr(self, 'facility_email_entry') and self.facility_email_entry.winfo_exists():
            self.facility_email = self.facility_email_entry.get()

        print('Facility Name:', self.facility_name)
        print('Facility Email:', self.facility_email)

        
        self.clear_frame()
        self.brightness_value = 50  # Reset brightness value
        
        self.exit_button = tk.Button(self.root, text="✕", command=self.root.quit, fg="red", font=("Comfortaa", 24, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=1030, y=31, width=24, height=24)
        
        self.camera_label = tk.Label(self.root, width=515, height=600, bg="black", bd=0)
        self.camera_label.place(x=10, y=5)
        
        self.capture_button = tk.Button(
            self.root, text="Capture", command=self.capture_image, bg="#1a80e6", fg="white", font=("Google Sans", 16, "bold")
        )
        self.capture_button.place(x=550, y=250, width=499, height=62)
        
        self.upload_button = tk.Button(
            self.root, text="Upload", command=self.upload_image, bg="#234679", fg="white", font=("Google Sans", 16, "bold")
        )
        self.upload_button.place(x=550, y=320, width=499, height=62)
    
        tk.Label(self.root, text="Live Brightness", bg="#171d29", fg="white", font=("Google Sans", 14)).place(x=550, y=400)
        self.camera_brightness_slider = tk.Scale(
            self.root,
            from_=0,
            to=500,
            orient="horizontal",
            length=499,
            sliderlength=30,  # 🔼 Increase to make slider thicker
            bg="#171d29",
            fg="white",
            troughcolor="gray",
            highlightthickness=0,
            command=self.update_camera_brightness
        )

        self.camera_brightness_slider.set(self.brightness_value)
        self.camera_brightness_slider.place(x=550, y=430)


            # Start camera thread to reduce boot delay
        threading.Thread(target=self.initialize_camera, daemon=True).start()
                
        # self.cap = cv2.VideoCapture(0)
        # if not self.cap.isOpened():
        #     print("Error: Unable to access external webcam.")
        #     self.cap = cv2.VideoCapture(0)
        # self.update_camera_feed()

    def get_processed_image(self, resize_to=None, as_tk_image=False):
        if self.captured_image is None:
            return None

        image = self.captured_image.copy()
        h, w, _ = image.shape

        # Ensure valid crop values
        crop_bottom = min(self.crop_bottom, h - self.crop_top - 1)
        crop_right = min(self.crop_right, w - self.crop_left - 1)

        # Crop
        image = image[self.crop_top:h - crop_bottom, self.crop_left:w - crop_right]

        # Brightness adjustment
        brightness_scale = self.brightness_value / 50.0
        image = np.clip(image * brightness_scale, 0, 255).astype(np.uint8)

        # Convert color
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Resize if needed
        if resize_to:
            image = cv2.resize(image, resize_to)

        if as_tk_image:
            return ImageTk.PhotoImage(Image.fromarray(image))
        else:
            return image

    
    def initialize_camera(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use CAP_DSHOW for faster initialization on Windows

        if not self.cap.isOpened():
            print("Error: Unable to access external webcam.")
            return
        
        # Set camera resolution early to avoid resizing lag
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.update_camera_feed()

#### HELPER MEHODS

    def add_crop_controls(self):
        # Dictionary to store slider values
        self.crop_values = {}

        # Crop options without column positioning
        crop_options = [
            ("Top", "top", 50),
            ("Bottom", "bottom", 120),
            ("Left", "left", 190),
            ("Right", "right", 260)
        ]

        x_offset = 550  # Keep all sliders aligned at this x position

        for label, direction, y_pos in crop_options:
            # Create label
            tk.Label(self.root, text=label, bg="#171d29", fg="white", font=("Google Sans", 16, "bold")).place(x=x_offset, y=y_pos)

            # Create slider (Scale) for smooth cropping control (0-50)
            slider = tk.Scale(self.root, from_=0, to=500, orient="horizontal", length=350,
                            bg="#171d29", fg="white", troughcolor="gray", highlightthickness=0,
                            command=lambda value, d=direction: self.adjust_crop(d, int(value)))
            slider.place(x=x_offset + 100, y=y_pos)
            
            # Store slider reference
            self.crop_values[direction] = slider



    def adjust_crop(self, direction, value):
        """ Set cropping value directly instead of incrementing. """
        if direction == "top":
            self.crop_top = value
        elif direction == "bottom":
            self.crop_bottom = value
        elif direction == "left":
            self.crop_left = value
        elif direction == "right":
            self.crop_right = value

        self.update_preview_image()




    def process_image(self):

        self.show_result_page()

        #update the self.captured_image with the processed image
        self.captured_image = self.get_processed_image(resize_to=(400, 478), as_tk_image=False)

        processed_image = self.get_processed_image(resize_to=(400, 478), as_tk_image=True)
        if processed_image:
            self.result_image_label.config(image=processed_image)
            self.result_image_label.image = processed_image
            
    


        
    def update_preview_image(self):
        preview_image = self.get_processed_image(resize_to=(515, 615), as_tk_image=True)
        if preview_image:
            self.image_label.config(image=preview_image)
            self.image_label.image = preview_image  # Prevent garbage collection



    def update_brightness(self, value):
        self.brightness_value = int(value)
        self.update_preview_image()


### HELPER END

    def show_preview_page(self):
        self.clear_frame()
        self.close_camera()

        # Initialize crop values
        self.crop_top = 0
        self.crop_bottom = 0
        self.crop_left = 0
        self.crop_right = 0

        self.exit_button = tk.Button(self.root, text="✕", command=self.root.quit, fg="red",
                                    font=("Comfortaa", 24, "bold"), bd=0, bg="#171d29", 
                                    activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=1030, y=31, width=24, height=24)

        # Image display label
        

        self.image_label = tk.Label(self.root, width=515, height=600, bg="black", bd=0)
        self.image_label.place(x=10, y=5)

        self.update_preview_image()  # Update the image with the initial crop values


        # Crop adjustment buttons
        self.add_crop_controls()

        # Buttons for processing and retaking
        self.proceed_button = tk.Button(self.root, text="Process", command=self.process_image, 
                                        bg="#1a80e6", fg="white", font=("Google Sans", 16, "bold"))
        self.proceed_button.place(x=550, y=350, width=499, height=62)

        self.retake_button = tk.Button(self.root, text="Retake Photo", command=self.create_initial_page, 
                                    bg="#234679", fg="white", font=("Google Sans", 16, "bold"))
        self.retake_button.place(x=550, y=420, width=499, height=62)

    # def resize_image_keep_aspect(self, img, max_width, max_height):
    #     h, w = img.shape[:2]
    #     scale = min(max_width / w, max_height / h)
    #     new_w, new_h = int(w * scale), int(h * scale)
    #     return cv2.resize(img, (new_w, new_h))

    
    def show_result_page(self):
        self.clear_frame()
        self.close_camera()
        # Classify the captured image
        # classification_result, self.normal_confidence, self.bacterial_confidence, self.viral_confidence, self.others_confidence = self.classify_pneumonia()
        
        # Convert confidence levels to percentages
        self.normal_confidence_level = self.normal_confidence 
        self.viral_confidence_level = self.viral_confidence
        self.bacterial_confidence_level = self.bacterial_confidence 
        self.others_confidence_level = self.others_confidence 

        result_title_label = tk.Label(self.root, text="Pneumonia Detection and Classification", font=("Google Sans", 18), bg="#171d29", fg="white")
        result_title_label.place(x=490, y=21)

        self.back_button = tk.Button(self.root, text="Back", command=self.create_initial_page, bg="#1a80e6", fg="white", font=("Google Sans", 15, "bold"))
        self.back_button.place(x=938, y=530, width=140, height=35)

        self.result_image_label = tk.Label(self.root, width=400, height=478, bg="black", bd=0)
        self.result_image_label.place(x=10, y=5)

        self.priority_level = "LOW"  # Placeholder for priority level

        patient_data = {
            "Patient Name": self.patient_name,
            "Age": self.age,
            "Sex": self.sex,
            "Address": self.address,
            "Contact Number": self.contact,
        }
        print(patient_data)
        y_position = 84
        for key, value in patient_data.items():
            label = tk.Label(self.root, text=f"{key}: {value}", font=("Google Sans", 14), bg="#171d29", fg="white")
            label.place(x=420, y=y_position)
            y_position += 28
        
        self.line = tk.Label(self.root, text="_____________________________________________________________________________________________", font=("Google Sans", 10), bg="#171d29", fg="#234679")
        self.second_line = tk.Label(self.root, text="_____________________________________________________________________________________________", font=("Google Sans", 10), bg="#171d29", fg="#234679")
        self.third_line = tk.Label(self.root, text="_____________________________________________________________________________________________", font=("Google Sans", 10), bg="#171d29", fg="#234679")
        self.fourth_line = tk.Label(self.root, text="_____________________________________________________________________________________________", font=("Google Sans", 10), bg="#171d29", fg="#234679")

        self.line.place(x=420, y=224)
        self.second_line.place(x=420, y=273)
        self.third_line.place(x=420, y=322)
        self.fourth_line.place(x=420, y=371)

        self.normal_confidence_label = tk.Label(self.root, text=f"Normal:", font=("Google Sans", 14), bg="#171d29", fg="white")
        self.normal_confidence_label.place(x=420, y=252)
        self.normal_confidence_level_label = tk.Label(self.root, text=f"Confidence Level: {self.normal_confidence_level}%", font=("Google Sans", 14, "bold"), bg="#171d29", fg="white")
        self.normal_confidence_level_label.place(x=595, y=252)

        self.viral_confidence_label = tk.Label(self.root, text=f"Viral:", font=("Google Sans", 14), bg="#171d29", fg="white")
        self.viral_confidence_label.place(x=420, y=301)
        self.viral_confidence_level_label = tk.Label(self.root, text=f"Confidence Level: {self.viral_confidence_level}%", font=("Google Sans", 14, "bold"), bg="#171d29", fg="white")
        self.viral_confidence_level_label.place(x=595, y=301)

        self.bacterial_confidence_label = tk.Label(self.root, text=f"Bacterial:", font=("Google Sans", 14), bg="#171d29", fg="white")
        self.bacterial_confidence_label.place(x=420, y=350)
        self.bacterial_confidence_level_label = tk.Label(self.root, text=f"Confidence Level: {self.bacterial_confidence_level}%", font=("Google Sans", 14, "bold"), bg="#171d29", fg="white")
        self.bacterial_confidence_level_label.place(x=595, y=350)

        self.others_confidence_label = tk.Label(self.root, text=f"Others:", font=("Google Sans", 14), bg="#171d29", fg="white")
        self.others_confidence_label.place(x=420, y=399)
        self.others_confidence_level_label = tk.Label(self.root, text=f"Confidence Level: {self.others_confidence_level}%", font=("Google Sans", 14, "bold"), bg="#171d29", fg="white")
        self.others_confidence_level_label.place(x=595, y=399)

        self.priority_label = tk.Label(self.root, text=f"Priority Level:", font=("Google Sans", 16), bg="#1a345b", fg="white", bd=21)
        self.priority_label.place(x=840, y=455)

        self.priority_level_label = tk.Label(self.root, text=f"{self.priority_level}", font=("Google Sans", 16, "bold"), bg="#1a345b", fg="white", bd=0, padx=7, pady=22, anchor="w")
        self.priority_level_label.place(x=994, y=455, width=84)

        self.print_as_pdf_button = tk.Button(self.root, text="Print as Pdf", command=self.generate_pdf, bg="#1a80e6", fg="white", font=("Google Sans", 8, "bold"))
        self.print_as_pdf_button.place(x=875, y=84, width=140, height=35)

        self.send_to_doctor_button = tk.Button(self.root, text="Send to Doctor", command=self.send_to_doctor_page, bg="#234679", fg="white", font=("Google Sans", 8, "bold"))
        self.send_to_doctor_button.place(x=875, y=133, width=140, height=35)

    def generate_pdf(self):
        timestamp = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        directory = "C:/Documents/Generated_PDF/"
        os.makedirs(directory, exist_ok=True)

        # template_path = "REAL-SCREENING-RESULT.pdf"
        template_path = "REAL-CHEST-RADIOGRAPH-INITIAL-SCREENING-RESULT.pdf"
        output_pdf_path = os.path.join(directory, f"{self.patient_name}_pneumonia_report_{timestamp}.pdf")

        # Read the template PDF
        template_reader = PdfReader(template_path)
        output_writer = PdfWriter()

        # Create an overlay with reportlab
        overlay_path = os.path.join(directory, "overlay.pdf")
        overlay_canvas = canvas.Canvas(overlay_path, pagesize=letter)

        # Set patient details dynamically
        overlay_canvas.setFont("Helvetica", 12)
        overlay_canvas.drawString(270, 622, self.patient_name)  # Name
        overlay_canvas.drawString(270, 600, self.age)  # Age
        overlay_canvas.drawString(270, 575, self.sex)  # Sex
        overlay_canvas.drawString(270, 550, self.address)  # Address
        overlay_canvas.drawString(270, 525, self.contact)  # Contact Number
        timestamp_released = datetime.now().strftime("%B %d, %Y").upper()
        overlay_canvas.drawString(270, 475, timestamp_released) # requested
        overlay_canvas.drawString(270, 450, timestamp_released) # released
        overlay_canvas.drawString(270, 425, self.facility_name) # requested
        overlay_canvas.drawString(270, 400, self.facility_email) # released
        # Set screening results
        # Set screening results
        overlay_canvas.drawString(300, 306, self.priority_level)

        overlay_canvas.drawString(300, 230, self.normal_confidence_level)  # Normal
        overlay_canvas.drawString(300, 200, self.viral_confidence_level)  # Viral
        overlay_canvas.drawString(300, 172, self.bacterial_confidence_level)  # Bacterial
        overlay_canvas.drawString(300, 142, self.others_confidence_level)  # Others

        overlay_canvas.save()

        # Merge template and overlay
        overlay_reader = PdfReader(overlay_path)
        template_page = template_reader.pages[0]
        template_page.merge_page(overlay_reader.pages[0])

        output_writer.add_page(template_page)

        # ✅ **Second Page (Full-Size Image)**
        if self.captured_image is not None:
            temp_full_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)  # Temp file for full image
            cv2.imwrite(temp_full_img.name, self.captured_image)  # Save full image
            temp_full_img_path = temp_full_img.name
            temp_full_img.close()

            second_page_path = os.path.join(directory, "second_page.pdf")
            second_canvas = canvas.Canvas(second_page_path, pagesize=letter)

            # Dynamically scale image to fit within page (8.5x11 inches minus margins)
            page_width, page_height = letter
            img_width, img_height = 500, 600  # Adjust as needed to fit page

            x_position = (page_width - img_width) / 2
            y_position = (page_height - img_height) / 2

            second_canvas.drawImage(temp_full_img_path, x_position, y_position, width=img_width, height=img_height)
            second_canvas.save()

            # Add second page to PDF
            second_page_reader = PdfReader(second_page_path)
            output_writer.add_page(second_page_reader.pages[0])

            # Cleanup temporary files
            os.remove(temp_full_img_path)
            os.remove(second_page_path)

        with open(output_pdf_path, "wb") as output_pdf:
            output_writer.write(output_pdf)

        # Remove temporary overlay file
        os.remove(overlay_path)

        messagebox.showinfo("PDF Generated", f"Pneumonia report saved as {output_pdf_path}")
        return output_pdf_path
    
    def send_email(self):
        receiver_email = self.email_entry.get()
        if not receiver_email:
            messagebox.showerror("Error", "Please enter a valid email address.")
            return
        
        pdf_filename = self.generate_pdf()
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")

        # password is generated from the app password in gmail
        # REFERENCE: https://support.google.com/mail/answer/185833?hl=en
        # ENABLE 2-STEP VERIFICATION FIRST
        subject = "Pneumonia Detection and Classification Report"
        body = "Attached is the pneumonia detection report."
        
        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.set_content(body)
        
        # Extract only the file name from the full path
        file_name = os.path.basename(pdf_filename)
        
        with open(pdf_filename, "rb") as f:
            file_data = f.read()
            msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)
        
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
            messagebox.showinfo("Success", "Email sent successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {e}")
    
    
    def send_to_doctor_page(self):
        self.clear_frame()
        tk.Label(self.root, text="Pneumonia Detection and Classification", font=("Google Sans", 20), bg="#171d29", fg="white").pack(pady=20)
        tk.Label(self.root, text="Enter the radiology department’s email address:", font=("Google Sans", 14), bg="#171d29", fg="white").pack(pady=10)
        self.email_entry = tk.Entry(self.root, font=("Google Sans", 14), width=40)
        self.email_entry.pack(pady=10)
        self.set_active_entry(self.email_entry)
        
        tk.Button(self.root, text="Send to Doctor", command=self.send_email, bg="#1a80e6", fg="white", font=("Google Sans", 16, "bold"), width=20).pack(pady=10)
        tk.Button(self.root, text="Back to Patient Info", command=self.create_patient_info_page, bg="#234679", fg="white", font=("Google Sans", 16, "bold"), width=20).pack(pady=10)
        
        self.keyboard_frame = tk.Frame(self.root, bg="#171d29")
        self.keyboard_frame.pack(pady=20)
        self.create_keyboard()
    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def close_camera(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close_camera)
    root.mainloop()