@echo off
chcp 65001
echo ====================================
echo 简洁直接的解决方案
echo 不过度处理，让pandoc自己处理数学公式
echo ====================================

echo.
echo 第一步：复制图片到正确位置...
if not exist docs\chapters\chapter06 mkdir docs\chapters\chapter06
xcopy ..\docs\chapters\chapter06\images docs\chapters\chapter06\images /e /i /y >nul 2>&1

echo.
echo 第二步：使用简化合并脚本...
python simple_merge.py

echo.
echo 第三步：直接生成PDF（让pandoc处理数学公式）...
pandoc output\simple_textbook.md --defaults simple-config.yaml

if %errorlevel% neq 0 (
    echo 生成调试信息...
    pandoc output\simple_textbook.md --defaults simple-config.yaml -o output\simple_debug.tex
    echo 请查看：output\simple_debug.tex
    pause
) else (
    echo.
    echo ========================================
    echo 🎉 成功！简洁方案奏效！
    echo ========================================
    echo.
    for %%f in (output\智慧水利教材简洁版.pdf) do echo PDF大小: %%~zf 字节
    echo.
    echo 生成多种格式：
    pandoc output\simple_textbook.md -f markdown -t docx -o output\智慧水利教材简洁版.docx --toc 2>nul
    
    echo ✅ PDF: output\智慧水利教材简洁版.pdf
    echo ✅ Word: output\智慧水利教材简洁版.docx
    echo ✅ Markdown: output\simple_textbook.md
)

echo.
pause