import tkinter as tk
from tkinter import ttk
import time
import threading

class HeaderFrame(ttk.Frame):
    """Header component with title and clock"""
    def __init__(self, parent, title="", subtitle=""):
        super().__init__(parent, padding="20 20 20 10")
        
        # Title and subtitle
        self.title_label = ttk.Label(self, text=title, font=("Helvetica", 24, "bold"))
        self.title_label.pack(side=tk.LEFT)
        
        if subtitle:
            self.subtitle_label = ttk.Label(self, text=subtitle, font=("Helvetica", 12))
            self.subtitle_label.pack(side=tk.LEFT, padx=(10, 0), pady=(8, 0))
        
        # Time frame
        self.time_frame = ttk.Frame(self)
        self.time_frame.pack(side=tk.RIGHT)
        
        # Current date
        self.date_label = ttk.Label(self.time_frame, font=("Helvetica", 12))
        self.date_label.pack(side=tk.LEFT)
        
        # Clock
        self.clock_label = ttk.Label(self.time_frame, font=("Helvetica", 12))
        self.clock_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def update_clock(self, time_string):
        """Update the clock display"""
        self.clock_label.config(text=time_string)

class FooterFrame(ttk.Frame):
    """Footer component with buttons and copyright"""
    def __init__(self, parent):
        super().__init__(parent, padding="20 10 20 20")
        
        # Create a horizontal separator
        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill='x', pady=(0, 10))
        
        # Button frame
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(side=tk.LEFT)
        
        # Change password button
        self.change_pass_btn = ttk.Button(
            self.button_frame, 
            text="Change Password", 
            command=self.on_change_password
        )
        self.change_pass_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Contact button
        self.contact_btn = ttk.Button(
            self.button_frame, 
            text="Contact Support", 
            command=self.on_contact
        )
        self.contact_btn.pack(side=tk.LEFT)
        
        # Copyright
        current_year = time.strftime("%Y")
        copyright_text = f"© {current_year} Smart Attendance System"
        self.copyright_label = ttk.Label(self, text=copyright_text, font=("Helvetica", 9))
        self.copyright_label.pack(side=tk.RIGHT)
    
    def on_change_password(self):
        """Run when change password button is clicked"""
        pass  # Will be connected to the actual function
    
    def on_contact(self):
        """Run when contact button is clicked"""
        pass  # Will be connected to the actual function

class RoundedButton(ttk.Button):
    """Button with rounded corners and optional icon"""
    def __init__(self, parent, text="", command=None, icon=None, **kwargs):
        super().__init__(parent, text=text, command=command, **kwargs)
        
        # Store the icon if provided
        self.icon = icon
        if icon:
            self.config(compound=tk.LEFT, image=icon, padding=(10, 5))
        else:
            self.config(padding=(10, 5))

class InfoCard(ttk.Frame):
    """Information card with title and content"""
    def __init__(self, parent, title="", content=""):
        super().__init__(parent, padding="15")
        
        # Add a border
        self.config(borderwidth=1, relief="solid")
        
        # Title
        if title:
            self.title_label = ttk.Label(self, text=title, font=("Helvetica", 14, "bold"))
            self.title_label.pack(anchor="w", pady=(0, 10))
        
        # Content
        if content:
            self.content_label = ttk.Label(self, text=content, wraplength=300, justify="left")
            self.content_label.pack(anchor="w")

class LoadingDialog:
    """Dialog with loading animation"""
    def __init__(self, parent, title="Loading", message="Please wait..."):
        self.parent = parent
        self.title = title
        self.message = message
        self.dialog = None
        self.progress = None
        self.message_label = None
        self.cancel_button = None
        self.is_running = False
    
    def start(self):
        """Show the loading dialog"""
        # Create dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("300x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create a main frame with padding
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Message
        self.message_label = ttk.Label(main_frame, text=self.message, font=("Helvetica", 11))
        self.message_label.pack(pady=(0, 15))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate", length=250)
        self.progress.pack(pady=(0, 15))
        self.progress.start(10)
        
        # Cancel button
        self.cancel_button = ttk.Button(main_frame, text="Cancel", command=self.stop)
        self.cancel_button.pack()
        
        # Mark as running
        self.is_running = True
        
        # Make dialog modal
        self.dialog.protocol("WM_DELETE_WINDOW", self.stop)
        
        return self.dialog
    
    def stop(self):
        """Close the loading dialog"""
        if self.dialog and self.is_running:
            self.progress.stop()
            self.dialog.grab_release()
            self.dialog.destroy()
            self.is_running = False

class AnimatedProgressbar(ttk.Progressbar):
    """Progressbar with smooth animation"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.current_value = 0
        self.target_value = 0
        self.animation_thread = None
        self.animation_running = False
    
    def config(self, **kwargs):
        """Override config to intercept value changes"""
        if 'value' in kwargs:
            self._animate_to(kwargs.pop('value'))
        return super().config(**kwargs)
    
    def configure(self, **kwargs):
        """Alias for config"""
        return self.config(**kwargs)
    
    def _animate_to(self, target_value):
        """Animate progress to target value"""
        if target_value == self.current_value:
            return
        
        self.target_value = float(target_value)
        
        # Stop any running animation
        self.animation_running = False
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_thread.join(0.1)
        
        # Start a new animation
        self.animation_running = True
        self.animation_thread = threading.Thread(
            target=self._animation_loop,
            args=(self.current_value, self.target_value)
        )
        self.animation_thread.daemon = True
        self.animation_thread.start()
    
    def _animation_loop(self, start_value, end_value):
        """Animation loop to update progressbar"""
        duration = 0.5  # seconds
        steps = 20
        step_time = duration / steps
        step_size = (end_value - start_value) / steps
        
        for i in range(steps + 1):
            if not self.animation_running:
                break
            
            # Calculate the current progress value
            t = i / steps
            # Easing function (ease out cubic)
            t = 1 - (1 - t) ** 3
            value = start_value + (end_value - start_value) * t
            
            self.current_value = value
            super().config(value=value)
            
            time.sleep(step_time)
        
        # Ensure we reach the final value
        if self.animation_running:
            self.current_value = end_value
            super().config(value=end_value)
