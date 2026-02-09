
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
import logging
import platform
import pystray # type: ignore
from PIL import Image, ImageDraw # type: ignore
from datetime import datetime

# Windows API Constants
CREATE_NO_WINDOW = 0x08000000
HIGH_PRIORITY_CLASS = 0x00000080
REALTIME_PRIORITY_CLASS = 0x00000100

# App Config
HOME_DIR = os.getcwd()
LOG_FILE = "quantum_logs.txt"
AI_MEMORY_FILE = "nexus_quantum_memory.json"
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Setup Logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

class QuantumUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QUANTUM NEXUS - HYPERVISOR")
        self.geometry("1100x700")
        self.resizable(False, False)
        
        # Theme: Midnight Cyber
        self.bg_color = "#050505"
        self.sidebar_color = "#0a0a0a"
        self.accent_color = "#00ddee" # Quantum Blue
        self.danger_color = "#ff3333" # Critical Red
        self.success_color = "#00ff88" # Stable Green
        self.configure(fg_color=self.bg_color)

        # Core Engines
        self.titan = TitanHardwareCore()
        self.nexus = NexusHiveMind(self.titan)
        self.is_minimized = False
        
        # GUI Structure
        self.grid_columnconfigure(0, weight=1) # Full width for boot
        self.grid_rowconfigure(0, weight=1)

        # Boot Screen (Initial State)
        self.boot_frame = ctk.CTkFrame(self, fg_color=self.bg_color)
        self.boot_frame.grid(row=0, column=0, sticky="nsew")
        self.boot_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.boot_label = ctk.CTkLabel(self.boot_frame, text="INITIALIZING QUANTUM CORE...", font=ctk.CTkFont(size=20, weight="bold"), text_color=self.accent_color)
        self.boot_label.pack(pady=20)
        
        self.boot_progress = ctk.CTkProgressBar(self.boot_frame, width=400, height=4, progress_color=self.accent_color)
        self.boot_progress.pack(pady=10)
        self.boot_progress.set(0)

        self.sidebar = None # Delayed init
        self.main_frame = None

        # Start Boot Animation
        self.after(500, self.run_boot_sequence)

        # Core Engines (Background)
        self.titan = TitanHardwareCore()
        self.nexus = NexusHiveMind(self.titan)
        self.is_minimized = False
        
        self.tray_icon = self.setup_tray()
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

    def run_boot_sequence(self):
        # Fake loading steps
        steps = [
            (0.2, "LOADING TITAN MODULES..."),
            (0.4, "SCANNIG HARDWARE ID..."),
            (0.6, "CONNECTING TO NEXUS HIVE..."),
            (0.8, "CALIBRATING DEFENSE SYSTEMS..."),
            (1.0, "SYSTEM READY.")
        ]
        self.animate_boot(steps, 0)

    def animate_boot(self, steps, index):
        if index < len(steps):
            progress, text = steps[index]
            self.boot_label.configure(text=text)
            self.boot_progress.set(progress)
            self.after(600, lambda: self.animate_boot(steps, index + 1))
        else:
            self.boot_frame.destroy()
            self.init_main_interface()

    def init_main_interface(self):
        # Restore Grid
        self.grid_columnconfigure(0, weight=0) # Sidebar width
        self.grid_columnconfigure(1, weight=1) # Main width
        
        self.setup_sidebar()
        self.setup_main_area()
        
        # Auto-Scan
        self.titan.scan_hardware()
        self.update_hardware_info()
        self.update_live_feed()

    # ... (Tray methods remain the same) ...

    # --- DASHBOARD UI ---
    def build_dashboard(self):
        ctk.CTkLabel(self.page_dashboard, text="SYSTEM OVERVIEW", font=ctk.CTkFont(size=24, weight="bold"), text_color="white").pack(anchor="w", pady=(0, 20))
        
        # Stats Row
        stats_frame = ctk.CTkFrame(self.page_dashboard, fg_color="transparent")
        stats_frame.pack(fill="x", pady=10)
        
        self.dash_cpu_bar = self.create_visual_stat_card(stats_frame, "CPU LOAD", "0%", self.danger_color)
        self.dash_cpu_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.dash_ram_bar = self.create_visual_stat_card(stats_frame, "RAM USAGE", "0%", self.accent_color)
        self.dash_ram_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.dash_ai_state = self.create_visual_stat_card(stats_frame, "AI ACTIVITY", "IDLE", self.success_color, is_bar=False)
        self.dash_ai_state.pack(side="left", fill="x", expand=True)

        # Quick Actions
        ctk.CTkLabel(self.page_dashboard, text="QUICK PROTOCOLS", font=ctk.CTkFont(size=18, weight="bold"), text_color="gray").pack(anchor="w", pady=(30, 10))
        
        # Notification Area
        self.dash_notify = ctk.CTkLabel(self.page_dashboard, text="", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.accent_color)
        self.dash_notify.pack(anchor="w", pady=(0, 5))

        action_frame = ctk.CTkFrame(self.page_dashboard, fg_color="transparent")
        action_frame.pack(fill="x")
        
        ctk.CTkButton(action_frame, text="FLUSH MEMORY", height=50, fg_color="#333333", hover_color=self.accent_color, command=lambda: self.run_action(self.nexus.force_ram_clean, "Flushing Memory...")).pack(fill="x", pady=5)
        ctk.CTkButton(action_frame, text="NETWORK RESET", height=50, fg_color="#333333", hover_color=self.accent_color, command=lambda: self.run_action(self.nexus.optimize_network, "Resetting Network...")).pack(fill="x", pady=5)

    def create_visual_stat_card(self, parent, title, value, color, is_bar=True):
        frame = ctk.CTkFrame(parent, fg_color="#1a1a1a", height=120)
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(15, 5))
        lbl = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        lbl.pack(pady=(0, 5))
        
        if is_bar:
            bar = ctk.CTkProgressBar(frame, width=150, height=6, progress_color=color)
            bar.pack(pady=(5, 15))
            bar.set(0)
            lbl.bar_ref = bar # Attach reference
        
        return lbl 

    # ... (Titan/Nexus UI methods unchanged, logic below needs update for bars) ...

    def update_live_feed(self):
        # UI Updates
        try:
             # CPU/RAM
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            
            # Update Text
            self.dash_cpu_bar.configure(text=f"{cpu}%")
            self.dash_cpu_bar.configure(text_color=self.danger_color if cpu > 90 else "white")
            if hasattr(self.dash_cpu_bar, 'bar_ref'): self.dash_cpu_bar.bar_ref.set(cpu / 100) # Update Bar
            
            self.dash_ram_bar.configure(text=f"{ram.percent}%")
            self.dash_ram_bar.configure(text_color=self.danger_color if ram.percent > 90 else "white")
            if hasattr(self.dash_ram_bar, 'bar_ref'): self.dash_ram_bar.bar_ref.set(ram.percent / 100) # Update Bar
            
            # AI State
            state = "ACTIVE" if self.nexus.is_active else "IDLE"
            self.dash_ai_state.configure(text=state)
            self.dash_ai_state.configure(text_color=self.success_color if self.nexus.is_active else "gray")

            # Check Nexus Feed
            while not self.nexus.msg_queue.empty():
                msg = self.nexus.msg_queue.get_nowait()
                self.log_nexus(msg)

        except: pass
        
        self.after(1000, self.update_live_feed)

# --- ENGINE 1: TITAN HARDWARE CORE ---
class TitanHardwareCore:
    def __init__(self):
        self.hardware_specs = {}

    def scan_hardware(self):
        specs = {}
        try:
            specs['os'] = f"{platform.system()} {platform.release()}"
            specs['cpu_physical'] = psutil.cpu_count(logical=False)
            specs['cpu_logical'] = psutil.cpu_count(logical=True)
            specs['ram_total'] = round(psutil.virtual_memory().total / (1024**3), 2)
            
            # GPU Scan (Windows specific)
            gpu_info = "Unknown"
            if os.name == 'nt':
                try:
                    wmic = subprocess.check_output('wmic path win32_videocontroller get name', shell=True)
                    gpu_info = wmic.decode().split('\n')[1].strip()
                except: pass
            specs['gpu'] = gpu_info
            
            self.hardware_specs = specs
            return True
        except Exception as e:
            return False

    def get_report(self):
        s = self.hardware_specs
        return f"""
[SYSTEM HARDWARE MANIFEST]
==========================
OS:       {s.get('os', 'Unknown')}
CPU:      {s.get('cpu_physical', '?')} Cores / {s.get('cpu_logical', '?')} Threads
RAM:      {s.get('ram_total', '?')} GB
GPU:      {s.get('gpu', 'Unknown')}
==========================
TITAN ANALYSIS:
> CPU Bottleneck Risk: {'HIGH' if s.get('cpu_physical', 4) < 4 else 'LOW'} # type: ignore
> RAM Bottleneck Risk: {'HIGH' if s.get('ram_total', 8) < 16 else 'LOW'} # type: ignore
        """

# --- ENGINE 2: NEXUS HIVE MIND (AI CONTROLLER) ---
class NexusHiveMind:
    def __init__(self, titan_ref):
        self.titan = titan_ref
        self.msg_queue = __import__('queue').Queue() # type: ignore
        self.is_active = True
        
        # Sub-Modules
        self.module_cortex = True # Pattern Rec
        self.module_sentinel = True # Active Defense
        self.module_oracle = True # Prediction

        self.history = self.load_memory()
        
        # Hardware limits (Calibrated by Titan)
        self.cpu_limit_soft = 85
        self.ram_limit_soft = 85

        # Background Thread
        self.thread = threading.Thread(target=self.neural_loop, daemon=True)
        self.thread.start()

    def load_memory(self):
        if os.path.exists(AI_MEMORY_FILE):
            try:
                with open(AI_MEMORY_FILE, 'r') as f: return json.load(f)
            except: return {}
        return {}

    def save_memory(self):
        try:
            with open(AI_MEMORY_FILE, 'w') as f: json.dump(self.history, f)
        except: pass

    def ingest_hardware_data(self, specs):
        ram = specs.get('ram_total', 16)
        # Adapt thresholds based on hardware
        if ram < 8: self.ram_limit_soft = 75 # Be more aggressive on low RAM
        if ram > 32: self.ram_limit_soft = 92 # Relax on high RAM

    def set_modules(self, cortex, sentinel, oracle):
        self.module_cortex = cortex
        self.module_sentinel = sentinel
        self.module_oracle = oracle

    def neural_loop(self):
        while True:
            if self.is_active:
                try:
                    # 1. CORTEX: Analyze State
                    if self.module_cortex:
                        self.cortex_analyze()
                    
                    # 2. SENTINEL: React
                    if self.module_sentinel:
                        self.sentinel_react()

                except Exception as e:
                    pass
            time.sleep(2)

    def cortex_analyze(self):
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        active_app = self.get_active_app()

        if active_app and (cpu > self.cpu_limit_soft or ram > self.ram_limit_soft):
            # Record Pattern
            if active_app not in self.history:
                self.history[active_app] = {"spikes": 0, "type": "unknown"} # type: ignore
            
            self.history[active_app]["spikes"] += 1
            bottleneck = "CPU" if cpu > self.cpu_limit_soft else "RAM"
            self.history[active_app]["type"] = bottleneck
            
            self.save_memory()
            self.msg_queue.put(f"CORTEX: Lag pattern detected in '{active_app}' ({bottleneck} Spike).")

    def sentinel_react(self):
        # Autonomous fixes
        ram = psutil.virtual_memory().percent
        if ram > self.ram_limit_soft:
             self.msg_queue.put("SENTINEL: RAM Critical. Deploying FLUX CAPACITOR...")
             self.force_ram_clean()


    def force_ram_clean(self):
        try:
            if os.name == 'nt':
                PID = os.getpid()
                handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, PID) # type: ignore
                success = ctypes.windll.psapi.EmptyWorkingSet(handle) # type: ignore
                ctypes.windll.kernel32.CloseHandle(handle) # type: ignore
                if success:
                     self.msg_queue.put("SENTINEL: RAM Purge Successful.")
                else:
                     self.msg_queue.put("SENTINEL: RAM Purge Failed (Access Denied?).")
        except Exception as e:
            self.msg_queue.put(f"SENTINEL ERROR: {e}")

    def optimize_network(self):
         try:
            if os.name == 'nt':
                subprocess.run(["ipconfig", "/flushdns"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW) # type: ignore
                self.msg_queue.put("SENTINEL: Network Reset Complete.")
         except Exception as e:
            self.msg_queue.put(f"SENTINEL ERROR: {e}")

    def get_active_app(self):
        try:
            if os.name == 'nt':
                hwnd = ctypes.windll.user32.GetForegroundWindow() # type: ignore
                pid = ctypes.c_ulong()
                ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid)) # type: ignore
                return psutil.Process(pid.value).name()
        except: return None

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() # type: ignore
    except:
        return False

if __name__ == "__main__":
    if not is_admin():
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1) # type: ignore
        sys.exit()
    app = QuantumUI()
    app.mainloop()
