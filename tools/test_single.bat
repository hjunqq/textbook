@echo off
chcp 65001
echo ====================================
echo 智慧水利教材转换器 - 单章节测试
echo ====================================

echo.
echo 第一步：测试单章节转换...
pandoc test_single_chapter.md --defaults test-config.yaml -o test_output.pdf
if %errorlevel% neq 0 (
    echo 错误：PDF生成失败
    pause
    exit /b 1
)

echo.
echo 第二步：生成LaTeX源文件...
pandoc test_single_chapter.md --defaults test-config.yaml -o test_output.tex
if %errorlevel% neq 0 (
    echo 错误：LaTeX生成失败
    pause
    exit /b 1
)

echo.
echo 测试完成！生成的文件：
echo - test_output.pdf
echo - test_output.tex
echo.
pause