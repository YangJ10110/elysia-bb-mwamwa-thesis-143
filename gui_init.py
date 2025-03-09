import tkinter as tk
from tkinter import filedialog, font
from PIL import Image, ImageTk
import cv2
import json
#tkinter drag window


class CameraApp:
    def __init__(self, root):
        self.root = root
<<<<<<< Updated upstream
        self.root.overrideredirect(True)  # Remove title bar
        self.root.geometry("600x1024")
=======
        self.root.overrideredirect(False)  # Remove title bar
        self.root.geometry("1920x1080")  # Set to landscape
>>>>>>> Stashed changes
        self.root.configure(bg="#171d29")
        #center-top the window

        self.current_frame = None
        self.captured_image = None
        self.filename = None
<<<<<<< Updated upstream
=======
        self.patient_name = ""
        self.cap = None
>>>>>>> Stashed changes

        self.create_initial_page()



<<<<<<< Updated upstream

    def create_initial_page(self):
        self.clear_frame()
        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 22, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=570, y=10, width=20, height=20)
        # Camera Feed
        # make the input camera fliiped (so it can be portrait without compressing the feed)

        self.camera_label = tk.Label(self.root, width=600, height=800, bg="black", bd=0)
        self.camera_label.place(x=2.5, y=40)

        # Capture and Upload Buttons
        self.capture_button = tk.Button(
            self.root, text="Capture", command=self.capture_image, bg="#4CAF50", fg="white", font=("Google Sans", 18, "bold")
        )
        self.capture_button.place(
            x=15,
            y=855,
            width=570,
            height=70)

        self.upload_button = tk.Button(
            self.root, 
            text="Upload", 
            command=self.upload_image, 
            bg="#2196F3", 
            fg="white", 
            font=("Google Sans", 18, "bold")
        )
        self.upload_button.place(
            x=15, 
            y=940, 
            width=570, 
            height=70)

        self.cap = cv2.VideoCapture(0)
=======
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

        self.sex_entry = tk.Entry(self.root, font=("Google Sans", 26), width=3, relief="flat", highlightthickness=1, highlightbackground="gray", bd=10)
        self.sex_entry.place(x=1085, y=195)
        self.sex_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.sex_entry))

        tk.Label(self.root, text="Address:", font=("Google Sans", 26), bg="#171d29", fg="white").place(x=220, y=270)
        tk.Label(self.root, text="Contact Number:", font=("Google Sans", 26), bg="#171d29", fg="white").place(x=885, y=270)

        self.address_entry = tk.Entry(self.root, font=("Google Sans", 26), width=20, relief="flat", highlightthickness=1, highlightbackground="gray", bd=10)
        self.address_entry.place(x=220, y=315)
        self.address_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.address_entry))

        self.contact_entry = tk.Entry(self.root, font=("Google Sans", 26), width=16, relief="flat", highlightthickness=1, highlightbackground="gray", bd=10)
        self.contact_entry.place(x=895, y=315)
        self.contact_entry.bind("<FocusIn>", lambda event: self.set_active_entry(self.contact_entry))

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
    
    def create_initial_page(self):
        if self.name_entry.winfo_exists():
            self.patient_name = self.name_entry.get()
        self.clear_frame()
        
        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 30, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=1450, y=40, width=30, height=31)
        
        self.camera_label = tk.Label(self.root, width=720, height=860, bg="black", bd=0)
        self.camera_label.place(x=20, y=1)
        
        self.capture_button = tk.Button(
            self.root, text="Capture", command=self.capture_image, bg="#1a80e6", fg="white", font=("Google Sans", 20, "bold")
        )
        self.capture_button.place(x=815, y=350, width=640, height=80)
        ##1a80e6
        ##234679
        
        self.upload_button = tk.Button(
            self.root, text="Upload", command=self.upload_image, bg="#234679", fg="white", font=("Google Sans", 20, "bold")
        )
        self.upload_button.place(x=815, y=450, width=640, height=80)
        
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            print("Error: Unable to access external webcam.")
            self.cap = cv2.VideoCapture(1)
>>>>>>> Stashed changes
        self.update_camera_feed()

    def update_camera_feed(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
<<<<<<< Updated upstream
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)  # Rotate to portrait mode
                # Resize the frame to fit the label
                frame = cv2.resize(frame, (580, 800))
=======
                frame = cv2.resize(frame, (720, 960))
>>>>>>> Stashed changes
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

    def show_preview_page(self):
        self.clear_frame()
<<<<<<< Updated upstream
        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 22, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=570, y=10, width=20, height=20)
        image = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2RGB)
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        image = cv2.resize(image, (600, 800))
        image = ImageTk.PhotoImage(Image.fromarray(image))

        self.image_label = tk.Label(self.root, image=image)
        self.image_label.image = image
        self.image_label.pack()
        self.image_label.place(x=0, y=40)

        self.back_button = tk.Button(self.root, text="Back", command=self.create_initial_page, font=("Google Sans", 12))


        self.proceed_button = tk.Button(self.root, text="Proceed", command=self.show_result_page, font=("Google Sans", 12))


        
        self.proceed_button.place(
            x=15, 
            y=940, 
            width=570, 
            height=70)

        self.back_button.place(
            x=15, 
            y=855, 
            width=570, 
            height=70)

=======
        
        self.exit_button = tk.Button(self.root, text="✕", command=self.close_camera, fg="red", font=("Comfortaa", 30, "bold"), bd=0, bg="#171d29", activebackground="#171d29", activeforeground="white")
        self.exit_button.place(x=1450, y=40, width=30, height=31)
        
        image = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (720, 860))
        image = ImageTk.PhotoImage(Image.fromarray(image))
        
        # self.camera_label = tk.Label(self.root, width=720, height=860, bg="black", bd=0)
        # self.camera_label.place(x=20, y=1)
        
        self.image_label = tk.Label(self.root, image=image, width=720, bg="black", height=860,bd=0)
        self.image_label.image = image
        self.image_label.place(x=20, y=1)
        
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
    
>>>>>>> Stashed changes
    def show_result_page(self):
        self.clear_frame()

        resized_image = cv2.resize(self.captured_image, (300, 400))
        resized_image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)))

        self.result_image_label = tk.Label(self.root, image=resized_image)
        self.result_image_label.image = resized_image
<<<<<<< Updated upstream
        self.result_image_label.pack(pady=10)
=======
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
        c.setFont ("Helvetica", 14)
>>>>>>> Stashed changes

        mock_data = {
            "Pneumonia":"Yes",
            "Classification": "Viral",
            "Confidence Level": "87%",
            "NOTE": "It is recommended to consult a doctor for further validation of diagnosis"
        }

        for key, value in mock_data.items():
            label = tk.Label(self.root, text=f"{key}: {value}", font=("Google Sans", 14))
            label.pack()

        self.back_button = tk.Button(self.root, text="Back", command=self.create_initial_page, font=("Google Sans", 12))
        self.back_button.pack(pady=10)

<<<<<<< Updated upstream
=======
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
        tk.Button(self.root, text="Back to Patient Info", command=self.create_patient_info_page, bg="#234679", fg="white", font=("Google Sans", 16, "bold"), width=20).pack(pady=10)
    
    
>>>>>>> Stashed changes
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
