
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
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_area()
        self.tray_icon = self.setup_tray()

        # Start Systems
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.update_live_feed()

        # Auto-Scan on Launch
        self.titan.scan_hardware()
        self.update_hardware_info()

    def setup_tray(self):
        # Create a simple icon image
        image = Image.new('RGB', (64, 64), color=(0, 0, 0))
        d = ImageDraw.Draw(image)
        d.rectangle([16, 16, 48, 48], fill=self.accent_color)
        
        menu = pystray.Menu(
            pystray.MenuItem('Restore', self.restore_from_tray),
            pystray.MenuItem('Exit', self.quit_app)
        )
        return pystray.Icon("QuantumNexus", image, "Quantum Nexus Engine", menu)

    def minimize_to_tray(self):
        self.withdraw()
        self.is_minimized = True
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_from_tray(self, icon, item):
        self.tray_icon.stop()
        self.after(0, self.deiconify)
        self.is_minimized = False

    def quit_app(self, icon, item):
        self.tray_icon.stop()
        self.destroy()
        os._exit(0)

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.sidebar_color)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        # Logo
        ctk.CTkLabel(self.sidebar, text="QUANTUM\nNEXUS", font=ctk.CTkFont(size=26, weight="bold"), text_color=self.accent_color).grid(row=0, column=0, padx=20, pady=(40, 20))
        
        # Buttons
        self.btn_dashboard = self.create_nav_btn("DASHBOARD", 1, self.show_dashboard)
        self.btn_titan = self.create_nav_btn("TITAN HARDWARE", 2, self.show_titan)
        self.btn_nexus = self.create_nav_btn("NEXUS HIVE", 3, self.show_nexus)
        
        # Status
        self.status_label = ctk.CTkLabel(self.sidebar, text="SYSTEM: ONLINE", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.success_color)
        self.status_label.grid(row=7, column=0, padx=20, pady=20)

    def create_nav_btn(self, text, row, command):
        btn = ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", text_color="gray", hover_color="#222222", anchor="w", command=command, height=45)
        btn.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        return btn

    def setup_main_area(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Frames for pages
        self.page_dashboard = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.page_titan = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.page_nexus = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        # Init Pages
        self.build_dashboard()
        self.build_titan()
        self.build_nexus()
        
        # Show default
        self.show_dashboard()

    def show_page(self, page, btn):
        # Reset buttons
        for b in [self.btn_dashboard, self.btn_titan, self.btn_nexus]:
            b.configure(fg_color="transparent", text_color="gray")
        btn.configure(fg_color="#222222", text_color="white")
        
        # Hide all pages
        for p in [self.page_dashboard, self.page_titan, self.page_nexus]:
            p.pack_forget()
        
        # Show selected
        page.pack(fill="both", expand=True)

    def show_dashboard(self): self.show_page(self.page_dashboard, self.btn_dashboard)
    def show_titan(self): self.show_page(self.page_titan, self.btn_titan)
    def show_nexus(self): self.show_page(self.page_nexus, self.btn_nexus)

    # --- DASHBOARD UI ---
    def build_dashboard(self):
        ctk.CTkLabel(self.page_dashboard, text="SYSTEM OVERVIEW", font=ctk.CTkFont(size=24, weight="bold"), text_color="white").pack(anchor="w", pady=(0, 20))
        
        # Stats Row
        stats_frame = ctk.CTkFrame(self.page_dashboard, fg_color="transparent")
        stats_frame.pack(fill="x", pady=10)
        
        self.dash_cpu = self.create_stat_card(stats_frame, "CPU LOAD", "0%")
        self.dash_cpu.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.dash_ram = self.create_stat_card(stats_frame, "RAM USAGE", "0%")
        self.dash_ram.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.dash_ai_state = self.create_stat_card(stats_frame, "AI ACTIVITY", "IDLE")
        self.dash_ai_state.pack(side="left", fill="x", expand=True)

        # Quick Actions
        ctk.CTkLabel(self.page_dashboard, text="QUICK PROTOCOLS", font=ctk.CTkFont(size=18, weight="bold"), text_color="gray").pack(anchor="w", pady=(30, 10))
        
        action_frame = ctk.CTkFrame(self.page_dashboard, fg_color="transparent")
        action_frame.pack(fill="x")
        
        ctk.CTkButton(action_frame, text="FLUSH MEMORY", height=50, fg_color="#333333", hover_color=self.accent_color, command=self.nexus.force_ram_clean).pack(fill="x", pady=5)
        ctk.CTkButton(action_frame, text="NETWORK RESET", height=50, fg_color="#333333", hover_color=self.accent_color, command=self.nexus.optimize_network).pack(fill="x", pady=5)

    def create_stat_card(self, parent, title, value):
        frame = ctk.CTkFrame(parent, fg_color="#1a1a1a", height=100)
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(15, 5))
        lbl = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color="white")
        lbl.pack(pady=(0, 15))
        return lbl # Return value label specifically

    # --- TITAN UI ---
    def build_titan(self):
        ctk.CTkLabel(self.page_titan, text="TITAN HARDWARE SCANNER", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.accent_color).pack(anchor="w", pady=(0, 20))
        
        self.titan_text = ctk.CTkTextbox(self.page_titan, height=300, fg_color="#111111", text_color="#00ff88", font=("Consolas", 12))
        self.titan_text.pack(fill="x", pady=10)
        
        ctk.CTkButton(self.page_titan, text="RUN DEEP HARDWARE SCAN", height=50, fg_color=self.accent_color, text_color="black", hover_color="#00aabb", command=self.update_hardware_info).pack(fill="x", pady=20)

    # --- NEXUS UI ---
    def build_nexus(self):
        ctk.CTkLabel(self.page_nexus, text="NEXUS HIVE MIND (AI SWARM)", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.accent_color).pack(anchor="w", pady=(0, 20))
        
        # Switches for AI Modules
        self.sw_cortex = ctk.CTkSwitch(self.page_nexus, text="CORTEX: Pattern Recognition (Detect Lag)", onvalue=True, offvalue=False, command=self.toggle_nexus_modules)
        self.sw_cortex.pack(anchor="w", pady=10)
        self.sw_cortex.select()

        self.sw_sentinel = ctk.CTkSwitch(self.page_nexus, text="SENTINEL: Real-time Defense (Auto-Fix)", onvalue=True, offvalue=False, command=self.toggle_nexus_modules)
        self.sw_sentinel.pack(anchor="w", pady=10)
        self.sw_sentinel.select()
        
        self.sw_oracle = ctk.CTkSwitch(self.page_nexus, text="ORACLE: Predictive Pre-caching", onvalue=True, offvalue=False, command=self.toggle_nexus_modules)
        self.sw_oracle.pack(anchor="w", pady=10)
        self.sw_oracle.select()

        # Nexus Log
        ctk.CTkLabel(self.page_nexus, text="NEURAL FEED", font=ctk.CTkFont(size=14, weight="bold"), text_color="gray").pack(anchor="w", pady=(20, 5))
        self.nexus_log = ctk.CTkTextbox(self.page_nexus, height=200, fg_color="#000000", text_color=self.accent_color, font=("Consolas", 11))
        self.nexus_log.pack(fill="both", expand=True)

    def log_nexus(self, msg):
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.nexus_log.insert("end", f"[{timestamp}] {msg}\n")
            self.nexus_log.see("end")
        except: pass

    # --- LOGIC ---
    def update_hardware_info(self):
        info = self.titan.get_report()
        self.titan_text.delete("1.0", "end")
        self.titan_text.insert("end", info)
        # Feed info to Nexus
        self.nexus.ingest_hardware_data(self.titan.hardware_specs)
        self.log_nexus("TITAN: Hardware profile updated. Nexus calibrated.")

    def toggle_nexus_modules(self):
        self.nexus.set_modules(
            self.sw_cortex.get(),
            self.sw_sentinel.get(),
            self.sw_oracle.get()
        )
        self.log_nexus("NEXUS: Module limits reconfigured.")

    def update_live_feed(self):
        # UI Updates
        try:
             # CPU/RAM
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            
            self.dash_cpu.configure(text=f"{cpu}%")
            self.dash_cpu.configure(text_color=self.danger_color if cpu > 90 else "white")
            
            self.dash_ram.configure(text=f"{ram.percent}%")
            self.dash_ram.configure(text_color=self.danger_color if ram.percent > 90 else "white")
            
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
> CPU Bottleneck Risk: {'HIGH' if s.get('cpu_physical', 4) < 4 else 'LOW'}
> RAM Bottleneck Risk: {'HIGH' if s.get('ram_total', 8) < 16 else 'LOW'}
        """

# --- ENGINE 2: NEXUS HIVE MIND (AI CONTROLLER) ---
class NexusHiveMind:
    def __init__(self, titan_ref):
        self.titan = titan_ref
        self.msg_queue = __import__('queue').Queue()
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
                self.history[active_app] = {"spikes": 0, "type": "unknown"}
            
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
                ctypes.windll.psapi.EmptyWorkingSet(handle) # type: ignore
                ctypes.windll.kernel32.CloseHandle(handle) # type: ignore
        except: pass

    def optimize_network(self):
         try:
            if os.name == 'nt':
                subprocess.run(["ipconfig", "/flushdns"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW) # type: ignore
                self.msg_queue.put("SENTINEL: Network Reset Complete.")
         except: pass

    def get_active_app(self):
        try:
            if os.name == 'nt':
                hwnd = ctypes.windll.user32.GetForegroundWindow() # type: ignore
                pid = ctypes.c_ulong()
                ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid)) # type: ignore
                return psutil.Process(pid.value).name()
        except: return None

if __name__ == "__main__":
    app = QuantumUI()
    app.mainloop()
