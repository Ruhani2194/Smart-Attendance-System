import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mess
import tkinter.simpledialog as tsd
import cv2
import os
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
import pyttsx3
from ttkthemes import ThemedTk
import threading
import webbrowser

# Import custom modules
from styles import setup_styles
from components import HeaderFrame, FooterFrame, LoadingDialog, InfoCard
from utils import center_window, create_tooltip

class AttendanceSystem:
    def __init__(self, root):
        """Initialize the attendance system"""
        self.root = root
        
        # Setup the UI style and components
        self.setup_variables()
        self.style = setup_styles(root)
        self.setup_ui()
        
        # Initialize the required directories
        self.assure_path_exists("Attendance/")
        self.assure_path_exists("StudentDetails/")
        self.assure_path_exists("TrainingImage/")
        self.assure_path_exists("TrainingImageLabel/")
        
        # Check for haarcascade file
        self.check_haarcascadefile()
        
        # Update the registration count
        self.update_total_registrations()
    
    def setup_variables(self):
        """Initialize variables for the application"""
        # Current date and time
        ts = time.time()
        self.date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
        self.day, self.month, self.year = self.date.split("-")
        
        # Month names dictionary
        self.month_names = {
            '01': 'January',
            '02': 'February',
            '03': 'March',
            '04': 'April',
            '05': 'May',
            '06': 'June',
            '07': 'July',
            '08': 'August',
            '09': 'September',
            '10': 'October',
            '11': 'November',
            '12': 'December'
        }
        
        # Password related variables
        self.master = None  # For password dialog
        self.old = None
        self.new = None
        self.nnew = None
    
    def setup_ui(self):
        """Set up the user interface"""
        # Setup header with title and clock
        self.header = HeaderFrame(self.root, title="Smart Attendance System")
        self.header.pack(fill=tk.X)
        
        # Set date in header
        formatted_date = f"{self.day}-{self.month_names[self.month]}-{self.year}  |  "
        self.header.date_label.config(text=formatted_date)
        
        # Setup clock update
        self.update_clock()
        
        # Create tabbed interface
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create tabs
        self.registration_tab = ttk.Frame(self.tab_control, padding=20)
        self.attendance_tab = ttk.Frame(self.tab_control, padding=20)
        self.view_tab = ttk.Frame(self.tab_control, padding=20)
        
        # Add tabs to notebook
        self.tab_control.add(self.registration_tab, text='Registration')
        self.tab_control.add(self.attendance_tab, text='Take Attendance')
        self.tab_control.add(self.view_tab, text='View Attendance')
        
        # Setup individual tabs
        self.setup_registration_tab()
        self.setup_attendance_tab()
        self.setup_view_tab()
        
        # Create footer with buttons
        self.footer = FooterFrame(self.root)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Connect footer buttons to methods
        self.footer.change_pass_btn.config(command=self.change_pass)
        self.footer.contact_btn.config(command=self.contact)
        
        # Create a menu bar
        self.menu_bar = tk.Menu(self.root)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Change Password", command=self.change_pass)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.destroy)
        self.menu_bar.add_cascade(label="Settings", menu=self.file_menu)
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="Contact Support", command=self.contact)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        
        # Set the menu bar
        self.root.config(menu=self.menu_bar)
    
    def setup_registration_tab(self):
        """Set up the registration tab interface"""
        # Registration form frame
        self.form_frame = ttk.LabelFrame(self.registration_tab, text="Registration Form", padding=20)
        self.form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Student ID field
        id_label = ttk.Label(self.form_frame, text="Student ID:", font=("Helvetica", 12))
        id_label.grid(row=0, column=0, sticky="w", pady=10)
        
        self.id_entry = ttk.Entry(self.form_frame, width=30, font=("Helvetica", 12))
        self.id_entry.grid(row=0, column=1, sticky="w", padx=10, pady=10)
        
        clear_id_btn = ttk.Button(self.form_frame, text="Clear", command=self.clear_id_entry)
        clear_id_btn.grid(row=0, column=2, sticky="w", padx=10, pady=10)
        
        # Student Name field
        name_label = ttk.Label(self.form_frame, text="Student Name:", font=("Helvetica", 12))
        name_label.grid(row=1, column=0, sticky="w", pady=10)
        
        self.name_entry = ttk.Entry(self.form_frame, width=30, font=("Helvetica", 12))
        self.name_entry.grid(row=1, column=1, sticky="w", padx=10, pady=10)
        
        clear_name_btn = ttk.Button(self.form_frame, text="Clear", command=self.clear_name_entry)
        clear_name_btn.grid(row=1, column=2, sticky="w", padx=10, pady=10)
        
        # Registration instructions
        instructions_label = ttk.Label(
            self.form_frame, 
            text="Instructions:\n1. Enter Student ID and Name\n2. Click 'Take Images' to capture facial data\n3. Click 'Save Profile' to save the profile", 
            font=("Helvetica", 11),
            justify=tk.LEFT
        )
        instructions_label.grid(row=2, column=0, columnspan=3, sticky="w", pady=20)
        
        # Status label
        self.status_label = ttk.Label(self.form_frame, text="Status: Ready", font=("Helvetica", 12, "italic"))
        self.status_label.grid(row=3, column=0, columnspan=3, sticky="w", pady=10)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(self.form_frame, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky="ew", pady=10)
        
        # Action buttons frame
        button_frame = ttk.Frame(self.form_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Take Images button
        self.take_img_btn = ttk.Button(button_frame, text="Take Images", command=self.TakeImages, style="Accent.TButton")
        self.take_img_btn.pack(side=tk.LEFT, padx=10)
        
        # Save Profile button
        self.save_profile_btn = ttk.Button(button_frame, text="Save Profile", command=self.psw)
        self.save_profile_btn.pack(side=tk.LEFT, padx=10)
        
        # Total registrations label
        self.total_label = ttk.Label(self.form_frame, text="Total Registrations: 0", font=("Helvetica", 12, "bold"))
        self.total_label.grid(row=6, column=0, columnspan=3, sticky="w", pady=10)
        
        # Add tooltips
        create_tooltip(self.take_img_btn, "Start the webcam to capture student images for face recognition")
        create_tooltip(self.save_profile_btn, "Save the captured images and create a profile for the student")
    
    def setup_attendance_tab(self):
        """Set up the attendance tracking tab interface"""
        # Attendance frame
        self.attendance_frame = ttk.LabelFrame(self.attendance_tab, text="Facial Recognition Attendance", padding=20)
        self.attendance_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        attendance_instructions = ttk.Label(
            self.attendance_frame, 
            text="Instructions:\n1. Click 'Start Recognition' to begin\n2. The system will recognize registered students\n3. Attendance will be marked automatically", 
            font=("Helvetica", 11),
            justify=tk.LEFT
        )
        attendance_instructions.pack(anchor="w", pady=10)
        
        # Start button
        self.start_attendance_btn = ttk.Button(
            self.attendance_frame, 
            text="Start Recognition", 
            command=self.TrackImages,
            style="Accent.TButton"
        )
        self.start_attendance_btn.pack(anchor="w", pady=10)
        
        # Status label
        self.track_status_label = ttk.Label(self.attendance_frame, text="Status: Ready", font=("Helvetica", 12, "italic"))
        self.track_status_label.pack(anchor="w", pady=10)
        
        # Progress bar
        self.track_progress = ttk.Progressbar(self.attendance_frame, orient="horizontal", length=500, mode="determinate")
        self.track_progress.pack(fill="x", pady=10)
        
        # Attendance records frame
        attendance_records_frame = ttk.LabelFrame(self.attendance_frame, text="Today's Attendance")
        attendance_records_frame.pack(fill="both", expand=True, pady=10)
        
        # Attendance tree view
        self.attendance_tree = ttk.Treeview(attendance_records_frame, columns=("name", "date", "time"), show="headings", height=10)
        self.attendance_tree.heading("name", text="Name")
        self.attendance_tree.heading("date", text="Date")
        self.attendance_tree.heading("time", text="Time")
        self.attendance_tree.column("name", width=150)
        self.attendance_tree.column("date", width=150)
        self.attendance_tree.column("time", width=150)
        self.attendance_tree.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Scrollbar for attendance tree
        attendance_scroll = ttk.Scrollbar(attendance_records_frame, orient="vertical", command=self.attendance_tree.yview)
        attendance_scroll.pack(side=tk.RIGHT, fill="y")
        self.attendance_tree.configure(yscrollcommand=attendance_scroll.set)
        
        # Add tooltip
        create_tooltip(self.start_attendance_btn, "Start the webcam for face recognition to mark attendance")
    
    def setup_view_tab(self):
        """Set up the view attendance records tab"""
        # View attendance frame
        self.view_frame = ttk.LabelFrame(self.view_tab, text="View Attendance Records", padding=20)
        self.view_frame.pack(fill=tk.BOTH, expand=True)
        
        # Date selection frame
        date_frame = ttk.Frame(self.view_frame)
        date_frame.pack(anchor="w", fill="x", pady=10)
        
        # Date label
        date_select_label = ttk.Label(date_frame, text="Select Date (DD-MM-YYYY):", font=("Helvetica", 12))
        date_select_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Date entry
        self.date_entry = ttk.Entry(date_frame, width=15, font=("Helvetica", 12))
        self.date_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.date_entry.insert(0, datetime.datetime.now().strftime('%d-%m-%Y'))
        
        # View button
        view_btn = ttk.Button(date_frame, text="View", command=self.view_attendance)
        view_btn.pack(side=tk.LEFT)
        
        # Export button
        export_btn = ttk.Button(date_frame, text="Export CSV", command=self.export_attendance_data, style="Success.TButton")
        export_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Status label
        self.view_status_label = ttk.Label(self.view_frame, text="Status: Ready", font=("Helvetica", 12, "italic"))
        self.view_status_label.pack(anchor="w", pady=10)
        
        # View attendance tree frame
        view_tree_frame = ttk.Frame(self.view_frame)
        view_tree_frame.pack(fill="both", expand=True, pady=10)
        
        # View attendance tree
        self.view_attendance_tree = ttk.Treeview(view_tree_frame, columns=("name", "date", "time"), show="headings", height=15)
        self.view_attendance_tree.heading("name", text="Name")
        self.view_attendance_tree.heading("date", text="Date")
        self.view_attendance_tree.heading("time", text="Time")
        self.view_attendance_tree.column("name", width=150)
        self.view_attendance_tree.column("date", width=150)
        self.view_attendance_tree.column("time", width=150)
        self.view_attendance_tree.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Scrollbar for view attendance tree
        view_scroll = ttk.Scrollbar(view_tree_frame, orient="vertical", command=self.view_attendance_tree.yview)
        view_scroll.pack(side=tk.RIGHT, fill="y")
        self.view_attendance_tree.configure(yscrollcommand=view_scroll.set)
        
        # Add tooltips
        create_tooltip(view_btn, "View attendance records for the selected date")
        create_tooltip(export_btn, "Export attendance records to a CSV file")
    
    def update_clock(self):
        """Update the clock in the header"""
        time_string = time.strftime('%H:%M:%S')
        self.header.update_clock(time_string)
        # Call again after 200ms
        self.root.after(200, self.update_clock)
    
    def announce_attendance_marked(self):
        """Announce attendance marked using text-to-speech"""
        try:
            engine = pyttsx3.init()
            engine.say("Attendance marked successfully!")
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
    
    def assure_path_exists(self, path):
        """Create directory if it doesn't exist"""
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)
    
    def check_haarcascadefile(self):
        """Check if haarcascade file exists"""
        haarcascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        exists = os.path.isfile(haarcascade_path)
        if exists:
            return True
        else:
            mess.showinfo(title='File Missing', message='Please reinstall the application or contact support.')
            return False
    
    def save_pass(self):
        """Save password for the application"""
        self.assure_path_exists("TrainingImageLabel/")
        exists1 = os.path.isfile("TrainingImageLabel/psd.txt")
        if exists1:
            tf = open("TrainingImageLabel/psd.txt", "r")
            key = tf.read()
        else:
            self.master.destroy()
            new_pas = tsd.askstring('Old Password not found', 'Please enter a new password below', show='*')
            if new_pas == None:
                mess.showinfo(title='No Password Entered', message='Password not set! Please try again')
            else:
                tf = open("TrainingImageLabel/psd.txt", "w")
                tf.write(new_pas)
                mess.showinfo(title='Password Registered', message='New password was registered successfully!')
                return
        op = (self.old.get())
        newp = (self.new.get())
        nnewp = (self.nnew.get())
        if (op == key):
            if(newp == nnewp):
                txf = open("TrainingImageLabel/psd.txt", "w")
                txf.write(newp)
            else:
                mess.showinfo(title='Error', message='Confirm new password again!')
                return
        else:
            mess.showinfo(title='Wrong Password', message='Please enter correct old password.')
            return
        mess.showinfo(title='Password Changed', message='Password changed successfully!')
        self.master.destroy()
    
    def change_pass(self):
        """Change password dialog"""
        self.master = tk.Toplevel(self.root)
        self.master.title("Change Password")
        self.master.geometry("500x220")
        self.master.configure(background="#f0f0f0")
        self.master.resizable(False, False)
        
        # Center the window
        center_window(self.master)
        
        # Create a main frame
        main_frame = ttk.Frame(self.master, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = ttk.Label(main_frame, text="Change Password", font=("Helvetica", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Form fields
        ttk.Label(main_frame, text="Current Password:", font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.old = ttk.Entry(main_frame, width=30, show='*')
        self.old.grid(row=1, column=1, sticky="we", pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="New Password:", font=("Helvetica", 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.new = ttk.Entry(main_frame, width=30, show='*')
        self.new.grid(row=2, column=1, sticky="we", pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Confirm New Password:", font=("Helvetica", 10)).grid(row=3, column=0, sticky="w", pady=5)
        self.nnew = ttk.Entry(main_frame, width=30, show='*')
        self.nnew.grid(row=3, column=1, sticky="we", pady=5, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(15, 0), sticky="e")
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.master.destroy, style="Accent.TButton")
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        save_btn = ttk.Button(button_frame, text="Save", command=self.save_pass)
        save_btn.pack(side=tk.RIGHT)
    
    def psw(self):
        """Password verification for training"""
        self.assure_path_exists("TrainingImageLabel/")
        exists1 = os.path.isfile("TrainingImageLabel/psd.txt")
        if exists1:
            tf = open("TrainingImageLabel/psd.txt", "r")
            key = tf.read()
        else:
            new_pas = tsd.askstring('Old Password not found', 'Please enter a new password below', show='*')
            if new_pas is None:
                mess.showinfo(title='No Password Entered', message='Password not set! Please try again')
            else:
                tf = open("TrainingImageLabel/psd.txt", "w")
                tf.write(new_pas)
                mess.showinfo(title='Password Registered', message='New password was registered successfully!')
                return
        password = tsd.askstring('Password', 'Enter Password', show='*')
        if password == key:
            self.TrainImages()
        elif password is None:
            pass
        else:
            mess.showinfo(title='Wrong Password', message='You have entered the wrong password')
    
    def clear_id_entry(self):
        """Clear ID field"""
        self.id_entry.delete(0, 'end')
        self.status_label.configure(text="Status: Ready")
    
    def clear_name_entry(self):
        """Clear name field"""
        self.name_entry.delete(0, 'end')
        self.status_label.configure(text="Status: Ready")
    
    def update_image_preview(self, img):
        """Update the camera preview with new image"""
        # Convert BGR to RGB for display
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        
        return img_tk
    
    def TakeImages(self):
        """Capture images for training"""
        if not self.check_haarcascadefile():
            return
        
        # Get student ID and name
        student_id = self.id_entry.get()
        name = self.name_entry.get()
        
        # Validate inputs
        if not student_id or not name:
            self.status_label.configure(text="Status: ID and Name are required")
            return
        
        if not name.replace(" ", "").isalpha():
            self.status_label.configure(text="Status: Name should contain only alphabets")
            return
        
        # Initialize student database if not exists
        columns = ['SERIAL NO.', '', 'ID', '', 'NAME']
        self.assure_path_exists("StudentDetails/")
        self.assure_path_exists("TrainingImage/")
        
        # Get serial number
        serial = self._get_next_serial()
        
        # Start image capture in a separate thread
        self.status_label.configure(text="Status: Starting camera...")
        self.progress_bar["value"] = 10
        self.root.update_idletasks()
        
        # Start capturing images
        threading.Thread(target=self.capture_images, args=(student_id, name, serial)).start()
    
    def capture_images(self, Id, name, serial):
        """Capture images in a separate thread"""
        # Initialize camera
        cam = cv2.VideoCapture(0)
        harcascadePath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(harcascadePath)
        
        # Create a preview window for the camera feed
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Taking Images - Press 'q' to stop")
        preview_window.geometry("640x520")
        preview_window.configure(background="#f0f0f0")
        
        # Center the window
        center_window(preview_window)
        
        # Create a label for the camera feed
        lbl_cam = ttk.Label(preview_window)
        lbl_cam.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create a progress label
        lbl_progress = ttk.Label(preview_window, text="Capturing: 0/100", font=("Helvetica", 12))
        lbl_progress.pack(pady=(0, 20))
        
        # Create a progressbar
        capture_progress = ttk.Progressbar(preview_window, orient="horizontal", length=600, mode="determinate")
        capture_progress.pack(padx=20, pady=(0, 20))
        
        # Variables to control capturing
        sampleNum = 0
        stop_capture = False
        img_display = None
        
        # Function to update the camera feed
        def update_cam():
            nonlocal sampleNum, img_display
            
            if not stop_capture:
                ret, img = cam.read()
                if ret:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = detector.detectMultiScale(gray, 1.3, 5)
                    
                    for (x, y, w, h) in faces:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                        
                        # Save the captured image
                        if sampleNum < 100:  # Limit to 100 samples per person
                            sampleNum += 1
                            filename = f"TrainingImage/{name}.{serial}.{Id}.{sampleNum}.jpg"
                            cv2.imwrite(filename, gray[y:y+h, x:x+w])
                            
                            # Update progress label and bar
                            lbl_progress.config(text=f"Capturing: {sampleNum}/100")
                            capture_progress["value"] = sampleNum
                            
                            # Update main window progress
                            self.progress_bar["value"] = 10 + (sampleNum * 0.8)
                            self.root.update_idletasks()
                    
                    # Convert image for display
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    img_display = ImageTk.PhotoImage(image=img_pil)
                    
                    # Update the camera feed
                    lbl_cam.configure(image=img_display)
                    lbl_cam.image = img_display  # Keep reference to avoid garbage collection
                    
                    if sampleNum >= 100:  # Finish when enough samples are collected
                        stop_capture = True
                        self.status_label.configure(text="Status: Images captured successfully")
                        self.progress_bar["value"] = 90
                        self.root.update_idletasks()
                        
                        # Save the student details to CSV
                        row = [serial, '', Id, '', name]
                        with open('StudentDetails/StudentDetails.csv', 'a+') as csvFile:
                            writer = csv.writer(csvFile)
                            writer.writerow(row)
                        csvFile.close()
                        
                        # Finish and close the preview window after a delay
                        preview_window.after(1000, preview_window.destroy)
                        return
                
                # Continue updating
                preview_window.after(20, update_cam)
        
        # Function to handle window close
        def on_close():
            nonlocal stop_capture
            stop_capture = True
            cam.release()
            preview_window.destroy()
            self.status_label.configure(text="Status: Image capture canceled")
            self.progress_bar["value"] = 0
            self.root.update_idletasks()
        
        preview_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Start updating the camera feed
        update_cam()
        
        # Wait for the preview window to close
        self.root.wait_window(preview_window)
        
        # Release resources
        cam.release()
        cv2.destroyAllWindows()
        
        # Check if capture was completed
        if sampleNum >= 100:
            self.status_label.configure(text=f"Status: Images taken for ID: {Id}")
            self.progress_bar["value"] = 100
            self.update_total_registrations()
            self.root.update_idletasks()
    
    def _get_next_serial(self):
        """Get the next serial number for registration"""
        serial = 0
        exists = os.path.isfile("StudentDetails/StudentDetails.csv")
        if exists:
            with open("StudentDetails/StudentDetails.csv", 'r') as csvFile1:
                reader1 = csv.reader(csvFile1)
                for l in reader1:
                    serial = serial + 1
            serial = (serial // 2)
            csvFile1.close()
        else:
            with open("StudentDetails/StudentDetails.csv", 'a+') as csvFile1:
                writer = csv.writer(csvFile1)
                writer.writerow(['SERIAL NO.', '', 'ID', '', 'NAME'])
                serial = 1
            csvFile1.close()
        
        return serial
    
    def TrainImages(self):
        """Train the model with captured images"""
        if not self.check_haarcascadefile():
            return
        
        # Update status
        self.status_label.configure(text="Status: Training started...")
        self.progress_bar["value"] = 20
        self.root.update_idletasks()
        
        # Create a loading dialog
        loading_dialog = LoadingDialog(self.root, title="Training Model", message="Please wait while the AI model is being trained...")
        loading_dialog.start()
        
        # Train model in a separate thread
        threading.Thread(target=self._train_model_thread, args=(loading_dialog,)).start()
    
    def _train_model_thread(self, loading_dialog):
        """Train model in a separate thread"""
        try:
            # Initialize face recognizer
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            harcascadePath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            detector = cv2.CascadeClassifier(harcascadePath)
            
            # Get training data
            faces, ID = self.getImagesAndLabels("TrainingImage")
            
            # Check if we have training data
            if len(faces) == 0:
                loading_dialog.stop()
                self.status_label.configure(text="Status: No training images found")
                self.progress_bar["value"] = 0
                return
            
            # Update status
            self.progress_bar["value"] = 70
            self.status_label.configure(text="Status: Training AI model...")
            self.root.update_idletasks()
            
            # Train the model
            recognizer.train(faces, np.array(ID))
            recognizer.save("TrainingImageLabel/Trainner.yml")
            
            # Stop loading dialog
            loading_dialog.stop()
            
            # Update status
            self.progress_bar["value"] = 100
            self.status_label.configure(text="Status: Profile saved successfully")
            
            # Show completion message
            mess.showinfo(title='Training Complete', message='Your AI model has been trained successfully!')
            
        except Exception as e:
            # Handle errors
            loading_dialog.stop()
            self.status_label.configure(text=f"Status: Error during training: {str(e)}")
            self.progress_bar["value"] = 0
            mess.showerror(title='Training Error', message=f'An error occurred during training: {str(e)}')
    
    def getImagesAndLabels(self, path):
        """Get images and their labels for training"""
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        faces = []
        Ids = []
        
        for imagePath in imagePaths:
            try:
                # Open and convert to grayscale
                pilImage = Image.open(imagePath).convert('L')
                # Convert to numpy array
                imageNp = np.array(pilImage, 'uint8')
                # Get ID from filename
                ID = int(os.path.split(imagePath)[-1].split(".")[1])
                # Add face sample
                faces.append(imageNp)
                Ids.append(ID)
            except Exception as e:
                print(f"Error processing {imagePath}: {e}")
                continue
        
        return faces, Ids
    
    def TrackImages(self):
        """Track and mark attendance with face recognition"""
        if not self.check_haarcascadefile():
            return
        
        # Clear the attendance tree view
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        # Update status
        self.track_status_label.configure(text="Status: Starting facial recognition...")
        self.track_progress["value"] = 10
        self.root.update_idletasks()
        
        # Check for trained model
        if not os.path.isfile("TrainingImageLabel/Trainner.yml"):
            mess.showinfo(title='Data Missing', message='Please train the model first!')
            self.track_status_label.configure(text="Status: Training data missing")
            self.track_progress["value"] = 0
            return
        
        # Check for student details
        if not os.path.isfile("StudentDetails/StudentDetails.csv"):
            mess.showinfo(title='Details Missing', message='Student details are missing!')
            self.track_status_label.configure(text="Status: Student details missing")
            self.track_progress["value"] = 0
            return
        
        # Initialize recognizer
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("TrainingImageLabel/Trainner.yml")
        
        # Start tracking in a separate thread
        threading.Thread(target=self._track_images_thread, args=(recognizer,)).start()
    
    def _track_images_thread(self, recognizer):
        """Track images in a separate thread"""
        # Initialize face detector
        harcascadePath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        faceCascade = cv2.CascadeClassifier(harcascadePath)
        
        # Load student details
        df = pd.read_csv("StudentDetails/StudentDetails.csv")
        
        # Initialize camera
        cam = cv2.VideoCapture(0)
        
        # Initialize attendance data
        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
        attendance_file = f"Attendance/Attendance_{date}.csv"
        
        # Initialize column names
        col_names = ['Id', '', 'Name', '', 'Date', '', 'Time']
        attendance = []  # Track attendance to write to file
        recognized_faces = set()  # Track recognized faces
        
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Face Recognition - Press 'q' to stop")
        preview_window.geometry("640x520")
        preview_window.configure(background="#f0f0f0")
        center_window(preview_window)
        
        # Create a label for the camera feed
        lbl_cam = ttk.Label(preview_window)
        lbl_cam.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create a status label
        lbl_status = ttk.Label(preview_window, text="Searching for faces...", font=("Helvetica", 12))
        lbl_status.pack(pady=(0, 20))
        
        # Variables to control recognition
        stop_recognition = False
        img_display = None
        
        # Function to update recognition
        def update_recognition():
            nonlocal stop_recognition, img_display
            
            if not stop_recognition:
                ret, img = cam.read()
                if ret:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = faceCascade.detectMultiScale(gray, 1.2, 5)
                    
                    # Update progress
                    self.track_progress["value"] = 40 + min(len(recognized_faces) * 5, 50)
                    
                    # Process detected faces
                    for (x, y, w, h) in faces:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (225, 0, 0), 2)
                        
                        # Try to recognize the face
                        try:
                            serial, conf = recognizer.predict(gray[y:y + h, x:x + w])
                            
                            # If confidence is less than 50, we have a match
                            if conf < 50:
                                ts = time.time()
                                date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                                time_str = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                
                                # Get name and ID from student details
                                student_name = df.loc[df['SERIAL NO.'] == serial]['NAME'].values[0]
                                student_id = df.loc[df['SERIAL NO.'] == serial]['ID'].values[0]
                                
                                # Mark attendance if not already marked
                                if student_id not in recognized_faces:
                                    recognized_faces.add(student_id)
                                    
                                    # Create attendance record
                                    attendance_record = [str(student_id), '', student_name, '', date, '', time_str]
                                    attendance.append(attendance_record)
                                    
                                    # Update UI
                                    self._update_attendance_ui(student_id, student_name, date, time_str)
                                    lbl_status.config(text=f"Recognized: {student_name} (ID: {student_id})")
                                    
                                    # Announce attendance
                                    threading.Thread(target=self.announce_attendance_marked).start()
                                
                                # Display name on the image
                                display_text = f"{student_name}"
                            else:
                                display_text = "Unknown"
                        except Exception as e:
                            print(f"Recognition error: {e}")
                            display_text = "Unknown"
                        
                        # Put text on the image
                        cv2.putText(img, display_text, (x, y + h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    
                    # Convert image for display
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    img_display = ImageTk.PhotoImage(image=img_pil)
                    
                    # Update the preview
                    lbl_cam.configure(image=img_display)
                    lbl_cam.image = img_display  # Keep reference
                
                # Continue updating
                preview_window.after(20, update_recognition)
        
        # Function to handle window close
        def on_close():
            nonlocal stop_recognition
            stop_recognition = True
            cam.release()
            
            # Update attendance file if any entries were recorded
            if attendance:
                self._update_attendance_file(attendance, col_names, date)
            
            preview_window.destroy()
            self.track_status_label.configure(text=f"Status: Attendance marked for {len(recognized_faces)} students")
            self.track_progress["value"] = 100
        
        # Set close handler
        preview_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Create a stop button
        stop_btn = ttk.Button(preview_window, text="Stop Recognition", command=on_close)
        stop_btn.pack(pady=(0, 20))
        
        # Start recognition
        update_recognition()
    
    def _update_attendance_file(self, attendance, col_names, date):
        """Update the attendance file with new attendance"""
        attendance_file = f"Attendance/Attendance_{date}.csv"
        
        # Check if file exists
        if os.path.isfile(attendance_file):
            # Read existing data to avoid duplicates
            with open(attendance_file, 'r') as file:
                reader = csv.reader(file)
                existing_data = list(reader)
                header = existing_data[0] if existing_data else col_names
                existing_ids = set(row[0] for row in existing_data[1:]) if len(existing_data) > 1 else set()
            
            # Filter out duplicate entries
            new_attendance = [record for record in attendance if record[0] not in existing_ids]
            
            # Write all data back
            with open(attendance_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(header)  # Write header
                # Write existing data except header
                for row in existing_data[1:]:
                    writer.writerow(row)
                # Write new data
                for row in new_attendance:
                    writer.writerow(row)
        else:
            # Create new file
            with open(attendance_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(col_names)  # Write header
                for row in attendance:
                    writer.writerow(row)
    
    def _update_attendance_ui(self, student_id, student_name, date, time_str):
        """Update the attendance UI with new entry"""
        # Add to treeview
        self.attendance_tree.insert('', 0, text=student_id, values=(student_name, date, time_str))
        # Update UI
        self.root.update_idletasks()
    
    def update_total_registrations(self):
        """Update the total registrations count"""
        res = 0
        exists = os.path.isfile("StudentDetails/StudentDetails.csv")
        if exists:
            with open("StudentDetails/StudentDetails.csv", 'r') as csvFile1:
                reader1 = csv.reader(csvFile1)
                for l in reader1:
                    res = res + 1
            res = (res // 2) - 1
            csvFile1.close()
        else:
            res = 0
        
        # Update label
        self.total_label.configure(text=f'Total Registrations: {str(res)}')
    
    def view_attendance(self):
        """Load attendance data for selected date"""
        # Clear the view attendance tree
        for item in self.view_attendance_tree.get_children():
            self.view_attendance_tree.delete(item)
        
        # Get selected date
        selected_date = self.date_entry.get()
        if not selected_date:
            selected_date = datetime.datetime.now().strftime('%d-%m-%Y')
        
        # Check if attendance file exists for the date
        attendance_file = f"Attendance/Attendance_{selected_date}.csv"
        if not os.path.isfile(attendance_file):
            self.view_status_label.configure(text=f"Status: No attendance records for {selected_date}")
            return
        
        # Load and display the attendance data
        with open(attendance_file, 'r') as csvFile:
            reader = csv.reader(csvFile)
            next(reader)  # Skip header
            i = 0
            for lines in reader:
                i += 1
                if i % 2 != 0 and len(lines) >= 7:  # Skip alternate rows (empty rows)
                    self.view_attendance_tree.insert('', 'end', text=lines[0], values=(lines[2], lines[4], lines[6]))
        csvFile.close()
        
        self.view_status_label.configure(text=f"Status: Showing attendance for {selected_date}")
    
    def export_attendance_data(self):
        """Export attendance data to CSV"""
        # Get selected date
        selected_date = self.date_entry.get()
        if not selected_date:
            selected_date = datetime.datetime.now().strftime('%d-%m-%Y')
        
        # Source file path
        attendance_file = f"Attendance/Attendance_{selected_date}.csv"
        if not os.path.isfile(attendance_file):
            self.view_status_label.configure(text=f"Status: No attendance records for {selected_date}")
            mess.showinfo(title="Export Failed", message=f"No attendance records found for {selected_date}")
            return
        
        # Create exports directory if it doesn't exist
        self.assure_path_exists("Exports/")
        
        # Export file path
        export_file = f"Exports/Attendance_{selected_date}_export.csv"
        
        try:
            # Read the source file
            with open(attendance_file, 'r') as source_file:
                reader = csv.reader(source_file)
                data = list(reader)
            
            # Create a cleaned-up export file
            with open(export_file, 'w', newline='') as export_csv:
                writer = csv.writer(export_csv)
                # Write header
                writer.writerow(['ID', 'Name', 'Date', 'Time'])
                
                # Write data rows, removing empty columns
                for i, row in enumerate(data):
                    if i > 0 and len(row) >= 7:  # Skip header, only process valid rows
                        writer.writerow([row[0], row[2], row[4], row[6]])
            
            self.view_status_label.configure(text=f"Status: Attendance exported to {export_file}")
            mess.showinfo(title="Export Success", message=f"Attendance data exported to {export_file}")
            
        except Exception as e:
            self.view_status_label.configure(text=f"Status: Export failed - {str(e)}")
            mess.showerror(title="Export Error", message=f"Failed to export attendance data: {str(e)}")
    
    def contact(self):
        """Open email to contact support"""
        webbrowser.open('mailto:support@smartattendance.com')
