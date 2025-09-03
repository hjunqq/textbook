@echo off
chcp 65001
echo ====================================
echo 测试Python合并脚本
echo ====================================

echo.
echo 测试Python环境和合并功能...
python merge_chapters.py

if %errorlevel% neq 0 (
    echo 错误：Python脚本执行失败
    echo 请检查：
    echo 1. Python是否已安装
    echo 2. 文件路径是否正确
    pause
    exit /b 1
)

echo.
echo Python合并脚本测试成功！
echo 查看生成的合并文件：

if exist output\complete_textbook.md (
    echo.
    echo 文件已生成，大小：
    for %%f in (output\complete_textbook.md) do echo %%~zf 字节
    
    echo.
    echo 前50行预览：
    echo ----------------------------------------
    more /e +1 output\complete_textbook.md | head -50
    echo ----------------------------------------
) else (
    echo 错误：合并文件未生成
)

echo.
pause