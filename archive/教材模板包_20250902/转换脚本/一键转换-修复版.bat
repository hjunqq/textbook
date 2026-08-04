@echo off
chcp 65001 >nul
echo ========================================
echo 智慧水利教材一键转换脚本 (修复版)
echo ========================================
echo.

:: 设置路径
set "SCRIPT_DIR=%~dp0"
set "CONVERTER=%SCRIPT_DIR%修复后的通用教材转换器.py"
set "SOURCE_DIR=%SCRIPT_DIR%..\..\docs"
set "OUTPUT_DIR=%SCRIPT_DIR%..\输出"

:: 检查源目录
if not exist "%SOURCE_DIR%" (
    echo 错误：源目录不存在 - %SOURCE_DIR%
    echo 请检查docs目录是否存在
    pause
    exit /b 1
)

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

:: 检查转换脚本
if not exist "%CONVERTER%" (
    echo 错误：转换脚本不存在 - %CONVERTER%
    pause
    exit /b 1
)

echo 源目录: %SOURCE_DIR%
echo 输出目录: %OUTPUT_DIR%
echo 转换脚本: %CONVERTER%
echo.

:: 询问用户选择格式
echo 请选择输出格式:
echo 1. LaTeX (.tex)
echo 2. PDF
echo 3. Word (.docx)
echo.
set /p choice="请输入选择 (1-3): "

set "format=pdf"
if "%choice%"=="1" set "format=latex"
if "%choice%"=="2" set "format=pdf"
if "%choice%"=="3" set "format=docx"

echo.
echo 开始转换为 %format% 格式...
echo.

:: 执行转换
python "%CONVERTER%" "%SOURCE_DIR%" -f %format% -o "%OUTPUT_DIR%"

if errorlevel 1 (
    echo.
    echo 转换失败！请检查错误信息。
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo 转换完成！
    echo ========================================
    echo 输出目录: %OUTPUT_DIR%
    echo.
    echo 主要修复内容:
    echo   ✓ 修复了LaTeX文档结构问题
    echo   ✓ 统一了图片路径到 images/ 目录
    echo   ✓ 移除了不支持的emoji字符
    echo   ✓ 修复了缺失的LaTeX命令定义
    echo   ✓ 优化了包依赖管理
    echo.
    
    :: 询问是否打开输出目录
    set /p open="是否打开输出目录？(y/n): "
    if /i "%open%"=="y" (
        explorer "%OUTPUT_DIR%"
    )
)

pause