#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('修复 GitBook graceful-fs 兼容性问题...');

// 查找所有可能的 graceful-fs 路径
const gracefulFsPaths = [
  // pnpm 路径
  'node_modules\\.pnpm\\npm@5.1.0\\node_modules\\npm\\node_modules\\graceful-fs\\polyfills.js',
  // npm 路径
  'node_modules\\graceful-fs\\polyfills.js',
  'node_modules\\npm\\node_modules\\graceful-fs\\polyfills.js',
  // GitBook 全局路径
  path.join(process.env.APPDATA || process.env.HOME, '.gitbook', 'versions', '3.2.3', 'node_modules', 'graceful-fs', 'polyfills.js')
];

let hasFixed = false;

gracefulFsPaths.forEach(filePath => {
  if (fs.existsSync(filePath)) {
    console.log(`\n找到文件: ${filePath}`);
    
    try {
      let content = fs.readFileSync(filePath, 'utf8');
      let originalContent = content;
      
      // 修复1: cb.apply 问题
      content = content.replace(
        /if \(cb\) cb\.apply\(this, arguments\)/g,
        'if (cb && typeof cb === "function") cb.apply(this, arguments)'
      );
      
      // 修复2: callback.apply 问题
      content = content.replace(
        /if \(callback\) callback\.apply\(this, arguments\)/g,
        'if (callback && typeof callback === "function") callback.apply(this, arguments)'
      );
      
      // 修复3: 其他可能的回调问题
      content = content.replace(
        /(\w+)\.apply\(this, arguments\)/g,
        (match, funcName) => {
          if (funcName === 'cb' || funcName === 'callback') {
            return `${funcName} && typeof ${funcName} === "function" && ${funcName}.apply(this, arguments)`;
          }
          return match;
        }
      );
      
      if (content !== originalContent) {
        // 备份原文件
        fs.writeFileSync(filePath + '.backup', originalContent, 'utf8');
        console.log(`📁 已备份原文件: ${filePath}.backup`);
        
        // 写入修复后的内容
        fs.writeFileSync(filePath, content, 'utf8');
        console.log(`✅ 已修复: ${filePath}`);
        hasFixed = true;
      } else {
        console.log(`ℹ️  无需修复: ${filePath}`);
      }
    } catch (error) {
      console.log(`❌ 修复失败: ${filePath} - ${error.message}`);
    }
  }
});

if (!hasFixed) {
  console.log('\n🔍 未找到需要修复的 graceful-fs 文件。');
  console.log('可能的解决方案：');
  console.log('1. 降级 Node.js 到 v16 或 v18');
  console.log('2. 使用 HonKit 替代 GitBook');
  console.log('3. 手动查找并修复 graceful-fs');
}

console.log('\n修复完成！');
console.log('现在可以尝试运行：');
console.log('gitbook install');
console.log('gitbook serve'); 