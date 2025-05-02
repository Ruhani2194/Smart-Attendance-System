import tkinter as tk
from ttkthemes import ThemedTk
from attendance_system import AttendanceSystem
from utils import center_window

def main():
    # Create root window with theme
    root = ThemedTk(theme="arc")
    root.title("Smart Attendance System")
    root.geometry("1080x680")
    root.configure(background='#f0f0f0')
    root.resizable(True, True)

    # Center the window
    center_window(root)
    
    # Initialize the attendance system
    app = AttendanceSystem(root)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
