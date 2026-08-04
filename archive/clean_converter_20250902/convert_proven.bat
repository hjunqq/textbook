@echo off
chcp 65001 >nul
echo Proven Smart Water Textbook Converter
echo Based on successful conversion experience
echo ========================================

set PYTHONIOENCODING=utf-8
set CURRENT_DIR=%~dp0

echo Checking requirements...

REM Check Pandoc
pandoc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Pandoc not found
    pause
    exit /b 1
)
echo - Pandoc: OK

REM Check XeLaTeX  
xelatex --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: XeLaTeX not found
    pause
    exit /b 1
)
echo - XeLaTeX: OK

echo.
echo Starting conversion with proven methods...
echo ========================================

python proven_converter.py

if %errorlevel% neq 0 (
    echo.
    echo Conversion failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Conversion completed.
echo Check the output directory for results.
echo ========================================

pause