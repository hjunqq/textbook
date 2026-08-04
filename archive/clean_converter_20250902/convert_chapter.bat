@echo off
chcp 65001 >nul
echo Single Chapter Converter - Based on Proven Methods
echo ===================================================

set PYTHONIOENCODING=utf-8

REM Check if chapter ID provided
if "%1"=="" (
    echo Usage: convert_chapter.bat [chapter_id^|all^|list]
    echo.
    echo Examples:
    echo   convert_chapter.bat chapter01    - Process chapter 1
    echo   convert_chapter.bat all          - Process all chapters
    echo   convert_chapter.bat list         - List available chapters
    echo.
    python single_chapter_converter.py
    pause
    exit /b 0
)

if /i "%1"=="list" (
    python single_chapter_converter.py
    pause
    exit /b 0
)

echo Checking requirements...

REM Check Pandoc
pandoc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Pandoc not found
    pause
    exit /b 1
)

REM Check XeLaTeX  
xelatex --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: XeLaTeX not found - only Markdown processing will work
    echo.
)

echo.
echo Processing: %1
echo ===================================================

python single_chapter_converter.py %1

if %errorlevel% neq 0 (
    echo.
    echo Processing failed!
    pause
    exit /b 1
)

echo.
echo ===================================================
echo SUCCESS! Check output/chapters/ directory
echo ===================================================

REM Ask if user wants to convert to LaTeX/PDF
set /p continue="Convert to LaTeX and PDF? (y/N): "
if /i "%continue%"=="y" (
    echo.
    echo Converting to LaTeX and PDF...
    python chapter_to_pdf.py %1
)

pause