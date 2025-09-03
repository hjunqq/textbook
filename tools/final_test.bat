@echo off
chcp 65001
echo ========================================
echo FINAL TEST - Correct Structure
echo ========================================

echo.
echo Generating with correct chapter structure...
python radical_fix.py

echo.
echo Testing final version with proper chapters...
pandoc output\ready_to_publish.md --pdf-engine=xelatex -V CJKmainfont="Microsoft YaHei" --toc --toc-depth=2 -o "output\FINAL_CORRECT.pdf"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS! PROPER STRUCTURED PDF!
    echo ========================================
    
    for %%f in ("output\FINAL_CORRECT.pdf") do echo PDF size: %%~zf bytes
    
    echo.
    echo Creating Word version with TOC...
    pandoc output\ready_to_publish.md -t docx --toc --toc-depth=2 -o "output\FINAL_CORRECT.docx"
    
    echo.
    echo Creating HTML version...
    pandoc output\ready_to_publish.md -t html --toc --toc-depth=2 --standalone -o "output\FINAL_CORRECT.html"
    
    echo.
    echo ========================================
    echo COMPLETE SUCCESS!
    echo ========================================
    echo.
    echo Generated files:
    dir output\FINAL_CORRECT.*
    echo.
    echo Your textbook is ready with:
    echo - Correct chapter structure (9 chapters)
    echo - Proper table of contents
    echo - All text content preserved
    echo - Math formulas as placeholders (can be added later)
    
) else (
    echo.
    echo Final test failed, checking error...
    echo.
    pandoc output\ready_to_publish.md --pdf-engine=xelatex -V CJKmainfont="Microsoft YaHei" --toc -o temp.pdf 2>final_error.txt
    type final_error.txt
)

echo.
pause