@echo off
chcp 65001
echo ====================================
echo 修复数学公式语法错误
echo 问题：原始文件中的 \sqrt { 有非法空格
echo ====================================

echo.
echo 第一步：复制图片文件...
if not exist docs\chapters\chapter06 mkdir docs\chapters\chapter06
xcopy ..\docs\chapters\chapter06\images docs\chapters\chapter06\images /e /i /y >nul 2>&1

echo.
echo 第二步：修复数学公式语法错误...
python math_fix_merge.py

echo.
echo 第三步：检查修复效果...
findstr /c:"\\sqrt {" output\math_fixed_textbook.md >nul
if %errorlevel% equ 0 (
    echo ❌ 仍有 \sqrt { 空格问题
) else (
    echo ✅ \sqrt { 空格问题已修复
)

echo.
echo 第四步：生成PDF...
pandoc output\math_fixed_textbook.md --defaults simple-config.yaml -o output\智慧水利教材语法修复版.pdf

if %errorlevel% neq 0 (
    echo LaTeX编译失败，查看具体错误...
    pandoc output\math_fixed_textbook.md --defaults simple-config.yaml -o output\syntax_debug.tex 2>latex_error.txt
    echo.
    echo 错误信息：
    type latex_error.txt 2>nul
    echo.
    echo 请检查：output\syntax_debug.tex
    pause
) else (
    echo.
    echo =========================================
    echo 🎉 成功！数学公式语法修复奏效！
    echo =========================================
    echo.
    for %%f in (output\智慧水利教材语法修复版.pdf) do echo PDF大小: %%~zf 字节
    echo.
    echo 生成其他格式...
    pandoc output\math_fixed_textbook.md -f markdown -t docx -o output\智慧水利教材语法修复版.docx --toc 2>nul
    
    echo ✅ PDF: output\智慧水利教材语法修复版.pdf  
    echo ✅ Word: output\智慧水利教材语法修复版.docx
    echo ✅ 源文件: output\math_fixed_textbook.md
)

echo.
pause