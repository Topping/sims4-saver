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
import psutil
from pynput.keyboard import Controller, Key


class SimsSaverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("The Sims 4 Save Helper")
        self.root.geometry("500x700")
        self.root.resizable(False, False)

        # Auto-save state
        self.is_running = False
        self.auto_save_thread = None
        self.keyboard = Controller()

        # Load settings
        self.settings_file = os.path.join(os.path.dirname(__file__), "settings.json")
        self.settings = self.load_settings()
        self.test_mode = self.settings.get("test_mode", False)
        self.selected_key = self.settings.get("selected_key", "escape")
        
        # Load interval setting with new non-linear mapping
        if "interval_slider_value" in self.settings:
            self.interval_slider_value = self.settings["interval_slider_value"]
        else:
            # Default to 5 minutes (position 70 in new mapping)
            self.interval_slider_value = 70

        # Available keys for dropdown
        self.available_keys = {
            "escape": "Escape (opens menu)",
            "f5": "F5 (common save key)",
            "f9": "F9 (common quicksave key)",
            "ctrl+s": "Ctrl+S (standard save)",
            "ctrl+shift+s": "Ctrl+Shift+S (custom save)"
        }

        self.setup_modern_style()
        self.create_gui()

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
            display_text = f"{seconds} second{'s' if seconds != 1 else ''}"
        else:
            # Map 31-100 to minutes 1-30
            minutes = max(1, int(1 + ((value - 30) * 29 / 70)))
            display_text = f"{minutes} minute{'s' if minutes != 1 else ''}"
            
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
        title_frame.pack()

        # Modern title with icon
        title_label = ttk.Label(title_frame, text="🎮 Sims 4 Auto-Saver", style='Title.TLabel')
        title_label.pack()

        subtitle_label = ttk.Label(title_frame, text="Automatic save reminder system", 
                                  style='Body.TLabel')
        subtitle_label.pack(pady=(4, 0))

        # Main content card
        self.main_card = self.create_card(main_container)
        self.main_card.pack(fill=tk.X)

        # Interval section
        self.create_interval_section()

        # Key selection section
        self.create_key_section()

        # Test mode section
        self.create_test_mode_section()

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

    def create_interval_section(self):
        """Create the interval configuration section"""
        # Section header
        interval_header = tk.Frame(self.main_card, bg=self.colors['card'])
        interval_header.pack(fill=tk.X, padx=24, pady=(24, 16))

        header_label = ttk.Label(interval_header, text="Save Interval", style='Heading.TLabel')
        header_label.pack(anchor=tk.W)

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

        ttk.Label(labels_frame, text="1 sec", style='BodyOnCard.TLabel').pack(side=tk.LEFT)
        ttk.Label(labels_frame, text="30 min", style='BodyOnCard.TLabel').pack(side=tk.RIGHT)

        self.on_interval_changed(self.interval_slider_value)

    def create_key_section(self):
        """Create the key selection section"""
        # Section header
        key_header = tk.Frame(self.main_card, bg=self.colors['card'])
        key_header.pack(fill=tk.X, padx=24, pady=(16, 12))

        header_label = ttk.Label(key_header, text="Key to Press", style='Heading.TLabel')
        header_label.pack(anchor=tk.W)

        # Key selection container
        key_container = tk.Frame(self.main_card, bg=self.colors['card'])
        key_container.pack(fill=tk.X, padx=24, pady=(0, 8))

        self.key_var = tk.StringVar(value=self.selected_key)
        key_options = list(self.available_keys.keys())
        self.key_dropdown = ttk.Combobox(key_container, textvariable=self.key_var,
                                        values=key_options, state="readonly", width=20,
                                        style='Modern.TCombobox')
        self.key_dropdown.pack(anchor=tk.W)
        self.key_dropdown.bind("<<ComboboxSelected>>", self.on_key_selected)

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
                                              text="Test Mode - Press keys regardless of game status",
                                              variable=self.test_mode_var,
                                              command=self.toggle_test_mode,
                                              style='Modern.TCheckbutton')
        self.test_mode_check.pack()

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

        status_title = ttk.Label(status_inner, text="Status", style='Body.TLabel')
        status_title.pack(anchor=tk.W)

        self.status_var = tk.StringVar(value="Ready to start")
        self.status_label = ttk.Label(status_inner, textvariable=self.status_var,
                                     style='Status.TLabel')
        self.status_label.pack(anchor=tk.W, pady=(4, 0))

    def create_action_buttons(self, parent):
        """Create the action buttons section"""
        button_container = tk.Frame(parent, bg=self.colors['background'])
        button_container.pack(fill=tk.X, pady=12)

        button_frame = tk.Frame(button_container, bg=self.colors['background'])
        button_frame.pack()

        self.start_button = ttk.Button(button_frame, text="Start Auto-Save",
                                      command=self.start_auto_save, style='Modern.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 12))

        self.stop_button = ttk.Button(button_frame, text="Stop Auto-Save",
                                     command=self.stop_auto_save, state=tk.DISABLED,
                                     style='Secondary.TButton')
        self.stop_button.pack(side=tk.LEFT)

    def create_info_footer(self, parent):
        """Create the information footer"""
        footer_frame = tk.Frame(parent, bg=self.colors['background'])
        footer_frame.pack(fill=tk.X, pady=(16, 0))

        # Separator line
        separator = tk.Frame(footer_frame, height=1, bg=self.colors['border'])
        separator.pack(fill=tk.X, pady=(0, 16))

        info_text = ("💡 This app will press your selected key when The Sims 4 is running.\n"
                    "Use Test Mode to verify functionality. Ensure the game has focus when keys are pressed.")
        info_label = ttk.Label(footer_frame, text=info_text, justify=tk.LEFT,
                              style='Body.TLabel')
        info_label.pack(anchor=tk.W)

    def is_sims_running(self):
        """Check if The Sims 4 is currently running"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Check for various Sims 4 process names
                if any(name in proc.info['name'].lower() for name in [
                    'ts4.exe', 'the sims 4.exe', 'ts4_x64.exe'
                ]):
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

                if self.test_mode or self.is_sims_running():
                    if self.test_mode:
                        self.root.after(0, lambda: self.status_var.set("Test Mode - Pressing key..."))
                    else:
                        self.root.after(0, lambda: self.status_var.set("Game detected - Pressing key..."))

                    if self.simulate_save_keybind():
                        self.root.after(0, lambda: self.status_var.set("✅ Key pressed successfully"))
                    else:
                        self.root.after(0, lambda: self.status_var.set("❌ Key press failed"))

                    # Brief pause after save
                    time.sleep(2)
                    if not self.is_running:  # Check if we should stop
                        break

                    if self.test_mode:
                        self.root.after(0, lambda: self.status_var.set("Test Mode - Waiting for next interval"))
                    else:
                        self.root.after(0, lambda: self.status_var.set("Running - Waiting for next interval"))
                else:
                    self.root.after(0, lambda: self.status_var.set("🔍 Waiting for Sims 4..."))

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
                    self.root.after(0, lambda: self.status_var.set("⚠️ Error occurred"))
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
        self.status_var.set("Ready to start")

    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return {"interval_slider_value": 70, "test_mode": False, "selected_key": "escape"}  # Default 5 minutes

    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = SimsSaverApp(root)

    # Handle window close
    def on_closing():
        if app.is_running:
            app.stop_auto_save()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
