@echo off
chcp 65001
echo ====================================
echo 修复正则表达式错误并重新生成
echo ====================================

echo.
echo 第一步：重新合并（修复了正则表达式错误）...
python merge_chapters.py

if %errorlevel% neq 0 (
    echo Python脚本执行失败，停止处理
    pause
    exit /b 1
)

echo.
echo 第二步：生成PDF...
pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\智慧水利教材最终版.pdf

if %errorlevel% neq 0 (
    echo PDF生成失败，生成调试文件...
    pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\final_debug.tex
    echo.
    echo 请查看调试文件：output\final_debug.tex
    pause
) else (
    echo.
    echo ========================================
    echo 🎉 成功！PDF生成完成！
    echo ========================================
    echo.
    echo 生成文件：output\智慧水利教材最终版.pdf
    echo.
    for %%f in (output\智慧水利教材最终版.pdf) do echo PDF大小: %%~zf 字节
    echo.
    echo 同时生成Word版本...
    pandoc output\complete_textbook.md -f markdown -t docx -o output\智慧水利教材最终版.docx --toc 2>nul
    echo Word文件：output\智慧水利教材最终版.docx
)

echo.
pause