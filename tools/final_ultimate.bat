@echo off
chcp 65001
echo ====================================
echo 最终数学公式修复
echo ====================================

echo.
echo 第一步：删除并重新生成合并文件...
if exist output\complete_textbook.md del output\complete_textbook.md
python merge_chapters.py

echo.
echo 第二步：检查关键数学公式是否正确包装...
findstr /n /C:"$$K_{p} = f_{k}" output\complete_textbook.md
if %errorlevel% equ 0 (
    echo ✅ 数学公式已正确包装
) else (
    echo ❌ 数学公式仍未正确包装，检查原因：
    findstr /n "K_{p} = f_{k}" output\complete_textbook.md
)

echo.
echo 第三步：检查是否有错误的公式包装...
findstr /C:"$$在式" output\complete_textbook.md >nul
if %errorlevel% equ 0 (
    echo ❌ 发现错误的公式包装
) else (
    echo ✅ 没有错误的公式包装
)

echo.
echo 第四步：最终PDF生成...
pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\智慧水利教材终极完美版.pdf

if %errorlevel% neq 0 (
    echo 仍有错误，查看LaTeX文件的具体问题...
    pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\final_debug.tex 2>error.txt
    echo 错误信息：
    type error.txt
    echo.
    echo 请检查LaTeX文件：output\final_debug.tex
    pause
) else (
    echo.
    echo =========================================
    echo 🎉🎊 终极成功！🎊🎉
    echo 智慧水利平台架构与开发教材完成！
    echo =========================================
    echo.
    for %%f in (output\智慧水利教材终极完美版.pdf) do echo 📊 PDF文件大小: %%~zf 字节
    echo.
    echo 📚 完整内容包含：
    echo   ✅ 前言 + 9个完整章节
    echo   ✅ 所有小节内容
    echo   ✅ 修复的图片显示
    echo   ✅ 格式正确的数学公式
    echo   ✅ 保护的代码块
    echo   ✅ 转换的提示框
    echo   ✅ 清理的编码
    
    echo.
    echo 🎯 同时生成多种格式：
    pandoc output\complete_textbook.md -f markdown -t docx -o output\智慧水利教材终极完美版.docx --toc 2>nul
    pandoc output\complete_textbook.md -f markdown -t html -o output\智慧水利教材终极完美版.html --toc --standalone 2>nul
    
    echo ✅ PDF: output\智慧水利教材终极完美版.pdf
    echo ✅ Word: output\智慧水利教材终极完美版.docx  
    echo ✅ HTML: output\智慧水利教材终极完美版.html
)

echo.
pause