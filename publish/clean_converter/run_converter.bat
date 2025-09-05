@echo off
chcp 65001 > nul
echo.
echo ===============================================
echo   智慧水利教材转换器 - 快速启动脚本
echo   Textbook Converter - Quick Start Script
echo ===============================================
echo.

REM 设置脚本路径
set "SCRIPT_DIR=%~dp0"
set "CONVERTER_SCRIPT=%SCRIPT_DIR%textbook_converter.py"
set "TEST_SCRIPT=%SCRIPT_DIR%test_converter.py"

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或不在PATH中
    echo 请安装Python 3.7或更高版本
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
echo [1] 运行转换器 (PDF输出)
echo [2] 运行转换器 (LaTeX输出) 
echo [3] 运行转换器 (HTML输出)
echo [4] 运行测试套件
echo [5] 检查系统环境
echo [6] 显示帮助信息
echo [7] 自定义命令
echo [0] 退出
echo.

set /p choice="请输入选项 (0-7): "

if "%choice%"=="1" goto convert_pdf
if "%choice%"=="2" goto convert_latex  
if "%choice%"=="3" goto convert_html
if "%choice%"=="4" goto run_tests
if "%choice%"=="5" goto check_env
if "%choice%"=="6" goto show_help
if "%choice%"=="7" goto custom_command
if "%choice%"=="0" goto exit
echo 无效选项，请重新选择
goto menu

:convert_pdf
echo.
echo 🔄 转换为PDF格式...
echo.
set /p input_dir="请输入文档目录路径 (默认: docs): "
if "%input_dir%"=="" set input_dir=docs

set /p output_dir="请输出目录路径 (默认: output): "
if "%output_dir%"=="" set output_dir=output

echo.
echo 执行命令: python "%CONVERTER_SCRIPT%" -i "%input_dir%" -o "%output_dir%" -f pdf -v
echo.
python "%CONVERTER_SCRIPT%" -i "%input_dir%" -o "%output_dir%" -f pdf -v
goto end_operation

:convert_latex
echo.
echo 🔄 转换为LaTeX格式...
echo.
set /p input_dir="请输入文档目录路径 (默认: docs): "
if "%input_dir%"=="" set input_dir=docs

set /p output_dir="请输出目录路径 (默认: output): "
if "%output_dir%"=="" set output_dir=output

echo.
echo 执行命令: python "%CONVERTER_SCRIPT%" -i "%input_dir%" -o "%output_dir%" -f latex -v
echo.
python "%CONVERTER_SCRIPT%" -i "%input_dir%" -o "%output_dir%" -f latex -v
goto end_operation

:convert_html
echo.
echo 🔄 转换为HTML格式...
echo.
set /p input_dir="请输入文档目录路径 (默认: docs): "
if "%input_dir%"=="" set input_dir=docs

set /p output_dir="请输出目录路径 (默认: output): "
if "%output_dir%"=="" set output_dir=output

echo.
echo 执行命令: python "%CONVERTER_SCRIPT%" -i "%input_dir%" -o "%output_dir%" -f html -v
echo.
python "%CONVERTER_SCRIPT%" -i "%input_dir%" -o "%output_dir%" -f html -v
goto end_operation

:run_tests
echo.
echo 🧪 运行测试套件...
echo.
if exist "%TEST_SCRIPT%" (
    python "%TEST_SCRIPT%" -v
) else (
    echo ❌ 测试脚本不存在: %TEST_SCRIPT%
)
goto end_operation

:check_env
echo.
echo 🔍 检查系统环境...
echo.

echo 检查Python版本:
python --version

echo.
echo 检查Pandoc:
pandoc --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Pandoc未安装或不在PATH中
    echo 请从 https://pandoc.org/installing.html 下载安装
) else (
    echo ✅ Pandoc已安装
    pandoc --version | findstr "pandoc"
)

echo.
echo 检查XeLaTeX:
xelatex --version >nul 2>&1
if errorlevel 1 (
    echo ❌ XeLaTeX未安装（PDF输出需要）
    echo 请安装TeX Live或MiKTeX
) else (
    echo ✅ XeLaTeX已安装
)

echo.
echo 检查转换器脚本:
if exist "%CONVERTER_SCRIPT%" (
    echo ✅ 转换器脚本存在: %CONVERTER_SCRIPT%
) else (
    echo ❌ 转换器脚本不存在: %CONVERTER_SCRIPT%
)

if exist "%TEST_SCRIPT%" (
    echo ✅ 测试脚本存在: %TEST_SCRIPT%
) else (
    echo ❌ 测试脚本不存在: %TEST_SCRIPT%
)
goto end_operation

:show_help
echo.
echo 📚 帮助信息
echo.
python "%CONVERTER_SCRIPT%" --help
goto end_operation

:custom_command
echo.
echo 🛠️ 自定义命令模式
echo.
echo 请输入完整的转换命令参数 (不包含python和脚本路径):
echo 示例: -i docs -o output -f pdf --chapters chapter01,chapter02 -v
echo.
set /p custom_args="命令参数: "

if "%custom_args%"=="" (
    echo 未输入参数，返回主菜单
    goto menu
)

echo.
echo 执行命令: python "%CONVERTER_SCRIPT%" %custom_args%
echo.
python "%CONVERTER_SCRIPT%" %custom_args%
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
pause
exit /b 0