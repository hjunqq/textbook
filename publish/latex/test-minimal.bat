@echo off
chcp 65001 >nul

echo 测试最小化配置编译...

cd /d "%~dp0"

if not exist "output" mkdir output

echo 编译 minimal.tex...
xelatex -interaction=nonstopmode -output-directory=output minimal.tex

if exist "output\minimal.pdf" (
    echo ========================================
    echo 最小化测试编译成功!
    echo PDF文件: output\minimal.pdf
    echo ========================================
) else (
    echo 编译失败，请检查日志: output\minimal.log
    if exist "output\minimal.log" (
        echo 错误信息:
        findstr /C:"!" output\minimal.log
    )
)

pause