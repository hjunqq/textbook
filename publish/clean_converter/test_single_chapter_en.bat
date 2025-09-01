@echo off
chcp 65001 >nul
echo Single Chapter Test Tool
echo ========================================

set PYTHONIOENCODING=utf-8
set CURRENT_DIR=%~dp0
set OUTPUT_DIR=%CURRENT_DIR%output
set TEST_DIR=%OUTPUT_DIR%\single_tests

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%TEST_DIR%" mkdir "%TEST_DIR%"

echo Available chapters:
echo   1. chapter01 - Smart Water Management Overview
echo   2. chapter02 - Software Engineering Fundamentals  
echo   3. chapter03 - Version Control with Git
echo   4. chapter04 - Frontend Development Stack
echo   5. chapter05 - Backend Development Framework
echo   6. chapter06 - Data Processing and Algorithms
echo   7. chapter07 - System Integration and Deployment
echo   8. chapter08 - Performance Optimization
echo   9. chapter09 - Project Management
echo.

set /p chapter_num="Choose chapter number (1-9): "

if "%chapter_num%"=="1" set chapter_id=chapter01
if "%chapter_num%"=="2" set chapter_id=chapter02
if "%chapter_num%"=="3" set chapter_id=chapter03
if "%chapter_num%"=="4" set chapter_id=chapter04
if "%chapter_num%"=="5" set chapter_id=chapter05
if "%chapter_num%"=="6" set chapter_id=chapter06
if "%chapter_num%"=="7" set chapter_id=chapter07
if "%chapter_num%"=="8" set chapter_id=chapter08
if "%chapter_num%"=="9" set chapter_id=chapter09

if "%chapter_id%"=="" (
    echo Invalid chapter number
    pause
    exit /b 1
)

echo.
echo Testing chapter: %chapter_id%
echo ========================================

echo Step 1: Preprocessing chapter file...
python test_single_chapter.py %chapter_id%

if %errorlevel% neq 0 (
    echo Preprocessing failed
    pause
    exit /b 1
)

cd /d "%TEST_DIR%"

echo Step 2: Converting to LaTeX...
pandoc %chapter_id%.md ^
    -o %chapter_id%.tex ^
    --from=markdown ^
    --to=latex ^
    --template=../../templates/chinese.tex ^
    --standalone ^
    --toc ^
    --variable=CJKmainfont:"SimSun" ^
    --variable=CJKsansfont:"SimHei" ^
    --variable=CJKmonofont:"FangSong"

if %errorlevel% neq 0 (
    echo LaTeX conversion failed
    pause
    exit /b 1
)

echo LaTeX conversion successful
for %%A in ("%chapter_id%.tex") do echo LaTeX file size: %%~zA bytes

echo.
set /p continue_pdf="Continue with PDF conversion? (y/N): "
if /i not "%continue_pdf%"=="y" (
    echo LaTeX conversion completed
    echo File location: %TEST_DIR%\%chapter_id%.tex
    pause
    exit /b 0
)

echo Step 3: Compiling PDF...
xelatex --version >nul 2>&1
if %errorlevel% neq 0 (
    echo XeLaTeX not installed
    pause
    exit /b 1
)

echo Compiling...
xelatex -interaction=nonstopmode %chapter_id%.tex

if %errorlevel% equ 0 (
    if exist %chapter_id%.pdf (
        for %%A in ("%chapter_id%.pdf") do (
            set /a size_kb=%%~zA/1024
            echo PDF generated successfully ^(!size_kb! KB^)
        )
        echo.
        echo PDF file info:
        echo   - File: %TEST_DIR%\%chapter_id%.pdf
        echo   - Open with PDF reader to check results
    ) else (
        echo PDF file not generated
    )
) else (
    echo PDF compilation failed
    echo Check log file: %chapter_id%.log
)

echo.
echo Single chapter test completed!
echo Test files location: %TEST_DIR%
echo Generated files:
if exist %chapter_id%.md echo   - %chapter_id%.md (Markdown source)
if exist %chapter_id%.tex echo   - %chapter_id%.tex (LaTeX file)  
if exist %chapter_id%.pdf echo   - %chapter_id%.pdf (PDF file)
if exist %chapter_id%.log echo   - %chapter_id%.log (Compilation log)

echo.
echo Recommendations:
echo   1. Check PDF quality
echo   2. If issues found, check .log file
echo   3. After success, test next chapter
echo   4. Run full conversion after all chapters tested

pause