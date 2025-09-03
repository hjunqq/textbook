@echo off
chcp 65001
echo ====================================
echo 智慧水利教材转换器 - 简化测试
echo ====================================

echo.
echo 第一步：生成LaTeX文件查看问题...
pandoc test_single_chapter.md --defaults test-config.yaml -o test_output.tex
if %errorlevel% neq 0 (
    echo 错误：LaTeX生成失败
    pause
    exit /b 1
)

echo.
echo LaTeX文件已生成，请查看 test_output.tex 的内容
echo 按任意键继续尝试PDF生成...
pause

echo.
echo 第二步：尝试最简单的PDF转换...
pandoc test_single_chapter.md -f markdown -t pdf --pdf-engine=xelatex -V CJKmainfont="Microsoft YaHei" -V geometry:margin=25mm -o test_simple.pdf
if %errorlevel% neq 0 (
    echo 错误：简化PDF生成失败
    pause
    exit /b 1
)

echo.
echo 成功！生成的文件：
echo - test_output.tex (查看LaTeX源码)
echo - test_simple.pdf (简化版PDF)
echo.
pause