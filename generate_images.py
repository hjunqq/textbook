import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 确保图片目录存在
os.makedirs('docs/assets/images', exist_ok=True)
os.makedirs('docs/chapters/images/chapter02', exist_ok=True)
os.makedirs('docs/chapters/images/chapter03', exist_ok=True)
os.makedirs('docs/chapters/images/chapter06', exist_ok=True)

def create_chapter01_framework():
    """生成第一章功能框架图"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # 绘制层次结构
    levels = [
        {'name': '智慧水利平台', 'pos': (5, 7), 'size': (3, 0.8), 'color': '#1890ff'},
        {'name': '数据层', 'pos': (1.5, 5.5), 'size': (2, 0.6), 'color': '#52c41a'},
        {'name': '服务层', 'pos': (4.5, 5.5), 'size': (2, 0.6), 'color': '#52c41a'},
        {'name': '应用层', 'pos': (7.5, 5.5), 'size': (2, 0.6), 'color': '#52c41a'},
        {'name': '水文监测', 'pos': (1, 4), 'size': (1.5, 0.5), 'color': '#faad14'},
        {'name': '水质监测', 'pos': (2.8, 4), 'size': (1.5, 0.5), 'color': '#faad14'},
        {'name': '调度服务', 'pos': (4.5, 4), 'size': (1.5, 0.5), 'color': '#faad14'},
        {'name': '预警服务', 'pos': (6.2, 4), 'size': (1.5, 0.5), 'color': '#faad14'},
        {'name': '三维展示', 'pos': (8, 4), 'size': (1.5, 0.5), 'color': '#faad14'},
    ]

    for level in levels:
        rect = patches.Rectangle(
            (level['pos'][0] - level['size'][0]/2, level['pos'][1] - level['size'][1]/2),
            level['size'][0], level['size'][1],
            linewidth=2, edgecolor='black', facecolor=level['color'], alpha=0.7
        )
        ax.add_patch(rect)
        ax.text(level['pos'][0], level['pos'][1], level['name'], 
                ha='center', va='center', fontsize=10, fontweight='bold')

    # 添加连接线
    connections = [
        ((5, 6.6), (1.5, 6.1)),
        ((5, 6.6), (4.5, 6.1)),
        ((5, 6.6), (7.5, 6.1)),
        ((1.5, 5.2), (1, 4.5)),
        ((1.5, 5.2), (2.8, 4.5)),
        ((4.5, 5.2), (4.5, 4.5)),
        ((4.5, 5.2), (6.2, 4.5)),
        ((7.5, 5.2), (8, 4.5)),
    ]

    for start, end in connections:
        ax.plot([start[0], end[0]], [start[1], end[1]], 'k-', linewidth=1.5)

    plt.title('智慧水利平台功能体系框架图', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('docs/assets/images/chapter01_function_framework.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('第一章功能框架图已生成')

def create_waterfall_model():
    """生成瀑布模型图"""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # 瀑布模型的各个阶段
    stages = [
        {'name': '需求分析', 'pos': (2, 7), 'size': (3, 0.8)},
        {'name': '系统设计', 'pos': (2, 6), 'size': (3, 0.8)},
        {'name': '程序设计', 'pos': (2, 5), 'size': (3, 0.8)},
        {'name': '编码实现', 'pos': (2, 4), 'size': (3, 0.8)},
        {'name': '测试', 'pos': (2, 3), 'size': (3, 0.8)},
        {'name': '运行维护', 'pos': (2, 2), 'size': (3, 0.8)},
    ]

    colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#6c5ce7', '#a0e7e5']
    
    for i, stage in enumerate(stages):
        rect = patches.Rectangle(
            (stage['pos'][0] - stage['size'][0]/2, stage['pos'][1] - stage['size'][1]/2),
            stage['size'][0], stage['size'][1],
            linewidth=2, edgecolor='black', facecolor=colors[i], alpha=0.7
        )
        ax.add_patch(rect)
        ax.text(stage['pos'][0], stage['pos'][1], stage['name'], 
                ha='center', va='center', fontsize=12, fontweight='bold')
        
        # 添加箭头
        if i < len(stages) - 1:
            ax.arrow(stage['pos'][0], stage['pos'][1] - 0.5, 0, -0.3, 
                    head_width=0.2, head_length=0.1, fc='black', ec='black')

    plt.title('瀑布模型', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('docs/chapters/images/chapter02/waterfall_model.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('瀑布模型图已生成')

def create_spiral_model():
    """生成螺旋模型图"""
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.axis('off')

    # 绘制螺旋线
    theta = np.linspace(0, 4*np.pi, 100)
    r = theta / (4*np.pi) * 4
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    ax.plot(x, y, 'b-', linewidth=3)

    # 添加四个象限的标签
    quadrants = [
        {'name': '确定目标\n识别约束', 'pos': (-2.5, 2.5)},
        {'name': '风险分析\n原型开发', 'pos': (2.5, 2.5)},
        {'name': '开发验证\n下一层产品', 'pos': (2.5, -2.5)},
        {'name': '评审\n规划下一阶段', 'pos': (-2.5, -2.5)},
    ]

    for quad in quadrants:
        ax.text(quad['pos'][0], quad['pos'][1], quad['name'], 
                ha='center', va='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))

    # 添加分割线
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax.axvline(x=0, color='k', linestyle='--', alpha=0.5)

    plt.title('螺旋模型', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('docs/chapters/images/chapter02/spiral_model.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('螺旋模型图已生成')

def create_git_workflow():
    """生成Git工作流程图"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Git三个区域
    areas = [
        {'name': '工作目录\n(Working Directory)', 'pos': (2, 6), 'size': (3, 1.5), 'color': '#ffecb3'},
        {'name': '暂存区\n(Staging Area)', 'pos': (6, 6), 'size': (3, 1.5), 'color': '#c8e6c9'},
        {'name': '版本库\n(Repository)', 'pos': (10, 6), 'size': (3, 1.5), 'color': '#bbdefb'},
    ]

    for area in areas:
        rect = patches.Rectangle(
            (area['pos'][0] - area['size'][0]/2, area['pos'][1] - area['size'][1]/2),
            area['size'][0], area['size'][1],
            linewidth=2, edgecolor='black', facecolor=area['color'], alpha=0.7
        )
        ax.add_patch(rect)
        ax.text(area['pos'][0], area['pos'][1], area['name'], 
                ha='center', va='center', fontsize=11, fontweight='bold')

    # 添加操作箭头和标签
    operations = [
        {'start': (3.5, 6), 'end': (4.5, 6), 'label': 'git add'},
        {'start': (7.5, 6), 'end': (8.5, 6), 'label': 'git commit'},
        {'start': (8.5, 5.5), 'end': (7.5, 5.5), 'label': 'git checkout'},
        {'start': (4.5, 5.5), 'end': (3.5, 5.5), 'label': 'git reset'},
    ]

    for op in operations:
        ax.annotate('', xy=op['end'], xytext=op['start'],
                   arrowprops=dict(arrowstyle='->', lw=2, color='red'))
        mid_x = (op['start'][0] + op['end'][0]) / 2
        mid_y = (op['start'][1] + op['end'][1]) / 2 + 0.3
        ax.text(mid_x, mid_y, op['label'], ha='center', va='bottom', 
                fontsize=10, color='red', fontweight='bold')

    plt.title('Git工作流程', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('docs/assets/images/chapter03/git_workflow.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('Git工作流程图已生成')

def create_monitoring_system():
    """生成监测系统架构图"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # 系统架构层次
    layers = [
        {'name': '数据采集层', 'y': 8.5, 'components': ['传感器', '监测站', '数据采集器']},
        {'name': '数据传输层', 'y': 7, 'components': ['4G/5G', '卫星通信', '光纤网络']},
        {'name': '数据处理层', 'y': 5.5, 'components': ['数据清洗', '数据融合', '实时计算']},
        {'name': '应用服务层', 'y': 4, 'components': ['监测分析', '预警服务', '调度优化']},
        {'name': '用户界面层', 'y': 2.5, 'components': ['Web端', '移动端', '大屏展示']},
    ]

    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']

    for i, layer in enumerate(layers):
        # 绘制层次背景
        rect = patches.Rectangle((1, layer['y']-0.4), 12, 0.8,
                               facecolor=colors[i], alpha=0.3, edgecolor='black')
        ax.add_patch(rect)
        
        # 层次标题
        ax.text(0.5, layer['y'], layer['name'], ha='right', va='center', 
                fontsize=12, fontweight='bold')
        
        # 组件
        comp_width = 3.5
        start_x = 2
        for j, comp in enumerate(layer['components']):
            comp_x = start_x + j * 4
            comp_rect = patches.Rectangle((comp_x, layer['y']-0.3), comp_width, 0.6,
                                        facecolor=colors[i], alpha=0.7, edgecolor='black')
            ax.add_patch(comp_rect)
            ax.text(comp_x + comp_width/2, layer['y'], comp, ha='center', va='center', 
                    fontsize=10, fontweight='bold')

    # 添加连接箭头
    for i in range(len(layers)-1):
        y_start = layers[i]['y'] - 0.4
        y_end = layers[i+1]['y'] + 0.4
        for j in range(3):
            x = 2 + j * 4 + 1.75
            ax.arrow(x, y_start, 0, y_end - y_start - 0.1, 
                    head_width=0.2, head_length=0.1, fc='gray', ec='gray')

    plt.title('流域水情监测系统架构示意图', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('docs/assets/images/chapter03/river_basin_monitoring_system.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('监测系统架构图已生成')

def create_oblique_photogrammetry():
    """生成倾斜摄影测量系统结构图"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # 无人机
    drone_rect = patches.Rectangle((5, 6.5), 2, 1, facecolor='lightblue', edgecolor='black')
    ax.add_patch(drone_rect)
    ax.text(6, 7, '无人机平台', ha='center', va='center', fontsize=12, fontweight='bold')

    # 五个相机
    cameras = [
        {'name': '垂直相机', 'pos': (6, 5.5)},
        {'name': '前视相机', 'pos': (6, 4.5)},
        {'name': '后视相机', 'pos': (6, 3.5)},
        {'name': '左视相机', 'pos': (4.5, 4)},
        {'name': '右视相机', 'pos': (7.5, 4)},
    ]

    for cam in cameras:
        cam_rect = patches.Rectangle((cam['pos'][0]-0.5, cam['pos'][1]-0.3), 1, 0.6, 
                                   facecolor='yellow', edgecolor='black')
        ax.add_patch(cam_rect)
        ax.text(cam['pos'][0], cam['pos'][1], cam['name'], ha='center', va='center', 
                fontsize=9, fontweight='bold')

    # 地面控制点
    gcp_positions = [(2, 1), (4, 1), (8, 1), (10, 1)]
    for pos in gcp_positions:
        circle = patches.Circle(pos, 0.3, facecolor='red', edgecolor='black')
        ax.add_patch(circle)
        ax.text(pos[0], pos[1], 'GCP', ha='center', va='center', 
                fontsize=8, fontweight='bold', color='white')

    # 连接线表示拍摄
    for cam in cameras:
        for gcp_pos in gcp_positions:
            ax.plot([cam['pos'][0], gcp_pos[0]], [cam['pos'][1], gcp_pos[1]], 
                   'g--', alpha=0.3, linewidth=1)

    ax.text(6, 0.3, '地面控制点 (GCP)', ha='center', va='center', fontsize=12, fontweight='bold')
    
    plt.title('无人机倾斜摄影测量系统结构图', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('docs/chapters/chapter06/images/oblique_photogrammetry_system.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('倾斜摄影测量系统结构图已生成')

# 生成所有图片
if __name__ == "__main__":
    create_chapter01_framework()
    create_waterfall_model()
    create_spiral_model()
    create_git_workflow()
    create_monitoring_system()
    create_oblique_photogrammetry()
    print("所有图片生成完成！") 