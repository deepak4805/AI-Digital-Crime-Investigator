@echo off
title AIDCI - AI Module (Port 5001)
cd /d "C:\gg\AI-Digital-Crime-Investigator\ai-module"
echo =======================================================
echo Starting AI Digital Crime Investigator - AI Microservice
echo Port: 5001
echo =======================================================
..\venv\Scripts\python.exe app.py
pause
