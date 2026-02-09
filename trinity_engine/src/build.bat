@echo off
echo =========================================================
echo       QUANTUM NEXUS - HYPERVISOR INSTALLER
echo =========================================================
echo.
echo [1/3] Installing Quantum Dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [2/3] Compiling Quantum Nexus (Hypervisor)...
pyinstaller --noconfirm --onefile --windowed --name "QuantumNexus" quantum_engine.py

echo.
echo [3/3] Build Complete! Check dist/QuantumNexus.exe
echo.
pause
