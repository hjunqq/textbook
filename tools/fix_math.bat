@echo off
chcp 65001
echo ====================================
echo 修复数学公式并重新生成
echo ====================================

echo.
echo 第一步：删除旧的合并文件...
if exist output\complete_textbook.md del output\complete_textbook.md

echo.
echo 第二步：使用修复后的数学公式处理重新合并...
python merge_chapters.py

echo.
echo 第三步：检查有问题的公式是否修复...
findstr /n "K_p = f_k" output\complete_textbook.md

echo.
echo 第四步：生成PDF...
pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\智慧水利教材数学修复版.pdf

if %errorlevel% neq 0 (
    echo 错误：PDF生成仍然失败
    echo 生成LaTeX文件查看详细问题...
    pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\math_debug.tex
    echo.
    echo 请查看 output\math_debug.tex 文件第35683行附近
    pause
) else (
    echo.
    echo ========================================
    echo 🎉 数学公式修复成功！PDF生成完成！
    echo ========================================
    echo.
    echo 生成文件：output\智慧水利教材数学修复版.pdf
    echo.
    for %%f in (output\智慧水利教材数学修复版.pdf) do echo PDF大小: %%~zf 字节
)

echo.
pause