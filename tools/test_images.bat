@echo off
chcp 65001
echo ====================================
echo 测试图片路径修复效果
echo ====================================

echo.
echo 第一步：重新合并内容（包含图片路径修复）...
python merge_chapters.py

echo.
echo 第二步：检查修复后的图片路径...
findstr /n "images/" output\complete_textbook.md | head -5

echo.
echo 第三步：复制图片到工具目录方便访问...
if not exist docs mkdir docs
if not exist docs\chapters mkdir docs\chapters
xcopy ..\docs\chapters\images docs\chapters\images /e /i /y >nul 2>&1

echo.
echo 第四步：测试PDF生成（包含图片）...
pandoc output\complete_textbook.md --defaults textbook-config.yaml -o output\测试图片.pdf
if %errorlevel% neq 0 (
    echo 错误：PDF生成失败
    pause
    exit /b 1
)

echo.
echo 成功！生成了包含图片的PDF文件：
echo - output\测试图片.pdf

echo.
echo 图片处理信息：
dir docs\chapters\images\chapter02 /b | wc -l 2>nul || echo "图片目录已创建"

pause