@echo off
chcp 65001
echo ====================================
echo 智慧水利教材转换器环境检查
echo ====================================

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未找到，尝试其他方式...
    py --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ 未找到Python环境
        echo 请确保Python已正确安装并添加到PATH
        goto :end
    ) else (
        echo ✅ 找到Python（通过py命令）
        set PYTHON_CMD=py
    )
) else (
    echo ✅ 找到Python
    set PYTHON_CMD=python
)

echo.
echo 正在检查Pandoc...
pandoc --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Pandoc未找到
    echo 请从 https://pandoc.org/installing.html 安装Pandoc
) else (
    echo ✅ Pandoc已安装
)

echo.
echo 正在检查XeLaTeX...
xelatex --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  XeLaTeX未找到（PDF编译可能失败）
    echo 可选：安装TeX Live或MiKTeX
) else (
    echo ✅ XeLaTeX已安装
)

echo.
echo 正在检查文件结构...
if exist "..\..\docs\chapters" (
    echo ✅ 发现章节目录
    dir /b "..\..\docs\chapters" | find "chapter" >nul
    if errorlevel 1 (
        echo ⚠️  未找到章节文件
    ) else (
        echo ✅ 发现章节文件
    )
) else (
    echo ❌ 未找到章节目录: ..\..\docs\chapters
)

echo.
echo 正在检查脚本文件...
if exist "智慧水利教材终极转换器.py" (
    echo ✅ 转换器脚本存在
) else (
    echo ❌ 转换器脚本缺失
)

if exist "教材质量检查器.py" (
    echo ✅ 质量检查器存在
) else (
    echo ❌ 质量检查器缺失
)

if exist "智慧水利教材配置.json" (
    echo ✅ 配置文件存在
) else (
    echo ❌ 配置文件缺失
)

echo.
echo ====================================
echo 环境检查完成
echo ====================================
echo 如果所有检查都通过，可以运行转换器
echo 使用方法: %PYTHON_CMD% 智慧水利教材终极转换器.py

:end
pause
