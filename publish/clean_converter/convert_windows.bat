@echo off
REM 智慧水利教材转换器 - Windows环境修复版
chcp 65001 >nul
echo 🌊 智慧水利教材转换器 v2.0 (Windows版)
echo ========================================

REM 检查环境
echo 📋 检查Windows环境...
pandoc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Pandoc未安装或不在PATH中
    echo 💡 请确保已安装Pandoc并重启命令提示符
    pause
    exit /b 1
)
echo ✅ Pandoc已安装

xelatex --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  XeLaTeX未安装，无法生成PDF
    echo 💡 如需PDF输出，请安装MiKTeX或TeX Live
) else (
    echo ✅ XeLaTeX已安装
)

REM 获取当前目录的Windows路径
set CURRENT_DIR=%~dp0
set OUTPUT_DIR=%CURRENT_DIR%output
set IMAGES_DIR=%OUTPUT_DIR%\images

REM 创建输出目录
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%IMAGES_DIR%" mkdir "%IMAGES_DIR%"

REM 检查源文件目录
set DOCS_DIR=%CURRENT_DIR%..\..\docs
if not exist "%DOCS_DIR%" (
    echo ❌ 未找到源文件目录: %DOCS_DIR%
    echo 💡 请确认在正确的目录中运行此脚本
    pause
    exit /b 1
)

echo ✅ 找到源文件目录

REM 执行转换
echo.
echo 🚀 开始转换流程...

REM 先用Python处理文件合并和预处理
echo 📝 步骤1: 合并和预处理文件...
python core_win.py

if %errorlevel% neq 0 (
    echo ❌ 预处理失败
    pause
    exit /b 1
)

REM 检查是否生成了合并文件
if not exist "%OUTPUT_DIR%\textbook_merged.md" (
    echo ❌ 未生成合并的Markdown文件
    pause
    exit /b 1
)

echo ✅ 预处理完成

REM 使用Pandoc转换
cd /d "%OUTPUT_DIR%"

echo 🔄 步骤2: Pandoc转换...

REM 根据参数选择输出格式
set FORMAT=%1
if "%FORMAT%"=="" set FORMAT=pdf

if "%FORMAT%"=="latex" goto convert_latex
if "%FORMAT%"=="pdf" goto convert_pdf

:convert_latex
echo 📄 转换为LaTeX...
pandoc textbook_merged.md -o textbook.tex --from=markdown --to=latex --standalone --toc --number-sections
if %errorlevel% equ 0 (
    echo ✅ LaTeX转换成功: %OUTPUT_DIR%\textbook.tex
) else (
    echo ❌ LaTeX转换失败
)
goto end

:convert_pdf
echo 🎯 转换为PDF...
pandoc textbook_merged.md -o textbook.pdf --from=markdown --to=pdf --pdf-engine=xelatex --standalone --toc --number-sections
if %errorlevel% equ 0 (
    echo ✅ PDF转换成功: %OUTPUT_DIR%\textbook.pdf
    for %%A in ("%OUTPUT_DIR%\textbook.pdf") do echo 📄 文件大小: %%~zA bytes
) else (
    echo ❌ PDF转换失败
    echo 💡 请检查XeLaTeX安装和中文字体配置
)
goto end

:end
echo.
echo 📁 输出目录: %OUTPUT_DIR%
echo 🎉 转换完成！
pause