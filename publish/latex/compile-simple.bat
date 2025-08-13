@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Starting LaTeX compilation...
echo Current directory: %CD%

echo Step 1: Compiling with XeLaTeX...
xelatex -interaction=nonstopmode main.tex

if errorlevel 1 (
    echo Compilation failed. Check main.log for details.
    pause
    exit /b 1
)

echo Step 2: Running biber for bibliography...
biber main

echo Step 3: Final XeLaTeX compilation...
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex

if exist main.pdf (
    echo Success! PDF generated: main.pdf
    start main.pdf
) else (
    echo Compilation failed. Check main.log for details.
)

pause
