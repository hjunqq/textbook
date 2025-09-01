@echo off
REM 章节状态检查工具
chcp 65001 >nul
echo 📋 章节状态检查工具
echo ========================================

set PYTHONIOENCODING=utf-8

python check_chapters.py

echo.
pause