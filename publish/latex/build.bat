@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM ========================================
REM LaTeX Build Script - Windows
REM Smart Water Conservancy Platform
REM ========================================

echo =========================================
echo Starting LaTeX compilation...
echo =========================================

REM Check if XeLaTeX is available
where xelatex >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: XeLaTeX not found
    echo Please install TeX Live or MiKTeX
    echo Recommended: TeX Live 2023 or newer
    pause
    exit /b 1
)

REM Show XeLaTeX version
echo XeLaTeX version detected:
xelatex --version | findstr "XeTeX" 2>nul

REM Set working directory
cd /d "%~dp0"

REM Create output directories
if not exist "output" mkdir output
if not exist "build" mkdir build
if not exist "build\logs" mkdir build\logs

REM Clean old files
echo Cleaning old compilation files...
del /q output\*.aux 2>nul
del /q output\*.log 2>nul
del /q output\*.toc 2>nul
del /q output\*.out 2>nul
del /q output\*.fdb_latexmk 2>nul
del /q output\*.fls 2>nul
del /q output\*.synctex.gz 2>nul

REM Step 1: Test minimal configuration
echo Step 1: Testing minimal configuration...
xelatex -interaction=nonstopmode -output-directory=output minimal.tex > build\logs\minimal.log 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Minimal test passed
) else (
    echo [ERROR] Minimal test failed
    echo Please check LaTeX environment configuration
    echo Detailed error log: build\logs\minimal.log
    echo.
    echo First few errors:
    findstr /C:"!" build\logs\minimal.log | head -3 2>nul
    pause
    exit /b 1
)

REM Step 2: Compile main document
echo Step 2: Compiling main document...
echo First compilation...
xelatex -interaction=nonstopmode -output-directory=output main.tex > build\logs\compile_1.log 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] First compilation failed
    echo Error details:
    findstr /C:"!" build\logs\compile_1.log 2>nul | head -5
    echo Full log: build\logs\compile_1.log
    pause
    exit /b 1
)

echo Second compilation (generating TOC and cross-references)...
xelatex -interaction=nonstopmode -output-directory=output main.tex > build\logs\compile_2.log 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Second compilation failed
    echo Full log: build\logs\compile_2.log
    REM Second compilation failure might be due to cross-reference issues, don't force exit
)

REM Check if PDF was generated successfully
if exist "output\main.pdf" (
    echo =========================================
    echo [SUCCESS] Compilation successful!
    echo PDF file: output\main.pdf
    echo =========================================
    
    REM Show file size
    for %%F in ("output\main.pdf") do (
        set size=%%~zF
        set /a sizeKB=!size!/1024
        echo File size: !sizeKB! KB
    )
    
    REM Ask if user wants to open PDF
    set /p "open=Open PDF file? (y/n): "
    if /i "!open!"=="y" (
        start "" "output\main.pdf"
    )
) else (
    echo =========================================
    echo [ERROR] Compilation failed - PDF not generated
    echo =========================================
    echo Possible issues:
    echo 1. Missing LaTeX packages
    echo 2. Chinese fonts not properly installed
    echo 3. File path contains special characters
    echo.
    echo Please check compilation logs: build\logs\
    pause
    exit /b 1
)

echo Compilation process completed!
pause