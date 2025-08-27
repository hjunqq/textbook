@echo off
chcp 65001 >nul

echo 测试简化版编译...

cd /d "%~dp0"

if not exist "output" mkdir output

echo 编译 main-simple.tex...
xelatex -interaction=nonstopmode -output-directory=output main-simple.tex

if exist "output\main-simple.pdf" (
    echo 编译成功!
    echo PDF文件: output\main-simple.pdf
) else (
    echo 编译失败，请检查日志: output\main-simple.log
)

pause