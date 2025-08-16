# 4.1 HTML5与CSS3基础

## 学习目标

1. 掌握HTML5语义化标签的使用方法和最佳实践
2. 熟练运用CSS3选择器、布局技术和动画效果
3. 理解响应式设计原理，能够开发适配多终端的Web界面
4. 具备使用CSS预处理器提高开发效率的能力

## 4.1.1 HTML5语义化标签与文档结构

### HTML5语义化标签详解

HTML5引入了一系列语义化标签，为文档提供了更清晰的结构描述。在智慧水利平台开发中，合理使用语义化标签不仅提高了代码可读性，还有利于搜索引擎优化和无障碍访问。

#### 主要语义化标签

**1. 文档结构标签**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智慧水利监测平台</title>
</head>
<body>
    <header>
        <nav>
            <ul>
                <li><a href="#dashboard">仪表板</a></li>
                <li><a href="#monitoring">实时监测</a></li>
                <li><a href="#analysis">数据分析</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <section id="dashboard">
            <h1>系统仪表板</h1>
            <article>
                <h2>水位监测概览</h2>
                <p>当前全流域水位状况...</p>
            </article>
        </section>
        
        <aside>
            <h3>快速导航</h3>
            <ul>
                <li><a href="#alerts">预警信息</a></li>
                <li><a href="#reports">报表中心</a></li>
            </ul>
        </aside>
    </main>
    
    <footer>
        <p>&copy; 2024 智慧水利监测平台</p>
    </footer>
</body>
</html>
```

**2. 内容组织标签**

| 标签 | 用途 | 在水利平台中的应用 |
|------|------|-------------------|
| `<header>` | 页面或区块头部 | 平台标题、导航菜单 |
| `<nav>` | 导航链接 | 主导航、面包屑导航 |
| `<main>` | 主要内容 | 核心功能区域 |
| `<section>` | 独立的内容区块 | 监测数据模块、图表区域 |
| `<article>` | 独立的文章内容 | 报告详情、新闻动态 |
| `<aside>` | 侧边栏内容 | 快捷操作、相关链接 |
| `<footer>` | 页面或区块底部 | 版权信息、联系方式 |

> **Note**: 语义化标签的选择应基于内容的实际意义，而非视觉效果。这样既提高了代码可维护性，也增强了可访问性。

#### 表单控件与数据验证

HTML5增强了表单功能，新增了多种输入类型和验证属性，特别适用于水利数据采集界面。

```html
<form id="waterLevelForm" novalidate>
    <fieldset>
        <legend>水位数据录入</legend>
        
        <!-- 数值输入with 范围限制 -->
        <label for="waterLevel">当前水位 (米):</label>
        <input type="number" 
               id="waterLevel" 
               name="waterLevel" 
               min="0" 
               max="100" 
               step="0.01" 
               required
               placeholder="请输入水位数值">
        <span class="error-message" id="waterLevel-error"></span>
        
        <!-- 日期时间输入 -->
        <label for="measureTime">测量时间:</label>
        <input type="datetime-local" 
               id="measureTime" 
               name="measureTime" 
               required>
        
        <!-- 地理位置输入 -->
        <label for="latitude">纬度:</label>
        <input type="number" 
               id="latitude" 
               name="latitude" 
               min="-90" 
               max="90" 
               step="0.000001" 
               required>
        
        <label for="longitude">经度:</label>
        <input type="number" 
               id="longitude" 
               name="longitude" 
               min="-180" 
               max="180" 
               step="0.000001" 
               required>
        
        <!-- 选择列表 -->
        <label for="stationType">监测站类型:</label>
        <select id="stationType" name="stationType" required>
            <option value="">请选择</option>
            <option value="river">河流站</option>
            <option value="lake">湖泊站</option>
            <option value="reservoir">水库站</option>
        </select>
        
        <!-- 文本区域 -->
        <label for="remarks">备注信息:</label>
        <textarea id="remarks" 
                  name="remarks" 
                  rows="3" 
                  maxlength="500"
                  placeholder="可选的备注信息..."></textarea>
        
        <button type="submit">提交数据</button>
        <button type="reset">重置表单</button>
    </fieldset>
</form>

<script>
// 自定义表单验证
document.getElementById('waterLevelForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const waterLevel = document.getElementById('waterLevel');
    const errorElement = document.getElementById('waterLevel-error');
    
    // 清除之前的错误信息
    errorElement.textContent = '';
    
    // 自定义验证逻辑
    if (waterLevel.value < 0 || waterLevel.value > 100) {
        errorElement.textContent = '水位数值必须在0-100米之间';
        waterLevel.focus();
        return;
    }
    
    // 验证通过，处理表单提交
    console.log('表单验证通过，准备提交数据');
});
</script>
```

#### 多媒体元素与Canvas API

HTML5的多媒体支持为水利数据展示提供了丰富的可能性。

**1. 视频播放器**

```html
<section class="media-section">
    <h2>实时监控视频</h2>
    <video controls 
           width="800" 
           height="600" 
           poster="dam-preview.jpg"
           preload="metadata">
        <source src="dam-monitor-hd.mp4" type="video/mp4">
        <source src="dam-monitor-hd.webm" type="video/webm">
        <track kind="captions" 
               src="dam-monitor-captions.vtt" 
               srclang="zh" 
               label="中文字幕">
        <p>您的浏览器不支持视频播放，请升级浏览器。</p>
    </video>
</section>
```

**2. Canvas绘图基础**

```html
<section class="chart-section">
    <h2>水位变化趋势图</h2>
    <canvas id="waterLevelChart" 
            width="800" 
            height="400"
            style="border: 1px solid #ddd;">
        您的浏览器不支持Canvas，无法显示图表。
    </canvas>
</section>

<script>
// Canvas绘制水位趋势图
function drawWaterLevelChart() {
    const canvas = document.getElementById('waterLevelChart');
    const ctx = canvas.getContext('2d');
    
    // 模拟水位数据
    const data = [
        {time: '00:00', level: 15.2},
        {time: '06:00', level: 15.8},
        {time: '12:00', level: 16.5},
        {time: '18:00', level: 16.1},
        {time: '24:00', level: 15.7}
    ];
    
    // 设置绘图参数
    const padding = 50;
    const chartWidth = canvas.width - 2 * padding;
    const chartHeight = canvas.height - 2 * padding;
    
    // 清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 绘制坐标轴
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    
    // X轴
    ctx.beginPath();
    ctx.moveTo(padding, canvas.height - padding);
    ctx.lineTo(canvas.width - padding, canvas.height - padding);
    ctx.stroke();
    
    // Y轴
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, canvas.height - padding);
    ctx.stroke();
    
    // 绘制数据点和连线
    ctx.strokeStyle = '#2196F3';
    ctx.fillStyle = '#2196F3';
    ctx.lineWidth = 2;
    
    const xStep = chartWidth / (data.length - 1);
    const minLevel = Math.min(...data.map(d => d.level));
    const maxLevel = Math.max(...data.map(d => d.level));
    const levelRange = maxLevel - minLevel;
    
    ctx.beginPath();
    data.forEach((point, index) => {
        const x = padding + index * xStep;
        const y = canvas.height - padding - 
                 ((point.level - minLevel) / levelRange) * chartHeight;
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
        
        // 绘制数据点
        ctx.fillRect(x - 3, y - 3, 6, 6);
        
        // 添加标签
        ctx.fillStyle = '#666';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(point.time, x, canvas.height - padding + 20);
        ctx.fillText(point.level + 'm', x, y - 10);
        ctx.fillStyle = '#2196F3';
    });
    
    ctx.stroke();
}

// 页面加载完成后绘制图表
document.addEventListener('DOMContentLoaded', drawWaterLevelChart);
</script>
```

### 文档结构设计与可访问性

良好的文档结构不仅有利于SEO，更重要的是提高了系统的可访问性，确保残障用户也能正常使用水利监测平台。

#### 可访问性最佳实践

**1. 合理的标题层级**

```html
<main>
    <h1>智慧水利监测平台</h1>
    
    <section>
        <h2>实时监测数据</h2>
        
        <article>
            <h3>长江流域监测点</h3>
            <h4>宜昌水文站</h4>
            <p>当前水位: 15.6米</p>
            
            <h4>武汉水文站</h4>
            <p>当前水位: 12.3米</p>
        </article>
        
        <article>
            <h3>珠江流域监测点</h3>
            <!-- 更多内容 -->
        </article>
    </section>
    
    <section>
        <h2>历史数据分析</h2>
        <!-- 分析内容 -->
    </section>
</main>
```

**2. ARIA属性应用**

```html
<nav role="navigation" aria-label="主导航">
    <ul>
        <li><a href="#dashboard" aria-current="page">仪表板</a></li>
        <li><a href="#monitoring">实时监测</a></li>
        <li><a href="#analysis">数据分析</a></li>
    </ul>
</nav>

<section role="region" aria-labelledby="alerts-heading">
    <h2 id="alerts-heading">系统警报</h2>
    <div role="alert" aria-live="polite" id="alert-container">
        <!-- 动态警报内容 -->
    </div>
</section>

<table role="table" aria-label="水位监测数据表格">
    <caption>近7天水位监测数据汇总</caption>
    <thead>
        <tr>
            <th scope="col">监测站点</th>
            <th scope="col">当前水位(m)</th>
            <th scope="col">变化趋势</th>
            <th scope="col">预警等级</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <th scope="row">宜昌水文站</th>
            <td>15.6</td>
            <td aria-label="上升">↗</td>
            <td>正常</td>
        </tr>
    </tbody>
</table>
```

**3. 键盘导航支持**

```css
/* 焦点样式 */
button:focus,
input:focus,
select:focus,
textarea:focus,
a:focus {
    outline: 2px solid #2196F3;
    outline-offset: 2px;
}

/* 跳过链接 */
.skip-link {
    position: absolute;
    top: -40px;
    left: 6px;
    background: #000;
    color: #fff;
    padding: 8px;
    text-decoration: none;
    z-index: 1000;
}

.skip-link:focus {
    top: 6px;
}
```

```html
<body>
    <a href="#main-content" class="skip-link">跳过导航</a>
    <nav><!-- 导航内容 --></nav>
    <main id="main-content" tabindex="-1">
        <!-- 主要内容 -->
    </main>
</body>
```

## 4.1.2 CSS3选择器与样式设计

### CSS3选择器语法与优先级

CSS3引入了更强大的选择器，为复杂的Web应用样式控制提供了精确的手段。

#### 高级选择器类型

**1. 属性选择器**

```css
/* 基础属性选择器 */
input[type="number"] {
    border: 2px solid #4CAF50;
}

/* 属性值匹配 */
input[name^="water"] {  /* 以"water"开头 */
    background-color: #E3F2FD;
}

input[class*="level"] {  /* 包含"level" */
    font-weight: bold;
}

input[id$="Time"] {  /* 以"Time"结尾 */
    border-radius: 4px;
}

/* 自定义数据属性 */
[data-station-type="river"] {
    border-left: 4px solid #2196F3;
}

[data-alert-level="high"] {
    background-color: #FFEBEE;
    border-color: #F44336;
}
```

**2. 伪类选择器**

```css
/* 结构伪类 */
.station-list li:nth-child(odd) {
    background-color: #F5F5F5;
}

.station-list li:nth-child(3n) {
    border-right: 3px solid #2196F3;
}

.data-table tr:first-child {
    background-color: #1976D2;
    color: white;
}

.data-table tr:last-child {
    border-bottom: 2px solid #333;
}

/* 状态伪类 */
.form-field input:valid {
    border-color: #4CAF50;
}

.form-field input:invalid {
    border-color: #F44336;
}

.nav-item:hover {
    background-color: #E3F2FD;
}

.button:active {
    transform: scale(0.98);
}

/* 目标伪类 */
section:target {
    animation: highlight 2s ease-in-out;
}

@keyframes highlight {
    0% { background-color: #FFEB3B; }
    100% { background-color: transparent; }
}
```

**3. 伪元素选择器**

```css
/* 内容装饰 */
.water-level::before {
    content: "💧 ";
    color: #2196F3;
}

.alert-high::after {
    content: " ⚠️";
    color: #F44336;
}

/* 首字母样式 */
.report-content::first-letter {
    font-size: 2em;
    color: #1976D2;
    float: left;
    margin: 0.1em 0.1em 0.1em 0;
}

/* 首行样式 */
.article-content::first-line {
    font-weight: bold;
    color: #333;
}

/* 选中文本样式 */
.data-display::selection {
    background-color: #2196F3;
    color: white;
}
```

#### 选择器优先级计算

```css
/* 优先级: 0,1,0,1 */
#header .nav-item {
    color: blue;
}

/* 优先级: 0,0,1,1 */
.nav-item.active {
    color: red;
}

/* 优先级: 0,0,0,2 */
nav a {
    color: green;
}

/* 使用!important (不推荐) */
.emergency-alert {
    color: red !important;
}
```

> **Tip**: 为了代码的可维护性，应尽量避免使用`!important`，而是通过合理的选择器设计来控制样式优先级。

### 盒模型与布局原理

#### CSS盒模型详解

```css
/* 标准盒模型 */
.standard-box {
    width: 300px;
    height: 200px;
    padding: 20px;
    border: 5px solid #ddd;
    margin: 10px;
    /* 实际占用空间: 370px × 270px */
}

/* IE盒模型(border-box) */
.border-box {
    box-sizing: border-box;
    width: 300px;
    height: 200px;
    padding: 20px;
    border: 5px solid #ddd;
    margin: 10px;
    /* 实际占用空间: 320px × 220px */
    /* 内容区域: 250px × 150px */
}

/* 全局设置 */
*, *::before, *::after {
    box-sizing: border-box;
}
```

#### 布局方法对比

**1. 浮动布局(Float)**

```css
.container {
    overflow: hidden; /* 清除浮动 */
}

.sidebar {
    float: left;
    width: 25%;
    background-color: #F5F5F5;
}

.main-content {
    float: left;
    width: 75%;
    padding: 20px;
}

/* 清除浮动 */
.clearfix::after {
    content: "";
    display: table;
    clear: both;
}
```

**2. 定位布局(Position)**

```css
.monitoring-dashboard {
    position: relative;
    height: 100vh;
}

.header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    background-color: #1976D2;
    z-index: 1000;
}

.sidebar {
    position: absolute;
    top: 60px;
    left: 0;
    width: 250px;
    bottom: 0;
    background-color: #F5F5F5;
}

.main-content {
    position: absolute;
    top: 60px;
    left: 250px;
    right: 0;
    bottom: 0;
    overflow-y: auto;
}

.floating-alert {
    position: fixed;
    top: 80px;
    right: 20px;
    background-color: #FFEB3B;
    padding: 15px;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
```

### CSS预处理器(Sass/Less)入门

CSS预处理器为样式开发提供了变量、嵌套、混合等高级功能，显著提高开发效率。

#### Sass基础语法

**1. 变量定义**

```scss
// 颜色变量
$primary-color: #1976D2;
$secondary-color: #FFC107;
$success-color: #4CAF50;
$error-color: #F44336;
$warning-color: #FF9800;

// 尺寸变量
$header-height: 60px;
$sidebar-width: 250px;
$border-radius: 4px;
$box-shadow: 0 2px 8px rgba(0,0,0,0.15);

// 字体变量
$font-family-base: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
$font-size-base: 14px;
$font-size-large: 16px;
$font-size-small: 12px;
```

**2. 嵌套规则**

```scss
.water-monitoring-panel {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: $border-radius;
    box-shadow: $box-shadow;
    
    .panel-header {
        background-color: $primary-color;
        color: white;
        padding: 15px 20px;
        border-radius: $border-radius $border-radius 0 0;
        
        h3 {
            margin: 0;
            font-size: $font-size-large;
        }
        
        .actions {
            float: right;
            
            button {
                background: none;
                border: 1px solid rgba(255,255,255,0.3);
                color: white;
                padding: 5px 10px;
                border-radius: 2px;
                
                &:hover {
                    background-color: rgba(255,255,255,0.1);
                }
                
                &.active {
                    background-color: rgba(255,255,255,0.2);
                }
            }
        }
    }
    
    .panel-content {
        padding: 20px;
        
        .data-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
            
            &:last-child {
                border-bottom: none;
            }
            
            .label {
                font-weight: 500;
                color: #666;
            }
            
            .value {
                font-weight: bold;
                
                &.normal { color: $success-color; }
                &.warning { color: $warning-color; }
                &.danger { color: $error-color; }
            }
        }
    }
}
```

**3. 混合(Mixins)**

```scss
// 响应式断点混合
@mixin breakpoint($size) {
    @if $size == 'small' {
        @media (max-width: 768px) { @content; }
    }
    @else if $size == 'medium' {
        @media (min-width: 769px) and (max-width: 1024px) { @content; }
    }
    @else if $size == 'large' {
        @media (min-width: 1025px) { @content; }
    }
}

// 按钮样式混合
@mixin button-style($bg-color, $text-color: white) {
    background-color: $bg-color;
    color: $text-color;
    border: none;
    padding: 10px 20px;
    border-radius: $border-radius;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
        background-color: darken($bg-color, 10%);
        transform: translateY(-1px);
    }
    
    &:active {
        transform: translateY(0);
    }
    
    &:disabled {
        background-color: #ccc;
        cursor: not-allowed;
        transform: none;
    }
}

// 卡片样式混合
@mixin card-style($padding: 20px) {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: $border-radius;
    box-shadow: $box-shadow;
    padding: $padding;
    
    @include breakpoint('small') {
        padding: $padding / 2;
        margin: 10px;
    }
}

// 使用混合
.primary-button {
    @include button-style($primary-color);
}

.success-button {
    @include button-style($success-color);
}

.monitoring-card {
    @include card-style(25px);
}
```

**4. 函数和条件**

```scss
// 自定义函数
@function calculate-rem($px-value, $base-font-size: 16px) {
    @return ($px-value / $base-font-size) * 1rem;
}

// 条件语句
@mixin alert-style($type) {
    padding: 15px;
    border-radius: $border-radius;
    margin-bottom: 15px;
    
    @if $type == 'success' {
        background-color: lighten($success-color, 40%);
        border: 1px solid $success-color;
        color: darken($success-color, 20%);
    } @else if $type == 'warning' {
        background-color: lighten($warning-color, 40%);
        border: 1px solid $warning-color;
        color: darken($warning-color, 20%);
    } @else if $type == 'error' {
        background-color: lighten($error-color, 40%);
        border: 1px solid $error-color;
        color: darken($error-color, 20%);
    } @else {
        background-color: #f0f0f0;
        border: 1px solid #ccc;
        color: #666;
    }
}

// 使用示例
.alert-success {
    @include alert-style('success');
}

.text-large {
    font-size: calculate-rem(18px);
}
```

## 实践练习

### 练习4.1.1: 智慧水利监测站信息表单

创建一个完整的监测站信息录入表单，要求：

1. 使用HTML5语义化标签构建页面结构
2. 包含多种类型的表单控件
3. 实现客户端数据验证
4. 支持键盘导航和屏幕阅读器

### 练习4.1.2: 水位数据可视化看板

使用Canvas API创建一个简单的数据看板，要求：

1. 绘制实时水位柱状图
2. 显示多个监测点的数据对比
3. 支持鼠标悬停显示详细信息
4. 实现数据的定时更新

### 练习4.1.3: 响应式监测平台界面

设计一个响应式的水利监测平台主界面，要求：

1. 使用Sass编写样式代码
2. 实现三栏布局（头部、侧边栏、主内容区）
3. 在不同屏幕尺寸下自适应显示
4. 包含导航菜单和数据展示区域

## 思考题

1. **语义化标签的选择原则**：在设计水利监测平台界面时，如何根据内容特点选择合适的HTML5语义化标签？请举例说明。

2. **可访问性设计的重要性**：为什么在水利系统中特别需要考虑可访问性设计？请分析可能的使用场景。

3. **CSS预处理器的优势**：相比传统CSS，使用Sass等预处理器为大型水利项目开发带来哪些具体好处？

4. **性能优化考虑**：在编写HTML和CSS时，应该注意哪些性能优化要点，特别是对于需要实时显示大量监测数据的水利平台？

## 小结

本节介绍了HTML5与CSS3的核心技术，重点包括：

1. **HTML5语义化标签**：提供了更清晰的文档结构，提高了代码可读性和可访问性
2. **表单控件与验证**：HTML5增强的表单功能为数据采集提供了强大支持
3. **多媒体与Canvas**：为富媒体内容展示和数据可视化奠定了基础
4. **CSS3选择器**：提供了更精确的样式控制能力
5. **布局技术**：掌握了多种布局方法的应用场景
6. **CSS预处理器**：显著提高了样式开发的效率和可维护性

这些技术为后续学习响应式设计、JavaScript交互和Vue.js框架开发打下了坚实基础，是构建现代水利监测平台不可缺少的技能。

---

**扩展阅读**：
- [HTML5 Specification - W3C](https://www.w3.org/TR/html52/)
- [CSS3 Reference - MDN](https://developer.mozilla.org/en-US/docs/Web/CSS)
- [Web Accessibility Guidelines - WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/)
- [Sass Documentation](https://sass-lang.com/documentation)
