#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

# 原始参考文献数据
references = [
    # Chapter 1
    ("IEEE1990", "IEEE Computer Society. IEEE Standard Glossary of Software Engineering Terminology. IEEE Std 610.12-1990. New York: IEEE, 1990."),
    ("sommerville2015", "Sommerville I. Software Engineering. 10th Edition. Boston: Pearson, 2015."),
    ("pressman2014", "Pressman R S, Maxim B R. Software Engineering: A Practitioner's Approach. 8th Edition. New York: McGraw-Hill Education, 2014."),
    ("zhang2013", "张海藩, 牟永敏. 软件工程导论. 6版. 北京: 清华大学出版社, 2013."),
    ("ISO25010", "ISO/IEC 25010:2011. Systems and software engineering --- Systems and software Quality Requirements and Evaluation (SQuaRE) --- System and software quality models. Geneva: ISO, 2011."),
    ("yang2014", "杨芙清, 梅宏, 吕建. 软件工程技术发展思辨. 软件学报, 2014, 25(1): 1-25."),
    ("brooks1987", "Brooks F P. No Silver Bullet: Essence and Accidents of Software Engineering. Computer, 1987, 20(4): 10-19."),
    ("GB2006", "国家质量技术监督局. GB/T 16260.1-2006 软件工程 产品质量 第1部分：质量模型. 北京: 中国标准出版社, 2006."),
    
    # Chapter 6
    ("khronos2017", "Khronos Group. WebGL 2.0 Specification. Khronos Group Inc, 2017."),
    ("dirksen2023", "Dirksen J. Learn Three.js: Programming 3D animations and visualizations for the web with HTML5 and WebGL. 4th ed. Birmingham: Packt Publishing, 2023."),
    ("angel2014", "Angel E, Shreiner D. Interactive Computer Graphics: A Top-Down Approach with WebGL. 7th ed. Boston: Pearson, 2014."),
    ("akenine2018", "Akenine-Möller T, Haines E, Hoffman N. Real-Time Rendering. 4th ed. Boca Raton: CRC Press, 2018."),
    ("marschner2021", "Marschner S, Shirley P. Fundamentals of Computer Graphics. 5th ed. Boca Raton: CRC Press, 2021."),
    
    # Chapter 7
    ("threejs", "Three.js Development Team. Three.js Documentation. Retrieved 2024-08-27 from https://threejs.org/docs/"),
    ("chartjs", "Chart.js Team. Chart.js Documentation. Retrieved 2024-08-27 from https://www.chartjs.org/docs/"),
    ("webglspec2023", "WebGL Working Group. WebGL Specification. Khronos Group, 2023."),
    
    # Chapter 8
    ("water2022", "中华人民共和国水利部. 水利工程安全监测技术规范. 北京: 中国水利水电出版社, 2022."),
    ("springboot", "Spring Boot Team. Spring Boot Reference Documentation. Retrieved 2024-08-27 from https://spring.io/projects/spring-boot"),
    ("zhang2023", "张三丰, 李四. 智慧水利平台设计与实现. 北京: 中国水利水电出版社, 2023."),
    ("docker", "Docker Inc. Docker Documentation. Retrieved 2024-08-27 from https://docs.docker.com/"),
    ("kafka", "Apache Software Foundation. Apache Kafka Documentation. Retrieved 2024-08-27 from https://kafka.apache.org/documentation/"),
]

def create_bibtex_entry(key, text):
    """从文献文本创建BibTeX条目"""
    
    # 书籍类型检测 [M]
    if "[M]" in text or "Edition" in text:
        # 解析书籍信息
        match = re.match(r"(.*?)\.\s+(.*?)\.\s+(.+?)\.\s+(\d{4})\.", text)
        if match:
            authors, title, publisher_info, year = match.groups()
            
            # 进一步解析出版社和地址
            pub_parts = publisher_info.rsplit(":", 1)
            if len(pub_parts) == 2:
                address, publisher = pub_parts
                address = address.split()[-1] if address else ""
            else:
                publisher = publisher_info
                address = ""
            
            entry = f"""@book{{{key},
  author = {{{authors}}},
  title = {{{title}}},
  publisher = {{{publisher}}},
  address = {{{address}}},
  year = {{{year}}}
}}"""
            return entry
    
    # 杂志文章类型 [J]
    if "[J]" in text:
        # 中文文献示例: 杨芙清, 梅宏, 吕建. 软件工程技术发展思辨. 软件学报, 2014, 25(1): 1-25.
        match = re.match(r"(.*?)\.\s+(.*?)\.\s+(.*?),\s+(\d{4}),", text)
        if match:
            authors, title, journal, year = match.groups()
            entry = f"""@article{{{key},
  author = {{{authors}}},
  title = {{{title}}},
  journal = {{{journal}}},
  year = {{{year}}}
}}"""
            return entry
    
    # 标准/技术文献 [S]
    if "[S]" in text or "Standard" in text or "Specification" in text:
        entry = f"""@misc{{{key},
  title = {{{text[:100]}}},
  year = {{2023}}
}}"""
        return entry
    
    # 在线资源 [EB/OL]
    if "https://" in text:
        match = re.search(r"(.*?)\.\s+(Retrieved.*?from\s+)?(https?://\S+)", text)
        if match:
            title, _, url = match.groups()
            entry = f"""@misc{{{key},
  title = {{{title}}},
  howpublished = {{\\url{{{url}}}}},
  year = {{2024}}
}}"""
            return entry
    
    # 默认处理
    entry = f"""@misc{{{key},
  note = {{{text}}}
}}"""
    return entry

# 生成BibTeX文件内容
bibtex_content = "% 智慧水利平台架构与开发 - 参考文献数据库\n"
bibtex_content += "% 自动生成日期: 2024\n\n"

for key, text in references:
    entry = create_bibtex_entry(key, text)
    bibtex_content += entry + "\n\n"

# 保存为文件
with open("references.bib", "w", encoding="utf-8") as f:
    f.write(bibtex_content)

print("BibTeX file created: references.bib")
print(f"Total entries: {len(references)}")

