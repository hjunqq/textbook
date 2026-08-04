@echo off
chcp 65001 >nul
echo Testing Fixed Numbering System
echo ===============================

set PYTHONIOENCODING=utf-8

echo Creating test chapter...
echo.

REM Create a simple test chapter with duplicate numbering
echo # 第一章 测试章节 > test_chapter.md
echo. >> test_chapter.md
echo ## 1.1 概述 >> test_chapter.md
echo. >> test_chapter.md
echo 这是概述内容。 >> test_chapter.md
echo. >> test_chapter.md
echo ### 1.1.1 背景 >> test_chapter.md
echo. >> test_chapter.md
echo 背景内容。 >> test_chapter.md
echo. >> test_chapter.md
echo ## 1.2 基本概念 >> test_chapter.md
echo. >> test_chapter.md
echo 基本概念内容。 >> test_chapter.md
echo. >> test_chapter.md
echo ## 本章小结 >> test_chapter.md
echo. >> test_chapter.md
echo 这个应该被删除。 >> test_chapter.md

echo Test chapter created: test_chapter.md

echo.
echo Converting with fixed numbering logic...
echo.

REM Convert to LaTeX with fixed numbering
pandoc test_chapter.md ^
    -o test_chapter_fixed.tex ^
    --from=markdown ^
    --to=latex ^
    --number-sections ^
    --standalone

if %errorlevel% equ 0 (
    echo Conversion successful!
    echo.
    echo Check test_chapter_fixed.tex to see if numbering is correct.
    echo Expected: Only one set of numbers ^(from Pandoc^), no duplicates.
    
    echo.
    echo Key sections to check:
    findstr /C:"section{" test_chapter_fixed.tex
    
) else (
    echo Conversion failed!
)

echo.
pause