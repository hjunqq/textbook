@echo off
chcp 65001
echo ====================================
echo 终极清理：移除所有LaTeX命令
echo ====================================

echo.
echo 第一步：创建完全无LaTeX版本...
python total_cleanup.py

if not exist output\latex_free_textbook.md (
    echo ❌ 清理脚本失败
    pause
    exit /b 1
)

echo.
echo 第二步：检查清理效果...
findstr /c:"\frac\|\\partial\|\\sqrt" output\latex_free_textbook.md >nul
if %errorlevel% equ 0 (
    echo ⚠️ 仍有LaTeX命令残留
) else (
    echo ✅ LaTeX命令清理完成
)

echo.
echo 第三步：测试完全清理版本...
pandoc output\latex_free_textbook.md --defaults simple-config.yaml -o output\智慧水利教材_完全清理版.pdf

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 🎉 问题确认：LaTeX命令是罪魁祸首！
    echo ========================================
    echo.
    for %%f in (output\智慧水利教材_完全清理版.pdf) do echo 清理版PDF大小: %%~zf 字节
    echo.
    echo 现在我们知道问题所在，可以正确修复数学公式了！
    
) else (
    echo.
    echo ❌ 即使完全清理也失败，问题更深层...
    echo 生成调试信息：
    pandoc output\latex_free_textbook.md --defaults simple-config.yaml -o output\cleanup_debug.tex 2>cleanup_error.txt
    
    echo 错误信息：
    type cleanup_error.txt
    
    echo.
    echo 可能的问题：
    echo 1. 文件编码问题
    echo 2. 特殊Unicode字符
    echo 3. 图片路径问题
    echo 4. 其他LaTeX语法问题
)

echo.
pause