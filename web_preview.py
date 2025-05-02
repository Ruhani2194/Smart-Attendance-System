from flask import Flask, render_template, send_from_directory
import os
import base64
import io
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# Create directories if they don't exist
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Create preview images programmatically
def create_preview_images():
    # Dictionary to store the preview images
    previews = {
        'registration': create_registration_tab(),
        'attendance': create_attendance_tab(),
        'view': create_view_tab()
    }
    
    # Save images
    for name, img in previews.items():
        img.save(f'static/{name}_preview.png')

def create_base_window(width=800, height=600, title="Smart Attendance System"):
    # Create the base window image
    img = Image.new('RGB', (width, height), color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Add window frame
    draw.rectangle((0, 0, width, height), outline='#cccccc', width=1)
    
    # Add title bar
    draw.rectangle((0, 0, width, 40), fill='#1976d2')
    
    # Window title
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()
    
    draw.text((20, 10), title, fill='white', font=font)
    
    # Add close button
    draw.rectangle((width-40, 5, width-10, 35), fill='#e81123')
    draw.text((width-30, 10), 'X', fill='white', font=font)
    
    return img, draw

def add_header(img, draw, width):
    # Add header
    draw.rectangle((0, 40, width, 100), fill='#ffffff')
    
    # Add title
    try:
        title_font = ImageFont.truetype("arial.ttf", 24) 
    except IOError:
        title_font = ImageFont.load_default()
        
    draw.text((20, 55), "Smart Attendance System", fill='#1976d2', font=title_font)
    
    # Add date and time
    try:
        small_font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        small_font = ImageFont.load_default()
        
    draw.text((width-150, 60), "01-May-2025 | 12:30:45", fill='#555555', font=small_font)
    
    return img, draw

def add_tabs(img, draw, width, active_tab):
    # Draw tab bar
    draw.rectangle((20, 110, width-20, 150), fill='#ffffff')
    
    # Tab positions
    tabs = [
        ("Registration", 20, 180),
        ("Take Attendance", 181, 341),
        ("View Attendance", 342, 502)
    ]
    
    try:
        tab_font = ImageFont.truetype("arial.ttf", 14)
    except IOError:
        tab_font = ImageFont.load_default()
    
    # Draw tabs
    for i, (name, x1, x2) in enumerate(tabs):
        if i == active_tab:
            # Active tab
            draw.rectangle((x1, 110, x2, 150), fill='#1976d2')
            draw.text((x1 + 30, 122), name, fill='white', font=tab_font)
        else:
            # Inactive tab
            draw.rectangle((x1, 110, x2, 145), fill='#e0e0e0')
            draw.text((x1 + 30, 120), name, fill='#555555', font=tab_font)
    
    return img, draw

def create_registration_tab():
    width, height = 800, 600
    img, draw = create_base_window(width, height)
    img, draw = add_header(img, draw, width)
    img, draw = add_tabs(img, draw, width, 0)  # 0 = Registration tab active
    
    # Content area
    draw.rectangle((20, 160, width-20, height-60), fill='white', outline='#cccccc')
    
    # Form title
    try:
        title_font = ImageFont.truetype("arial.ttf", 16)
        normal_font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        title_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
    
    draw.text((40, 180), "Registration Form", fill='#333333', font=title_font)
    
    # Form fields
    field_y = 220
    draw.text((40, field_y), "Student ID:", fill='#333333', font=normal_font)
    draw.rectangle((150, field_y-5, 400, field_y+25), fill='white', outline='#cccccc')
    draw.rectangle((420, field_y-5, 480, field_y+25), fill='#f44336', outline='#cccccc')
    draw.text((435, field_y), "Clear", fill='white', font=normal_font)
    
    field_y += 50
    draw.text((40, field_y), "Student Name:", fill='#333333', font=normal_font)
    draw.rectangle((150, field_y-5, 400, field_y+25), fill='white', outline='#cccccc')
    draw.rectangle((420, field_y-5, 480, field_y+25), fill='#f44336', outline='#cccccc')
    draw.text((435, field_y), "Clear", fill='white', font=normal_font)
    
    # Instructions
    field_y += 60
    draw.text((40, field_y), "Instructions:", fill='#333333', font=normal_font)
    field_y += 25
    draw.text((40, field_y), "1. Enter Student ID and Name", fill='#555555', font=normal_font)
    field_y += 20
    draw.text((40, field_y), "2. Click 'Take Images' to capture facial data", fill='#555555', font=normal_font)
    field_y += 20
    draw.text((40, field_y), "3. Click 'Save Profile' to save the profile", fill='#555555', font=normal_font)
    
    # Status
    field_y += 40
    draw.text((40, field_y), "Status: Ready", fill='#1976d2', font=normal_font)
    
    # Progress bar
    field_y += 30
    draw.rectangle((40, field_y, 700, field_y+20), fill='#e0e0e0', outline='#cccccc')
    
    # Buttons
    field_y += 50
    draw.rectangle((40, field_y, 180, field_y+40), fill='#1976d2', outline='#0d47a1')
    draw.text((75, field_y+10), "Take Images", fill='white', font=normal_font)
    
    draw.rectangle((200, field_y, 340, field_y+40), fill='#4caf50', outline='#2e7d32')
    draw.text((235, field_y+10), "Save Profile", fill='white', font=normal_font)
    
    # Total registrations
    field_y += 60
    draw.text((40, field_y), "Total Registrations: 0", fill='#333333', font=title_font)
    
    return img

def create_attendance_tab():
    width, height = 800, 600
    img, draw = create_base_window(width, height)
    img, draw = add_header(img, draw, width)
    img, draw = add_tabs(img, draw, width, 1)  # 1 = Attendance tab active
    
    # Content area
    draw.rectangle((20, 160, width-20, height-60), fill='white', outline='#cccccc')
    
    # Form title
    try:
        title_font = ImageFont.truetype("arial.ttf", 16)
        normal_font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        title_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
    
    draw.text((40, 180), "Facial Recognition Attendance", fill='#333333', font=title_font)
    
    # Instructions
    field_y = 220
    draw.text((40, field_y), "Instructions:", fill='#333333', font=normal_font)
    field_y += 25
    draw.text((40, field_y), "1. Click 'Start Recognition' to begin", fill='#555555', font=normal_font)
    field_y += 20
    draw.text((40, field_y), "2. The system will recognize registered students", fill='#555555', font=normal_font)
    field_y += 20
    draw.text((40, field_y), "3. Attendance will be marked automatically", fill='#555555', font=normal_font)
    
    # Button
    field_y += 40
    draw.rectangle((40, field_y, 220, field_y+40), fill='#1976d2', outline='#0d47a1')
    draw.text((60, field_y+10), "Start Recognition", fill='white', font=normal_font)
    
    # Status
    field_y += 60
    draw.text((40, field_y), "Status: Ready", fill='#1976d2', font=normal_font)
    
    # Progress bar
    field_y += 30
    draw.rectangle((40, field_y, 700, field_y+20), fill='#e0e0e0', outline='#cccccc')
    
    # Attendance table
    field_y += 50
    draw.text((40, field_y), "Today's Attendance", fill='#333333', font=title_font)
    
    field_y += 30
    table_width = 680
    table_height = 150
    draw.rectangle((40, field_y, 40+table_width, field_y+table_height), fill='white', outline='#cccccc')
    
    # Table header
    draw.rectangle((40, field_y, 40+table_width, field_y+30), fill='#e0e0e0', outline='#cccccc')
    col_widths = [100, 290, 180, 110]
    col_x = 40
    for i, col in enumerate(["ID", "Name", "Date", "Time"]):
        draw.text((col_x + 10, field_y + 8), col, fill='#333333', font=normal_font)
        col_x += col_widths[i] if i < len(col_widths) else 100
        draw.line((col_x, field_y, col_x, field_y+table_height), fill='#cccccc', width=1)
    
    return img

def create_view_tab():
    width, height = 800, 600
    img, draw = create_base_window(width, height)
    img, draw = add_header(img, draw, width)
    img, draw = add_tabs(img, draw, width, 2)  # 2 = View Attendance tab active
    
    # Content area
    draw.rectangle((20, 160, width-20, height-60), fill='white', outline='#cccccc')
    
    # Form title
    try:
        title_font = ImageFont.truetype("arial.ttf", 16)
        normal_font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        title_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
    
    draw.text((40, 180), "View Attendance Records", fill='#333333', font=title_font)
    
    # Date selector
    field_y = 220
    draw.text((40, field_y), "Select Date (DD-MM-YYYY):", fill='#333333', font=normal_font)
    draw.rectangle((240, field_y-5, 380, field_y+25), fill='white', outline='#cccccc')
    draw.text((250, field_y), "01-05-2025", fill='#555555', font=normal_font)
    
    draw.rectangle((390, field_y-5, 450, field_y+25), fill='#1976d2', outline='#0d47a1')
    draw.text((410, field_y), "View", fill='white', font=normal_font)
    
    draw.rectangle((460, field_y-5, 560, field_y+25), fill='#4caf50', outline='#2e7d32')
    draw.text((475, field_y), "Export CSV", fill='white', font=normal_font)
    
    # Status
    field_y += 50
    draw.text((40, field_y), "Status: Ready", fill='#1976d2', font=normal_font)
    
    # Attendance table
    field_y += 40
    table_width = 720
    table_height = 250
    draw.rectangle((40, field_y, 40+table_width, field_y+table_height), fill='white', outline='#cccccc')
    
    # Table header
    draw.rectangle((40, field_y, 40+table_width, field_y+30), fill='#e0e0e0', outline='#cccccc')
    col_widths = [100, 320, 180, 120]
    col_x = 40
    for i, col in enumerate(["ID", "Name", "Date", "Time"]):
        draw.text((col_x + 10, field_y + 8), col, fill='#333333', font=normal_font)
        col_x += col_widths[i] if i < len(col_widths) else 100
        draw.line((col_x, field_y, col_x, field_y+table_height), fill='#cccccc', width=1)
    
    # Sample data rows
    row_y = field_y + 30
    for i in range(5):
        draw.rectangle((40, row_y, 40+table_width, row_y+30), fill='white', outline='#cccccc')
        if i % 2 == 1:
            draw.rectangle((40, row_y, 40+table_width, row_y+30), fill='#f5f5f5', outline='#cccccc')
        
        # Sample data
        col_x = 40
        student_id = f"STU{1001+i}"
        name = f"Student {i+1}"
        date = "01-05-2025"
        time_str = f"09:{10+i}:00"
        
        for j, data in enumerate([student_id, name, date, time_str]):
            draw.text((col_x + 10, row_y + 8), data, fill='#333333', font=normal_font)
            col_x += col_widths[j] if j < len(col_widths) else 100
        
        row_y += 30
    
    return img

@app.route('/')
def index():
    # Create preview images first
    create_preview_images()
    
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Create a simple HTML template
def create_html_template():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Attendance System Preview</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
                color: #333;
            }
            h1 {
                color: #1976d2;
                margin-bottom: 20px;
                text-align: center;
            }
            .description {
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                line-height: 1.6;
            }
            .preview-container {
                display: flex;
                flex-direction: column;
                gap: 30px;
                align-items: center;
                margin-top: 30px;
            }
            .preview-item {
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                width: 840px;
                max-width: 100%;
            }
            .preview-item h2 {
                color: #1976d2;
                margin-top: 0;
                padding-bottom: 10px;
                border-bottom: 1px solid #eee;
            }
            .preview-item img {
                width: 100%;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            .feature-list {
                list-style-type: none;
                padding: 0;
            }
            .feature-list li {
                padding: 8px 0;
                padding-left: 25px;
                position: relative;
            }
            .feature-list li::before {
                content: "✓";
                color: #4caf50;
                font-weight: bold;
                position: absolute;
                left: 0;
            }
            .feature-list li.in-progress::before {
                content: "→";
                color: #ff9800;
            }
        </style>
    </head>
    <body>
        <h1>Smart Attendance System Preview</h1>
        
        <div class="description">
            <h2>Elegant UI/UX Redesign</h2>
            <p>The Smart Attendance System has been redesigned with a clean, modern interface that improves usability while maintaining all original functionality.</p>
            
            <h3>Key Features:</h3>
            <ul class="feature-list">
                <li>Modern tabbed interface with Registration, Attendance, and View Records sections</li>
                <li>Clean, professional styling with a consistent color scheme</li>
                <li>Interactive components with tooltips and visual feedback</li>
                <li>Animated progress indicators and responsive layout</li>
                <li>Improved visual organization with frames and card layouts</li>
                <li class="in-progress">Enhanced face recognition with real-time feedback</li>
            </ul>
        </div>
        
        <div class="preview-container">
            <div class="preview-item">
                <h2>Registration Tab</h2>
                <p>Allows administrators to register new students by capturing facial images and saving their profiles.</p>
                <img src="/static/registration_preview.png" alt="Registration Tab Preview">
            </div>
            
            <div class="preview-item">
                <h2>Take Attendance Tab</h2>
                <p>Enables automatic attendance tracking using facial recognition technology.</p>
                <img src="/static/attendance_preview.png" alt="Attendance Tab Preview">
            </div>
            
            <div class="preview-item">
                <h2>View Attendance Tab</h2>
                <p>Provides access to attendance records with filtering, viewing, and export capabilities.</p>
                <img src="/static/view_preview.png" alt="View Attendance Tab Preview">
            </div>
        </div>
    </body>
    </html>
    '''
    
    with open('templates/index.html', 'w') as f:
        f.write(html)

if __name__ == '__main__':
    # Create HTML template
    create_html_template()
    
    # Create preview images
    create_preview_images()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)
