# 4.3 CSS基础与样式设计

<!--
教材内容修改指导原则（2024年更新）：

1. 内容详实化原则：
   - 每个技术标签/概念都要有详细的功能解释和使用场景说明
   - 不能只有简短描述，必须包含：定义、特点、优势、适用场景
   - 解释要在代码示例之前，先理论后实践

2. 语言表达多样化原则：
   - 避免重复使用"智慧水利平台"等固定短语
   - 使用多样化表达：水利监测平台、监测系统、水利系统、数据监测系统等
   - 保持专业性的同时提升可读性

3. 代码示例实用化原则：
   - 代码要短小精悍，每个概念单独展示
   - 包含必要的属性和配置参数
   - 添加适当的注释说明
   - 提供完整但不冗长的示例

4. 教学结构规范化原则：
   - 采用"解释说明 + 代码示例"的结构
   - 重要概念用**重点内容**标注
   - 相关概念用表格形式总结
   - 章节末尾提供总结和过渡

5. 专业应用场景化原则：
   - 所有示例都要结合水利行业实际应用
   - 强调技术在实际项目中的价值
   - 提供具体的使用场景描述
-->

CSS（Cascading Style Sheets，层叠样式表）是用于描述Web页面视觉表现的样式语言，它与HTML和JavaScript一起构成了现代Web开发的三大基石。在水利监测平台开发中，CSS负责控制页面的布局结构、视觉样式和交互效果，是创建专业化、用户友好界面的关键技术。通过合理运用CSS，我们可以将枯燥的水文数据转化为直观美观的可视化界面，提升用户的使用体验和工作效率。

CSS3作为CSS的最新标准，在原有功能基础上新增了大量强大特性，包括新的选择器、动画效果、布局方法、视觉效果等，为现代Web应用的界面设计提供了更丰富的表现手段。在水利监测系统中，这些新特性能够帮助我们创建更加动态、交互性更强的监测界面，例如实时数据的动画展示、响应式的地图界面、渐变色的预警提示等。本节将系统介绍CSS3的核心技术特性，并重点讲解如何在水利平台中应用这些技术创建专业化的用户界面。

## 4.3.1 CSS3选择器与新特性

CSS选择器是CSS语言的核心组成部分，用于选择HTML文档中需要应用样式的元素。CSS3在原有选择器基础上新增了许多强大的选择器类型，使得样式定位更加精确和灵活。在水利监测平台的样式设计中，正确使用各种选择器不仅能够提高样式代码的效率，还能确保样式的可维护性和扩展性。

基础选择器是CSS选择器体系的基础，包括元素选择器、类选择器、ID选择器等。这些选择器虽然简单，但在水利系统界面设计中应用广泛，需要深入理解其使用原则和最佳实践。选择器的正确使用直接影响到样式的性能和维护性，特别是在复杂的数据监测界面中，合理的选择器策略能够显著提升开发效率和代码质量。

### CSS基础选择器详解

下面我们逐一介绍每种基础选择器的具体用法和应用场景：

#### 1. 元素选择器 - HTML标签直接样式化

元素选择器是最基本的CSS选择器，它直接通过HTML标签名来选择页面中的所有对应元素。这种选择器的优势在于简洁直观，能够为页面建立基础的样式规范。在水利监测系统中，元素选择器通常用于设置整体的排版风格、基础色彩方案和通用布局规则。

使用元素选择器时需要注意其全局性影响，因为它会作用于页面中所有同类型的HTML元素。这种特性既是优势也可能带来问题，因此在设计时需要仔细考虑样式的继承和覆盖关系。

```css
/* 为所有表格设置统一的边框和间距 */
table {
    border-collapse: collapse;  /* 合并边框，避免双重边框 */
    width: 100%;
    margin: 20px 0;
    font-family: 'Microsoft YaHei', Arial, sans-serif;
}

/* 为所有标题元素设置水利行业主题色 */
h1, h2, h3 {
    color: #1565c0;             /* 深蓝色体现专业性 */
    font-family: 'Microsoft YaHei', Arial, sans-serif;
    font-weight: 600;
    line-height: 1.4;
}

/* 监测数据区域的基础样式 */
section {
    padding: 20px;
    margin-bottom: 15px;
    background: #f8f9fa;        /* 浅灰背景提升可读性 */
    border-radius: 4px;
    border-left: 4px solid #2196f3;  /* 左侧蓝色边框作为装饰 */
}
```

#### 2. 类选择器 - 可复用的样式组件

类选择器是CSS中最常用和最灵活的选择器之一，通过HTML元素的class属性来选择元素。它的核心优势在于可复用性和模块化，允许我们创建独立的样式组件，这些组件可以在页面的不同位置重复使用。在水利监测系统的开发中，类选择器是实现组件化设计的重要工具。

类选择器支持多类名的灵活组合，一个HTML元素可以同时拥有多个class，这使得我们能够将基础样式和变体样式分离，创建更加灵活和可维护的样式体系。例如，我们可以定义一个基础的按钮样式类，然后通过不同的修饰类来实现不同颜色、尺寸的按钮变体。

```css
/* 基础水位数据显示样式类 */
.water-level {
    font-size: 18px;
    font-weight: bold;
    color: #2196f3;
    padding: 8px 12px;
    border-radius: 4px;
    background: rgba(33, 150, 243, 0.1);
    display: inline-block;
    min-width: 80px;
    text-align: center;
}

/* 不同监测状态的样式类 */
.status-normal { 
    color: #4caf50; 
    background: rgba(76, 175, 80, 0.1);
    border-left: 4px solid #4caf50;
}

.status-warning { 
    color: #ff9800; 
    background: rgba(255, 152, 0, 0.1);
    border-left: 4px solid #ff9800;
}

.status-danger { 
    color: #f44336; 
    background: rgba(244, 67, 54, 0.1);
    border-left: 4px solid #f44336;
    animation: pulse 2s infinite; /* 危险状态添加脉冲动画 */
}

/* 监测数据卡片组件样式 */
.monitor-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.monitor-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transform: translateY(-2px);
}
```

#### 3. ID选择器 - 唯一元素的特定样式

ID选择器用于选择页面中具有特定ID属性的唯一元素，它具有最高的CSS优先级（除了内联样式）。在水利监测系统中，ID选择器主要用于页面的主要结构元素，如导航栏、主内容区域、图表容器等具有唯一性和重要性的组件。

ID选择器的使用需要遵循"一个页面中每个ID只能使用一次"的原则，这确保了元素的唯一性。同时，由于其高优先级特性，ID选择器应当谨慎使用，避免造成样式覆盖的困难。在实际开发中，建议主要将ID选择器用于页面布局的主要容器和需要JavaScript操作的特定元素。

```css
/* 平台主导航栏 */
#main-nav {
    background: #1565c0;
    color: white;
    padding: 0 20px;
    height: 60px;
    display: flex;
    align-items: center;
    position: fixed;          /* 固定定位保持导航可见 */
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;           /* 确保导航在最顶层 */
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* 主内容容器 */
#main-content {
    max-width: 1200px;
    margin: 80px auto 0;     /* 顶部留出导航栏空间 */
    padding: 20px;
    min-height: calc(100vh - 140px); /* 确保内容区域最小高度 */
}

/* 实时监测数据图表的容器 */
#realtime-chart {
    width: 100%;
    height: 400px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
    position: relative;
    overflow: hidden;        /* 防止图表内容溢出 */
}

/* 数据统计面板 */
#stats-dashboard {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}
```

#### 4. 属性选择器 - 基于HTML属性的精确选择

属性选择器是CSS3中功能强大且灵活的选择器类型，它能够根据HTML元素的属性及其值来精确选择目标元素。这种选择器在数据驱动的水利监测系统中特别有用，因为我们经常需要根据数据的状态、类型或其他属性来应用不同的样式。

属性选择器支持多种匹配模式，包括属性存在判断、精确值匹配、部分值匹配等，这使得我们能够创建更加智能和动态的样式规则。在水利监测界面中，这种选择器常用于根据数据状态、设备类型、监测参数等属性来动态调整元素样式。

```css
/* 选择所有标记为必填的表单输入框 */
input[required] {
    border-left: 4px solid #2196f3;
    background: rgba(33, 150, 243, 0.05);
}

input[required]:focus {
    border-left-color: #1565c0;
    box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

/* 根据输入框类型设置不同样式 */
input[type="number"] {
    text-align: right;        /* 数值输入右对齐 */
    padding-right: 12px;
    font-family: 'Consolas', 'Monaco', monospace; /* 等宽字体便于数据对比 */
}

input[type="email"] {
    background-image: url('data:image/svg+xml,...'); /* 邮箱图标 */
    background-repeat: no-repeat;
    background-position: right 12px center;
    background-size: 16px;
    padding-right: 40px;
}

/* 根据数据状态属性设置不同的背景色 */
[data-status="normal"] { 
    background: #e8f5e8; 
    border-left: 4px solid #4caf50;
}

[data-status="warning"] { 
    background: #fff3e0; 
    border-left: 4px solid #ff9800;
}

[data-status="danger"] { 
    background: #ffebee; 
    border-left: 4px solid #f44336;
    position: relative;
}

/* 为危险状态添加闪烁提示 */
[data-status="danger"]::before {
    content: '⚠️';
    position: absolute;
    left: -15px;
    top: 50%;
    transform: translateY(-50%);
    animation: blink 1s infinite;
}

/* 根据设备类型设置不同的图标 */
[data-device="water-level"]::before { content: '🌊'; }
[data-device="flow-meter"]::before { content: '💧'; }
[data-device="rain-gauge"]::before { content: '☔'; }
[data-device="temperature"]::before { content: '🌡️'; }
```

### CSS3高级选择器详解

CSS3引入了多种高级选择器，提供了更加精确和灵活的元素选择能力。这些选择器在构建复杂的水利监测界面时特别有用，能够帮助我们实现精细化的样式控制。

#### 1. 关系选择器 - 基于元素关系的选择

关系选择器利用HTML文档中元素之间的父子、兄弟关系来选择目标元素。在水利监测系统的数据展示中，这类选择器能够帮助我们根据数据结构的层次关系来应用相应的样式，实现更加智能和结构化的界面设计。

```css
/* 直接子元素选择器 - 只选择直接子级 */
.monitor-panel > .data-item {
    border-bottom: 1px solid #eee;
    padding: 10px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.monitor-panel > .data-item:last-child {
    border-bottom: none;      /* 最后一项不显示底边框 */
}

/* 相邻兄弟选择器 - 选择紧邻的下一个兄弟元素 */
.data-label + .data-value {
    font-weight: bold;
    margin-left: 15px;
    color: #1565c0;
    font-family: 'Consolas', monospace; /* 数据值使用等宽字体 */
}

.warning-icon + .warning-text {
    color: #ff5722;
    font-weight: 600;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}

/* 通用兄弟选择器 - 选择所有后续兄弟元素 */
.section-title ~ .data-row {
    padding-left: 20px;       /* 为标题后的所有数据行添加缩进 */
    border-left: 2px solid #e3f2fd;
}

.error-message ~ input {
    border-color: #f44336;    /* 错误信息后的所有输入框标红 */
    background: rgba(244, 67, 54, 0.05);
}
```

#### 2. 伪类选择器 - 基于元素状态的动态选择

伪类选择器能够根据元素的状态、位置或用户交互来选择元素，为水利监测界面提供了丰富的交互反馈和动态效果。这类选择器特别适合用于创建响应用户操作的界面元素，如鼠标悬停效果、表格行的交替颜色、表单验证状态等。

伪类选择器的强大之处在于它们能够响应元素的动态状态变化，无需JavaScript即可实现丰富的交互效果。在数据密集的水利监测系统中，合理使用伪类选择器能够显著提升用户体验。

```css
/* 鼠标悬停效果 - 提供视觉反馈 */
.monitor-card:hover {
    box-shadow: 0 8px 16px rgba(0,0,0,0.15);
    transform: translateY(-3px) scale(1.02);
    transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
    border-color: #2196f3;
}

/* 焦点状态样式 - 增强可访问性 */
.form-input:focus {
    outline: none;
    border-color: #2196f3;
    box-shadow: 
        0 0 0 3px rgba(33, 150, 243, 0.1),
        0 2px 8px rgba(0, 0, 0, 0.1);
    background: white;
}

/* 表格行交替颜色和悬停效果 */
.data-table tr:nth-child(even) {
    background-color: #f8f9fa;
}

.data-table tr:hover {
    background-color: #e3f2fd;
    cursor: pointer;
    transform: scale(1.01);
    transition: all 0.2s ease;
}

/* 首个和最后一个元素的特殊样式 */
.data-list li:first-child {
    border-top: 3px solid #2196f3;
    font-weight: bold;
    background: linear-gradient(90deg, #e3f2fd, transparent);
}

.data-list li:last-child {
    border-bottom: none;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
}

/* 数据项的奇偶行样式 */
.monitor-grid .data-item:nth-child(odd) {
    background: rgba(33, 150, 243, 0.03);
}

.monitor-grid .data-item:nth-child(even) {
    background: rgba(76, 175, 80, 0.03);
}

/* 链接的不同状态 */
.nav-link:link { color: #1565c0; }
.nav-link:visited { color: #7b1fa2; }
.nav-link:hover { 
    color: #0d47a1; 
    text-decoration: underline;
    background: rgba(13, 71, 161, 0.1);
    padding: 4px 8px;
    border-radius: 4px;
}
.nav-link:active { color: #01579b; }
```

#### 3. 伪元素选择器 - 创建虚拟元素增强设计

伪元素选择器允许我们选择元素的特定部分或创建不存在于HTML中的虚拟元素，为页面添加装饰性内容或特殊效果。在水利监测系统中，伪元素常用于添加图标、创建装饰线条、实现特殊的文本效果等，能够在不增加HTML结构复杂度的情况下丰富界面的视觉表现。

`::before`和`::after`伪元素是最常用的伪元素，它们可以在元素的内容前后插入生成的内容。这些伪元素必须设置`content`属性才能显示，即使是空内容也需要设置为空字符串。

```css
/* 在数据项前添加装饰性图标 */
.water-level::before {
    content: "💧";
    margin-right: 8px;
    font-size: 1.2em;
    display: inline-block;
    animation: float 3s ease-in-out infinite; /* 浮动动画效果 */
}

/* 为数值添加单位后缀 */
.unit-meter::after {
    content: " 米";
    font-size: 0.85em;
    color: #666;
    margin-left: 3px;
    font-weight: normal;
}

.unit-cms::after {
    content: " m³/s";
    font-size: 0.85em;
    color: #666;
    margin-left: 3px;
}

/* 报告内容的首字母大写装饰 */
.report-content::first-letter {
    font-size: 2.5em;
    font-weight: bold;
    color: #1565c0;
    float: left;
    margin-right: 8px;
    margin-top: 4px;
    line-height: 0.8;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

/* 创建状态指示器 */
.status-indicator::before {
    content: '';
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
    background: #4caf50; /* 默认正常状态 */
}

.status-warning::before {
    background: #ff9800;
    animation: pulse 2s infinite;
}

.status-danger::before {
    background: #f44336;
    animation: blink 1s infinite;
}

/* 为卡片添加装饰性边框 */
.highlight-card::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #2196f3, #4caf50, #ff9800);
}

/* 选择文本的第一行 */
.intro-text::first-line {
    font-weight: bold;
    color: #1565c0;
    font-size: 1.1em;
}
```

### CSS3新增属性特性

CSS3引入了大量新的样式属性，为界面设计提供了更加丰富和强大的表现手段。这些新特性不仅增强了视觉效果，还提升了用户体验。在水利监测系统中，合理运用这些新特性能够创建更加现代化和专业化的用户界面。

#### 1. 边框和背景增强

CSS3在边框和背景处理方面的增强为创建精美的界面元素提供了强大支持。圆角边框、阴影效果、渐变背景等特性让我们能够摆脱传统的矩形设计限制，创建更加美观和现代的界面元素。

```css
/* 现代化圆角卡片设计 */
.rounded-card {
    border-radius: 12px;           /* 统一圆角 */
    background: white;
    border: 1px solid #e0e0e0;
    overflow: hidden;              /* 确保内容不超出圆角 */
    transition: all 0.3s ease;
}

/* 多层阴影效果创建深度感 */
.elevated-panel {
    box-shadow: 
        0 1px 3px rgba(0,0,0,0.12),      /* 近距离阴影 */
        0 1px 2px rgba(0,0,0,0.24),      /* 中距离阴影 */
        0 4px 8px rgba(0,0,0,0.08);      /* 远距离阴影 */
}

.elevated-panel:hover {
    box-shadow: 
        0 4px 8px rgba(0,0,0,0.12),
        0 2px 4px rgba(0,0,0,0.24),
        0 8px 16px rgba(0,0,0,0.08);
}

/* 水利主题渐变背景 */
.gradient-header {
    background: linear-gradient(135deg, #1565c0 0%, #1976d2 50%, #42a5f5 100%);
    color: white;
    padding: 30px;
    position: relative;
    overflow: hidden;
}

/* 为渐变背景添加动态效果 */
.gradient-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
    animation: shimmer 3s infinite;
    pointer-events: none;
}

/* 多重背景图层效果 */
.pattern-bg {
    background: 
        url('water-pattern.png') repeat,              /* 水纹图案 */
        radial-gradient(circle at 25% 25%, #e3f2fd 0%, transparent 50%),
        radial-gradient(circle at 75% 75%, #bbdefb 0%, transparent 50%),
        linear-gradient(to bottom, #e3f2fd, #f3e5f5); /* 基础渐变 */
    background-size: 
        100px 100px,      /* 图案尺寸 */
        200px 200px,      /* 第一个径向渐变 */
        150px 150px,      /* 第二个径向渐变 */
        cover;            /* 基础渐变覆盖全部 */
}

/* 特殊边框样式 */
.special-border {
    border: 2px solid transparent;
    border-radius: 8px;
    background: 
        linear-gradient(white, white) padding-box,
        linear-gradient(45deg, #2196f3, #4caf50, #ff9800) border-box;
}
```

#### 2. 文本效果增强

CSS3为文本处理提供了丰富的视觉效果选项，包括阴影、描边、渐变等。在水利监测系统中，这些文本效果能够突出重要信息，增强数据的视觉层次感，提升整体界面的专业性。

文本效果的使用需要考虑可读性和可访问性，过度的装饰可能会影响信息的传达效果。因此，在水利监测界面中应该适度使用这些效果，主要用于标题、重要数值、状态标识等关键信息的突出显示。

```css
/* 标题文字阴影效果 */
.title-shadow {
    text-shadow: 
        2px 2px 4px rgba(0,0,0,0.3),      /* 主阴影 */
        1px 1px 2px rgba(0,0,0,0.5);      /* 增强阴影 */
    color: #1565c0;
    font-weight: bold;
    letter-spacing: 1px;
}

/* 多层文字阴影创建立体效果 */
.embossed-text {
    color: #f5f5f5;
    text-shadow: 
        1px 1px 0px #ccc,
        2px 2px 0px #999,
        3px 3px 0px #666,
        4px 4px 5px rgba(0,0,0,0.3);
}

/* 文字描边效果（主要用于深色背景上的文字） */
.outlined-text {
    color: white;
    text-shadow: 
        -1px -1px 0 #1565c0,
        1px -1px 0 #1565c0,
        -1px 1px 0 #1565c0,
        1px 1px 0 #1565c0;
    /* 或使用webkit专有属性 */
    -webkit-text-stroke: 2px #1565c0;
    -webkit-text-fill-color: transparent;
}

/* 渐变文字效果 */
.gradient-text {
    background: linear-gradient(45deg, #2196f3, #4caf50, #ff9800);
    background-size: 200% 200%;           /* 扩大背景以支持动画 */
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradientShift 3s ease-in-out infinite;
    font-weight: bold;
    font-size: 1.2em;
}

/* 发光文字效果（用于重要警告） */
.glow-text {
    color: #ff4444;
    text-shadow: 
        0 0 5px #ff4444,
        0 0 10px #ff4444,
        0 0 15px #ff4444,
        0 0 20px #ff0000;
    animation: glow 2s ease-in-out infinite alternate;
}

/* 打字机效果文字 */
.typewriter-text {
    overflow: hidden;
    border-right: 2px solid #2196f3;
    white-space: nowrap;
    animation: 
        typing 3s steps(40, end),
        blink-caret 0.75s step-end infinite;
}

/* 数据高亮文字 */
.data-highlight {
    background: linear-gradient(120deg, transparent 0%, #2196f3 0%);
    background-size: 0% 100%;
    background-repeat: no-repeat;
    transition: background-size 0.5s ease;
}

.data-highlight:hover {
    background-size: 100% 100%;
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
}
```

## 4.3.2 CSS3布局系统

现代Web应用需要适应各种设备屏幕尺寸，CSS3提供了多种强大的布局方法来应对这一挑战。在水利监测平台中，合理的布局设计不仅能够确保数据信息的清晰展示，还能提升用户的操作效率。本小节将重点介绍Flexbox弹性布局和Grid网格布局这两种现代布局技术。

传统的CSS布局主要依赖float、position和display属性，虽然能够实现基本的布局需求，但在处理复杂的响应式布局时存在诸多限制。CSS3的Flexbox和Grid布局模型为现代Web应用提供了更加灵活和强大的布局解决方案。这两种布局方法各有特点：Flexbox适合一维布局（如导航栏、卡片排列），Grid适合二维布局（如整体页面结构）。

### Flexbox弹性布局详解

Flexbox（弹性盒子布局）是CSS3中的一维布局方法，特别适合处理组件内部元素的对齐和分布问题。它通过将容器设置为弹性容器，让其子元素（弹性项目）能够灵活地调整大小和位置，以最佳方式填充可用空间。

Flexbox的核心概念包括主轴（main axis）和交叉轴（cross axis）。主轴是弹性项目排列的主要方向，交叉轴与主轴垂直。通过控制这两个轴上的对齐和分布，我们可以实现各种复杂的布局效果。

#### 1. Flex容器属性详解

弹性容器是应用了`display: flex`或`display: inline-flex`的元素，它为其子元素建立了弹性布局上下文。容器属性控制着子元素的整体排列方式。

```css
/* 基础弹性容器设置 */
.flex-container {
    display: flex;
    justify-content: space-between;    /* 主轴对齐：两端对齐 */
    align-items: center;              /* 交叉轴对齐：居中对齐 */
    gap: 20px;                        /* 项目间距（现代浏览器支持） */
    flex-wrap: wrap;                  /* 允许换行 */
    min-height: 100px;                /* 确保容器有足够高度 */
}

/* 监测数据行的弹性布局 */
.data-row {
    display: flex;
    align-items: center;              /* 垂直居中对齐 */
    justify-content: space-between;   /* 标签和数值分别靠左右对齐 */
    padding: 15px;
    border-bottom: 1px solid #eee;
    transition: background 0.2s ease;
}

.data-row:hover {
    background: rgba(33, 150, 243, 0.05);
}

/* 导航栏的弹性布局 */
.nav-bar {
    display: flex;
    justify-content: space-between;   /* Logo和菜单分别在两端 */
    align-items: center;              /* 垂直居中 */
    padding: 0 20px;
    height: 60px;
    background: #1565c0;
    color: white;
    position: sticky;                 /* 粘性定位 */
    top: 0;
    z-index: 1000;
}

/* 弹性方向和换行控制 */
.responsive-flex {
    display: flex;
    flex-direction: row;              /* 默认水平排列 */
    flex-wrap: wrap;                  /* 允许换行 */
    align-content: flex-start;        /* 多行时的对齐方式 */
}

@media (max-width: 768px) {
    .responsive-flex {
        flex-direction: column;       /* 移动端改为垂直排列 */
    }
}
```

#### 2. Flex项目属性详解

弹性项目是弹性容器的直接子元素，它们可以通过特定的CSS属性来控制自己在容器中的行为。这些属性包括伸缩比例、基础尺寸、对齐方式等，为创建灵活的响应式布局提供了强大支持。

```css
/* 水利监测仪表板的卡片布局 */
.monitor-dashboard {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;                  /* 允许卡片换行 */
    padding: 20px;
}

.monitor-card {
    flex: 1 1 300px;                 /* flex-grow: 1, flex-shrink: 1, flex-basis: 300px */
    min-width: 280px;                /* 最小宽度保证可读性 */
    max-width: 400px;                /* 最大宽度防止过宽 */
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

/* 数据项的标签和数值布局 */
.data-item {
    display: flex;
    justify-content: space-between;
    align-items: baseline;            /* 基线对齐，适合不同字体大小 */
    margin: 12px 0;
    padding: 8px 0;
    border-bottom: 1px dotted #ddd;
}

.data-label {
    flex: 0 0 120px;                 /* 固定宽度标签 */
    color: #666;
    font-weight: 500;
}

.data-value {
    flex: 1;                         /* 占据剩余空间 */
    text-align: right;
    font-weight: bold;
    color: #1565c0;
    font-family: 'Consolas', monospace; /* 等宽字体便于对齐 */
}

.data-unit {
    flex: 0 0 auto;                  /* 不伸缩的单位标签 */
    margin-left: 5px;
    font-size: 0.9em;
    color: #888;
}

/* 按钮组的弹性布局 */
.button-group {
    display: flex;
    gap: 10px;
    margin-top: 20px;
}

.btn-primary {
    flex: 1;                         /* 按钮等宽分布 */
    min-height: 44px;                /* 触控友好的最小高度 */
}

.btn-secondary {
    flex: 0 0 auto;                  /* 保持内容宽度 */
}

/* 响应式卡片网格 */
@media (max-width: 768px) {
    .monitor-card {
        flex: 1 1 100%;              /* 移动端全宽显示 */
        max-width: none;
    }
    
    .data-item {
        flex-direction: column;       /* 垂直堆叠 */
        align-items: flex-start;
    }
    
    .data-label {
        flex: none;
        margin-bottom: 5px;
    }
    
    .data-value {
        text-align: left;
    }
}
```

#### 3. 实用的Flex布局模式

```css
/* 水利平台头部布局 */
.platform-header {
    display: flex;
    align-items: center;
    padding: 0 20px;
    height: 70px;
    background: linear-gradient(90deg, #1565c0, #1976d2);
    color: white;
}

.logo {
    flex: 0 0 auto;
    margin-right: 30px;
}

.nav-menu {
    flex: 1;
    display: flex;
    justify-content: center;
    gap: 30px;
}

.user-info {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    gap: 15px;
}

/* 监测数据三栏布局 */
.content-layout {
    display: flex;
    gap: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.sidebar {
    flex: 0 0 250px;           /* 固定侧边栏 */
    background: #f5f5f5;
    border-radius: 8px;
    padding: 20px;
}

.main-content {
    flex: 1;                   /* 主内容区自适应 */
    background: white;
    border-radius: 8px;
    padding: 20px;
}

.chart-panel {
    flex: 0 0 300px;           /* 固定图表面板 */
    background: white;
    border-radius: 8px;
    padding: 20px;
}
```

### Grid网格布局深度解析

CSS Grid是CSS3引入的二维布局系统，与Flexbox的一维特性不同，Grid可以同时控制行和列的布局，为创建复杂页面结构提供了强大而精确的控制能力。在水利监测平台的开发中，Grid布局特别适合仪表板设计、数据面板排列、复杂表单布局等场景，能够像Excel表格一样实现精确的位置控制。

#### 1. Grid容器基础概念与属性详解

Grid容器是应用了`display: grid`的元素，它建立了一个网格格式化上下文。网格由行（row）和列（column）组成，交叉形成网格线（grid line）和网格区域（grid area），为子元素提供精确的二维定位能力。

```css
/* 水利监测平台主仪表板网格容器 */
.main-dashboard {
    display: grid;
    /* 定义三列：侧边栏(固定) 主内容(弹性) 信息栏(固定) */
    grid-template-columns: 260px 1fr 320px;
    /* 定义三行：头部(自动高度) 主体(填充) 底部(固定) */
    grid-template-rows: 70px 1fr 45px;
    /* 使用区域名称模板，增强可读性和维护性 */
    grid-template-areas: 
        "sidebar header info-panel"     /* 第一行布局 */
        "sidebar main-content info-panel"  /* 第二行布局 */
        "footer footer footer";         /* 底部跨所有列 */
    gap: 18px 15px;                    /* 行间距18px，列间距15px */
    min-height: 100vh;                 /* 最小全屏高度 */
    padding: 20px;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    font-family: 'Microsoft YaHei', sans-serif;
}

/* 复杂的监测数据网格系统 */
.monitoring-data-grid {
    display: grid;
    /* 使用repeat和minmax创建自适应列 */
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    /* 自动生成行，最小200px高度 */
    grid-auto-rows: minmax(200px, auto);
    /* 设置网格间距 */
    gap: 25px 20px;
    padding: 30px;
    /* 对齐整个网格内容 */
    justify-content: start;
    align-content: start;
    /* 默认网格项目对齐方式 */
    justify-items: stretch;
    align-items: stretch;
}

/* 高级网格线命名和定位 */
.water-quality-layout {
    display: grid;
    /* 为网格线命名，便于项目定位 */
    grid-template-columns: 
        [nav-start] 200px 
        [nav-end content-start] 1fr 
        [content-end sidebar-start] 300px 
        [sidebar-end];
    grid-template-rows: 
        [header-start] 80px 
        [header-end body-start] 1fr 
        [body-end footer-start] 50px 
        [footer-end];
    gap: 15px;
    min-height: 100vh;
    max-width: 1400px;
    margin: 0 auto;
}

/* 嵌套网格实现复杂布局 */
.data-visualization-area {
    display: grid;
    grid-template-columns: 1fr 1fr;     /* 两列等宽 */
    grid-template-rows: repeat(3, 1fr);  /* 三行等高 */
    gap: 25px;
    padding: 25px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

/* 单个图表容器也使用嵌套网格 */
.chart-wrapper {
    display: grid;
    grid-template-rows: auto 1fr auto auto;  /* 标题-图表-数据-操作 */
    gap: 12px;
    background: #fefefe;
    border: 1px solid #e1e8ed;
    border-radius: 8px;
    padding: 20px;
    transition: all 0.3s ease;
    position: relative;
}

.chart-wrapper:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    transform: translateY(-2px);
}

.chart-title {
    grid-row: 1;
    font-size: 1.1em;
    font-weight: 600;
    color: #2c3e50;
    text-align: center;
    padding-bottom: 8px;
    border-bottom: 2px solid #3498db;
}

.chart-canvas {
    grid-row: 2;
    min-height: 250px;
    position: relative;
    overflow: hidden;
}

.chart-data-summary {
    grid-row: 3;
    font-size: 0.9em;
    color: #7f8c8d;
    text-align: center;
    padding: 8px 0;
    border-top: 1px dotted #bdc3c7;
}

.chart-controls {
    grid-row: 4;
    display: flex;
    justify-content: center;
    gap: 10px;
}
```
```

#### 2. Grid项目定位与区域分配详解

Grid项目是网格容器的直接子元素，它们可以通过多种方式进行精确定位：基于网格线的数字定位、基于命名网格线的定位、基于网格区域名称的定位等。这种灵活的定位机制使得复杂布局的实现变得直观而高效。

```css
/* 水利监测平台的完整布局实现 */
.water-monitoring-platform {
    display: grid;
    grid-template-areas: 
        "logo navigation user-info"
        "sidebar main-dashboard alerts"
        "sidebar data-tables alerts"
        "footer footer footer";
    grid-template-columns: 280px 1fr 350px;
    grid-template-rows: 70px 400px 1fr 60px;
    gap: 20px;
    padding: 20px;
    min-height: 100vh;
    background: #f8fafc;
}

/* 各区域的具体实现和样式 */
.platform-logo {
    grid-area: logo;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(45deg, #2196F3, #21CBF3);
    color: white;
    font-weight: bold;
    border-radius: 8px;
}

.main-navigation {
    grid-area: navigation;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 10px;
    align-items: center;
    background: white;
    border-radius: 8px;
    padding: 0 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.user-info-panel {
    grid-area: user-info;
    background: white;
    border-radius: 8px;
    padding: 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

/* 基于网格线数字的精确定位 */
.critical-alert-banner {
    /* 使用行列数字定位：从第1行到第2行，跨所有列 */
    grid-row: 1 / 2;
    grid-column: 1 / -1;        /* -1表示最后一条网格线 */
    background: linear-gradient(90deg, #ff6b6b, #ff8e8e);
    color: white;
    padding: 10px 20px;
    border-radius: 6px;
    text-align: center;
    font-weight: 600;
    animation: pulse 2s infinite;
    z-index: 10;
}

/* 使用命名网格线定位 */
.data-export-section {
    /* 假设我们之前定义了命名网格线 */
    grid-column: sidebar-end / alerts-start;
    grid-row: data-tables-start / footer-start;
    background: white;
    border-radius: 8px;
    padding: 25px;
    display: grid;
    grid-template-rows: auto 1fr auto;
    gap: 15px;
}

/* 跨越多个网格区域的特殊项目 */
.full-screen-report {
    /* 占据从第二行开始到底部的所有区域 */
    grid-row: 2 / -1;
    grid-column: 1 / -1;
    background: rgba(255,255,255,0.98);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    z-index: 100;
    display: none;              /* 默认隐藏，需要时显示 */
}

.full-screen-report.active {
    display: grid;
    grid-template-rows: auto 1fr auto;
    gap: 20px;
}

/* 动态生成的网格项目 */
.dynamic-sensor-card {
    /* JavaScript动态分配网格位置 */
    background: white;
    border-radius: 8px;
    padding: 20px;
    border-left: 4px solid #3498db;
    box-shadow: 0 3px 12px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
    
    /* 内部也使用网格布局 */
    display: grid;
    grid-template-areas: 
        "icon title status"
        "icon value trend"
        "controls controls controls";
    grid-template-columns: 60px 1fr auto;
    grid-template-rows: auto auto auto;
    gap: 10px 15px;
    align-items: center;
}

.sensor-icon {
    grid-area: icon;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.5em;
}

.sensor-title {
    grid-area: title;
    font-weight: 600;
    color: #2c3e50;
    margin: 0;
}

.sensor-status {
    grid-area: status;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8em;
    font-weight: 500;
    text-align: center;
}

.sensor-value {
    grid-area: value;
    font-size: 1.4em;
    font-weight: bold;
    color: #27ae60;
    font-family: 'Consolas', monospace;
}

.sensor-trend {
    grid-area: trend;
    font-size: 0.9em;
    color: #7f8c8d;
}

.sensor-controls {
    grid-area: controls;
    display: flex;
    gap: 8px;
    margin-top: 10px;
}
```
```

#### 3. 响应式Grid布局设计策略

现代水利监测平台需要在各种设备上提供一致的用户体验，从大屏显示器到移动设备，都应该能够清晰地展示监测数据和操作界面。Grid布局的响应式特性通过媒体查询、自动调整函数和弹性单位的组合，为不同屏幕尺寸提供优化的布局方案。

```css
/* 自适应监测卡片网格系统 */
.monitoring-cards-responsive {
    display: grid;
    /* auto-fit会自动调整列数，minmax确保最小宽度 */
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    /* auto-fill与auto-fit的区别：auto-fill会保留空列 */
    /* grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); */
    gap: 25px 20px;
    padding: 30px;
    max-width: 1600px;
    margin: 0 auto;
}

/* 每个监测卡片的内部网格布局 */
.monitoring-card-advanced {
    display: grid;
    grid-template-areas: 
        "icon title status"
        "icon metrics trend"
        "chart chart chart"
        "controls controls controls";
    grid-template-columns: 80px 1fr auto;
    grid-template-rows: auto auto 200px auto;
    gap: 15px 12px;
    
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 
        0 4px 6px rgba(0, 0, 0, 0.05),
        0 10px 20px rgba(0, 0, 0, 0.1);
    border-left: 5px solid #3498db;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    overflow: hidden;
    position: relative;
}

.monitoring-card-advanced:hover {
    transform: translateY(-8px);
    box-shadow: 
        0 8px 15px rgba(0, 0, 0, 0.1),
        0 15px 35px rgba(0, 0, 0, 0.15);
}

/* 复杂的数据表格Grid布局 */
.advanced-data-table {
    display: grid;
    /* 固定列宽用于表头对齐 */
    grid-template-columns: 
        minmax(60px, auto)    /* 序号列 */
        minmax(150px, 200px)  /* 站点名称 */
        minmax(120px, 1fr)    /* 水位数据 */
        minmax(120px, 1fr)    /* 流量数据 */
        minmax(100px, auto)   /* 状态列 */
        minmax(120px, auto);  /* 操作列 */
    gap: 0;                   /* 表格无间距 */
    border: 1px solid #e1e8ed;
    border-radius: 8px;
    overflow: hidden;
    background: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

/* 表格头部 */
.table-header {
    display: contents;        /* 使子元素成为网格项目 */
}

.table-header > * {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 16px 12px;
    font-weight: 600;
    text-align: center;
    border-right: 1px solid rgba(255,255,255,0.2);
}

.table-header > *:last-child {
    border-right: none;
}

/* 表格行 */
.table-row {
    display: contents;
}

.table-row > * {
    padding: 14px 12px;
    border-right: 1px solid #f1f3f4;
    border-bottom: 1px solid #f1f3f4;
    text-align: center;
    transition: background-color 0.2s ease;
}

.table-row:nth-child(even) > * {
    background: #f8f9fa;
}

.table-row:hover > * {
    background: #e3f2fd !important;
}

/* 响应式媒体查询实现 */
@media (max-width: 1200px) {
    .monitoring-cards-responsive {
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        padding: 20px;
        gap: 20px 15px;
    }
    
    .advanced-data-table {
        grid-template-columns: 
            50px                  /* 缩小序号列 */
            minmax(120px, 150px)  /* 缩小站点名称 */
            minmax(100px, 1fr)    /* 调整数据列 */
            minmax(100px, 1fr)
            80px                  /* 缩小状态列 */
            100px;                /* 缩小操作列 */
    }
}

@media (max-width: 768px) {
    .monitoring-cards-responsive {
        grid-template-columns: 1fr;  /* 单列布局 */
        padding: 15px;
        gap: 20px;
    }
    
    .monitoring-card-advanced {
        grid-template-areas: 
            "title title title"
            "icon metrics status"
            "chart chart chart"
            "controls controls controls";
        grid-template-columns: auto 1fr auto;
        padding: 20px;
    }
    
    /* 移动端表格采用卡片式布局 */
    .advanced-data-table {
        grid-template-columns: 1fr;  /* 单列 */
        gap: 15px;
        padding: 15px;
    }
    
    .table-header {
        display: none;            /* 隐藏表头 */
    }
    
    .table-row {
        display: grid;
        grid-template-columns: 1fr;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        padding: 15px;
        gap: 8px;
    }
    
    .table-row > * {
        border: none !important;
        background: none !important;
        padding: 8px 0 !important;
        text-align: left !important;
        border-bottom: 1px dotted #ddd !important;
    }
    
    .table-row > *:last-child {
        border-bottom: none !important;
    }
    
    /* 为移动端表格数据添加标签 */
    .table-row > *:nth-child(1)::before { content: "序号: "; font-weight: bold; color: #666; }
    .table-row > *:nth-child(2)::before { content: "站点: "; font-weight: bold; color: #666; }
    .table-row > *:nth-child(3)::before { content: "水位: "; font-weight: bold; color: #666; }
    .table-row > *:nth-child(4)::before { content: "流量: "; font-weight: bold; color: #666; }
    .table-row > *:nth-child(5)::before { content: "状态: "; font-weight: bold; color: #666; }
    .table-row > *:nth-child(6)::before { content: "操作: "; font-weight: bold; color: #666; }
}

@media (max-width: 480px) {
    .monitoring-card-advanced {
        padding: 15px;
        grid-template-areas: 
            "title status"
            "metrics metrics"
            "chart chart"
            "controls controls";
        grid-template-columns: 1fr auto;
        gap: 12px;
    }
    
    .table-row {
        padding: 12px;
        font-size: 0.9em;
    }
}
```
```

### 响应式设计技术全面解析

响应式设计是现代Web开发的基石，它确保水利监测平台能够在各种设备和屏幕尺寸上提供最佳的用户体验。通过弹性网格、灵活图像、CSS媒体查询等技术的综合应用，响应式设计让一套代码能够适应从大型显示器到移动设备的所有终端，这对于需要随时随地监控水利设施的管理人员来说至关重要。

#### 1. 媒体查询深度应用与断点策略

媒体查询是响应式设计的核心机制，它允许我们根据设备特征（如屏幕宽度、高度、分辨率、方向等）应用不同的CSS规则。在水利平台开发中，合理的断点设置能够确保数据在各种设备上都能清晰可读。

```css
/* 水利监测平台的完整响应式断点体系 */

/* 超大屏幕：大型显示器、会议室大屏 (≥1400px) */
@media screen and (min-width: 1400px) {
    .water-monitoring-dashboard {
        max-width: 1360px;
        margin: 0 auto;
        grid-template-columns: 320px 1fr 400px;  /* 更宽的侧栏和信息面板 */
    }
    
    .monitoring-cards-grid {
        grid-template-columns: repeat(4, 1fr);    /* 4列卡片布局 */
        gap: 30px 25px;
    }
    
    .data-charts-section {
        grid-template-columns: repeat(3, 1fr);    /* 3列图表布局 */
    }
    
    .detailed-table {
        font-size: 1rem;                         /* 标准字体大小 */
    }
    
    /* 大屏专用的详细信息显示 */
    .large-screen-details {
        display: block;
    }
}

/* 大屏幕：桌面电脑 (1200px - 1399px) */
@media screen and (min-width: 1200px) and (max-width: 1399px) {
    .water-monitoring-dashboard {
        grid-template-columns: 280px 1fr 350px;
        padding: 20px;
    }
    
    .monitoring-cards-grid {
        grid-template-columns: repeat(3, 1fr);    /* 3列卡片布局 */
        gap: 25px 20px;
    }
    
    .data-charts-section {
        grid-template-columns: repeat(2, 1fr);    /* 2列图表布局 */
    }
    
    /* 调整字体和间距以适应中等屏幕 */
    .card-title {
        font-size: 1.1em;
    }
    
    .data-value {
        font-size: 1.8em;
    }
}

/* 中等屏幕：小笔记本、大平板 (992px - 1199px) */
@media screen and (min-width: 992px) and (max-width: 1199px) {
    .water-monitoring-dashboard {
        grid-template-areas: 
            "header header header"
            "sidebar content info"
            "footer footer footer";
        grid-template-columns: 250px 1fr 300px;
        grid-template-rows: 70px 1fr 50px;
        gap: 15px;
    }
    
    .monitoring-cards-grid {
        grid-template-columns: repeat(2, 1fr);    /* 2列卡片布局 */
        gap: 20px 15px;
    }
    
    .data-charts-section {
        grid-template-columns: 1fr 1fr;
    }
    
    /* 紧凑的导航菜单 */
    .main-navigation {
        font-size: 0.9em;
        gap: 8px;
    }
    
    .nav-item {
        padding: 8px 12px;
    }
}

/* 小屏幕：平板竖屏 (768px - 991px) */
@media screen and (min-width: 768px) and (max-width: 991px) {
    .water-monitoring-dashboard {
        grid-template-areas: 
            "header header"
            "sidebar content"
            "info info"
            "footer footer";
        grid-template-columns: 200px 1fr;
        grid-template-rows: auto 1fr auto auto;
        gap: 15px;
        padding: 15px;
    }
    
    .monitoring-cards-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 18px 12px;
    }
    
    .data-charts-section {
        grid-template-columns: 1fr;              /* 单列图表 */
        gap: 20px;
    }
    
    /* 平板优化的表格显示 */
    .data-table-responsive {
        display: grid;
        grid-template-columns: 1fr;
        gap: 10px;
    }
    
    .table-row-tablet {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        padding: 12px;
        background: white;
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 隐藏次要功能，突出核心数据 */
    .secondary-info {
        display: none;
    }
    
    .primary-data {
        font-size: 1.2em;
        font-weight: bold;
    }
}

/* 小屏幕：手机横屏、小平板 (576px - 767px) */
@media screen and (min-width: 576px) and (max-width: 767px) {
    .water-monitoring-dashboard {
        grid-template-areas: 
            "header"
            "content"
            "sidebar"
            "info"
            "footer";
        grid-template-columns: 1fr;
        gap: 12px;
        padding: 12px;
    }
    
    .monitoring-cards-grid {
        grid-template-columns: 1fr 1fr;          /* 2列紧凑布局 */
        gap: 15px 10px;
    }
    
    .monitoring-card-compact {
        padding: 15px;
        display: grid;
        grid-template-areas: 
            "title value"
            "status trend";
        grid-template-columns: 1fr auto;
        gap: 8px;
        align-items: center;
    }
    
    .card-title {
        grid-area: title;
        font-size: 0.9em;
        font-weight: 600;
        color: #2c3e50;
    }
    
    .card-value {
        grid-area: value;
        font-size: 1.3em;
        font-weight: bold;
        color: #27ae60;
        text-align: right;
    }
    
    .card-status {
        grid-area: status;
        font-size: 0.8em;
        color: #7f8c8d;
    }
    
    .card-trend {
        grid-area: trend;
        font-size: 0.8em;
        text-align: right;
    }
    
    /* 简化的导航菜单 */
    .main-navigation {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
        gap: 5px;
        font-size: 0.8em;
    }
}

/* 超小屏幕：手机竖屏 (≤575px) */
@media screen and (max-width: 575px) {
    .water-monitoring-dashboard {
        grid-template-areas: 
            "header"
            "content"
            "footer";
        grid-template-columns: 1fr;
        gap: 10px;
        padding: 10px;
        margin: 0;
    }
    
    .monitoring-cards-grid {
        grid-template-columns: 1fr;              /* 单列布局 */
        gap: 12px;
    }
    
    .monitoring-card-mobile {
        padding: 12px;
        display: grid;
        grid-template-areas: 
            "title"
            "value"
            "details"
            "actions";
        gap: 10px;
        border-left: 4px solid #3498db;
    }
    
    .card-title-mobile {
        grid-area: title;
        font-size: 1em;
        font-weight: 600;
        color: #2c3e50;
        margin: 0;
    }
    
    .card-value-mobile {
        grid-area: value;
        font-size: 2em;
        font-weight: bold;
        color: #27ae60;
        text-align: center;
        padding: 10px 0;
        background: #f8f9fa;
        border-radius: 4px;
    }
    
    .card-details-mobile {
        grid-area: details;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        font-size: 0.8em;
        color: #666;
    }
    
    .card-actions-mobile {
        grid-area: actions;
        display: flex;
        gap: 8px;
        justify-content: center;
    }
    
    .btn-mobile {
        flex: 1;
        padding: 8px 12px;
        border: none;
        border-radius: 4px;
        font-size: 0.9em;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    /* 移动端专用的侧边导航 */
    .mobile-sidebar {
        position: fixed;
        top: 0;
        left: -300px;                            /* 默认隐藏 */
        width: 300px;
        height: 100vh;
        background: white;
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        transition: left 0.3s ease;
        z-index: 1000;
        overflow-y: auto;
    }
    
    .mobile-sidebar.active {
        left: 0;                                 /* 显示状态 */
    }
    
    .mobile-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 999;
        display: none;
    }
    
    .mobile-overlay.active {
        display: block;
    }
    
    /* 移动端数据表格采用卡片堆叠 */
    .table-mobile {
        display: block;
    }
    
    .table-row-mobile {
        display: block;
        background: white;
        margin-bottom: 10px;
        border-radius: 6px;
        padding: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    
    .table-cell-mobile {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px dotted #ddd;
    }
    
    .table-cell-mobile:last-child {
        border-bottom: none;
    }
    
    .cell-label {
        font-weight: 600;
        color: #666;
        font-size: 0.9em;
    }
    
    .cell-value {
        font-weight: bold;
        color: #2c3e50;
    }
}

/* 超高分辨率屏幕适配 */
@media screen and (-webkit-min-device-pixel-ratio: 2), 
       screen and (min-resolution: 192dpi) {
    .icon, .chart-canvas, .data-visualization {
        image-rendering: -webkit-optimize-contrast;
        image-rendering: optimizeQuality;
    }
    
    /* 高分辨率下的字体平滑 */
    body {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
}

/* 打印样式 */
@media print {
    .water-monitoring-dashboard {
        display: block !important;
        grid-template-areas: none !important;
        grid-template-columns: none !important;
    }
    
    .no-print {
        display: none !important;
    }
    
    .monitoring-card {
        break-inside: avoid;
        margin-bottom: 20px;
    }
    
    .chart-container {
        break-inside: avoid;
    }
    
    body {
        font-size: 12pt;
        line-height: 1.4;
    }
}
```
        gap: 10px;
    }
}

/* 手机端 */
@media screen and (max-width: 480px) {
    .monitoring-cards {
        grid-template-columns: 1fr;
        gap: 15px;
        padding: 15px;
    }
    
    .data-grid {
        grid-template-columns: 1fr;
        gap: 5px;
        text-align: center;
    }
}
```

#### 2. 移动端交互优化与触控体验

移动设备的触控交互与桌面鼠标操作有着根本性差异，在水利监测平台的移动端适配中，需要特别关注触控区域大小、手势操作、屏幕方向变化等因素。良好的移动端体验能够确保现场工作人员在各种环境下都能高效地操作系统。

```css
/* 触控友好的交互元素尺寸标准 */
.touch-friendly-button {
    min-height: 44px;                        /* Apple建议的最小触控尺寸 */
    min-width: 44px;
    padding: 12px 20px;
    border: none;
    border-radius: 8px;
    font-size: 16px;                         /* 防止iOS自动缩放 */
    font-weight: 500;
    cursor: pointer;
    user-select: none;                       /* 防止长按选中文字 */
    -webkit-tap-highlight-color: transparent; /* 移除点击高亮 */
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}

/* 按钮的触摸反馈效果 */
.touch-friendly-button::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255,255,255,0.3);
    transition: width 0.3s ease, height 0.3s ease;
    transform: translate(-50%, -50%);
    pointer-events: none;
}

.touch-friendly-button:active::before {
    width: 300px;
    height: 300px;
}

/* 水利数据录入表单的移动端优化 */
.mobile-form-container {
    padding: 20px 15px;
    background: white;
    border-radius: 12px 12px 0 0;
    margin-top: 20px;
}

.mobile-form-group {
    margin-bottom: 20px;
    position: relative;
}

.mobile-form-label {
    display: block;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 8px;
    font-size: 1rem;
}

.mobile-form-input {
    width: 100%;
    min-height: 50px;                        /* 比标准更大，便于操作 */
    padding: 15px 12px;
    border: 2px solid #e1e8ed;
    border-radius: 8px;
    font-size: 16px;                         /* 防止iOS缩放 */
    background: white;
    transition: all 0.3s ease;
    -webkit-appearance: none;                /* 移除默认样式 */
    appearance: none;
}

.mobile-form-input:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    transform: translateY(-2px);
}

/* 数字输入的专用样式 */
.mobile-number-input {
    text-align: center;
    font-size: 18px;
    font-weight: bold;
    color: #2c3e50;
    font-family: 'Consolas', monospace;
}

/* 移动端导航菜单优化 */
.mobile-navigation {
    position: fixed;
    top: 0;
    left: -320px;                           /* 初始隐藏在屏幕外 */
    width: 320px;
    height: 100vh;
    background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    box-shadow: 2px 0 15px rgba(0,0,0,0.2);
    transition: left 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    z-index: 1000;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;       /* iOS惯性滚动 */
}

.mobile-navigation.active {
    left: 0;                                /* 显示状态 */
}

.mobile-nav-header {
    background: rgba(0,0,0,0.2);
    padding: 25px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.mobile-nav-title {
    color: white;
    font-size: 1.2em;
    font-weight: bold;
    margin: 0;
}

.mobile-nav-subtitle {
    color: rgba(255,255,255,0.7);
    font-size: 0.9em;
    margin: 5px 0 0 0;
}

.mobile-nav-menu {
    padding: 15px 0;
}

.mobile-nav-item {
    display: block;
    padding: 15px 20px;
    color: white;
    text-decoration: none;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    transition: all 0.2s ease;
    font-size: 1rem;
    font-weight: 500;
}

.mobile-nav-item:hover,
.mobile-nav-item:active {
    background: rgba(52, 152, 219, 0.2);
    padding-left: 25px;
    color: #3498db;
}

.mobile-nav-item.active {
    background: rgba(52, 152, 219, 0.3);
    border-left: 4px solid #3498db;
    color: #3498db;
}

/* 遮罩层 */
.mobile-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    z-index: 999;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
}

.mobile-overlay.active {
    opacity: 1;
    visibility: visible;
}

/* 汉堡菜单按钮动画 */
.hamburger-menu {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    width: 28px;
    height: 28px;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    z-index: 1001;
}

.hamburger-line {
    width: 28px;
    height: 3px;
    background: white;
    border-radius: 2px;
    transition: all 0.3s ease;
    transform-origin: center;
}

.hamburger-menu.active .hamburger-line:nth-child(1) {
    transform: rotate(45deg) translate(6px, 6px);
}

.hamburger-menu.active .hamburger-line:nth-child(2) {
    opacity: 0;
    transform: scaleX(0);
}

.hamburger-menu.active .hamburger-line:nth-child(3) {
    transform: rotate(-45deg) translate(8px, -8px);
}

/* 移动端数据卡片的滑动操作 */
.swipeable-card {
    position: relative;
    background: white;
    border-radius: 8px;
    margin-bottom: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    overflow: hidden;
    transform: translateX(0);
    transition: transform 0.3s ease;
}

.swipeable-card.swiping-left {
    transform: translateX(-80px);
}

.swipeable-card.swiping-right {
    transform: translateX(80px);
}

.card-actions {
    position: absolute;
    top: 0;
    right: -80px;
    width: 80px;
    height: 100%;
    background: #e74c3c;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.2em;
}

/* 底部操作栏（适合移动端的固定操作区域） */
.mobile-bottom-actions {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    border-top: 1px solid #e1e8ed;
    padding: 15px 20px;
    padding-bottom: calc(15px + env(safe-area-inset-bottom)); /* 适配刘海屏 */
    display: flex;
    gap: 12px;
    z-index: 100;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
}

.mobile-action-button {
    flex: 1;
    min-height: 50px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}

.mobile-action-primary {
    background: #3498db;
    color: white;
}

.mobile-action-secondary {
    background: #ecf0f1;
    color: #2c3e50;
    border: 1px solid #bdc3c7;
}

.mobile-action-button:active {
    transform: scale(0.98);
}

/* 屏幕方向变化适配 */
@media screen and (orientation: landscape) and (max-height: 500px) {
    .mobile-form-container {
        padding: 15px;
        margin-top: 10px;
    }
    
    .mobile-form-input {
        min-height: 40px;
        padding: 12px;
    }
    
    .mobile-bottom-actions {
        padding: 10px 20px;
        padding-bottom: calc(10px + env(safe-area-inset-bottom));
    }
    
    .mobile-action-button {
        min-height: 40px;
        font-size: 14px;
    }
}

/* iOS Safari特有的适配 */
@supports (-webkit-appearance: none) {
    .mobile-form-input {
        -webkit-appearance: none;
        border-radius: 8px;
    }
    
    /* 修复iOS下的输入框样式 */
    input[type="text"],
    input[type="number"],
    input[type="email"],
    textarea {
        -webkit-appearance: none;
        -webkit-border-radius: 8px;
    }
}

/* Android Chrome特有的适配 */
@media screen and (-webkit-min-device-pixel-ratio: 0) {
    .mobile-form-input:focus {
        /* 防止Android放大页面 */
        zoom: 1;
    }
}
```
```

## 4.3.4 CSS3动画与过渡效果深度应用

CSS3的动画和过渡效果是现代Web界面不可或缺的组成部分，它们不仅能够提升用户体验，更重要的是可以有效地传达信息、引导用户操作、减少认知负荷。在水利监测平台中，恰当的动画效果可以突出关键数据变化、指示系统状态、提供操作反馈，让复杂的监测系统变得更加直观易用。

### CSS3过渡效果精细化控制

过渡(Transition)是CSS3提供的一种在元素状态改变时创建平滑动画的机制。与关键帧动画不同，过渡专注于两个状态之间的变化过程，具有简单易用、性能优秀的特点，特别适合用户交互响应。

#### 1. 过渡属性深度解析与实际应用

```css
/* 水利监测数据卡片的精细化过渡效果 */
.water-data-card {
    background: white;
    border-radius: 12px;
    padding: 25px;
    margin: 15px;
    border-left: 5px solid #3498db;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
    
    /* 多属性过渡配置 */
    transition: 
        transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1),    /* 变形动画 */
        box-shadow 0.3s cubic-bezier(0.25, 0.8, 0.25, 1),  /* 阴影动画 */
        border-left-width 0.2s ease-out,                   /* 边框宽度 */
        background-color 0.2s ease-in-out;                 /* 背景色变化 */
}

.water-data-card:hover {
    transform: translateY(-8px) scale(1.02);               /* 提升和轻微缩放 */
    box-shadow: 
        0 10px 25px rgba(0,0,0,0.15),                      /* 主阴影 */
        0 5px 10px rgba(52, 152, 219, 0.2);               /* 彩色光晕 */
    border-left-width: 8px;                               /* 边框加宽 */
    background-color: #fafbfc;                            /* 背景微调 */
}

.water-data-card:active {
    transform: translateY(-2px) scale(0.98);              /* 点击反馈 */
    transition-duration: 0.1s;                           /* 快速反应 */
}

/* 关键数据的呼吸动画效果 */
.critical-value {
    font-size: 2.2em;
    font-weight: bold;
    color: #2c3e50;
    display: inline-block;
    position: relative;
    
    /* 值变化时的过渡 */
    transition: 
        color 0.5s ease,
        transform 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55); /* 弹性效果 */
}

/* 数值异常时的警告动画 */
.critical-value.warning {
    color: #f39c12;
    animation: valueWarning 2s ease-in-out infinite;
}

.critical-value.danger {
    color: #e74c3c;
    animation: valueDanger 1.5s ease-in-out infinite;
}

.critical-value.updated {
    transform: scale(1.15);
    color: #27ae60;
}

@keyframes valueWarning {
    0%, 100% { 
        opacity: 1; 
        transform: scale(1); 
    }
    50% { 
        opacity: 0.7; 
        transform: scale(1.05); 
    }
}

@keyframes valueDanger {
    0%, 100% { 
        opacity: 1; 
        transform: scale(1); 
        box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.4); 
    }
    25% { 
        opacity: 0.8; 
        transform: scale(1.08); 
        box-shadow: 0 0 0 8px rgba(231, 76, 60, 0.2); 
    }
    50% { 
        opacity: 1; 
        transform: scale(1.12); 
        box-shadow: 0 0 0 12px rgba(231, 76, 60, 0.1); 
    }
    75% { 
        opacity: 0.9; 
        transform: scale(1.05); 
        box-shadow: 0 0 0 6px rgba(231, 76, 60, 0.15); 
    }
}

/* 进度指示器的过渡效果 */
.progress-indicator {
    width: 100%;
    height: 8px;
    background: #ecf0f1;
    border-radius: 4px;
    overflow: hidden;
    position: relative;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #3498db, #2ecc71);
    border-radius: 4px;
    
    /* 宽度变化的平滑过渡 */
    transition: width 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    
    /* 流动效果的背景动画 */
    position: relative;
    overflow: hidden;
}

.progress-bar::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        90deg, 
        transparent, 
        rgba(255,255,255,0.4), 
        transparent
    );
    animation: progressShine 2s infinite;
}

@keyframes progressShine {
    0% { left: -100%; }
    50% { left: 100%; }
    100% { left: 100%; }
}

/* 状态切换的颜色过渡 */
.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    position: relative;
    
    /* 所有状态变化的平滑过渡 */
    transition: 
        background-color 0.4s ease,
        box-shadow 0.4s ease,
        transform 0.2s ease;
}

.status-indicator.online {
    background-color: #27ae60;
    box-shadow: 
        0 0 0 3px rgba(39, 174, 96, 0.2),
        inset 0 1px 1px rgba(255,255,255,0.3);
}

.status-indicator.offline {
    background-color: #e74c3c;
    box-shadow: 
        0 0 0 3px rgba(231, 76, 60, 0.2),
        inset 0 1px 1px rgba(0,0,0,0.1);
}

.status-indicator.maintenance {
    background-color: #f39c12;
    box-shadow: 
        0 0 0 3px rgba(243, 156, 18, 0.2),
        inset 0 1px 1px rgba(255,255,255,0.3);
    animation: maintenanceBlink 2s ease-in-out infinite;
}

@keyframes maintenanceBlink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* 表单验证的过渡反馈 */
.form-field {
    position: relative;
    margin-bottom: 20px;
}

.form-input {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e1e8ed;
    border-radius: 6px;
    font-size: 16px;
    background: white;
    
    /* 焦点和验证状态的过渡 */
    transition: 
        border-color 0.3s ease,
        box-shadow 0.3s ease,
        background-color 0.2s ease;
}

.form-input:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    background-color: #fafbfc;
}

.form-input.valid {
    border-color: #27ae60;
    background-color: rgba(39, 174, 96, 0.05);
}

.form-input.invalid {
    border-color: #e74c3c;
    background-color: rgba(231, 76, 60, 0.05);
    animation: shakeError 0.5s ease-in-out;
}

@keyframes shakeError {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
    20%, 40%, 60%, 80% { transform: translateX(5px); }
}

/* 错误消息的淡入淡出效果 */
.error-message {
    color: #e74c3c;
    font-size: 14px;
    margin-top: 8px;
    opacity: 0;
    transform: translateY(-10px);
    
    transition: 
        opacity 0.3s ease,
        transform 0.3s ease;
}

.error-message.show {
    opacity: 1;
    transform: translateY(0);
}

/* 按钮的多状态过渡效果 */
.action-button {
    background: #3498db;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    
    /* 基础过渡设置 */
    transition: 
        background-color 0.2s ease,
        transform 0.1s ease,
        box-shadow 0.2s ease;
}

.action-button:hover {
    background: #2980b9;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.action-button:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(52, 152, 219, 0.2);
}

.action-button:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

/* 加载状态的按钮动画 */
.action-button.loading {
    color: transparent;
    cursor: wait;
}

.action-button.loading::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 16px;
    height: 16px;
    margin: -8px 0 0 -8px;
    border: 2px solid rgba(255,255,255,0.3);
    border-top: 2px solid white;
    border-radius: 50%;
    animation: buttonSpin 1s linear infinite;
}

@keyframes buttonSpin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
```

/* 监测卡片悬停效果 */
.monitor-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: 
        transform 0.3s ease,
        box-shadow 0.3s ease;
}

.monitor-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.15);
}

/* 按钮交互效果 */
.water-button {
    background: #2196f3;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s ease;
}

.water-button:hover {
    background: #1976d2;
}

.water-button:active {
    transform: scale(0.98);
    transition: transform 0.1s ease;
}
```

#### 2. 表单输入框过渡效果

```css
/* 输入框焦点效果 */
.form-input {
    border: 2px solid #e0e0e0;
    padding: 12px;
    border-radius: 4px;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-input:focus {
    outline: none;
    border-color: #2196f3;
    box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

/* 标签浮动效果 */
.floating-label {
    position: relative;
}

.floating-label input {
    padding-top: 20px;
    padding-bottom: 5px;
}

.floating-label label {
    position: absolute;
    left: 12px;
    top: 12px;
    color: #666;
    pointer-events: none;
    transition: all 0.3s ease;
}

.floating-label input:focus + label,
.floating-label input:not(:placeholder-shown) + label {
    transform: translateY(-15px) scale(0.8);
    color: #2196f3;
}
```

### CSS3关键帧动画

关键帧动画提供更复杂的动画控制。

#### 1. 数据加载动画

```css
/* 加载旋转动画 */
@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.loading-spinner {
    width: 30px;
    height: 30px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #2196f3;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

/* 水波纹动画 */
@keyframes ripple {
    0% {
        transform: scale(0);
        opacity: 1;
    }
    100% {
        transform: scale(4);
        opacity: 0;
    }
}

.water-ripple::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: rgba(33, 150, 243, 0.3);
    animation: ripple 2s infinite;
}
```

#### 2. 数据更新提示动画

```css
/* 数据变化闪烁提示 */
@keyframes dataUpdate {
    0%, 100% { background: transparent; }
    50% { background: rgba(76, 175, 80, 0.3); }
}

.data-updated {
    animation: dataUpdate 0.8s ease-in-out;
}

/* 警告状态脉冲动画 */
@keyframes pulse {
    0% { 
        box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.7);
        transform: scale(1);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(244, 67, 54, 0);
        transform: scale(1.05);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(244, 67, 54, 0);
        transform: scale(1);
    }
}

.warning-indicator {
    animation: pulse 2s infinite;
}
```

#### 3. 进度条动画

```css
/* 数据加载进度条 */
@keyframes progressFill {
    from { width: 0%; }
    to { width: 100%; }
}

.progress-bar {
    width: 100%;
    height: 6px;
    background: #e0e0e0;
    border-radius: 3px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #2196f3, #4caf50);
    border-radius: 3px;
    animation: progressFill 3s ease-in-out;
}

/* 水位上升动画 */
@keyframes waterRise {
    from { 
        height: 0%;
        opacity: 0.7;
    }
    to { 
        height: var(--water-level);
        opacity: 1;
    }
}

.water-level-indicator {
    position: relative;
    width: 60px;
    height: 200px;
    border: 2px solid #2196f3;
    border-radius: 30px;
    overflow: hidden;
}

.water-fill {
    position: absolute;
    bottom: 0;
    width: 100%;
    background: linear-gradient(to top, #1976d2, #42a5f5);
    animation: waterRise 2s ease-out;
}
```

## 4.3.4 水利平台UI设计规范

在智慧水利平台的界面设计中，建立统一的UI设计规范至关重要。良好的设计规范不仅能够确保界面的一致性和专业性，还能提升用户体验和开发效率。水利行业具有其特殊性，需要结合行业特点制定适合的色彩方案、组件规范和交互模式。

### 水利主题色彩系统

水利行业的色彩设计应体现专业性、可信度和与水相关的自然属性。

#### 1. 主色调定义

```css
/* 水利主题色彩变量 */
:root {
    /* 主色调 - 蓝色系 */
    --primary-color: #1565c0;
    --primary-light: #42a5f5;
    --primary-dark: #0d47a1;
    
    /* 辅助色 */
    --secondary-color: #26a69a;
    --accent-color: #ff7043;
    
    /* 状态色 */
    --success-color: #4caf50;
    --warning-color: #ff9800;
    --error-color: #f44336;
    --info-color: #2196f3;
    
    /* 中性色 */
    --gray-50: #fafafa;
    --gray-100: #f5f5f5;
    --gray-200: #eeeeee;
    --gray-300: #e0e0e0;
    --gray-400: #bdbdbd;
    --gray-500: #9e9e9e;
    --gray-600: #757575;
    --gray-700: #616161;
    --gray-800: #424242;
    --gray-900: #212121;
}

/* 色彩应用示例 */
.primary-button {
    background-color: var(--primary-color);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 4px;
    cursor: pointer;
}

.secondary-button {
    background-color: var(--secondary-color);
    color: white;
}

.status-normal { color: var(--success-color); }
.status-warning { color: var(--warning-color); }
.status-error { color: var(--error-color); }
```

#### 2. 渐变色方案

```css
/* 水利主题渐变 */
.water-gradient-1 {
    background: linear-gradient(135deg, #1565c0, #42a5f5);
}

.water-gradient-2 {
    background: linear-gradient(to right, #26a69a, #4db6ac);
}

.depth-gradient {
    background: linear-gradient(to bottom, 
        #e3f2fd 0%,
        #bbdefb 25%,
        #90caf9 50%,
        #64b5f6 75%,
        #42a5f5 100%);
}

/* 数据可视化渐变 */
.chart-gradient {
    background: linear-gradient(45deg, 
        var(--primary-color),
        var(--secondary-color),
        var(--success-color));
}
```

### 组件化设计规范

建立统一的组件库确保界面的一致性。

#### 1. 按钮组件规范

```css
/* 按钮基础样式 */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 500;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 80px;
}

/* 按钮尺寸变体 */
.btn-small { padding: 6px 12px; font-size: 12px; }
.btn-medium { padding: 10px 20px; font-size: 14px; }
.btn-large { padding: 14px 28px; font-size: 16px; }

/* 按钮类型变体 */
.btn-primary {
    background: var(--primary-color);
    color: white;
}

.btn-primary:hover {
    background: var(--primary-dark);
}

.btn-secondary {
    background: var(--gray-100);
    color: var(--gray-700);
    border: 1px solid var(--gray-300);
}

.btn-outline {
    background: transparent;
    color: var(--primary-color);
    border: 2px solid var(--primary-color);
}

.btn-outline:hover {
    background: var(--primary-color);
    color: white;
}
```

#### 2. 卡片组件规范

```css
/* 基础卡片组件 */
.card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-header {
    padding: 20px;
    border-bottom: 1px solid var(--gray-200);
    background: var(--gray-50);
}

.card-body {
    padding: 20px;
}

.card-footer {
    padding: 15px 20px;
    border-top: 1px solid var(--gray-200);
    background: var(--gray-50);
}

/* 监测数据卡片 */
.monitor-card {
    position: relative;
}

.monitor-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--primary-color);
}

.monitor-card.warning::before {
    background: var(--warning-color);
}

.monitor-card.error::before {
    background: var(--error-color);
}
```

#### 3. 表格组件规范

```css
/* 数据表格样式 */
.data-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.data-table th {
    background: var(--gray-100);
    color: var(--gray-700);
    font-weight: 600;
    padding: 15px;
    text-align: left;
    border-bottom: 1px solid var(--gray-300);
}

.data-table td {
    padding: 15px;
    border-bottom: 1px solid var(--gray-200);
    color: var(--gray-800);
}

.data-table tr:hover {
    background: var(--gray-50);
}

.data-table tr:last-child td {
    border-bottom: none;
}

/* 状态指示器 */
.status-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 8px;
}

.status-indicator.normal { background: var(--success-color); }
.status-indicator.warning { background: var(--warning-color); }
.status-indicator.error { background: var(--error-color); }
```

### 响应式设计适配

确保水利平台在各种设备上的良好体验。

#### 1. 移动端适配策略

```css
/* 移动端基础适配 */
@media screen and (max-width: 768px) {
    .container {
        padding: 15px;
    }
    
    .monitor-card {
        margin-bottom: 15px;
    }
    
    .data-table {
        font-size: 14px;
    }
    
    .data-table th,
    .data-table td {
        padding: 10px;
    }
    
    /* 移动端隐藏次要信息 */
    .desktop-only {
        display: none;
    }
    
    /* 移动端按钮适配 */
    .btn {
        min-height: 44px;
        width: 100%;
        margin-bottom: 10px;
    }
}

/* 超小屏幕适配 */
@media screen and (max-width: 480px) {
    .card-body {
        padding: 15px;
    }
    
    .data-table {
        display: block;
        overflow-x: auto;
        white-space: nowrap;
    }
    
    /* 卡片式表格布局 */
    .mobile-table {
        display: block;
    }
    
    .mobile-table tr {
        display: block;
        border: 1px solid var(--gray-200);
        margin-bottom: 10px;
        border-radius: 4px;
    }
    
    .mobile-table td {
        display: block;
        text-align: right;
        border: none;
        padding: 8px;
    }
    
    .mobile-table td::before {
        content: attr(data-label);
        float: left;
        font-weight: bold;
        color: var(--gray-600);
    }
}
```

通过本节的学习，我们全面掌握了CSS3的核心技术和在智慧水利平台中的应用方法。从基础的选择器和样式属性，到现代的Flexbox和Grid布局系统，再到动画效果和UI设计规范，这些技术为创建专业化的水利信息系统界面提供了强有力的支撑。合理运用CSS3技术不仅能够提升用户体验，还能确保系统在不同设备上的一致性表现。在下一节中，我们将学习JavaScript技术，了解如何为静态的HTML和CSS添加动态交互功能。
