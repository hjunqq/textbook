# 《智慧水利平台架构与开发》教材开发指南

## 项目概述

本项目是为水利专业本科大三年级学生设计的《智慧水利平台架构与开发》课程教材，采用Markdown格式编写，使用MkDocs构建，便于内容的快速迭代和更新。

## 文件组织结构

```
智慧水利平台架构与开发/
├── README.md                        # 教材简介和目录
├── README-DEV.md                    # 开发指南（本文档）
├── docs/                           # MkDocs文档目录
│   ├── chapters/                   # 章节内容
│   │   ├── chapter01/              # 第一章
│   │   │   ├── chapter01.md        # 第一章概述
│   │   │   ├── section01-01.md     # 第一节
│   │   │   ├── section01-02.md     # 第二节
│   │   │   ├── section01-03.md     # 第三节
│   │   │   └── section01-04.md     # 第四节
│   │   ├── ...
│   ├── appendix/                   # 附录
│   │   ├── appendixA.md            # 附录A
│   │   ├── appendixB.md            # 附录B
│   │   └── appendixC.md            # 附录C
│   ├── assets/                     # 静态资源
│   │   ├── css/                    # 样式文件
│   │   └── images/                 # 图片资源
│   └── index.md                    # 首页
├── mkdocs.yml                      # MkDocs配置文件
└── site/                          # 生成的静态网站
```

## 内容创作指南

### 章节结构

每个章节均应包含：
- 章节概述：简要介绍本章内容和学习目标
- 本章内容：列出各节标题并链接到相应文件
- 学习目标：明确列出学习本章后应达到的目标
- 关键词：列出本章的核心概念和关键词汇

### 节结构

每节均应包含：
- 节标题和内容概述
- 小节和子小节内容
- 习题与思考：针对本节内容设计的练习题和思考题
- 参考文献：本节内容的相关参考资料

### Markdown规范

- 使用标准Markdown语法，保持风格一致
- 标题层级：章节使用一级标题(#)，节使用一级标题(#)，小节使用二级标题(##)，子小节使用三级标题(###)
- 代码块：使用三个反引号(```)包围，并指定语言类型
- 图片：统一放在docs/assets/images/目录下，按章节分类存放
- 表格：使用Markdown表格语法，保持表格整洁
- 链接：使用相对路径链接到其他文件

### 图片规范

- 图片文件名格式：chapter{XX}_{description}.{ext}，例如chapter01_system_architecture.png
- 分辨率：保证图片清晰度，建议宽度不超过800px
- 格式：优先使用PNG格式，图片压缩后再添加

### 代码示例规范

- 代码文件名格式：chapter{XX}_{description}.{ext}，例如chapter04_vue_demo.js
- 代码应有详细注释，解释关键步骤和逻辑
- 示例代码应简洁明了，突出核心概念

## 开发环境配置

### 1. 安装必要的开发工具

- [Node.js](https://nodejs.org/) (LTS版本)
- [Git](https://git-scm.com/)
- [Visual Studio Code](https://code.visualstudio.com/) 或其他代码编辑器
- [Python](https://www.python.org/) (3.8或更高版本)
- [MkDocs](https://www.mkdocs.org/) 文档生成工具

### 2. 安装MkDocs及相关插件

```bash
# 创建并激活虚拟环境
conda create -n book python=3.9
conda activate book

# 安装MkDocs和Material主题
pip install mkdocs
pip install mkdocs-material

# 安装其他必要插件
pip install mkdocs-git-revision-date-localized-plugin
pip install mkdocs-git-revision-date-plugin
pip install mkdocs-minify-plugin
pip install mkdocs-redirects
```

### 3. 开发流程

1. **内容编写**
   - 在`docs/chapters`目录下创建或编辑章节内容
   - 使用Markdown格式编写文档
   - 图片资源放在`docs/assets/images`目录下

2. **本地预览**
   ```bash
   # 启动本地服务器
   mkdocs serve
   ```
   访问 http://127.0.0.1:8000 预览文档

3. **构建静态网站**
   ```bash
   # 生成静态网站
   mkdocs build
   ```
   生成的网站文件位于`site`目录

### 4. 文档规范

#### 4.1 文件命名规范
- 章节文件：`chapterXX.md`（XX为章节号）
- 小节文件：`sectionXX-YY.md`（XX为章节号，YY为小节号）
- 图片文件：使用有意义的英文名称，如`water_level_monitoring.png`

#### 4.2 Markdown编写规范
- 使用标准的Markdown语法
- 标题层级：从`#`开始，最多使用`#####`
- 代码块：使用三个反引号包裹，并指定语言
- 图片：使用相对路径，如`![图片说明](../assets/images/example.png)`
- 链接：使用相对路径，如`[链接文本](../chapter01/section01-01.md)`

#### 4.3 内容组织规范
- 每个章节必须有明确的学习目标
- 使用列表和表格组织内容
- 代码示例要简洁明了，并附有注释
- 重要概念要使用加粗或斜体强调

### 5. 主题定制

#### 5.1 自定义样式
编辑`docs/assets/css/extra.css`文件，可以自定义以下样式：
- 标题样式
- 正文样式
- 代码块样式
- 表格样式
- 提示框样式
- 导航样式

#### 5.2 主题配置
在`mkdocs.yml`中配置主题相关选项：
```yaml
theme:
  name: material
  language: zh
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.tabs
    - navigation.indexes
    - toc.follow
    - content.code.copy
```

### 6. 插件使用

#### 6.1 已安装插件
- git-revision-date-localized：显示文档最后更新时间
- minify：压缩HTML、CSS和JavaScript
- redirects：处理页面重定向

#### 6.2 插件配置
在`mkdocs.yml`中配置插件：
```yaml
plugins:
  - search
  - git-revision-date-localized:
      enable_creation_date: true
      fallback_to_build_date: true
      enable_git_follow: false
  - minify:
      minify_html: true
      minify_js: true
      minify_css: true
```

### 7. 常见问题解决

#### 7.1 图片路径问题
- 确保图片文件放在`docs/assets/images`目录下
- 使用相对路径引用图片，如`../assets/images/example.png`
- 检查图片文件名大小写

#### 7.2 导航配置问题
- 确保`mkdocs.yml`中的导航配置与文件结构一致
- 检查文件路径是否正确
- 确保所有引用的文件都存在

#### 7.3 构建错误
- 检查Markdown语法是否正确
- 确保所有引用的资源都存在
- 检查配置文件格式是否正确

### 8. 部署说明

#### 8.1 本地部署
1. 构建静态网站：
   ```bash
   mkdocs build
   ```
2. 将`site`目录下的文件复制到Web服务器

#### 8.2 GitHub Pages部署
1. 创建GitHub仓库
2. 配置GitHub Actions工作流
3. 推送代码到仓库
4. 在仓库设置中启用GitHub Pages

### 9. 维护与更新

#### 9.1 内容更新
- 定期检查并更新过时内容
- 添加新的案例和实践经验
- 根据用户反馈优化内容

#### 9.2 技术更新
- 定期更新依赖包版本
- 测试新版本MkDocs的兼容性
- 评估并集成新的插件

#### 9.3 版本控制
- 使用Git进行版本控制
- 遵循语义化版本规范
- 保持提交信息的清晰和规范

### 10. 贡献指南

欢迎贡献内容或提出改进建议：

1. Fork本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

### 11. 许可证

本项目采用MIT许可证，详见LICENSE文件。 