@echo off
chcp 65001 >nul

REM ========================================
REM 清理LaTeX编译产生的临时文件 - Windows版本
REM ========================================

echo 清理LaTeX临时文件...

REM 设置目录
cd /d "%~dp0"

REM 清理输出目录中的临时文件
if exist "output" (
    echo 清理output目录...
    del /q output\*.aux 2>nul
    del /q output\*.log 2>nul
    del /q output\*.toc 2>nul
    del /q output\*.out 2>nul
    del /q output\*.fdb_latexmk 2>nul
    del /q output\*.fls 2>nul
    del /q output\*.lot 2>nul
    del /q output\*.lof 2>nul
    del /q output\*.synctex.gz 2>nul
    del /q output\*.nav 2>nul
    del /q output\*.snm 2>nul
    del /q output\*.vrb 2>nul
    del /q output\*.bbl 2>nul
    del /q output\*.blg 2>nul
    del /q output\*.idx 2>nul
    del /q output\*.ilg 2>nul
    del /q output\*.ind 2>nul
)

REM 清理编译日志
if exist "build\logs" (
    echo 清理编译日志...
    del /q build\logs\*.log 2>nul
)

REM 清理根目录下可能的临时文件
del /q *.aux 2>nul
del /q *.log 2>nul
del /q *.toc 2>nul
del /q *.out 2>nul
del /q *.fdb_latexmk 2>nul
del /q *.fls 2>nul
del /q *.lot 2>nul
del /q *.lof 2>nul
del /q *.synctex.gz 2>nul

echo 清理完成!
pause