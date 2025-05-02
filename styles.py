import tkinter as tk
from tkinter import ttk

def setup_styles(root):
    """Setup custom styles for the application"""
    # Configure the style
    style = ttk.Style(root)
    
    # Configure theme-specific colors
    bg_color = '#f0f0f0'
    accent_color = '#1976d2'  # Blue
    success_color = '#388e3c'  # Green
    warning_color = '#f57c00'  # Orange
    danger_color = '#d32f2f'   # Red
    text_color = '#212121'     # Dark Gray
    
    # Set theme colors
    style.configure('TFrame', background=bg_color)
    style.configure('TLabel', background=bg_color, foreground=text_color)
    style.configure('TButton', foreground=text_color)
    
    # Special button styles
    style.configure('Accent.TButton', foreground='white', background=accent_color)
    style.map('Accent.TButton',
              foreground=[('pressed', 'white'), ('active', 'white')],
              background=[('pressed', '#1565c0'), ('active', '#1e88e5')])
    
    style.configure('Success.TButton', foreground='white', background=success_color)
    style.map('Success.TButton',
              foreground=[('pressed', 'white'), ('active', 'white')],
              background=[('pressed', '#2e7d32'), ('active', '#43a047')])
    
    style.configure('Warning.TButton', foreground='white', background=warning_color)
    style.map('Warning.TButton',
              foreground=[('pressed', 'white'), ('active', 'white')],
              background=[('pressed', '#e65100'), ('active', '#fb8c00')])
    
    style.configure('Danger.TButton', foreground='white', background=danger_color)
    style.map('Danger.TButton',
              foreground=[('pressed', 'white'), ('active', 'white')],
              background=[('pressed', '#b71c1c'), ('active', '#e53935')])
    
    # Combobox styles
    style.map('TCombobox', fieldbackground=[('readonly', bg_color)])
    style.map('TCombobox', selectbackground=[('readonly', accent_color)])
    style.map('TCombobox', selectforeground=[('readonly', 'white')])
    
    # Notebook styles
    style.configure('TNotebook', background=bg_color, tabmargins=[2, 5, 2, 0])
    style.configure('TNotebook.Tab', background='#e0e0e0', foreground=text_color,
                  padding=[10, 5], font=('Helvetica', 10))
    style.map('TNotebook.Tab',
             background=[('selected', accent_color), ('active', '#bbdefb')],
             foreground=[('selected', 'white'), ('active', text_color)])
    
    # Treeview styles
    style.configure('Treeview', background='white', foreground=text_color, rowheight=25)
    style.configure('Treeview.Heading', background='#e1e1e1', foreground=text_color, font=('Helvetica', 10, 'bold'))
    style.map('Treeview', background=[('selected', accent_color)], foreground=[('selected', 'white')])
    
    # Progressbar styles
    style.configure('TProgressbar', background=accent_color, troughcolor='#e0e0e0')
    
    return style
