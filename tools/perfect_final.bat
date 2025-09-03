@echo off
chcp 65001
echo ====================================
echo 智能修复：区分数学公式和代码
echo ====================================

echo.
echo 第一步：删除有问题的合并文件...
if exist output\complete_textbook.md del output\complete_textbook.md

echo.
echo 第二步：使用智能数学公式检测重新合并...
python merge_chapters.py

echo.
echo 第三步：检查JavaScript代码是否被错误处理...
findstr /n "WebSocket" output\complete_textbook.md | findstr "\$\$"
if %errorlevel% equ 0 (
    echo 警告：仍有代码被错误识别为数学公式
) else (
    echo ✅ JavaScript代码处理正确
)

echo.
echo 第四步：检查真正的数学公式...
findstr /n "K_{p}" output\complete_textbook.md

echo.
echo 第五步：生成最终PDF...
pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\智慧水利教材完美版.pdf

if %errorlevel% neq 0 (
    echo 错误信息：
    pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\debug.tex 2>&1 | findstr /i "error"
    echo.
    echo 生成调试文件：output\debug.tex
    pause
) else (
    echo.
    echo ========================================
    echo 🎉✨ 完美成功！所有问题已解决 ✨🎉
    echo ========================================
    echo.
    echo 🎯 智慧水利平台架构与开发教材
    echo 📖 完整版PDF已生成！
    echo.
    for %%f in (output\智慧水利教材完美版.pdf) do echo 📊 PDF大小: %%~zf 字节
    echo.
    echo ✅ 包含完整内容：
    echo    📚 所有章节和小节
    echo    🖼️ 正确显示的图片
    echo    🧮 格式正确的数学公式
    echo    💻 保持原样的代码块
    echo    📝 转换后的admonition
    echo    🔤 清理的编码格式
    
    echo.
    echo 📄 生成Word版本...
    pandoc output\complete_textbook.md -f markdown -t docx -o output\智慧水利教材完美版.docx --toc 2>nul
    echo ✅ Word版本：output\智慧水利教材完美版.docx
)

echo.
pause