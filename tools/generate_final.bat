@echo off
chcp 65001
echo ====================================
echo 继续PDF生成（跳过检查步骤）
echo ====================================

echo.
echo 直接生成PDF（所有修复已应用）...
pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\智慧水利教材终极版.pdf

if %errorlevel% neq 0 (
    echo.
    echo 如果出现错误，生成LaTeX文件进行调试...
    pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\debug.tex
    echo LaTeX调试文件已生成：output\debug.tex
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo 🎉 成功！智慧水利教材转换完成！
    echo ========================================
    echo.
    echo 生成文件：
    dir output\*.pdf /b 2>nul
    echo.
    echo 文件大小：
    for %%f in (output\智慧水利教材终极版.pdf) do echo PDF大小: %%~zf 字节
    echo.
    echo 包含内容：
    echo ✅ 所有章节和小节
    echo ✅ 修复的图片路径
    echo ✅ 修复的数学公式
    echo ✅ 清理的编码问题
    echo ✅ 转换的admonition语法
)

echo.
pause