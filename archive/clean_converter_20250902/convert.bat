@echo off
chcp 65001 >nul
echo 🌊 智慧水利教材转换器 v2.0
echo ========================================

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 未安装或不在 PATH 中
    echo 请安装 Python 3.7+ 后重试
    pause
    exit /b 1
)

REM 检查Pandoc是否安装
pandoc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Pandoc 未安装
    echo 请从 https://pandoc.org/installing.html 下载安装
    echo.
    echo 继续执行可能会失败...
    timeout /t 3 >nul
)

REM 执行转换
echo.
echo 🚀 开始转换...
python convert.py %*

REM 检查结果
if %errorlevel% equ 0 (
    echo.
    echo ✅ 转换成功完成！
    echo 📁 请查看 output 目录中的文件
) else (
    echo.
    echo ❌ 转换失败
    echo 请检查错误信息并重试
)

echo.
pause