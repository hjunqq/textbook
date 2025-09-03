@echo off
chcp 65001
echo ====================================
echo 测试正确修复版本的PDF生成
echo ====================================

echo.
echo 第一步：检查修复效果...
if not exist output\properly_fixed_textbook.md (
    echo ❌ 修复文件不存在，请先运行 proper_math_fix.py
    pause
    exit /b 1
)

echo ✅ 正确修复文件存在
for %%f in (output\properly_fixed_textbook.md) do echo 文件大小: %%~zf 字节

echo.
echo 第二步：生成PDF（使用正确修复的数学公式）...
pandoc output\properly_fixed_textbook.md --defaults simple-config.yaml -o "output\智慧水利教材_正确修复版.pdf"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 🎉🎉🎉 成功！数学公式修复生效！🎉🎉🎉
    echo ========================================
    for %%f in ("output\智慧水利教材_正确修复版.pdf") do echo PDF大小: %%~zf 字节
    
    echo.
    echo 生成其他格式：
    echo 生成Word版本...
    pandoc output\properly_fixed_textbook.md -f markdown -t docx -o "output\智慧水利教材_正确修复版.docx" --toc 2>nul
    if %errorlevel% equ 0 (
        echo ✅ Word版本生成成功
        for %%f in ("output\智慧水利教材_正确修复版.docx") do echo Word大小: %%~zf 字节
    )
    
    echo 生成HTML版本...
    pandoc output\properly_fixed_textbook.md -f markdown -t html -o "output\智慧水利教材_正确修复版.html" --toc --standalone --mathjax 2>nul
    if %errorlevel% equ 0 (
        echo ✅ HTML版本生成成功
        for %%f in ("output\智慧水利教材_正确修复版.html") do echo HTML大小: %%~zf 字节
    )
    
) else (
    echo.
    echo ❌ PDF生成失败，生成调试信息...
    pandoc output\properly_fixed_textbook.md --defaults simple-config.yaml -o output\proper_debug.tex 2>proper_error.txt
    
    echo 错误信息：
    type proper_error.txt
    
    echo.
    echo 检查是否还有数学公式问题：
    findstr /c:"Missing" proper_error.txt >nul && echo ⚠️ 仍有数学公式语法错误
    findstr /c:"sqrt" proper_error.txt >nul && echo ⚠️ sqrt命令仍有问题  
    findstr /c:"frac" proper_error.txt >nul && echo ⚠️ frac命令仍有问题
)

echo.
echo 第三步：验证数学公式修复效果...
echo 检查修复前后对比：

echo 验证第二章.md的图片引用数量:
grep -c "images/" 第二章.md

echo -e "\n检查是否还有base64残留:"
grep -c "data:image" 第二章.md

echo.
pause