@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ========================================
REM 通用教材转换批处理脚本
REM 支持多种转换格式和配置选项
REM 版本: v2.0
REM 更新: 2025年8月7日
REM ========================================

echo ========================================
echo         通用教材转换工具
echo ========================================
echo.

REM 设置默认参数
set "source_dir=."
set "output_format=pdf"
set "output_dir=输出"
set "config_file="

REM 解析命令行参数
:parse_args
if "%~1"=="" goto :start_conversion
if "%~1"=="-f" (
    set "output_format=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="-o" (
    set "output_dir=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="-c" (
    set "config_file=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="-h" goto :show_help
if "%~1"=="--help" goto :show_help

REM 第一个参数作为源目录
set "source_dir=%~1"
shift
goto :parse_args

:show_help
echo 用法: %0 [源目录] [选项]
echo.
echo 选项:
echo   -f FORMAT    输出格式 (latex, pdf, docx) 默认: pdf
echo   -o DIR       输出目录 默认: 输出
echo   -c FILE      配置文件
echo   -h, --help   显示此帮助信息
echo.
echo 示例:
echo   %0                           # 转换当前目录为PDF
echo   %0 第一章 -f latex           # 转换第一章为LaTeX
echo   %0 . -f docx -o 我的输出     # 转换为Word并指定输出目录
echo.
goto :end

:start_conversion
echo 转换参数:
echo   源目录: %source_dir%
echo   输出格式: %output_format%
echo   输出目录: %output_dir%
if defined config_file echo   配置文件: %config_file%
echo.

REM 检查源目录
if not exist "%source_dir%" (
    echo 错误：源目录不存在: %source_dir%
    goto :end
)

REM 检查依赖工具
echo 检查依赖工具...

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python 不可用
    echo 请安装Python: https://www.python.org/downloads/
    goto :end
) else (
    echo ✓ Python 可用
)

REM 检查Pandoc
pandoc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Pandoc 不可用
    echo 请安装Pandoc: https://pandoc.org/installing.html
    if "%output_format%"=="latex" (
        echo 警告：没有Pandoc将无法转换
    )
    if "%output_format%"=="docx" (
        echo 错误：转换Word格式需要Pandoc
        goto :end
    )
) else (
    echo ✓ Pandoc 可用
)

REM 检查XeLaTeX（仅在需要PDF时）
if "%output_format%"=="pdf" (
    xelatex --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo ✗ XeLaTeX 不可用
        echo 请安装TeX Live: https://www.tug.org/texlive/
        echo 或安装MiKTeX: https://miktex.org/
        goto :end
    ) else (
        echo ✓ XeLaTeX 可用
    )
)

echo.

REM 创建输出目录
if not exist "%output_dir%" (
    mkdir "%output_dir%"
    echo ✓ 创建输出目录: %output_dir%
)

REM 检查Python转换脚本
set "converter_script=转换脚本\通用教材转换器.py"
if not exist "%converter_script%" (
    echo 错误：找不到转换脚本: %converter_script%
    goto :end
)

REM 构建Python命令
set "python_cmd=python "%converter_script%" "%source_dir%" -f %output_format% -o "%output_dir%""
if defined config_file (
    set "python_cmd=!python_cmd! -c "%config_file%""
)

echo 执行转换...
echo 命令: %python_cmd%
echo.

REM 执行转换
%python_cmd%

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo          转换成功完成！
    echo ========================================
    echo.
    echo 输出文件位于: %output_dir%
    echo.
    
    REM 列出生成的文件
    echo 生成的文件:
    for %%f in ("%output_dir%\*") do (
        echo   %%~nxf
    )
    echo.
    
    choice /c YN /m "是否打开输出目录"
    if !errorlevel! equ 1 start "" "%output_dir%"
    
) else (
    echo.
    echo ========================================
    echo          转换失败！
    echo ========================================
    echo.
    echo 请检查:
    echo 1. 源目录中是否有Markdown文件
    echo 2. 文件编码是否正确 (UTF-8)
    echo 3. Markdown语法是否正确
    echo 4. 是否有必要的依赖工具
    echo.
    echo 如需帮助，请查看转换脚本的详细输出
)

:end
echo.
pause
