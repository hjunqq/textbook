# 第二节 数据可视化基础方法

## 引言

数据可视化是将抽象的数据转换为直观图形表示的技术和艺术，是连接数据与用户认知的重要桥梁。在智慧水利平台中，有效的数据可视化不仅能够帮助用户快速理解复杂的监测数据，更能够支持科学决策和应急响应。

随着水利监测技术的发展，数据的规模和复杂性不断增长，传统的表格和简单图表已经无法满足现代水利管理的需求。需要运用多种可视化技术，包括统计图表、地理信息可视化、时间序列可视化、多维数据可视化等，构建立体化的数据展示体系。

本节将系统介绍数据可视化的基本理论、主要方法和技术实现，为监测数据在三维场景中的融合展示奠定基础。

## 7.2.1 可视化设计原理

### 可视化认知理论

#### 视觉感知原理
人类视觉系统对不同视觉元素的感知能力存在差异：

```javascript
// 视觉感知优先级层次
const visualPerceptionHierarchy = {
    highest: {
        elements: ['位置', '长度'],
        accuracy: '很高',
        useCase: '精确数值比较'
    },
    high: {
        elements: ['角度', '斜率', '面积'],
        accuracy: '高',
        useCase: '趋势分析'
    },
    medium: {
        elements: ['体积', '密度', '颜色饱和度'],
        accuracy: '中等',
        useCase: '分类展示'
    },
    low: {
        elements: ['颜色色调', '形状'],
        accuracy: '较低',
        useCase: '标识区分'
    }
};

// 应用示例：水位数据可视化
function designWaterLevelChart(data) {
    return {
        // 利用位置编码精确水位值
        yAxis: 'waterLevel',
        // 利用颜色区分不同站点
        colorBy: 'stationId',
        // 利用形状表示数据质量
        shapeBy: 'dataQuality',
        // 利用大小表示重要程度
        sizeBy: 'importance'
    };
}
```

#### 认知负荷理论
有效的可视化设计应该最小化用户的认知负荷：

```python
class CognitiveLoadOptimizer:
    """认知负荷优化器"""
    
    def __init__(self):
        self.design_principles = {
            'chunking': '信息分组，避免过量信息',
            'progressive_disclosure': '渐进式信息展示',
            'consistency': '保持一致的视觉语言',
            'affordance': '提供清晰的交互线索'
        }
    
    def optimize_chart_design(self, data, user_task):
        """优化图表设计以减少认知负荷"""
        if user_task == 'overview':
            return self.design_overview_chart(data)
        elif user_task == 'comparison':
            return self.design_comparison_chart(data)
        elif user_task == 'trend_analysis':
            return self.design_trend_chart(data)
        else:
            return self.design_general_chart(data)
    
    def design_overview_chart(self, data):
        """设计概览图表"""
        return {
            'chart_type': 'dashboard',
            'max_indicators': 6,  // 7±2原则
            'grouping': 'by_category',
            'highlighting': 'anomalies_only'
        }
```

### 数据-视觉映射

#### 映射策略
不同类型的数据需要采用合适的视觉编码方式：

```javascript
// 数据类型与视觉编码映射表
const dataVisualMapping = {
    quantitative: {
        continuous: {
            primary: ['position', 'length', 'area'],
            secondary: ['color_intensity', 'size'],
            examples: ['水位', '流量', '温度']
        },
        discrete: {
            primary: ['position', 'length'],
            secondary: ['color_hue', 'shape'],
            examples: ['站点数量', '等级分类']
        }
    },
    ordinal: {
        primary: ['position', 'color_intensity'],
        secondary: ['size', 'texture'],
        examples: ['预警等级', '水质类别']
    },
    nominal: {
        primary: ['color_hue', 'shape'],
        secondary: ['position_grouping', 'texture'],
        examples: ['站点类型', '行政区域']
    },
    temporal: {
        primary: ['position_x'],
        secondary: ['animation', 'small_multiples'],
        examples: ['时间序列', '历史趋势']
    }
};
```

#### 多维数据编码
复杂的水利监测数据往往具有多个维度：

```python
def encode_multidimensional_data(water_data):
    """多维水利数据编码"""
    encoding = {
        // 主要维度：空间位置
        'x': water_data['longitude'],
        'y': water_data['latitude'],
        
        // 数据值：使用颜色强度
        'color_intensity': water_data['water_level'],
        
        // 数据质量：使用形状
        'shape': water_data['data_quality'],
        
        // 重要性：使用大小
        'size': water_data['station_importance'],
        
        // 趋势：使用颜色色调
        'color_hue': water_data['trend_direction'],
        
        // 时间：使用动画
        'animation': water_data['timestamp']
    }
    
    return encoding
```

## 7.2.2 统计图表可视化

### 基础图表类型

#### 时间序列图表
时间序列是水利监测数据的重要特征：

```javascript
// ECharts时间序列图表配置
const timeSeriesConfig = {
    title: {
        text: '水位变化趋势',
        subtext: '最近30天监测数据'
    },
    xAxis: {
        type: 'time',
        splitLine: {
            show: false
        },
        axisLabel: {
            formatter: function(value) {
                return echarts.format.formatTime('MM-dd', value);
            }
        }
    },
    yAxis: {
        type: 'value',
        name: '水位(m)',
        min: function(value) {
            return value.min - 5;
        },
        max: function(value) {
            return value.max + 5;
        },
        splitLine: {
            lineStyle: {
                type: 'dashed'
            }
        }
    },
    series: [{
        name: '实测水位',
        type: 'line',
        data: waterLevelData,
        lineStyle: {
            color: '#1890ff',
            width: 2
        },
        areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
                { offset: 1, color: 'rgba(24, 144, 255, 0.1)' }
            ])
        },
        markLine: {
            data: [
                { yAxis: 185, name: '警戒水位' },
                { yAxis: 188, name: '保证水位' }
            ],
            lineStyle: {
                color: '#f5222d',
                type: 'solid',
                width: 2
            }
        }
    }],
    tooltip: {
        trigger: 'axis',
        formatter: function(params) {
            const data = params[0];
            const time = echarts.format.formatTime('yyyy-MM-dd hh:mm', data.value[0]);
            const value = data.value[1].toFixed(2);
            return `时间: ${time}<br/>水位: ${value}m`;
        }
    },
    dataZoom: [{
        type: 'inside',
        start: 70,
        end: 100
    }, {
        type: 'slider',
        start: 70,
        end: 100
    }]
};
```

#### 多变量关联图表
展示多个监测参数之间的关系：

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_multivariate_plot(monitoring_data):
    """创建多变量关联图表"""
    
    // 创建子图布局
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('水位-流量关系', '水位-降雨关系', 
                       '水质参数相关性', '综合评价雷达图'),
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "scatter"}, {"type": "scatterpolar"}]]
    )
    
    // 水位-流量散点图
    fig.add_trace(
        go.Scatter(
            x=monitoring_data['water_level'],
            y=monitoring_data['flow_rate'],
            mode='markers',
            marker=dict(
                size=8,
                color=monitoring_data['temperature'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="温度(°C)")
            ),
            name='水位-流量'
        ),
        row=1, col=1
    )
    
    // 水位-降雨时间序列
    fig.add_trace(
        go.Scatter(
            x=monitoring_data['datetime'],
            y=monitoring_data['water_level'],
            name='水位',
            yaxis='y2'
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=monitoring_data['datetime'],
            y=monitoring_data['rainfall'],
            name='降雨量',
            opacity=0.7
        ),
        row=1, col=2
    )
    
    // 相关性热力图
    correlation_matrix = calculate_correlation_matrix(monitoring_data)
    fig.add_trace(
        go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0
        ),
        row=2, col=1
    )
    
    // 雷达图
    fig.add_trace(
        go.Scatterpolar(
            r=[85, 92, 78, 88, 91],
            theta=['水位', '流量', '水质', '设备状态', '预警'],
            fill='toself',
            name='综合评价'
        ),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=True)
    return fig
```

### 高级统计可视化

#### 分布分析图表
```python
def create_distribution_analysis(data):
    """创建分布分析图表"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    // 直方图
    axes[0, 0].hist(data['water_level'], bins=30, alpha=0.7, 
                    color='skyblue', edgecolor='black')
    axes[0, 0].set_title('水位分布直方图')
    axes[0, 0].set_xlabel('水位(m)')
    axes[0, 0].set_ylabel('频次')
    
    // 箱线图
    box_data = [data[data['season']==season]['water_level'] 
                for season in ['春', '夏', '秋', '冬']]
    axes[0, 1].boxplot(box_data, labels=['春', '夏', '秋', '冬'])
    axes[0, 1].set_title('季节性水位箱线图')
    axes[0, 1].set_ylabel('水位(m)')
    
    // 概率密度图
    for station in data['station_id'].unique():
        station_data = data[data['station_id']==station]['water_level']
        axes[1, 0].hist(station_data, alpha=0.5, label=f'站点{station}', 
                       density=True, bins=20)
    axes[1, 0].set_title('各站点水位概率密度')
    axes[1, 0].legend()
    
    // Q-Q图
    from scipy import stats
    stats.probplot(data['water_level'], dist="norm", plot=axes[1, 1])
    axes[1, 1].set_title('水位数据正态性检验')
    
    plt.tight_layout()
    return fig
```

#### 异常检测可视化
```javascript
// 异常检测结果可视化
function createAnomalyDetectionChart(data, anomalies) {
    const config = {
        title: {
            text: '异常检测结果',
            subtext: '基于孤立森林算法'
        },
        xAxis: {
            type: 'time'
        },
        yAxis: {
            type: 'value',
            name: '监测值'
        },
        series: [
            {
                name: '正常数据',
                type: 'scatter',
                data: data.normal,
                symbolSize: 6,
                itemStyle: {
                    color: '#52c41a'
                }
            },
            {
                name: '异常数据',
                type: 'scatter',
                data: anomalies,
                symbolSize: 10,
                itemStyle: {
                    color: '#f5222d'
                },
                label: {
                    show: true,
                    position: 'top',
                    formatter: function(params) {
                        return '异常';
                    }
                }
            },
            {
                name: '置信区间',
                type: 'line',
                data: data.confidence_upper,
                lineStyle: {
                    color: '#1890ff',
                    type: 'dashed'
                },
                symbol: 'none'
            },
            {
                name: '置信区间下限',
                type: 'line',
                data: data.confidence_lower,
                lineStyle: {
                    color: '#1890ff',
                    type: 'dashed'
                },
                symbol: 'none',
                areaStyle: {
                    color: 'rgba(24, 144, 255, 0.1)'
                }
            }
        ],
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                if (params.seriesName === '异常数据') {
                    return `时间: ${params.value[0]}<br/>
                           值: ${params.value[1]}<br/>
                           异常分数: ${params.data.anomalyScore}`;
                }
                return `时间: ${params.value[0]}<br/>值: ${params.value[1]}`;
            }
        }
    };
    
    return echarts.init(document.getElementById('anomaly-chart')).setOption(config);
}
```

## 7.2.3 地理信息可视化

### 空间数据展示

#### 站点分布地图
```javascript
// 使用Leaflet创建监测站点地图
class MonitoringStationMap {
    constructor(containerId) {
        this.map = L.map(containerId).setView([39.9, 116.4], 10);
        this.initBaseLayers();
        this.initStationLayers();
    }
    
    initBaseLayers() {
        // 添加底图
        const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
        const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}');
        
        const baseLayers = {
            "街道地图": osmLayer,
            "卫星地图": satelliteLayer
        };
        
        osmLayer.addTo(this.map);
        L.control.layers(baseLayers).addTo(this.map);
    }
    
    initStationLayers() {
        this.stationLayer = L.layerGroup().addTo(this.map);
        this.clusterGroup = L.markerClusterGroup({
            iconCreateFunction: function(cluster) {
                const count = cluster.getChildCount();
                return L.divIcon({
                    html: `<div class="cluster-icon">${count}</div>`,
                    className: 'custom-cluster',
                    iconSize: [30, 30]
                });
            }
        });
    }
    
    addMonitoringStations(stations) {
        stations.forEach(station => {
            const marker = this.createStationMarker(station);
            this.clusterGroup.addLayer(marker);
        });
        
        this.map.addLayer(this.clusterGroup);
    }
    
    createStationMarker(station) {
        // 根据数据状态选择图标颜色
        const color = this.getStatusColor(station.status);
        const icon = L.divIcon({
            className: 'station-marker',
            html: `<div class="marker-icon" style="background-color: ${color}">
                     <i class="fas fa-tint"></i>
                   </div>`,
            iconSize: [25, 25]
        });
        
        const marker = L.marker([station.lat, station.lng], { icon });
        
        // 添加弹窗信息
        const popupContent = this.createPopupContent(station);
        marker.bindPopup(popupContent);
        
        // 添加实时数据更新
        marker.on('popupopen', () => {
            this.startRealTimeUpdate(station.id, marker);
        });
        
        return marker;
    }
    
    getStatusColor(status) {
        const colors = {
            'normal': '#52c41a',
            'warning': '#faad14', 
            'alert': '#f5222d',
            'offline': '#d9d9d9'
        };
        return colors[status] || colors['offline'];
    }
    
    createPopupContent(station) {
        return `
            <div class="station-popup">
                <h3>${station.name}</h3>
                <div class="station-info">
                    <p><strong>类型:</strong> ${station.type}</p>
                    <p><strong>状态:</strong> <span class="status ${station.status}">${station.status}</span></p>
                    <p><strong>最新数据:</strong> ${station.lastValue} ${station.unit}</p>
                    <p><strong>更新时间:</strong> ${station.lastUpdate}</p>
                </div>
                <div class="station-actions">
                    <button onclick="viewStationDetails('${station.id}')">详细信息</button>
                    <button onclick="viewStationChart('${station.id}')">历史图表</button>
                </div>
            </div>
        `;
    }
}
```

#### 流域水系可视化
```python
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString

class WatershedVisualization:
    """流域水系可视化"""
    
    def __init__(self, watershed_data, river_data, station_data):
        self.watershed = gpd.read_file(watershed_data)
        self.rivers = gpd.read_file(river_data)
        self.stations = self.create_station_geodf(station_data)
    
    def create_station_geodf(self, station_data):
        """创建站点地理数据框"""
        geometry = [Point(row['longitude'], row['latitude']) 
                   for _, row in station_data.iterrows()]
        return gpd.GeoDataFrame(station_data, geometry=geometry)
    
    def create_watershed_map(self, data_column='water_level'):
        """创建流域地图"""
        fig, ax = plt.subplots(1, 1, figsize=(15, 12))
        
        // 绘制流域边界
        self.watershed.boundary.plot(ax=ax, color='black', linewidth=2)
        
        // 绘制河流网络
        self.rivers.plot(ax=ax, color='blue', linewidth=1, alpha=0.7)
        
        // 绘制监测站点
        self.stations.plot(
            column=data_column,
            ax=ax,
            markersize=100,
            cmap='viridis',
            legend=True,
            legend_kwds={'label': f'{data_column} 值', 'shrink': 0.8}
        )
        
        // 添加站点标签
        for idx, station in self.stations.iterrows():
            ax.annotate(
                station['name'],
                (station.geometry.x, station.geometry.y),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=8,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8)
            )
        
        ax.set_title('流域监测站点分布图', fontsize=16, fontweight='bold')
        ax.set_xlabel('经度')
        ax.set_ylabel('纬度')
        
        return fig
    
    def create_interpolation_map(self, parameter='water_level'):
        """创建插值等值线图"""
        from scipy.interpolate import griddata
        import numpy as np
        
        // 提取坐标和数据
        points = np.array([[p.x, p.y] for p in self.stations.geometry])
        values = self.stations[parameter].values
        
        // 创建网格
        x_min, x_max = points[:, 0].min(), points[:, 0].max()
        y_min, y_max = points[:, 1].min(), points[:, 1].max()
        
        xi = np.linspace(x_min, x_max, 100)
        yi = np.linspace(y_min, y_max, 100)
        xi, yi = np.meshgrid(xi, yi)
        
        // 插值
        zi = griddata(points, values, (xi, yi), method='cubic')
        
        // 绘制图形
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        
        // 等值线
        contour = ax.contourf(xi, yi, zi, levels=20, cmap='viridis', alpha=0.8)
        contour_lines = ax.contour(xi, yi, zi, levels=20, colors='black', linewidths=0.5)
        ax.clabel(contour_lines, inline=True, fontsize=8)
        
        // 流域边界
        self.watershed.boundary.plot(ax=ax, color='red', linewidth=2)
        
        // 监测点
        self.stations.plot(ax=ax, color='red', markersize=50, edgecolors='white')
        
        // 颜色条
        plt.colorbar(contour, ax=ax, label=f'{parameter} 等值线')
        
        ax.set_title(f'{parameter} 空间分布插值图')
        return fig
```

### 热力图可视化

#### 密度热力图
```javascript
// 使用Leaflet.heat创建密度热力图
class DensityHeatMap {
    constructor(map) {
        this.map = map;
        this.heatLayer = null;
    }
    
    updateHeatMap(data, options = {}) {
        // 移除现有热力图层
        if (this.heatLayer) {
            this.map.removeLayer(this.heatLayer);
        }
        
        // 处理数据格式
        const heatData = data.map(point => [
            point.latitude,
            point.longitude,
            point.intensity || 1
        ]);
        
        // 创建热力图层
        this.heatLayer = L.heatLayer(heatData, {
            radius: options.radius || 25,
            blur: options.blur || 15,
            maxZoom: options.maxZoom || 17,
            max: options.max || 1.0,
            gradient: options.gradient || {
                0.0: 'blue',
                0.2: 'cyan',
                0.4: 'lime',
                0.6: 'yellow',
                0.8: 'orange',
                1.0: 'red'
            }
        });
        
        this.map.addLayer(this.heatLayer);
    }
    
    createTemporalHeatMap(timeSeriesData) {
        """创建时间序列热力图"""
        const timeSteps = Object.keys(timeSeriesData).sort();
        let currentStep = 0;
        
        const updateMap = () => {
            const currentData = timeSeriesData[timeSteps[currentStep]];
            this.updateHeatMap(currentData);
            
            // 更新时间显示
            document.getElementById('time-display').textContent = timeSteps[currentStep];
            
            currentStep = (currentStep + 1) % timeSteps.length;
        };
        
        // 初始显示
        updateMap();
        
        // 自动播放
        const interval = setInterval(updateMap, 1000);
        
        // 返回控制接口
        return {
            play: () => {
                if (!this.playing) {
                    interval = setInterval(updateMap, 1000);
                    this.playing = true;
                }
            },
            pause: () => {
                clearInterval(interval);
                this.playing = false;
            },
            stop: () => {
                clearInterval(interval);
                currentStep = 0;
                this.playing = false;
            }
        };
    }
}
```

## 7.2.4 时间序列可视化

### 多尺度时间展示

#### 时间层次结构
```python
class MultiScaleTimeVisualization:
    """多尺度时间可视化"""
    
    def __init__(self, data):
        self.data = data
        self.time_scales = {
            'minute': {'format': '%H:%M', 'freq': 'T'},
            'hour': {'format': '%m-%d %H:00', 'freq': 'H'},
            'day': {'format': '%m-%d', 'freq': 'D'},
            'month': {'format': '%Y-%m', 'freq': 'M'},
            'year': {'format': '%Y', 'freq': 'Y'}
        }
    
    def create_hierarchical_timeline(self, parameter='water_level'):
        """创建层次化时间线"""
        fig, axes = plt.subplots(4, 1, figsize=(15, 12), 
                                gridspec_kw={'height_ratios': [3, 1, 1, 1]})
        
        // 主时间序列图
        self.plot_main_timeline(axes[0], parameter)
        
        // 日均值趋势
        daily_data = self.data.resample('D')[parameter].mean()
        axes[1].plot(daily_data.index, daily_data.values, 'b-', linewidth=1)
        axes[1].set_title('日均值趋势')
        axes[1].grid(True, alpha=0.3)
        
        // 月均值趋势
        monthly_data = self.data.resample('M')[parameter].mean()
        axes[2].plot(monthly_data.index, monthly_data.values, 'g-', linewidth=2)
        axes[2].set_title('月均值趋势')
        axes[2].grid(True, alpha=0.3)
        
        // 年度对比
        self.plot_yearly_comparison(axes[3], parameter)
        
        plt.tight_layout()
        return fig
    
    def plot_main_timeline(self, ax, parameter):
        """绘制主时间序列"""
        ax.plot(self.data.index, self.data[parameter], 
               'b-', linewidth=1, alpha=0.8)
        
        // 添加移动平均线
        ma_7 = self.data[parameter].rolling(window=7*24).mean()  // 7天移动平均
        ma_30 = self.data[parameter].rolling(window=30*24).mean()  // 30天移动平均
        
        ax.plot(ma_7.index, ma_7.values, 'r--', linewidth=1, label='7天移动平均')
        ax.plot(ma_30.index, ma_30.values, 'g--', linewidth=1, label='30天移动平均')
        
        // 标记关键事件
        self.mark_events(ax, parameter)
        
        ax.set_title(f'{parameter} 时间序列 (原始数据)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def mark_events(self, ax, parameter):
        """标记关键事件"""
        // 标记极值点
        max_idx = self.data[parameter].idxmax()
        min_idx = self.data[parameter].idxmin()
        
        ax.scatter(max_idx, self.data.loc[max_idx, parameter], 
                  color='red', s=100, marker='^', 
                  label='最大值', zorder=5)
        ax.scatter(min_idx, self.data.loc[min_idx, parameter], 
                  color='blue', s=100, marker='v', 
                  label='最小值', zorder=5)
        
        // 标记异常事件
        anomalies = self.detect_anomalies(parameter)
        if not anomalies.empty:
            ax.scatter(anomalies.index, anomalies[parameter], 
                      color='orange', s=50, marker='x', 
                      label='异常值', zorder=5)
```

#### 周期性分析可视化
```javascript
// 周期性分析可视化
function createCyclicalAnalysis(data, parameter) {
    const config = {
        title: {
            text: `${parameter} 周期性分析`,
            subtext: '日、周、月、季节周期模式'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        toolbox: {
            feature: {
                dataView: { show: true, readOnly: false },
                restore: { show: true },
                saveAsImage: { show: true }
            }
        },
        legend: {
            data: ['小时均值', '日均值', '周均值', '月均值']
        },
        xAxis: [
            {
                type: 'category',
                data: Array.from({length: 24}, (_, i) => `${i}:00`),
                axisPointer: {
                    type: 'shadow'
                }
            }
        ],
        yAxis: [
            {
                type: 'value',
                name: parameter,
                axisLabel: {
                    formatter: '{value}'
                }
            }
        ],
        series: [
            {
                name: '小时均值',
                type: 'line',
                data: calculateHourlyMean(data, parameter),
                smooth: true,
                lineStyle: {
                    color: '#1890ff'
                }
            },
            {
                name: '日均值',
                type: 'bar',
                xAxisIndex: 1,
                yAxisIndex: 1,
                data: calculateDailyMean(data, parameter),
                itemStyle: {
                    color: '#52c41a'
                }
            }
        ]
    };
    
    // 添加多个x轴用于不同周期
    config.xAxis.push(
        {
            type: 'category',
            data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
            position: 'bottom',
            offset: 80
        },
        {
            type: 'category', 
            data: Array.from({length: 12}, (_, i) => `${i+1}月`),
            position: 'bottom',
            offset: 120
        }
    );
    
    return config;
}

function calculateHourlyMean(data, parameter) {
    const hourlyData = new Array(24).fill(0);
    const hourlyCounts = new Array(24).fill(0);
    
    data.forEach(item => {
        const hour = new Date(item.timestamp).getHours();
        hourlyData[hour] += item[parameter];
        hourlyCounts[hour]++;
    });
    
    return hourlyData.map((sum, i) => 
        hourlyCounts[i] > 0 ? (sum / hourlyCounts[i]).toFixed(2) : 0
    );
}
```

### 实时数据流可视化

#### 动态更新图表
```javascript
class RealTimeChart {
    constructor(containerId, options = {}) {
        this.chart = echarts.init(document.getElementById(containerId));
        this.maxDataPoints = options.maxDataPoints || 100;
        this.updateInterval = options.updateInterval || 1000;
        this.data = [];
        
        this.initChart();
        this.startRealTimeUpdate();
    }
    
    initChart() {
        const option = {
            title: {
                text: '实时监测数据流'
            },
            xAxis: {
                type: 'time',
                splitLine: {
                    show: false
                }
            },
            yAxis: {
                type: 'value',
                boundaryGap: [0, '100%'],
                splitLine: {
                    show: false
                }
            },
            series: [{
                name: '实时数据',
                type: 'line',
                showSymbol: false,
                data: this.data,
                lineStyle: {
                    color: '#1890ff',
                    width: 2
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
                        { offset: 1, color: 'rgba(24, 144, 255, 0.05)' }
                    ])
                }
            }],
            animation: false
        };
        
        this.chart.setOption(option);
    }
    
    addDataPoint(timestamp, value) {
        this.data.push({
            name: timestamp,
            value: [timestamp, value]
        });
        
        // 保持数据点数量在限制范围内
        if (this.data.length > this.maxDataPoints) {
            this.data.shift();
        }
        
        // 更新图表
        this.chart.setOption({
            series: [{
                data: this.data
            }]
        });
    }
    
    startRealTimeUpdate() {
        // 模拟实时数据接收
        this.updateTimer = setInterval(() => {
            const now = new Date();
            const value = this.generateMockData();
            this.addDataPoint(now, value);
        }, this.updateInterval);
    }
    
    generateMockData() {
        // 模拟数据生成（实际应用中从WebSocket或API获取）
        const baseValue = 180;
        const randomVariation = (Math.random() - 0.5) * 10;
        const timeVariation = Math.sin(Date.now() / 10000) * 5;
        return baseValue + randomVariation + timeVariation;
    }
    
    stop() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
        }
    }
    
    pause() {
        this.stop();
    }
    
    resume() {
        this.startRealTimeUpdate();
    }
}

// WebSocket实时数据连接
class WebSocketDataStream {
    constructor(url, chart) {
        this.ws = new WebSocket(url);
        this.chart = chart;
        this.setupEventHandlers();
    }
    
    setupEventHandlers() {
        this.ws.onopen = () => {
            console.log('WebSocket连接已建立');
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.chart.addDataPoint(data.timestamp, data.value);
            } catch (error) {
                console.error('数据解析错误:', error);
            }
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket错误:', error);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket连接已关闭');
            // 尝试重连
            setTimeout(() => {
                this.reconnect();
            }, 5000);
        };
    }
    
    reconnect() {
        console.log('尝试重连...');
        this.ws = new WebSocket(this.url);
        this.setupEventHandlers();
    }
}
```

## 小结

数据可视化是连接复杂监测数据与用户理解的重要桥梁。通过合理的视觉编码和交互设计，可以将抽象的数据转换为直观的图形表示，大大提升数据分析和决策支持的效率。

**关键要点总结**：

1. **设计原理**：基于视觉感知和认知负荷理论，选择合适的视觉编码方式

2. **图表类型**：掌握时间序列、多变量关联、分布分析等基础图表的设计方法

3. **空间可视化**：利用地理信息系统和热力图技术展示数据的空间分布特征

4. **时间维度**：构建多尺度时间展示和实时数据流可视化系统

在下一节中，我们将探讨如何将这些可视化技术应用到三维场景中，实现监测数据的空间化展示。

