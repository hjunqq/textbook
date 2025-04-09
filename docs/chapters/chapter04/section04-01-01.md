# HTML5基础

## 1. HTML基本概念
HTML(超文本标记语言)是Web前端开发的基础，用于创建和组织网页内容和结构。HTML5是最新版本，提供了更丰富的语义化标签和功能。在智慧水利平台开发中，合理使用HTML结构对于提高页面可访问性和搜索引擎优化至关重要。

HTML文档是由元素(Elements)组成的，每个元素通常由开始标签、内容和结束标签组成。例如：
```html
<p>这是一个段落元素</p>
```

HTML元素可以包含属性(Attributes)，提供元素的附加信息：
```html
<a href="https://www.example.com" target="_blank">这是一个链接</a>
```

## 2. HTML5文档结构
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智慧水利平台</title>
    <meta name="description" content="智慧水利监测与管理平台">
    <link rel="stylesheet" href="styles.css">
    <script src="scripts.js" defer></script>
</head>
<body>
    <header>
        <!-- 页头内容 -->
    </header>
    <main>
        <!-- 主要内容 -->
    </main>
    <footer>
        <!-- 页脚内容 -->
    </footer>
</body>
</html>
```

每个部分的作用：
- `<!DOCTYPE html>`: 文档类型声明，告诉浏览器这是HTML5文档
- `<html>`: 根元素，包含整个HTML文档
- `<head>`: 包含元数据，如字符集、视口设置、标题、样式表链接等
- `<body>`: 包含可见的页面内容

## 3. HTML5语义化标签

HTML5引入了一系列语义化标签，使页面结构更加清晰和有意义。在水利平台开发中，语义化标签有助于构建更清晰的信息架构。

### 3.1 结构性标签

```html
<header>
    <h1>某流域智慧水利监测系统</h1>
    <nav>
        <!-- 导航菜单 -->
        <ul>
            <li><a href="#dashboard">监控面板</a></li>
            <li><a href="#monitoring">实时监测</a></li>
            <li><a href="#reports">统计报表</a></li>
            <li><a href="#management">系统管理</a></li>
        </ul>
    </nav>
</header>

<main>
    <section id="dashboard">
        <h2>监控面板</h2>
        <article class="dashboard-card">
            <h3>水库水位监测</h3>
            <!-- 水位监测内容 -->
        </article>
        <article class="dashboard-card">
            <h3>流量监测</h3>
            <!-- 流量监测内容 -->
        </article>
    </section>
    
    <section id="alerts">
        <h2>预警信息</h2>
        <aside class="notification-panel">
            <!-- 预警通知面板 -->
        </aside>
    </section>
</main>

<footer>
    <p>© 2023 智慧水利平台</p>
</footer>
```

这些语义化标签的作用：
- `<header>`: 页面或区段的头部
- `<nav>`: 导航链接区域
- `<main>`: 文档主要内容
- `<section>`: 文档中的一个区块
- `<article>`: 独立的、可复用的内容块
- `<aside>`: 与周围内容相关但可分离的内容
- `<footer>`: 页面或区段的底部 