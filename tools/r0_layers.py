# -*- coding: utf-8 -*-
"""R0：按标题规则给 sections.csv / listings.csv 打层次草标（核心 C / 指导实践 G / 拓展 E）。
规则是草案，R1/R2 逐节人工复核后固化到正文 \\paragraph{本节层次}。"""
import csv, re, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R0 = os.path.join(ROOT, "tools", "r0")
E = ["国内外建设路径", "政策体系的阅读方法", "智能能力的技术选型", "退役与数据处置", "螺旋模型", "Scrum", "DevOps", "其他模型",
     "需求变更控制流程", "微服务", "事件驱动", "Web 形态", "复杂度与风险分析", "ATAM", "评估方法",
     "层叠上下文", "CSS 变量与暗色主题", "闭包", "事件循环", "Vite工程化与性能优化", "认证契约测试与故障复盘",
     "Bean 作用域", "N+1", "查询测试、执行计划", "数值稳定性", "七种传播", "隔离级别", "统计量更新",
     "HTTP 状态转换", "测试矩阵", "密钥生命周期", "CSRF", "撤销、重放", "可观测性与演练", "令牌失效", "分区、顺序",
     "性能优化与可观测性", "缓存与 Redis", "游标", "连接池", "Actuator", "性能故障", "质量门禁",
     "WebGL2渲染管线", "Cesium", "倾斜摄影数据生产", "BIM语义", "多源模型融合", "数字孪生水利平台架构概览",
     "概念边界与五维", "分层技术架构", "跨层契约", "业务场景与需求分解", "数据底板", "模型卡与可信度", "事件时间、状态估计",
     "三维交互与决策证据链", "实时同步与闭环控制", "接口与事件契约", "大坝安全监测场景", "流域预报调度场景", "云边协同",
     "安全、权限与失效降级", "可观测性、数据血缘", "验证、验收与持续改进", "发展重点",
     "多源异构数据", "专题地图", "色彩体系", "LOD与聚合", "触控半径", "渲染器、性能预算",
     "从业务约束到物理设计的推导", "存储、缓存与一致性", "模型可信度与人在回路", "数字孪生水利平台案例", "案例来源、边界",
     "防台防洪", "淹没影响", "四预", "闸门调度", "预警方案预演", "AI助手", "底板与算法解耦", "对象编码、时空基线",
     "模型任务编排", "供需平衡", "场景版本", "端到端实现切片", "会商时间线", "失效降级、验收与课程实现",
     "技术发展趋势", "政策与建设背景", "延伸方向", "新技术是否值得投入", "面向前沿技术", "行业追踪", "跨学科",
     "Three.js主线与Cesium扩展", "感知、通信与数据交换", "发展脉络"]
G = ["Grid", "Flexbox", "响应式断点", "Flex布局的故障定位", "事件委托", "AbortController", "request.js", "Vite 代理",
     "登录到受保护接口", "生命周期与资源清理", "测站列表筛选页", "根组件、路由表", "StationDetail", "AssetDetail", "路由参数", "Pinia",
     "application.yml", "自动配置诊断", "工程骨架的测试切片", "关联关系与懒加载", "派生查询", "乐观锁", "索引设计",
     "只读事务与事件发布", "统一错误响应", "三层校验", "DTO 契约", "Spring Security 6与JWT", "威胁模型", "密码、账户",
     "权限建模", "事务事件与消息队列", "生产者", "消费者幂等", "重试、退避", "事务发件箱",
     "Three.js场景组织", "OGC地图", "CGCS2000", "高程基准", "课程项目实施路线",
     "实时流、历史回放", "数据质量检验", "可运行的实时曲线", "图表与三维对象的双向联动", "坐标转换与局部原点", "射线拾取",
     "案例联调与验收", "场景组织、材质与交互", "关系模型、空间索引", "数据库迁移、查询与运行维护练习", "Vue前端页面组织",
     "Spring Boot后端与数据质量", "监测主线后端实现", "从预警到工单", "部署架构", "可观测性、备份", "阶段验收",
     "架构决策记录", "案例分析：", "构件级设计", "构件协作与接口设计", "把设计交给评审", "课堂演练",
     "需求获取方法的组合", "结构化分析的交叉校验", "需求评审检查单", "模型选择", "决策表", "状态转换图"]
# 人工复核后的逐节改判（R2，2026-09-09）：键为 (章, 标题片段)
OVERRIDES = {
    ("ch03", "原型定义与细化"): "G", ("ch03", "构件级设计"): "G", ("ch03", "软件架构的定义与重要性"): "G",
    ("ch04", "函数、闭包与数组高阶方法"): "C", ("ch04", "模块化开发与调试技巧"): "G", ("ch04", "阶段验收"): "C", ("ch04", "收束练习"): "C", ("ch04", "Vite 工程化与性能优化"): "E",
    ("ch05", "测试策略与质量门禁"): "G", ("ch05", "为什么引入消息队列"): "C", ("ch05", "返回固定数据的接口"): "C", ("ch05", "路径参数、查询参数与错误体"): "C", ("ch05", "用第4章的页面和故障表验证接口"): "C", ("ch05", "第一个 HTTP 接口"): "C",
    ("ch06", "Three.js场景组织与模型加载"): "C", ("ch06", "CGCS2000与投影坐标"): "C", ("ch06", "高程基准与空间一致性"): "C",
    ("ch07", "图表与三维对象的双向联动"): "C", ("ch07", "射线拾取与安全的向量运算"): "C",
    ("ch08", "从预警到工单与复盘"): "G",
    ("ch03", "构件协作与接口设计"): "C", ("ch03", "单体、模块化单体与微服务"): "C", ("ch03", "课堂演练"): "G",
}
def layer(title, chapter):
    for (c, k), v in OVERRIDES.items():
        if c == chapter and k in title: return v
    for k in E:
        if k in title: return "E"
    for k in G:
        if k in title: return "G"
    return "C"
rows = list(csv.DictReader(open(os.path.join(R0, "sections.csv"), encoding="utf-8-sig")))
# 章末要件不分层
sec_layer = {}
for r in rows:
    if r["title"] in ("小结", "章末交付物", "思考题与练习题", "核心术语表") or r["title"].startswith("章末交付物"):
        r["layer"] = "-"
    else:
        r["layer"] = layer(r["title"], r["chapter"])
    if r["level"] == "section":
        sec_layer[(r["chapter"], r["title"])] = r["layer"]
    elif r["level"] == "subsection":
        # 上级 section 为拓展则整体拓展
        if sec_layer.get((r["chapter"], r["section"])) == "E": r["layer"] = "E"
        sec_layer[(r["chapter"], r["title"])] = r["layer"]
    else:
        parent = sec_layer.get((r["chapter"], r["section"]))
        if parent == "E": r["layer"] = "E"
with open(os.path.join(R0, "sections.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
# 汇总（只按 subsection + 无子节的 section 的 chars_own 累计，避免重复）
tot = collections.defaultdict(lambda: collections.Counter())
for r in rows:
    if r["level"] == "subsubsection": continue
    tot[r["chapter"]][r["layer"]] += int(r["chars_own"])
    if r["level"] == "subsection": pass
# subsubsection 的字数归入其 subsection 的层次
for r in rows:
    if r["level"] == "subsubsection":
        tot[r["chapter"]][r["layer"]] += int(r["chars_own"])
print("%-8s %7s %7s %7s %7s %7s" % ("章", "核心", "指导", "拓展", "要件", "合计"))
grand = collections.Counter()
for ch in ["preface"] + ["ch%02d" % i for i in range(1, 10)]:
    c = tot[ch]; s = sum(c.values()); grand.update(c)
    print("%-8s %7d %7d %7d %7d %7d" % (ch, c["C"], c["G"], c["E"], c["-"], s))
print("%-8s %7d %7d %7d %7d %7d" % ("合计", grand["C"], grand["G"], grand["E"], grand["-"], sum(grand.values())))
# listings
lst = list(csv.DictReader(open(os.path.join(R0, "listings.csv"), encoding="utf-8-sig")))
for l in lst:
    key = (l["chapter"], l["subsection"] or l["section"])
    l["layer"] = sec_layer.get(key, "C")
    lang = l["language"].lower()
    if lang in ("yaml", "xml", "bash", "nginx", "json", "http"): l["category"] = "工程支撑"
    elif re.search(r"测站|测点|asset|reading|观测|预警|工单|登录|JWT|station|告警|水位|渗压|案例", l["caption"], re.I): l["category"] = "连续案例"
    else: l["category"] = "原理实验"
with open(os.path.join(R0, "listings.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(lst[0].keys())); w.writeheader(); w.writerows(lst)
print(collections.Counter(l["layer"] for l in lst), collections.Counter(l["category"] for l in lst))
