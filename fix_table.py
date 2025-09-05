#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fix_table_in_chapter02():
    file_path = "/mnt/e/2025/教材/智慧水利平台架构与开发/publish/latex/chapters/chapter02.tex"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix the malformed table
    old_table = r"""\begin{longtable}[]{@{} >{\raggedright\arraybackslash}p{(\columnwidth - 4\tabcolsep) * \real{0.3333}} >{\raggedright\arraybackslash}p{(\columnwidth - 4\tabcolsep) * \real{0.3333}} >{\raggedright\arraybackslash}p{(\columnwidth - 4\tabcolsep) * \real{0.3333}}@{}}
\toprule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
符合 & 名称 & 说明 \\
\includegraphics{../images/chapter02/image11.png} & 处理 & 能改变数据值或位置的加工。例如,程序模块、处理机等都是处理 \\
\includegraphics{../images/chapter02/image12.png} & 输入/输出 & 表示输人或输出，是一个广义的不指明具体设备的符号 \\
\includegraphics{../images/chapter02/image13.png} & 连接 & 指出转到图的另一部分或从图的另一部分转来,通常在同一页 \\
\includegraphics{../images/chapter02/image14.png} & 换页连接 & 指出转到另一页图上或由另一页图转来 \\
\includegraphics{../images/chapter02/image15.png} & 数据流 & 用来连接其他符号，指明数据流动方向 \\
\includegraphics{../images/chapter02/image16.png} & 文档 & 通常表示打印输出,也可表示用打印终端输入数据 \\
\includegraphics{../images/chapter02/image17.png} & 联机存储 & 表示任何种类的联机存储,包括磁盘、软盘和海量存储器件等 \\
\includegraphics{../images/chapter02/image18.png} & 磁盘 & 磁盘输入/输出,也可表示存储在磁盘上的文件或数据库 \\
\includegraphics{../images/chapter02/image19.png} & 显示 & CRT终端或类似的显示部件,可用于输人或输出,也可既输人又输出 \\
\includegraphics{../images/chapter02/image20.png} & 人工输人 & 人工输入数据的脱机处理。例如,填写表格 \\
\includegraphics{../images/chapter02/image21.png} & 人工操作 & 人工完成的处理。例如，会计在工资支票上签名 \\
\includegraphics{../images/chapter02/image22.png} & 辅助操作 & 使用设备进行的脱机操作 \\
\includegraphics{../images/chapter02/image23.png} & 通信链路 & 通过远程通信线路或链路传送数据 \\
\end{longtable}"""
    
    new_table = r"""\begin{longtable}[]{@{} >{\raggedright\arraybackslash}p{(\columnwidth - 4\tabcolsep) * \real{0.3333}} >{\raggedright\arraybackslash}p{(\columnwidth - 4\tabcolsep) * \real{0.3333}} >{\raggedright\arraybackslash}p{(\columnwidth - 4\tabcolsep) * \real{0.3333}}@{}}
\toprule\noalign{}
\begin{minipage}[b]{\linewidth}\raggedright
符号
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
名称
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
说明
\end{minipage} \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
\includegraphics[width=0.8\linewidth]{../images/chapter02/image11.png} & 处理 & 能改变数据值或位置的加工。例如,程序模块、处理机等都是处理 \\
\includegraphics[width=0.8\linewidth]{../images/chapter02/image12.png} & 输入/输出 & 表示输人或输出，是一个广义的不指明具体设备的符号 \\
\includegraphics[width=0.8\linewidth]{../images/chapter02/image13.png} & 连接 & 指出转到图的另一部分或从图的另一部分转来,通常在同一页 \\
\includegraphics[width=0.8\linewidth]{../images/chapter02/image14.png} & 换页连接 & 指出转到另一页图上或由另一页图转来 \\
\includegraphics[width=0.8\linewidth]{../images/chapter02/image15.png} & 数据流 & 用来连接其他符号，指明数据流动方向 \\
\includegraphics[width=0.8\linewidth]{../images/chapter02/image16.png} & 文档 & 通常表示打印输出,也可表示用打印终端输入数据 \\
\includegraphics[width=0.8\linewidth]{../images/chapter02/image17.png} & 联机存储 & 表示任何种类的联机存储,包括磁盘、软盘和海量存储器件等 \\
\includegraphics[width=0.8\linewidth]{../images/chapter02/image18.png} & 磁盘 & 磁盘输入/输出,也可表示存储在磁盘上的文件或数据库 \\
\includegraphics[width=0.8\linewidth]{../images/chapter02/image19.png} & 显示 & CRT终端或类似的显示部件,可用于输人或输出,也可既输人又输出 \\
\includegraphics[width=0.8\linewidth]{../images/chapter02/image20.png} & 人工输入 & 人工输入数据的脱机处理。例如,填写表格 \\
\includegraphics[width=0.8\linewidth]{../images/chapter02/image21.png} & 人工操作 & 人工完成的处理。例如，会计在工资支票上签名 \\
\includegraphics[width=0.8\linewidth]{../images/chapter02/image22.png} & 辅助操作 & 使用设备进行的脱机操作 \\
\includegraphics[width=0.8\linewidth]{../images/chapter02/image23.png} & 通信链路 & 通过远程通信线路或链路传送数据 \\
\end{longtable}"""

    # Replace the malformed table with the corrected one
    new_content = content.replace(old_table, new_table)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Fixed malformed table in chapter02.tex")
    return True

if __name__ == "__main__":
    fix_table_in_chapter02()