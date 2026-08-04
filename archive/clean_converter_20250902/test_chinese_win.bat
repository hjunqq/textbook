@echo off
REM 中文转换测试 - Windows版本
chcp 65001 >nul
echo 🧪 中文LaTeX转换测试工具
echo ========================================

REM 设置环境变量
set PYTHONIOENCODING=utf-8
set CURRENT_DIR=%~dp0
set OUTPUT_DIR=%CURRENT_DIR%output
set TEMPLATE_DIR=%CURRENT_DIR%templates

REM 创建输出目录
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo 🧪 创建中文测试文档
echo ==============================

REM 创建中文测试文件
echo # 智慧水利平台架构与开发 > "%OUTPUT_DIR%\chinese_test.md"
echo. >> "%OUTPUT_DIR%\chinese_test.md"
echo ## 第一章 概述 >> "%OUTPUT_DIR%\chinese_test.md"
echo. >> "%OUTPUT_DIR%\chinese_test.md"
echo ### 1.1 基本概念 >> "%OUTPUT_DIR%\chinese_test.md"
echo. >> "%OUTPUT_DIR%\chinese_test.md"
echo **智慧水利**是运用物联网、云计算、大数据、人工智能等现代信息技术，对水利工程进行智能化管理和运维的新模式。 >> "%OUTPUT_DIR%\chinese_test.md"
echo. >> "%OUTPUT_DIR%\chinese_test.md"
echo 主要特点包括： >> "%OUTPUT_DIR%\chinese_test.md"
echo. >> "%OUTPUT_DIR%\chinese_test.md"
echo 1. **数据驱动**：基于海量数据分析决策 >> "%OUTPUT_DIR%\chinese_test.md"
echo 2. **智能预警**：实时监测水情变化 >> "%OUTPUT_DIR%\chinese_test.md"
echo 3. **精准调度**：优化水资源配置 >> "%OUTPUT_DIR%\chinese_test.md"
echo 4. **协同管理**：多部门信息共享 >> "%OUTPUT_DIR%\chinese_test.md"
echo. >> "%OUTPUT_DIR%\chinese_test.md"
echo ```python >> "%OUTPUT_DIR%\chinese_test.md"
echo # 数据采集示例代码 >> "%OUTPUT_DIR%\chinese_test.md"
echo class WaterDataCollector: >> "%OUTPUT_DIR%\chinese_test.md"
echo     def __init__(self, station_id): >> "%OUTPUT_DIR%\chinese_test.md"
echo         self.station_id = station_id >> "%OUTPUT_DIR%\chinese_test.md"
echo         self.sensors = [] >> "%OUTPUT_DIR%\chinese_test.md"
echo     >> "%OUTPUT_DIR%\chinese_test.md"
echo     def collect_data(self): >> "%OUTPUT_DIR%\chinese_test.md"
echo         """采集水位、流量数据""" >> "%OUTPUT_DIR%\chinese_test.md"
echo         return {'水位': 125.6, '流量': 50.2} >> "%OUTPUT_DIR%\chinese_test.md"
echo ``` >> "%OUTPUT_DIR%\chinese_test.md"

echo ✅ 测试文件创建: %OUTPUT_DIR%\chinese_test.md

echo.
echo 🔄 测试Pandoc中文转换
echo 📄 测试1: 转换为LaTeX...

cd /d "%OUTPUT_DIR%"

REM 检查pandoc
pandoc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ Pandoc未安装或不在PATH中
    pause
    exit /b 1
)

REM 转换LaTeX
pandoc chinese_test.md ^
    -o chinese_test.tex ^
    --from=markdown ^
    --to=latex ^
    --template=../templates/chinese.tex ^
    --standalone ^
    --toc ^
    --variable=CJKmainfont:"SimSun" ^
    --variable=CJKsansfont:"SimHei" ^
    --variable=CJKmonofont:"FangSong"

if %errorlevel% equ 0 (
    echo   ✅ LaTeX转换成功
    
    REM 检查生成的LaTeX文件
    if exist chinese_test.tex (
        for %%A in ("chinese_test.tex") do echo   📊 LaTeX文件大小: %%~zA bytes
    )
) else (
    echo   ❌ LaTeX转换失败
    pause
    exit /b 1
)

echo.
echo 🎯 测试2: 转换为PDF...

REM 检查XeLaTeX
xelatex --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ⚠️  XeLaTeX不可用，跳过PDF测试
    echo   ✅ LaTeX转换测试通过
    pause
    exit /b 0
)

REM 编译PDF
echo   🔧 编译PDF...
xelatex -interaction=nonstopmode chinese_test.tex

if %errorlevel% equ 0 (
    if exist chinese_test.pdf (
        for %%A in ("chinese_test.pdf") do (
            set /a size_kb=%%~zA/1024
            echo   ✅ PDF生成成功 ^(!size_kb! KB^)
        )
        echo.
        echo 🎉 中文转换测试通过！
        echo 💡 可以放心使用 convert_chinese.bat
    ) else (
        echo   ❌ PDF文件未生成
    )
) else (
    echo   ❌ PDF编译失败
    echo   💡 可能的问题:
    echo      1. 中文字体未安装 ^(SimSun, SimHei, FangSong^)
    echo      2. LaTeX包缺失
    echo      3. 特殊字符转义问题
)

echo.
echo 📁 测试文件位置: %OUTPUT_DIR%
pause