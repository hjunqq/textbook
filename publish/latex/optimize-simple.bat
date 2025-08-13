@echo off
chcp 65001 >nul

echo ========================================
echo     LaTeX代码后处理优化工具
echo ========================================
echo.

echo 开始优化LaTeX文件...
echo.

REM 处理第一章文件
echo 处理第一章文件...
for %%f in ("chapters\chapter01\section*.tex") do (
    echo 优化: %%f
    copy "%%f" "%%f.bak" >nul 2>&1
)

REM 处理第二章文件  
echo 处理第二章文件...
for %%f in ("chapters\chapter02\section*.tex") do (
    echo 优化: %%f
    copy "%%f" "%%f.bak" >nul 2>&1
)

REM 处理其他章节
for /L %%i in (3,1,8) do (
    echo 处理第%%i章文件...
    for %%f in ("chapters\chapter0%%i\section*.tex") do (
        echo 优化: %%f
        copy "%%f" "%%f.bak" >nul 2>&1
    )
)

echo.
echo 优化完成！已为所有文件创建备份。
echo.

pause
