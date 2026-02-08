@echo off
echo =========================================================
echo       APEX GAME ENGINE - LOCAL BUILD SYSTEM
echo =========================================================
echo.
echo [1/3] Installing Dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [2/3] Building Optimized Executeable...
pyinstaller --noconfirm --onefile --windowed --name "ApexGameBooster" main.py

echo.
echo [3/3] Build Complete! Check the 'dist' folder for your .exe
echo.
pause
