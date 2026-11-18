@echo off
title AIDCI - Launch Full Stack Platform
echo ============================================================
echo  Starting AI Digital Crime Investigator Platform (AIDCI)
echo ============================================================
start "AIDCI AI Module (5001)" "start_ai_module.bat"
timeout /t 2 /nobreak >nul
start "AIDCI Backend (5000)" "start_backend.bat"
timeout /t 2 /nobreak >nul
start "AIDCI Frontend (5173)" "start_frontend.bat"
echo.
echo All services launched!
echo Open http://localhost:5173 in your browser.
pause
