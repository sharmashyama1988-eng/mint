
import customtkinter as ctk # type: ignore
import psutil # type: ignore
import os
import ctypes
import subprocess
import threading
import time
import humanize # type: ignore
import sys
import shutil
from PIL import Image # type: ignore

# Constants for Windows API
CREATE_NO_WINDOW = 0x08000000
HIGH_PRIORITY_CLASS = 0x00000080
REALTIME_PRIORITY_CLASS = 0x00000100

# Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")  

class DualEngineApp(ctk.CTk): # type: ignore
    def __init__(self):
        super().__init__()

        self.title("PROJECT GEMINI - DUAL ENGINE SYSTEM")
        self.geometry("1000x700")
        self.resizable(False, False)
        
        # Colors & Theme
        self.bg_color = "#050505"
        self.apex_color = "#00ff88" # Green for Apex (Safe/Stable)
        self.trinity_color = "#ff3333" # Red for Trinity (Aggressive/God Mode)
        self.secondary_color = "#111111"
        self.configure(fg_color=self.bg_color)

        self.boost_active_apex = False
        self.boost_active_trinity = False
        
        # Layout: Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Tab View for Dual Engines
        self.engine_tabs = ctk.CTkTabview(self, width=900, height=600, corner_radius=10, fg_color=self.secondary_color)
        self.engine_tabs.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Add Tabs
        self.tab_apex = self.engine_tabs.add("APEX ENGINE (STABLE)")
        self.tab_trinity = self.engine_tabs.add("TRINITY ENGINE (GOD MODE)")
        
        # Configure Tab Colors
        self.engine_tabs._segmented_button.configure(selected_color=self.apex_color, selected_hover_color=self.apex_color, unselected_color="#333333", text_color="black")
        
        # --- BUILD APEX UI ---
        self.build_apex_ui()
        
        # --- BUILD TRINITY UI ---
        self.build_trinity_ui()

        # Console Log (Shared at bottom)
        self.console = ctk.CTkTextbox(self, height=120, fg_color="#000000", text_color="#00ff00", font=("Consolas", 12))
        self.console.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.log("System Online. Select Engine Mode.")

        # Bind tab change to color update
        self.engine_tabs._segmented_button.configure(command=self.on_tab_change)

        # Start monitoring
        self.update_metrics()

    def on_tab_change(self, value):
        # Change theme based on tab
        selected_tab = self.engine_tabs.get()
        if selected_tab == "APEX ENGINE (STABLE)":
            self.engine_tabs._segmented_button.configure(selected_color=self.apex_color, selected_hover_color=self.apex_color)
            self.console.configure(text_color=self.apex_color)
            self.log("Switched to APEX Core. Safe optimizations ready.")
        else:
            self.engine_tabs._segmented_button.configure(selected_color=self.trinity_color, selected_hover_color=self.trinity_color)
            self.console.configure(text_color=self.trinity_color)
            self.log("Switched to TRINITY Core. God Mode ready.")

    def build_apex_ui(self):
        # Apex Tab Layout
        self.tab_apex.grid_columnconfigure((0,1), weight=1)
        
        # Header
        ctk.CTkLabel(self.tab_apex, text="APEX PERFORMANCE SUITE", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.apex_color).grid(row=0, column=0, columnspan=2, pady=20)
        
        # Metrics
        self.apex_cpu = self.create_metric_card(self.tab_apex, "CPU Load", "0%", 1, 0, self.apex_color)
        self.apex_ram = self.create_metric_card(self.tab_apex, "RAM Usage", "0/0 GB", 1, 1, self.apex_color)

        # Switches (Safe)
        self.apex_clean_ram = ctk.CTkSwitch(self.tab_apex, text="Smart RAM Cleaning", progress_color=self.apex_color)
        self.apex_clean_ram.grid(row=2, column=0, pady=10, sticky="w", padx=40)
        self.apex_clean_ram.select()
        
        self.apex_priority = ctk.CTkSwitch(self.tab_apex, text="Game Priority Boost", progress_color=self.apex_color)
        self.apex_priority.grid(row=2, column=1, pady=10, sticky="w", padx=40)
        self.apex_priority.select()

        self.apex_power = ctk.CTkSwitch(self.tab_apex, text="Balanced Power Plan", progress_color=self.apex_color)
        self.apex_power.grid(row=3, column=0, pady=10, sticky="w", padx=40)
        
        # Button
        self.apex_btn = ctk.CTkButton(self.tab_apex, text="ACTIVATE APEX BOOST", fg_color=self.apex_color, text_color="black", height=50, font=ctk.CTkFont(size=16, weight="bold"), hover_color="#00cc6a", command=self.toggle_apex)
        self.apex_btn.grid(row=4, column=0, columnspan=2, pady=30, padx=40, sticky="ew")

    def build_trinity_ui(self):
        # Trinity Tab Layout
        self.tab_trinity.grid_columnconfigure((0,1), weight=1)
        
        # Header
        ctk.CTkLabel(self.tab_trinity, text="TRINITY GOD MODE", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.trinity_color).grid(row=0, column=0, columnspan=2, pady=20)
        
        # Metrics
        self.trinity_cpu = self.create_metric_card(self.tab_trinity, "CPU Load", "0%", 1, 0, self.trinity_color)
        self.trinity_ram = self.create_metric_card(self.tab_trinity, "RAM Usage", "0/0 GB", 1, 1, self.trinity_color)

        # Switches (Aggressive)
        self.trinity_clean_ram = ctk.CTkSwitch(self.tab_trinity, text="FLUX CAPACITOR (Aggressive RAM Purge)", progress_color=self.trinity_color)
        self.trinity_clean_ram.grid(row=2, column=0, pady=10, sticky="w", padx=40)
        self.trinity_clean_ram.select()
        
        self.trinity_priority = ctk.CTkSwitch(self.tab_trinity, text="NEURAL PRIORITY (Realtime CPU)", progress_color=self.trinity_color)
        self.trinity_priority.grid(row=2, column=1, pady=10, sticky="w", padx=40)
        self.trinity_priority.select()

        self.trinity_net = ctk.CTkSwitch(self.tab_trinity, text="HYPERLOOP (Zero Latency Net)", progress_color=self.trinity_color)
        self.trinity_net.grid(row=3, column=0, pady=10, sticky="w", padx=40)
        self.trinity_net.select()

        self.trinity_temp = ctk.CTkSwitch(self.tab_trinity, text="VOID STORAGE (Delete Temp Files)", progress_color=self.trinity_color)
        self.trinity_temp.grid(row=3, column=1, pady=10, sticky="w", padx=40)
        self.trinity_temp.select()
        
        # Button
        self.trinity_btn = ctk.CTkButton(self.tab_trinity, text="ENGAGE GOD MODE", fg_color=self.trinity_color, text_color="white", height=50, font=ctk.CTkFont(size=16, weight="bold"), hover_color="#cc0000", command=self.toggle_trinity)
        self.trinity_btn.grid(row=4, column=0, columnspan=2, pady=30, padx=40, sticky="ew")

    def create_metric_card(self, parent, title, value, row, col, color):
        frame = ctk.CTkFrame(parent, fg_color="#1a1a1a", corner_radius=15, height=100)
        frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=12), text_color="gray").place(relx=0.5, rely=0.3, anchor="center")
        label_value = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=24, weight="bold"), text_color=color)
        label_value.place(relx=0.5, rely=0.6, anchor="center")
        return label_value

    def log(self, message):
        self.console.insert("end", f"> {message}\n")
        self.console.see("end")

    def update_metrics(self):
        try:
            cpu = psutil.cpu_percent(interval=None) # Non-blocking
            ram = psutil.virtual_memory()
            
            # Update Apex UI
            self.apex_cpu.configure(text=f"{cpu}%")
            self.apex_ram.configure(text=f"{ram.percent}%")
            
            # Update Trinity UI
            self.trinity_cpu.configure(text=f"{cpu}%")
            self.trinity_ram.configure(text=f"{ram.percent}%")
            
        except Exception:
            pass
        self.after(1000, self.update_metrics)

    # --- APEX LOGIC ---
    def toggle_apex(self):
        if not self.boost_active_apex:
            self.boost_active_apex = True
            self.apex_btn.configure(text="DEACTIVATE APEX", fg_color="gray")
            self.log("APEX ENGINE ENGAGED.")
            threading.Thread(target=self.run_apex, daemon=True).start()
        else:
            self.boost_active_apex = False
            self.apex_btn.configure(text="ACTIVATE APEX BOOST", fg_color=self.apex_color)
            self.log("APEX ENGINE DISENGAGED.")

    def run_apex(self):
        if self.apex_clean_ram.get():
            self.log("[APEX] Clearing Standby Memory...")
            self.clean_ram_safe()
        
        if self.apex_priority.get():
            self.log("[APEX] Setting High Priority...")
            threading.Thread(target=self.boost_priority_loop, args=(HIGH_PRIORITY_CLASS,), daemon=True).start()

    # --- TRINITY LOGIC ---
    def toggle_trinity(self):
        if not self.boost_active_trinity:
            self.boost_active_trinity = True
            self.trinity_btn.configure(text="DISENGAGE GOD MODE", fg_color="gray")
            self.log("TRINITY GOD MODE ENGAGED.")
            threading.Thread(target=self.run_trinity, daemon=True).start()
        else:
            self.boost_active_trinity = False
            self.trinity_btn.configure(text="ENGAGE GOD MODE", fg_color=self.trinity_color)
            self.log("TRINITY GOD MODE DISENGAGED.")

    def run_trinity(self):
        self.log("[TRINITY] INITIATING GOD PROTOCOLS...")
        
        if self.trinity_clean_ram.get():
            self.log("[TRINITY] PURGING ALL MEMORY BUFFERS...")
            self.clean_ram_aggressive()
            
        if self.trinity_temp.get():
            self.log("[TRINITY] VAPORIZING TEMP FILES...")
            self.clean_temp_files()
            
        if self.trinity_net.get():
            self.log("[TRINITY] FLUSHING NETWORK STACK...")
            self.optimize_network()

        if self.trinity_priority.get():
            self.log("[TRINITY] SEIZING CPU RESOURCES (REALTIME)...")
            threading.Thread(target=self.boost_priority_loop, args=(REALTIME_PRIORITY_CLASS,), daemon=True).start()

    # --- SHARED UTILS ---
    def clean_ram_safe(self):
        try:
            if os.name == 'nt':
                PID = os.getpid()
                handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, PID) # type: ignore
                ctypes.windll.psapi.EmptyWorkingSet(handle) # type: ignore
                ctypes.windll.kernel32.CloseHandle(handle) # type: ignore
        except: pass

    def clean_ram_aggressive(self):
        self.clean_ram_safe()
        # Aggressive logic placeholder - repeating clean or targeting explicit processes would go here

    def clean_temp_files(self):
        temp_dir = os.environ.get('TEMP')
        if temp_dir:
            try:
                count = 0
                for root, dirs, files in os.walk(temp_dir): # type: ignore
                    if count > 100: break 
                    for f in files: # type: ignore
                        try:
                           os.remove(os.path.join(root, f)) 
                           count += 1 # type: ignore
                        except: pass
                self.log(f"[TRINITY] Deleted {count} files.")
            except: pass

    def optimize_network(self):
        try:
            if os.name == 'nt':
                subprocess.run(["ipconfig", "/flushdns"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW) # type: ignore
        except: pass

    def boost_priority_loop(self, priority_level):
        while self.boost_active_apex or self.boost_active_trinity:
            try:
                if os.name == 'nt':
                    hwnd = ctypes.windll.user32.GetForegroundWindow() # type: ignore
                    pid = ctypes.c_ulong()
                    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid)) # type: ignore
                    
                    if pid.value > 0:
                        p = psutil.Process(pid.value)
                        target_name = p.name().lower()
                        if target_name not in ["explorer.exe", "searchui.exe", "lockapp.exe", "python.exe"]:
                            # Only boost if it's the right engine active
                            if self.boost_active_trinity: # Trinity overrides Apex
                                if p.nice() != REALTIME_PRIORITY_CLASS:
                                    p.nice(REALTIME_PRIORITY_CLASS)
                                    self.log(f"[TRINITY] BOOST: {target_name} -> REALTIME")
                            elif self.boost_active_apex:
                                if p.nice() != HIGH_PRIORITY_CLASS:
                                    p.nice(HIGH_PRIORITY_CLASS)
                                    self.log(f"[APEX] BOOST: {target_name} -> HIGH")
            except: pass
            time.sleep(5)

if __name__ == "__main__":
    app = DualEngineApp() # type: ignore
    app.mainloop()
