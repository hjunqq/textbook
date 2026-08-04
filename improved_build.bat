@echo off
chcp 65001 > nul
echo.
echo ===============================================
echo   智慧水利教材转换器 - 改进版构建脚本
echo   Improved Textbook Converter Build Script
echo ===============================================
echo.

set "PROJECT_ROOT=%~dp0"
set "CONVERTER_SCRIPT=%PROJECT_ROOT%tools\improved_main_converter.py"

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或不在PATH中
    pause
    exit /b 1
)

REM 检查转换器脚本是否存在
if not exist "%CONVERTER_SCRIPT%" (
    echo ❌ 转换器脚本不存在: %CONVERTER_SCRIPT%
    pause
    exit /b 1
)

:menu
echo 请选择操作:
echo.
echo [1] 完整转换流程 (MD → LaTeX → PDF)
echo [2] 仅转换 Markdown 到 LaTeX
echo [3] 仅构建 PDF (需要先转换)
echo [4] 清理构建文件
echo [5] 查看构建日志
echo [0] 退出
echo.

set /p choice="请输入选项 (0-5): "

if "%choice%"=="1" goto full_build
if "%choice%"=="2" goto convert_only
if "%choice%"=="3" goto build_only
if "%choice%"=="4" goto clean_build
if "%choice%"=="5" goto view_log
if "%choice%"=="0" goto exit
echo 无效选项，请重新选择
goto menu

:full_build
echo.
echo 🚀 执行完整转换流程...
echo.
echo 步骤 1: 转换 Markdown 到 LaTeX
echo 步骤 2: 处理图片文件
echo 步骤 3: 构建 PDF 文档
echo.
python "%CONVERTER_SCRIPT%" --project-root "%PROJECT_ROOT%"
goto end_operation

:convert_only
echo.
echo 🔄 仅转换 Markdown 到 LaTeX...
echo.
echo 正在转换章节文件...
echo - 智能处理章节顺序 (sections 在章节最后)
echo - 保持现有中文标题格式
echo - 自动移除重复的"本章小节"部分
echo - 统一处理图片路径
echo.
python "%CONVERTER_SCRIPT%" --project-root "%PROJECT_ROOT%" --convert-only
goto end_operation

:build_only
echo.
echo 🔨 仅构建 PDF 文档...
echo.
echo 正在使用 XeLaTeX + Biber 构建 PDF...
echo.
python "%CONVERTER_SCRIPT%" --project-root "%PROJECT_ROOT%" --build-only
goto end_operation

:clean_build
echo.
echo 🧹 清理构建文件...
echo.
cd /d "%PROJECT_ROOT%\output"

echo 清理 LaTeX 临时文件...
del /q *.aux *.log *.out *.toc *.bbl *.bcf *.blg *.run.xml *.fdb_latexmk *.fls *.synctex.gz 2>nul

echo 清理转换日志...
del /q "%PROJECT_ROOT%\conversion.log" 2>nul

echo ✅ 清理完成
goto end_operation

:view_log
echo.
echo 📄 查看构建日志...
echo.
set "LOG_FILE=%PROJECT_ROOT%\conversion.log"
if exist "%LOG_FILE%" (
    echo 最后 20 行日志内容:
    echo ----------------------------------------
    more /e +0 "%LOG_FILE%" | find /v "" | for /l %%i in (1,1,20) do (
        set /p line=
        echo !line!
    )
    echo ----------------------------------------
    echo.
    echo 完整日志文件位置: %LOG_FILE%
) else (
    echo 日志文件不存在: %LOG_FILE%
    echo 请先运行一次转换
)
goto end_operation

:end_operation
echo.
echo ===============================================
echo.
set /p continue="按回车键继续，或输入'q'退出: "
if /i "%continue%"=="q" goto exit
goto menu

:exit
echo.
echo 👋 感谢使用智慧水利教材转换器！
echo.
if exist "%PROJECT_ROOT%\output\main.pdf" (
    echo ✅ 当前 PDF 文件: %PROJECT_ROOT%\output\main.pdf
    set "PDF_SIZE="
    for %%i in ("%PROJECT_ROOT%\output\main.pdf") do set "PDF_SIZE=%%~zi"
    if defined PDF_SIZE echo    文件大小: !PDF_SIZE! bytes
)
echo.
pause
exit /b 0
