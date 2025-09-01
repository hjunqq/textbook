@echo off
chcp 65001 > nul
cd /d %~dp0

echo ==============================================
echo 智慧水利教材单章节转换器 v1.0
echo ==============================================

if "%1"=="" (
    echo.
    echo 使用方法:
    echo   %0 ^<chapter_key^>
    echo.
    echo 可用的章节:
    echo   preface      - 前言
    echo   chapter01    - 第一章
    echo   chapter02    - 第二章  
    echo   chapter03    - 第三章
    echo   all          - 转换所有章节
    echo.
    echo 示例:
    echo   %0 preface
    echo   %0 chapter01
    echo   %0 all
    echo.
    pause
    exit /b 1
)

echo.
echo 正在检查Python环境...
python --version > nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境
    pause
    exit /b 1
)

echo 正在检查Pandoc环境...
pandoc --version > nul 2>&1
if errorlevel 1 (
    echo 警告：未找到Pandoc，转换可能会失败
    echo 请从 https://pandoc.org/installing.html 下载并安装Pandoc
    echo.
)

echo.
echo 开始转换章节: %1
echo.

python chapter_converter.py %1

if errorlevel 1 (
    echo.
    echo 转换失败！请检查错误信息和日志文件：chapter_conversion.log
    echo.
) else (
    echo.
    echo 转换完成！
    echo 输出目录: 逐章节输出\
    echo 日志文件: chapter_conversion.log
    echo.
)

pause
