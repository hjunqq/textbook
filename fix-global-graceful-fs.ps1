# 修复全局 gitbook-cli 中的 graceful-fs 问题
Write-Host "修复全局 GitBook CLI 中的 graceful-fs 兼容性问题..." -ForegroundColor Green

$gracefulFsPath = "C:\Users\qhjun\AppData\Roaming\nvm\v22.9.0\node_modules\gitbook-cli\node_modules\npm\node_modules\graceful-fs\polyfills.js"

if (Test-Path $gracefulFsPath) {
    Write-Host "找到文件: $gracefulFsPath" -ForegroundColor Yellow
    
    try {
        # 读取文件内容
        $content = Get-Content $gracefulFsPath -Raw
        $originalContent = $content
        
        # 备份原文件
        $backupPath = $gracefulFsPath + ".backup"
        $originalContent | Out-File -FilePath $backupPath -Encoding utf8
        Write-Host "已备份原文件: $backupPath" -ForegroundColor Blue
        
        # 修复 cb.apply 问题
        $content = $content -replace 'if \(cb\) cb\.apply\(this, arguments\)', 'if (cb && typeof cb === "function") cb.apply(this, arguments)'
        
        # 修复 callback.apply 问题
        $content = $content -replace 'if \(callback\) callback\.apply\(this, arguments\)', 'if (callback && typeof callback === "function") callback.apply(this, arguments)'
        
        if ($content -ne $originalContent) {
            # 写入修复后的内容
            $content | Out-File -FilePath $gracefulFsPath -Encoding utf8
            Write-Host "✅ 修复成功: $gracefulFsPath" -ForegroundColor Green
        } else {
            Write-Host "ℹ️  无需修复: $gracefulFsPath" -ForegroundColor Cyan
        }
    }
    catch {
        Write-Host "❌ 修复失败: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "❌ 文件不存在: $gracefulFsPath" -ForegroundColor Red
}

Write-Host "`n修复完成！现在可以尝试运行：" -ForegroundColor Green
Write-Host "gitbook install" -ForegroundColor Yellow
Write-Host "gitbook serve" -ForegroundColor Yellow 