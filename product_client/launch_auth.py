import customtkinter as ctk
import sys
import os
import threading
import json

# Ensure we can import from string_cleaner and local utils
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add string_cleaner directory to sys.path to allow importing gui
sys.path.append(os.path.join(current_dir, '..', 'string_cleaner'))
# Add current dir for utils
sys.path.append(current_dir)

import api_client
from hwid_utils import get_hwid

# Constants
LICENSE_FILE = os.path.join(os.getenv('APPDATA'), 'MakiCleaner', 'license.json')
LOGO_COLOR = "#A855F7"

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Maki Cleaner - Login")
        self.geometry("400x300")
        self.resizable(False, False)
        self.configure(fg_color="#000000")
        
        # Center Window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (400 // 2)
        y = (screen_height // 2) - (300 // 2)
        self.geometry(f"400x300+{x}+{y}")

        # UI Elements
        self.logo = ctk.CTkLabel(self, text="Maki Cleaner", font=("Segoe UI", 24, "bold"), text_color=LOGO_COLOR)
        self.logo.pack(pady=(40, 20))

        self.key_entry = ctk.CTkEntry(self, placeholder_text="Enter License Key", width=300, height=40, font=("Segoe UI", 12))
        self.key_entry.pack(pady=10)

        self.login_btn = ctk.CTkButton(self, text="Activate", command=self.attempt_login, width=300, height=40, 
                                       fg_color=LOGO_COLOR, hover_color="#9333EA", font=("Segoe UI", 12, "bold"))
        self.login_btn.pack(pady=10)

        self.status = ctk.CTkLabel(self, text="Status: Waiting for key...", text_color="gray", font=("Segoe UI", 10))
        self.status.pack(pady=10)

        self.hwid_display = ctk.CTkLabel(self, text=f"HWID: {get_hwid()}", text_color="#333333", font=("Segoe UI", 8))
        self.hwid_display.pack(side="bottom", pady=5)

        # Auto-check stored license
        self.authenticated = False
        self.check_stored_license()

    def check_stored_license(self):
        if os.path.exists(LICENSE_FILE):
             try:
                 with open(LICENSE_FILE, 'r') as f:
                     data = json.load(f)
                     key = data.get('key')
                     if key:
                         self.key_entry.insert(0, key)
                         self.status.configure(text="Validating saved key...")
                         threading.Thread(target=self.validate_and_launch, args=(key,), daemon=True).start()
             except: pass

    def attempt_login(self):
        key = self.key_entry.get().strip()
        if not key:
            self.status.configure(text="Please enter a key.", text_color="#EF4444")
            return
        
        self.login_btn.configure(state="disabled", text="Checking...")
        threading.Thread(target=self.validate_and_launch, args=(key,), daemon=True).start()

    def validate_and_launch(self, key):
        valid, message = api_client.validate_license(key)
        
        if valid:
            self.status.configure(text="Success! Launching...", text_color="#10B981")
            self.save_license(key)
            self.authenticated = True
            self.after(1000, self.quit_login)
        else:
            self.status.configure(text=f"Error: {message}", text_color="#EF4444")
            self.login_btn.configure(state="normal", text="Activate")

    def save_license(self, key):
        try:
            os.makedirs(os.path.dirname(LICENSE_FILE), exist_ok=True)
            with open(LICENSE_FILE, 'w') as f:
                json.dump({'key': key}, f)
        except: pass

    def quit_login(self):
        self.destroy()

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
    
    # ONLY Run Main App if Authenticated AND Login Window is Closed
    if getattr(app, 'authenticated', False):
        try:
            import gui
            main_app = gui.StringCleanerApp()
            main_app.mainloop()
        except ImportError as e:
            # Fallback if not found (e.g. during standalone testing)
            print(f"Could not load main app: {e}")
            import tkinter.messagebox
            root = tkinter.Tk()
            root.withdraw()
            tkinter.messagebox.showerror("Error", f"Failed to load application core: {e}")
