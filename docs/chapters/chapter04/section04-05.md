## 4.1.5 CSS3选择器与样式设计

CSS3（Cascading Style Sheets Level 3）是CSS技术的最新发展阶段，采用模块化设计理念，将不同功能划分为独立的规范模块[14]。这种设计策略使得浏览器厂商能够根据实际情况逐步实现各个模块，推动了Web样式技术的快速发展。CSS3在选择器、布局、视觉效果、动画等方面都有重大突破，为现代Web应用的界面设计提供了强大的表现力[15]。

在智慧水利平台开发中，CSS3技术的价值体现在多个层面：精确的选择器为复杂界面的样式控制提供了便利；强大的布局技术支持响应式设计，确保平台在各种设备上的良好表现；丰富的视觉效果提升了用户体验；动画技术为数据变化、状态转换等提供了直观的视觉反馈。

### CSS3选择器增强

CSS3大幅扩展了选择器的功能，提供了更精确、更灵活的元素定位能力。这些新增的选择器不仅简化了样式编写，还提高了CSS代码的可维护性。

#### 属性选择器扩展

CSS3增强了属性选择器的功能，支持更复杂的属性值匹配模式：

```css
/* 基础属性选择器 */
input[type="email"] {
    background-image: url('icons/email.svg');
    background-repeat: no-repeat;
    background-position: right 10px center;
    padding-right: 35px;
}

/* 属性值前缀匹配 (^=) */
input[name^="water"] {
    border-left: 4px solid #2196F3;
}

/* 属性值后缀匹配 ($=) */
input[id$="Level"] {
    font-weight: bold;
    color: #1976D2;
}

/* 属性值包含匹配 (*=) */
div[class*="alert"] {
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 15px;
}

/* 属性值单词匹配 (~=) */
div[class~="status"] {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
}

/* 属性值语言匹配 (|=) */
p[lang|="zh"] {
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
}

/* 自定义数据属性 */
[data-station-type="river"] {
    background-color: #E3F2FD;
    border-color: #2196F3;
}

[data-alert-level="high"] {
    background-color: #FFEBEE;
    border-color: #F44336;
    animation: pulse-warning 2s infinite;
}

@keyframes pulse-warning {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

/* 组合属性选择器 */
input[type="number"][required] {
    border: 2px solid #4CAF50;
}

input[type="number"][required]:invalid {
    border-color: #F44336;
    background-color: #FFF5F5;
}
```

#### 结构伪类选择器

CSS3引入了强大的结构伪类选择器，能够根据元素在文档树中的位置进行精确选择：

```css
/* 第n个子元素 */
.station-list li:nth-child(odd) {
    background-color: #F5F5F5;
}

.station-list li:nth-child(even) {
    background-color: #FFFFFF;
}

/* 每三个元素为一组 */
.data-grid .data-item:nth-child(3n+1) {
    clear: left;
    margin-left: 0;
}

/* 前三个元素 */
.monitoring-alerts .alert-item:nth-child(-n+3) {
    border-left: 4px solid #FF9800;
    font-weight: bold;
}

/* 最后三个元素 */
.recent-reports .report-item:nth-last-child(-n+3) {
    border-bottom: 2px solid #E0E0E0;
}

/* 特定类型的第n个元素 */
.content-section h2:nth-of-type(1) {
    color: #1976D2;
    font-size: 24px;
}

.content-section h2:nth-of-type(2) {
    color: #388E3C;
    font-size: 22px;
}

/* 唯一子元素 */
.widget-container div:only-child {
    width: 100%;
    text-align: center;
}

/* 唯一类型元素 */
.article-content p:only-of-type {
    font-style: italic;
    text-align: center;
}

/* 第一个和最后一个子元素 */
.navigation-menu li:first-child a {
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
}

.navigation-menu li:last-child a {
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}

/* 空元素 */
.data-container:empty::before {
    content: "暂无数据";
    color: #757575;
    font-style: italic;
    display: block;
    text-align: center;
    padding: 20px;
}
```

#### UI状态伪类选择器

CSS3新增了多个UI状态伪类选择器，用于响应用户交互和表单状态：

```css
/* 表单状态选择器 */
input:valid {
    border-color: #4CAF50;
    background-image: url('icons/check.svg');
}

input:invalid {
    border-color: #F44336;
    background-image: url('icons/error.svg');
}

input:required {
    box-shadow: inset 0 0 0 1px #FF9800;
}

input:optional {
    background-color: #F9F9F9;
}

input:in-range {
    border-color: #4CAF50;
}

input:out-of-range {
    border-color: #F44336;
    animation: shake 0.5s ease-in-out;
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

/* 启用/禁用状态 */
button:enabled {
    cursor: pointer;
    background-color: #2196F3;
    color: white;
}

button:disabled {
    cursor: not-allowed;
    background-color: #E0E0E0;
    color: #9E9E9E;
}

/* 选中状态 */
input[type="checkbox"]:checked + label {
    font-weight: bold;
    color: #1976D2;
}

input[type="radio"]:checked + label::before {
    content: "✓ ";
    color: #4CAF50;
}

/* 焦点状态 */
input:focus,
textarea:focus,
select:focus {
    outline: 2px solid #2196F3;
    outline-offset: 2px;
    box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.2);
}

/* 目标伪类 */
section:target {
    background-color: #FFFDE7;
    border: 2px solid #FFEB3B;
    animation: highlight-target 3s ease-out;
}

@keyframes highlight-target {
    from { background-color: #FFEB3B; }
    to { background-color: #FFFDE7; }
}
```

#### 伪元素选择器增强

CSS3对伪元素选择器进行了标准化和扩展：

```css
/* ::before 和 ::after 伪元素 */
.water-level-indicator::before {
    content: "💧";
    color: #2196F3;
    margin-right: 5px;
}

.alert-message::after {
    content: " ⚠️";
    color: #FF9800;
}

/* 图标字体应用 */
.icon-station::before {
    content: "\f041"; /* FontAwesome 图标编码 */
    font-family: "Font Awesome 5 Free";
    font-weight: 900;
    margin-right: 8px;
    color: #1976D2;
}

/* 装饰性元素 */
.section-title::before {
    content: "";
    display: inline-block;
    width: 4px;
    height: 20px;
    background-color: #2196F3;
    margin-right: 10px;
    vertical-align: middle;
}

/* 计数器应用 */
.numbered-list {
    counter-reset: item-counter;
}

.numbered-list li::before {
    counter-increment: item-counter;
    content: counter(item-counter) ". ";
    font-weight: bold;
    color: #1976D2;
}

/* 多级计数器 */
.nested-list {
    counter-reset: section-counter;
}

.nested-list > li {
    counter-increment: section-counter;
    counter-reset: subsection-counter;
}

.nested-list > li::before {
    content: counter(section-counter) ". ";
}

.nested-list li li {
    counter-increment: subsection-counter;
}

.nested-list li li::before {
    content: counter(section-counter) "." counter(subsection-counter) " ";
}

/* ::first-line 和 ::first-letter 伪元素 */
.article-content::first-letter {
    font-size: 3em;
    float: left;
    line-height: 1;
    margin: 0 8px 0 0;
    color: #1976D2;
    font-weight: bold;
}

.article-content::first-line {
    font-weight: bold;
    color: #333;
}

/* ::selection 伪元素 */
.selectable-text::selection {
    background-color: #2196F3;
    color: white;
}

.data-table td::selection {
    background-color: #FFF9C4;
    color: #333;
}

/* ::placeholder 伪元素 */
input::placeholder {
    color: #757575;
    font-style: italic;
}

input:focus::placeholder {
    opacity: 0.5;
}
```

### 盒模型与布局技术

CSS3在布局技术方面取得了重大突破，引入了Flexbox和Grid等现代布局方法，彻底改变了传统的布局模式。

#### CSS盒模型详解

理解盒模型是掌握CSS布局的基础。CSS3提供了box-sizing属性来控制盒模型的计算方式：

```css
/* 标准盒模型（content-box） */
.standard-box {
    box-sizing: content-box; /* 默认值 */
    width: 300px;
    height: 200px;
    padding: 20px;
    border: 5px solid #ddd;
    margin: 15px;
    
    /* 
    实际占用空间计算：
    宽度 = margin-left + border-left + padding-left + width + padding-right + border-right + margin-right
         = 15 + 5 + 20 + 300 + 20 + 5 + 15 = 380px
    高度 = margin-top + border-top + padding-top + height + padding-bottom + border-bottom + margin-bottom
         = 15 + 5 + 20 + 200 + 20 + 5 + 15 = 280px
    */
}

/* IE盒模型（border-box） */
.border-box {
    box-sizing: border-box;
    width: 300px;
    height: 200px;
    padding: 20px;
    border: 5px solid #ddd;
    margin: 15px;
    
    /* 
    实际占用空间计算：
    内容区宽度 = width - padding-left - border-left - padding-right - border-right
              = 300 - 20 - 5 - 20 - 5 = 250px
    内容区高度 = height - padding-top - border-top - padding-bottom - border-bottom
              = 200 - 20 - 5 - 20 - 5 = 150px
    总占用宽度 = margin-left + width + margin-right = 15 + 300 + 15 = 330px
    */
}

/* 全局设置为border-box */
*,
*::before,
*::after {
    box-sizing: border-box;
}

/* 响应式容器 */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

@media (max-width: 768px) {
    .container {
        padding: 0 15px;
    }
}
```

#### Flexbox弹性布局

Flexbox布局模型为一维布局提供了强大而灵活的解决方案：

```css
/* 基础Flex容器 */
.flex-container {
    display: flex;
    flex-direction: row; /* row | row-reverse | column | column-reverse */
    flex-wrap: wrap; /* nowrap | wrap | wrap-reverse */
    justify-content: space-between; /* flex-start | flex-end | center | space-between | space-around | space-evenly */
    align-items: center; /* stretch | flex-start | flex-end | center | baseline */
    align-content: flex-start; /* 多行对齐 */
    gap: 20px; /* 项目间距 */
}

/* 监测站点卡片布局 */
.station-cards {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    padding: 20px;
}

.station-card {
    flex: 1 1 300px; /* flex-grow | flex-shrink | flex-basis */
    min-width: 0; /* 防止内容溢出 */
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 响应式Flex布局 */
@media (max-width: 768px) {
    .station-cards {
        flex-direction: column;
    }
    
    .station-card {
        flex: 1 1 auto;
    }
}

/* 水平垂直居中 */
.center-content {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 200px;
}

/* 导航栏布局 */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    background-color: #1976D2;
    color: white;
}

.nav-brand {
    flex: 0 0 auto;
}

.nav-menu {
    display: flex;
    flex: 1 1 auto;
    justify-content: center;
    list-style: none;
    margin: 0;
    padding: 0;
    gap: 30px;
}

.nav-actions {
    flex: 0 0 auto;
}

/* 表单布局 */
.form-row {
    display: flex;
    gap: 15px;
    margin-bottom: 15px;
}

.form-group {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.form-group label {
    margin-bottom: 5px;
    font-weight: 500;
}

.form-group input,
.form-group select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

/* 等高列布局 */
.equal-height-columns {
    display: flex;
    gap: 20px;
}

.column {
    flex: 1;
    background: white;
    padding: 20px;
    border: 1px solid #e0e0e0;
}

/* 自适应侧边栏布局 */
.main-layout {
    display: flex;
    min-height: 100vh;
    gap: 20px;
}

.sidebar {
    flex: 0 0 250px;
    background: #f5f5f5;
    padding: 20px;
}

.main-content {
    flex: 1;
    padding: 20px;
    min-width: 0;
}

@media (max-width: 768px) {
    .main-layout {
        flex-direction: column;
    }
    
    .sidebar {
        flex: 0 0 auto;
        order: 2;
    }
    
    .main-content {
        order: 1;
    }
}
```

#### Grid网格布局

CSS Grid为二维布局提供了强大的解决方案，特别适合复杂的页面布局：

```css
/* 基础Grid容器 */
.grid-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr); /* 3列等宽 */
    grid-template-rows: auto 1fr auto; /* 头部自适应，主体填充，底部自适应 */
    grid-gap: 20px; /* 或者使用 gap: 20px */
    min-height: 100vh;
}

/* 命名网格线 */
.page-layout {
    display: grid;
    grid-template-columns: 
        [sidebar-start] 250px 
        [sidebar-end main-start] 1fr 
        [main-end];
    grid-template-rows: 
        [header-start] 60px 
        [header-end content-start] 1fr 
        [content-end footer-start] 40px 
        [footer-end];
    gap: 20px;
    min-height: 100vh;
}

/* 使用grid-template-areas定义布局 */
.dashboard-layout {
    display: grid;
    grid-template-areas:
        "header header header"
        "sidebar main aside"
        "footer footer footer";
    grid-template-columns: 200px 1fr 200px;
    grid-template-rows: 60px 1fr 40px;
    gap: 15px;
    min-height: 100vh;
}

.header { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main { grid-area: main; }
.aside { grid-area: aside; }
.footer { grid-area: footer; }

/* 监测数据网格布局 */
.data-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    padding: 20px;
}

.data-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 响应式Grid布局 */
.responsive-grid {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 20px;
}

.grid-item-12 { grid-column: span 12; }
.grid-item-6 { grid-column: span 6; }
.grid-item-4 { grid-column: span 4; }
.grid-item-3 { grid-column: span 3; }

@media (max-width: 768px) {
    .grid-item-6,
    .grid-item-4,
    .grid-item-3 {
        grid-column: span 12;
    }
}

/* 复杂的仪表板布局 */
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    grid-template-rows: repeat(4, 200px);
    gap: 15px;
    padding: 20px;
}

.overview-panel {
    grid-column: 1 / 4;
    grid-row: 1 / 2;
}

.quick-stats {
    grid-column: 4 / 7;
    grid-row: 1 / 2;
}

.main-chart {
    grid-column: 1 / 5;
    grid-row: 2 / 4;
}

.side-panels {
    grid-column: 5 / 7;
    grid-row: 2 / 4;
    display: grid;
    grid-template-rows: 1fr 1fr;
    gap: 15px;
}

.recent-alerts {
    grid-column: 1 / 7;
    grid-row: 4 / 5;
}

/* Grid项目定位 */
.featured-item {
    grid-column: 2 / 5;
    grid-row: 2 / 4;
    z-index: 1;
}

/* 隐式网格 */
.auto-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-auto-rows: 200px;
    grid-auto-flow: row dense; /* 自动填充 */
    gap: 15px;
}

.span-2 {
    grid-column: span 2;
}

.span-2-rows {
    grid-row: span 2;
}
```

### 视觉效果与装饰

CSS3在视觉效果方面提供了丰富的功能，包括圆角、阴影、渐变、变换等，为界面设计提供了强大的表现力。

#### 圆角与边框效果

```css
/* 基础圆角 */
.rounded-card {
    border-radius: 8px;
    background: white;
    border: 1px solid #e0e0e0;
}

/* 不同方向的圆角 */
.header-card {
    border-radius: 8px 8px 0 0; /* 上左 上右 下右 下左 */
}

.footer-card {
    border-radius: 0 0 8px 8px;
}

/* 圆形元素 */
.circular-avatar {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    overflow: hidden;
}

/* 椭圆形按钮 */
.pill-button {
    border-radius: 25px;
    padding: 10px 25px;
    background: #2196F3;
    color: white;
    border: none;
}

/* 复杂边框样式 */
.fancy-border {
    border: 3px solid;
    border-image: linear-gradient(45deg, #2196F3, #4CAF50, #FF9800) 1;
    border-radius: 0; /* border-image 不支持圆角 */
}

/* 多重边框 */
.multiple-borders {
    border: 3px solid #2196F3;
    box-shadow: 
        0 0 0 6px #4CAF50,
        0 0 0 9px #FF9800;
}

/* 渐变边框 */
.gradient-border {
    position: relative;
    background: white;
    border-radius: 8px;
}

.gradient-border::before {
    content: '';
    position: absolute;
    inset: 0;
    padding: 2px;
    background: linear-gradient(45deg, #2196F3, #4CAF50);
    border-radius: inherit;
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: xor;
    -webkit-mask-composite: xor;
}
```

#### 阴影效果

```css
/* 基础盒阴影 */
.card-shadow {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.elevated-card {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.floating-card {
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

/* 内阴影 */
.inset-shadow {
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 多重阴影 */
.complex-shadow {
    box-shadow: 
        0 2px 4px rgba(0, 0, 0, 0.1),
        0 8px 16px rgba(0, 0, 0, 0.1),
        0 16px 32px rgba(0, 0, 0, 0.1);
}

/* 彩色阴影 */
.colored-shadow {
    box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
}

/* 文字阴影 */
.text-shadow {
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.outline-text {
    color: white;
    text-shadow: 
        -1px -1px 0 #000,
        1px -1px 0 #000,
        -1px 1px 0 #000,
        1px 1px 0 #000;
}

/* 悬停效果 */
.hover-shadow {
    transition: box-shadow 0.3s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.hover-shadow:hover {
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    transform: translateY(-2px);
}

/* 分层阴影效果 */
.layered-shadow {
    position: relative;
}

.layered-shadow::before {
    content: '';
    position: absolute;
    top: 10px;
    left: 10px;
    right: -10px;
    bottom: -10px;
    background: rgba(0, 0, 0, 0.05);
    border-radius: inherit;
    z-index: -1;
}
```

#### 渐变背景

```css
/* 线性渐变 */
.linear-gradient-bg {
    background: linear-gradient(
        to right, 
        #2196F3, 
        #4CAF50
    );
}

.diagonal-gradient {
    background: linear-gradient(
        45deg, 
        #2196F3 0%, 
        #21CBF3 50%, 
        #4CAF50 100%
    );
}

/* 径向渐变 */
.radial-gradient-bg {
    background: radial-gradient(
        circle at center, 
        #2196F3, 
        #1976D2
    );
}

.ellipse-gradient {
    background: radial-gradient(
        ellipse at top left, 
        #4CAF50 0%, 
        #2196F3 100%
    );
}

/* 复杂渐变 */
.complex-gradient {
    background: linear-gradient(
        135deg,
        #667eea 0%,
        #764ba2 100%
    );
}

/* 多重渐变 */
.multiple-gradients {
    background: 
        linear-gradient(217deg, rgba(255,0,0,.8), rgba(255,0,0,0) 70.71%),
        linear-gradient(127deg, rgba(0,255,0,.8), rgba(0,255,0,0) 70.71%),
        linear-gradient(336deg, rgba(0,0,255,.8), rgba(0,0,255,0) 70.71%);
}

/* 渐变文字 */
.gradient-text {
    background: linear-gradient(45deg, #2196F3, #4CAF50);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent; /* 降级支持 */
}

/* 渐变边框（使用伪元素） */
.gradient-border-alt {
    position: relative;
    background: white;
    border-radius: 8px;
}

.gradient-border-alt::before {
    content: '';
    position: absolute;
    inset: -2px;
    background: linear-gradient(45deg, #2196F3, #4CAF50);
    border-radius: inherit;
    z-index: -1;
}

/* 动态渐变 */
.animated-gradient {
    background: linear-gradient(
        -45deg, 
        #2196F3, 
        #21CBF3, 
        #4CAF50, 
        #FFC107
    );
    background-size: 400% 400%;
    animation: gradient-shift 4s ease infinite;
}

@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
```

这些CSS3选择器和样式技术为智慧水利平台的界面设计提供了强大的技术支撑，能够创建出既美观又实用的用户界面，提升用户体验和系统的整体品质。
