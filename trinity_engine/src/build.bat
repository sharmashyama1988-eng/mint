@echo off
echo =========================================================
echo       PROJECT GEMINI - TRIPLE ENGINE INSTALLER
echo =========================================================
echo.
echo [1/3] Installing Dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [2/3] Compiling Project Gemini (Neural Core)...
pyinstaller --noconfirm --onefile --windowed --name "ProjectGemini" trinity.py

echo.
echo [3/3] Build Complete! Check dist/ProjectGemini.exe
echo.
pause
