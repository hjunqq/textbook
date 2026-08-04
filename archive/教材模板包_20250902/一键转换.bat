@echo off
chcp 65001
echo ====================================
echo 智慧水利教材一键转换脚本
echo ====================================

rem 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境
    echo 请确保已安装Python并添加到PATH环境变量
    pause
    exit /b 1
)

rem 检查Pandoc
pandoc --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Pandoc
    echo 请安装Pandoc: https://pandoc.org/installing.html
    pause
    exit /b 1
)

rem 检查XeLaTeX
xelatex --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到XeLaTeX
    echo 请安装TeX Live或MiKTeX
    pause
    exit /b 1
)

echo 环境检查通过，开始转换...
echo.

rem 切换到项目根目录
cd /d "%~dp0..\.."

rem 运行转换脚本
python "publish\教材模板包\智慧水利教材终极转换器.py" --config "publish\教材模板包\智慧水利教材配置.json"

if errorlevel 1 (
    echo.
    echo 转换失败！请检查错误信息
    pause
    exit /b 1
)

echo.
echo ====================================
echo 转换完成！
echo 输出位置: publish\latex_output
echo ====================================
pause
