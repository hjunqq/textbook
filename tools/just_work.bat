@echo off
chcp 65001
echo ========================================
echo BRUTAL FIX - Just Get It Done
echo ========================================

echo.
echo Creating brutal fix version (removes all math)...
python brutal_fix.py

echo.
echo Testing brutal fix...
pandoc output\brutal_fix.md --pdf-engine=xelatex -V CJKmainfont="Microsoft YaHei" -o "output\FINAL_WORKING.pdf"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS! PDF GENERATED!
    echo ========================================
    for %%f in ("output\FINAL_WORKING.pdf") do echo PDF size: %%~zf bytes
    
    echo.
    echo Creating Word version...
    pandoc output\brutal_fix.md -t docx -o "output\FINAL_WORKING.docx" --toc
    
    echo.
    echo DONE! You have working files:
    echo - output\FINAL_WORKING.pdf
    echo - output\FINAL_WORKING.docx
    echo.
    echo You can manually add back math formulas as images if needed.
    
) else (
    echo STILL FAILED - Something deeper is wrong
    echo Try this basic command:
    echo pandoc output\brutal_fix.md -o output\basic.pdf
)

pause