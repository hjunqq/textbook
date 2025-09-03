@echo off
chcp 65001
echo ====================================
echo 第一性原理：系统化隔离问题
echo ====================================

echo.
echo 步骤1：创建最基础的测试文件...
echo # 智慧水利教材测试 > output\test_clean.md
echo. >> output\test_clean.md
echo ## 第一章 概述 >> output\test_clean.md
echo. >> output\test_clean.md
echo 这是一个基础的测试文档。 >> output\test_clean.md
echo. >> output\test_clean.md
echo 数学公式测试： >> output\test_clean.md
echo. >> output\test_clean.md
echo $$\sigma = \sqrt{\frac{1}{N}\sum_{i=1}^{N} (Z_i - z_i)^2}$$ >> output\test_clean.md

pandoc output\test_clean.md --pdf-engine=xelatex -V CJKmainfont="Microsoft YaHei" -o output\test_basic.pdf

if %errorlevel% neq 0 (
    echo ❌ 基础测试失败，pandoc或LaTeX环境有问题
    pause
    exit /b 1
) else (
    echo ✅ 基础测试成功
)

echo.
echo 步骤2：创建无数学公式版本...
python test_isolate.py no_math

if not exist output\no_math_textbook.md (
    echo ❌ 无数学版本创建失败
    pause
    exit /b 1
)

pandoc output\no_math_textbook.md --defaults simple-config.yaml -o output\智慧水利教材_无数学版.pdf

if %errorlevel% neq 0 (
    echo ❌ 无数学版本转换也失败，说明问题不在数学公式
    echo 问题可能在：文件编码、特殊字符、图片路径等
    pause
    exit /b 1
) else (
    echo ✅ 无数学版本成功！确认问题在数学公式
)

echo.
echo 步骤3：创建超级清理的数学公式版本...
python test_isolate.py ultra_clean

pandoc output\ultra_clean_textbook.md --defaults simple-config.yaml -o output\智慧水利教材_超级清理版.pdf

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 🎉🎉🎉 第一性原理成功！🎉🎉🎉
    echo ========================================
    for %%f in (output\智慧水利教材_超级清理版.pdf) do echo PDF大小: %%~zf 字节
    
    echo.
    echo 生成其他格式：
    pandoc output\ultra_clean_textbook.md -f markdown -t docx -o output\智慧水利教材_超级清理版.docx --toc 2>nul
    echo ✅ Word版本也已生成
    
) else (
    echo ❌ 还是失败，生成调试文件分析...
    pandoc output\ultra_clean_textbook.md --defaults simple-config.yaml -o output\final_debug.tex 2>final_error.txt
    
    echo 错误信息：
    type final_error.txt
    
    echo.
    echo 请提供以下信息以进一步分析：
    echo 1. LaTeX错误的具体行号
    echo 2. final_debug.tex文件中该行的内容
)

echo.
pause