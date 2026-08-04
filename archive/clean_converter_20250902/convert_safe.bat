@echo off
REM 智慧水利教材转换器 - 安全版本（先LaTeX后PDF）
chcp 65001 >nul
echo 🌊 智慧水利教材转换器 v2.1 (安全版)
echo ========================================

REM 检查环境
echo 📋 检查Windows环境...
pandoc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Pandoc未安装或不在PATH中
    pause
    exit /b 1
)
echo ✅ Pandoc已安装

REM 获取路径
set CURRENT_DIR=%~dp0
set OUTPUT_DIR=%CURRENT_DIR%output
set IMAGES_DIR=%OUTPUT_DIR%\images

REM 创建输出目录
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%IMAGES_DIR%" mkdir "%IMAGES_DIR%"

REM 检查源文件
set DOCS_DIR=%CURRENT_DIR%..\..\docs
if not exist "%DOCS_DIR%" (
    echo ❌ 未找到源文件目录
    pause
    exit /b 1
)

echo 🚀 开始转换流程...

REM 步骤1: 预处理
echo 📝 步骤1: 预处理和合并文件...
python core_win.py

if %errorlevel% neq 0 (
    echo ❌ 预处理失败
    pause
    exit /b 1
)

REM 切换到输出目录
cd /d "%OUTPUT_DIR%"

REM 步骤2: 生成LaTeX (安全步骤)
echo 📄 步骤2: 生成LaTeX文件...
pandoc textbook_merged.md -o textbook.tex --from=markdown --to=latex --standalone --toc --number-sections

if %errorlevel% neq 0 (
    echo ❌ LaTeX生成失败
    echo 💡 请检查Markdown文件内容
    pause
    exit /b 1
)

echo ✅ LaTeX文件生成成功
echo 📁 位置: %OUTPUT_DIR%\textbook.tex

REM 询问是否继续转换PDF
echo.
set /p continue="是否继续转换为PDF? (y/N): "
if /i not "%continue%"=="y" (
    echo 🎉 LaTeX转换完成！您可以手动检查 textbook.tex 文件
    echo 💡 如需转换PDF，请运行: xelatex textbook.tex
    pause
    exit /b 0
)

REM 步骤3: 转换PDF
echo 🎯 步骤3: 转换为PDF...
xelatex --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ XeLaTeX未安装
    echo 💡 请安装MiKTeX或TeX Live
    pause
    exit /b 1
)

REM 使用XeLaTeX直接编译（避免Pandoc的PDF问题）
echo 🔧 使用XeLaTeX编译...
xelatex textbook.tex

if %errorlevel% equ 0 (
    echo ✅ PDF转换成功！
    echo 📄 输出文件: %OUTPUT_DIR%\textbook.pdf
    for %%A in ("textbook.pdf") do echo 📊 文件大小: %%~zA bytes
    
    REM 可选：再次编译以生成目录
    echo 🔄 第二次编译（生成目录）...
    xelatex textbook.tex >nul
    
) else (
    echo ❌ PDF编译失败
    echo 💡 LaTeX编译错误，请检查 textbook.tex 文件
    echo 💡 常见问题：
    echo    - 特殊字符未转义
    echo    - 缺少LaTeX包
    echo    - 中文字体问题
)

echo.
echo 📁 所有文件位置: %OUTPUT_DIR%
echo 🎉 转换完成！
pause