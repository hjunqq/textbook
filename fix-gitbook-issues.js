#!/usr/bin/env node

/**
 * 修复 GitBook 在新版本 Node.js 中的兼容性问题
 * 主要解决 graceful-fs 模块的回调函数问题
 */

const fs = require('fs');
const path = require('path');

console.log('修复 GitBook 兼容性问题...');

// 查找 graceful-fs 模块路径
const gracefulFsPaths = [
  path.join(__dirname, 'node_modules', 'graceful-fs', 'polyfills.js'),
  path.join(__dirname, 'node_modules', 'npm', 'node_modules', 'graceful-fs', 'polyfills.js'),
  path.join(process.env.APPDATA || process.env.HOME, '.gitbook', 'versions', '3.2.3', 'node_modules', 'graceful-fs', 'polyfills.js')
];

gracefulFsPaths.forEach(filePath => {
  if (fs.existsSync(filePath)) {
    console.log(`处理文件: ${filePath}`);
    
    try {
      let content = fs.readFileSync(filePath, 'utf8');
      
      // 修复 graceful-fs 的回调问题
      const originalCode = `if (cb) cb.apply(this, arguments)`;
      const fixedCode = `if (cb && typeof cb === 'function') cb.apply(this, arguments)`;
      
      if (content.includes(originalCode)) {
        content = content.replace(new RegExp(originalCode.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), fixedCode);
        fs.writeFileSync(filePath, content, 'utf8');
        console.log(`✅ 已修复: ${filePath}`);
      } else {
        console.log(`ℹ️  无需修复: ${filePath}`);
      }
    } catch (error) {
      console.log(`❌ 修复失败: ${filePath} - ${error.message}`);
    }
  }
});

console.log('修复完成！');
console.log('\n现在可以尝试运行：');
console.log('npm run install');
console.log('npm run serve'); 