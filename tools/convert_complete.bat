@echo off
chcp 65001
echo ====================================
echo 智慧水利教材完整转换器 v2.0
echo 包含所有章节和小节，修复格式问题
echo ====================================

echo.
echo 第一步：清理输出目录...
if exist output rmdir /s /q output
mkdir output

echo.
echo 第二步：使用Python脚本合并所有内容...
python merge_chapters.py
if %errorlevel% neq 0 (
    echo 错误：内容合并失败，请检查Python环境
    pause
    exit /b 1
)

echo.
echo 第三步：转换为PDF...
pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\智慧水利教材完整版.pdf
if %errorlevel% neq 0 (
    echo 错误：PDF生成失败
    pause
    exit /b 1
)

echo.
echo 第四步：生成LaTeX源文件...
pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\智慧水利教材完整版.tex

echo.
echo 第五步：生成Word文档...
pandoc output\complete_textbook.md -f markdown -t docx -o output\智慧水利教材完整版.docx --toc --reference-doc=reference.docx 2>nul

echo.
echo ====================================
echo 转换完成！生成的文件：
echo - output\智慧水利教材完整版.pdf   (包含所有章节小节)
echo - output\智慧水利教材完整版.tex   (LaTeX源码)
echo - output\智慧水利教材完整版.docx  (Word文档)
echo - output\complete_textbook.md    (合并后的Markdown)
echo ====================================
echo.

echo 文件列表：
dir output /b

echo.
echo 检查合并文件大小：
for %%f in (output\complete_textbook.md) do echo 合并文件大小: %%~zf 字节

echo.
pause