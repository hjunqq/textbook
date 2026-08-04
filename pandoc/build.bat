@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0.."

echo 正在执行路线B的Pandoc构建...

:: 1. 生成文件顺序
echo 步骤1: 生成文件列表...
python pandoc/tools/nav_to_list.py
if errorlevel 1 (
    echo 错误: 生成文件列表失败
    pause
    exit /b 1
)

:: 2. 预处理 MkDocs Admonition 语法
echo 步骤2: 预处理文件...
if not exist "pandoc/tmp" mkdir "pandoc/tmp"
if exist "pandoc/tmp/*" del /q /s "pandoc/tmp/*" >nul 2>&1

for /f "usebackq delims=" %%f in ("pandoc/files.txt") do (
    echo 处理文件: %%f
    for %%d in ("%%f") do (
        if not "%%~pd"=="" (
            if not exist "pandoc/tmp/%%~pd" mkdir "pandoc/tmp/%%~pd"
        )
    )
    python pandoc/tools/preprocess_admonition.py < "%%f" > "pandoc/tmp/%%f"
    if errorlevel 1 (
        echo 错误: 预处理文件 %%f 失败
        pause
        exit /b 1
    )
)

:: 3. 调用 Pandoc
echo 步骤3: 生成PDF...
set FILES=
for /f "usebackq delims=" %%f in ("pandoc/files.txt") do (
    set FILES=!FILES! pandoc/tmp/%%f
)

pandoc !FILES! --defaults pandoc/defaults-pdf.yaml -o pandoc/book.pdf
if errorlevel 1 (
    echo 错误: 生成PDF失败
    pause
    exit /b 1
)

echo 步骤4: 生成LaTeX源码...
pandoc !FILES! --defaults pandoc/defaults-pdf.yaml -o pandoc/book.tex
if errorlevel 1 (
    echo 错误: 生成LaTeX失败
    pause
    exit /b 1
)

echo.
echo 完成！输出文件：
echo - pandoc/book.pdf
echo - pandoc/book.tex
pause