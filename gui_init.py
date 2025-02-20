import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1280x800")  # Set to landscape resolution
        self.root.configure(bg="#171d29")
        
        self.current_frame = None
        self.captured_image = None
        self.filename = None
        
        self.create_initial_page()

    def create_initial_page(self):
        self.clear_frame()
        
        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 20, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=1250, y=10, width=25, height=25)

        self.camera_label = tk.Label(self.root, width=640, height=400, bg="black", bd=0)
        self.camera_label.place(x=320, y=100)  # Centered horizontally

        self.capture_button = tk.Button(self.root, text="Capture", command=self.capture_image, bg="#4CAF50", fg="white", font=("Google Sans", 16, "bold"))
        self.capture_button.place(x=320, y=520, width=280, height=50)

        self.upload_button = tk.Button(self.root, text="Upload", command=self.upload_image, bg="#2196F3", fg="white", font=("Google Sans", 16, "bold"))
        self.upload_button.place(x=640, y=520, width=280, height=50)
        
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            print("Error: Unable to access external webcam.")
            self.cap = cv2.VideoCapture(0)
        self.update_camera_feed()

    def update_camera_feed(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (640, 400))  # Resize to half of 1280x800
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
        self.exit_button.place(x=1250, y=10, width=25, height=25)
        
        image = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (640, 400))  # Keep the preview at half screen size
        image = ImageTk.PhotoImage(Image.fromarray(image))

        self.image_label = tk.Label(self.root, image=image)
        self.image_label.image = image
        self.image_label.place(x=320, y=100)

        self.back_button = tk.Button(self.root, text="Back", command=self.create_initial_page, bg="#f44336", fg="white", font=("Google Sans", 16, "bold"))
        self.back_button.place(x=320, y=520, width=280, height=50)

        self.proceed_button = tk.Button(self.root, text="Proceed", command=self.show_result_page, bg="#4CAF50", fg="white", font=("Google Sans", 16, "bold"))
        self.proceed_button.place(x=640, y=520, width=280, height=50)

    def show_result_page(self):
        self.clear_frame()
        
        resized_image = cv2.resize(self.captured_image, (320, 200))  # Smaller result image
        resized_image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)))

        self.result_image_label = tk.Label(self.root, image=resized_image)
        self.result_image_label.image = resized_image
        self.result_image_label.pack(pady=20)
        
        mock_data = {
            "Pneumonia": "Yes",
            "Classification": "Viral",
            "Confidence Level": "87%",
            "NOTE": "It is recommended to consult a doctor for further validation."
        }

        for key, value in mock_data.items():
            label = tk.Label(self.root, text=f"{key}: {value}", font=("Google Sans", 12), fg="white", bg="#171d29")
            label.pack()

        self.back_button = tk.Button(self.root, text="Back", command=self.create_initial_page, bg="#f44336", fg="white", font=("Google Sans", 16, "bold"))
        self.back_button.pack(pady=20)

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
