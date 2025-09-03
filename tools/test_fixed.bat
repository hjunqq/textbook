@echo off
chcp 65001
echo ====================================
echo 修复版测试 - 使用简化配置
echo ====================================

echo.
echo 第一步：使用修复的配置文件...
pandoc test_single_chapter.md --defaults test-config-fixed.yaml
if %errorlevel% neq 0 (
    echo 错误：修复配置仍然失败
    pause
    exit /b 1
)

echo.
echo 第二步：生成LaTeX查看结构...
pandoc test_single_chapter.md --defaults test-config-fixed.yaml -o test_fixed.tex

echo.
echo 成功！生成的文件：
echo - test_output.pdf
echo - test_fixed.tex
echo.
pause