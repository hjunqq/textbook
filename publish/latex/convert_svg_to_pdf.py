#!/usr/bin/env python3
"""
SVG到PDF转换脚本
用于LaTeX编译前批量转换SVG图像文件
"""

import os
import subprocess
import sys
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_inkscape():
    """查找Inkscape可执行文件"""
    possible_paths = [
        "inkscape",
        "C:\\Program Files\\Inkscape\\bin\\inkscape.exe",
        "C:\\Program Files (x86)\\Inkscape\\bin\\inkscape.exe",
        "C:\\Users\\%USERNAME%\\AppData\\Local\\Inkscape\\bin\\inkscape.exe"
    ]
    
    for path in possible_paths:
        try:
            # 展开环境变量
            expanded_path = os.path.expandvars(path)
            subprocess.run([expanded_path, "--version"], 
                         capture_output=True, check=True, timeout=10)
            logger.info(f"找到Inkscape: {expanded_path}")
            return expanded_path
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return None

def convert_svg_to_pdf(svg_file, pdf_file, inkscape_path):
    """使用Inkscape将SVG转换为PDF"""
    try:
        cmd = [
            inkscape_path,
            "--export-type=pdf",
            f"--export-filename={pdf_file}",
            str(svg_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info(f"成功转换: {svg_file} -> {pdf_file}")
            return True
        else:
            logger.error(f"转换失败: {svg_file}")
            logger.error(f"错误信息: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"转换超时: {svg_file}")
        return False
    except Exception as e:
        logger.error(f"转换异常: {svg_file} - {str(e)}")
        return False

def batch_convert_svg_to_pdf(base_dir):
    """批量转换SVG文件为PDF"""
    base_path = Path(base_dir)
    
    # 查找Inkscape
    inkscape_path = find_inkscape()
    if not inkscape_path:
        logger.error("未找到Inkscape，请确保已安装Inkscape并添加到PATH")
        logger.info("可以从 https://inkscape.org/release/ 下载安装Inkscape")
        return False
    
    # 查找所有SVG文件
    svg_files = list(base_path.rglob("*.svg"))
    
    if not svg_files:
        logger.info("未找到SVG文件")
        return True
    
    logger.info(f"找到 {len(svg_files)} 个SVG文件")
    
    success_count = 0
    failed_count = 0
    
    for svg_file in svg_files:
        # 生成PDF文件名
        pdf_file = svg_file.with_suffix('.pdf')
        
        # 如果PDF文件已存在且比SVG文件新，跳过转换
        if pdf_file.exists() and pdf_file.stat().st_mtime > svg_file.stat().st_mtime:
            logger.info(f"跳过(PDF已存在且较新): {svg_file}")
            continue
        
        # 转换文件
        if convert_svg_to_pdf(svg_file, pdf_file, inkscape_path):
            success_count += 1
        else:
            failed_count += 1
    
    logger.info(f"转换完成: 成功 {success_count} 个, 失败 {failed_count} 个")
    return failed_count == 0

def main():
    """主函数"""
    current_dir = Path.cwd()
    logger.info(f"开始转换SVG文件，工作目录: {current_dir}")
    
    success = batch_convert_svg_to_pdf(current_dir)
    
    if success:
        logger.info("所有SVG文件转换完成")
        sys.exit(0)
    else:
        logger.error("转换过程中出现错误")
        sys.exit(1)

if __name__ == "__main__":
    main()
