@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ========================================
REM 智慧水利平台架构与开发 - Markdown转LaTeX脚本
REM 基于最佳实践的Pandoc转换
REM 版本: v1.0
REM 创建时间: 2025年8月7日
REM ========================================

echo ========================================
echo     智慧水利平台架构与开发
echo     Markdown转LaTeX转换工具
echo ========================================
echo.

REM 设置路径
set "SOURCE_DIR=..\..\chapters"
set "OUTPUT_DIR=chapters"
set "TEMPLATE_DIR=templates"

REM 检查源目录
if not exist "%SOURCE_DIR%" (
    echo 错误：源目录不存在: %SOURCE_DIR%
    goto :end
)

REM 创建输出目录
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo 开始转换章节内容...
echo.

REM 转换第一章
echo 转换第一章...
if not exist "%OUTPUT_DIR%\chapter01" mkdir "%OUTPUT_DIR%\chapter01"

REM 转换第一章主文件
pandoc "%SOURCE_DIR%\chapter01\chapter01.md" ^
-o "%OUTPUT_DIR%\chapter01\chapter01-content.tex" ^
--from=markdown ^
--to=latex ^
--standalone=false ^
--listings ^
--variable=fontsize:12pt ^
--variable=linestretch:1.5 ^
--filter=pandoc-citeproc

REM 转换第一章各节
for %%f in ("%SOURCE_DIR%\chapter01\section*.md") do (
    set "filename=%%~nf"
    echo 转换 !filename!.md...
    pandoc "%%f" ^
    -o "%OUTPUT_DIR%\chapter01\!filename!.tex" ^
    --from=markdown ^
    --to=latex ^
    --standalone=false ^
    --listings ^
    --variable=fontsize:12pt ^
    --variable=linestretch:1.5
)

REM 转换第二章
echo 转换第二章...
if not exist "%OUTPUT_DIR%\chapter02" mkdir "%OUTPUT_DIR%\chapter02"

pandoc "%SOURCE_DIR%\chapter02\chapter02.md" ^
-o "%OUTPUT_DIR%\chapter02\chapter02-content.tex" ^
--from=markdown ^
--to=latex ^
--standalone=false ^
--listings

for %%f in ("%SOURCE_DIR%\chapter02\section*.md") do (
    set "filename=%%~nf"
    echo 转换 !filename!.md...
    pandoc "%%f" ^
    -o "%OUTPUT_DIR%\chapter02\!filename!.tex" ^
    --from=markdown ^
    --to=latex ^
    --standalone=false ^
    --listings
)

REM 转换第三章
echo 转换第三章...
if not exist "%OUTPUT_DIR%\chapter03" mkdir "%OUTPUT_DIR%\chapter03"

pandoc "%SOURCE_DIR%\chapter03\chapter03.md" ^
-o "%OUTPUT_DIR%\chapter03\chapter03-content.tex" ^
--from=markdown ^
--to=latex ^
--standalone=false ^
--listings

for %%f in ("%SOURCE_DIR%\chapter03\section*.md") do (
    set "filename=%%~nf"
    echo 转换 !filename!.md...
    pandoc "%%f" ^
    -o "%OUTPUT_DIR%\chapter03\!filename!.tex" ^
    --from=markdown ^
    --to=latex ^
    --standalone=false ^
    --listings
)

REM 转换第四章
echo 转换第四章...
if not exist "%OUTPUT_DIR%\chapter04" mkdir "%OUTPUT_DIR%\chapter04"

pandoc "%SOURCE_DIR%\chapter04\chapter04.md" ^
-o "%OUTPUT_DIR%\chapter04\chapter04-content.tex" ^
--from=markdown ^
--to=latex ^
--standalone=false ^
--listings

for %%f in ("%SOURCE_DIR%\chapter04\section*.md") do (
    set "filename=%%~nf"
    echo 转换 !filename!.md...
    pandoc "%%f" ^
    -o "%OUTPUT_DIR%\chapter04\!filename!.tex" ^
    --from=markdown ^
    --to=latex ^
    --standalone=false ^
    --listings
)

REM 转换第五章
echo 转换第五章...
if not exist "%OUTPUT_DIR%\chapter05" mkdir "%OUTPUT_DIR%\chapter05"

pandoc "%SOURCE_DIR%\chapter05\chapter05.md" ^
-o "%OUTPUT_DIR%\chapter05\chapter05-content.tex" ^
--from=markdown ^
--to=latex ^
--standalone=false ^
--listings

for %%f in ("%SOURCE_DIR%\chapter05\section*.md") do (
    set "filename=%%~nf"
    echo 转换 !filename!.md...
    pandoc "%%f" ^
    -o "%OUTPUT_DIR%\chapter05\!filename!.tex" ^
    --from=markdown ^
    --to=latex ^
    --standalone=false ^
    --listings
)

REM 转换第六章
echo 转换第六章...
if not exist "%OUTPUT_DIR%\chapter06" mkdir "%OUTPUT_DIR%\chapter06"

pandoc "%SOURCE_DIR%\chapter06\chapter06.md" ^
-o "%OUTPUT_DIR%\chapter06\chapter06-content.tex" ^
--from=markdown ^
--to=latex ^
--standalone=false ^
--listings

for %%f in ("%SOURCE_DIR%\chapter06\section*.md") do (
    set "filename=%%~nf"
    echo 转换 !filename!.md...
    pandoc "%%f" ^
    -o "%OUTPUT_DIR%\chapter06\!filename!.tex" ^
    --from=markdown ^
    --to=latex ^
    --standalone=false ^
    --listings
)

REM 转换第七章
echo 转换第七章...
if not exist "%OUTPUT_DIR%\chapter07" mkdir "%OUTPUT_DIR%\chapter07"

pandoc "%SOURCE_DIR%\chapter07\chapter07.md" ^
-o "%OUTPUT_DIR%\chapter07\chapter07-content.tex" ^
--from=markdown ^
--to=latex ^
--standalone=false ^
--listings

for %%f in ("%SOURCE_DIR%\chapter07\section*.md") do (
    set "filename=%%~nf"
    echo 转换 !filename!.md...
    pandoc "%%f" ^
    -o "%OUTPUT_DIR%\chapter07\!filename!.tex" ^
    --from=markdown ^
    --to=latex ^
    --standalone=false ^
    --listings
)

REM 转换第八章
echo 转换第八章...
if not exist "%OUTPUT_DIR%\chapter08" mkdir "%OUTPUT_DIR%\chapter08"

pandoc "%SOURCE_DIR%\chapter08\chapter08.md" ^
-o "%OUTPUT_DIR%\chapter08\chapter08-content.tex" ^
--from=markdown ^
--to=latex ^
--standalone=false ^
--listings

for %%f in ("%SOURCE_DIR%\chapter08\section*.md") do (
    set "filename=%%~nf"
    echo 转换 !filename!.md...
    pandoc "%%f" ^
    -o "%OUTPUT_DIR%\chapter08\!filename!.tex" ^
    --from=markdown ^
    --to=latex ^
    --standalone=false ^
    --listings
)

echo.
echo ========================================
echo 转换完成！
echo ========================================
echo.
echo 已生成以下文件：
echo - 各章节LaTeX文件
echo - 各小节LaTeX文件
echo.
echo 接下来可以运行主文档编译：
echo xelatex main.tex
echo.

:end
pause
