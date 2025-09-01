@echo off
chcp 65001 >nul
echo Chapter Status Checker
echo ======================

set PYTHONIOENCODING=utf-8

python check_status.py

pause