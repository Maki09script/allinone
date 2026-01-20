import customtkinter as ctk
from PIL import Image
import os
import sys
import threading
import time
from cleaner import *

# Set appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class StringCleanerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("String Cleaner")
        self.geometry("600x800") # Slightly taller to fit more
        self.configure(fg_color="#000000")
        self.resizable(False, False)

        # Center Window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (600 // 2)
        y = (screen_height // 2) - (800 // 2)
        self.geometry(f"600x800+{x}+{y}")

        # --- Top UI Elements (Shared) ---
        self.logo_label = ctk.CTkLabel(self, text="Maki", font=("Segoe UI", 18, "bold"), text_color="#A855F7")
        self.logo_label.place(x=20, y=20)

        self.stream_mode = ctk.CTkCheckBox(self, text="Streammode", font=("Segoe UI", 12), 
                                          fg_color="#3B82F6", border_color="#4B5563", 
                                          hover_color="#2563EB", corner_radius=5)
        self.stream_mode.place(x=450, y=20)

        self.close_btn = ctk.CTkLabel(self, text="✕", font=("Segoe UI", 16), text_color="#9CA3AF")
        self.close_btn.place(x=560, y=20)
        self.close_btn.bind("<Button-1>", lambda e: self.quit())

        self.main_title = ctk.CTkLabel(self, text="String Cleaner", font=("Segoe UI", 16, "bold"), text_color="white")
        self.main_title.pack(pady=(60, 10))

        # --- Shared Status Bar ---
        self.status_bar = ctk.CTkLabel(self, text="Ready", font=("Segoe UI", 11), text_color="#6B7280", height=20)
        self.status_bar.place(x=300, y=750, anchor="center")

        self.btn_params = {
            "width": 220, "height": 40, "corner_radius": 10,
            "fg_color": "#111827", "text_color": "#9CA3AF",
            "font": ("Segoe UI", 12), "border_width": 1,
            "border_color": "#1F2937", "hover_color": "#1F2937"
        }

        self.button_objects = {}

        # --- Page 1: Standard Cleaner (Image 2) ---
        self.page1 = ctk.CTkFrame(self, fg_color="transparent")
        
        self.category_var = ctk.StringVar(value="Select Category")
        self.category_dropdown = ctk.CTkComboBox(self.page1, values=["Windows Logs", "Registry Traces", "Cache Files"],
                                               variable=self.category_var, width=450, height=35,
                                               fg_color="#111827", border_color="#374151", 
                                               button_color="#1F2937", button_hover_color="#374151",
                                               dropdown_fg_color="#111827", dropdown_hover_color="#1F2937",
                                               corner_radius=15, font=("Segoe UI", 13))
        self.category_dropdown.pack(pady=10)

        self.grid1 = ctk.CTkFrame(self.page1, fg_color="transparent")
        self.grid1.pack(pady=10)

        self.config1 = [
            ("Clean Data Usage", clean_data_usage, "Clean Reset Data Usage", clean_reset_data_usage),
            ("Clean USB Plug", clean_usb_plug, "Clean LastRunTime of Apps", clean_last_runtime),
            ("Clean Installed Programs", clean_installed_programs, "Clean Shimcache", clean_shimcache),
            ("Clean OverwriteMemory", clean_overwrite_memory, "Clean Form History", clean_form_history),
            ("Clean Windows Search", clean_windows_search, "Clean NirSoft Logs", clean_nirsoft_logs),
            ("Clean OsForensics Logs", clean_osforensics_logs, "Clean Thumbnail Cache", clean_thumbnail_cache),
            ("Clean Run History", clean_run_history, "Clean AmCache", clean_amcache),
            ("Clean RecentFileCache", clean_recent_file_cache, "Clean MRU Registry", clean_mru_registry)
        ]

        for row, (l_text, l_func, r_text, r_func) in enumerate(self.config1):
            btn_l = ctk.CTkButton(self.grid1, text=l_text, command=lambda f=l_func, t=l_text: self.execute_cleanup(t, f), **self.btn_params)
            btn_l.grid(row=row, column=0, padx=10, pady=5)
            self.button_objects[l_text] = btn_l
            btn_r = ctk.CTkButton(self.grid1, text=r_text, command=lambda f=r_func, t=r_text: self.execute_cleanup(t, f), **self.btn_params)
            btn_r.grid(row=row, column=1, padx=10, pady=5)
            self.button_objects[r_text] = btn_r

        # --- Page 2: Advanced Cleaner (Image 1) ---
        self.page2 = ctk.CTkFrame(self, fg_color="transparent")
        self.grid2 = ctk.CTkFrame(self.page2, fg_color="transparent")
        self.grid2.pack(pady=10)

        self.config2 = [
            ("Clean Windows Temp", clean_windows_temp, "Clean Prefetch", clean_prefetch),
            ("Clean Crashdumps", clean_crash_dumps, "Clean Recent", clean_recent_items),
            ("Clean Last Activity", clean_last_activity, "Clean User Assist", clean_user_assist),
            ("Clean Regseeker", clean_regseeker, "Clean ShellBag", clean_shellbags),
            ("Clean Event Log", clean_event_logs, "Clean History", clean_history),
            ("Clean Registry Editor", clean_registry_editor, "Clean Steam Accounts", clean_steam_accounts),
            ("Clean Protection History", clean_protection_history, "Clean Jump List", clean_jumplist_cache),
            ("Clean Browser History", clean_browser_history, "Clean Nvidia", clean_nvidia_cache),
            ("Clean Journal Traces", clean_journal_traces, "Clean Regedits", clean_regedits),
            ("Clean Memory", clean_memory, "Clean DNSCache", clean_dns_cache)
        ]

        for row, (l_text, l_func, r_text, r_func) in enumerate(self.config2):
            btn_l = ctk.CTkButton(self.grid2, text=l_text, command=lambda f=l_func, t=l_text: self.execute_cleanup(t, f), **self.btn_params)
            btn_l.grid(row=row, column=0, padx=10, pady=4)
            self.button_objects[l_text] = btn_l
            btn_r = ctk.CTkButton(self.grid2, text=r_text, command=lambda f=r_func, t=r_text: self.execute_cleanup(t, f), **self.btn_params)
            btn_r.grid(row=row, column=1, padx=10, pady=4)
            self.button_objects[r_text] = btn_r

        # --- Page 3: System Cleaner (Image 3) ---
        self.page3 = ctk.CTkFrame(self, fg_color="transparent")
        self.grid3 = ctk.CTkFrame(self.page3, fg_color="transparent")
        self.grid3.pack(pady=10)

        self.config3 = [
            ("Clean WMI Process", clean_wmi_process, "Clean Windows Timeline", clean_windows_timeline),
            ("Clean EtwTrace", clean_etw_trace, "Clean .etl", clean_etl),
            ("Clean DiagTrack", clean_diagtrack, "Clean USB Traces Registry", clean_usb_traces_registry),
            ("Clean MountedDevices", clean_mounted_devices, "Clean TypeURLS", clean_type_urls),
            ("Clean Run Dialog History", clean_run_dialog_history, "Clean Start Menu Search", clean_start_menu_search),
            ("Clean JumpList Cache", clean_jumplist_cache, "Clean Clipboard History", clean_clipboard_history),
            ("Clean IconCache", clean_icon_cache, "Clean SPP Machine GUIDs", clean_spp_machine_guids),
            ("Windows Reliability Monitor", clean_reliability_monitor, "Clean Nvidia Configurations", clean_nvidia_configurations)
        ]

        for row, (l_text, l_func, r_text, r_func) in enumerate(self.config3):
            btn_l = ctk.CTkButton(self.grid3, text=l_text, command=lambda f=l_func, t=l_text: self.execute_cleanup(t, f), **self.btn_params)
            btn_l.grid(row=row, column=0, padx=10, pady=5)
            self.button_objects[l_text] = btn_l
            btn_r = ctk.CTkButton(self.grid3, text=r_text, command=lambda f=r_func, t=r_text: self.execute_cleanup(t, f), **self.btn_params)
            btn_r.grid(row=row, column=1, padx=10, pady=5)
            self.button_objects[r_text] = btn_r

        # --- RESTORED FEATURES (Not in images but previously present) ---
        self.advanced_frame = ctk.CTkFrame(self.page3, fg_color="transparent")
        self.advanced_frame.pack(pady=10)

        self.pid_entry = ctk.CTkEntry(self.advanced_frame, placeholder_text="PID", width=60, height=35, 
                                     fg_color="#111827", border_color="#374151", text_color="white")
        self.pid_entry.pack(side="left", padx=5)

        self.pid_wipe_btn = ctk.CTkButton(self.advanced_frame, text="PID WIPE", 
                                        command=self.run_pid_wipe,
                                        width=120, height=35, corner_radius=10,
                                        fg_color="#5865F2", hover_color="#4752C4",
                                        font=("Segoe UI", 11, "bold"))
        self.pid_wipe_btn.pack(side="left", padx=5)

        self.bam_btn = ctk.CTkButton(self.advanced_frame, text="BAM CLEANER", 
                                       command=lambda: self.execute_cleanup("BAM CLEANER", lambda: clean_bam_state(log_callback=self.update_status)),
                                       width=120, height=35, corner_radius=10,
                                       fg_color="#10B981", hover_color="#059669",
                                       font=("Segoe UI", 11, "bold"))
        self.bam_btn.pack(side="left", padx=5)
        self.button_objects["BAM CLEANER"] = self.bam_btn

        self.solara_btn = ctk.CTkButton(self.advanced_frame, text="SOLARA DEEP SCAN", 
                                       command=self.run_solara_scan,
                                       width=210, height=35, corner_radius=10,
                                       fg_color="#ED4245", hover_color="#C03537",
                                       font=("Segoe UI", 11, "bold"))
        self.solara_btn.pack(side="left", padx=5)

        # --- Shared Log Area ---
        self.log_area = ctk.CTkTextbox(self, width=560, height=100, corner_radius=10,
                                       fg_color="#000000", border_color="#1F2937", border_width=1,
                                       text_color="#9CA3AF", font=("Consolas", 10))
        self.log_area.place(x=20, y=620)

        # --- Footer Navigation (Shared) ---
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(side="bottom", fill="x", pady=20, padx=20)

        self.back_btn = ctk.CTkLabel(self.footer_frame, text="<- Back", font=("Segoe UI", 12), text_color="#9CA3AF", cursor="hand2")
        self.back_btn.pack(side="left")
        self.back_btn.bind("<Button-1>", lambda e: self.navigate(-1))

        self.more_btn = ctk.CTkLabel(self.footer_frame, text="More ->", font=("Segoe UI", 12), text_color="#9CA3AF", cursor="hand2")
        self.more_btn.pack(side="right")
        self.more_btn.bind("<Button-1>", lambda e: self.navigate(1))

        self.current_page = 1
        self.show_page(1)

    def navigate(self, direction):
        self.current_page += direction
        if self.current_page < 1: self.current_page = 1
        if self.current_page > 3: self.current_page = 3
        self.show_page(self.current_page)

    def show_page(self, page_num):
        self.page1.pack_forget()
        self.page2.pack_forget()
        self.page3.pack_forget()

        if page_num == 1:
            self.page1.pack(fill="both", expand=True)
            self.back_btn.configure(text_color="#374151")
            self.more_btn.configure(text_color="#9CA3AF")
        elif page_num == 2:
            self.page2.pack(fill="both", expand=True)
            self.back_btn.configure(text_color="#9CA3AF")
            self.more_btn.configure(text_color="#9CA3AF")
        elif page_num == 3:
            self.page3.pack(fill="both", expand=True)
            self.back_btn.configure(text_color="#9CA3AF")
            self.more_btn.configure(text_color="#374151")

    def update_status(self, text, color="#6B7280"):
        # Streammode / Privacy Mode: Hide sensitive info
        if self.stream_mode.get() == 1:
            try:
                # Basic sanitization of username
                username = os.getlogin()
                if username and username.lower() in text.lower():
                    text = text.replace(username, "****")
                    text = text.replace(username.lower(), "****")
                    text = text.replace(username.upper(), "****")
            except: pass
            
        self.status_bar.configure(text=text, text_color=color)
        t = time.strftime("%H:%M:%S")
        self.log_area.insert("end", f"[{t}] {text}\n")
        self.log_area.see("end")

    def execute_cleanup(self, label, func):
        if not func: return
        btn = self.button_objects[label]
        original_text = btn.cget("text")
        btn.configure(text="Cleaning...", text_color="#FBBF24")
        self.update_status(f"Started: {label}", "#FBBF24")
        self.update_idletasks()
        
        def run():
            try:
                success = func()
                if success:
                    btn.configure(text="Success", text_color="#10B981")
                    self.update_status(f"Completed: {label}", "#10B981")
                else:
                    btn.configure(text="Failed", text_color="#EF4444")
                    self.update_status(f"Failed: {label}", "#EF4444")
            except Exception as e:
                btn.configure(text="Error", text_color="#EF4444")
                self.update_status(f"Error: {e}", "#EF4444")
            self.after(2000, lambda: btn.configure(text=original_text, text_color="#9CA3AF"))
        
        threading.Thread(target=run, daemon=True).start()

    def run_pid_wipe(self):
        pid = self.pid_entry.get().strip()
        if not pid:
            self.update_status("ERROR: Enter a valid PID first!", "#EF4444")
            return
        
        self.pid_wipe_btn.configure(state="disabled", text="WIPING...")
        self.update_status(f"Initializing Memory Wipe for PID {pid}...", "#3B82F6")
        
        def task():
            success, result = execute_memory_wipe(pid)
            if success:
                self.update_status(f"Memory Wipe Finished. Cleaned {result} strings.", "#10B981")
            else:
                self.update_status(f"Memory Wipe Failed: {result}", "#EF4444")
            self.pid_wipe_btn.configure(state="normal", text="PID WIPE")
        
        threading.Thread(target=task, daemon=True).start()

    def run_solara_scan(self):
        self.solara_btn.configure(state="disabled", text="SCANNING...")
        self.update_status("Deep Scan In Progress. Searching all drives...", "#3B82F6")
        
        def task():
            success, result = solara_deep_scan()
            if success:
                self.update_status(f"Deep Scan Finished. Removed {result} items.", "#10B981")
            else:
                self.update_status("Deep Scan Failed.", "#EF4444")
            self.solara_btn.configure(state="normal", text="SOLARA DEEP SCAN")
        
        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    app = StringCleanerApp()
    app.mainloop()
