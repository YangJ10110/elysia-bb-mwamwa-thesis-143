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


"""
def create_patient_info_page(self):
        self.clear_frame()
        
        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 20, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=1250, y=10, width=30, height=30)
        
        tk.Label(self.root, text="Enter Patient's Name:", font=("Google Sans", 16), bg="#171d29", fg="white").place(x=400, y=200)
        
        self.name_entry = tk.Entry(self.root, font=("Google Sans", 16), width=30)
        self.name_entry.place(x=400, y=250)
        
        self.keyboard_frame = tk.Frame(self.root, bg="#171d29")
        self.keyboard_frame.place(x=400, y=300)
        self.create_keyboard()
        
        self.done_button = tk.Button(self.root, text="Done", command=self.create_initial_page, bg="#4CAF50", fg="white", font=("Google Sans", 16, "bold"))
        self.done_button.place(x=700, y=550, width=240, height=60)
    
    def create_keyboard(self):
        keys = [
            "qwertyuiop",
            "asdfghjkl",
            "zxcvbnm"
        ]
        
        for row_index, row in enumerate(keys):
            for col_index, key in enumerate(row):
                button = tk.Button(self.keyboard_frame, text=key, font=("Google Sans", 16), width=4, height=2,
                                   command=lambda k=key: self.insert_character(k))
                button.grid(row=row_index, column=col_index)
                
        space_button = tk.Button(self.keyboard_frame, text="Space", font=("Google Sans", 16), width=20, height=2,
                                 command=lambda: self.insert_character(" "))
        space_button.grid(row=3, column=0, columnspan=10)
    
    def insert_character(self, char):
        self.name_entry.insert(tk.END, char)
"""
# CAMERA: 1920X1080
class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(False)  # Remove title bar
        self.root.geometry("1280x800")  # Set to landscape
        self.root.configure(bg="#171d29")
        
        self.current_frame = None
        self.captured_image = None
        self.filename = None
        self.patient_name = ""

        self.create_patient_info_page()

    
    def create_patient_info_page(self):
        self.clear_frame()

        self.active_entry = None  # Track active entry

        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 20, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=1250, y=10, width=30, height=30)

        tk.Label(self.root, text="Hello!", font=("Google Sans", 40), bg="#171d29", fg="white").place(x=530, y=50)

        tk.Label(self.root, text="Patient's Name:", font=("Google Sans", 16), bg="#171d29", fg="white").place(x=200, y=150)
        tk.Label(self.root, text="Age:", font=("Google Sans", 16), bg="#171d29", fg="white").place(x=660, y=150)
        tk.Label(self.root, text="Sex:", font=("Google Sans", 16), bg="#171d29", fg="white").place(x=870, y=150)

        self.name_entry = tk.Entry(self.root, font=("Google Sans", 16), width=25, relief="flat", highlightthickness=1, highlightbackground="gray", bd=10)
        self.name_entry.place(x=200, y=180)
        self.name_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.name_entry))

        self.age_entry = tk.Entry(self.root, font=("Google Sans", 16), width=10, relief="flat", highlightthickness=1, highlightbackground="gray", bd=10)
        self.age_entry.place(x=655, y=180)
        self.age_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.age_entry))

        self.sex_entry = tk.Entry(self.root, font=("Google Sans", 16), width=10, relief="flat", highlightthickness=1, highlightbackground="gray", bd=10)
        self.sex_entry.place(x=865, y=180)
        self.sex_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.sex_entry))

        tk.Label(self.root, text="Address:", font=("Google Sans", 16), bg="#171d29", fg="white").place(x=200, y=250)
        tk.Label(self.root, text="Contact Number:", font=("Google Sans", 16), bg="#171d29", fg="white").place(x=660, y=250)

        self.address_entry = tk.Entry(self.root, font=("Google Sans", 16), width=25, relief="flat", highlightthickness=1, highlightbackground="gray", bd=10)
        self.address_entry.place(x=200, y=280)
        self.address_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.address_entry))

        self.contact_entry = tk.Entry(self.root, font=("Google Sans", 16), width=25, relief="flat", highlightthickness=1, highlightbackground="gray", bd=10)
        self.contact_entry.place(x=655, y=280)
        self.contact_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.contact_entry))

        self.keyboard_frame = tk.Frame(self.root, bg="#171d29")
        self.keyboard_frame.place(x=200, y=350)
        self.create_keyboard()

        self.done_button = tk.Button(self.root, text="Done", command=self.create_initial_page, bg="#4CAF50", fg="white", font=("Google Sans", 16, "bold"))
        self.done_button.place(x=780, y=510, width=250, height=70)
    
    def create_keyboard(self):
        keys = [
            "1234567890",
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNÑM"
        ]
        
        for row_index, row in enumerate(keys):
            for col_index, key in enumerate(row):
                button = tk.Button(self.keyboard_frame, text=key, font=("Google Sans", 16), width=4, height=2,
                                   command=lambda k=key: self.insert_character(k))
                button.grid(row=row_index, column=col_index)
                
        back_button = tk.Button(self.keyboard_frame, text="Backspace", font=("Google Sans", 16),  width=20, height=2, command=lambda: self.name_entry.delete(len(self.name_entry.get())-1, tk.END))
        back_button.grid(row=0, column=10, columnspan=10)

        space_button = tk.Button(self.keyboard_frame, text="Space", font=("Google Sans", 16), width=20, height=2, command=lambda: self.insert_character(" "))
        space_button.grid(row=1, column=10, columnspan=10)
    
    def set_active_entry(self, entry):
        """ Set the active entry field. """
        self.active_entry = entry

    def insert_character(self, char):
        """ Insert character into the active entry field. """
        if self.active_entry:
            self.active_entry.insert(tk.END, char)
    
    def create_initial_page(self):
        self.patient_name = self.name_entry.get()
        self.clear_frame()
        
        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 20, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=1250, y=10, width=30, height=30)
        
        self.camera_label = tk.Label(self.root, width=960, height=720, bg="black", bd=0)
        self.camera_label.place(x=20, y=40)
        
        self.capture_button = tk.Button(
            self.root, text="Capture", command=self.capture_image, bg="#4CAF50", fg="white", font=("Google Sans", 16, "bold")
        )
        self.capture_button.place(x=1000, y=300, width=240, height=60)
        
        self.upload_button = tk.Button(
            self.root, text="Upload", command=self.upload_image, bg="#2196F3", fg="white", font=("Google Sans", 16, "bold")
        )
        self.upload_button.place(x=1000, y=400, width=240, height=60)
        
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
                frame = cv2.resize(frame, (960, 720))
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
        self.exit_button.place(x=1250, y=10, width=30, height=30)
        
        image = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (960, 720))
        image = ImageTk.PhotoImage(Image.fromarray(image))
        
        self.image_label = tk.Label(self.root, image=image)
        self.image_label.image = image
        self.image_label.place(x=20, y=40)
        
        self.proceed_button = tk.Button(
            self.root, text="Proceed", command=self.show_result_page, bg="#4CAF50", fg="white", font=("Google Sans", 16, "bold")
        )
        self.proceed_button.place(x=1000, y=300, width=240, height=60)
        
    
    def show_result_page(self):
        self.clear_frame()
        
        resized_image = cv2.resize(self.captured_image, (480, 360))
        resized_image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)))
        
        self.result_image_label = tk.Label(self.root, image=resized_image)
        self.result_image_label.image = resized_image
        self.result_image_label.place(x=400, y=200)
        
        mock_data = {
            "Patient Name": self.patient_name,
            "Pneumonia": "Yes",
            "Classification": "Viral",
            "Confidence Level": "87%",
            "NOTE": "Consult a doctor for further validation."
        }
        
        y_position = 600
        for key, value in mock_data.items():
            label = tk.Label(self.root, text=f"{key}: {value}", font=("Google Sans", 14), bg="#171d29", fg="white")
            label.place(x=500, y=y_position)
            y_position += 40
        
        # self.print_as_pdf_button = tk.Button(self.root, text="Back", command=self.create_initial_page, bg="##1a80e6", fg="white", font=("Google Sans", 16, "bold"))
        
        self.print_as_pdf_button = tk.Button(self.root, text="Print as Pdf",command=self.generate_pdf , bg="#1a80e6", fg="white", font=("Google Sans", 16, "bold"))

        self.print_as_pdf_button.place(x=1000, y=200, width=240, height=60)

        self.send_to_doctor_button = tk.Button(self.root, text="Send to Doctor",command=self.send_to_doctor_page, bg="#234679", fg="white", font=("Google Sans", 16, "bold"))

        self.send_to_doctor_button.place(x=1000, y=300, width=240, height=60)

        # #1a80e6
        # #234679
    def generate_pdf(self):
        timestamp = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        directory = "C:/Documents/Generated_PDF/"
        
        # Ensure the directory exists before saving the file
        os.makedirs(directory, exist_ok=True)

        pdf_filename = os.path.join(directory, f"{self.patient_name}_pneumonia_report_{timestamp}.pdf")
        
        c = canvas.Canvas(pdf_filename)
        c.setFont("Helvetica", 20)
        c.drawString(100, 750, "Pneumonia Detection Report")
        c.setFont("Helvetica", 14)

        mock_data = {
            "Patient Name": self.patient_name,
            "Pneumonia": "Yes",
            "Classification": "Viral",
            "Confidence Level": "87%",
            "NOTE": "Consult a doctor for further validation."
        }

        y_position = 700
        for key, value in mock_data.items():
            c.drawString(100, y_position, f"{key}: {value}")
            y_position -= 30

        c.save()
        messagebox.showinfo("PDF Generated", "Pneumonia report saved as PDF.")

        return pdf_filename
    
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
        
        tk.Button(self.root, text="Send to Doctor", command=self.send_email, bg="#1a80e6", fg="white", font=("Google Sans", 16, "bold"), width=20).pack(pady=10)
        tk.Button(self.root, text="Back to Camera", command=self.show_result_page, bg="#234679", fg="white", font=("Google Sans", 16, "bold"), width=20).pack(pady=10)
    
    
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
