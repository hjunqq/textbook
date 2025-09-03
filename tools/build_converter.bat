@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 智慧水利教材转换器 v1.0
echo ========================================
echo.

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或不在PATH中
    echo 请安装Python 3.7+并添加到系统PATH
    pause
    exit /b 1
)

echo [2/4] 检查pandoc环境...
pandoc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Pandoc未安装或不在PATH中
    echo 请安装Pandoc并添加到系统PATH
    pause
    exit /b 1
)

echo [3/4] 检查XeLaTeX环境...
xelatex --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ XeLaTeX未安装或不在PATH中
    echo 请安装完整的LaTeX发行版（如MiKTeX或TeX Live）
    pause
    exit /b 1
)

echo ✅ 环境检查完成
echo.

echo [4/4] 运行测试套件...
python test_framework.py
if %errorlevel% neq 0 (
    echo ❌ 测试失败，请检查代码
    pause
    exit /b 1
)

echo ✅ 测试通过
echo.

echo 🚀 开始转换流程...
echo.
python main_converter.py

if %errorlevel% equ 0 (
    echo.
    echo 🎉🎉🎉 转换完成！🎉🎉🎉
    echo.
    echo 生成的文件：
    echo   📁 output/
    echo   ├── main.tex     ^(主LaTeX文件^)
    echo   ├── main.pdf     ^(最终PDF^)
    echo   └── chapters/    ^(各章节tex文件^)
    echo.
    echo 是否打开输出目录？ ^(y/n^)
    set /p choice=
    if /i "%choice%"=="y" (
        start output
    )
) else (
    echo.
    echo ❌ 转换失败
    echo 请检查日志文件 converter.log
    echo.
)

pause