# 单元自包含：定义解析器 + 转换内联大纲 + 导出Excel（v2：严格空白对齐/属性块/关系覆盖）
import re, pandas as pd

COLUMNS = [
    "一级知识点","二级知识点","三级知识点","四级知识点","五级知识点","六级知识点","七级知识点",
    "前置知识点","后置知识点","关联知识点","标签","认知维度","分类","教学目标","知识点说明"
]

HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)$')
BULLET_RE  = re.compile(r'^(?P<indent>\s*)([-*+])\s+(?P<text>.+)$')
ATTR_CURLY = re.compile(r"\{([^}]*)\}\s*$")
ATTR_BRACK = re.compile(r"\[([^\]]*)\]\s*$")
KV_SPLIT_RE = re.compile(r"[;；]\s*")
KV_PAIR_RE  = re.compile(r"\s*([\u4e00-\u9fa5A-Za-z_]+)\s*[:=]\s*(.+?)\s*$")

ATTR_MAP = {
    "标签": "标签", "tag": "标签", "tags": "标签",
    "认知": "认知维度", "认知维度": "认知维度", "cognitive": "认知维度",
    "分类": "分类", "category": "分类",
    "目标": "教学目标", "教学目标": "教学目标", "objective": "教学目标",
    "说明": "知识点说明", "描述": "知识点说明", "desc": "知识点说明", "description": "知识点说明",
    "前置": "前置知识点", "前置知识点": "前置知识点", "prereq": "前置知识点",
    "后置": "后置知识点", "后置知识点": "后置知识点", "postreq": "后置知识点",
    "关联": "关联知识点", "关联知识点": "关联知识点", "related": "关联知识点",
}

def strip_code_ticks(text: str) -> str:
    return re.sub(r"`([^`]*)`", r"\1", text)

def normalize(text: str, strip_ticks: bool=True) -> str:
    t = text.strip()
    if strip_ticks: t = strip_code_ticks(t)
    return re.sub(r"\s+", " ", t)

def parse_attr_block(text: str):
    attrs = {}
    m = ATTR_CURLY.search(text) or ATTR_BRACK.search(text)
    if not m: return text, attrs
    whole = m.group(0); payload = m.group(1).strip()
    core = text[: text.rfind(whole)].rstrip()
    if payload:
        for token in KV_SPLIT_RE.split(payload):
            if not token.strip(): continue
            m2 = KV_PAIR_RE.match(token)
            if not m2: continue
            k_raw, v = m2.group(1).strip(), m2.group(2).strip()
            key = ATTR_MAP.get(k_raw.lower(), ATTR_MAP.get(k_raw, k_raw))
            attrs[key] = v
    return core, attrs

def bullet_depth(indent_spaces: int) -> int:
    return min(7, 3 + indent_spaces // 2)

def convert(md_text: str, props_start_level: int=3):
    rows = []
    rel_index = {}  # frozenset({A,B}) -> (row_idx, rel_col, tgt)
    def add_row(depth, text, attrs):
        row = {col: "" for col in COLUMNS}
        row[COLUMNS[depth-1]] = text  # 只写一个级别列，其余留空
        
        if depth >= props_start_level and attrs:
            for k, v in attrs.items():
                if k in COLUMNS: row[k] = v
        
        def _targets(s):
            return [t.strip() for t in s.split(";") if t.strip()]
        def _remove_target(cell, tgt):
            items = [x.strip() for x in cell.split(";") if x.strip()]
            items = [x for x in items if x != tgt]
            return ";".join(items)
        
        for rel_col in ("前置知识点","后置知识点","关联知识点"):
            if not row.get(rel_col): continue
            me = text
            for tgt in _targets(row[rel_col]):
                key = frozenset([me, tgt])
                if key in rel_index:
                    old_idx, old_col, old_tgt = rel_index[key]
                    prev = rows[old_idx]
                    prev[old_col] = _remove_target(prev.get(old_col, ""), old_tgt)
                rel_index[key] = (len(rows), rel_col, tgt)
        
        rows.append(row)
    
    for raw in md_text.splitlines():
        line = raw.rstrip()
        if not line.strip(): continue
        m = HEADING_RE.match(line)
        if m:
            depth = min(len(m.group(1)), 7)
            core, attrs = parse_attr_block(m.group(2))
            add_row(depth, normalize(core), attrs)
            continue
        m = BULLET_RE.match(line)
        if m:
            depth = bullet_depth(len(m.group("indent")))
            core, attrs = parse_attr_block(m.group("text"))
            add_row(depth, normalize(core), attrs)
            continue
        if rows:
            last = rows[-1]
            last_depth = next((i+1 for i,c in enumerate(COLUMNS[:7]) if last[c]), 1)
            if last_depth >= 3:
                last["知识点说明"] = (last.get("知识点说明","") + ("; " if last.get("知识点说明") else "") + normalize(line)).strip()
    return rows

MD_TEXT = r'''
# 第5章 前端开发技术（超细化）
## 5.1 HTML — 结构与语义
- 文档骨架
  - `<!DOCTYPE html>`、`<html lang>`、`<head>`、`<body>`
  - 元数据：`<meta charset>`、`viewport`、`X-UA-Compatible`（历史）、`<base>`
  - 资源引入：`<link rel="stylesheet">`、`<script defer/async>`、`<noscript>`
- 语义化布局
  - 语义标签：`header`、`nav`、`main`、`article`、`section`、`aside`、`footer`
  - 文本与分组：`h1~h6`、`p`、`span`、`div`、`hr`、`blockquote`、`pre`、`code`
  - 列表：`ul/ol/li`、`dl/dt/dd`、嵌套列表与有序编号控制
- 超链接与导航
  - `<a href target rel="noopener noreferrer" download>`、锚点与片段标识符 `#id`
  - 面包屑、跳转链接、外链安全（`rel`）
- 多媒体与图形
  - 图片：`<img alt>`、响应式图片 `srcset`/`sizes`、`<picture>`与`<source>`
  - 音视频：`<audio>`/`<video>`、`controls`、`autoplay`、`muted`、`preload`、`<track>`字幕
  - 图形：`<svg>`（矢量）与 `<canvas>`（位图）
- 表格
  - 结构：`table`、`caption`、`thead/tbody/tfoot`、`tr/th/td`
  - 单元格：`rowspan/colspan`、`scope`、表头关联与无障碍
- 表单
  - 容器与提交：`<form method action enctype>`、GET vs POST、`FormData`
  - 输入组件：`input`（`text/email/number/date/file/color/range`…）、`select`、`datalist`、`textarea`、`button`
  - 组合与标注：`label for`、`fieldset/legend`
  - 校验：`required`、`min/max/step`、`pattern`、`novalidate`、原生校验消息与自定义校验
  - 上传：多文件、拖放、分片/断点（前后端配合）
- SEO 与可发现性
  - `<title>`、`<meta name="description">`、canonical、`robots/noindex`、`hreflang`
  - Open Graph / Twitter Card、站点地图（sitemap）
- 可访问性（A11y）与国际化
  - 必要的 `alt`、表单 `label`、可聚焦 `tabindex`、可见焦点样式
  - ARIA：`role`、`aria-label/expanded/controls` 等
  - 国际化：`lang`、`dir=rtl`、字符编码、日期/数字本地化
- 性能与加载策略
  - `defer` vs `async`、`preload`/`prefetch`/`dns-prefetch`
  - 关键渲染路径、首屏与懒加载
## 5.2 CSS — 选择器、盒模型与布局
- 层叠与特指度（Specificity）
  - 继承/层叠顺序、`!important`、计算方式（ID > 类 > 元素）
- 选择器体系
  - 基础：元素、类、ID、通配
  - 组合：后代、子代、相邻兄弟、普遍兄弟
  - 属性选择器：`[type="text"]`、`^=`、`$=`、`*=`
  - 伪类：`hover/focus/active`、`:nth-child/an-of/only-child`、`:not()`
  - 伪元素：`::before/::after/::first-line`
- 盒模型与显示
  - 标准盒/怪异盒：`box-sizing`、`content/padding/border/margin`
  - `display`：block/inline/inline-block/none/contents
  - `overflow`、`visibility`、`opacity`、`z-index`/层叠上下文
- 颜色、单位与排版
  - 颜色：`hex`/`rgb(a)`/`hsl(a)`、色域与对比度
  - 单位：`px/em/rem/vw/vh/%`、`calc()`、`clamp()`
  - 字体：`font-family`、`@font-face`、`font-display`、字重/行高/字距/连字
- 布局演进与要点
  - 浮动布局：`float/clear`、BFC、圣杯/双飞翼（历史）
  - 定位：`relative/absolute/fixed/sticky`、定位上下文、堆叠上下文
  - Flexbox：
    - 容器：`display:flex`、`flex-direction`、`flex-wrap`、`justify-content`、`align-items`、`align-content`
    - 子项：`flex` 简写、`align-self`、`order`
    - 模式：水平/垂直居中、等高列、两端对齐
  - Grid：
    - 轨道与区域：`grid-template-rows/columns`、`grid-template-areas`
    - 自适应：`fr` 单位、`auto-fit/auto-fill`、`minmax()`
    - 典型布局：两/三列、卡片网格、瀑布流（变体）
- 响应式与适配
  - 媒体查询：`@media (min-width)`、移动优先、断点策略
  - 容器查询、流式排版、响应式图片配合
- 视觉与动效
  - 背景与边框：多重背景、`border-radius`、`box-shadow`、`filter`、`mix-blend-mode`
  - 变换与过渡：`transform/transition`
  - 关键帧动画：`@keyframes`、`animation`、性能注意（合成层）
- CSS 架构与维护
  - BEM/OOCSS/SMACSS、原子化/实用类、命名规范
  - 现代 CSS：自定义属性（`--var`）、`@layer`（级联层）
  - 打印样式与偏好媒体：`@media print`、`prefers-reduced-motion`、`prefers-color-scheme`
- 性能优化：关键 CSS、减少重排/重绘、选择器性能、压缩与树摇
## 5.3 JavaScript — 语言、DOM 与异步
- 语言核心
  - 变量：`let/const/var`、暂时性死区、解构与展开
  - 类型：原始类型与对象
  - 函数与 this：闭包、call/apply/bind、箭头函数
  - 作用域与提升、严格模式
  - 原型与 class、私有字段 `#prop`
  - 模块：ESM import/export、动态导入
  - 标准库：数组迭代、Map/Set、Date/Intl
- DOM 与事件：选择/遍历/修改；捕获/冒泡；事件委托；自定义事件
- BOM 与存储：history、localStorage/sessionStorage、IndexedDB
- 异步与网络：事件循环、Promise/async、fetch/XHR、CORS、WebSocket/SSE
- 安全/调试/性能：XSS/CSP、断点与SourceMap、节流/防抖、rAF、Worker
- PWA：Service Worker、manifest、离线与推送
- 测试与质量：Jest/Vitest、Playwright/Cypress、eslint/prettier
- TypeScript（可选）：接口/泛型、tsconfig、JS互操作
## 5.4 工程化与 Vue 框架
- 依赖与脚手架：npm/yarn/pnpm、Vite/Webpack、Babel/ESBuild、PostCSS、多环境
- 质量保障：ESLint/Prettier/Stylelint、Commitlint、Husky
- Vue 核心：组合式API、props/emits、插槽、provide/inject、生命周期、指令
- 表单校验：vee-validate/yup；路由：Vue Router；状态：Pinia/Vuex
- 数据：组合式 useXxx、错误/加载态；动画：transition/transition-group
- SSR/SSG/Nuxt（可选）；性能：代码分割、懒加载、keep-alive、虚拟滚动；测试：@vue/test-utils
- 安全/A11y：CSP、SameSite、权限路由、ARIA；国际化：vue-i18n
## 5.5 常见问题与案例
- 表单防抖/节流、复杂校验、分片上传；懒加载与响应式；CORS 预检/代理；SPA SEO

# 第6章 后端开发技术（超细化）
## 6.1 HTTP 与 API 基础
- 请求/响应、幂等/安全；方法与状态码（200/201/204/301/304/400/401/403/404/409/429/500/503）
- 缓存：Cache-Control/ETag/Last-Modified/Vary；身份：Authorization/Cookie（Secure/HttpOnly/SameSite）
- 跨域：Origin/Access-Control-*/预检；内容协商：Accept/Lang/Encoding；HTTPS/TLS/HSTS
- API 风格：REST/GraphQL/gRPC；版本；OpenAPI/Swagger
## 6.2 典型后端架构
- 分层单体；微服务（注册/发现、配置、网关、限流/熔断/降级、链路追踪）；事件驱动（消息队列、最终一致性）
## 6.3 Spring Boot 生态
- 自动配置/Starter；配置/Profiles；Controller/参数/JSR-303；Filter/Interceptor；异常处理（RFC7807）
- JPA/MyBatis；事务；MySQL/PG/Redis/Mongo；HikariCP
- 异步/@Async；调度/@Scheduled；缓存穿透/击穿/雪崩治理
- 安全：Spring Security（认证/授权）；CSRF；密码存储（BCrypt/Argon2）
- 可观察性：Micrometer+Prometheus；ELK/EFK；OpenTelemetry/Zipkin/Jaeger
- 文档/测试：SpringDoc、MockMvc、Testcontainers
- 打包/部署：可执行JAR、容器化、多阶段、健康/就绪探针
## 6.4 Python 后端（Flask/Django）
- Flask：路由/视图、蓝图、请求/响应、模板；中间件、验证、会话、扩展（Login/SQLAlchemy）
- Django：MTV、ORM/QuerySet、迁移、Admin；表单/验证、中间件、静态资源
- 迁移：Alembic/Django；安全：CSRF/XSS/开放重定向
## 6.5 API 设计实践
- 资源建模、URI、幂等键；错误模型 problem+json；查询/分页；大文件上传/下载/Range
## 6.6 运维与可观察性
- 日志结构化与追踪；RED/USE 指标；健康检查；限流/熔断/重试
## 6.7 安全与合规
- 输入/输出校验、防注入；Session/JWT/OAuth2/OIDC；RBAC/ABAC；密钥管理；SCA/CVE/SBOM
## 6.8 部署与发布
- CI/CD；Dockerfile 多阶段；K8s（Deployment/Service/Ingress/ConfigMap/Secret）；蓝绿/金丝雀/灰度
## 6.9 性能与扩展
- 索引/连接池/慢查/读写分离；线程池/超时/背压；缓存策略；L4/L7 负载；会话保持
## 6.10 综合案例
- 商品检索/详情/库存；REST 资源；JWT+RBAC；日志/指标/健康；容器化+金丝雀
'''

rows = convert(MD_TEXT, props_start_level=3)
df = pd.DataFrame(rows, columns=COLUMNS)

out_path = "第5-6章_超细化_知识点大纲_v2.xlsx"
with pd.ExcelWriter(out_path, engine="xlsxwriter") as writer:
    first_col = df["一级知识点"].fillna("")
    mask5 = first_col.str.contains("第5章", na=False)
    mask6 = first_col.str.contains("第6章", na=False)
    df5 = df[mask5].reset_index(drop=True)
    df6 = df[mask6].reset_index(drop=True)
    df5.to_excel(writer, sheet_name="第5章", index=False)
    df6.to_excel(writer, sheet_name="第6章", index=False)

out_path
