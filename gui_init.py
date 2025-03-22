import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2

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
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.applications.vgg16 import VGG16
import torch
from transformers import ViTImageProcessor, ViTForImageClassification

original_width, original_height = 1080, 1920
scale_steps = 50
scale_factor = 0.02  # 5% decrease per step

scaled_sizes = [
    (int(original_width * (1 - scale_factor * step)), 
     int(original_height * (1 - scale_factor * step)))
    for step in range(scale_steps + 1)
]

print(scaled_sizes)

# 1440

# 810
class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)  # Remove title bar
        self.root.geometry("1100x800")  # Set to landscape
        self.root.configure(bg="#171d29")
        #center-top the window

        self.current_frame = None
        self.captured_image = None
        self.filename = None
        self.patient_name = ""
        self.normal_confidence = 0
        self.viral_confidence = 0
        self.bacterial_confidence = 0
        self.age = 0
        self.address = ""
        self.contact = ""
        self.sex = ""
        self.active_entry = None
        self.others_confidence = 0
        self.priority_level = ""
        self.cap = None
        self.image = None

        self.create_patient_info_page()
        
        # showing the result page immediately for testing
        # self.show_result_page()
        self.weights_path = r""



    def classify_pneumonia(self):
        # ✅ DEVICE CONFIGURATION
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # ✅ LOAD ViT MODEL (Fine-Tuning Enabled)
        vit_model_name = "facebook/dino-vits16"
        vit_processor = ViTImageProcessor.from_pretrained(vit_model_name)
        vit_model = ViTForImageClassification.from_pretrained(vit_model_name, num_labels=3).to(device)

        def vit_forward(image_batch):
            def process_images(images):
                images = images.numpy()
                images = (images * 255).astype(np.uint8)
                inputs = vit_processor(images=images, return_tensors="pt").to(device)
                outputs = vit_model(**inputs)
                features = torch.nn.functional.softmax(outputs.logits, dim=1).cpu().detach().numpy()
                return np.expand_dims(features, axis=-1)

            return tf.py_function(func=process_images, inp=[image_batch], Tout=tf.float32)

        # ✅ LOAD VGG MODEL (Frozen Backbone)
        vgg_base = VGG16(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
        vgg_model = Model(inputs=vgg_base.input, outputs=Flatten()(vgg_base.output))

        # ✅ HYBRID MODEL CLASS
        class HybridModel(Model):
            def __init__(self, vgg_model, vit_forward, **kwargs):
                super(HybridModel, self).__init__(**kwargs)
                self.vgg_model = Model(inputs=vgg_model.input, outputs=vgg_model.output)
                self.vgg_fc = Dense(512, activation="relu")
                self.vit_forward = vit_forward
                self.vit_fc = Dense(512, activation="relu")
                self.fc = Dense(3, activation="softmax")

            def call(self, inputs, training=False):
                vgg_features = self.vgg_model(inputs)
                vgg_features = self.vgg_fc(vgg_features)
                vit_features = self.vit_forward(inputs)
                vit_features = tf.reshape(vit_features, (-1, 3))
                vit_features = self.vit_fc(vit_features)
                merged_features = (vgg_features + vit_features) / 2
                return self.fc(merged_features)

        # ✅ RECREATE MODEL
        hybrid_model = HybridModel(vgg_model, vit_forward)

        # ✅ INITIALIZE MODEL
        dummy_input = tf.random.normal((1, 224, 224, 3))
        _ = hybrid_model(dummy_input)
        hybrid_model.build(input_shape=(None, 224, 224, 3))

        # ✅ LOAD WEIGHTS
        hybrid_model.load_weights(self.weights_path)
        print("\n✅ Model loaded successfully!")

        # ✅ DEFINE CLASS LABELS
        class_labels = {1: "Normal", 0: "Bacterial Pneumonia", 2: "Viral Pneumonia"}

        def preprocess_image(cv_image):
            img = cv2.resize(cv_image, (224, 224))
            img_array = np.expand_dims(img, axis=0) / 255.0
            return img_array

        # ✅ PREDICTION
        img_array = preprocess_image(self.captured_image)
        predictions = hybrid_model.predict(img_array)
        class_probs = predictions[0]
        class_index = np.argmax(class_probs)

        # Extract confidence levels
        normal_confidence = class_probs[1]
        bacterial_confidence = class_probs[0]
        viral_confidence = class_probs[2]

        print("\n📊 Classification Confidence Levels:")
        for idx, label in class_labels.items():
            print(f"   {label}: {class_probs[idx] * 100:.2f}%")

        final_prediction = f"\n✅ Final Prediction: {class_labels[class_index]} with {class_probs[class_index] * 100:.2f}% confidence.\n"
        print(final_prediction)

        return class_labels[class_index], normal_confidence, bacterial_confidence, viral_confidence






    def create_patient_info_page(self):
        self.clear_frame()

        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 24, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=930, y=31, width=24, height=24)

        tk.Label(self.root, text="Hello!", font=("Google Sans", 40), bg="#171d29", fg="white").place(x=503, y=40)

        tk.Label(self.root, text="Patient's Name:", font=("Google Sans", 20), bg="#171d29", fg="white").place(x=172, y=118)
        tk.Label(self.root, text="Age:", font=("Google Sans", 20), bg="#171d29", fg="white").place(x=697, y=118)
        tk.Label(self.root, text="Sex:", font=("Google Sans", 20), bg="#171d29", fg="white").place(x=870, y=118)

        self.name_entry = tk.Entry(self.root, font=("Google Sans", 20), width=25, relief="flat", highlightthickness=1, highlightbackground="gray", bd=6)
        self.name_entry.place(x=172, y=152)
        self.name_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.name_entry))


        self.age_entry = tk.Entry(self.root, font=("Google Sans", 20), width=4, relief="flat", highlightthickness=1, highlightbackground="gray", bd=6)
        self.age_entry.place(x=697, y=152)
        self.age_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.age_entry))
        self.age = self.age_entry.get() 
        print(self.age)

        self.sex_entry = tk.Entry(self.root, font=("Google Sans", 20), width=4, relief="flat", highlightthickness=1, highlightbackground="gray", bd=6)
        self.sex_entry.place(x=870, y=152)
        self.sex_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.sex_entry))
        self.sex = self.sex_entry.get()
        print(self.sex)

        tk.Label(self.root, text="Address:", font=("Google Sans", 20), bg="#171d29", fg="white").place(x=172, y=211)
        tk.Label(self.root, text="Contact Number:", font=("Google Sans", 20), bg="#171d29", fg="white").place(x=695, y=211)

        self.address_entry = tk.Entry(self.root, font=("Google Sans", 20), width=25, relief="flat", highlightthickness=1, highlightbackground="gray", bd=6)
        self.address_entry.place(x=172, y=246)
        self.address_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.address_entry))
        self.address = self.address_entry.get()
        print(self.address)

        self.contact_entry = tk.Entry(self.root, font=("Google Sans", 20), width=14, relief="flat", highlightthickness=1, highlightbackground="gray", bd=6)
        self.contact_entry.place(x=697, y=246)
        self.contact_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.contact_entry))
        self.contact = self.contact_entry.get()
        print(self.contact)

        self.keyboard_frame = tk.Frame(self.root, bg="#171d29")
        self.keyboard_frame.place(x=165, y=320)
        self.create_keyboard()


        self.done_button = tk.Button(self.root, text="Done", command=self.create_initial_page, bg="#4CAF50", fg="white", font=("Google Sans", 16, "bold"))
        self.done_button.place(x=805, y=500, width=155, height=82)
    
    def create_keyboard(self):
        self.caps_lock = False

        self.capitalized_keys = [
            "1234567890",
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNÑM",
            "._-@"
        ]

        self.non_capitalized_keys = [
            "1234567890",
            "qwertyuiop",
            "asdfghjkl",
            "zxcvbnñm",
            "._-@"
        ]

        self.keys = self.non_capitalized_keys

        self.render_keyboard()

    def render_keyboard(self):
        for widget in self.keyboard_frame.winfo_children():
            widget.destroy()

        caps_lock_button = tk.Button(self.keyboard_frame, text="Caps Lock", font=("Google Sans", 12), width=16, height=2, command=self.toggle_caps_lock)
        caps_lock_button.grid(row=2, column=16, columnspan=6)

        for row_index, row in enumerate(self.keys):
            for col_index, key in enumerate(row):
                button = tk.Button(self.keyboard_frame, text=key, font=("Google Sans", 12), width=6, height=2,
                                   command=lambda k=key: self.insert_character(k))
                button.grid(row=row_index, column=col_index)

        backspace_button = tk.Button(self.keyboard_frame, text="Backspace", font=("Google Sans", 12), width=16, height=2, command=self.backspace_character)
        backspace_button.grid(row=0, column=16, columnspan=16)

        space_button = tk.Button(self.keyboard_frame, text="Space", font=("Google Sans", 12), width=16, height=2, command=lambda: self.insert_character(" "))
        space_button.grid(row=1, column=16, columnspan=16)

    def toggle_caps_lock(self):
        self.caps_lock = not self.caps_lock
        self.keys = self.capitalized_keys if self.caps_lock else self.non_capitalized_keys
        self.render_keyboard()
    
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
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                self.captured_image = frame
                self.cap.release()
                self.show_preview_page()
                

    def upload_image(self):
        self.filename = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if self.filename:
            self.captured_image = cv2.imread(self.filename)
            self.show_preview_page()

    def image_preview_prepare(self):
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
                # Rotate frame to portrait orientation
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

                # Convert frame to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Get original aspect ratio (portrait mode)
                # original_h, original_w = frame.shape[:2]  # 1080x1920 becomes 1920x1080 after rotation

                # # Target display size (modify these based on your UI dimensions)
                # target_w, target_h = 720, 960

                # # Calculate the scaling factor
                # scale_factor = min(target_w / original_w, target_h / original_h)

                # # Compute new dimensions while maintaining aspect ratio
                # new_w = int(original_w * scale_factor)
                # new_h = int(original_h * scale_factor)
                #(515, 615)

                # Resize while keeping aspect ratio
                # frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
                frame = cv2.resize(frame, (515, 615), interpolation=cv2.INTER_LINEAR)


                # Convert frame for tkinter
                self.current_frame = ImageTk.PhotoImage(Image.fromarray(frame))

                # Ensure the label exists before updating
                if self.camera_label.winfo_exists():
                    self.camera_label.config(image=self.current_frame)

                # Schedule next frame update
                self.root.after(10, self.update_camera_feed)

    def create_initial_page(self):
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
        
        self.clear_frame()
        
        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 24, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
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
        
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            print("Error: Unable to access external webcam.")
            self.cap = cv2.VideoCapture(1)
        self.update_camera_feed()

    def show_preview_page(self):
        self.clear_frame()
        
        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 24, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=1030, y=31, width=24, height=24)
        
        image = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (515, 615))  # Scaled up by 10%
        image = ImageTk.PhotoImage(Image.fromarray(image))
        
        self.image_label = tk.Label(self.root, image=image, width=515, bg="black", height=600, bd=0)  # Scaled up by 10%
        self.image_label.image = image
        self.image_label.place(x=10, y=5)
        
        self.proceed_button = tk.Button(
            self.root, text="Process", command=self.show_result_page, bg="#1a80e6", fg="white", font=("Google Sans", 16, "bold")
        )
        self.proceed_button.place(x=550, y=250, width=499, height=62)  # Scaled up by 10%
        
        self.retake_button = tk.Button(
            self.root, text="Retake Photo", command=self.create_initial_page, bg="#234679", fg="white", font=("Google Sans", 16, "bold")
        )
        self.retake_button.place(x=550, y=320, width=499, height=62)  # Scaled up by 10%
    
    def show_result_page(self):
        self.clear_frame()
        
        # Classify the captured image
        classification_result, self.normal_confidence, self.bacterial_confidence, self.viral_confidence = self.classify_pneumonia()
        
        # Convert confidence levels to percentages
        self.normal_confidence_level = self.normal_confidence * 100
        self.viral_confidence_level = self.viral_confidence * 100
        self.bacterial_confidence_level = self.bacterial_confidence * 100

        # You can define logic to set priority level based on confidence scores
        self.priority_level = "Low"  # Modify this logic if needed
        self.others_confidence_level = 100 - (self.normal_confidence_level + self.viral_confidence_level + self.bacterial_confidence_level)



        
        result_title_label = tk.Label(self.root, text="Pneumonia Detection and Classification", font=("Google Sans", 18), bg="#171d29", fg="white")
        result_title_label.place(x=490, y=21)

        self.back_button = tk.Button (self.root, text="Back", command=self.create_initial_page, bg="#1a80e6", fg="white", font=("Google Sans", 12, "bold"))
        self.back_button.place(x=7, y=7, width=70, height=22)

        if self.captured_image is not None:
            resized_image = cv2.resize(self.captured_image, (400, 537))
            resized_image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)))
        else:
            resized_image = ImageTk.PhotoImage(Image.new('RGB', (216, 288), 'black'))

        # image = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2RGB)
        # image = cv2.resize(image, (515, 615))  # Scaled up by 10%
        # image = ImageTk.PhotoImage(Image.fromarray(image))
        
        # self.image_label = tk.Label(self.root, image=image, width=515, bg="black", height=600, bd=0)  # Scaled up by 10%
        # self.image_label.image = image
        # self.image_label.place(x=10, y=5)
        self.result_image_label = tk.Label(self.root, image=resized_image, width=312, bg="black", height=537)
        self.result_image_label.image = resized_image
        self.result_image_label.place(x=70, y=42)

        patient_data = {
            "Patient Name": self.patient_name,
            "Age": self.age,
            "Sex": self.sex,
            "Address": self.address,
            "Contact Number": self.contact,
        }
        
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

        template_path = "CHEST-RADIOGRAPH-TEMPLATE.pdf"
        output_pdf_path = os.path.join(directory, f"{self.patient_name}_pneumonia_report_{timestamp}.pdf")

        # Read the template PDF
        template_reader = PdfReader(template_path)
        output_writer = PdfWriter()

        # Create an overlay with reportlab
        overlay_path = os.path.join(directory, "overlay.pdf")
        overlay_canvas = canvas.Canvas(overlay_path, pagesize=letter)

        # Set patient details dynamically
        overlay_canvas.setFont("Helvetica", 11)
        overlay_canvas.drawString(250, 633, self.priority_level)
        overlay_canvas.drawString(250, 560, self.patient_name)  # Name
        overlay_canvas.drawString(250, 545, self.age)  # Age
        overlay_canvas.drawString(250, 530, self.sex)  # Sex
        overlay_canvas.drawString(250, 515, self.address)  # Address
        overlay_canvas.drawString(250, 500, self.contact)  # Contact Number
        # Set screening results
        overlay_canvas.drawString(250, 190, "Normal")  # Viral
        overlay_canvas.drawString(250, 170, "Viral")  # Bacterial 
        overlay_canvas.drawString(250, 150, "Bacterial")  # Others
        overlay_canvas.drawString(250, 130, "Others")  # Normal (example) 

        if self.captured_image is not None:
            temp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)  # Create a temp image file
            cv2.imwrite(temp_img.name, self.captured_image)  # Save the image
            temp_img_path = temp_img.name  # Get the file path
            temp_img.close()  # Close the file

            # ✅ Pass the file path to drawImage() instead of the PhotoImage object
            overlay_canvas.drawImage(temp_img_path, 210, 250, width=151.2, height=226.8)

        overlay_canvas.save()

        # Merge template and overlay
        overlay_reader = PdfReader(overlay_path)
        template_page = template_reader.pages[0]
        template_page.merge_page(overlay_reader.pages[0])

        output_writer.add_page(template_page)

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
        sender_email=os.getenv("SENDER_EMAIL")
        sender_password=os.getenv("SENDER_PASSWORD")

        # password is generated from the app password in gmail
        # REFRENCE: https://support.google.com/mail/answer/185833?hl=en
        # ENABLE 2-STEP VERIFICATION FIRST
        subject = "Pneumonia Detection and Classification Report"
        body = "Attached is the pneumonia detection report."
        
        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.set_content(body)
        
        with open(pdf_filename, "rb") as f:
            file_data = f.read()
            msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=pdf_filename)
        
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
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close_camera)
    root.mainloop()
