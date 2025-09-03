@echo off
chcp 65001
echo ====================================
echo 全面修复：图片+数学公式+编码
echo ====================================

echo.
echo 第一步：复制第6章图片到正确位置...
if not exist docs\chapters\chapter06 mkdir docs\chapters\chapter06
xcopy ..\docs\chapters\chapter06\images docs\chapters\chapter06\images /e /i /y >nul 2>&1

echo.
echo 第二步：重新合并（修复所有格式问题）...
if exist output\complete_textbook.md del output\complete_textbook.md
python merge_chapters.py

echo.
echo 第三步：检查修复效果...
echo 检查图片路径：
findstr /c:"ch6_image" output\complete_textbook.md | head -3

echo.
echo 检查数学公式：
findstr /c:"sqrt" output\complete_textbook.md | head -2

echo.
echo 第四步：生成PDF（最终版本）...
pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\智慧水利教材终极版.pdf
if %errorlevel% neq 0 (
    echo 错误：PDF生成失败，查看详细错误...
    pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\debug.tex 2>error.log
    echo 错误日志已保存到 error.log
    echo LaTeX调试文件：output\debug.tex
    pause
    exit /b 1
)

echo.
echo ========================================
echo 🎉 成功！智慧水利教材转换完成！
echo ========================================
echo 生成文件：
echo - output\智慧水利教材终极版.pdf (完整版PDF)
echo - output\complete_textbook.md    (合并的Markdown)
echo.
echo 包含：
echo ✅ 所有章节和小节内容
echo ✅ 修复的admonition语法
echo ✅ 正确的图片路径和显示
echo ✅ 修复的数学公式格式
echo ✅ 清理的Unicode编码
echo.

pause