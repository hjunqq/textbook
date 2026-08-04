#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

# 所有参考文献（从之前的grep输出中提取）
all_refs_text = {
    1: """
{[}1{]} IEEE Computer Society. IEEE Standard Glossary of Software Engineering Terminology{[}S{]}. IEEE Std 610.12-1990. New York: IEEE, 1990.

{[}2{]} Sommerville I. Software Engineering{[}M{]}. 10th Edition. Boston: Pearson, 2015.

{[}3{]} Pressman R S, Maxim B R. Software Engineering: A Practitioner's Approach{[}M{]}. 8th Edition. New York: McGraw-Hill Education, 2014.

{[}4{]} 张海藩, 牟永敏. 软件工程导论{[}M{]}. 6版. 北京: 清华大学出版社, 2013.

{[}5{]} ISO/IEC 25010:2011. Systems and software engineering --- Systems and software Quality Requirements and Evaluation (SQuaRE) --- System and software quality models{[}S{]}. Geneva: ISO, 2011.

{[}6{]} 杨芙清, 梅宏, 吕建. 软件工程技术发展思辨{[}J{]}. 软件学报, 2014, 25(1): 1-25.

{[}7{]} Brooks F P. No Silver Bullet: Essence and Accidents of Software Engineering{[}J{]}. Computer, 1987, 20(4): 10-19.

{[}8{]} 国家质量技术监督局. GB/T 16260.1-2006 软件工程 产品质量 第1部分：质量模型{[}S{]}. 北京: 中国标准出版社, 2006.
""",
    6: """
{[}1{]} Khronos Group. WebGL 2.0 Specification{[}S{]}. Khronos Group Inc, 2017.

{[}2{]} Dirksen J. Learn Three.js: Programming 3D animations and visualizations for the web with HTML5 and WebGL{[}M{]}. 4th ed.~Birmingham: Packt Publishing, 2023.

{[}3{]} Angel E, Shreiner D. Interactive Computer Graphics: A Top-Down Approach with WebGL{[}M{]}. 7th ed.~Boston: Pearson, 2014.

{[}4{]} Akenine-Möller T, Haines E, Hoffman N. Real-Time Rendering{[}M{]}. 4th ed.~Boca Raton: CRC Press, 2018.

{[}5{]} Marschner S, Shirley P. Fundamentals of Computer Graphics{[}M{]}. 5th ed.~Boca Raton: CRC Press, 2021.
""",
    7: """
{[}1{]} Three.js Development Team. Three.js Documentation{[}EB/OL{]}. {[}2024-08-27{]}. https://threejs.org/docs/.

{[}2{]} Chart.js Team. Chart.js Documentation{[}EB/OL{]}. {[}2024-08-27{]}. https://www.chartjs.org/docs/.

{[}3{]} WebGL Working Group. WebGL Specification{[}S{]}. Khronos Group, 2023.
""",
    8: """
{[}1{]} 中华人民共和国水利部. 水利工程安全监测技术规范{[}S{]}. 北京: 中国水利水电出版社, 2022.

{[}2{]} Three.js Development Team. Three.js Documentation{[}EB/OL{]}. {[}2024-08-27{]}. https://threejs.org/docs/.

{[}3{]} Spring Boot Team. Spring Boot Reference Documentation{[}EB/OL{]}. {[}2024-08-27{]}. https://spring.io/projects/spring-boot.

{[}4{]} 张三丰, 李四. 智慧水利平台设计与实现{[}M{]}. 北京: 中国水利水电出版社, 2023.

{[}5{]} Docker Inc. Docker Documentation{[}EB/OL{]}. {[}2024-08-27{]}. https://docs.docker.com/.

{[}6{]} Apache Software Foundation. Apache Kafka Documentation{[}EB/OL{]}. {[}2024-08-27{]}. https://kafka.apache.org/documentation/.
"""
}

# 创建全局引用字典（去重）
global_refs = {}
ref_id_counter = 1

def parse_and_store_refs(text, chapter):
    """解析参考文献文本并存储到全局字典"""
    global ref_id_counter
    
    # 匹配 {[}N{]} 格式的引用
    pattern = r'\{\[\}(\d+)\{\]\}\s+(.*?)(?=\{\[\}|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    for _, ref_text in matches:
        ref_text = ref_text.strip()
        # 检查是否已存在
        if ref_text not in global_refs:
            global_refs[ref_text] = f"ref{ref_id_counter}"
            ref_id_counter += 1

# 解析所有章节的参考文献
for chapter, text in all_refs_text.items():
    parse_and_store_refs(text, chapter)

print(f"Total unique references found: {len(global_refs)}")
print("\nReference texts:")
for i, (text, key) in enumerate(global_refs.items(), 1):
    print(f"{i}. {key}: {text[:100]}...")

