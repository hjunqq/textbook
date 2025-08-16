## 4.1.4 文档结构设计与可访问性

Web可访问性（Web Accessibility）是现代Web开发的重要组成部分，旨在确保所有用户，包括身体有障碍的用户，都能有效地访问和使用Web内容[11]。世界卫生组织统计显示，全球约有15%的人口患有某种形式的残疾，其中约2.85亿人存在视觉障碍。在智慧水利平台这样的关键基础设施管理系统中，可访问性设计不仅是技术要求，更是社会责任的体现[12]。

可访问性设计遵循WCAG（Web Content Accessibility Guidelines）标准，该标准由W3C制定，包含四个基本原则：可感知（Perceivable）、可操作（Operable）、可理解（Understandable）、健壮性（Robust）[13]。这些原则指导我们构建包容性的用户界面，确保不同能力的用户都能获得良好的使用体验。

### 可访问性设计原则

#### 可感知性原则

可感知性要求信息和用户界面组件必须以用户能够感知的方式呈现，这意味着信息不能对用户的所有感官都是不可见的。

**文本替代内容**：为所有非文本内容提供替代文本，使其能够转换为用户需要的其他形式。

```html
<!-- 图像的替代文本 -->
<img src="charts/water-level-trend.png" 
     alt="长江流域2024年3月水位变化趋势图，显示宜昌站水位从15.2米上升至16.8米">

<!-- 装饰性图像 -->
<img src="decorations/water-wave.svg" alt="" role="presentation">

<!-- 复杂图表的详细描述 -->
<figure>
    <img src="charts/dam-structure.png" 
         alt="三峡大坝结构示意图" 
         aria-describedby="dam-description">
    <figcaption id="dam-description">
        该图显示了三峡大坝的主要结构组成，包括挡水坝段、泄洪坝段、
        电站坝段等三个主要部分。坝体全长2335米，最大坝高185米。
    </figcaption>
</figure>

<!-- 功能性图标 -->
<button type="button" class="alert-btn">
    <img src="icons/warning.svg" alt="预警">
    发送预警
</button>

<!-- SVG图标的可访问性 -->
<svg role="img" aria-labelledby="water-icon-title">
    <title id="water-icon-title">水位监测</title>
    <path d="M12 2l3.09 6.26L22 9l-5 4.87L18.18 22 12 18.77 5.82 22 7 13.87 2 9l6.91-.74L12 2z"/>
</svg>
```

**时间基础媒体的替代内容**：为音频和视频内容提供字幕、音频描述等替代形式。

```html
<!-- 视频字幕支持 -->
<video controls poster="preview.jpg">
    <source src="water-safety-training.mp4" type="video/mp4">
    <source src="water-safety-training.webm" type="video/webm">
    
    <!-- 中文字幕 -->
    <track kind="captions" 
           src="captions/training-zh.vtt" 
           srclang="zh" 
           label="中文字幕" 
           default>
    
    <!-- 英文字幕 -->
    <track kind="captions" 
           src="captions/training-en.vtt" 
           srclang="en" 
           label="English Captions">
    
    <!-- 音频描述 -->
    <track kind="descriptions" 
           src="descriptions/training-desc.vtt" 
           srclang="zh" 
           label="音频描述">
    
    <p>您的浏览器不支持视频播放。请 
       <a href="transcripts/training-transcript.html">查看文字稿</a>。</p>
</video>

<!-- WebVTT字幕文件示例 (training-zh.vtt) -->
<!--
WEBVTT

1
00:00:05.000 --> 00:00:10.000
欢迎来到水利工程安全培训课程

2
00:00:10.000 --> 00:00:15.000
本课程将介绍大坝安全监测的基本原理

3
00:00:15.000 --> 00:00:20.000
首先，我们来了解水位监测系统的组成
-->
```

**适应性内容**：确保内容能够以不同方式呈现而不会丢失信息或结构。

```html
<!-- 响应式数据表格 -->
<div class="table-container">
    <table class="responsive-table" 
           role="table" 
           aria-label="监测站点数据表">
        <caption>长江流域主要监测站点实时数据</caption>
        <thead>
            <tr>
                <th scope="col" id="station">监测站点</th>
                <th scope="col" id="level">当前水位(m)</th>
                <th scope="col" id="flow">流量(m³/s)</th>
                <th scope="col" id="status">状态</th>
                <th scope="col" id="update">更新时间</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <th scope="row" headers="station">宜昌水文站</th>
                <td headers="station level">15.67</td>
                <td headers="station flow">12,350</td>
                <td headers="station status">
                    <span class="status normal" aria-label="正常状态">正常</span>
                </td>
                <td headers="station update">
                    <time datetime="2024-03-15T14:30:00+08:00">14:30</time>
                </td>
            </tr>
            <tr>
                <th scope="row" headers="station">武汉关水文站</th>
                <td headers="station level">24.56</td>
                <td headers="station flow">18,920</td>
                <td headers="station status">
                    <span class="status warning" aria-label="预警状态">预警</span>
                </td>
                <td headers="station update">
                    <time datetime="2024-03-15T14:25:00+08:00">14:25</time>
                </td>
            </tr>
        </tbody>
    </table>
</div>

<!-- 移动端表格替代显示 -->
<div class="mobile-table" aria-hidden="true">
    <div class="mobile-row">
        <h3>宜昌水文站</h3>
        <dl>
            <dt>当前水位</dt>
            <dd>15.67米</dd>
            <dt>流量</dt>
            <dd>12,350 m³/s</dd>
            <dt>状态</dt>
            <dd><span class="status normal">正常</span></dd>
            <dt>更新时间</dt>
            <dd>14:30</dd>
        </dl>
    </div>
</div>
```

#### 可操作性原则

可操作性要求用户界面组件和导航必须是可操作的，用户必须能够操作界面元素。

**键盘可访问性**：所有功能都必须能够通过键盘操作。

```html
<!-- 自定义下拉菜单的键盘支持 -->
<div class="dropdown" role="combobox" 
     aria-expanded="false" 
     aria-haspopup="listbox"
     aria-owns="station-list">
    <button type="button" 
            class="dropdown-toggle"
            aria-label="选择监测站点"
            aria-describedby="dropdown-help">
        <span class="selected-text">请选择监测站点</span>
        <span class="dropdown-arrow" aria-hidden="true">▼</span>
    </button>
    
    <ul id="station-list" 
        class="dropdown-menu" 
        role="listbox" 
        aria-label="监测站点列表"
        hidden>
        <li role="option" 
            aria-selected="false" 
            tabindex="-1"
            data-value="yichang">宜昌水文站</li>
        <li role="option" 
            aria-selected="false" 
            tabindex="-1"
            data-value="wuhan">武汉关水文站</li>
        <li role="option" 
            aria-selected="false" 
            tabindex="-1"
            data-value="hankou">汉口水文站</li>
    </ul>
    
    <div id="dropdown-help" class="sr-only">
        使用空格键打开菜单，方向键导航，回车键选择
    </div>
</div>

<script>
class AccessibleDropdown {
    constructor(element) {
        this.dropdown = element;
        this.toggle = element.querySelector('.dropdown-toggle');
        this.menu = element.querySelector('.dropdown-menu');
        this.options = element.querySelectorAll('[role="option"]');
        this.selectedIndex = -1;
        
        this.initializeEvents();
    }
    
    initializeEvents() {
        // 切换按钮事件
        this.toggle.addEventListener('click', () => this.toggleMenu());
        this.toggle.addEventListener('keydown', (e) => this.handleToggleKeydown(e));
        
        // 选项事件
        this.options.forEach((option, index) => {
            option.addEventListener('click', () => this.selectOption(index));
            option.addEventListener('keydown', (e) => this.handleOptionKeydown(e, index));
        });
        
        // 外部点击关闭
        document.addEventListener('click', (e) => {
            if (!this.dropdown.contains(e.target)) {
                this.closeMenu();
            }
        });
    }
    
    toggleMenu() {
        const isExpanded = this.toggle.getAttribute('aria-expanded') === 'true';
        if (isExpanded) {
            this.closeMenu();
        } else {
            this.openMenu();
        }
    }
    
    openMenu() {
        this.toggle.setAttribute('aria-expanded', 'true');
        this.menu.removeAttribute('hidden');
        
        // 焦点移至第一个选项
        if (this.options.length > 0) {
            this.setSelectedIndex(0);
            this.options[0].focus();
        }
    }
    
    closeMenu() {
        this.toggle.setAttribute('aria-expanded', 'false');
        this.menu.setAttribute('hidden', '');
        this.toggle.focus();
        this.selectedIndex = -1;
    }
    
    handleToggleKeydown(e) {
        switch (e.key) {
            case ' ':
            case 'Enter':
            case 'ArrowDown':
                e.preventDefault();
                this.openMenu();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.openMenu();
                if (this.options.length > 0) {
                    this.setSelectedIndex(this.options.length - 1);
                    this.options[this.options.length - 1].focus();
                }
                break;
        }
    }
    
    handleOptionKeydown(e, index) {
        switch (e.key) {
            case 'Enter':
            case ' ':
                e.preventDefault();
                this.selectOption(index);
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.moveToNext();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.moveToPrevious();
                break;
            case 'Escape':
                e.preventDefault();
                this.closeMenu();
                break;
            case 'Home':
                e.preventDefault();
                this.setSelectedIndex(0);
                this.options[0].focus();
                break;
            case 'End':
                e.preventDefault();
                this.setSelectedIndex(this.options.length - 1);
                this.options[this.options.length - 1].focus();
                break;
        }
    }
    
    moveToNext() {
        const nextIndex = (this.selectedIndex + 1) % this.options.length;
        this.setSelectedIndex(nextIndex);
        this.options[nextIndex].focus();
    }
    
    moveToPrevious() {
        const prevIndex = this.selectedIndex - 1 < 0 
            ? this.options.length - 1 
            : this.selectedIndex - 1;
        this.setSelectedIndex(prevIndex);
        this.options[prevIndex].focus();
    }
    
    setSelectedIndex(index) {
        // 清除之前的选择状态
        this.options.forEach(option => {
            option.setAttribute('aria-selected', 'false');
            option.setAttribute('tabindex', '-1');
        });
        
        // 设置新的选择状态
        if (index >= 0 && index < this.options.length) {
            this.selectedIndex = index;
            this.options[index].setAttribute('aria-selected', 'true');
            this.options[index].setAttribute('tabindex', '0');
        }
    }
    
    selectOption(index) {
        const option = this.options[index];
        const value = option.getAttribute('data-value');
        const text = option.textContent;
        
        // 更新显示文本
        this.toggle.querySelector('.selected-text').textContent = text;
        
        // 触发change事件
        const changeEvent = new CustomEvent('change', {
            detail: { value, text }
        });
        this.dropdown.dispatchEvent(changeEvent);
        
        this.closeMenu();
    }
}

// 初始化下拉菜单
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.dropdown').forEach(dropdown => {
        new AccessibleDropdown(dropdown);
    });
});
</script>
```

**无癫痫发作内容**：避免使用已知会引起癫痫发作的内容。

```css
/* 禁用可能引起癫痫的动画 */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
}

/* 安全的动画设计 */
.loading-spinner {
    animation: spin 2s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* 避免快速闪烁 */
.alert-blink {
    animation: safe-blink 2s ease-in-out infinite;
}

@keyframes safe-blink {
    0%, 50% { opacity: 1; }
    25%, 75% { opacity: 0.7; }
}
```

**导航辅助**：提供帮助用户导航和定位内容的方式。

```html
<!-- 跳过链接 -->
<div class="skip-links">
    <a href="#main-content" class="skip-link">跳转到主要内容</a>
    <a href="#navigation" class="skip-link">跳转到导航菜单</a>
    <a href="#search" class="skip-link">跳转到搜索</a>
</div>

<!-- 面包屑导航 -->
<nav aria-label="面包屑导航" class="breadcrumb">
    <ol>
        <li><a href="/">首页</a></li>
        <li><a href="/monitoring">实时监测</a></li>
        <li><a href="/monitoring/yangtze">长江流域</a></li>
        <li aria-current="page">宜昌水文站</li>
    </ol>
</nav>

<!-- 页面内导航 -->
<nav aria-label="页面内容导航" class="page-navigation">
    <h2>页面内容</h2>
    <ul>
        <li><a href="#current-status">当前状态</a></li>
        <li><a href="#historical-data">历史数据</a></li>
        <li><a href="#trend-analysis">趋势分析</a></li>
        <li><a href="#alert-settings">预警设置</a></li>
    </ul>
</nav>

<!-- 地标导航 -->
<header role="banner">
    <h1>智慧水利监测平台</h1>
    <nav role="navigation" aria-label="主导航">
        <!-- 主导航内容 -->
    </nav>
</header>

<main role="main" id="main-content">
    <h1>监测站详情</h1>
    <!-- 主要内容 -->
</main>

<aside role="complementary" aria-label="相关信息">
    <!-- 侧边栏内容 -->
</aside>

<footer role="contentinfo">
    <!-- 页脚内容 -->
</footer>
```

#### 可理解性原则

可理解性要求信息和用户界面的操作必须是可理解的。

**可读性**：使文本内容可读和可理解。

```html
<!-- 明确的页面语言 -->
<html lang="zh-CN">

<!-- 段落语言标记 -->
<p>系统支持多种数据格式：
    <span lang="en">JSON</span>、
    <span lang="en">XML</span>、
    <span lang="en">CSV</span>
</p>

<!-- 术语解释 -->
<p>当前流域的
    <dfn>
        <abbr title="Discharge Per Second">DPS</abbr>
    </dfn>
    值为1,250立方米每秒。
</p>

<!-- 复杂缩写的解释 -->
<p>根据
    <abbr title="Global Positioning System" 
          aria-describedby="gps-explanation">GPS</abbr>
    定位数据显示...
</p>
<div id="gps-explanation" class="explanation">
    GPS（全球定位系统）是一种基于卫星的导航系统
</div>
```

**可预测性**：使Web页面的显示和操作方式可预测。

```html
<!-- 一致的导航 -->
<nav class="main-navigation" aria-label="主导航">
    <ul>
        <li><a href="/dashboard" aria-current="page">仪表板</a></li>
        <li><a href="/monitoring">实时监测</a></li>
        <li><a href="/analysis">数据分析</a></li>
        <li><a href="/alerts">预警管理</a></li>
        <li><a href="/reports">报表中心</a></li>
        <li><a href="/settings">系统设置</a></li>
    </ul>
</nav>

<!-- 一致的页面结构 -->
<main class="page-content">
    <header class="page-header">
        <h1>页面标题</h1>
        <p class="page-description">页面描述</p>
    </header>
    
    <div class="page-actions">
        <!-- 页面操作按钮 -->
    </div>
    
    <section class="page-main">
        <!-- 主要内容 -->
    </section>
    
    <aside class="page-sidebar">
        <!-- 侧边栏内容 -->
    </aside>
</main>

<!-- 状态变化的明确提示 -->
<form id="data-form">
    <div class="form-group">
        <label for="water-level">水位数据</label>
        <input type="number" 
               id="water-level" 
               aria-describedby="level-status"
               required>
        <div id="level-status" 
             role="status" 
             aria-live="polite"
             class="field-status"></div>
    </div>
    
    <button type="submit" 
            aria-describedby="submit-status">
        提交数据
    </button>
    
    <div id="submit-status" 
         role="status" 
         aria-live="assertive"
         class="submit-feedback"></div>
</form>

<script>
// 提供明确的状态反馈
document.getElementById('water-level').addEventListener('input', function(e) {
    const status = document.getElementById('level-status');
    const value = parseFloat(e.target.value);
    
    if (isNaN(value)) {
        status.textContent = '';
    } else if (value < 0 || value > 50) {
        status.textContent = '数值超出有效范围（0-50米）';
        status.className = 'field-status error';
    } else {
        status.textContent = '数值有效';
        status.className = 'field-status success';
    }
});

document.getElementById('data-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const feedback = document.getElementById('submit-status');
    feedback.textContent = '正在提交数据...';
    feedback.className = 'submit-feedback loading';
    
    // 模拟异步提交
    setTimeout(() => {
        feedback.textContent = '数据提交成功';
        feedback.className = 'submit-feedback success';
    }, 2000);
});
</script>
```

#### 健壮性原则

健壮性要求内容必须足够健壮，能够被各种用户代理（包括辅助技术）可靠地解释。

**兼容性**：最大化与现有和未来辅助技术的兼容性。

```html
<!-- 正确的ARIA标记 -->
<div class="data-visualization" 
     role="img" 
     aria-labelledby="chart-title"
     aria-describedby="chart-summary">
    
    <h3 id="chart-title">水位变化趋势图</h3>
    
    <canvas id="water-chart" width="800" height="400">
        <!-- Canvas内容的文本替代 -->
        <p>该图表显示了过去7天的水位变化趋势。
           起始水位为15.2米，逐步上升至当前的16.8米，
           整体呈上升趋势。</p>
    </canvas>
    
    <div id="chart-summary" class="chart-summary">
        <h4>数据摘要</h4>
        <ul>
            <li>最高水位：16.8米（3月15日）</li>
            <li>最低水位：15.2米（3月9日）</li>
            <li>平均水位：16.0米</li>
            <li>变化趋势：上升</li>
        </ul>
    </div>
</div>

<!-- 表格数据的详细版本 -->
<details class="data-table-details">
    <summary>查看详细数据表格</summary>
    <table>
        <caption>水位监测详细数据</caption>
        <thead>
            <tr>
                <th scope="col">日期</th>
                <th scope="col">时间</th>
                <th scope="col">水位(米)</th>
                <th scope="col">变化(米)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <th scope="row">2024-03-09</th>
                <td>08:00</td>
                <td>15.2</td>
                <td>-</td>
            </tr>
            <!-- 更多数据行 -->
        </tbody>
    </table>
</details>

<!-- 渐进增强的组件 -->
<div class="progressive-enhancement">
    <!-- 基础HTML内容 -->
    <div class="basic-content">
        <h3>监测点状态</h3>
        <ul>
            <li>宜昌站：正常运行</li>
            <li>武汉站：预警状态</li>
            <li>汉口站：正常运行</li>
        </ul>
    </div>
    
    <!-- JavaScript增强内容 -->
    <div class="enhanced-content" hidden>
        <!-- 交互式地图或图表 -->
    </div>
</div>

<script>
// 渐进增强脚本
document.addEventListener('DOMContentLoaded', function() {
    // 检查浏览器能力
    if (window.fetch && window.Promise && document.querySelector) {
        // 启用增强功能
        const basicContent = document.querySelector('.basic-content');
        const enhancedContent = document.querySelector('.enhanced-content');
        
        if (basicContent && enhancedContent) {
            basicContent.setAttribute('hidden', '');
            enhancedContent.removeAttribute('hidden');
            
            // 初始化交互式组件
            initializeInteractiveComponents();
        }
    }
});
</script>
```

### 屏幕阅读器优化

屏幕阅读器是视觉障碍用户访问Web内容的主要工具，优化屏幕阅读器体验需要注意以下几个方面：

#### 语义化HTML结构

```html
<!-- 正确的标题层级 -->
<main>
    <h1>智慧水利监测平台</h1>
    
    <section>
        <h2>实时监测</h2>
        
        <article>
            <h3>长江流域</h3>
            
            <section>
                <h4>主要监测站点</h4>
                <!-- 站点内容 -->
            </section>
            
            <section>
                <h4>水位趋势</h4>
                <!-- 趋势内容 -->
            </section>
        </article>
    </section>
</main>

<!-- 正确的列表结构 -->
<nav aria-label="监测站点导航">
    <ul>
        <li>
            <a href="/stations/yangtze">长江流域</a>
            <ul>
                <li><a href="/stations/yichang">宜昌水文站</a></li>
                <li><a href="/stations/wuhan">武汉关水文站</a></li>
                <li><a href="/stations/hankou">汉口水文站</a></li>
            </ul>
        </li>
        <li>
            <a href="/stations/yellow">黄河流域</a>
            <ul>
                <li><a href="/stations/lanzhou">兰州水文站</a></li>
                <li><a href="/stations/xiaolangdi">小浪底水文站</a></li>
            </ul>
        </li>
    </ul>
</nav>
```

#### ARIA属性的正确使用

```html
<!-- 动态内容区域 -->
<section aria-live="polite" aria-label="实时水位数据">
    <h2>实时水位</h2>
    <div id="live-data">
        <!-- 动态更新的数据 -->
    </div>
</section>

<!-- 紧急警报 -->
<div role="alert" aria-live="assertive">
    <h3>紧急预警</h3>
    <p>武汉关水文站水位超过警戒线，请立即关注！</p>
</div>

<!-- 状态指示器 -->
<div class="status-indicators">
    <div class="status-item" 
         role="status" 
         aria-label="系统连接状态">
        <span class="indicator online" aria-hidden="true"></span>
        <span class="sr-only">系统连接状态：</span>
        在线
    </div>
    
    <div class="status-item" 
         role="status" 
         aria-label="数据更新状态">
        <span class="indicator updating" aria-hidden="true"></span>
        <span class="sr-only">数据更新状态：</span>
        正在更新
    </div>
</div>

<!-- 复杂控件的描述 -->
<div class="water-level-control" 
     role="group" 
     aria-labelledby="control-title"
     aria-describedby="control-instructions">
    
    <h3 id="control-title">水位阈值设置</h3>
    
    <div id="control-instructions" class="instructions">
        使用滑块设置预警和危险水位阈值。
        拖拽左侧滑块设置预警阈值，右侧滑块设置危险阈值。
    </div>
    
    <div class="range-slider">
        <input type="range" 
               id="warning-level"
               min="20" 
               max="30" 
               value="25"
               aria-label="预警水位阈值"
               aria-describedby="warning-value">
        <output id="warning-value">25.0米</output>
        
        <input type="range" 
               id="danger-level"
               min="25" 
               max="35" 
               value="30"
               aria-label="危险水位阈值"
               aria-describedby="danger-value">
        <output id="danger-value">30.0米</output>
    </div>
</div>
```

通过遵循这些可访问性设计原则和最佳实践，我们能够构建出真正包容性的智慧水利平台，确保所有用户都能平等地访问和使用系统功能，体现了技术服务于人的核心理念。
