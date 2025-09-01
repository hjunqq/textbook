@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0.."

echo Starting Pandoc Build Route B for Windows...

:: Step 1: Generate file list
echo Step 1: Generating file list...
python pandoc/tools/nav_to_list.py
if errorlevel 1 (
    echo Error: Failed to generate file list
    pause
    exit /b 1
)

:: Step 2: Preprocess files
echo Step 2: Preprocessing files...
if exist "pandoc/tmp" rmdir /s /q "pandoc/tmp"
mkdir "pandoc/tmp"

for /f "usebackq delims=" %%f in ("pandoc/files.txt") do (
    echo Processing file: %%f
    
    :: Get directory part and create it
    set "filepath=%%f"
    set "filepath=!filepath:/=\!"
    for %%d in ("!filepath!") do (
        set "dirpath=%%~dpd"
        if not "!dirpath!"=="" (
            if not exist "pandoc/tmp/!dirpath!" mkdir "pandoc/tmp/!dirpath!" 2>nul
        )
    )
    
    :: Preprocess the file
    python pandoc/tools/preprocess_admonition.py < "%%f" > "pandoc/tmp/%%f" 2>nul
    if errorlevel 1 (
        echo Error: Failed to preprocess file %%f
        pause
        exit /b 1
    )
)

:: Step 3: Generate PDF
echo Step 3: Generating PDF...
set FILES=
for /f "usebackq delims=" %%f in ("pandoc/files.txt") do (
    set FILES=!FILES! "pandoc/tmp/%%f"
)

pandoc !FILES! --defaults pandoc/defaults-pdf.yaml -o pandoc/book.pdf
if errorlevel 1 (
    echo Error: Failed to generate PDF
    echo Check if pandoc and xelatex are installed and in PATH
    echo This might take several minutes for the first run...
    pause
    exit /b 1
)

:: Step 4: Generate LaTeX source
echo Step 4: Generating LaTeX source...
pandoc !FILES! --defaults pandoc/defaults-pdf.yaml -o pandoc/book.tex
if errorlevel 1 (
    echo Error: Failed to generate LaTeX
    pause
    exit /b 1
)

echo.
echo Done! Output files:
echo - pandoc/book.pdf  
echo - pandoc/book.tex
pause