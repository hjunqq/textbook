@echo off
chcp 65001
echo ====================================
echo 清理编码问题并重新生成
echo ====================================

echo.
echo 第一步：删除有问题的合并文件...
if exist output\complete_textbook.md del output\complete_textbook.md

echo.
echo 第二步：使用修复后的脚本重新合并...
python merge_chapters.py
if %errorlevel% neq 0 (
    echo 错误：合并脚本失败
    pause
    exit /b 1
)

echo.
echo 第三步：检查是否还有Unicode转义问题...
findstr /c:"\\u" output\complete_textbook.md >nul
if %errorlevel% equ 0 (
    echo 警告：仍然发现Unicode转义字符
) else (
    echo 好的：Unicode转义字符已清理
)

echo.
echo 第四步：检查文件大小和内容...
for %%f in (output\complete_textbook.md) do echo 文件大小: %%~zf 字节

echo.
echo 第五步：尝试生成PDF...
pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\智慧水利教材清洁版.pdf
if %errorlevel% neq 0 (
    echo 错误：PDF生成失败，正在生成LaTeX文件供调试...
    pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\debug.tex
    echo 请查看 output\debug.tex 文件
    pause
    exit /b 1
)

echo.
echo 成功！生成了清洁的PDF文件：
echo - output\智慧水利教材清洁版.pdf

pause