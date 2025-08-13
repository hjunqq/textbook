@echo off
chcp 65001 >nul

REM ========================================
REM 智慧水利平台架构与开发 - 完整生成脚本
REM 基于最佳实践的完整转换和编译流程
REM 版本: v1.0
REM 创建时间: 2025年8月7日
REM ========================================

echo ========================================
echo 智慧水利平台架构与开发 - 教材生成工具
echo ========================================
echo.

echo 步骤1: 检查依赖工具...
echo.

REM 检查Pandoc
pandoc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Pandoc 不可用
    echo 请安装Pandoc: https://pandoc.org/installing.html
    goto :end
) else (
    echo ✓ Pandoc 可用
)

REM 检查XeLaTeX
xelatex --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ XeLaTeX 不可用
    echo 请安装TeX Live或MiKTeX
    goto :end
) else (
    echo ✓ XeLaTeX 可用
)

echo.
echo 步骤2: 转换Markdown到LaTeX...
echo.

REM 运行转换脚本
call convert-chapters.bat

echo.
echo 步骤3: 编译LaTeX文档...
echo.

REM 编译主文档
xelatex -interaction=nonstopmode main.tex >nul 2>&1
if %errorlevel% neq 0 (
    echo 编译出现错误，尝试交互模式...
    xelatex main.tex
    goto :end
)

echo 第一次编译完成
xelatex -interaction=nonstopmode main.tex >nul 2>&1
echo 第二次编译完成
xelatex -interaction=nonstopmode main.tex >nul 2>&1
echo 第三次编译完成

echo.
echo ========================================
echo 成功生成教材PDF！
echo ========================================
echo.

if exist main.pdf (
    echo 生成的文件：main.pdf
    for %%f in (main.pdf) do echo 文件大小：%%~zf 字节
    echo.
    echo 可以打开PDF文件查看效果
) else (
    echo PDF文件生成失败，请检查错误日志
)

echo.
echo 工作完成！
echo.

:end
pause
