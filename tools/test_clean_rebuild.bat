@echo off
chcp 65001
echo 测试完全干净的版本（不修改数学公式）
pandoc output\clean_rebuild.md --defaults simple-config.yaml -o "output\测试_干净版本.pdf" 2>clean_test_error.txt

if %errorlevel% equ 0 (
    echo ? 干净版本成功！
    for %%f in ("output\测试_干净版本.pdf") do echo PDF大小: %%~zf 字节
) else (
    echo ? 干净版本也失败
    type clean_test_error.txt
    echo.
    echo 这说明问题不在数学公式，而在其他地方：
    echo - 文件编码问题
    echo - 特殊字符问题  
    echo - 图片路径问题
    echo - Pandoc配置问题
)
pause