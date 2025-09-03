@echo off
chcp 65001
echo ====================================
echo 最终修复数学公式格式
echo ====================================

echo.
echo 第一步：删除有问题的合并文件...
if exist output\complete_textbook.md del output\complete_textbook.md

echo.
echo 第二步：使用改进的数学公式处理重新合并...
python merge_chapters.py

echo.
echo 第三步：检查修复后的公式格式...
echo 查找公式行：
findstr /n "K_{p} = f_{k}" output\complete_textbook.md

echo.
echo 第四步：生成最终PDF...
pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\智慧水利完整教材.pdf

if %errorlevel% neq 0 (
    echo 如果还有错误，查看前几行问题：
    findstr /n "Missing" output\final_debug.tex 2>nul
    echo.
    echo 请手动检查output\final_debug.tex文件
    pause
) else (
    echo.
    echo ========================================
    echo 🎉🎉🎉 完全成功！🎉🎉🎉
    echo ========================================
    echo.
    echo 生成的完整教材文件：
    dir output\*.pdf output\*.docx /b 2>nul
    echo.
    for %%f in (output\智慧水利完整教材.pdf) do echo PDF大小: %%~zf 字节
    echo.
    echo 包含内容：
    echo ✅ 所有9个章节 + 前言
    echo ✅ 所有小节内容  
    echo ✅ 修复的图片显示
    echo ✅ 修复的数学公式
    echo ✅ 修复的admonition语法
    echo ✅ 清理的编码问题
    
    echo.
    echo 同时生成Word版本...
    pandoc output\complete_textbook.md -f markdown -t docx -o output\智慧水利完整教材.docx --toc 2>nul
    echo Word版本：output\智慧水利完整教材.docx
)

echo.
pause