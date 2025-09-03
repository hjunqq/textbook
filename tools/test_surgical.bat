@echo off
chcp 65001
echo ====================================
echo Testing Surgical Fix
echo ====================================

echo.
echo Testing surgically fixed version...
python surgical_fix.py

if not exist output\surgical_fixed.md (
    echo ERROR: surgical_fixed.md not found
    pause
    exit /b 1
)

echo.
echo Attempting PDF generation with surgical fixes...
pandoc output\surgical_fixed.md --defaults simple-config.yaml -o "output\surgical_fixed.pdf" 2>surgical_error.txt

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS! Surgical fix worked!
    echo ========================================
    for %%f in ("output\surgical_fixed.pdf") do echo PDF size: %%~zf bytes
    
    echo.
    echo Generating other formats...
    pandoc output\surgical_fixed.md -t docx -o "output\surgical_fixed.docx" --toc
    pandoc output\surgical_fixed.md -t html -o "output\surgical_fixed.html" --toc --standalone --mathjax
    
    echo All formats generated successfully!
    dir output\surgical_fixed.*
    
) else (
    echo.
    echo Still failed, checking specific error...
    type surgical_error.txt
    
    echo.
    echo Looking for remaining issues...
    findstr /n "Missing" surgical_error.txt
    findstr /n "l\." surgical_error.txt
    
    echo.
    echo The remaining issue is likely:
    findstr /c:"sqrt" surgical_error.txt >nul && echo - Still has sqrt space issues
    findstr /c:"frac" surgical_error.txt >nul && echo - Still has frac space issues
    findstr /c:"Missing" surgical_error.txt >nul && echo - Still has unmatched $ symbols
)

echo.
pause