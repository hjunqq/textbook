#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF内容提取工具
用于提取PPT转PDF文件中的文本内容
"""

import sys
import os

def extract_pdf_content():
    """提取PDF文件内容"""
    
    # 检查是否安装了必要的库
    try:
        import PyPDF2
        import pdfplumber
        print("PDF处理库已安装")
    except ImportError:
        print("需要安装PDF处理库:")
        print("pip install PyPDF2 pdfplumber")
        return
    
    # 定义PDF文件路径
    pdf_files = [
        r"e:\2025\教材\智慧水利平台架构与开发\参考\智慧水利平台架构与开发 4 软件开发项目管理.pdf"
    ]
    
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            print(f"\n{'='*60}")
            print(f"处理文件: {os.path.basename(pdf_file)}")
            print('='*60)
            
            try:
                # 使用pdfplumber提取文本
                with pdfplumber.open(pdf_file) as pdf:
                    full_text = []
                    for page_num, page in enumerate(pdf.pages, 1):
                        text = page.extract_text()
                        if text:
                            print(f"\n--- 第 {page_num} 页 ---")
                            print(text)
                            full_text.append(f"第{page_num}页:\n{text}\n")
                        
                        # 限制输出页数避免过长
                        # if page_num >= 10:
                        #     print(f"\n[文件共{len(pdf.pages)}页，已显示前10页]")
                        #     break
                
                # 保存提取的文本到文件
                output_file = pdf_file.replace('.pdf', '_extracted.txt')
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(full_text))
                print(f"\n文本内容已保存到: {output_file}")
                
            except Exception as e:
                print(f"处理文件时出错: {e}")
                
                # 尝试使用PyPDF2作为备选方案
                try:
                    print("尝试使用PyPDF2...")
                    with open(pdf_file, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        text_content = []
                        
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            text = page.extract_text()
                            if text:
                                print(f"\n--- 第 {page_num + 1} 页 ---")
                                print(text)
                                text_content.append(f"第{page_num + 1}页:\n{text}\n")
                        
                        # 保存文本
                        output_file = pdf_file.replace('.pdf', '_PyPDF2_extracted.txt')
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(text_content))
                        print(f"\n文本内容已保存到: {output_file}")
                        
                except Exception as e2:
                    print(f"PyPDF2也失败了: {e2}")
        else:
            print(f"文件不存在: {pdf_file}")

if __name__ == "__main__":
    extract_pdf_content()
