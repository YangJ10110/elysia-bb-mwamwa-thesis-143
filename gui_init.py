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

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)  # Remove title bar
        self.root.geometry("1920x1080")  # Set to landscape
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
        self.show_result_page()




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
        
        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 30, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=1450, y=40, width=30, height=31)
        
        self.camera_label = tk.Label(self.root, width=720, height=860, bg="black", bd=0)
        self.camera_label.place(x=20, y=1)
        
        self.capture_button = tk.Button(
            self.root, text="Capture", command=self.capture_image, bg="#1a80e6", fg="white", font=("Google Sans", 20, "bold")
        )
        self.capture_button.place(x=815, y=350, width=640, height=80)
        
        self.upload_button = tk.Button(
            self.root, text="Upload", command=self.upload_image, bg="#234679", fg="white", font=("Google Sans", 20, "bold")
        )
        self.upload_button.place(x=815, y=450, width=640, height=80)
        
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            print("Error: Unable to access external webcam.")
            self.cap = cv2.VideoCapture(1)
        self.update_camera_feed()


    def create_patient_info_page(self):
        self.clear_frame()

        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 30, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=1450, y=40, width=30, height=31)

        tk.Label(self.root, text="Hello!", font=("Google Sans", 50), bg="#171d29", fg="white").place(x=645, y=50)

        tk.Label(self.root, text="Patient's Name:", font=("Google Sans", 26), bg="#171d29", fg="white").place(x=220, y=150)
        tk.Label(self.root, text="Age:", font=("Google Sans", 26), bg="#171d29", fg="white").place(x=895, y=150)
        tk.Label(self.root, text="Sex:", font=("Google Sans", 26), bg="#171d29", fg="white").place(x=1085, y=150)

        self.name_entry = tk.Entry(self.root, font=("Google Sans", 26), width=20, relief="flat", highlightthickness=1, highlightbackground="gray", bd=10)
        self.name_entry.place(x=220, y=195)
        self.name_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.name_entry))


        self.age_entry = tk.Entry(self.root, font=("Google Sans", 26), width=3, relief="flat", highlightthickness=1, highlightbackground="gray", bd=10)
        self.age_entry.place(x=895, y=195)
        self.age_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.age_entry))
        self.age = self.age_entry.get() 
        print(self.age)

        self.sex_entry = tk.Entry(self.root, font=("Google Sans", 26), width=3, relief="flat", highlightthickness=1, highlightbackground="gray", bd=10)
        self.sex_entry.place(x=1085, y=195)
        self.sex_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.sex_entry))
        self.sex = self.sex_entry.get()
        print(self.sex)

        tk.Label(self.root, text="Address:", font=("Google Sans", 26), bg="#171d29", fg="white").place(x=220, y=270)
        tk.Label(self.root, text="Contact Number:", font=("Google Sans", 26), bg="#171d29", fg="white").place(x=885, y=270)

        self.address_entry = tk.Entry(self.root, font=("Google Sans", 26), width=20, relief="flat", highlightthickness=1, highlightbackground="gray", bd=10)
        self.address_entry.place(x=220, y=315)
        self.address_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.address_entry))
        self.address = self.address_entry.get()
        print(self.address)

        self.contact_entry = tk.Entry(self.root, font=("Google Sans", 26), width=16, relief="flat", highlightthickness=1, highlightbackground="gray", bd=10)
        self.contact_entry.place(x=895, y=315)
        self.contact_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.contact_entry))
        self.contact = self.contact_entry.get()
        print(self.contact)

        self.keyboard_frame = tk.Frame(self.root, bg="#171d29")
        self.keyboard_frame.place(x=220, y=410)
        self.create_keyboard()


        self.done_button = tk.Button(self.root, text="Done", command=self.create_initial_page, bg="#4CAF50", fg="white", font=("Google Sans", 20, "bold"))
        # # Add logo image
        # logo_image = Image.open("CheXray_Colored.png")
        # logo_image = logo_image.resize((200, 200), Image.LANCZOS)
        # self.logo_photo = ImageTk.PhotoImage(logo_image)
        # self.logo_label = tk.Label(self.root, image=self.logo_photo, bg="#171d29")
        # self.logo_label.place(x=10, y=10)

        self.done_button.place(x=1040, y=700, width=250, height=105)
    
    def create_keyboard(self):
        keys = [
            "1234567890",
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNÑM"
        ]
        
        for row_index, row in enumerate(keys):
            for col_index, key in enumerate(row):
                button = tk.Button(self.keyboard_frame, text=key, font=("Google Sans", 16), width=6, height=3,
                                   command=lambda k=key: self.insert_character(k))
                button.grid(row=row_index, column=col_index)
                
        backspace_button = tk.Button(self.keyboard_frame, text="Backspace", font=("Google Sans", 16), width=20, height=3, command=self.backspace_character)
        backspace_button.grid(row=0, column=10, columnspan=10)

        space_button = tk.Button(self.keyboard_frame, text="Space", font=("Google Sans", 16), width=20, height=3, command=lambda: self.insert_character(" "))
        space_button.grid(row=1, column=10, columnspan=10)
    
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
    


    def update_camera_feed(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (720, 960))
                self.current_frame = ImageTk.PhotoImage(Image.fromarray(frame))
                if self.camera_label.winfo_exists():
                    self.camera_label.config(image=self.current_frame)
                self.root.after(10, self.update_camera_feed)

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

    def show_preview_page(self):
        self.clear_frame()
        
        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 30, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=1450, y=40, width=30, height=31)
        
        image = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (720, 860))
        image = ImageTk.PhotoImage(Image.fromarray(image))
        
        # self.camera_label = tk.Label(self.root, width=720, height=860, bg="black", bd=0)
        # self.camera_label.place(x=20, y=1)
        
        self.image_label = tk.Label(self.root, image=image, width=720, bg="black", height=840,bd=0)
        self.image_label.image = image
        self.image_label.place(x=20, y=10)
        
        ##1a80e6
        ##234679

        self.proceed_button = tk.Button(
            self.root, text="Process", command=self.show_result_page, bg="#1a80e6", fg="white", font=("Google Sans", 20, "bold")
        )
        #font=("Google Sans", 20, "bold"
        self.proceed_button.place(x=815, y=350, width=640, height=80)
        #        self.capture_button.place(x=815, y=350, width=640, height=80)

        
        self.retake_button = tk.Button(
            self.root, text="Retake Photo", command=self.create_initial_page, bg="#234679", fg="white", font=("Google Sans", 20, "bold")
        )
        self.retake_button.place(x=815, y=450, width=640, height=80)

        #self.upload_button.place(x=815, y=450, width=640, height=80)
    
    def show_result_page(self):
        self.clear_frame()
        self.patient_name = "Jerome"
        self.sex = "M"
        self.address = "Cebu City"
        self.contact = "09123456789" 
        self.age = "25"
        self.normal_confidence_level = 87
        self.viral_confidence_level = 13
        self.bacterial_confidence_level = 0
        self.priority_level = "Low"
        self.others_confidence_level = 0
        
        result_title_label = tk.Label(self.root, text="Pneumonia Detection and Classification", font=("Google Sans", 25), bg="#171d29", fg="white")
        result_title_label.place(x=700, y=30)

        self.back_button = tk.Button (self.root, text="Back", command=self.create_initial_page, bg="#1a80e6", fg="white", font=("Google Sans", 16, "bold"))
        self.back_button.place(x=10, y=10, width=100, height=31)
        #back button to camera
        

        # self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 30, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        # self.exit_button.place(x=1450, y=40, width=30, height=31)

        if self.captured_image is not None:
            resized_image = cv2.resize(self.captured_image, (700, 800))
            resized_image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)))
        else:
            resized_image = ImageTk.PhotoImage(Image.new('RGB', (300, 400), 'black'))

        
        self.result_image_label = tk.Label(self.root, image=resized_image, width=460, bg="black", height=740)
        self.result_image_label.image = resized_image
        self.result_image_label.place(x=100, y=60)

        #        self.image_label = tk.Label(self.root, image=image, width=720, bg="black", height=840,bd=0)
        #        self.image_label.image = image
        #        self.image_label.place(x=20, y=10)

        patient_data = {
            "Patient Name": self.patient_name,
            "Age": self.age,
            "Sex": self.sex,
            "Address": self.address,
            "Contact Number": self.contact,
        }
        
        y_position = 120
        for key, value in patient_data.items():
            label = tk.Label(self.root, text=f"{key}: {value}", font=("Google Sans", 20), bg="#171d29", fg="white")
            label.place(x=600, y=y_position)
            y_position += 40
        
        #line with color #234679

        self.line = tk.Label(self.root, text="_____________________________________________________________________________________________", font=("Google Sans", 14), bg="#171d29", fg="#234679")
        self.second_line = tk.Label(self.root, text="_____________________________________________________________________________________________", font=("Google Sans", 14), bg="#171d29", fg="#234679")
        self.third_line = tk.Label(self.root, text="_____________________________________________________________________________________________", font=("Google Sans", 14), bg="#171d29", fg="#234679")
        self.fourth_line = tk.Label(self.root, text="_____________________________________________________________________________________________", font=("Google Sans", 14), bg="#171d29", fg="#234679")

        self.line.place(x=600, y=320)
        self.second_line.place(x=600, y=390)
        self.third_line.place(x=600, y=460)
        self.fourth_line.place(x=600, y=530)

        self.normal_confidence_label = tk.Label(self.root, text=f"Normal:", font=("Google Sans", 20), bg="#171d29", fg="white")
        self.normal_confidence_label.place(x=600, y=360)
        self.normal_confidence_level_label = tk.Label(self.root, text=f"Confidence Level: {self.normal_confidence_level}%", font=("Google Sans", 20,"bold"), bg="#171d29", fg="white")
        self.normal_confidence_level_label.place(x=850, y=360)


        self.viral_confidence_label = tk.Label(self.root, text=f"Viral:", font=("Google Sans", 20), bg="#171d29", fg="white")
        self.viral_confidence_label.place(x=600, y=430)
        self.viral_confidence_level_label = tk.Label(self.root, text=f"Confidence Level: {self.viral_confidence_level}%", font=("Google Sans", 20,"bold"), bg="#171d29", fg="white")
        self.viral_confidence_level_label.place(x=850, y=430)


        self.bacterial_confidence_label = tk.Label(self.root, text=f"Bacterial:", font=("Google Sans", 20), bg="#171d29", fg="white")
        self.bacterial_confidence_label.place(x=600, y=500)
        self.bacterial_confidence_level_label = tk.Label(self.root, text=f"Confidence Level: {self.bacterial_confidence_level}%", font=("Google Sans", 20, "bold"), bg="#171d29", fg="white")
        self.bacterial_confidence_level_label.place(x=850, y=500)

        self.others_confidence_label = tk.Label(self.root, text=f"Others:", font=("Google Sans", 20), bg="#171d29", fg="white")
        self.others_confidence_label.place(x=600, y=570)
        self.others_confidence_level_label = tk.Label(self.root, text=f"Confidence Level: {self.others_confidence_level}%", font=("Google Sans", 20, "bold"), bg="#171d29", fg="white")
        self.others_confidence_level_label.place(x=850, y=570)


        self.priority_label = tk.Label(self.root, text=f"Priority Level:", font=("Google Sans", 23), bg="#1a345b", fg="white",bd=30)
        self.priority_label.place(x=1200, y=650)

        self.priority_level_label = tk.Label(self.root, text=f"{self.priority_level}", font=("Google Sans", 23, "bold"), bg="#1a345b", fg="white", bd=0, padx=10, pady=31, anchor="w")
        self.priority_level_label.place(x=1420, y=650, width=120)
        
        # self.print_as_pdf_button = tk.Button(self.root, text="Back", command=self.create_initial_page, bg="##1a80e6", fg="white", font=("Google Sans", 16, "bold"))
        
        self.print_as_pdf_button = tk.Button(self.root, text="Print as Pdf",command=self.generate_pdf , bg="#1a80e6", fg="white", font=("Google Sans", 12, "bold"))

        self.print_as_pdf_button.place(x=1250, y=120, width=200, height=50)
        #         self.exit_button.place(x=1450, y=40, width=30, height=31)


        self.send_to_doctor_button = tk.Button(self.root, text="Send to Doctor",command=self.send_to_doctor_page, bg="#234679", fg="white", font=("Google Sans", 12, "bold"))

        self.send_to_doctor_button.place(x=1250, y=190, width=200, height=50)

        # #1a80e6
        # #234679


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
        
        tk.Button(self.root, text="Send to Doctor", command=self.send_email, bg="#1a80e6", fg="white", font=("Google Sans", 16, "bold"), width=20).pack(pady=10)
        tk.Button(self.root, text="Back to Patient Info", command=self.create_patient_info_page, bg="#234679", fg="white", font=("Google Sans", 16, "bold"), width=20).pack(pady=10)
    
    
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
