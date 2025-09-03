@echo off
chcp 65001
echo ====================================
echo 🚨 紧急测试修复版本
echo ====================================

echo.
echo 第一步：运行紧急修复...
python emergency_fix.py

echo.
echo 第二步：测试紧急修复版本...
if not exist output\emergency_fixed_textbook.md (
    echo ❌ 紧急修复文件不存在
    pause
    exit /b 1
)

echo 文件存在，尝试生成PDF...
pandoc output\emergency_fixed_textbook.md --defaults simple-config.yaml -o "output\智慧水利教材_紧急修复版.pdf" 2>emergency_error.txt

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 🎉🎉🎉 紧急修复成功！PDF生成成功！🎉🎉🎉
    echo ========================================
    
    for %%f in ("output\智慧水利教材_紧急修复版.pdf") do (
        echo PDF大小: %%~zf 字节
        set pdf_size=%%~zf
    )
    
    echo.
    echo 快速生成其他格式...
    pandoc output\emergency_fixed_textbook.md -t docx -o "output\智慧水利教材_紧急修复版.docx" --toc
    pandoc output\emergency_fixed_textbook.md -t html -o "output\智慧水利教材_紧急修复版.html" --toc --standalone --mathjax
    
    echo ✅ 所有格式生成完成！
    echo.
    dir output\智慧水利教材_紧急修复版.*
    
) else (
    echo.
    echo ❌ 还是失败，查看错误...
    echo.
    type emergency_error.txt
    
    echo.
    echo 🔍 搜索具体错误位置...
    findstr /n "Missing.*inserted" emergency_error.txt
    findstr /n "l\." emergency_error.txt
    
    echo.
    echo 💡 可能的解决方案：
    echo 1. 可能还有其他嵌套$$问题
    echo 2. 可能有不匹配的单个$符号
    echo 3. 可能有特殊字符问题
    
    echo.
    echo 生成调试文件分析...
    pandoc output\emergency_fixed_textbook.md --defaults simple-config.yaml -o output\emergency_debug.tex
    echo 调试文件: output\emergency_debug.tex
)

echo.
pause