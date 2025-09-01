@echo off
REM 中文优化版转换器 - 专门解决中文识别问题
chcp 65001 >nul
echo 🌊 智慧水利教材转换器 v2.2 (中文优化版)
echo ========================================

REM 设置环境变量确保UTF-8编码
set PYTHONIOENCODING=utf-8

REM 检查环境
echo 📋 检查环境...
pandoc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Pandoc未安装
    pause
    exit /b 1
)

REM 路径设置
set CURRENT_DIR=%~dp0
set OUTPUT_DIR=%CURRENT_DIR%output
set TEMPLATE_DIR=%CURRENT_DIR%templates

REM 创建输出目录
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%OUTPUT_DIR%\images" mkdir "%OUTPUT_DIR%\images"

echo 🚀 开始中文优化转换流程...

REM 步骤1: 预处理
echo 📝 步骤1: 预处理文件...
python core_win.py

if %errorlevel% neq 0 (
    echo ❌ 预处理失败
    pause
    exit /b 1
)

cd /d "%OUTPUT_DIR%"

REM 步骤2: 使用中文优化模板转换LaTeX
echo 📄 步骤2: 使用中文模板生成LaTeX...
pandoc textbook_merged.md ^
    -o textbook_chinese.tex ^
    --from=markdown ^
    --to=latex ^
    --template=../templates/chinese.tex ^
    --standalone ^
    --toc ^
    --number-sections ^
    --variable=CJKmainfont:"SimSun" ^
    --variable=CJKsansfont:"SimHei" ^
    --variable=CJKmonofont:"FangSong"

if %errorlevel% neq 0 (
    echo ❌ LaTeX转换失败
    pause
    exit /b 1
)

echo ✅ LaTeX文件生成成功
echo 📄 文件: %OUTPUT_DIR%\textbook_chinese.tex

REM 步骤3: 询问是否编译PDF
echo.
set /p continue="是否继续编译PDF? (y/N): "
if /i not "%continue%"=="y" (
    echo 🎉 LaTeX转换完成！
    echo 💡 您可以手动检查 textbook_chinese.tex 文件
    echo 💡 手动编译: xelatex textbook_chinese.tex
    pause
    exit /b 0
)

REM 步骤4: XeLaTeX编译
echo 🎯 步骤3: XeLaTeX编译PDF...
xelatex --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ XeLaTeX未安装
    echo 💡 请安装MiKTeX或TeX Live
    pause
    exit /b 1
)

echo 🔧 第一次编译...
xelatex -interaction=nonstopmode textbook_chinese.tex

if %errorlevel% equ 0 (
    echo ✅ 第一次编译成功
    
    echo 🔧 第二次编译 (生成目录)...
    xelatex -interaction=nonstopmode textbook_chinese.tex >nul
    
    echo ✅ PDF生成成功！
    echo 📄 输出文件: %OUTPUT_DIR%\textbook_chinese.pdf
    
    REM 显示文件大小
    for %%A in ("textbook_chinese.pdf") do (
        set /a size_kb=%%~zA/1024
        echo 📊 PDF文件大小: !size_kb! KB
    )
    
) else (
    echo ❌ XeLaTeX编译失败
    echo 💡 可能的问题:
    echo    1. 中文字体未安装 (SimSun, SimHei, FangSong)
    echo    2. LaTeX包缺失
    echo    3. 特殊字符转义问题
    echo.
    echo 💡 建议:
    echo    1. 检查 textbook_chinese.log 文件查看详细错误
    echo    2. 手动运行: xelatex textbook_chinese.tex
    echo    3. 安装缺失的字体或LaTeX包
)

echo.
echo 📁 输出目录: %OUTPUT_DIR%
echo 📄 生成的文件:
if exist textbook_chinese.tex echo   - textbook_chinese.tex (LaTeX源码)
if exist textbook_chinese.pdf echo   - textbook_chinese.pdf (PDF文档)
echo   - textbook_merged.md (合并的Markdown)

echo.
echo 🎉 转换完成！
pause