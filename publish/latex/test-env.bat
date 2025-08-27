@echo off
chcp 65001 >nul 2>&1

echo Testing super simple LaTeX document...

cd /d "%~dp0"

if not exist "output" mkdir output

echo Compiling simple-test.tex...
xelatex -interaction=nonstopmode -output-directory=output simple-test.tex

if exist "output\simple-test.pdf" (
    echo [SUCCESS] Super simple test passed!
    echo Now testing minimal configuration...
    
    xelatex -interaction=nonstopmode -output-directory=output minimal.tex
    
    if exist "output\minimal.pdf" (
        echo [SUCCESS] Minimal test also passed!
        echo LaTeX environment is working correctly.
    ) else (
        echo [ERROR] Minimal test failed
        echo Issue is in the minimal-config.tex template
    )
) else (
    echo [ERROR] Super simple test failed
    echo Basic LaTeX environment has issues
    echo Check if ctex package is installed
)

pause