@echo off
REM SVG to PDF 转换批处理文件
REM 用于LaTeX编译前批量转换SVG图像文件

echo ========================================
echo 智慧水利平台架构与开发教材
echo SVG到PDF转换工具
echo ========================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请确保已安装Python并添加到PATH
    echo 可以从 https://python.org/downloads/ 下载安装Python
    pause
    exit /b 1
)

echo 开始转换SVG文件...
echo.

REM 运行Python转换脚本
python convert_svg_to_pdf.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 转换完成！现在可以运行LaTeX编译了
    echo ========================================
) else (
    echo.
    echo ========================================
    echo 转换失败，请检查错误信息
    echo ========================================
)

echo.
echo 按任意键退出...
pause >nul
