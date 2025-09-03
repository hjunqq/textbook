@echo off
chcp 65001
echo ====================================
echo 测试最终修复版本
echo ====================================

echo.
echo 第一步：运行最终修复脚本...
python final_math_fix.py

if not exist output\final_fixed_textbook.md (
    echo ❌ 最终修复失败
    pause
    exit /b 1
)

echo.
echo 第二步：测试PDF生成...
pandoc output\final_fixed_textbook.md --defaults simple-config.yaml -o "output\智慧水利教材_最终版.pdf" 2>final_pdf_error.txt

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 🎉🎉🎉 成功生成PDF！🎉🎉🎉
    echo ========================================
    for %%f in ("output\智慧水利教材_最终版.pdf") do echo PDF大小: %%~zf 字节
    
    echo.
    echo 生成其他格式...
    pandoc output\final_fixed_textbook.md -t docx -o "output\智慧水利教材_最终版.docx" --toc 2>nul
    pandoc output\final_fixed_textbook.md -t html -o "output\智慧水利教材_最终版.html" --toc --standalone --mathjax 2>nul
    echo ✅ 所有格式生成完成
    
) else (
    echo.
    echo ❌ PDF生成仍然失败，查看详细错误...
    echo.
    echo === 错误信息 ===
    type final_pdf_error.txt
    echo.
    
    echo === 分析可能问题 ===
    findstr /c:"Missing" final_pdf_error.txt >nul && echo - 仍有数学公式语法错误
    findstr /c:"Undefined" final_pdf_error.txt >nul && echo - 有未定义的命令
    findstr /c:"Extra" final_pdf_error.txt >nul && echo - 有多余的符号
    
    echo.
    echo === 生成LaTeX调试文件 ===
    pandoc output\final_fixed_textbook.md --defaults simple-config.yaml -o output\final_debug.tex 2>nul
    echo LaTeX调试文件已生成: output\final_debug.tex
    
    echo.
    echo === 搜索问题行 ===
    findstr /n "Missing" final_pdf_error.txt
    findstr /n "frac" final_pdf_error.txt | head -5
    
)

echo.
echo 第三步：检查修复统计...
if exist output\final_report.md (
    type output\final_report.md
) else (
    echo 修复报告不存在
)

echo.
pause