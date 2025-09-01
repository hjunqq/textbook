@echo off
cd /d "%~dp0.."
python pandoc/build.py
pause