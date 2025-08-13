@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ========================================
REM 智慧水利平台架构与开发 - LaTeX编译脚本
REM 基于最佳实践的XeLaTeX编译
REM 版本: v1.0
REM 创建时间: 2025年8月7日
REM ========================================

echo ========================================
echo     智慧水利平台架构与开发
echo     LaTeX文档编译工具
echo ========================================
echo.

REM 检查XeLaTeX是否可用
xelatex --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：XeLaTeX不可用
    echo 请安装TeX Live或MiKTeX
    echo 下载地址：
    echo - TeX Live: https://www.tug.org/texlive/
    echo - MiKTeX: https://miktex.org/
    goto :end
) else (
    echo ✓ XeLaTeX 可用
)

echo.
echo 开始编译主文档...
echo.

REM 第一次编译 - 生成辅助文件
echo 第一次编译（生成辅助文件）...
xelatex -interaction=nonstopmode main.tex
if %errorlevel% neq 0 (
    echo 编译失败！请检查LaTeX语法错误。
    goto :show_log
)

REM 第二次编译 - 处理交叉引用
echo 第二次编译（处理交叉引用）...
xelatex -interaction=nonstopmode main.tex
if %errorlevel% neq 0 (
    echo 编译失败！请检查LaTeX语法错误。
    goto :show_log
)

REM 第三次编译 - 完善目录和引用
echo 第三次编译（完善目录和引用）...
xelatex -interaction=nonstopmode main.tex
if %errorlevel% neq 0 (
    echo 编译失败！请检查LaTeX语法错误。
    goto :show_log
)

echo.
echo ========================================
echo 编译成功！
echo ========================================
echo.
echo 生成的PDF文件：main.pdf
echo 文件大小：
for %%f in (main.pdf) do echo %%~zf 字节
echo.
echo 可以使用PDF阅读器打开查看效果
echo.

goto :cleanup

:show_log
echo.
echo 编译日志（最后50行）：
echo ----------------------------------------
if exist main.log (
    powershell "Get-Content main.log | Select-Object -Last 50"
) else (
    echo 日志文件不存在
)
echo ----------------------------------------
echo.

:cleanup
echo 清理临时文件...
if exist *.aux del *.aux
if exist *.log del *.log
if exist *.out del *.out
if exist *.toc del *.toc
if exist *.lof del *.lof
if exist *.lot del *.lot
if exist *.fdb_latexmk del *.fdb_latexmk
if exist *.fls del *.fls
if exist *.synctex.gz del *.synctex.gz

:end
pause
