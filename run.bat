@echo off

call venv\Scripts\activate

start /min cmd /c python src/app.py
