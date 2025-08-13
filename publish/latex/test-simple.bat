@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Testing simplified LaTeX compilation...

echo Step 1: Compiling with XeLaTeX (simple version)...
xelatex -interaction=nonstopmode main-simple.tex

if errorlevel 1 (
    echo First compilation failed. Check main-simple.log
    pause
    exit /b 1
)

echo Step 2: Second pass for cross-references...
xelatex -interaction=nonstopmode main-simple.tex

if exist main-simple.pdf (
    echo Success! Simple PDF generated: main-simple.pdf
    start main-simple.pdf
) else (
    echo Compilation failed. Check main-simple.log
)

pause
