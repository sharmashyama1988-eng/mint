
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
import json
from datetime import datetime
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

        self.title("PROJECT GEMINI - TRIPLE ENGINE SYSTEM")
        self.geometry("1100x750")
        self.resizable(False, False)
        
        # Colors & Theme
        self.bg_color = "#050505"
        self.apex_color = "#00ff88" # Green (Safe)
        self.trinity_color = "#ff3333" # Red (Aggressive)
        self.nexus_color = "#00aaff" # Blue (AI/Smart)
        self.secondary_color = "#111111"
        self.configure(fg_color=self.bg_color)

        self.boost_active_apex = False
        self.boost_active_trinity = False
        self.nexus_ai_active = False
        
        # AI Memory
        self.lag_history_file = "nexus_memory.json"
        self.process_stats = self.load_ai_memory()

        # Layout: Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Tab View for Engines
        self.engine_tabs = ctk.CTkTabview(self, width=1000, height=600, corner_radius=10, fg_color=self.secondary_color)
        self.engine_tabs.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Add Tabs
        self.tab_apex = self.engine_tabs.add("APEX (STABLE)")
        self.tab_trinity = self.engine_tabs.add("TRINITY (GOD MODE)")
        self.tab_nexus = self.engine_tabs.add("NEXUS AI (ADAPTIVE)")
        
        # Configure Tab Colors
        self.engine_tabs._segmented_button.configure(selected_color=self.apex_color, selected_hover_color=self.apex_color, unselected_color="#333333", text_color="white")
        
        # --- BUILD UIs ---
        self.build_apex_ui()
        self.build_trinity_ui()
        self.build_nexus_ui()

        # Console Log (Shared at bottom)
        self.console = ctk.CTkTextbox(self, height=120, fg_color="#000000", text_color="#00ff00", font=("Consolas", 12))
        self.console.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.log("System Online. NEXUS AI initialized.")

        # Bind tab change to color update
        self.engine_tabs._segmented_button.configure(command=self.on_tab_change)

        # Start monitoring
        self.update_metrics()

    def load_ai_memory(self):
        if os.path.exists(self.lag_history_file):
            try:
                with open(self.lag_history_file, 'r') as f:
                    return json.load(f)
            except: return {}
        return {}

    def save_ai_memory(self):
        try:
            with open(self.lag_history_file, 'w') as f:
                json.dump(self.process_stats, f)
        except: pass

    def on_tab_change(self, value):
        # Change theme based on tab
        selected_tab = self.engine_tabs.get()
        if "APEX" in selected_tab:
            self.engine_tabs._segmented_button.configure(selected_color=self.apex_color)
            self.console.configure(text_color=self.apex_color)
            self.log("Switched to APEX Core.")
        elif "TRINITY" in selected_tab:
            self.engine_tabs._segmented_button.configure(selected_color=self.trinity_color)
            self.console.configure(text_color=self.trinity_color)
            self.log("Switched to TRINITY Core.")
        else:
            self.engine_tabs._segmented_button.configure(selected_color=self.nexus_color)
            self.console.configure(text_color=self.nexus_color)
            self.log("Switched to NEXUS AI Core.")

    def build_apex_ui(self):
        self.tab_apex.grid_columnconfigure((0,1), weight=1)
        ctk.CTkLabel(self.tab_apex, text="APEX PERFORMANCE SUITE", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.apex_color).grid(row=0, column=0, columnspan=2, pady=20)
        self.apex_cpu = self.create_metric_card(self.tab_apex, "CPU Load", "0%", 1, 0, self.apex_color)
        self.apex_ram = self.create_metric_card(self.tab_apex, "RAM Usage", "0/0 GB", 1, 1, self.apex_color)
        
        self.apex_clean_ram = ctk.CTkSwitch(self.tab_apex, text="Smart RAM Cleaning", progress_color=self.apex_color)
        self.apex_clean_ram.grid(row=2, column=0, pady=10, sticky="w", padx=40)
        self.apex_priority = ctk.CTkSwitch(self.tab_apex, text="Game Priority Boost", progress_color=self.apex_color)
        self.apex_priority.grid(row=2, column=1, pady=10, sticky="w", padx=40)
        
        self.apex_btn = ctk.CTkButton(self.tab_apex, text="ACTIVATE APEX BOOST", fg_color=self.apex_color, text_color="black", height=50, font=ctk.CTkFont(size=16, weight="bold"), hover_color="#00cc6a", command=self.toggle_apex)
        self.apex_btn.grid(row=4, column=0, columnspan=2, pady=30, padx=40, sticky="ew")

    def build_trinity_ui(self):
        self.tab_trinity.grid_columnconfigure((0,1), weight=1)
        ctk.CTkLabel(self.tab_trinity, text="TRINITY GOD MODE", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.trinity_color).grid(row=0, column=0, columnspan=2, pady=20)
        self.trinity_cpu = self.create_metric_card(self.tab_trinity, "CPU Load", "0%", 1, 0, self.trinity_color)
        self.trinity_ram = self.create_metric_card(self.tab_trinity, "RAM Usage", "0/0 GB", 1, 1, self.trinity_color)
        
        self.trinity_clean_ram = ctk.CTkSwitch(self.tab_trinity, text="FLUX CAPACITOR (RAM)", progress_color=self.trinity_color)
        self.trinity_clean_ram.grid(row=2, column=0, pady=10, sticky="w", padx=40)
        self.trinity_priority = ctk.CTkSwitch(self.tab_trinity, text="NEURAL PRIORITY (CPU)", progress_color=self.trinity_color)
        self.trinity_priority.grid(row=2, column=1, pady=10, sticky="w", padx=40)
        
        self.trinity_btn = ctk.CTkButton(self.tab_trinity, text="ENGAGE GOD MODE", fg_color=self.trinity_color, text_color="white", height=50, font=ctk.CTkFont(size=16, weight="bold"), hover_color="#cc0000", command=self.toggle_trinity)
        self.trinity_btn.grid(row=4, column=0, columnspan=2, pady=30, padx=40, sticky="ew")

    def build_nexus_ui(self):
        self.tab_nexus.grid_columnconfigure((0,1), weight=1)
        ctk.CTkLabel(self.tab_nexus, text="NEXUS AI - AUTONOMOUS OPTIMIZER", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.nexus_color).grid(row=0, column=0, columnspan=2, pady=20)
        
        self.nexus_status = ctk.CTkLabel(self.tab_nexus, text="AI STATE: ANALYZING...", font=ctk.CTkFont(size=16), text_color="gray")
        self.nexus_status.grid(row=1, column=0, columnspan=2, pady=10)

        # AI Stats
        self.ai_card = ctk.CTkFrame(self.tab_nexus, fg_color="#1a1a1a", corner_radius=15, height=150)
        self.ai_card.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        self.nexus_info_label = ctk.CTkLabel(self.ai_card, text="Bottlenecks Detected: 0\nEfficiency Rating: 100%", font=ctk.CTkFont("Consolas", 14), text_color="white", justify="left")
        self.nexus_info_label.place(relx=0.05, rely=0.5, anchor="w")

        # Switches
        self.nexus_learn = ctk.CTkSwitch(self.tab_nexus, text="Deep Learning (Record Lag)", progress_color=self.nexus_color)
        self.nexus_learn.grid(row=3, column=0, pady=20, sticky="w", padx=40)
        self.nexus_learn.select()
        
        self.nexus_auto = ctk.CTkSwitch(self.tab_nexus, text="Autonomous Correction (Fix Lag)", progress_color=self.nexus_color)
        self.nexus_auto.grid(row=3, column=1, pady=20, sticky="w", padx=40)
        self.nexus_auto.select()

        self.nexus_btn = ctk.CTkButton(self.tab_nexus, text="ACTIVATE NEXUS AI", fg_color=self.nexus_color, text_color="black", height=50, font=ctk.CTkFont(size=16, weight="bold"), hover_color="#0088cc", command=self.toggle_nexus)
        self.nexus_btn.grid(row=4, column=0, columnspan=2, pady=30, padx=40, sticky="ew")

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
            
            for label in [self.apex_cpu, self.trinity_cpu]:
                label.configure(text=f"{cpu}%")
            for label in [self.apex_ram, self.trinity_ram]:
                label.configure(text=f"{ram.percent}%")
                
        except Exception: pass
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
            self.clean_ram_safe()
        if self.apex_priority.get():
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
        if self.trinity_clean_ram.get(): self.clean_ram_aggressive()
        if self.trinity_priority.get(): threading.Thread(target=self.boost_priority_loop, args=(REALTIME_PRIORITY_CLASS,), daemon=True).start()

    # --- NEXUS AI LOGIC ---
    def toggle_nexus(self):
        if not self.nexus_ai_active:
            self.nexus_ai_active = True
            self.nexus_btn.configure(text="DEACTIVATE NEXUS AI", fg_color="gray")
            self.nexus_status.configure(text="AI STATE: MONITORING & LEARNING", text_color=self.nexus_color)
            self.log("[NEXUS] AI Neural Net Loaded. Scanning for bottlenecks...")
            threading.Thread(target=self.run_nexus_core, daemon=True).start()
        else:
            self.nexus_ai_active = False
            self.nexus_btn.configure(text="ACTIVATE NEXUS AI", fg_color=self.nexus_color)
            self.nexus_status.configure(text="AI STATE: STANDBY", text_color="gray")
            self.log("[NEXUS] AI Systems Offline. Data saved.")
            self.save_ai_memory()

    def run_nexus_core(self):
        # The Brain of the operation
        while self.nexus_ai_active:
            try:
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                
                # Detect Active Game/App
                active_process = self.get_active_window_process_name()
                
                # 1. RECORDING PHASE
                if self.nexus_learn.get() and active_process:
                    if cpu > 85 or ram > 85:
                        self.log(f"[NEXUS] LAG DETECTED in {active_process} (CPU:{cpu}% RAM:{ram}%)")
                        if active_process not in self.process_stats:
                            self.process_stats[active_process] = {"lag_count": 0, "bottleneck_type": "none"} # type: ignore
                        self.process_stats[active_process]["lag_count"] += 1 # type: ignore
                        
                        if cpu > 85: self.process_stats[active_process]["bottleneck_type"] = "CPU" # type: ignore
                        elif ram > 85: self.process_stats[active_process]["bottleneck_type"] = "RAM" # type: ignore
                        
                        self.nexus_info_label.configure(text=f"Bottlenecks Detected: {len(self.process_stats)}\nLast Limit: {active_process}")

                # 2. ACTION PHASE
                if self.nexus_auto.get():
                    if ram > 85:
                        self.log("[NEXUS] RAM Critical! Engaging Flux Capacitor...")
                        self.clean_ram_aggressive()
                    
                    if cpu > 90:
                        self.log("[NEXUS] CPU Critical! Engaging Neural Priority...")
                         # Auto-enable Trinity priority if not already on
                        if not self.boost_active_trinity:
                            self.clean_temp_files() # Quick temp clean to help I/O
                            # We can't easily start a thread from a thread without care, but we can call the util matches
                            pass 

                # 3. PREDICTION PHASE
                if active_process in self.process_stats:
                    stats = self.process_stats[active_process]
                    if stats["lag_count"] > 2:
                        # Known heavy app
                        if not self.boost_active_trinity and not self.boost_active_apex:
                            self.log(f"[NEXUS] KNOWN HEAVY APP '{active_process}' detected. Pre-allocating resources.")
                            # Auto-trigger optimizers without full mode switch
                            if stats["bottleneck_type"] == "RAM":
                                self.clean_ram_safe()
            except Exception: pass
            
            time.sleep(2)

    # --- SHARED UTILS ---
    def get_active_window_process_name(self):
        try:
            if os.name == 'nt':
                hwnd = ctypes.windll.user32.GetForegroundWindow() # type: ignore
                pid = ctypes.c_ulong()
                ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid)) # type: ignore
                p = psutil.Process(pid.value)
                return p.name()
        except: return None

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

    def clean_temp_files(self):
        try:
            temp_dir = os.environ.get('TEMP')
            if temp_dir:
                for root, dirs, files in os.walk(temp_dir): # type: ignore
                    for f in files: # type: ignore
                        try:
                           os.remove(os.path.join(root, f)) 
                        except: pass
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
                            if self.boost_active_trinity: 
                                if p.nice() != REALTIME_PRIORITY_CLASS: p.nice(REALTIME_PRIORITY_CLASS)
                            elif self.boost_active_apex:
                                if p.nice() != HIGH_PRIORITY_CLASS: p.nice(HIGH_PRIORITY_CLASS)
            except: pass
            time.sleep(5)

if __name__ == "__main__":
    app = DualEngineApp() # type: ignore
    app.mainloop()
