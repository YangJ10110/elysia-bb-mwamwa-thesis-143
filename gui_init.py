import tkinter as tk
from tkinter import filedialog, font
from PIL import Image, ImageTk
import cv2
import json

class CameraApp: #Configurations for the camera app - start
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)  # Remove title bar, para hindi drag-able yung window
        self.root.geometry("468x800")  #para sa size
        self.root.configure(bg="#171d29")

        self.current_frame = None
        self.captured_image = None
        self.filename = None
# Configurations for the camera app until here

        self.create_initial_page()

    def create_initial_page(self): #function, pwede magconsume pa ng ibang functions
        self.clear_frame()
        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 20, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=444, y=9, width=17, height=17)  # Scaled down from x=494, y=9, width=17, height=17

        self.camera_label = tk.Label(self.root, width=468, height=600, bg="black", bd=0)  # Scaled down from width=520, height=693
        self.camera_label.place(x=0, y=35)  # Scaled down from x=2.17, y=35

        self.capture_button = tk.Button(
            self.root, text="Capture", command=self.capture_image, bg="#4CAF50", fg="white", font=("Google Sans", 16, "bold")
        )
        self.capture_button.place(
            x=13,
            y=650,
            width=442,
            height=50)  # Scaled down from x=13, y=741, width=494, height=61

        self.upload_button = tk.Button(
            self.root, 
            text="Upload", 
            command=self.upload_image, 
            bg="#2196F3", 
            fg="white", 
            font=("Google Sans", 16, "bold")
        )
        self.upload_button.place(
            x=13, 
            y=710, 
            width=442, 
            height=50)  # Scaled down from x=13, y=815, width=494, height=61

        self.cap = cv2.VideoCapture(0)
        self.update_camera_feed() #eto yung camera, function siya

    def update_camera_feed(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read() #ret is a boolean, frame is the image
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #converts the color from BGR to RGB
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)  # Rotate to portrait mode
                frame = cv2.resize(frame, (468, 600))  # Scale mo yung image
                self.current_frame = ImageTk.PhotoImage(Image.fromarray(frame))
                self.camera_label.config(image=self.current_frame)
                self.root.after(10, self.update_camera_feed)

    def capture_image(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.captured_image = frame
                self.cap.release()
                self.show_preview_page()

    def upload_image(self):
        self.filename = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if self.filename:
            self.captured_image = cv2.imread(self.filename)
            self.show_preview_page()

    def show_preview_page(self):
        self.clear_frame()
        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 20, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=444, y=9, width=17, height=17)  # Scaled down from x=494, y=9, width=17, height=17
        image = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2RGB)
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        image = cv2.resize(image, (468, 600))  # Scaled down from (520, 693)
        image = ImageTk.PhotoImage(Image.fromarray(image))

        self.image_label = tk.Label(self.root, image=image)
        self.image_label.image = image
        self.image_label.pack()
        self.image_label.place(x=0, y=35)  # Scaled down from x=0, y=35

        self.back_button = tk.Button(self.root, text="Back", command=self.create_initial_page, font=("Google Sans", 10))  # Scaled down from font size 10

        self.proceed_button = tk.Button(self.root, text="Proceed", command=self.show_result_page, font=("Google Sans", 10))  # Scaled down from font size 10

        self.back_button = tk.Button(
            self.root, 
            text="Upload", 
            command=self.upload_image, 
            bg="#2196F3", 
            fg="white", 
            font=("Google Sans", 16, "bold")
        )
        self.proceed_button.place(
            x=13, 
            y=710, 
            width=442, 
            height=50)  # Scaled down from x=13, y=815, width=494, height=61

    def show_result_page(self):
        self.clear_frame()

        resized_image = cv2.resize(self.captured_image, (234, 300))  # Scaled down from (260, 347)
        resized_image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)))

        self.result_image_label = tk.Label(self.root, image=resized_image)
        self.result_image_label.image = resized_image
        self.result_image_label.pack(pady=10)  # Scaled down from pady=13

        mock_data = {
            "Pneumonia":"Yes",
            "Classification": "Viral",
            "Confidence Level": "87%",
            "NOTE": "It is recommended to consult a doctor for further validation of diagnosis"
        }

        for key, value in mock_data.items():
            label = tk.Label(self.root, text=f"{key}: {value}", font=("Google Sans", 10))  # Scaled down from font size 12
            label.pack()

        self.back_button = tk.Button(self.root, text="Back", command=self.create_initial_page, font=("Google Sans", 10))  # Scaled down from font size 10
        self.back_button.pack(pady=10)  # Scaled down from pady=13

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
# comment