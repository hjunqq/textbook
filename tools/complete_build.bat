@echo off
chcp 65001
echo ========================================
echo 完整解决方案 - 从源文件到最终PDF
echo ========================================

echo.
echo 第一步：生成干净的教材文件...
python complete_solution.py

if not exist output\final_textbook.md (
    echo ❌ 教材文件生成失败
    pause
    exit /b 1
)

echo.
echo 第二步：生成PDF...
pandoc output\final_textbook.md --pdf-engine=xelatex -V CJKmainfont="Microsoft YaHei" --toc --toc-depth=2 -o "output\教材最终版.pdf"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 🎉 成功生成PDF！
    echo ========================================
    
    for %%f in ("output\教材最终版.pdf") do echo PDF大小: %%~zf 字节
    
    echo.
    echo 第三步：生成其他格式...
    pandoc output\final_textbook.md -t docx --toc --toc-depth=2 -o "output\教材最终版.docx"
    echo ✅ Word版本已生成
    
    pandoc output\final_textbook.md -t html --toc --toc-depth=2 --standalone -o "output\教材最终版.html"
    echo ✅ HTML版本已生成
    
    echo.
    echo ========================================
    echo 🎊 全部完成！
    echo ========================================
    echo.
    echo 生成的文件：
    dir output\教材最终版.*
    echo.
    echo 您现在有了：
    echo - PDF版本（用于打印和正式发布）
    echo - Word版本（用于进一步编辑）
    echo - HTML版本（用于在线查看）
    echo.
    echo 所有文件都有正确的章节结构和目录！
    
) else (
    echo.
    echo ❌ PDF生成失败
    echo 检查详细错误信息...
    pandoc output\final_textbook.md --pdf-engine=xelatex -V CJKmainfont="Microsoft YaHei" --toc -o temp.pdf 2>complete_error.txt
    type complete_error.txt
)

echo.
pause