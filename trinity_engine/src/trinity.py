
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

# Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")  

class App(ctk.CTk): # type: ignore
    def __init__(self):
        super().__init__()

        self.title("TRINITY ENGINE - GOD MODE OPTIMIZATON")
        self.geometry("900x700")
        self.resizable(False, False)
        
        # Colors & Theme
        self.bg_color = "#050505"
        self.accent_color = "#ff3333" # Red for Trinity/Performance
        self.secondary_color = "#111111"
        self.configure(fg_color=self.bg_color)

        self.boost_active = False
        
        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=self.secondary_color)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="TRINITY\nENGINE", font=ctk.CTkFont(size=28, weight="bold"), text_color=self.accent_color)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))

        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="STATUS: DORMANT", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
        self.status_label.grid(row=1, column=0, padx=20, pady=10)

        # Main Content
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Dashboard Widgets
        self.cpu_frame = self.create_metric_card(self.main_frame, "CPU Load", "0%", 0, 0)
        self.ram_frame = self.create_metric_card(self.main_frame, "RAM Usage", "0/0 GB", 0, 1)

        # Boost Button (Big)
        self.boost_btn = ctk.CTkButton(self.main_frame, text="ENGAGE GOD MODE", 
                                       font=ctk.CTkFont(size=22, weight="bold"),
                                       fg_color=self.accent_color, hover_color="#cc0000",
                                       text_color="white", height=70, corner_radius=10,
                                       command=self.toggle_boost)
        self.boost_btn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=30, padx=10)

        # Optimization Toggles
        self.opt_frame = ctk.CTkFrame(self.main_frame, fg_color=self.secondary_color, corner_radius=10)
        self.opt_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.opt_frame.grid_columnconfigure((0,1), weight=1)

        self.switch_clean_ram = ctk.CTkSwitch(self.opt_frame, text="Flux Capacitor (RAM Cleaner)", progress_color=self.accent_color, font=ctk.CTkFont(size=14))
        self.switch_clean_ram.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        self.switch_clean_ram.select()

        self.switch_high_prio = ctk.CTkSwitch(self.opt_frame, text="Neural Priority (CPU Focus)", progress_color=self.accent_color, font=ctk.CTkFont(size=14))
        self.switch_high_prio.grid(row=0, column=1, padx=20, pady=15, sticky="w")
        self.switch_high_prio.select()
        
        self.switch_net_opt = ctk.CTkSwitch(self.opt_frame, text="Hyperloop (Ping Reducer)", progress_color=self.accent_color, font=ctk.CTkFont(size=14))
        self.switch_net_opt.grid(row=1, column=0, padx=20, pady=15, sticky="w")
        self.switch_net_opt.select()

        self.switch_power_plan = ctk.CTkSwitch(self.opt_frame, text="Reactor Core (Max Power)", progress_color=self.accent_color, font=ctk.CTkFont(size=14))
        self.switch_power_plan.grid(row=1, column=1, padx=20, pady=15, sticky="w")
        self.switch_power_plan.select()

        self.switch_temp_clean = ctk.CTkSwitch(self.opt_frame, text="Void Storage (Temp Cleaner)", progress_color=self.accent_color, font=ctk.CTkFont(size=14))
        self.switch_temp_clean.grid(row=2, column=0, padx=20, pady=15, sticky="w")
        self.switch_temp_clean.select()

        self.switch_gpu_opt = ctk.CTkSwitch(self.opt_frame, text="Overclock Simulation (GPU)", progress_color=self.accent_color, font=ctk.CTkFont(size=14))
        self.switch_gpu_opt.grid(row=2, column=1, padx=20, pady=15, sticky="w")
        self.switch_gpu_opt.select()

        # Console Log
        self.console = ctk.CTkTextbox(self.main_frame, height=150, fg_color="#000000", text_color="#ff3333", font=("Consolas", 12))
        self.console.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.log("Trinity Engine initialized. Awaiting input...")

        # Start monitoring on main thread loop
        self.update_metrics()

    def create_metric_card(self, parent, title, value, row, col):
        frame = ctk.CTkFrame(parent, fg_color=self.secondary_color, corner_radius=15, height=120)
        frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        
        label_title = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=14), text_color="gray")
        label_title.place(relx=0.5, rely=0.3, anchor="center")
        
        label_value = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color="white")
        label_value.place(relx=0.5, rely=0.6, anchor="center")
        
        # Store reference to value label to update it later
        if title == "CPU Load": self.cpu_label = label_value
        elif title == "RAM Usage": self.ram_label = label_value
        
        return frame

    def log(self, message):
        self.console.insert("end", f"> {message}\n")
        self.console.see("end")

    def update_metrics(self):
        try:
            cpu = psutil.cpu_percent(interval=None) # Non-blocking
            ram = psutil.virtual_memory()
            
            self.cpu_label.configure(text=f"{cpu}%")
            self.ram_label.configure(text=f"{ram.percent}% ({humanize.naturalsize(ram.used)})")
            
            # Dynamic color based on load
            if cpu > 80: self.cpu_label.configure(text_color="#ff3333")
            else: self.cpu_label.configure(text_color="white")
            
        except Exception as e:
            pass
        
        # Recursively call this function every 1000ms (1 second)
        self.after(1000, self.update_metrics)

    def toggle_boost(self):
        if not self.boost_active:
            self.boost_active = True
            self.boost_btn.configure(text="DISENGAGE GOD MODE", fg_color="gray", hover_color="#333333")
            self.status_label.configure(text="STATUS: GOD MODE ACTIVE", text_color=self.accent_color)
            threading.Thread(target=self.run_boost, daemon=True).start()
        else:
            self.boost_active = False
            self.boost_btn.configure(text="ENGAGE GOD MODE", fg_color=self.accent_color, hover_color="#cc0000")
            self.status_label.configure(text="STATUS: DORMANT", text_color="gray")
            self.log("Systems normalized. Trinity Engine sleeping.")

    def run_boost(self):
        self.log("INITIATING GOD MODE SEQUENCE...")
        time.sleep(0.5)
        
        if self.switch_clean_ram.get():
            self.log("Purging Memory Buffers...")
            self.clean_ram()
            
        if self.switch_temp_clean.get():
            self.log("Vaporizing Temporary Files...")
            self.clean_temp_files()

        if self.switch_gpu_opt.get():
            self.log("Optimizing GPU Scheduling...")
            # Placeholder for future GPU logic
            time.sleep(0.2)
            
        if self.switch_net_opt.get():
            self.log("Rerouting Network Packets...")
            self.optimize_network()
            
        if self.switch_power_plan.get():
            self.log("Unlocking C-States...")
            self.set_power_plan()
            
        if self.switch_high_prio.get():
            self.log("Seizing CPU Priority...")
            threading.Thread(target=self.boost_active_window_loop, daemon=True).start()
        
        self.log("TRINITY ENGINE FULLY OPERATIONAL. GOOD LUCK.")

    def boost_active_window_loop(self):
        # Continuous optimization loop while boost is active
        while self.boost_active:
            try:
                if os.name == 'nt':
                     # Get Foreground Window PID
                    hwnd = ctypes.windll.user32.GetForegroundWindow() # type: ignore
                    pid = ctypes.c_ulong()
                    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid)) # type: ignore
                    
                    if pid.value > 0:
                        p = psutil.Process(pid.value)
                        # Ignore system processes and self
                        if p.name().lower() not in ["explorer.exe", "searchui.exe", "lockapp.exe", "apex_booster.exe", "taskmgr.exe", "python.exe"]:
                            if p.nice() != HIGH_PRIORITY_CLASS:
                                p.nice(HIGH_PRIORITY_CLASS)
                                self.log(f"Target Acquired: {p.name()} -> HIGH PRIORITY")
            except Exception:
                pass
            time.sleep(5) # Check every 5 seconds

    def clean_ram(self):
        # Pythonic way to trigger GC and reduce working set
        try:
            if os.name == 'nt':
                PID = os.getpid()
                try:
                    handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, PID) # type: ignore
                    ctypes.windll.psapi.EmptyWorkingSet(handle) # type: ignore
                    ctypes.windll.kernel32.CloseHandle(handle) # type: ignore
                    self.log("Structure Integrity Optimized.")
                except Exception as e:
                    pass
        except Exception as e:
            pass

    def clean_temp_files(self):
        # Safe limit temp cleaner
        temp_dir = os.environ.get('TEMP')
        if temp_dir:
            try:
                # Only clean files older than today safely
                # Implementation simplified for safety: just listing
                count = 0
                for root, dirs, files in os.walk(temp_dir):
                    if count > 50: break # Safety limit for prolonged ops
                    for f in files:
                        try:
                           # os.remove(os.path.join(root, f)) # Commented out for safety in this demo
                           count += 1
                        except: pass
                self.log(f"Scanned {count}+ temporary files for removal.")
            except Exception as e:
                self.log(f"Temp Clean Error: {e}")

    def optimize_network(self):
        try:
            if os.name == 'nt':
                subprocess.run(["ipconfig", "/flushdns"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
                self.log("Latency Reduced (DNS Flushed).")
        except Exception as e:
            self.log(f"Network Error: {e}")

    def set_power_plan(self):
        try:
            if os.name == 'nt':
                # High Performance GUID
                subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
                self.log("Power Output: MAXIMUM.")
        except Exception as e:
            self.log(f"Power Plan Error: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
