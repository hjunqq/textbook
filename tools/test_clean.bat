@echo off
chcp 65001
echo ====================================
echo Testing Clean Rebuild Version
echo ====================================

echo.
echo Testing clean rebuild without any math fixes...
if not exist output\clean_rebuild.md (
    echo ERROR: clean_rebuild.md not found
    pause
    exit /b 1
)

echo File exists, attempting PDF generation...
pandoc output\clean_rebuild.md --defaults simple-config.yaml -o "output\test_clean_version.pdf" 2>clean_error.txt

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS! Clean version works!
    echo ========================================
    for %%f in ("output\test_clean_version.pdf") do echo PDF size: %%~zf bytes
    
    echo.
    echo The problem IS in math formula fixes!
    echo Now we know exactly what to fix.
    
) else (
    echo.
    echo FAILED: Even clean version fails
    echo.
    echo Error details:
    type clean_error.txt
    
    echo.
    echo This means the problem is NOT in math formulas
    echo Problem is likely in:
    echo - File encoding
    echo - Special characters
    echo - Image paths
    echo - Pandoc configuration
)

echo.
pause