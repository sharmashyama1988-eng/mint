@echo off
echo =========================================================
echo       TRINITY ENGINE - GOD MODE INSTALLER
echo =========================================================
echo.
echo [1/3] Installing Critical Core Components...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [2/3] Compiling Trinity Engine (God Mode)...
pyinstaller --noconfirm --onefile --windowed --name "TrinityEngineX" trinity.py

echo.
echo [3/3] Installation Complete. 
echo.
pause
