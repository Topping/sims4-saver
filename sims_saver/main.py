#!/usr/bin/env python3
"""
Auto-save utility for The Sims 4
Automatically presses Ctrl+Shift+S at configurable intervals when The Sims 4 is running.
"""

import json
import os
import sys
import tempfile
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import platform
# from playsound import playsound # Deprecated and removed
# import simpleaudio as sa # Removed as audio feature is scrapped
from PIL import Image
from pystray import Icon as TrayIcon, Menu as TrayMenu, MenuItem as TrayMenuItem

import psutil
from pynput.keyboard import Controller, Key
# import winsound  # Windows-specific sound module

from sims_saver.localization import Localization


class SimsSaverApp:
    def __init__(self, root):
        # Default settings
        self.DEFAULT_SETTINGS = {
            "interval_slider_value": 70,
            "test_mode": False,
            "selected_key": "escape",
            "monitored_process_name": ["ts4.exe", "the sims 4.exe", "ts4_x64.exe", "the sims 4"],
            "lang_code": "en",
        }

        # Load settings
        self.settings_file = Path(os.path.dirname(__file__)) / "settings.json"
        self.settings = self.load_settings()
        self.test_mode = self.settings.get("test_mode", False)
        self.selected_key = self.settings.get("selected_key", "escape")
        self.monitored_process_name = self.settings.get("monitored_process_name", ["ts4.exe", "the sims 4.exe", "ts4_x64.exe", "the sims 4"])
        self.lang_code = self.settings.get("lang_code", "en")
        self.loc = Localization(self.lang_code)
        
        self.root = root
        self.root.title(self.loc.get("app_title"))
        self.root.geometry("550x800")
        self.root.resizable(False, False)
        
        # Set window icon
        try:
            base_path = Path(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))))
            icon_path = base_path / ("icon.ico" if platform.system() == "Windows" else "icon.png") # Use PNG for non-Windows
            if icon_path.exists():
                # Tkinter on macOS might not support .ico directly, often prefers .png or .gif
                # For full .icns support, deeper integration with app bundle might be needed
                # For now, we'll try .ico on Windows and .png elsewhere as a fallback
                if platform.system() == "Windows":
                    self.root.iconbitmap(str(icon_path))
                else:
                    # Tkinter for non-Windows often needs PhotoImage for PNGs as window icon
                    # This might not set the actual app icon, but the window icon.
                    # Proper .icns requires PyObjC or similar for true app icon integration on macOS.
                    # For now, we'll use a simple approach.
                    try:
                        photo = tk.PhotoImage(file=str(icon_path))
                        self.root.iconphoto(True, photo)
                    except Exception as img_e:
                        print(f"Error setting PNG window icon: {img_e}")
            else:
                print(f"Warning: Icon not found at {icon_path}")
        except Exception as e:
            print(f"Error setting window icon: {e}")

        # Auto-save state
        self.is_running = False
        self.auto_save_thread = None
        self.keyboard = Controller()

        # Load interval setting with new non-linear mapping
        if "interval_slider_value" in self.settings:
            self.interval_slider_value = self.settings["interval_slider_value"]
        else:
            # Default to 5 minutes (position 70 in new mapping)
            self.interval_slider_value = 70

        # Available keys for dropdown
        self.available_keys = {
            "escape": self.loc.get("key_escape"),
            "f5": self.loc.get("key_f5"),
            "f9": self.loc.get("key_f9"),
            "ctrl+s": self.loc.get("key_ctrl_s"),
            "ctrl+shift+s": self.loc.get("key_ctrl_shift_s")
        }

        self.setup_modern_style()
        self.create_gui()
        self.update_gui_language()
        
        # Initialize tray icon
        self.tray_icon = None
        self.create_tray_icon()

    def setup_modern_style(self):
        """Setup modern Material Design-inspired styling"""
        # Material Design color palette
        self.colors = {
            'primary': '#6366F1',      # Indigo-500
            'primary_dark': '#4F46E5', # Indigo-600
            'primary_light': '#A5B4FC', # Indigo-300
            'surface': '#FFFFFF',       # White
            'background': '#F8FAFC',    # Slate-50
            'card': '#FFFFFF',          # White
            'text_primary': '#1E293B',  # Slate-800
            'text_secondary': '#64748B', # Slate-500
            'success': '#10B981',       # Emerald-500
            'warning': '#F59E0B',       # Amber-500
            'error': '#EF4444',         # Red-500
            'border': '#E2E8F0',        # Slate-200
            'hover': '#F1F5F9'          # Slate-100
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['background'])
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Modern button style
        style.configure('Modern.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 12),
                       font=('Segoe UI', 10, 'bold'))
        style.map('Modern.TButton',
                 background=[('active', self.colors['primary_dark']),
                           ('pressed', self.colors['primary_dark'])])
        
        # Secondary button style
        style.configure('Secondary.TButton',
                       background=self.colors['surface'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief='solid',
                       focuscolor='none',
                       padding=(20, 12),
                       font=('Segoe UI', 10))
        style.map('Secondary.TButton',
                 background=[('active', self.colors['hover']),
                           ('pressed', self.colors['hover'])])
        
        # Modern frame style
        style.configure('Card.TFrame',
                       background=self.colors['card'],
                       relief='flat',
                       borderwidth=0)
        
        # Modern label styles
        style.configure('Title.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 18, 'bold'))
        
        style.configure('Heading.TLabel',
                       background=self.colors['card'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 12, 'bold'))
        
        style.configure('Body.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 10))

        style.configure('BodyOnCard.TLabel',
                       background=self.colors['card'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 10))
        
        style.configure('Status.TLabel',
                       background=self.colors['card'],
                       foreground=self.colors['primary'],
                       font=('Segoe UI', 11, 'bold'))
        
        # Modern combobox style
        style.configure('Modern.TCombobox',
                       fieldbackground=self.colors['surface'],
                       background=self.colors['surface'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief='solid',
                       padding=(12, 8),
                       font=('Segoe UI', 10))
        
        # Modern checkbutton style
        style.configure('Modern.TCheckbutton',
                       background=self.colors['card'],
                       foreground=self.colors['text_primary'],
                       focuscolor='none',
                       font=('Segoe UI', 10))

    def toggle_test_mode(self):
        """Handle test mode toggle"""
        self.test_mode = self.test_mode_var.get()
        self.settings["test_mode"] = self.test_mode
        self.save_settings()

    def on_key_selected(self, event=None):
        """Handle key selection change"""
        selected_key = self.key_var.get()
        self.selected_key = selected_key
        self.key_description_var.set(self.available_keys[selected_key])
        self.settings["selected_key"] = selected_key
        self.save_settings()

    def on_interval_changed(self, value):
        """Handle interval slider change with non-linear mapping"""
        value = int(float(value))
        self.interval_slider_value = value
        
        # Non-linear mapping: 0-30 = seconds 1-59, 31-100 = minutes 1-30
        if value <= 30:
            # Map 0-30 to seconds 1-59 (approximately 2 seconds per slider position)
            seconds = max(1, int(1 + (value * 58 / 30)))
            display_text = f"{seconds} {self.loc.get('seconds_plural') if seconds != 1 else self.loc.get('seconds_singular')}"
        else:
            # Map 31-100 to minutes 1-30
            minutes = max(1, int(1 + ((value - 30) * 29 / 70)))
            display_text = f"{minutes} {self.loc.get('minutes_plural') if minutes != 1 else self.loc.get('minutes_singular')}"
            
        self.interval_display_var.set(display_text)
        self.settings["interval_slider_value"] = value
        self.save_settings()

    def get_interval_seconds_from_slider(self):
        """Get interval in seconds from slider value with non-linear mapping"""
        value = self.interval_slider_value
        
        # Non-linear mapping: 0-30 = seconds 1-59, 31-100 = minutes 1-30
        if value <= 30:
            # Map 0-30 to seconds 1-59
            return max(1, int(1 + (value * 58 / 30)))
        else:
            # Map 31-100 to minutes 1-30, convert to seconds
            minutes = max(1, int(1 + ((value - 30) * 29 / 70)))
            return minutes * 60

    def create_gui(self):
        """Create the modern GUI components"""
        # Main container with background
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        # Header section
        header_frame = tk.Frame(main_container, bg=self.colors['background'])
        header_frame.pack(fill=tk.X, pady=(0, 24))

        # App icon and title
        title_frame = tk.Frame(header_frame, bg=self.colors['background'])
        title_frame.pack(side=tk.LEFT)

        # Modern title with icon
        self.title_label = ttk.Label(title_frame, text=self.loc.get("app_title"), style='Title.TLabel')
        self.title_label.pack(anchor=tk.W)

        self.subtitle_label = ttk.Label(title_frame, text=self.loc.get("app_subtitle"), 
                                  style='Body.TLabel')
        self.subtitle_label.pack(anchor=tk.W, pady=(4, 0))

        # Language picker
        self.create_language_picker(header_frame)

        # Main content card
        self.main_card = self.create_card(main_container)
        self.main_card.pack(fill=tk.X)

        # Interval section
        self.create_interval_section()

        # Key selection section
        self.create_key_section()

        # Test mode section
        self.create_test_mode_section()

        # Process selection section
        self.create_process_selection_section()

        # Status, actions, and footer are moved out of the card
        self.create_status_section(main_container)
        self.create_action_buttons(main_container)
        self.create_info_footer(main_container)

    def create_card(self, parent):
        """Create a modern card container"""
        card = tk.Frame(parent, bg=self.colors['card'], relief='flat')
        # Add subtle shadow effect with multiple frames
        shadow = tk.Frame(parent, bg='#E2E8F0', height=2)
        shadow.pack(fill=tk.X, pady=(0, 0))
        return card

    def create_language_picker(self, parent):
        lang_frame = tk.Frame(parent, bg=self.colors['background'])
        lang_frame.pack(side=tk.RIGHT)

        # Use plain text language names
        self.language_options = {
            "en": "English",
            "da": "Danish"
        }

        # Initialize lang_var with the display name of the current language
        self.lang_var = tk.StringVar(value=self.language_options.get(self.lang_code, "English"))
        
        self.lang_picker = ttk.Combobox(lang_frame, textvariable=self.lang_var,
                                        values=list(self.language_options.values()), state="readonly", width=12,
                                        style='Modern.TCombobox') 
        self.lang_picker.pack(side=tk.RIGHT)
        self.lang_picker.bind("<<ComboboxSelected>>", self.on_language_selected)

    def on_language_selected(self, event=None):
        # Extract language code from the selected string (e.g., "English" -> "en")
        selected_display_text = self.lang_var.get()
        lang_code_map = {
            "English": "en",
            "Danish": "da"
        }
        selected_lang = lang_code_map.get(selected_display_text, "en") # Default to English if not found

        self.lang_code = selected_lang
        self.loc = Localization(self.lang_code)
        self.settings["lang_code"] = self.lang_code
        self.save_settings()
        self.update_gui_language()

    def update_gui_language(self):
        self.root.title(self.loc.get("app_title"))
        self.title_label.config(text=self.loc.get("app_title"))
        self.subtitle_label.config(text=self.loc.get("app_subtitle"))
        
        self.interval_header_label.config(text=self.loc.get("save_interval_title"))
        self.on_interval_changed(self.interval_slider_value) # Update interval display
        self.one_sec_label.config(text=self.loc.get("one_sec"))
        self.thirty_min_label.config(text=self.loc.get("thirty_min"))

        self.key_header_label.config(text=self.loc.get("key_to_press_title"))
        self.available_keys = {
            "escape": self.loc.get("key_escape"),
            "f5": self.loc.get("key_f5"),
            "f9": self.loc.get("key_f9"),
            "ctrl+s": self.loc.get("key_ctrl_s"),
            "ctrl+shift+s": self.loc.get("key_ctrl_shift_s")
        }
        self.key_dropdown.config(values=list(self.available_keys.keys()))
        self.key_description_var.set(self.available_keys[self.selected_key])

        self.test_mode_check.config(text=self.loc.get("test_mode_checkbox"))

        self.process_header_label.config(text=self.loc.get("monitored_process_title"))
        self.update_monitored_process_display()
        self.select_process_button.config(text=self.loc.get("select_custom_process_button"))

        self.status_title_label.config(text=self.loc.get("status_title"))
        if not self.is_running: # Only update if not actively running
            self.status_var.set(self.loc.get("status_ready"))

        self.start_button.config(text=self.loc.get("start_helper_button"))
        self.stop_button.config(text=self.loc.get("stop_helper_button"))
        self.revert_button.config(text=self.loc.get("revert_to_defaults_button"))
        self.info_label.config(text=self.loc.get("info_text"))


    def create_interval_section(self):
        """Create the interval configuration section"""
        # Section header
        interval_header = tk.Frame(self.main_card, bg=self.colors['card'])
        interval_header.pack(fill=tk.X, padx=24, pady=(24, 16))

        self.interval_header_label = ttk.Label(interval_header, text=self.loc.get("save_interval_title"), style='Heading.TLabel')
        self.interval_header_label.pack(anchor=tk.W)

        # Interval display
        display_frame = tk.Frame(self.main_card, bg=self.colors['card'])
        display_frame.pack(fill=tk.X, padx=24, pady=(0, 8))

        self.interval_display_var = tk.StringVar()
        self.interval_display_label = ttk.Label(display_frame, textvariable=self.interval_display_var,
                                               style='Status.TLabel')
        self.interval_display_label.pack(anchor=tk.W)

        # Modern slider container
        slider_container = tk.Frame(self.main_card, bg=self.colors['card'])
        slider_container.pack(fill=tk.X, padx=24, pady=(0, 16))

        # Custom styled slider
        self.interval_slider = tk.Scale(slider_container, from_=0, to=100, orient=tk.HORIZONTAL,
                                       command=self.on_interval_changed, length=400,
                                       bg=self.colors['card'], fg=self.colors['text_primary'],
                                       highlightthickness=0, troughcolor=self.colors['border'],
                                       activebackground=self.colors['primary'],
                                       font=('Segoe UI', 9), showvalue=0)
        self.interval_slider.set(self.interval_slider_value)
        self.interval_slider.pack(fill=tk.X)

        # Slider labels
        labels_frame = tk.Frame(slider_container, bg=self.colors['card'])
        labels_frame.pack(fill=tk.X, pady=(4, 0))

        self.one_sec_label = ttk.Label(labels_frame, text=self.loc.get("one_sec"), style='BodyOnCard.TLabel')
        self.one_sec_label.pack(side=tk.LEFT)
        self.thirty_min_label = ttk.Label(labels_frame, text=self.loc.get("thirty_min"), style='BodyOnCard.TLabel')
        self.thirty_min_label.pack(side=tk.RIGHT)

        self.on_interval_changed(self.interval_slider_value)

    def create_key_section(self):
        """Create the key selection section"""
        # Section header
        key_header = tk.Frame(self.main_card, bg=self.colors['card'])
        key_header.pack(fill=tk.X, padx=24, pady=(16, 12))

        self.key_header_label = ttk.Label(key_header, text=self.loc.get("key_to_press_title"), style='Heading.TLabel')
        self.key_header_label.pack(anchor=tk.W)

        # Key selection container
        key_container = tk.Frame(self.main_card, bg=self.colors['card'])
        key_container.pack(fill=tk.X, padx=24, pady=(0, 8))

        self.key_var = tk.StringVar(value=self.selected_key)
        key_options = list(self.available_keys.keys())
        self.key_dropdown = ttk.Combobox(key_container, textvariable=self.key_var,
                                        values=key_options, state="readonly", width=20,
                                        style='Modern.TCombobox')
        self.key_dropdown.pack(side=tk.LEFT, anchor=tk.W, padx=(0, 12))
        self.key_dropdown.bind("<<ComboboxSelected>>", self.on_key_selected)

        # Sound cue checkbox next to key dropdown
        # Audio feature scrapped, remove checkbox
        # self.play_sound_cue_var = tk.BooleanVar(value=self.play_sound_cue)
        # self.play_sound_cue_check = ttk.Checkbutton(key_container,
        #                                       text=self.loc.get("play_sound_cue_checkbox"),
        #                                       variable=self.play_sound_cue_var,
        #                                       command=self.toggle_sound_cue,
        #                                       style='Modern.TCheckbutton')
        # self.play_sound_cue_check.pack(side=tk.LEFT, anchor=tk.W)

        # Key description
        desc_frame = tk.Frame(self.main_card, bg=self.colors['card'])
        desc_frame.pack(fill=tk.X, padx=24, pady=(4, 16))

        self.key_description_var = tk.StringVar(value=self.available_keys[self.selected_key])
        key_desc_label = ttk.Label(desc_frame, textvariable=self.key_description_var,
                                  style='BodyOnCard.TLabel')
        key_desc_label.pack(anchor=tk.W)

    def create_test_mode_section(self):
        """Create the test mode section"""
        test_frame = tk.Frame(self.main_card, bg=self.colors['card'])
        test_frame.pack(fill=tk.X, padx=24, pady=(16, 16))

        # Create custom checkbox container
        checkbox_container = tk.Frame(test_frame, bg=self.colors['card'])
        checkbox_container.pack(anchor=tk.W)

        self.test_mode_var = tk.BooleanVar(value=self.test_mode)
        self.test_mode_check = ttk.Checkbutton(checkbox_container,
                                              text=self.loc.get("test_mode_checkbox"),
                                              variable=self.test_mode_var,
                                              command=self.toggle_test_mode,
                                              style='Modern.TCheckbutton')
        self.test_mode_check.pack()

    def create_process_selection_section(self):
        """Create the process selection section"""
        process_frame = tk.Frame(self.main_card, bg=self.colors['card'])
        process_frame.pack(fill=tk.X, padx=24, pady=(16, 16))

        self.process_header_label = ttk.Label(process_frame, text=self.loc.get("monitored_process_title"), style='Heading.TLabel')
        self.process_header_label.pack(anchor=tk.W, pady=(0, 8))

        self.monitored_process_var = tk.StringVar()
        self.update_monitored_process_display()
        process_label = ttk.Label(process_frame, textvariable=self.monitored_process_var, style='BodyOnCard.TLabel')
        process_label.pack(anchor=tk.W)

        self.select_process_button = ttk.Button(process_frame, text=self.loc.get("select_custom_process_button"), command=self.open_process_selection_dialog, style='Secondary.TButton')
        self.select_process_button.pack(anchor=tk.W, pady=(12, 0))

    def update_monitored_process_display(self):
        """Update the display for the currently monitored process names"""
        # Remove .exe for display purposes if on Windows, otherwise keep as is
        display_names = [name.replace('.exe', '') if platform.system() == "Windows" and name.lower().endswith('.exe') else name for name in self.monitored_process_name]
        self.monitored_process_var.set(self.loc.get("currently_monitoring", process_names=', '.join(display_names)))

    def open_process_selection_dialog(self):
        """Open a dialog for the user to select a custom process to monitor"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self.loc.get("select_process_dialog_title"))
        dialog.geometry("400x600")
        dialog.transient(self.root)  # Make dialog appear on top of main window
        dialog.grab_set()  # Modal dialog

        # Styles for dialog
        dialog.configure(bg=self.colors['background'])
        style = ttk.Style()
        style.configure('Dialog.TLabel', background=self.colors['background'], foreground=self.colors['text_primary'], font=('Segoe UI', 10))
        style.configure('Dialog.TButton', background=self.colors['primary'], foreground='white', borderwidth=0, font=('Segoe UI', 9, 'bold'))
        style.map('Dialog.TButton', background=[('active', self.colors['primary_dark'])])

        # Header
        header_frame = tk.Frame(dialog, bg=self.colors['background'])
        header_frame.pack(fill=tk.X, padx=16, pady=(16, 8))
        ttk.Label(header_frame, text=self.loc.get("select_process_dialog_header"), style='Dialog.TLabel').pack(anchor=tk.W)

        # Search bar
        search_frame = tk.Frame(dialog, bg=self.colors['background'])
        search_frame.pack(fill=tk.X, padx=16, pady=(0, 8))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40, style='Modern.TCombobox')
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Process list
        list_frame = tk.Frame(dialog, bg=self.colors['card'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        process_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, borderwidth=0, highlightthickness=0,
                                     font=('Segoe UI', 10), selectmode=tk.EXTENDED, 
                                     bg=self.colors['card'], fg=self.colors['text_primary'],
                                     selectbackground=self.colors['primary_light'], selectforeground=self.colors['text_primary'])
        scrollbar.config(command=process_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        process_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def populate_process_list(filter_text=""):
            process_listbox.delete(0, tk.END)
            running_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    process_name = proc.info['name']
                    if process_name:
                        # Only consider processes with names that are not empty
                        if platform.system() == "Windows" and process_name.lower().endswith('.exe'):
                            if filter_text.lower() in process_name.lower():
                                running_processes.append(process_name)
                        elif platform.system() == "Darwin": # MacOS
                            # On macOS, processes might not have .exe. Filter by name directly.
                            if filter_text.lower() in process_name.lower():
                                running_processes.append(process_name)
                        elif platform.system() == "Linux": # Linux (for completeness, though not primary target)
                            if filter_text.lower() in process_name.lower():
                                running_processes.append(process_name)
                        else:
                            # Fallback for other systems, just use process name
                            if filter_text.lower() in process_name.lower():
                                running_processes.append(process_name)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            running_processes = sorted(list(set(running_processes))) # Remove duplicates and sort
            for p_name in running_processes:
                process_listbox.insert(tk.END, p_name)

        def on_search_change(*args):
            populate_process_list(search_var.get())

        search_var.trace("w", on_search_change)

        populate_process_list()

        # Action buttons
        button_frame = tk.Frame(dialog, bg=self.colors['background'])
        button_frame.pack(fill=tk.X, padx=16, pady=(0, 16))

        def on_select():
            selected_indices = process_listbox.curselection()
            if selected_indices:
                selected_processes = [process_listbox.get(i).lower() for i in selected_indices]
                self.monitored_process_name = selected_processes
                self.settings["monitored_process_name"] = self.monitored_process_name
                self.save_settings()
                self.update_monitored_process_display()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        ttk.Button(button_frame, text=self.loc.get("select_button"), command=on_select, style='Dialog.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(button_frame, text=self.loc.get("cancel_button"), command=on_cancel, style='Secondary.TButton').pack(side=tk.LEFT)

        self.root.wait_window(dialog) # Wait for dialog to close

    def create_status_section(self, parent):
        """Create the status display section"""
        status_frame = tk.Frame(parent, bg=self.colors['background'])
        status_frame.pack(fill=tk.X, pady=(16, 0))

        # Status container with background
        status_container = tk.Frame(status_frame, bg=self.colors['background'], 
                                   relief='flat', bd=1)
        status_container.pack(fill=tk.X)

        status_inner = tk.Frame(status_container, bg=self.colors['background'])
        status_inner.pack(padx=16, pady=12)

        self.status_title_label = ttk.Label(status_inner, text=self.loc.get("status_title"), style='Body.TLabel')
        self.status_title_label.pack(anchor=tk.W)

        self.status_var = tk.StringVar(value=self.loc.get("status_ready"))
        self.status_label = ttk.Label(status_inner, textvariable=self.status_var,
                                     style='Status.TLabel')
        self.status_label.pack(anchor=tk.W, pady=(4, 0))

    def create_action_buttons(self, parent):
        """Create the action buttons section"""
        button_container = tk.Frame(parent, bg=self.colors['background'])
        button_container.pack(fill=tk.X, pady=12)

        button_frame = tk.Frame(button_container, bg=self.colors['background'])
        button_frame.pack()

        self.start_button = ttk.Button(button_frame, text=self.loc.get("start_helper_button"),
                                      command=self.start_auto_save, style='Modern.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 12))

        self.stop_button = ttk.Button(button_frame, text=self.loc.get("stop_helper_button"),
                                     command=self.stop_auto_save, state=tk.DISABLED,
                                     style='Secondary.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 12))

        self.revert_button = ttk.Button(button_frame, text=self.loc.get("revert_to_defaults_button"),
                                      command=self.revert_to_default_settings, style='Secondary.TButton')
        self.revert_button.pack(side=tk.LEFT, padx=(12, 0))

    def create_info_footer(self, parent):
        """Create the information footer"""
        footer_frame = tk.Frame(parent, bg=self.colors['background'])
        footer_frame.pack(fill=tk.X, pady=(16, 0))

        # Separator line
        separator = tk.Frame(footer_frame, height=1, bg=self.colors['border'])
        separator.pack(fill=tk.X, pady=(0, 16))

        info_text = self.loc.get("info_text")
        self.info_label = ttk.Label(footer_frame, text=info_text, justify=tk.LEFT,
                                  style='Body.TLabel')
        self.info_label.pack(anchor=tk.W)

    def is_process_running(self, process_names):
        """Check if any of the specified processes are currently running"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                process_full_name = proc.info['name'].lower() if proc.info['name'] else ""
                for name in process_names:
                    if platform.system() == "Windows" and name.lower().endswith('.exe'):
                        if name.lower() in process_full_name:
                            return True
                    elif platform.system() == "Darwin" or platform.system() == "Linux": # MacOS or Linux
                        # On macOS/Linux, process names might not have .exe. Match directly.
                        # Some macOS apps might have .app extension or no extension.
                        # We check if the monitored name is part of the full process name.
                        if name.lower() in process_full_name:
                            return True
                    else:
                        # Fallback for other systems, just use direct name matching
                        if name.lower() in process_full_name:
                            return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def simulate_save_keybind(self):
        """Simulate pressing the selected key combination"""
        try:
            key = self.selected_key

            if key == "escape":
                self.keyboard.press(Key.esc)
                self.keyboard.release(Key.esc)
            elif key == "f5":
                self.keyboard.press(Key.f5)
                self.keyboard.release(Key.f5)
            elif key == "f9":
                self.keyboard.press(Key.f9)
                self.keyboard.release(Key.f9)
            elif key == "ctrl+s":
                with self.keyboard.pressed(Key.ctrl):
                    self.keyboard.press('s')
                    self.keyboard.release('s')
            elif key == "ctrl+shift+s":
                with self.keyboard.pressed(Key.ctrl):
                    with self.keyboard.pressed(Key.shift):
                        self.keyboard.press('s')
                        self.keyboard.release('s')
            else:
                # Default to escape if unknown key
                self.keyboard.press(Key.esc)
                self.keyboard.release(Key.esc)

            return True
        except Exception as e:
            print(f"Error simulating key press: {e}")
            return False

    def auto_save_loop(self):
        """Main auto-save loop running in background thread"""
        while self.is_running:
            try:
                if not self.is_running:  # Check again in case we were stopped
                    break

                if self.test_mode or self.is_process_running(self.monitored_process_name):
                    if self.test_mode:
                        self.root.after(0, lambda: self.status_var.set(self.loc.get("status_test_mode_pressing")))
                    else:
                        self.root.after(0, lambda: self.status_var.set(self.loc.get("status_game_detected_pressing")))

                    if self.simulate_save_keybind():
                        self.root.after(0, lambda: self.status_var.set(self.loc.get("status_key_pressed_success")))
                    else:
                        self.root.after(0, lambda: self.status_var.set(self.loc.get("status_key_press_failed")))

                    # Brief pause after save
                    time.sleep(2)
                    if not self.is_running:  # Check if we should stop
                        break

                    if self.test_mode:
                        self.root.after(0, lambda: self.status_var.set(self.loc.get("status_test_mode_waiting")))
                    else:
                        self.root.after(0, lambda: self.status_var.set(self.loc.get("status_running_waiting")))
                else:
                    self.root.after(0, lambda: self.status_var.set(self.loc.get("status_waiting_for_process")))

                # Wait for next interval with periodic checks
                interval_seconds = self.get_interval_seconds()
                elapsed = 0
                while elapsed < interval_seconds and self.is_running:
                    sleep_time = min(1.0, interval_seconds - elapsed)  # Sleep max 1 second at a time
                    time.sleep(sleep_time)
                    elapsed += sleep_time

            except Exception as e:
                print(f"Error in auto-save loop: {e}")
                if self.is_running:  # Only update status if still running
                    self.root.after(0, lambda: self.status_var.set(self.loc.get("status_error_occurred")))
                    time.sleep(5)  # Brief pause before retry

    def get_interval_seconds(self):
        """Get the current interval in seconds"""
        return self.get_interval_seconds_from_slider()

    def start_auto_save(self):
        """Start the auto-save process"""
        if self.is_running:
            return

        # Ensure any previous thread is fully stopped
        if self.auto_save_thread and self.auto_save_thread.is_alive():
            self.stop_auto_save()
            time.sleep(0.5)  # Brief pause to ensure cleanup

        # Save settings
        self.settings["test_mode"] = self.test_mode
        self.settings["selected_key"] = self.selected_key
        self.settings["interval_slider_value"] = self.interval_slider_value
        self.settings["monitored_process_name"] = self.monitored_process_name
        self.settings["lang_code"] = self.lang_code
        self.save_settings()

        # Start auto-save
        self.is_running = True
        self.auto_save_thread = threading.Thread(target=self.auto_save_loop, daemon=True)
        self.auto_save_thread.start()

        # Update UI
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.interval_slider.config(state=tk.DISABLED)
        self.key_dropdown.config(state=tk.DISABLED)
        self.status_var.set("Running - Auto-save active")
        if self.tray_icon:
            self.tray_icon.update_menu() # Update tray icon menu to reflect state change

    def stop_auto_save(self):
        """Stop the auto-save process"""
        if not self.is_running:
            return

        self.is_running = False

        # Wait for thread to finish
        if self.auto_save_thread and self.auto_save_thread.is_alive():
            self.auto_save_thread.join(timeout=2)

        # Clear thread reference
        self.auto_save_thread = None

        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.interval_slider.config(state=tk.NORMAL)
        self.key_dropdown.config(state=tk.NORMAL)
        self.status_var.set(self.loc.get("status_ready"))
        if self.tray_icon:
            self.tray_icon.update_menu() # Update tray icon menu to reflect state change

    def revert_to_default_settings(self):
        """Revert all settings to their default values."""
        self.settings = self.DEFAULT_SETTINGS.copy() # Use a copy of default settings
        self.test_mode = self.settings["test_mode"]
        self.selected_key = self.settings["selected_key"]
        self.interval_slider_value = self.settings["interval_slider_value"]
        self.monitored_process_name = self.settings["monitored_process_name"]
        self.lang_code = self.settings["lang_code"]
        self.loc = Localization(self.lang_code)
        
        # Update UI elements
        self.update_monitored_process_display()
        self.key_var.set(self.selected_key)
        self.on_key_selected() 
        self.interval_slider.set(self.interval_slider_value)
        self.on_interval_changed(self.interval_slider_value) 
        self.test_mode_var.set(self.test_mode) 
        self.lang_var.set(self.language_options.get(self.lang_code, "English"))
        self.update_gui_language()
        self.save_settings() 
        self.root.after(0, lambda: self.status_var.set(self.loc.get("settings_reverted")))

    def load_settings(self):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return self.DEFAULT_SETTINGS.copy()  # Return default settings if loading fails or file doesn't exist

    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def on_closing(self):
        """Handles the window closing event."""
        if self.is_running:
            self.stop_auto_save()
        if self.tray_icon:
            self.tray_icon.stop()
            time.sleep(0.5) # Give the tray icon a moment to fully stop
        self.root.destroy()

    def create_tray_icon(self):
        """Creates a system tray icon for the application."""
        if self.tray_icon is not None:
            self.tray_icon.stop()
            self.tray_icon = None

        # Define the icon image
        # pystray requires a PIL Image object
        icon_filename = "icon.ico" if platform.system() == "Windows" else "icon.png"
        base_path = Path(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))))
        icon_path = base_path / icon_filename

        try:
            if icon_path.exists():
                image = Image.open(icon_path)
            else:
                print(f"Warning: Tray icon not found at {icon_path}")
                return
        except Exception as e:
            print(f"Error loading tray icon image: {e}")
            return

        # Create the menu items
        menu_items = [
            TrayMenuItem(self.loc.get("start_helper_button"), self.start_auto_save, default=True, visible=not self.is_running),
            TrayMenuItem(self.loc.get("stop_helper_button"), self.stop_auto_save, visible=self.is_running),
            TrayMenuItem(self.loc.get("revert_to_defaults_button"), self.revert_to_default_settings),
            TrayMenuItem(self.loc.get("quit_button"), self.on_closing)
        ]

        # Create the tray icon
        self.tray_icon = TrayIcon(
            self.loc.get("app_title"),
            image,
            menu=TrayMenu(*menu_items)
        )
        # Run the icon in a separate thread to not block the main Tkinter thread
        threading.Thread(target=self.tray_icon.run, daemon=True).start()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = SimsSaverApp(root)

    # Handle window close
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    try:
        root.mainloop()
    finally:
        # Ensure tray icon is stopped even if mainloop exits unexpectedly
        if app.tray_icon:
            app.tray_icon.stop()
            time.sleep(0.5)  # Give the tray icon a moment to fully stop


if __name__ == "__main__":
    main()
