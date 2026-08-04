@echo off
REM 单章节测试工具 - 逐章验证转换效果
chcp 65001 >nul
echo 📖 智慧水利教材单章节测试工具
echo ========================================

REM 设置环境
set PYTHONIOENCODING=utf-8
set CURRENT_DIR=%~dp0
set OUTPUT_DIR=%CURRENT_DIR%output
set TEST_DIR=%OUTPUT_DIR%\single_tests

REM 创建测试目录
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%TEST_DIR%" mkdir "%TEST_DIR%"

REM 章节列表
echo 📋 可用章节:
echo   1. chapter01 - 智慧水利概述与平台架构基础
echo   2. chapter02 - 软件工程基础与需求分析  
echo   3. chapter03 - 版本控制系统Git
echo   4. chapter04 - 前端开发技术栈
echo   5. chapter05 - 后端开发框架
echo   6. chapter06 - 数据处理与算法实现
echo   7. chapter07 - 系统集成与部署
echo   8. chapter08 - 性能优化与监控
echo   9. chapter09 - 项目管理与团队协作
echo.

set /p chapter_num="请选择要测试的章节编号 (1-9): "

REM 章节映射
if "%chapter_num%"=="1" set chapter_id=chapter01
if "%chapter_num%"=="2" set chapter_id=chapter02
if "%chapter_num%"=="3" set chapter_id=chapter03
if "%chapter_num%"=="4" set chapter_id=chapter04
if "%chapter_num%"=="5" set chapter_id=chapter05
if "%chapter_num%"=="6" set chapter_id=chapter06
if "%chapter_num%"=="7" set chapter_id=chapter07
if "%chapter_num%"=="8" set chapter_id=chapter08
if "%chapter_num%"=="9" set chapter_id=chapter09

if "%chapter_id%"=="" (
    echo ❌ 无效的章节编号
    pause
    exit /b 1
)

echo.
echo 🚀 开始测试章节: %chapter_id%
echo ========================================

REM 步骤1: 预处理单个章节
echo 📝 步骤1: 预处理章节文件...
python test_single_chapter.py %chapter_id%

if %errorlevel% neq 0 (
    echo ❌ 预处理失败
    pause
    exit /b 1
)

cd /d "%TEST_DIR%"

REM 步骤2: 转换LaTeX
echo 📄 步骤2: 转换为LaTeX...
pandoc %chapter_id%.md ^
    -o %chapter_id%.tex ^
    --from=markdown ^
    --to=latex ^
    --template=../../templates/chinese.tex ^
    --standalone ^
    --toc ^
    --variable=CJKmainfont:"SimSun" ^
    --variable=CJKsansfont:"SimHei" ^
    --variable=CJKmonofont:"FangSong"

if %errorlevel% neq 0 (
    echo ❌ LaTeX转换失败
    pause
    exit /b 1
)

echo ✅ LaTeX转换成功
for %%A in ("%chapter_id%.tex") do echo 📊 LaTeX文件大小: %%~zA bytes

REM 询问是否继续PDF转换
echo.
set /p continue_pdf="是否继续转换PDF? (y/N): "
if /i not "%continue_pdf%"=="y" (
    echo ✅ LaTeX转换完成
    echo 📁 文件位置: %TEST_DIR%\%chapter_id%.tex
    pause
    exit /b 0
)

REM 步骤3: 编译PDF
echo 🎯 步骤3: 编译PDF...
xelatex --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ XeLaTeX未安装
    pause
    exit /b 1
)

echo 🔧 编译中...
xelatex -interaction=nonstopmode %chapter_id%.tex

if %errorlevel% equ 0 (
    if exist %chapter_id%.pdf (
        for %%A in ("%chapter_id%.pdf") do (
            set /a size_kb=%%~zA/1024
            echo ✅ PDF生成成功 ^(!size_kb! KB^)
        )
        
        REM 检查PDF内容
        echo 📋 PDF文件信息:
        echo   - 文件: %TEST_DIR%\%chapter_id%.pdf
        echo   - 可以用PDF阅读器打开查看效果
        
    ) else (
        echo ❌ PDF文件未生成
    )
) else (
    echo ❌ PDF编译失败
    echo 💡 查看日志文件: %chapter_id%.log
)

echo.
echo 🎉 单章节测试完成！
echo 📁 测试文件位置: %TEST_DIR%
echo 📄 生成的文件:
if exist %chapter_id%.md echo   - %chapter_id%.md ^(Markdown源文件^)
if exist %chapter_id%.tex echo   - %chapter_id%.tex ^(LaTeX文件^)  
if exist %chapter_id%.pdf echo   - %chapter_id%.pdf ^(PDF文件^)
if exist %chapter_id%.log echo   - %chapter_id%.log ^(编译日志^)

echo.
echo 💡 建议:
echo   1. 检查生成的PDF效果
echo   2. 如有问题，查看.log文件
echo   3. 测试通过后可测试下一章节
echo   4. 所有章节测试完成后运行完整转换

pause