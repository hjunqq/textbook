#!/usr/bin/env python3
import re

content = """# 第一章 智慧水利平台概述

## 学习目标

通过本章学习，学生将能够：
- 理解智慧水利平台的基本概念和核心价值
- 掌握智慧水利平台的体系架构设计原则

## 关键概念

**数字孪生**：通过数字化手段对物理实体进行建模。
**物联网**：通过各种信息传感设备实现物物相连。

## 实践练习

请完成以下练习：
1. 搭建基本的开发环境
2. 配置数据库连接

## 本章小结

本章介绍了智慧水利平台的基本概念。"""

# 测试正则表达式 - 使用非贪婪匹配
patterns = {
    'learning_objectives': r'## 学习目标\s*\n(.*?)(?=\n## |\Z)',
    'key_points': r'## 关键概念\s*\n(.*?)(?=\n## |\Z)',
    'practice_exercise': r'## 实践练习\s*\n(.*?)(?=\n## |\Z)',
    'chapter_summary': r'## 本章小结\s*\n(.*?)(?=\n## |\Z)'
}

print("原始内容:")
print(content)
print("\n" + "="*50 + "\n")

for env_type, pattern in patterns.items():
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
    if matches:
        print(f"{env_type} 匹配:")
        for i, match in enumerate(matches):
            print(f"  匹配 {i+1}: {repr(match)}")
        print()