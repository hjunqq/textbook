# 7.2 数据图表展示

## 学习目标
通过本节学习，学生应能够：
1. 掌握三维场景中集成2D图表的技术方法
2. 理解时序数据的动态可视化实现原理
3. 熟练运用各类图表库进行数据可视化开发
4. 能够设计响应式和交互式的数据分析界面

## 引言

在智慧水利三维场景中，**数据图表展示**是将抽象的监测数据转化为直观可视信息的重要手段。与传统的独立图表应用不同，三维场景中的图表需要与空间模型无缝融合，既要保持图表的清晰可读性，又要与三维环境形成协调统一的视觉体验。

现代水利监测系统产生的数据具有多维度、大容量、实时性强等特点，如何在三维场景中有效地展示这些数据的变化趋势、关联关系和异常状态，直接影响到用户对系统状态的理解和决策效率。通过合理的图表设计和技术实现，可以实现"让数据自己说话"的可视化效果。

## 7.2.1 图表技术选型与集成

### 主流图表库对比分析

在三维场景开发中，选择合适的图表库是实现高质量数据可视化的基础。以下对主流图表库进行详细对比：

#### Chart.js
**特点与优势**：
- 轻量级、响应式设计，适合移动端应用
- 支持8种基本图表类型，可满足大部分需求
- HTML5 Canvas渲染，性能良好
- 丰富的配置选项和插件系统

```javascript
// Chart.js在三维场景中的集成示例
class WaterLevelChart {
    constructor(canvasId, sceneContainer) {
        this.canvasId = canvasId;
        this.sceneContainer = sceneContainer;
        this.chart = null;
        this.initChart();
    }
    
    initChart() {
        const ctx = document.getElementById(this.canvasId).getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '水位(m)',
                    data: [],
                    borderColor: '#00BFFF',
                    backgroundColor: 'rgba(0, 191, 255, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            displayFormats: {
                                hour: 'MM-DD HH:mm'
                            }
                        },
                        title: {
                            display: true,
                            text: '时间'
                        }
                    },
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: '水位(m)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff'
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }
    
    updateData(newData) {
        // 更新图表数据
        this.chart.data.labels = newData.timestamps;
        this.chart.data.datasets[0].data = newData.values;
        this.chart.update('active');
    }
    
    // 与三维场景联动
    syncWith3DScene(selectedPointId) {
        // 高亮对应时间点的数据
        this.highlightDataPoint(selectedPointId);
        // 触发场景中的相应视觉效果
        this.sceneContainer.highlightMonitoringPoint(selectedPointId);
    }
}
```

#### ECharts
**特点与优势**：
- 功能强大，支持30+图表类型
- 优秀的交互设计和动画效果
- 支持大数据量渲染优化
- 丰富的主题和定制选项

```javascript
// ECharts实现多参数关联分析图表
class MultiParameterChart {
    constructor(containerId) {
        this.chart = echarts.init(document.getElementById(containerId));
        this.initChart();
    }
    
    initChart() {
        const option = {
            title: {
                text: '水库多参数监测',
                left: 'center',
                textStyle: {
                    color: '#fff'
                }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                    crossStyle: {
                        color: '#999'
                    }
                }
            },
            toolbox: {
                feature: {
                    dataView: {show: true, readOnly: false},
                    magicType: {show: true, type: ['line', 'bar']},
                    restore: {show: true},
                    saveAsImage: {show: true}
                },
                iconStyle: {
                    normal: {
                        borderColor: '#fff'
                    }
                }
            },
            legend: {
                data: ['水位', '流量', '降雨量'],
                textStyle: {
                    color: '#fff'
                }
            },
            xAxis: [
                {
                    type: 'category',
                    data: [],
                    axisPointer: {
                        type: 'shadow'
                    },
                    axisLabel: {
                        color: '#fff'
                    }
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    name: '水位(m)',
                    position: 'left',
                    axisLabel: {
                        formatter: '{value} m',
                        color: '#fff'
                    }
                },
                {
                    type: 'value',
                    name: '流量(m³/s)',
                    position: 'right',
                    axisLabel: {
                        formatter: '{value} m³/s',
                        color: '#fff'
                    }
                }
            ],
            series: [
                {
                    name: '水位',
                    type: 'line',
                    data: [],
                    smooth: true,
                    itemStyle: {
                        color: '#00BFFF'
                    }
                },
                {
                    name: '流量',
                    type: 'line',
                    yAxisIndex: 1,
                    data: [],
                    smooth: true,
                    itemStyle: {
                        color: '#FF6347'
                    }
                },
                {
                    name: '降雨量',
                    type: 'bar',
                    data: [],
                    itemStyle: {
                        color: '#32CD32'
                    }
                }
            ],
            backgroundColor: 'transparent',
            grid: {
                borderColor: 'rgba(255, 255, 255, 0.1)'
            }
        };
        
        this.chart.setOption(option);
        
        // 图表事件绑定
        this.chart.on('click', (params) => {
            this.onChartClick(params);
        });
    }
    
    onChartClick(params) {
        // 点击图表时与三维场景联动
        const timestamp = params.name;
        const dataType = params.seriesName;
        
        // 通知三维场景显示对应时刻的状态
        this.notifySceneUpdate(timestamp, dataType);
    }
    
    updateMultiParameterData(timeData, waterLevel, flow, rainfall) {
        this.chart.setOption({
            xAxis: [{
                data: timeData
            }],
            series: [
                { data: waterLevel },
                { data: flow },
                { data: rainfall }
            ]
        });
    }
}
```

#### D3.js
**特点与优势**：
- 最大的灵活性和定制能力
- 强大的数据绑定和转换能力
- 支持复杂的交互和动画
- 适合创建独特的可视化方案

```javascript
// D3.js实现自定义径向流量图
class RadialFlowChart {
    constructor(containerId, width = 400, height = 400) {
        this.container = d3.select(`#${containerId}`);
        this.width = width;
        this.height = height;
        this.radius = Math.min(width, height) / 2 - 40;
        this.initChart();
    }
    
    initChart() {
        // 创建SVG容器
        this.svg = this.container.append('svg')
            .attr('width', this.width)
            .attr('height', this.height);
        
        // 创建主要绘图组
        this.g = this.svg.append('g')
            .attr('transform', `translate(${this.width/2}, ${this.height/2})`);
        
        // 创建径向比例尺
        this.radiusScale = d3.scaleLinear()
            .range([0, this.radius]);
        
        // 创建角度比例尺
        this.angleScale = d3.scaleLinear()
            .range([0, 2 * Math.PI]);
        
        // 创建线生成器
        this.line = d3.lineRadial()
            .radius(d => this.radiusScale(d.value))
            .angle(d => this.angleScale(d.time))
            .curve(d3.curveCardinalClosed);
        
        // 添加背景网格
        this.drawGrid();
    }
    
    drawGrid() {
        // 径向网格线
        const radiusGrid = this.g.selectAll('.radius-grid')
            .data(this.radiusScale.ticks(5))
            .enter().append('circle')
            .attr('class', 'radius-grid')
            .attr('r', d => this.radiusScale(d))
            .style('fill', 'none')
            .style('stroke', 'rgba(255, 255, 255, 0.2)')
            .style('stroke-dasharray', '2,2');
        
        // 角度网格线
        const angleGrid = this.g.selectAll('.angle-grid')
            .data(d3.range(0, 360, 30))
            .enter().append('line')
            .attr('class', 'angle-grid')
            .attr('x1', 0)
            .attr('y1', 0)
            .attr('x2', d => this.radius * Math.cos((d - 90) * Math.PI / 180))
            .attr('y2', d => this.radius * Math.sin((d - 90) * Math.PI / 180))
            .style('stroke', 'rgba(255, 255, 255, 0.2)')
            .style('stroke-width', 1);
    }
    
    updateData(flowData) {
        // 更新比例尺域
        this.radiusScale.domain([0, d3.max(flowData, d => d.value)]);
        this.angleScale.domain([0, flowData.length - 1]);
        
        // 绘制径向流量线
        const path = this.g.selectAll('.flow-path')
            .data([flowData]);
        
        path.enter().append('path')
            .attr('class', 'flow-path')
            .merge(path)
            .transition()
            .duration(1000)
            .attr('d', this.line)
            .style('fill', 'rgba(0, 191, 255, 0.3)')
            .style('stroke', '#00BFFF')
            .style('stroke-width', 2);
        
        // 添加数据点
        const dots = this.g.selectAll('.flow-dot')
            .data(flowData);
        
        dots.enter().append('circle')
            .attr('class', 'flow-dot')
            .merge(dots)
            .transition()
            .duration(1000)
            .attr('cx', d => this.radiusScale(d.value) * Math.cos(this.angleScale(d.time) - Math.PI/2))
            .attr('cy', d => this.radiusScale(d.value) * Math.sin(this.angleScale(d.time) - Math.PI/2))
            .attr('r', 4)
            .style('fill', '#00BFFF')
            .style('stroke', '#fff')
            .style('stroke-width', 2);
        
        dots.exit().remove();
    }
}
```

### 图表在三维场景中的集成策略

#### HTML叠加层技术
通过CSS定位将HTML图表元素叠加在三维场景上方：

```css
/* 图表容器样式 */
.chart-overlay {
    position: absolute;
    top: 20px;
    right: 20px;
    width: 400px;
    height: 300px;
    background: rgba(0, 0, 0, 0.8);
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    z-index: 1000;
    transition: all 0.3s ease;
}

.chart-overlay:hover {
    background: rgba(0, 0, 0, 0.9);
    transform: scale(1.05);
}

/* 响应式布局 */
@media (max-width: 768px) {
    .chart-overlay {
        position: relative;
        width: 100%;
        height: 250px;
        margin-bottom: 20px;
        transform: none !important;
    }
}

/* 图表标题样式 */
.chart-title {
    color: #fff;
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 15px;
    text-align: center;
    border-bottom: 2px solid #00BFFF;
    padding-bottom: 10px;
}

/* 图表工具栏 */
.chart-toolbar {
    position: absolute;
    top: 10px;
    right: 10px;
    display: flex;
    gap: 5px;
}

.chart-tool-btn {
    width: 30px;
    height: 30px;
    background: rgba(255, 255, 255, 0.2);
    border: none;
    border-radius: 4px;
    color: #fff;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.3s ease;
}

.chart-tool-btn:hover {
    background: rgba(255, 255, 255, 0.4);
}
```

#### 纹理映射技术
将图表渲染到纹理上，再映射到三维模型表面：

```javascript
class TextureChart {
    constructor(renderer, scene) {
        this.renderer = renderer;
        this.scene = scene;
        this.canvas = document.createElement('canvas');
        this.canvas.width = 512;
        this.canvas.height = 512;
        this.ctx = this.canvas.getContext('2d');
        this.texture = new THREE.CanvasTexture(this.canvas);
    }
    
    drawChartOnTexture(data) {
        // 清空画布
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 设置背景
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制标题
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '24px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('实时水位监测', this.canvas.width/2, 40);
        
        // 绘制图表
        this.drawLineChart(data);
        
        // 更新纹理
        this.texture.needsUpdate = true;
    }
    
    drawLineChart(data) {
        if (data.length < 2) return;
        
        const margin = 60;
        const chartWidth = this.canvas.width - 2 * margin;
        const chartHeight = this.canvas.height - 2 * margin - 60;
        
        // 计算数据范围
        const minValue = Math.min(...data.map(d => d.value));
        const maxValue = Math.max(...data.map(d => d.value));
        const valueRange = maxValue - minValue || 1;
        
        // 绘制坐标轴
        this.ctx.strokeStyle = '#ccc';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        // X轴
        this.ctx.moveTo(margin, this.canvas.height - margin);
        this.ctx.lineTo(this.canvas.width - margin, this.canvas.height - margin);
        // Y轴
        this.ctx.moveTo(margin, margin + 60);
        this.ctx.lineTo(margin, this.canvas.height - margin);
        this.ctx.stroke();
        
        // 绘制数据线
        this.ctx.strokeStyle = '#00BFFF';
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        
        data.forEach((point, index) => {
            const x = margin + (index / (data.length - 1)) * chartWidth;
            const y = (this.canvas.height - margin) - 
                     ((point.value - minValue) / valueRange) * chartHeight;
            
            if (index === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        });
        
        this.ctx.stroke();
        
        // 绘制数据点
        this.ctx.fillStyle = '#00BFFF';
        data.forEach((point, index) => {
            const x = margin + (index / (data.length - 1)) * chartWidth;
            const y = (this.canvas.height - margin) - 
                     ((point.value - minValue) / valueRange) * chartHeight;
            
            this.ctx.beginPath();
            this.ctx.arc(x, y, 4, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }
    
    applyToMesh(mesh) {
        // 将图表纹理应用到网格材质上
        if (mesh.material.map) {
            mesh.material.map = this.texture;
            mesh.material.needsUpdate = true;
        }
    }
}
```

## 7.2.2 时序数据的动态可视化

### 时间轴控制组件

时间轴控制是时序数据可视化的核心组件，需要提供直观的时间导航和数据播放功能：

```javascript
class TimelineController {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            width: options.width || 800,
            height: options.height || 60,
            margin: options.margin || { top: 10, right: 40, bottom: 20, left: 40 },
            autoPlay: options.autoPlay || false,
            playSpeed: options.playSpeed || 1000, // 毫秒
            ...options
        };
        
        this.currentTime = null;
        this.timeRange = null;
        this.playing = false;
        this.playTimer = null;
        
        this.initTimeline();
        this.bindEvents();
    }
    
    initTimeline() {
        // 创建SVG容器
        this.svg = d3.select(this.container)
            .append('svg')
            .attr('width', this.options.width)
            .attr('height', this.options.height);
        
        // 创建主绘图区
        this.g = this.svg.append('g')
            .attr('transform', `translate(${this.options.margin.left}, ${this.options.margin.top})`);
        
        // 创建时间刻度
        this.xScale = d3.scaleTime();
        this.xAxis = d3.axisBottom(this.xScale)
            .tickFormat(d3.timeFormat('%m-%d %H:%M'));
        
        // 创建时间轴组
        this.axisG = this.g.append('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0, ${this.options.height - this.options.margin.top - this.options.margin.bottom})`);
        
        // 创建播放控制按钮
        this.createControls();
        
        // 创建时间指示器
        this.timeIndicator = this.g.append('line')
            .attr('class', 'time-indicator')
            .attr('y1', 0)
            .attr('y2', this.options.height - this.options.margin.top - this.options.margin.bottom)
            .style('stroke', '#FF4500')
            .style('stroke-width', 2)
            .style('opacity', 0);
    }
    
    createControls() {
        const controlsContainer = d3.select(this.container)
            .append('div')
            .attr('class', 'timeline-controls')
            .style('margin-top', '10px');
        
        // 播放/暂停按钮
        this.playBtn = controlsContainer.append('button')
            .attr('class', 'timeline-btn play-btn')
            .html('▶')
            .on('click', () => this.togglePlay());
        
        // 停止按钮
        controlsContainer.append('button')
            .attr('class', 'timeline-btn stop-btn')
            .html('⏹')
            .on('click', () => this.stop());
        
        // 速度控制
        controlsContainer.append('label')
            .text('播放速度: ');
        
        controlsContainer.append('select')
            .attr('class', 'speed-selector')
            .on('change', (event) => {
                this.options.playSpeed = parseInt(event.target.value);
            })
            .selectAll('option')
            .data([500, 1000, 2000, 5000])
            .enter().append('option')
            .attr('value', d => d)
            .text(d => `${d/1000}秒`)
            .property('selected', d => d === this.options.playSpeed);
    }
    
    setTimeRange(startTime, endTime) {
        this.timeRange = [startTime, endTime];
        this.currentTime = startTime;
        
        // 更新刻度范围
        const chartWidth = this.options.width - this.options.margin.left - this.options.margin.right;
        this.xScale.domain(this.timeRange).range([0, chartWidth]);
        
        // 更新坐标轴
        this.axisG.call(this.xAxis);
        
        // 显示时间指示器
        this.updateTimeIndicator();
        this.timeIndicator.style('opacity', 1);
        
        // 启用拖拽
        this.enableDrag();
    }
    
    enableDrag() {
        const chartWidth = this.options.width - this.options.margin.left - this.options.margin.right;
        
        const drag = d3.drag()
            .on('start', () => {
                this.stop(); // 停止自动播放
            })
            .on('drag', (event) => {
                const x = Math.max(0, Math.min(chartWidth, event.x));
                const time = this.xScale.invert(x);
                this.setCurrentTime(time);
            });
        
        // 添加透明的拖拽区域
        this.g.append('rect')
            .attr('class', 'drag-area')
            .attr('width', chartWidth)
            .attr('height', this.options.height - this.options.margin.top - this.options.margin.bottom)
            .style('fill', 'transparent')
            .style('cursor', 'pointer')
            .call(drag);
    }
    
    togglePlay() {
        if (this.playing) {
            this.pause();
        } else {
            this.play();
        }
    }
    
    play() {
        if (!this.timeRange) return;
        
        this.playing = true;
        this.playBtn.html('⏸');
        
        this.playTimer = setInterval(() => {
            const nextTime = new Date(this.currentTime.getTime() + 60000); // 前进1分钟
            
            if (nextTime > this.timeRange[1]) {
                this.stop();
                return;
            }
            
            this.setCurrentTime(nextTime);
        }, this.options.playSpeed);
    }
    
    pause() {
        this.playing = false;
        this.playBtn.html('▶');
        if (this.playTimer) {
            clearInterval(this.playTimer);
            this.playTimer = null;
        }
    }
    
    stop() {
        this.pause();
        this.setCurrentTime(this.timeRange[0]);
    }
    
    setCurrentTime(time) {
        this.currentTime = time;
        this.updateTimeIndicator();
        
        // 触发时间变化事件
        this.onTimeChange(time);
    }
    
    updateTimeIndicator() {
        const x = this.xScale(this.currentTime);
        this.timeIndicator.attr('x1', x).attr('x2', x);
        
        // 更新时间显示
        const timeText = d3.timeFormat('%Y-%m-%d %H:%M:%S')(this.currentTime);
        
        // 如果时间文本不存在则创建
        if (!this.timeText) {
            this.timeText = this.g.append('text')
                .attr('class', 'time-text')
                .style('fill', '#fff')
                .style('font-size', '12px')
                .style('text-anchor', 'middle');
        }
        
        this.timeText
            .attr('x', x)
            .attr('y', -5)
            .text(timeText);
    }
    
    // 回调函数，由外部实现
    onTimeChange(time) {
        // 通知外部组件时间发生变化
        if (this.options.onTimeChange) {
            this.options.onTimeChange(time);
        }
    }
}
```

### 实时数据流处理

处理实时数据流并更新图表显示：

```javascript
class RealTimeDataProcessor {
    constructor(maxDataPoints = 100) {
        this.maxDataPoints = maxDataPoints;
        this.dataBuffer = new Map(); // 按传感器ID存储数据
        this.subscribers = new Map(); // 订阅者列表
        this.websocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }
    
    connect(websocketUrl) {
        try {
            this.websocket = new WebSocket(websocketUrl);
            this.setupEventHandlers();
        } catch (error) {
            console.error('WebSocket连接失败:', error);
            this.scheduleReconnect();
        }
    }
    
    setupEventHandlers() {
        this.websocket.onopen = () => {
            console.log('实时数据连接已建立');
            this.reconnectAttempts = 0;
            
            // 发送订阅消息
            this.websocket.send(JSON.stringify({
                action: 'subscribe',
                channels: ['water_level', 'flow_rate', 'rainfall']
            }));
        };
        
        this.websocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.processIncomingData(data);
            } catch (error) {
                console.error('数据解析错误:', error);
            }
        };
        
        this.websocket.onclose = () => {
            console.log('实时数据连接已关闭');
            this.scheduleReconnect();
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket错误:', error);
        };
    }
    
    processIncomingData(data) {
        const { sensorId, timestamp, value, dataType } = data;
        
        // 初始化传感器数据缓冲区
        if (!this.dataBuffer.has(sensorId)) {
            this.dataBuffer.set(sensorId, []);
        }
        
        const buffer = this.dataBuffer.get(sensorId);
        
        // 添加新数据点
        buffer.push({
            timestamp: new Date(timestamp),
            value: value,
            dataType: dataType
        });
        
        // 保持缓冲区大小
        if (buffer.length > this.maxDataPoints) {
            buffer.shift();
        }
        
        // 通知订阅者
        this.notifySubscribers(sensorId, buffer);
    }
    
    subscribe(sensorId, callback) {
        if (!this.subscribers.has(sensorId)) {
            this.subscribers.set(sensorId, []);
        }
        
        this.subscribers.get(sensorId).push(callback);
        
        // 如果已有数据，立即回调
        if (this.dataBuffer.has(sensorId)) {
            callback(this.dataBuffer.get(sensorId));
        }
    }
    
    unsubscribe(sensorId, callback) {
        if (this.subscribers.has(sensorId)) {
            const callbacks = this.subscribers.get(sensorId);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }
    
    notifySubscribers(sensorId, data) {
        if (this.subscribers.has(sensorId)) {
            this.subscribers.get(sensorId).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('订阅者回调错误:', error);
                }
            });
        }
    }
    
    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.pow(2, this.reconnectAttempts) * 1000; // 指数退避
            
            setTimeout(() => {
                console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
                this.connect(this.websocket?.url);
            }, delay);
        } else {
            console.error('已达到最大重连次数，连接失败');
        }
    }
    
    getLatestData(sensorId, count = 10) {
        if (!this.dataBuffer.has(sensorId)) {
            return [];
        }
        
        const buffer = this.dataBuffer.get(sensorId);
        return buffer.slice(-count);
    }
    
    disconnect() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        this.dataBuffer.clear();
        this.subscribers.clear();
    }
}
```

## 7.2.3 响应式图表设计

### 多设备适配策略

现代水利监测系统需要支持多种设备访问，响应式图表设计确保在不同屏幕尺寸和设备类型上都能提供良好的用户体验：

```css
/* 响应式图表布局 */
.chart-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    padding: 20px;
    width: 100%;
    box-sizing: border-box;
}

/* 大屏幕适配 */
@media (min-width: 1200px) {
    .chart-grid {
        grid-template-columns: repeat(3, 1fr);
        max-width: 1400px;
        margin: 0 auto;
    }
}

/* 平板适配 */
@media (max-width: 1024px) {
    .chart-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 15px;
        padding: 15px;
    }
}

/* 手机适配 */
@media (max-width: 768px) {
    .chart-grid {
        grid-template-columns: 1fr;
        gap: 10px;
        padding: 10px;
    }
    
    .chart-overlay {
        position: relative !important;
        top: auto !important;
        right: auto !important;
        width: 100% !important;
        height: auto !important;
        margin-bottom: 15px;
    }
}
```

### 交互优化设计

针对不同设备类型优化图表交互方式：

```javascript
class ResponsiveChartManager {
    constructor() {
        this.isMobile = this.detectMobile();
        this.touchHandler = null;
        this.setupInteractions();
    }
    
    detectMobile() {
        return window.innerWidth <= 768 || 
               /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
    
    setupInteractions() {
        if (this.isMobile) {
            this.setupMobileInteractions();
        } else {
            this.setupDesktopInteractions();
        }
    }
    
    setupMobileInteractions() {
        // 移动端交互优化
        const charts = document.querySelectorAll('.chart-container');
        
        charts.forEach(chart => {
            // 增大点击目标尺寸
            chart.style.minHeight = '250px';
            
            // 添加触摸反馈
            chart.addEventListener('touchstart', (e) => {
                chart.classList.add('chart-touched');
            });
            
            chart.addEventListener('touchend', (e) => {
                setTimeout(() => {
                    chart.classList.remove('chart-touched');
                }, 150);
            });
        });
    }
    
    setupDesktopInteractions() {
        // 桌面端交互优化
        const charts = document.querySelectorAll('.chart-container');
        
        charts.forEach(chart => {
            chart.addEventListener('mouseenter', (e) => {
                chart.classList.add('chart-hovered');
            });
            
            chart.addEventListener('mouseleave', (e) => {
                chart.classList.remove('chart-hovered');
            });
        });
    }
}
```

## 7.2.4 本节小结

本节详细介绍了在三维水利场景中实现数据图表展示的完整技术方案：

**图表技术选型**：
- 对比分析了Chart.js、ECharts、D3.js等主流图表库的特点和适用场景
- 提供了各图表库在三维场景中集成的具体实现方案
- 介绍了HTML叠加层和纹理映射等集成策略

**时序数据可视化**：
- 实现了完整的时间轴控制组件，支持播放、暂停、拖拽等交互
- 建立了实时数据流处理机制，支持WebSocket数据推送和缓冲管理
- 提供了动态图表更新和性能优化方案

**响应式设计**：
- 建立了多设备适配的CSS布局策略
- 优化了移动端和桌面端的不同交互体验
- 确保图表在各种设备上都能良好展示

这些技术为水利监测数据的可视化分析提供了坚实基础，使用户能够在三维场景中直观地理解和分析复杂的水利数据，提高决策效率和系统可用性。

## 思考题与练习

### 基础题

1. 比较Chart.js、ECharts、D3.js三种图表库的优缺点，并说明各自的适用场景。
2. 解释HTML叠加层技术和纹理映射技术的工作原理，分析其在三维场景中的应用优势。
3. 简述时间轴控制组件的主要功能，并说明其在时序数据可视化中的重要作用。

### 提高题

4. 设计一个实时数据流处理系统，要求支持多传感器数据接收、缓冲管理和异常处理。
5. 分析响应式图表设计的关键要素，并提出针对水利监测系统的优化建议。
6. 设计一个图表与三维场景的联动机制，实现数据选择和视觉效果的双向同步。

### 实践题

7. 使用Chart.js创建一个水位监测的实时折线图，包含数据更新、阈值预警等功能。
8. 用D3.js实现一个自定义的水库库容变化可视化图表，展示时间与库容的关系。
9. 开发一个响应式的多参数监测仪表盘，支持不同设备的优化显示。

### 综合题

10. 设计并实现一个完整的水利数据可视化平台，集成多种图表类型，支持实时数据展示和历史数据分析。