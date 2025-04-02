import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2

import os
import ssl
import threading

# Use the certifi path for SSL


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


class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(False)  # Remove title bar
        self.root.geometry("1100x800")  # Set to landscape
        self.root.configure(bg="#171d29")

        self.current_frame = None
        self.captured_image = None
        self.filename = None
        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # Initialize here

        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                self.captured_image = frame
                self.cap.release()
        
        self.create_initial_page()

        
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
                


    def initialize_camera(self):
        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # Use CAP_DSHOW for faster initialization on Windows

        if not self.cap.isOpened():
            print("Error: Unable to access external webcam.")
            return
        
        # Set camera resolution early to avoid resizing lag
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.update_camera_feed()

    def update_camera_feed(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Rotate frame to portrait orientation
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

                # Apply brightness reduction
                # frame = self.apply_gamma_correction(frame, gamma=0.5)  # Adjust gamma as needed
                # frame = reduce_brightness(frame)  # Alternative method

                # Convert frame for display
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (515, 615), interpolation=cv2.INTER_LINEAR)

                # Convert frame for tkinter
                self.current_frame = ImageTk.PhotoImage(Image.fromarray(frame))

                # Ensure the label exists before updating
                if self.camera_label.winfo_exists():
                    self.camera_label.config(image=self.current_frame)

                # Schedule next frame update
                self.root.after(10, self.update_camera_feed)

    
    def create_initial_page(self):

        
        self.clear_frame()
        
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

            # Start camera thread to reduce boot delay
        threading.Thread(target=self.initialize_camera, daemon=True).start()
        
        # self.cap = cv2.VideoCapture(0)
        # if not self.cap.isOpened():
        #     print("Error: Unable to access external webcam.")
        #     self.cap = cv2.VideoCapture(0)
        # self.update_camera_feed()

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


                #         tk.Button(self.root, text="+", command=lambda d=direction: self.adjust_crop(d, 5)).place(x=600, y=y_pos, width=62, height=62)
        #         tk.Button(self.root, text="-", command=lambda d=direction: self.adjust_crop(d, -5)).place(x=630, y=y_pos, width=62, height=62)

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

        self.update_preview_image()  # Update image in real-time


    def process_image(self):
        image = self.captured_image.copy()
        h, w, _ = image.shape

        # Apply the final crop values
        final_cropped = image[self.crop_top:h - self.crop_bottom, self.crop_left:w - self.crop_right]
        
        # Save the cropped version for further processing
        self.captured_image = final_cropped
        self.show_result_page()

    def update_preview_image(self):
        if self.captured_image is None:
            return

        image = self.captured_image.copy()
        h, w, _ = image.shape

        # Ensure valid crop values
        crop_bottom = min(self.crop_bottom, h - self.crop_top - 1)
        crop_right = min(self.crop_right, w - self.crop_left - 1)

        cropped_image = image[self.crop_top:h - crop_bottom, self.crop_left:w - crop_right]

        cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
        cropped_image = cv2.resize(cropped_image, (515, 615))  
        cropped_image = ImageTk.PhotoImage(Image.fromarray(cropped_image))

        self.image_label.config(image=cropped_image)
        self.image_label.image = cropped_image  # Prevent garbage collection


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

        self.update_preview_image()  # Show initial image

        # Crop adjustment buttons
        self.add_crop_controls()

        # Buttons for processing and retaking
        self.proceed_button = tk.Button(self.root, text="Save Image", command=self.save_image, 
                                        bg="#1a80e6", fg="white", font=("Google Sans", 16, "bold"))
        self.proceed_button.place(x=550, y=350, width=499, height=62)

        self.retake_button = tk.Button(self.root, text="Retake Photo", command=self.create_initial_page, 
                                    bg="#234679", fg="white", font=("Google Sans", 16, "bold"))
        self.retake_button.place(x=550, y=420, width=499, height=62)

    def save_image(self):
        if self.captured_image is None:
            messagebox.showerror("Error", "No image to save.")
            return

        # Create the directory if it doesn't exist
        directory = os.path.join(os.path.expanduser("~"), "Documents", "captured_images")
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(directory, f"cropped_image_{timestamp}.jpg")

        # Ensure valid crop values
        h, w, _ = self.captured_image.shape
        crop_bottom = min(self.crop_bottom, h - self.crop_top - 1)
        crop_right = min(self.crop_right, w - self.crop_left - 1)

        # Crop the image before saving
        cropped_image = self.captured_image[self.crop_top:h - crop_bottom, self.crop_left:w - crop_right]

        # Convert to correct format for saving
        cv2.imwrite(filename, cropped_image)

        messagebox.showinfo("Success", f"Image saved as {filename}")

        # Apply the final crop values

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