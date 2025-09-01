#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文内容测试器 - 快速测试中文转换效果
"""

import subprocess
from pathlib import Path

def create_chinese_test():
    """创建中文测试文件"""
    print("🧪 创建中文测试文档")
    print("=" * 30)
    
    # 中文测试内容
    chinese_test = """# 智慧水利平台架构与开发

## 第一章 概述

### 1.1 基本概念

**智慧水利**是运用物联网、云计算、大数据、人工智能等现代信息技术，对水利工程进行智能化管理和运维的新模式。

主要特点包括：

1. **数据驱动**：基于海量数据分析决策
2. **智能预警**：实时监测水情变化
3. **精准调度**：优化水资源配置
4. **协同管理**：多部门信息共享

### 1.2 技术架构

系统采用**分层架构**设计：

- **感知层**：传感器网络、监测设备
- **网络层**：通信传输、数据传递  
- **数据层**：数据存储、处理分析
- **应用层**：业务功能、用户界面

```python
# 数据采集示例代码
class WaterDataCollector:
    def __init__(self, station_id):
        self.station_id = station_id
        self.sensors = []
    
    def collect_data(self):
        \"\"\"采集水位、流量数据\"\"\"
        data = {
            '时间': datetime.now(),
            '水位': self.get_water_level(),
            '流量': self.get_flow_rate(),
            '温度': self.get_temperature()
        }
        return data
    
    def get_water_level(self):
        # 获取水位数据
        return 125.6  # 单位：米
```

### 1.3 发展趋势

智慧水利发展呈现以下趋势：

> **重要提示**：数字化转型是水利现代化的必由之路。

**发展方向**：
- 🌊 全流域一体化管理
- 🤖 人工智能深度应用  
- 📱 移动端智能服务
- 🔗 区块链技术应用

## 第二章 系统设计

### 2.1 需求分析

根据水利部门实际需求，系统需要实现：

1. **实时监测**：24小时不间断监控
2. **预警预报**：提前发现风险隐患
3. **决策支持**：辅助管理决策
4. **应急响应**：快速处置突发事件

### 2.2 数据库设计

核心数据表包括：

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| stations | 监测站点 | 站点ID、名称、位置、类型 |
| sensors | 传感器信息 | 设备ID、型号、参数、状态 |
| water_data | 水文数据 | 时间、水位、流量、降雨量 |
| alerts | 预警信息 | 预警级别、内容、处理状态 |

```sql
-- 创建水文数据表
CREATE TABLE water_data (
    id BIGINT PRIMARY KEY,
    station_id VARCHAR(50) NOT NULL COMMENT '站点ID',
    measure_time DATETIME NOT NULL COMMENT '监测时间',
    water_level DECIMAL(10,2) COMMENT '水位(米)',
    flow_rate DECIMAL(15,2) COMMENT '流量(立方米/秒)',
    rainfall DECIMAL(10,2) COMMENT '降雨量(毫米)',
    temperature DECIMAL(5,2) COMMENT '水温(摄氏度)',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 小结

本章介绍了智慧水利的基本概念、技术架构和发展趋势，为后续章节的深入学习奠定了基础。

---

*注：本文档用于测试中文LaTeX转换效果*
"""
    
    # 保存测试文件
    script_dir = Path(__file__).parent
    output_dir = script_dir / 'output'
    output_dir.mkdir(exist_ok=True)
    
    test_file = output_dir / 'chinese_test.md'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(chinese_test)
    
    print(f"✅ 测试文件创建: {test_file}")
    print(f"📊 文件大小: {len(chinese_test)} 字符")
    
    return test_file

def test_pandoc_chinese(test_file):
    """测试Pandoc中文转换"""
    print(f"\n🔄 测试Pandoc中文转换")
    
    output_dir = test_file.parent
    template_file = output_dir.parent / 'templates' / 'chinese.tex'
    
    # 测试LaTeX转换
    print("📄 测试1: 转换为LaTeX...")
    latex_file = output_dir / 'chinese_test.tex'
    
    cmd = [
        'pandoc', 'chinese_test.md',
        '-o', 'chinese_test.tex',
        '--from=markdown',
        '--to=latex',
        '--template', '../templates/chinese.tex',
        '--standalone',
        '--toc'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, 
                              cwd=output_dir, encoding='utf-8')
        
        if result.returncode == 0 and latex_file.exists():
            print(f"  ✅ LaTeX转换成功 ({latex_file.stat().st_size} bytes)")
            
            # 检查生成的LaTeX文件中的中文
            with open(latex_file, 'r', encoding='utf-8') as f:
                latex_content = f.read()
            
            chinese_chars = sum(1 for c in latex_content if '\u4e00' <= c <= '\u9fff')
            print(f"  📝 LaTeX文件包含 {chinese_chars} 个中文字符")
            
        else:
            print(f"  ❌ LaTeX转换失败")
            if result.stderr:
                print(f"  错误: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"  ❌ 转换异常: {e}")
        return False
    
    # 测试PDF转换 (如果XeLaTeX可用)
    print("🎯 测试2: 转换为PDF...")
    try:
        # 检查XeLaTeX
        xelatex_check = subprocess.run(['xelatex', '--version'], 
                                     capture_output=True, text=True)
        if xelatex_check.returncode != 0:
            print("  ⚠️  XeLaTeX不可用，跳过PDF测试")
            return True
        
        # 编译PDF
        pdf_result = subprocess.run(['xelatex', '-interaction=nonstopmode', 
                                   'chinese_test.tex'],
                                  capture_output=True, text=True,
                                  cwd=output_dir, encoding='gbk', errors='ignore')  # 修复：使用GBK编码
        
        pdf_file = output_dir / 'chinese_test.pdf'
        if pdf_result.returncode == 0 and pdf_file.exists():
            size_mb = pdf_file.stat().st_size / 1024 / 1024
            print(f"  ✅ PDF生成成功 ({size_mb:.2f} MB)")
            return True
        else:
            print(f"  ❌ PDF编译失败")
            print(f"  💡 检查字体安装: SimSun, SimHei, FangSong")
            return False
            
    except Exception as e:
        print(f"  ❌ PDF测试异常: {e}")
        return False

def main():
    """主函数"""
    print("🧪 中文LaTeX转换测试工具")
    print("=" * 40)
    
    # 创建测试文件
    test_file = create_chinese_test()
    
    # 测试转换
    success = test_pandoc_chinese(test_file)
    
    if success:
        print(f"\n🎉 中文转换测试通过！")
        print(f"💡 可以放心使用 convert_chinese.bat")
    else:
        print(f"\n❌ 中文转换测试失败")
        print(f"💡 建议检查:")
        print(f"   1. Pandoc版本 (建议2.0+)")
        print(f"   2. XeLaTeX安装")
        print(f"   3. 中文字体安装")
    
    print(f"\n📁 测试文件位置: {test_file.parent}")

if __name__ == '__main__':
    main()