@echo off
chcp 65001
echo ====================================
echo 最小测试 - 确认pandoc基本功能
echo ====================================

echo.
echo 第一步：最基础的转换测试...
pandoc test_minimal.md -o test_minimal.pdf --pdf-engine=xelatex -V CJKmainfont="Microsoft YaHei"

if %errorlevel% neq 0 (
    echo 错误：基础转换失败，请检查：
    echo 1. pandoc是否正确安装
    echo 2. xelatex是否可用
    echo 3. Microsoft YaHei字体是否安装
    pause
    exit /b 1
)

echo 成功！基础转换工作正常
echo 生成文件：test_minimal.pdf

echo.
echo 第二步：生成LaTeX源码检查...
pandoc test_minimal.md -o test_minimal.tex --pdf-engine=xelatex -V CJKmainfont="Microsoft YaHei"

echo 生成文件：test_minimal.tex
echo 请查看生成的文件内容
echo.
pause