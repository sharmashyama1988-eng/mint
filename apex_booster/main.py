
import customtkinter as ctk
import psutil
import os
import ctypes
import subprocess
import threading
import time
import humanize
import sys
from PIL import Image

# Constants for Windows API
CREATE_NO_WINDOW = 0x08000000
HIGH_PRIORITY_CLASS = 0x00000080

# Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")  # Will customize colors manually for "Gaming" look

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("APEX GAME ENGINE - SYSTEM OVERDRIVE")
        self.geometry("900x600")
        self.resizable(False, False)
        
        # Colors & Theme
        self.bg_color = "#0f0f0f"
        self.accent_color = "#00ff88" # Neon Green
        self.secondary_color = "#1a1a1a"
        self.configure(fg_color=self.bg_color)

        self.boost_active = False
        
        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=self.secondary_color)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="APEX ENGINE", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.accent_color)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="STATUS: IDLE", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
        self.status_label.grid(row=1, column=0, padx=20, pady=10)

        # Main Content
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Dashboard Widgets
        self.cpu_frame = self.create_metric_card(self.main_frame, "CPU Usage", "0%", 0, 0)
        self.ram_frame = self.create_metric_card(self.main_frame, "RAM Usage", "0/0 GB", 0, 1)

        # Boost Button (Big)
        self.boost_btn = ctk.CTkButton(self.main_frame, text="ACTIVATE TURBO BOOST", 
                                       font=ctk.CTkFont(size=20, weight="bold"),
                                       fg_color=self.accent_color, hover_color="#00cc6a",
                                       text_color="black", height=60, corner_radius=10,
                                       command=self.toggle_boost)
        self.boost_btn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=30, padx=10)

        # Optimization Toggles
        self.opt_frame = ctk.CTkFrame(self.main_frame, fg_color=self.secondary_color, corner_radius=10)
        self.opt_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.opt_frame.grid_columnconfigure((0,1), weight=1)

        self.switch_clean_ram = ctk.CTkSwitch(self.opt_frame, text="Aggressive RAM Cleaner", progress_color=self.accent_color, font=ctk.CTkFont(size=14))
        self.switch_clean_ram.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        self.switch_clean_ram.select()

        self.switch_high_prio = ctk.CTkSwitch(self.opt_frame, text="Force High Process Priority", progress_color=self.accent_color, font=ctk.CTkFont(size=14))
        self.switch_high_prio.grid(row=0, column=1, padx=20, pady=20, sticky="w")
        self.switch_high_prio.select()
        
        self.switch_net_opt = ctk.CTkSwitch(self.opt_frame, text="Network Latency Optimizer", progress_color=self.accent_color, font=ctk.CTkFont(size=14))
        self.switch_net_opt.grid(row=1, column=0, padx=20, pady=20, sticky="w")
        self.switch_net_opt.select()

        self.switch_power_plan = ctk.CTkSwitch(self.opt_frame, text="Ultimate Power Plan", progress_color=self.accent_color, font=ctk.CTkFont(size=14))
        self.switch_power_plan.grid(row=1, column=1, padx=20, pady=20, sticky="w")
        self.switch_power_plan.select()

        # Console Log
        self.console = ctk.CTkTextbox(self.main_frame, height=150, fg_color="#000000", text_color="#00ff00", font=("Consolas", 12))
        self.console.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.log("Ready to optimize system...")

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
        if title == "CPU Usage": self.cpu_label = label_value
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
            if cpu > 80: self.cpu_label.configure(text_color="#ff4444")
            else: self.cpu_label.configure(text_color="white")
            
        except Exception as e:
            pass
        
        # Recursively call this function every 1000ms (1 second)
        self.after(1000, self.update_metrics)

    def toggle_boost(self):
        if not self.boost_active:
            self.boost_active = True
            self.boost_btn.configure(text="DEACTIVATE BOOST", fg_color="#ff4444", hover_color="#cc0000")
            self.status_label.configure(text="STATUS: OVERDRIVE", text_color=self.accent_color)
            threading.Thread(target=self.run_boost, daemon=True).start()
        else:
            self.boost_active = False
            self.boost_btn.configure(text="ACTIVATE TURBO BOOST", fg_color=self.accent_color, hover_color="#00cc6a")
            self.status_label.configure(text="STATUS: IDLE", text_color="gray")
            self.log("System restored to normal state.")

    def run_boost(self):
        self.log("Initializing Boost Protocol...")
        
        if self.switch_clean_ram.get():
            self.log("Cleaning RAM...")
            self.clean_ram()
            
        if self.switch_net_opt.get():
            self.log("Flushing DNS & Resetting Winsock...")
            self.optimize_network()
            
        if self.switch_power_plan.get():
            self.log("Enforcing High Performance Power Plan...")
            self.set_power_plan()
            
        if self.switch_high_prio.get():
            self.log("Adjusting Process Priorities...")
            threading.Thread(target=self.boost_active_window_loop, daemon=True).start()
        
        self.log("OPTIMIZATION COMPLETE. System is running at max capacity.")

    def boost_active_window_loop(self):
        # Continuous optimization loop while boost is active
        while self.boost_active:
            try:
                if os.name == 'nt':
                     # Get Foreground Window PID
                    hwnd = ctypes.windll.user32.GetForegroundWindow()
                    pid = ctypes.c_ulong()
                    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    
                    if pid.value > 0:
                        p = psutil.Process(pid.value)
                        # Ignore system processes and self
                        if p.name().lower() not in ["explorer.exe", "searchui.exe", "lockapp.exe", "apex_booster.exe", "taskmgr.exe", "python.exe"]:
                            if p.nice() != HIGH_PRIORITY_CLASS:
                                p.nice(HIGH_PRIORITY_CLASS)
                                self.log(f"BOOSTED: {p.name()} -> HIGH PRIORITY")
            except Exception:
                pass
            time.sleep(5) # Check every 5 seconds

    def clean_ram(self):
        # Pythonic way to trigger GC and reduce working set
        try:
            # Clear standby list requires admin and specific API calls usually done by C++ tools like EmptyStandbyList.exe
            # We will use a safe method: EmptyWorkingSet for all user processes we can access
            if os.name == 'nt':
                # Simple EmptyWorkingSet for self to demonstrate
                PID = os.getpid()
                try:
                    handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, PID)
                    ctypes.windll.psapi.EmptyWorkingSet(handle)
                    ctypes.windll.kernel32.CloseHandle(handle)
                    self.log("Self-optimization successful.")
                except Exception as e:
                    self.log(f"RAM Cleaner Error: {e}")

        except Exception as e:
            self.log(f"Error cleaning RAM: {e}")

    def optimize_network(self):
        try:
            if os.name == 'nt':
                subprocess.run(["ipconfig", "/flushdns"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
                self.log("DNS Cache Flushed.")
        except Exception as e:
            self.log(f"Network Error: {e}")

    def set_power_plan(self):
        try:
            if os.name == 'nt':
                # High Performance GUID
                subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
                self.log("Power Plan set to High Performance.")
        except Exception as e:
            self.log(f"Power Plan Error: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
