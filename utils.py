import tkinter as tk
import time
from PIL import Image, ImageDraw

def center_window(window):
    """Center the window on the screen"""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def create_tooltip(widget, text):
    """Create a tooltip for a widget"""
    tooltip = None
    
    def enter(event):
        nonlocal tooltip
        x = widget.winfo_rootx() + widget.winfo_width() // 2
        y = widget.winfo_rooty() + widget.winfo_height() + 5
        
        # Create a toplevel window
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)  # Remove window decorations
        tooltip.wm_geometry(f"+{x}+{y}")  # Position the tooltip
        
        # Create a frame with border and background
        frame = tk.Frame(tooltip, background='#333333', borderwidth=1, relief="solid")
        frame.pack(fill="both", expand=True)
        
        # Create a label with the tooltip text
        label = tk.Label(frame, text=text, background='#333333', foreground="white",
                       font=("Helvetica", 9), wraplength=200, justify="left", padx=5, pady=3)
        label.pack()
    
    def leave(event):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
            tooltip = None
    
    # Bind events to the widget
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

def create_svg_icon(svg_path, width=24, height=24):
    """Create a PhotoImage from SVG file for icons"""
    try:
        from PIL import Image, ImageTk
        import io
        # Since cairosvg might not be available, we'll use a fallback
        # This function would normally use cairosvg to convert SVG to PNG
        # But for simplicity, we'll just use the fallback
        return create_fallback_icon(width, height)
    except (ImportError, Exception) as e:
        print(f"Error creating SVG icon: {e}")
        return create_fallback_icon(width, height)

def create_fallback_icon(width=24, height=24):
    """Create a fallback icon when SVG loading fails"""
    # Create a simple placeholder icon
    img = Image.new('RGBA', (width, height), (200, 200, 200, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple shape
    draw.rectangle((2, 2, width-3, height-3), outline="#666666")
    draw.line((2, 2, width-3, height-3), fill="#666666", width=1)
    draw.line((2, height-3, width-3, 2), fill="#666666", width=1)
    
    try:
        from PIL import ImageTk
        return ImageTk.PhotoImage(img)
    except ImportError:
        return None  # Return None if ImageTk is not available
