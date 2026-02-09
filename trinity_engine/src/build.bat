@echo off
echo =========================================================
echo       PROJECT GEMINI - DUAL ENGINE INSTALLER
echo =========================================================
echo.
echo [1/3] Installing Dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [2/3] Compiling Dual Engine Core...
pyinstaller --noconfirm --onefile --windowed --name "GeminiOptimizer" trinity.py

echo.
echo [3/3] Build Complete! Check dist/GeminiOptimizer.exe
echo.
pause
