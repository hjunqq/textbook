# CSS选择器详解

## 1. 选择器概述

CSS选择器是CSS规则的核心部分，用于指定样式将应用于哪些HTML元素。在智慧水利平台这样的复杂系统中，掌握各种选择器及其组合使用方法，对于精确控制界面元素的样式至关重要。

选择器的作用类似于"过滤器"，它告诉浏览器："请在HTML文档中找到所有符合这个条件的元素，并应用我定义的样式"。通过选择器，我们可以：

- 精确定位特定元素
- 基于元素之间的关系选择元素
- 根据元素的状态或属性选择元素
- 选择元素的特定部分

## 2. 基本选择器

基本选择器是最常用且最基础的选择器类型，它们直接根据元素的类型、ID或类名选择元素。

### 2.1 通用选择器

通用选择器（`*`）选择文档中的所有元素。

```css
* {
  box-sizing: border-box; /* 对所有元素应用盒模型设置 */
  margin: 0;
  padding: 0;
}
```

**使用场景**：
- 重置浏览器默认样式
- 应用全局盒模型设置
- CSS调试（如添加边框查看布局）

### 2.2 元素选择器

根据HTML标签名选择元素。

```css
h1 {
  font-size: 28px;
  color: #003366; /* 智慧水利平台的标题蓝 */
}

p {
  line-height: 1.6;
  margin-bottom: 1em;
}

button {
  background-color: #1890ff; /* 智慧水利平台的主题蓝 */
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
}
```

**使用场景**：
- 定义基础排版样式
- 设置元素默认外观
- 建立一致的视觉基调

### 2.3 类选择器

通过元素的`class`属性值选择元素。类选择器在CSS中使用点号（`.`）开头。

```css
.data-panel {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.water-level {
  color: #1890ff;
  font-weight: bold;
}

.warning {
  color: #faad14;
}

.danger {
  color: #ff4d4f;
}
```

**使用场景**：
- 应用模块化、可重用的样式
- 定义状态和修饰符
- 创建组件变体

### 2.4 ID选择器

通过元素的`id`属性值选择元素。ID选择器在CSS中使用井号（`#`）开头。

```css
#main-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

#water-level-chart {
  height: 400px;
  grid-column: span 2;
}

#control-panel {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: white;
}
```

**使用场景**：
- 唯一元素的样式（页面中只出现一次的元素）
- JavaScript交互目标
- 页面主要区域划分

### 2.5 属性选择器

根据元素的属性或属性值选择元素。

```css
/* 选择所有具有data-status属性的元素 */
[data-status] {
  position: relative;
}

/* 选择data-status属性为"warning"的元素 */
[data-status="warning"] {
  border-left: 4px solid #faad14;
}

/* 选择data-status属性为"danger"的元素 */
[data-status="danger"] {
  border-left: 4px solid #ff4d4f;
  background-color: #fff1f0;
}

/* 选择所有type为number的输入框 */
input[type="number"] {
  text-align: right;
}
```

**属性选择器的变体**：

- `[attr]`：选择具有指定属性的元素
- `[attr=value]`：选择属性值完全匹配的元素
- `[attr^=value]`：选择属性值以指定值开头的元素
- `[attr$=value]`：选择属性值以指定值结尾的元素
- `[attr*=value]`：选择属性值包含指定值的元素
- `[attr~=value]`：选择属性值包含指定词的元素（词以空格分隔）
- `[attr|=value]`：选择属性值以指定值开头或后跟连字符的元素

**应用示例**：

```css
/* 选择所有水库监测点 */
[data-station-type="reservoir"] {
  background-color: #e6f7ff;
}

/* 选择所有河道监测点 */
[data-station-type="river"] {
  background-color: #f6ffed;
}

/* 选择所有降雨监测点 */
[data-station-type="rainfall"] {
  background-color: #fff7e6;
}
```

## 3. 组合选择器

组合选择器通过元素之间的关系来选择元素，使我们能够更精确地定位复杂文档结构中的元素。

### 3.1 后代选择器

后代选择器选择指定元素的所有后代元素，无论嵌套层级如何。使用空格分隔。

```css
/* 选择.dashboard-card内部的所有.title元素 */
.dashboard-card .title {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 12px;
}

/* 选择#monitoring-section内部的所有表格 */
#monitoring-section table {
  width: 100%;
  border-collapse: collapse;
}

/* 选择.data-grid内部的所有段落中的所有强调文本 */
.data-grid p em {
  color: #1890ff;
}
```

**使用场景**：
- 为特定上下文中的元素定义样式
- 创建组件内部样式规则
- 覆盖通用样式

### 3.2 子元素选择器

子元素选择器选择指定元素的直接子元素，不包括更深层次的后代。使用大于号`>`分隔。

```css
/* 选择.nav-menu的直接子元素li */
.nav-menu > li {
  display: inline-block;
  margin-right: 20px;
}

/* 选择#data-table的直接子元素thead */
#data-table > thead {
  background-color: #f0f2f5;
}

/* 选择.panel的直接子元素h2 */
.panel > h2 {
  margin-top: 0;
  border-bottom: 1px solid #ddd;
}
```

**使用场景**：
- 设置列表项样式
- 控制直接子元素布局
- 避免样式渗透到更深层级

### 3.3 相邻兄弟选择器

相邻兄弟选择器选择紧接在指定元素后的同级元素。使用加号`+`分隔。

```css
/* 选择紧跟在h2后面的p元素 */
h2 + p {
  font-weight: 500;
  color: #333;
}

/* 选择紧跟在.form-group后面的.form-group */
.form-group + .form-group {
  margin-top: 16px;
}

/* 选择紧跟在.alert元素后面的.data-panel */
.alert + .data-panel {
  margin-top: 24px;
}
```

**使用场景**：
- 设置相邻元素间距
- 为跟在特定元素后的元素添加特殊样式
- 表单布局

### 3.4 通用兄弟选择器

通用兄弟选择器选择指定元素后的所有同级元素。使用波浪号`~`分隔。

```css
/* 选择h2后面的所有p元素 */
h2 ~ p {
  line-height: 1.6;
}

/* 选择.primary-reading后面的所有.secondary-reading元素 */
.primary-reading ~ .secondary-reading {
  font-size: 14px;
  color: #666;
}

/* 选择.alert-banner后面的所有.panel元素 */
.alert-banner ~ .panel {
  opacity: 0.8;
}
```

**使用场景**：
- 根据前面出现的元素设置后续元素样式
- 创建依赖于特定内容存在的样式规则

## 4. 伪类与伪元素

伪类和伪元素选择器用于选择元素的特定状态或部分，允许我们在不修改HTML的情况下应用样式。

### 4.1 状态伪类

状态伪类选择处于特定状态的元素。

#### 链接状态伪类

```css
/* 未访问链接 */
a:link {
  color: #1890ff;
}

/* 已访问链接 */
a:visited {
  color: #722ed1;
}

/* 鼠标悬停状态 */
a:hover {
  color: #40a9ff;
  text-decoration: underline;
}

/* 激活状态（鼠标按下） */
a:active {
  color: #096dd9;
}
```

**注意**：这些伪类应按照上述顺序声明，记忆方法：LoVe HAte（Link, Visited, Hover, Active）。

#### 交互状态伪类

```css
/* 获得焦点的输入框 */
input:focus {
  border-color: #40a9ff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

/* 禁用状态的按钮 */
button:disabled {
  background-color: #f5f5f5;
  color: rgba(0, 0, 0, 0.25);
  cursor: not-allowed;
}

/* 选中状态的复选框 */
input[type="checkbox"]:checked + label {
  color: #1890ff;
}
```

### 4.2 结构性伪类

结构性伪类根据元素在文档结构中的位置选择元素。

```css
/* 第一个子元素 */
.reading-list li:first-child {
  font-weight: bold;
}

/* 最后一个子元素 */
.reading-list li:last-child {
  border-bottom: none;
}

/* 偶数行 */
.data-table tr:nth-child(even) {
  background-color: #f9f9f9;
}

/* 奇数行 */
.data-table tr:nth-child(odd) {
  background-color: #ffffff;
}

/* 第n个子元素 */
.dashboard-grid .card:nth-child(3n+1) {
  background-color: #e6f7ff;
}

/* 唯一子元素 */
.alert:only-child {
  margin: 0;
}
```

**常用结构性伪类**：
- `:first-child`：第一个子元素
- `:last-child`：最后一个子元素
- `:nth-child(n)`：第n个子元素
- `:nth-last-child(n)`：倒数第n个子元素
- `:only-child`：唯一子元素
- `:first-of-type`：特定类型的第一个元素
- `:last-of-type`：特定类型的最后一个元素
- `:nth-of-type(n)`：特定类型的第n个元素
- `:empty`：没有子元素的元素

### 4.3 表单相关伪类

```css
/* 必填字段 */
input:required {
  border-left: 3px solid #1890ff;
}

/* 可选字段 */
input:optional {
  border-left: 1px solid #d9d9d9;
}

/* 有效输入 */
input:valid {
  border-color: #52c41a;
}

/* 无效输入 */
input:invalid {
  border-color: #ff4d4f;
}

/* 范围内的值 */
input[type="number"]:in-range {
  background-color: #f6ffed;
}

/* 范围外的值 */
input[type="number"]:out-of-range {
  background-color: #fff2f0;
}
```

### 4.4 否定伪类

`:not()`伪类选择不匹配指定选择器的元素。

```css
/* 选择非禁用的按钮 */
button:not(:disabled) {
  cursor: pointer;
}

/* 选择所有非.important的段落 */
p:not(.important) {
  color: #666;
}

/* 选择没有data-status属性的卡片 */
.station-card:not([data-status]) {
  background-color: #f5f5f5;
}

/* 选择非第一个子元素的列表项 */
li:not(:first-child) {
  border-top: 1px solid #eee;
}
```

### 4.5 伪元素

伪元素用于选择元素的特定部分或在元素前后插入内容。CSS3中伪元素使用双冒号`::`表示，以区别于伪类。

```css
/* 在元素前插入内容 */
.water-level::before {
  content: "水位: ";
  font-weight: normal;
  color: #666;
}

/* 在元素后插入内容 */
.required-field::after {
  content: "*";
  color: #ff4d4f;
  margin-left: 4px;
}

/* 首字样式 */
.introduction p::first-letter {
  font-size: 2em;
  font-weight: bold;
  color: #1890ff;
  float: left;
  padding-right: 8px;
}

/* 首行样式 */
.description::first-line {
  font-weight: bold;
  color: #333;
}

/* 选择文本样式 */
p::selection {
  background-color: rgba(24, 144, 255, 0.2);
  color: #1890ff;
}
```

**常用伪元素**：
- `::before`：在元素内容前插入内容
- `::after`：在元素内容后插入内容
- `::first-letter`：选择元素文本的第一个字母
- `::first-line`：选择元素文本的第一行
- `::selection`：选择用户选中的文本
- `::placeholder`：选择输入框的占位文本

## 5. 组合复杂选择器

在实际项目中，我们常常需要组合多种选择器来精确定位元素。复杂选择器的组合能力是CSS强大的基础。

### 5.1 组合模式示例

```css
/* 选择所有警告状态且显示中的监测站卡片 */
.station-card[data-status="warning"]:not(.hidden) {
  border-color: #faad14;
  background-color: #fffbe6;
}

/* 选择紧急警报列表中未确认的高优先级警报项 */
.alert-list .alert-item[data-severity="high"]:not([data-acknowledged="true"]) {
  background-color: #fff1f0;
  border-left: 4px solid #ff4d4f;
  font-weight: bold;
}

/* 选择水位超过警戒线的指示器的悬停提示 */
.water-level-indicator[data-value]:not([data-value=""]):hover::after {
  content: attr(data-value) "m";
  position: absolute;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 1;
}
```

### 5.2 智慧水利平台中的实际应用

以下是一个智慧水利平台水位监测界面中的复杂选择器应用示例：

```html
<div class="monitoring-panel" id="reservoir-status">
  <h2 class="panel-title">水库监测</h2>
  <div class="stations-grid">
    <!-- 正常状态水库 -->
    <div class="station-card" data-station-id="RS001" data-status="normal">
      <h3 class="station-name">龙泉水库</h3>
      <div class="reading-group">
        <div class="reading primary">
          <span class="label">水位</span>
          <span class="value">145.6</span>
          <span class="unit">m</span>
        </div>
        <div class="reading">
          <span class="label">蓄水量</span>
          <span class="value">3856</span>
          <span class="unit">万m³</span>
        </div>
      </div>
    </div>
    
    <!-- 警告状态水库 -->
    <div class="station-card" data-station-id="RS002" data-status="warning">
      <h3 class="station-name">青山水库</h3>
      <div class="reading-group">
        <div class="reading primary">
          <span class="label">水位</span>
          <span class="value">187.2</span>
          <span class="unit">m</span>
        </div>
        <div class="reading">
          <span class="label">蓄水量</span>
          <span class="value">5621</span>
          <span class="unit">万m³</span>
        </div>
      </div>
    </div>
  </div>
</div>
```

相应的CSS选择器：

```css
/* 基础卡片样式 */
.station-card {
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

/* 基于数据属性设置不同状态的卡片样式 */
.station-card[data-status="normal"] {
  border-left: 4px solid #52c41a;
  background-color: #f6ffed;
}

.station-card[data-status="warning"] {
  border-left: 4px solid #faad14;
  background-color: #fffbe6;
}

.station-card[data-status="danger"] {
  border-left: 4px solid #ff4d4f;
  background-color: #fff1f0;
}

/* 警告和危险状态卡片的动画效果 */
.station-card[data-status="warning"]:not(.acknowledged),
.station-card[data-status="danger"]:not(.acknowledged) {
  animation: pulse 2s infinite;
}

/* 主要读数样式 */
.reading.primary {
  padding-bottom: 8px;
  margin-bottom: 8px;
  border-bottom: 1px dashed #eee;
}

/* 值的样式，基于卡片状态变化 */
.station-card[data-status="normal"] .reading.primary .value {
  color: #52c41a;
}

.station-card[data-status="warning"] .reading.primary .value {
  color: #faad14;
  font-weight: bold;
}

.station-card[data-status="danger"] .reading.primary .value {
  color: #ff4d4f;
  font-weight: bold;
}

/* 悬停时显示额外信息 */
.station-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 使用伪元素添加状态标识 */
.station-card[data-status="warning"]::before,
.station-card[data-status="danger"]::before {
  content: "";
  position: absolute;
  top: 8px;
  right: 8px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.station-card[data-status="warning"]::before {
  background-color: #faad14;
}

.station-card[data-status="danger"]::before {
  background-color: #ff4d4f;
}
```

## 6. 选择器性能与最佳实践

CSS选择器的性能对于大型应用（如智慧水利平台）尤为重要。了解选择器的工作原理和性能影响可以帮助我们编写更高效的CSS。

### 6.1 选择器匹配原理

浏览器解析选择器的方式是从右向左匹配的。例如，对于选择器`.dashboard-panel .reading-card h3`：

1. 浏览器首先找到所有`h3`元素
2. 然后检查这些`h3`是否在`.reading-card`元素内
3. 最后检查这些`.reading-card`是否在`.dashboard-panel`内

### 6.2 性能优化原则

1. **避免过深的嵌套**
   ```css
   /* 不推荐 */
   .dashboard .panel .header .title span { ... }
   
   /* 推荐 */
   .dashboard-title { ... }
   ```

2. **限制使用通用选择器**
   ```css
   /* 不推荐 */
   .readings-panel * { ... }
   
   /* 推荐 */
   .readings-panel > * { ... } /* 如果必须使用，至少限制范围 */
   ```

3. **减少使用后代选择器，优先使用子选择器**
   ```css
   /* 可能性能较低 */
   .nav-menu li a { ... }
   
   /* 性能更好 */
   .nav-menu > li > a { ... }
   ```

4. **避免过度限定选择器**
   ```css
   /* 不必要的限定 */
   div.data-panel { ... }
   
   /* 更简洁 */
   .data-panel { ... }
   ```

### 6.3 选择器组织与命名约定

在智慧水利平台等大型系统中，采用一致的选择器命名和组织方式非常重要：

1. **BEM方法（Block, Element, Modifier）**
   ```css
   /* 块 */
   .water-level-card { ... }
   
   /* 元素 */
   .water-level-card__title { ... }
   .water-level-card__value { ... }
   
   /* 修饰符 */
   .water-level-card--warning { ... }
   .water-level-card--danger { ... }
   ```

2. **命名空间前缀**
   ```css
   /* 组件 */
   .c-card { ... }
   
   /* 布局 */
   .l-grid { ... }
   
   /* 工具类 */
   .u-hidden { ... }
   
   /* 状态 */
   .is-active { ... }
   .has-warning { ... }
   ```

## 7. 总结

CSS选择器是构建灵活、可维护的样式系统的基础。在智慧水利平台开发中，应灵活运用各类选择器，同时注意以下几点：

1. **选择器策略**：
   - 使用类选择器作为主要选择手段
   - 适当使用子选择器和伪类增强精确度
   - 谨慎使用ID选择器和过度嵌套

2. **命名与组织**：
   - 采用一致的命名约定（如BEM）
   - 按照功能组织选择器
   - 使用语义化命名，反映元素的用途

3. **性能考量**：
   - 避免不必要的复杂选择器
   - 优先使用类选择器而非复杂结构选择器
   - 在大型应用中考虑选择器性能 