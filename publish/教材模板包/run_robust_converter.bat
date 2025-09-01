@echo off
chcp 65001 > nul
cd /d %~dp0

echo ==============================================
echo 智慧水利教材健壮转换器 v6.0
echo ==============================================

echo.
echo 正在检查Python环境...
python --version > nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境，请先安装Python
    pause
    exit /b 1
)

echo 正在检查Pandoc环境...
pandoc --version > nul 2>&1
if errorlevel 1 (
    echo 警告：未找到Pandoc，将尝试安装或提示用户安装
    echo 请访问 https://pandoc.org/installing.html 安装Pandoc
    echo.
    echo 继续运行脚本，但可能无法生成LaTeX文件...
    echo.
)

echo.
echo 开始转换过程...
python robust_converter.py

if errorlevel 1 (
    echo.
    echo 转换失败！请查看错误信息和日志文件：conversion.log
    echo.
) else (
    echo.
    echo 转换完成！
    echo 请检查输出目录中的文件：
    echo - 教材.tex (LaTeX源文件)
    echo - 教材.pdf (如果LaTeX编译成功)
    echo - conversion.log (详细日志)
    echo.
)

echo 按任意键退出...
pause > nul
