@echo off
chcp 65001
echo ====================================
echo 智慧水利教材转换器 - 完整转换
echo ====================================

echo.
echo 第一步：清理并创建输出目录...
if exist output rmdir /s /q output
mkdir output

echo.
echo 第二步：合并所有章节文件...
(
echo # 智慧水利平台架构与开发
echo.
type "docs\前言.md"
echo.
echo \newpage
echo.
type "docs\chapters\chapter01\chapter01.md"
echo.
echo \newpage
echo.
type "docs\chapters\chapter02\chapter02.md"
echo.
echo \newpage
echo.
type "docs\chapters\chapter03\chapter03.md"
echo.
echo \newpage
echo.
type "docs\chapters\chapter04\chapter04.md"
echo.
echo \newpage
echo.
type "docs\chapters\chapter05\chapter05.md"
echo.
echo \newpage
echo.
type "docs\chapters\chapter06\chapter06.md"
echo.
echo \newpage
echo.
type "docs\chapters\chapter07\chapter07.md"
echo.
echo \newpage
echo.
type "docs\chapters\chapter08\chapter08.md"
echo.
echo \newpage
echo.
type "docs\chapters\chapter09\chapter09.md"
) > output\merged_textbook.md

echo.
echo 第三步：生成PDF...
pandoc output\merged_textbook.md --defaults pandoc\defaults-pdf.yaml -o output\智慧水利教材.pdf
if %errorlevel% neq 0 (
    echo 错误：PDF生成失败，请检查pandoc和xelatex是否正确安装
    pause
    exit /b 1
)

echo.
echo 第四步：生成LaTeX源文件...
pandoc output\merged_textbook.md --defaults pandoc\defaults-pdf.yaml -o output\智慧水利教材.tex

echo.
echo 第五步：生成Word文档...
pandoc output\merged_textbook.md -f markdown -t docx -o output\智慧水利教材.docx --reference-doc=pandoc\reference.docx 2>nul

echo.
echo ====================================
echo 转换完成！生成的文件：
echo - output\智慧水利教材.pdf
echo - output\智慧水利教材.tex  
echo - output\智慧水利教材.docx
echo - output\merged_textbook.md
echo ====================================
echo.
pause