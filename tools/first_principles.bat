@echo off
chcp 65001
echo ====================================
echo 第一性原理：直接生成最干净的PDF
echo ====================================

echo.
echo 创建最基础的测试文件...
echo # 智慧水利教材测试 > output\test_clean.md
echo. >> output\test_clean.md
echo ## 第一章 概述 >> output\test_clean.md
echo. >> output\test_clean.md
echo 这是一个基础的测试文档。 >> output\test_clean.md
echo. >> output\test_clean.md
echo 数学公式测试： >> output\test_clean.md
echo. >> output\test_clean.md
echo $$\sigma = \sqrt{\frac{1}{N}\sum_{i=1}^{N} (Z_i - z_i)^2}$$ >> output\test_clean.md
echo. >> output\test_clean.md

echo 第一步：测试最基础的转换...
pandoc output\test_clean.md --pdf-engine=xelatex -V CJKmainfont="Microsoft YaHei" -o output\test_basic.pdf

if %errorlevel% neq 0 (
    echo 基础测试失败，pandoc或LaTeX环境有问题
    pause
    exit /b 1
) else (
    echo ✅ 基础测试成功
)

echo.
echo 第二步：测试没有数学公式的完整文档...
python -c "
import re
from pathlib import Path

# 读取原始合并文件
with open('output/math_fixed_textbook.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 移除所有数学公式，用文字说明替代
content = re.sub(r'\$[^$]*\$', '[数学公式]', content)
content = re.sub(r'\$\$[^$]*\$\$', '[数学公式块]', content)

# 保存无数学版本
with open('output/no_math_textbook.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('无数学公式版本已创建')
"

pandoc output\no_math_textbook.md --defaults simple-config.yaml -o output\智慧水利教材_无数学版.pdf

if %errorlevel% neq 0 (
    echo 无数学版本也失败，说明不是数学公式问题
    pause
    exit /b 1
) else (
    echo ✅ 无数学版本成功，确认是数学公式问题
)

echo.
echo 第三步：重新处理数学公式...
python -c "
import re
from pathlib import Path

with open('output/math_fixed_textbook.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 彻底重新格式化数学公式
def fix_math_thoroughly(content):
    # 移除所有现有的数学标记
    content = re.sub(r'\$([^$]+)\$', r'MATHSTART\1MATHEND', content)
    
    # 清理数学内容
    def clean_math(match):
        math_content = match.group(1)
        # 移除多余的大括号和斜体标记
        math_content = re.sub(r'\*([^*]+)\*', r'\1', math_content)
        math_content = re.sub(r'\{+([^{}]+)\}+', r'{\1}', math_content)
        return f'\${math_content}\$'
    
    content = re.sub(r'MATHSTART([^M]+?)MATHEND', clean_math, content)
    return content

clean_content = fix_math_thoroughly(content)

with open('output/ultra_clean_textbook.md', 'w', encoding='utf-8') as f:
    f.write(clean_content)
print('超级清理版本已创建')
"

pandoc output\ultra_clean_textbook.md --defaults simple-config.yaml -o output\智慧水利教材_超级清理版.pdf

if %errorlevel% equ 0 (
    echo.
    echo 🎉🎉🎉 终于成功了！🎉🎉🎉
    for %%f in (output\智慧水利教材_超级清理版.pdf) do echo PDF大小: %%~zf 字节
) else (
    echo 还是有问题，需要更深入分析
    pandoc output\ultra_clean_textbook.md --defaults simple-config.yaml -o output\ultra_debug.tex
    echo 请查看: output\ultra_debug.tex
)

pause