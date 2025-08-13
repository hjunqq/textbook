@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ========================================
REM LaTeX后处理优化脚本
REM 基于最佳实践优化Pandoc生成的LaTeX代码
REM 版本: v1.0
REM 创建时间: 2025年8月7日
REM ========================================

echo ========================================
echo     LaTeX代码后处理优化工具
echo ========================================
echo.

echo 开始优化LaTeX文件...
echo.

REM 处理所有章节目录
for /d %%d in (chapters\*) do (
    echo 处理目录: %%d
    
    REM 处理该目录下所有.tex文件
    for %%f in ("%%d\*.tex") do (
        echo   优化文件: %%f
        
        REM 备份原文件
        copy "%%f" "%%f.bak" >nul
        
        REM 优化LaTeX代码
        powershell -Command "
            $content = Get-Content '%%f' -Encoding UTF8 -Raw
            
            # 1. 处理中文标点
            $content = $content -replace '，', '，'
            $content = $content -replace '。', '。'
            $content = $content -replace '：', '：'
            $content = $content -replace '；', '；'
            $content = $content -replace '？', '？'
            $content = $content -replace '！', '！'
            
            # 2. 处理代码块
            $content = $content -replace '\\begin{verbatim}', '\\begin{lstlisting}'
            $content = $content -replace '\\end{verbatim}', '\\end{lstlisting}'
            
            # 3. 处理列表
            $content = $content -replace '^\\item (.+)$', '\\item $1', 'Multiline'
            
            # 4. 处理特殊字符转义
            $content = $content -replace '([^\\])&', '$1\\&'
            $content = $content -replace '([^\\])%', '$1\\%'
            $content = $content -replace '([^\\])\$', '$1\\$'
            
            # 5. 处理图片引用
            $content = $content -replace '\\includegraphics\{([^}]+)\}', '\\includegraphics[width=0.8\\textwidth]{$1}'
            
            # 6. 优化段落间距
            $content = $content -replace '\n\n\n+', '\n\n'
            
            # 7. 添加中文支持
            if ($content -notmatch '\\usepackage\{ctex\}') {
                $content = '\\usepackage{ctex}' + \"`n\" + $content
            }
            
            # 保存优化后的内容
            [System.IO.File]::WriteAllText('%%f', $content, [System.Text.Encoding]::UTF8)
        "
    )
)

echo.
echo 优化完成！
echo.
echo 优化内容包括：
echo - 中文标点符号规范化
echo - 代码块格式统一
echo - 特殊字符转义处理
echo - 图片尺寸优化
echo - 段落间距调整
echo - 中文支持增强
echo.

echo 原文件已备份为 .bak 文件
echo 如需恢复，可以删除 .tex 文件并将 .bak 重命名为 .tex
echo.

:end
pause
