@echo off
chcp 65001 >nul

REM ========================================
REM LaTeX 快速编译脚本 - Windows版本
REM 仅编译一次，用于快速预览
REM ========================================

echo 快速编译模式...

REM 设置目录
cd /d "%~dp0"

REM 创建输出目录
if not exist "output" mkdir output

REM 单次编译
echo 编译中...
xelatex -interaction=nonstopmode -output-directory=output main.tex
if %ERRORLEVEL% equ 0 (
    echo 快速编译完成! PDF文件: output\main.pdf
    for %%F in ("output\main.pdf") do echo 文件大小: %%~zF 字节
) else (
    echo 编译失败
    pause
    exit /b 1
)

pause