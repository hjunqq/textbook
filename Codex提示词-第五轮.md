# Codex 提示词集 · 第五轮扩写与修订

> 共 60 个工作包：O 批 8 + A 批 43 + S 批 3 + B 批 6。执行顺序与每步的抽查要点见
> 《执行手册-第五轮.md》，那里有编号到 60 的完整清单和步骤 0 的 git 命令。

## 怎么用

1. **一次一个包，每包开一个新会话。** 34 个扩写包打包丢过去，它会为了"整体一致"采用统一压缩策略——那正是上一轮的失败路径。
2. 复制整段提示词贴进去，不要删减其中的硬指标。
3. 每包做完人工抽查两样：挑一段新代码贴进 IDE 看能不能跑；挑一节新文字读一遍，看有没有"XX 具有重要意义""为 YY 提供了有力支撑"这类空转句。门禁挡得住删除和粗暴注水，挡不住写得平庸。
4. **门禁阈值不许放宽。** 过不了检就补内容，不是改 `tools/check_textbook.py`。
5. 执行顺序：O1→O8 → A 系列（ch04→ch05→ch06→ch07→ch08→ch02→ch01→ch03→ch09→preface）→ S3 → S2 → B1→B6 → S1。

**开工前必须先做这一步**：第三轮（2026-08-05）的全部改动至今没有提交，11 个 tex 还是
工作区里的 M 状态，最后一次提交 d8beab0 保存的正是被删之前的版本。先存档：

```bash
cd E:\2026\教材\智慧水利平台架构与开发
git add -A && git commit -m "第三轮修改成果存档（2026-08-05，未经审查的状态）"
```

提交后 d8beab0（删除前，124,332 字）与新提交（删除后，75,859 字）两版都在历史里，
可随时 diff 与取用。**不做这一步，任何一次 git checkout . 都会把第三轮的成果抹掉。**

每条提示词都假定 Codex 会先读 `AGENTS.md`（八条铁律）和《扩写与修订方案-第五轮-2026-08-06.md》，所以不重复抄铁律。**请确保这两个文件在仓库根目录**（已落盘）。

---

## 通用收尾段（每条提示词末尾都有，这里说明一次）

```
【自检】运行 python tools/check_textbook.py --build ，必须全绿。
不许通过删内容过检，不许修改 tools/check_textbook.py 的阈值。

【收尾】追加写入《修改记录-第五轮.md》：工作包编号 / 各文件正文字数 before→after /
新增的小节、代码清单、图、表清单 / 修正的问题条目 / 删除的内容（如有，逐条列出原文与替代）/
门禁输出摘要。然后 git commit，提交信息首行为 "【包号】 标题（+N 字）"。

做完这一个工作包就停下来汇报，不要自动继续下一个。
```

---

# 批次 O · 阻断项（先做完这八个）

## O1

```
仓库：E:\2026\教材\智慧水利平台架构与开发

【开工前】完整读 AGENTS.md 的八条铁律，特别是第 1 条（只增不删）和第 2 条
（代码清单不设行数上限，上一轮"40行内"的指令已撤销）。再读
《扩写与修订方案-第五轮-2026-08-06.md》第四节的 O1 条目，以及
《审查报告-第四轮-2026-08-06.md》的 R4-001。

【工作包】O1 · 第6章五维模型学术归属修正

【问题】output/chapters/chapter06.tex 第 246 行写着"为便于水利平台设计，本教材把连接
机制单独列为第五维，形成 DT=(PE,VE,Ss,DD,CN)……该五维写法是对原始构成的工程化展开"。
但 (PE,VE,Ss,DD,CN) 正是陶飞等人 2019 年在《计算机集成制造系统》25(1):1-18 发表的
《数字孪生五维模型及十大领域应用》中提出的原创五维模型，不是本教材的扩展。
references.bib 里只有 tao2017dts（IEEE Access 的车间四要素文章），缺 2019 年这篇。
这是把他人成果记为自己的贡献，属于出版环节最敏感的一类问题。

【任务】
1. references.bib 新增 tao2019fivedim 条目（陶飞, 刘蔚然, 张萌, 等）。
2. 正文改写为：陶飞、张萌提出的数字孪生车间模型包含物理车间、虚拟车间、服务系统和
   孪生数据\cite{tao2017dts}；在此基础上，陶飞等进一步提出数字孪生五维模型
   \cite{tao2019fivedim}，M_DT=(PE,VE,Ss,DD,CN)……本章沿用该五维划分，并结合水利
   业务对各维度作工程化细化。
3. 数学符号由 DT 改为 M_{DT}，与原文一致。
4. 顺带核对紧邻的 glaessgen2012（NASA 文献）转述是否忠于原文——第四轮复核认为它是对的，
   不要改坏。

【硬指标】
- 正文不得再出现"本教材把……列为第五维"或"该五维写法是对原始构成的工程化展开"。
- tao2019fivedim 必须被 \cite 引用（门禁会检查 bib 无未引用条目）。
- chapter06.tex 正文汉字数不得低于基线（改写而非删除）。

【自检】python tools/check_textbook.py --build 全绿，不许删内容过检，不许改门禁阈值。
【收尾】追加《修改记录-第五轮.md》并 git commit，首行 "O1 第6章五维模型学术归属修正"。
做完停下汇报。
```

## O2

```
仓库：E:\2026\教材\智慧水利平台架构与开发

【开工前】读 AGENTS.md；读方案第四节 O2；读审查报告 R4-002。

【工作包】O2 · 第6章 IFC 4.3 段落重写

【问题】chapter06.tex 第 220 行三重缺陷：
(a) 前半句说 Ports and Waterways Domain"覆盖水道、船闸、闸门、溢洪道等设施语义"，
    后半句又说"buildingSMART 当前文档仍把坝、堤、堰列为该域范围之外"——溢洪道是大坝
    泄水建筑物，两句直接打架；
(b) 全段只说"不能用 IfcDoor 表示闸门""不能用 IfcFurniture 表示廊道"，却没有给出
    任何一个正确的 IFC 实体名；
(c) 第 763 行习题要求"结合 IFC 4.3 官方范围，说明闸门、坝体和廊道应如何避免错误实体
    映射"，按现有正文根本无法作答。

【任务】
1. 改写该段：Ports and Waterways Domain 的范围侧重航道、运河、船闸与升船机、港口码头等
   通航与港工设施。给出可用实体：IfcMarineFacility（配合 PredefinedType）、IfcMarinePart、
   IFC 4.3 通用基础设施实体 IfcFacility/IfcFacilityPart、IfcEarthworksElement/
   IfcEarthworksFill（土石方与填筑体）；机电与启闭设备映射到 IfcDistributionElement 分支。
2. 明确写出边界：IFC 4.3 没有专用的闸门与溢洪道实体，坝、堤、堰也在该域范围之外；这类
   对象应采用项目分类、IfcPropertySet 属性集和映射规则表达，并保留原始设计模型，
   不虚构不存在的 IFC 实体。
3. 新增一张"水工对象 → IFC 实体映射"三列表（对象 / 推荐实体与 PredefinedType / 说明与边界），
   覆盖坝体、闸门、廊道、溢洪道、船闸、护岸、监测仪器至少七项，并在正文用 \ref 引出。

【重要】具体实体名与 PredefinedType 枚举必须对照
ifc43-docs.standards.buildingsmart.org 上现行 IFC4X3_ADD2 文档逐一核对后填写。
凡是你无法在官方文档中确认的条目，在表格里写 "TODO-核对" 并在提交说明中列出，
不要凭记忆编造实体名。这一条比按时完成重要。

【硬指标】
- 新增映射表必须被 \ref 引用。
- 第 763 行习题按改后正文可以作答。
- chapter06.tex 正文汉字数净增 ≥ 500 字。

【自检】python tools/check_textbook.py --build 全绿。
【收尾】追加《修改记录-第五轮.md》并 git commit，首行 "O2 第6章IFC4.3段落重写"。
做完停下汇报。
```

## O3

```
仓库：E:\2026\教材\智慧水利平台架构与开发

【开工前】读 AGENTS.md（注意第 2 条：代码清单不设行数上限，要写完整可读的代码）；
读方案第四节 O3；读审查报告 R4-003。

【工作包】O3 · 第8章质量码与预警级代码缺陷修复

【问题】
(a) chapter08.tex 第 286-296 行：WarningLevel 枚举只有 BLUE/YELLOW/ORANGE/RED，
    没有"无预警"状态。于是 classify() 里 score=0.01 的完全正常测点返回 BLUE，
    quality != "valid" 的不可信数据也返回 BLUE。28 个测点会持续产生蓝色告警风暴；
    更危险的是 score=0.9 且 quality="suspect" 时系统吐出蓝色，掩盖真实风险。
    这与第7章第 44 行"设备故障数据不得参与风险判定"、本章第 326 行"数据质量不足时
    应降低可信等级或停算"正面冲突。第 259 行为了统一口径删掉 none 字符串时，
    把"正常"这个业务态一并删了。
(b) 第 224-245 行 inspect()：缺测（value==null）和单位错误两个分支只往 issues 里
    加字符串，不改写 quality；只有"范围越界"分支调了 withQuality("suspect")。
    结果缺测记录带着原始 valid 质量码流向下游被 classify() 当合格数据打分。
    第7章定义的 missing 质量码在整个第8章从未被写入过。

【任务】
1. 枚举补 NONE：public enum WarningLevel { NONE, BLUE, YELLOW, ORANGE, RED }。
2. classify() 对质量不合格返回"未评估"而非某个颜色——用独立结果类型（如
   sealed interface Classification 或一个带 evaluable 标志的 record）表达，
   不要用 Optional 硬塞。正文补一段说明："未评估"与"无预警"是两个不同的业务态，
   不能折叠进颜色维度。
3. inspect() 对缺测写 missing、对单位错误写 suspect 或直接拒收；补一段质量码优先级
   说明（missing > invalid > suspect），并处理多问题同时命中的情形。
4. 删掉冗余的 errorCount（它恒等于 issues.size()）；corrected 改名 qualityFlagAdjusted
   （现在第 247 行要用一整句解释"corrected 不表示篡改原始值"，命名靠散文来救就是命名错了）；
   range.isClearlyInvalid() 的结论改为 invalid（方法名断言"明显无效"却标"可疑"，语义不对齐）。
5. 新增一张"质量码 → 下游处理"对照表（质量码 / 含义 / 是否参与打分 / 界面表现 / 是否计入统计），
   在正文用 \ref 引出。
6. 第 222 行散文说校验 5 项（格式、单位、范围、时序、重复），代码实现 3 项，第 1110 行
   实践题要求 4 项——三处统一。建议把时序（occurredAt 不得晚于当前、不得早于上一条）
   与重复（eventId 去重）真正写进示例代码，第 104 行的失败流用例正好点名了这两项。

【硬指标】
- 代码必须可独立阅读：import、类型定义、依赖注入齐全，不设行数上限。
- 三值质量码 valid/suspect/missing 在第7、8章口径一致。
- chapter08.tex 正文汉字数净增 ≥ 600 字。

【自检】python tools/check_textbook.py --build 全绿。
【收尾】追加《修改记录-第五轮.md》并 git commit，首行 "O3 第8章质量码与预警级代码修复"。
做完停下汇报。
```

## O4

```
仓库：E:\2026\教材\智慧水利平台架构与开发

【开工前】读 AGENTS.md；读方案第四节 O4；读审查报告 R4-005、R4-006。

【工作包】O4 · 51WIM 致谢、商标与权威依据

【前提】北京五一视界的书面授权已于 2026-08-06 确认取得。本包按"补引权威文件 + 加致谢与
商标声明"路径执行。**默认不加产品界面截图**，8.5 节图示继续全部使用 TikZ 重绘的教学示意图。

【任务】
1. preface.tex 致谢段补一句："感谢北京五一视界数字孪生科技股份有限公司为本书 8.5 节
   提供《51WIM 数字孪生水利平台 V1.0（DEMO）使用说明手册》参考资料。"
2. 8.5 节首个脚注加商标声明："51WIM 及 51WORLD 为北京五一视界数字孪生科技股份有限公司的
   商标或注册商标，本书仅作技术说明性使用。"
3. references.bib 的 wuyi2026wim 条目：note 字段现在写的是"用户提供的项目资料"，
   这句话会原样印进参考文献表。改为"内部资料，未公开出版"，或整条移出
   \printbibliography 改为脚注致谢（按 GB/T 7714-2015，参考文献应可被读者获取，
   一份内部 DEMO 手册不满足）。
4. chapter08.tex 第 334 行"本教材不复刻产品界面，也不使用未获书面授权的截图"这句是
   写给法务看的，印给学生反而暗示存在"已授权截图"。移到版权页，正文改为中性表述：
   "本节图示均为按功能链路重新绘制的教学示意图，不复现产品界面。"
5. **这一条即使授权到手也必须做**：8.5 节 682 行的全部权威依据只有一份厂商手册，
   贯穿全节的"四预"概念一次都没引水利部文件。在 8.5.1 开篇引 smartWaterGuidance2021
   + twinProject2024 定义"四预"与建设要求；8.5.4 的对比表引 twinYellowRiver2024
   作为公开行业样本；新增一段"不同技术路线对比"（至少 400 字），使厂商方案退居
   "其中一种实现的参考"。这四个 bib 键都已存在，现在只有第9章用了。
   理由不是版权而是学术独立性：单一厂商依据 + 零横向对照，读起来接近产品白皮书的教学改写。

【硬指标】
- chapter08.tex 正文汉字数净增 ≥ 500 字。
- 新引的四个文献键被正确引用，门禁 bib 检查通过。

【自检】python tools/check_textbook.py --build 全绿。
【收尾】追加《修改记录-第五轮.md》，注明授权已落实并已归档；git commit，
首行 "O4 51WIM致谢商标与权威依据补充"。做完停下汇报。
```

## O5

```
仓库：E:\2026\教材\智慧水利平台架构与开发

【开工前】读 AGENTS.md 第 4 条（不许把改稿批注写进正文）；读方案第四节 O5；
读审查报告 R4-011 的完整表格。

【工作包】O5 · 清除全书改稿批注（21 处）

【问题】上一轮留下了 21 处写给上一稿作者或审稿人的纠错备忘，被当作正文印了出来。
读者从未见过被否定的说法，读到只会一头雾水。最刺眼的是 chapter08.tex 第 251 行
直接出现"原稿"二字。

【任务】先运行 python tools/check_textbook.py --report ，check_editorial 会精确
列出全部位置和行号。逐条改为面向学生的正面表述。

**关键：不是简单删掉。** 删掉会掉字数，门禁的防删除检查同样会拦。每一处都要改写成
有教学价值的正面内容，多数应该比原句更长。几个重点：

- ch01:44 "不能写成'洪灾风险从30年一遇降至100年一遇'"——这条有真实教学价值。
  改写成独立的 warningbox"常见概念误用：防洪标准 vs 洪灾风险"，并补上原因：
  重现期只刻画致灾因子，风险还取决于暴露度、脆弱性、调度能力与极端事件。
- ch01:50 "不用无出处的项目数量或成效百分比装饰结论"——编者自我辩解，整句删除，
  在别处补等量内容。
- ch01:73 整段 AI 模型选型内容（"模型许可、算力、更新机制、数据隔离和安全评测"）
  悬空在"感知、通信与数据交换"小节里，前后文都没有 AI 上下文。移到第9章 §9.2.1，
  或在第1章新增一个技术选型小节承接它。
- ch02:138/256/357/382 四处：分别改为正面表述（敏捷要求客户代表持续在场并具备决策权 /
  删去"而不是逆转告警处置顺序"这个本章从未出现的说法 / 数据字典的说明栏必须给出取值域、
  单位或校验规则 / 术语统一移到全书体例表）。
- ch04:111/249 两处自证式表述（"完整且不存在未闭合的媒体查询或选择器""没有省略语法结构"）
  ——删掉后半句，改为对代码的教学解读。
- ch05:90 保留"Spring Boot 3 使用 jakarta.servlet.*，Jakarta Servlet 6.x 是本章基线"，
  删掉"不再使用'Servlet 4.0是现代规范'的过时表述"。
- ch05:334 整段讲 @EnableEurekaClient 弃用，但 Spring Cloud、服务发现在本章从未引入。
  两个选择：等 A5-1 补上服务发现上下文后再保留，或本包整段移除并在同章别处补等量内容。
  本包选后者，并在提交说明中注明。
- ch06:190 "不再混用 PhotoScan、Smart 3D 等旧称"——改为正面说明软件名称沿革。
- ch07:125 "而不是'百度开源项目'的现行表述"——这段史实值得正面讲：ECharts 最初由
  百度开源，2018 年捐赠给 Apache 软件基金会，2021 年毕业为顶级项目，现由 ASF 社区维护。
- ch07:287 "不能调用未定义的全局变量"是为上一版 bug 辩解，删。
- ch08:128/251/259 三处"不再混用"，其中 251 含"原稿"二字，全部改为正面陈述
  （例："时序观测使用 PostgreSQL + TimescaleDB 扩展统一管理，业务、空间与时序数据
  共用一套事务与备份体系，避免多引擎带来的一致性与运维成本"）。
- ch09:32 "本节不再堆叠难以逐条核实的项目数字"——整句删除，直接从
  "从2023年2月印发的《数字中国建设整体布局规划》……"起笔，并在本节补等量内容。

【硬指标】
- check_editorial 零 FAIL。
- **每个文件的正文汉字数都不得低于基线**（这是本包最容易翻车的地方：改写时顺手删段落）。
- 全书正文汉字总数净增 ≥ 800 字。

【自检】python tools/check_textbook.py --build 全绿。
【收尾】追加《修改记录-第五轮.md》，逐条列出 21 处的原文与改后文字；git commit，
首行 "O5 清除全书改稿批注21处"。做完停下汇报。
```

## O6

```
仓库：E:\2026\教材\智慧水利平台架构与开发

【开工前】读 AGENTS.md 第 3 条（图表必须随文引出）；读方案第四节 O6；读审查报告 R4-007。

【工作包】O6 · 全书补 \ref 与浮动体控制

【问题】全书 110 个 \label，86 个从未被 \ref 引用。第7章 12 个、第8章 41 个全部零引用。
所有图表都是 [htbp] 浮动体而正文无锚点，排版后会漂到与讲解无关的页面，读者无法定位。
教材编校规范要求图、表、公式必须随文引出。第3章做到了（11 个 label 用了 10 次 ref），
说明体例本应如此。

【任务】
1. 运行 python tools/check_textbook.py --report ，check_refs 会列出全部 86 个未引用 label。
   逐个在正文最近的合适位置补引导语。
   **这不是纯机械操作，是补字数的机会**：每处引导语应带一句话说明该图表要讲什么，
   例如不要只写"如表6-1所示"，而写"各服务在数据粒度与缓存策略上的差异见表\ref{tab:ogc-services}，
   选型时应先确定是否需要按范围取原始像元值。"
2. main.tex 加 \usepackage[section]{placeins}；纯示意的 TikZ 图改用 [H]（float 宏包已加载）。
   理由：第8章在 682 行内有约 29 个浮动体，相邻之间常只有 1-2 段正文；LaTeX 默认
   topnumber=2/bottomnumber=1/totalnumber=3，浮动队列上限 18，本轮扩写后极易触发
   Too many unprocessed floats 致命错误。现在不加，后面必然踩。
3. chapter01.tex 第 105 行的 \label{fig:smart-water-evolution} 与图题"一次洪水预警
   从监测到复核的闭环"不符（evolution 是上一稿"发展历程图"的残留），改为
   fig:flood-warning-loop。
4. 顺带给全书 44 个代码清单补 caption 与 label（现在一个都没有），命名规则
   lst:章号-简短英文名，并在正文引用其中至少 20 个。

【硬指标】
- check_refs 零 FAIL。
- 各文件正文汉字数不低于基线；全书净增 ≥ 3,000 字（86 处引导语，平均 35 字以上）。

【自检】python tools/check_textbook.py --build 全绿。特别注意加 placeins 后可能出现新的
分页问题，Overfull 必须仍为 0。
【收尾】追加《修改记录-第五轮.md》并 git commit，首行 "O6 全书补ref与浮动体控制"。
做完停下汇报。
```

## O7

```
仓库：E:\2026\教材\智慧水利平台架构与开发

【开工前】读 AGENTS.md；读方案第四节 O7；读审查报告 R4-004。

【工作包】O7 · 前言承诺修正与配套资源节

【问题】前言对读者做了三处兑现不了的承诺，且全书没有配套资源说明。

【任务】
1. preface.tex 第 34 行"后端（第5章）：Spring Boot 和 Flask 框架"——第5章的 Flask
   只出现在 5.7 节扩展阅读的一句话里，且明说"主线工程仍为 Spring Boot"。改为：
   "后端（第5章）：Spring Boot 框架（Java 17 / Jakarta EE），RESTful API 设计、
   JPA 持久化、Spring Security 与消息队列；Python 生态（Flask/Django/FastAPI）
   作扩展阅读简介"。chapter09.tex 第 14 行"涵盖了 Java/Python 后端语言"同步改。
2. 第 51 行"每章末尾都有思考题和练习题"——第9章补齐章末要件的工作在 A9-1，
   本包**保留此句不动**（决策已定为补齐第9章，此句届时成立）。在提交说明中注明依赖 A9-1。
3. 第 70-71 行学时方案重排。现在写"32学时以第1-6章为主"，但第6章有 27 个小节含
   WebGL2、坐标系、IFC、数字孪生 17 节，讲不完。改为：
   - 32 学时 = 第1-5章 + 第6章仅讲 6.1、6.2 概念
   - 48 学时 = 第1-7章 + 第8章 8.1-8.4；8.5 节与第9章列为课程设计/自学
   每个方案后补一张章节学时分配表（如"第4章 8学时"），用 \ref 引出。
4. **新增"配套资源"一节**（这是本包的主要增量）。现在全书没有这一节，但第6章交付物
   要求"一段可运行的 Three.js 或 Cesium 加载代码"、第7章实践题写"使用提供的 1000 条
   水位数据"、第8章交付物预设读者能跑示例。内容包括：
   - 配套代码仓库地址与目录说明（对应 companion/water-platform-demo/，S2 建，此处先写结构）
   - 示例数据集说明（对应 companion/datasets/，S3 建）
   - 习题参考答案的获取方式（附录A，S1 建）
   - 环境版本清单：Node、JDK、Python、Vue、Vite、Spring Boot、Three.js、CesiumJS、
     PostgreSQL/PostGIS/TimescaleDB、Redis、Kafka 的具体版本号
   - 勘误反馈渠道
5. 第 22-41 行三部分介绍分别用了 importantbox(红)/tipbox(绿)/notebox(蓝)。
   importantbox 在 main.tex 里定义为 ImportantColor=D32F2F，是全书的警示色，
   读者会误读为"第一部分是警告"；notebox 还会自动带上"▷ 提示"标题，"第三部分 应用篇"
   顶着一个"提示"标签语义错位。三部分统一改用同一种中性表达（tipbox 或
   \subsection* + 正文）。
6. 致谢现在是"感谢各位同事和同学，感谢审稿专家"，无一具体对象也无基金/教改项目编号。
   补项目名称与编号（如暂无，标 TODO-补充）；51WIM 致谢由 O4 负责，本包不重复。

【硬指标】
- preface.tex 正文汉字数从 1,677 增至 ≥ 2,500。
- 新增的学时分配表被 \ref 引用。

【自检】python tools/check_textbook.py --build 全绿。
【收尾】追加《修改记录-第五轮.md》并 git commit，首行 "O7 前言承诺修正与配套资源节"。
做完停下汇报。
```

## O8

```
仓库：E:\2026\教材\智慧水利平台架构与开发

【开工前】读 AGENTS.md；读方案第四节 O8 的表格。

【工作包】O8 · 事实核验点标注（只标注，不改写）

【说明】以下 10 条政策与标准引用需要熟悉水利政策的编者回原文逐字核对，付印后无法挽回。
**你的任务只是把它们标注出来，不要自行判断、不要自行修改、不要联网查证后就当定论。**
凡是你觉得"应该是这样"的地方，一律标注而不是改写。

【任务】在对应位置插入 LaTeX 注释，格式统一为：
  % TODO-核对[编号]：<需核对的具体问题> —— 待编者确认后修改，勿自行改写

10 个核对点：
1. preface.tex L14 —《国家水网建设规划纲要》是否有"数字孪生水利体系"这一原词
   （通行表述为"推进数字孪生水网建设"）；此处未 \cite，而 nationalWaterNetwork2023
   在 bib 中现成未用。
2. chapter01.tex L49 —"七大江河数字孪生流域"的数量与措辞出处。
3. chapter01.tex L48-49 — smartWaterGuidance2021 一条 bib 同时代指《关于大力推进
   智慧水利建设的指导意见》与《"十四五"期间推进智慧水利建设实施方案》两份不同文件，
   且 URL 指向贵州省水利厅转载页而非水利部官网。需拆成两条并换官方 URL。
4. chapter01.tex 表1.2 — SL/T 651—2014 只写编号未写标准名《水文监测数据通信规约》；
   "用途"栏写的"智能传感器与遥测终端之间"是否在该标准适用范围内；SL 与 SL/T 前缀
   变更宜加脚注。
5. chapter02.tex L409 —"GB/T 9385-2008……目前继续有效"是时效性断言，付印后无法更新；
   且该标准修改采用 IEEE 830-1998，而 IEEE 830 已被 ISO/IEC/IEEE 29148 取代，
   教材完全未提 29148。
6. chapter02.tex L21 — \cite{IEEE1074} 为 IEEE Std 1074-2006，已被 ISO/IEC/IEEE 12207
   取代，而同句并列引用的正是 12207。
7. chapter09.tex L52 — lorawanSpec2023 键名年份与条目 year={2017} 不符；
   LoRaWAN L2 1.0.4 才是当前主推部署版本。
8. chapter09.tex L91 —"规划与指导文件（通常每年更新）"，规划纲要按五年期编制。
9. chapter06.tex L190 — Bentley ContextCapture 自 2023 年起并入 iTwin Capture Modeler
   产品线；本句以"纠正旧称"立论，自身却用了一个正在被替换的名称。
10. chapter06.tex L155 —"高程异常可达到十几米至几十米量级"过于含糊，宜给区间并指明
    应使用经批准的区域似大地水准面模型。

同时在仓库根目录新建《待核事实清单-第五轮.md》，把这 10 条整理成表（编号 / 位置 /
待核内容 / 建议核对来源 / 结论栏留空），交编者填写。

【硬指标】
- 只插入注释和新建清单文件，**不得修改任何一处正文文字**。
- 各文件正文汉字数与基线完全相等（注释不计入正文汉字，门禁会验证）。

【自检】python tools/check_textbook.py --build 全绿。
【收尾】追加《修改记录-第五轮.md》并 git commit，首行 "O8 事实核验点标注（10处）"。
做完停下汇报。
```

---

# 批次 A · 扩写主体

以下 34 个包共用同一段开头，只有工作包编号和硬指标不同。**开头段照抄，不要省略。**

## A 系列通用开头（每条都以此开头，一个字都不要省）

```
仓库：E:\2026\教材\智慧水利平台架构与开发

【开工前】完整读 AGENTS.md 的九条铁律。四条最关键：
  第 1 条 只增不删——任何文件的正文汉字数不得低于 tools/wordcount_baseline.json；
  第 2 条 代码清单不设行数上限——上一轮"压到40行内"的指令已撤销，教学代码的第一
         标准是可独立运行（import、类型定义、依赖注入、调用方齐全），宁可 60 行完整
         也不要 20 行片段；
  第 5 条 不许注水——技术章每 1,200 正文汉字至少配 1 个代码清单/图/表，新增的每个
         小节必须至少包含可运行代码、公式推导、数据表、反例、水利实例之一；
  第 9 条 扩写先回收，不许凭空写。
再读《扩写与修订方案-第五轮-2026-08-06.md》第五节中本工作包的条目、
《旧版内容回收清单-第五轮.md》（尤其第五节映射表和第六节甄别原则）、
以及《审查报告-第四轮-2026-08-06.md》中对应章的问题清单。

【第一步：回收，不要跳过】
本书素材总量 352,429 字，目标只有 200,000 字。**这是选材题不是作文题。**
动笔前先把本工作包能捞回的内容全部找出来：

  1) L1 删除前的 tex（首选，经过 2026-04 四阶段精修，质量最高）：
       git show d8beab0:output/chapters/chapterNN.tex > /tmp/old_chNN.tex
       git diff d8beab0 HEAD -- output/chapters/chapterNN.tex
     第三轮删掉了全书 48,473 字，本工作包对应的被删小节标题见回收清单第三节。

  2) L2 原始手稿（L1 里没有的再来这里找）：
       docs/chapters/chapterNN/sectionNN-MM.md
     具体文件见回收清单第五节的映射表。

  在提交说明里写清：回收了哪些段落（来源文件 + 小节名）、新写了哪些部分。
  凡是本工作包的目标内容在 L1/L2 里存在而你选择重写的，要说明为什么。

【第二步：回收内容必须过三道闸】
  (a) 概念、原理、公式、流程、水利实例、图表 —— 直接回收，只做体例适配。
  (b) 一切技术细节 —— **逐条对照 AGENTS.md 第 6 条的技术基线更新**。L2 手稿是
      2025 年的，里面有 Vue 2 选项式 API、Vue CLI/webpack、Spring Boot 2 的 javax.*、
      WebSecurityConfigurerAdapter、jjwt 0.9、Three.js 的 outputEncoding/Geometry、
      Cesium readyPromise、Chart.js、MySQL/Oracle/InfluxDB 等一大批过时写法。
      **回收一段代码就要逐行确认 API 未废弃**，原样搬进来等于把上一轮修掉的硬伤请回去。
  (c) 有几块第三轮删得对，**不要回收**：ch03 的 SafeHome 家庭安防案例、
      ch05 的 Python/Flask 平行实现、ch06 的"典型应用案例/关键技术挑战/发展趋势与展望"
      三节论文腔、ch09 的 10 道错位习题与"截至2026年4月"时点表述、
      任何无出处的项目数量与成效百分比。

【第三步：按下面的工作包要求补齐 L1/L2 里也没有的部分。】
```

## A4 系列 · 第4章前端（+23,543）

```
【工作包】A4-1 · HTML 语义化与文档结构 ｜ 目标：chapter04.tex 正文净增 ≥ 2,500 字

【素材】L1 ch04 已删小节：Web前端的定义与特点 / 万维网与Web技术体系 / 浏览器的组成架构 / 渲染引擎的工作原理 / JavaScript引擎与脚本执行 / 浏览器兼容性与标准化 / 网络通信与数据交换 / HTML基础与实践 / HTML核心概念与基础语法 / HTML5语言基础与语义化；L2 section04-01.md、**section04-02.md（12,826字，34块代码）**

必须落地：文档流与浏览器渲染流程；语义标签体系（header/nav/main/article/section/
aside/footer/figure）及为什么不用 div 堆砌；表单控件与原生校验（required/pattern/
min/max/step，以及为什么前端校验不能替代后端校验，与第5章 @Valid 呼应）；
role/aria-* 无障碍属性；一个完整的水利监测页面骨架（含跳转链接与地标区域）。
载体要求：≥ 1 图 + ≥ 3 个代码清单，每个清单带 caption/label 并被正文 \ref 引用。
```

```
【工作包】A4-2 · CSS 基础 ｜ 目标：chapter04.tex 正文净增 ≥ 4,000 字

【素材】L2 **section04-03.md（8,022字，32块代码）——盒模型、优先级、单位体系都在这里**；L1 ch04 已删的 CSS 部分

必须落地（括号内是现状，说明缺口有多大）：
- 盒模型与 box-sizing（全章"盒模型"出现 0 次、box-sizing 0 次——这是 CSS 教学的第一块基石）
- 选择器与优先级 (a,b,c) 计算示例（现在只有半句"主要受来源、优先级和出现顺序影响"）
- 层叠、继承与 !important 的代价
- 单位体系 px/em/rem/vw/vh/%，以及各自该用在哪
- position 五种取值与层叠上下文（现在 position 未出现）
载体要求：盒模型示意图 1 张（TikZ）、优先级三线表 1 张、≥ 4 个代码清单。
顺带修：第 18-24 行的 \lstdefinelanguage{CSS} 从章正文移入 main.tex 导言区，
补 alsoletter={-}（否则 grid-template-columns、border-radius 这类含连字符的关键字
永远匹配不上），sensitive 改 false（CSS 属性名大小写不敏感），并加 \lstalias{css}{CSS}。
```

```
【工作包】A4-3 · CSS 布局与响应式 ｜ 目标：chapter04.tex 正文净增 ≥ 3,500 字

【素材】L2 **section04-03.md**（Flex/Grid/响应式在同一文件）

必须落地：
- Flexbox 完整讲解与代码（现在全章 Flex 只有第 111 行一句话、0 行代码，而学习目标2
  要求"使用响应式CSS构建水利业务页面"，简答题2 若考 Flex 学生无从作答）
- Grid 完整（现在只有零星示例）
- 媒体查询与断点策略、移动优先 vs 桌面优先
- 大屏适配 1920/2560/3840（rem 方案与 transform: scale 方案对比）
- CSS 变量与暗色主题（第 93 行定义了 --normal: #1677ff 却从未使用，是死代码，用起来）
载体要求：≥ 2 图 + ≥ 4 个代码清单，其中必须有"告警工具栏 Flex 实例"和
"监测仪表盘 Grid 实例"两个完整可运行示例。
```

```
【工作包】A4-4 · JavaScript 语言与 DOM ｜ 目标：chapter04.tex 正文净增 ≥ 4,000 字

【素材】L1 ch04 已删小节：JavaScript核心概念与基础语法 / JavaScript语法 / 对象与数组 / 现代DOM查询与元素选择 / 现代事件处理机制 / ES6模块系统与项目架构；L2 **section04-04.md（19,456字，118块代码，全书代码最密的文件）**

必须落地：
- 类型与相等性、函数与闭包、数组高阶方法、解构与展开、ES 模块
- DOM 查询与增删改
- 事件对象、冒泡与捕获、事件委托、preventDefault（现在"冒泡"0 次、"事件委托"0 次，
  而第 226 行讲"列表较长时采用分页或虚拟滚动"，正是引入事件委托的天然位置）
- 长列表的事件委托与虚拟滚动实现思路
载体要求：≥ 1 图（事件流三阶段）+ ≥ 5 个代码清单。
顺带修：第 207-224 行用 language=html 标注了一段以 <script> 内 JavaScript 为主的清单，
JS 关键字不会高亮——拆成"HTML 片段 + JS 片段"两个清单。
```

```
【工作包】A4-5 · 异步与网络 ｜ 目标：chapter04.tex 正文净增 ≥ 3,000 字

【素材】L1 ch04 已删小节：Promise基础概念与状态管理 / async-await语法与现代异步编程 / 错误处理与异常管理 / Promise高级应用模式；L2 **section04-04.md**

必须落地：
- 事件循环与宏/微任务
- Promise 三态，且状态一经落定即不可再变（现在第 161 行只说有三种状态，
  而客观题3 恰恰考"fulfilled 后能否再变 rejected"，正文无支撑）
- async/await 与错误分类（第 147-157 行 parseReading 的 catch 同时接住 JSON.parse 的
  SyntaxError 和 validateLevel 抛的 RangeError，日志文案却统一写"监测数据解析失败"，
  与"应在界面给出可理解提示"自相矛盾——改为按错误类型分支）
- AbortController 完整用法（现在只有一句话、无代码）
- **request.js 封装**：fetch + Authorization 令牌注入 + 401 跳登录 + 超时
- Vite server.proxy 与 import.meta.env
**这一包补的是第5章签发的 JWT 在前端侧的断链**：现在第 314 行守卫直接读
sessionStorage.getItem('token')，但这个 token 从哪来、如何随请求发出、为何放
sessionStorage（XSS 权衡），全书没有交代。
载体要求：≥ 4 个代码清单。
```

```
【工作包】A4-6 · Vue 3 组合式 API ｜ 目标：chapter04.tex 正文净增 ≥ 4,000 字

【素材】L1 ch04 已删小节：Vue.js框架与前端开发 / Vue.js核心概念与MVVM模式 / Vue基础语法与开发实践；L2 **section04-05.md（11,550字，27块代码）**。注意手稿是 Vue 2/选项式，回收时全部改写为 Vue 3.4 组合式 API

必须落地（现状：第 249 行只用一句话提到 ref/reactive/computed，而全章代码里
ref( 出现 0 次、reactive 0 次、v-for 0 次、v-model 0 次、v-if 0 次、watch 0 次——
学生读完本章写不出一个"测站列表 + 筛选"的最基本页面）：
- ref / reactive / computed / watch / watchEffect，各自适用场景与 .value 陷阱
- 模板指令 v-if / v-show / v-for(:key) / v-model / v-bind / v-on
- 组件通信 props / emit / slot / provide-inject
- 完整生命周期，并配代码演示 onMounted 建定时器、onUnmounted 清理
  （第 294 行有这句文字但没有代码）
- SFC 结构与 <script setup>
载体要求：生命周期图 1 张 + ≥ 6 个代码清单，其中必须有一个"测站列表筛选页"的完整实现
（含 ref、computed、v-for、v-model、v-if、组件拆分）。
```

```
【工作包】A4-7 · Router 与 Pinia 实战 ｜ 目标：chapter04.tex 正文净增 ≥ 2,500 字

【素材】L2 section04-05.md、section04-06.md（55块代码）。手稿用 Vue CLI，改为 Vite 5

必须落地：
- <router-view> 与 App.vue 骨架（现在没有，学生不知道路由组件渲染在哪）
- useRouter / useRoute、编程式导航、嵌套路由与动态路由
- **修 bug**：第 313-316 行守卫 `return '/login'`，但 routes 里根本没有 /login，
  学生照抄会得到 [Vue Router warn] No match found 并停在空白页。补 /login 路由，
  守卫改为 return { name: 'login', query: { redirect: to.fullPath } } 并加防环判断。
- 第 309 行用了 props: true，但没展示 StationDetail.vue 如何 defineProps 接收——补上。
- 组件内 useStationStore()，以及 **storeToRefs 与"直接解构 store 会丢失响应性"**
  （Pinia 教学的头号易错点，现在完全没提）
- setup 式 store 写法与选项式对照
- **修 bug**：第 321-341 行 store 的 actions 用了 loadLatestLevel 但既无 import
  也无说明，补 import { loadLatestLevel } from '../api/stations.js'
载体要求：≥ 4 个代码清单。
```

```
【工作包】A4-8 · 工程化与构建 ｜ 目标：chapter04.tex 正文净增 ≥ 1,500 字

【素材】L1 ch04 已删小节：教材主线技术栈与扩展路线；L2 section04-06.md（脚手架工程化）、section04-07.md（部署发布，9,184字）。手稿是 webpack 口径，改为 Vite 5

必须落地：Vite 原理与开发/生产差异；路径别名；环境变量与多环境；
manualChunks 代码分割；产物体积分析；构建产物的部署方式（与 S2 的 docker-compose 呼应）。
**修 bug**：第 366-375 行注释写"明确生产构建目标并保留可追踪的分包名称"，
但配置里只有 target 和 sourcemap，没有任何分包配置。要么改注释，要么补
rollupOptions.output.manualChunks——本包选后者。
载体要求：≥ 2 个代码清单。
本包完成后 chapter04.tex 应达到 26,000 字、≥ 26 个代码清单、≥ 5 图，门禁会验证。
```

## A5 系列 · 第5章后端（+23,629）

```
【工作包】A5-1 · 后端分层与 REST ｜ 目标：chapter05.tex 正文净增 ≥ 2,500 字

【素材】L1 ch05 已删小节：后端服务概述 / HTTP协议与RESTful API设计；L2 section05-01.md（19,174字）、section05-02.md（13,537字）。**这两个文件里有大量 Python/Flask 平行实现，一律不回收**

必须落地：分层职责与依赖方向；REST 资源建模；HTTP 方法与**幂等性**对照表
（现有 tab:http-methods 补一列"是否幂等"，与 A5-7 的消息幂等呼应）；
状态码约定；API 版本化策略；分页/排序/过滤的 URL 约定；服务发现与微服务边界
（承接 O5 移除的 Eureka 段落，把它放回有上下文的地方）。
载体要求：≥ 1 图（请求链路，本章现在 0 张图）+ ≥ 2 个代码清单。
顺带修：第 21 行"若进一步拆分为网络服务"——所引 Newman《Building Microservices》
讲的是微服务，第3章全书用"微服务"15 次，此处统一为"微服务"。
```

```
【工作包】A5-2 · Spring Boot 工程骨架 ｜ 目标：chapter05.tex 正文净增 ≥ 2,500 字

【素材】L1 ch05 已删小节：Spring Boot企业级开发框架 / 依赖注入与控制反转 / 实际应用场景；L2 section05-03.md（13,169字，26块代码）。手稿是 Spring Boot 2/javax.*，全部改 3.2+/jakarta.*

必须落地：起步依赖与自动配置原理；application.yml 与 Profile 多环境；
依赖注入与 Bean 生命周期；工程目录结构。
**修 bug**：第 262-263 行 @ConfigurationProperties("security.jwt") 标注在 record 上，
需要 @EnableConfigurationProperties(JwtProperties.class) 或 @ConfigurationPropertiesScan
才会被注册（record 走构造器绑定，仅加 @Component 无效），书里没写；
同时 application.yml 只配了 secret 没配 issuer，而正文要求校验 issuer，
properties.issuer() 实际会是 null。两处都补上。
载体要求：≥ 3 个代码清单，其中 yml 清单必须标 [language=YAML]（main.tex 已定义该语言，
现在第 60-69 行裸用 \begin{lstlisting}）。
```

```
【工作包】A5-3 · 读写接口与参数校验 ｜ 目标：chapter05.tex 正文净增 ≥ 3,000 字

【素材】L1 ch05 已删小节：RESTful API设计 / 服务层架构设计；L2 section05-02.md、section05-05.md

必须落地：
- **@PostMapping + @Valid @RequestBody 的完整写接口**——现在全章 @PostMapping 出现
  0 次、@Valid 0 次，唯一的控制器是 @GetMapping。后果是第 192 行定义的
  CreateReadingRequest 和第 207 行的 MethodArgumentNotValidException 处理器
  在书里永远触发不了，第 23 行讲的"创建成功返回201"也无代码支撑，
  而章末交付物和习题12 都要求"监测值写入接口"。
- GET/POST/PUT/DELETE 全套 + 201 + Location 头
- DTO ↔ 实体转换
- @RestControllerAdvice 统一异常处理与错误响应体规范
**修**：第 192-195 行 @DecimalMin/@DecimalMax 用在 double 上——Jakarta Bean Validation
规范对这两个注解明确排除 double/float（舍入误差），能跑通只是 Hibernate Validator 的
规范外扩展。改为 @Min/@Max 或字段用 BigDecimal，并补一句浮点边界校验的舍入风险说明。
载体要求：≥ 4 个代码清单。
```

```
【工作包】A5-4 · JPA 与数据访问 ｜ 目标：chapter05.tex 正文净增 ≥ 4,000 字

【素材】L1 ch05 已删小节：数据库持久化技术 / 数据建模实践；L2 **section05-04.md（10,826字）**。手稿可能用 MySQL，改为 PostgreSQL/PostGIS/TimescaleDB

必须落地：实体映射与主键策略；关联与懒加载；**N+1 与 fetch join**（现在 0 次，
本科首门后端课必讲）；派生查询命名规则；@Query；**Pageable/Page**（现在 0 次，
但学习目标第6条承诺了分页）；@Version 乐观锁（0 次）；索引设计（第 338 行只说
"建立索引"）；审计字段；ddl-auto 与建表策略。
**调整**：第 170-181 行的 WaterDataSummary 公式与代码本身正确（上一轮硬伤确已修好），
但它被放在"Jakarta Persistence 与事务管理"节下却是一个与实体、Repository、事务
毫无关系的纯内存类。移到服务层小节，并补两点：非线程安全（并发调用会算错）、
浮点累积误差，给出 Welford 增量式写法 averageLevel += (newLevel - averageLevel)/(dataCount+1)
作为数值稳定的替代。
**补**：第 98-119 行 WaterReading 实体一个 getter 都没有，而第 84 行 ReadingResponse
要靠它取值。补访问器，或在章首统一声明"清单省略 public 修饰符与 import"。
载体要求：≥ 5 个代码清单 + ≥ 1 张索引/查询对照表。
```

```
【工作包】A5-5 · 事务 ｜ 目标：chapter05.tex 正文净增 ≥ 2,500 字

【素材】L1 ch05 已删小节：事务管理；L2 section05-04.md

必须落地：ACID；七种传播行为逐一说明与适用场景；隔离级别与并发异常；
自调用失效（现有示例通过注入另一 Bean 演示 REQUIRES_NEW，是对的，保留并扩展说明）；
只读事务；事务边界设计原则。
**修 bug**：第 293-308 行 ReadingEventHandler 有两个问题——(a) 字段与构造器写在使用
它的方法之后，读起来像截断产物，提到方法之前；(b) **全章没有发布方**，
没有任何 ApplicationEventPublisher.publishEvent(new ReadingSavedEvent(...))，
学生看不到事件从哪发出。在 ReadingCommandService.save()（第 152-156 行）补发布，
与 AFTER_COMMIT 形成闭环。MetricsCounter 也是未定义类，补定义或说明。
载体要求：≥ 1 图（事务传播与自调用失效）+ ≥ 3 个代码清单。
```

```
【工作包】A5-6 · 安全与 JWT ｜ 目标：chapter05.tex 正文净增 ≥ 4,000 字

【素材】L1 ch05 已删小节：Spring Security安全认证；L2 section05-06.md（12,617字）。**手稿几乎肯定是 WebSecurityConfigurerAdapter + jjwt 0.9，必须整体改写为 Security 6 + jjwt 0.11.x**

这是第5章最大的空洞，四处缺失叠加导致整章安全部分无法自洽：
1. **SecurityFilterChain 缺 exceptionHandling**（第 222-239 行）。写法本身符合
   Spring Security 6（用了 SecurityFilterChain + Lambda DSL + authorizeHttpRequests，
   没有出现已废弃的 WebSecurityConfigurerAdapter/authorizeRequests，这点已修好），
   但无认证机制配置时默认入口点是 Http403ForbiddenEntryPoint，未携带令牌的请求返回
   403，而第 23 行明确教"未认证返回401，无权限返回403"——教材前后打架。
   补 authenticationEntryPoint 返回 401、accessDeniedHandler 返回 403。
2. **JwtAuthenticationFilter 全章从未定义**（第 228 行只作为方法参数出现）。
   补一个完整的 OncePerRequestFilter 实现：从 Authorization: Bearer 取令牌、
   解析、构造 authorities、SecurityContextHolder 设置认证、异常时保持匿名。
3. **只有解析没有签发**（第 261-285 行只有 parseAllowExpired）。补 Jwts.builder()
   签发、登录接口、PasswordEncoder、UserDetailsService、访问令牌与刷新令牌的有效期。
4. **安全表述有误且危险**（第 259 行）："应先安全取得Claims，再验证令牌类型、签名、
   签发者和刷新期限"——这个顺序是错的。parseClaimsJws() 在返回前已完成签名校验，
   签名不合法时抛 SignatureException 根本拿不到 Claims；ExpiredJwtException.getClaims()
   之所以安全，恰恰是因为签名已经验过才轮到过期检查。按字面理解学生很可能去手工拆
   Base64 或改用不验签的 parseClaimsJwt()，直接埋下伪造令牌漏洞。**必须重写这段。**
   同时 parseAllowExpired 不做任何 type 校验，第 287 行只用文字要求，代码没落地，
   学生照抄会把过期的 access token 当刷新凭据接受——把类型校验写进方法。
另需补：方法级权限、CORS、令牌撤销机制（黑名单/jti/版本号，习题15 现在无正文支撑）。
版本口径：第 17 行写"jjwt 0.11+"字面上包含 0.12/0.13，但示例用的 parserBuilder()/
parseClaimsJws()/getBody()/setSigningKey() 自 0.12.0 起全部 @Deprecated。
改为"jjwt 0.11.x（示例接口）"并加一个 tipbox 说明 0.12 的迁移映射
（Jwts.parser().verifyWith(key).build().parseSignedClaims(t).getPayload()）。
载体要求：≥ 1 图（认证时序）+ ≥ 6 个代码清单。
```

```
【工作包】A5-7 · 消息队列 ｜ 目标：chapter05.tex 正文净增 ≥ 2,500 字

【素材】L2 section05-06.md；L1 帮助有限，本包以新写为主

必须落地：为什么要引入 MQ（同步调用的失败模式）；Kafka 核心概念；
**生产者 KafkaTemplate.send（现在只有消费者）**；spring.kafka.* 配置与
spring.json.trusted.packages（record 走 JSON 反序列化最经典的踩坑点，正文一字未提）；
幂等去重表或唯一约束（现在幂等被藏在方法名 evaluateIdempotently 里，没有展示实现）；
**重试与死信队列的真实代码**——第 332 行说"配置有限重试、死信队列和监控"，
但没有 DefaultErrorHandler + DeadLetterPublishingRecoverer 或 @RetryableTopic
任何代码，目前只是口号；事务发件箱（Transactional Outbox，注意中译，
第8章第 253 行误译为"事务外盒"，本包统一为"事务发件箱"）。
载体要求：≥ 4 个代码清单。
```

```
【工作包】A5-8 · 性能与可运维 ｜ 目标：chapter05.tex 正文净增 ≥ 2,500 字

【素材】L1 ch05 已删小节：异常处理与日志记录 / 应用最佳实践；L2 section05-06.md

必须落地：@Cacheable / Redis（现在 0 次）；缓存穿透、击穿、雪崩及应对；
分页与游标；连接池；慢查询定位；Actuator 端点；Micrometer 关键指标表；
结构化日志与 traceId 贯穿（与第8章第 654 行呼应）。
背景：学习目标第6条（第 12 行）承诺"通过缓存、分页、日志与指标改善服务性能和
可运维性"，但 5.7 节（第 336-340 行）总共两段文字、无代码、无表、无图。
载体要求：≥ 1 图 + ≥ 3 个代码清单 + ≥ 1 张指标表。
```

```
【工作包】A5-9 · 测试 ｜ 目标：chapter05.tex 正文净增 ≥ 2,000 字

【素材】L2 section05-05.md、section05-06.md；测试内容手稿里也少，本包以新写为主

必须落地：单元测试与集成测试的边界；@SpringBootTest；MockMvc；Testcontainers；
测试数据准备与清理；**正常/参数错误/无权限/资源不存在四场景覆盖表**。
背景：全章现在测试内容为零（无 @SpringBootTest、无 MockMvc、无 Testcontainers），
但第 373 行实践题要求"所有单元测试和接口测试均须包含正常、参数错误、无权限和
资源不存在场景"——习题严重超出正文支撑。
另：第 342-344 行 Python 框架节属"只列名词"（Flask/Django/FastAPI 各一句，无代码、
无对比维度）。改为一张三列对比表（适用场景/生态/部署约束）并整体收进 tipbox 选学框。
习题15"说明如何处理过期刷新令牌与服务端撤销"需与 A5-6 补的撤销机制对齐。
载体要求：≥ 3 个代码清单 + ≥ 1 张场景覆盖表。
本包完成后 chapter05.tex 应达到 26,000 字、≥ 26 个代码清单、≥ 5 图，门禁会验证。
```

## A6 系列 · 第6章三维场景（+18,835）

```
【工作包】A6-1 · WebGL 与 Three.js 基础补全 ｜ 目标：chapter06.tex 正文净增 ≥ 4,000 字

【素材】L1 ch06 已删小节：WebGL与Three.js三维渲染基础 / 三维图形学基础概念 / WebGL渲染流程与核心对象 / Three.js核心架构与开发流程 / 智慧水利场景的渲染优化策略；L2 **section06-02.md（36,255字，全书最大的单个文件）**、section06-06.md（9,881字）。手稿是旧版 Three.js，注意 outputEncoding→outputColorSpace、Geometry→BufferGeometry

**最重要的一条**：全书检索 WebGLRenderer、PerspectiveCamera、setAnimationLoop、
requestAnimationFrame、new Cesium.Viewer，在第6、7、8章出现次数均为 0。
第 76 行的 Three.js 片段创建了 scene 和 loader，但没有相机、渲染器和渲染循环，
**这段代码运行后屏幕上什么都不会有**；第 121、168 行的 viewer 变量从未定义。
而第 745 行章末交付物白纸黑字要求"一段可运行的 Three.js 或 Cesium 加载代码"。

必须落地：
- 最小可运行程序骨架（renderer + camera + setAnimationLoop + resize 处理）
- r152+ 色彩管理：outputColorSpace / SRGBColorSpace 取代已移除的
  outputEncoding / sRGBEncoding；THREE.ColorManagement.enabled 默认 true
  （教材声称以 r160+ 为基线却未提及这个最容易踩的废弃 API）
- 几何体、材质、光照、场景图与变换
- 性能：实例化绘制、LOD、纹理与内存
- 透视矩阵补一句 NDC 深度区间约定：该矩阵对应 OpenGL/WebGL 的 z∈[-1,1]，
  WebGPU、Direct3D 与 Cesium 的 reverse-Z 采用 [0,1]，第三行系数不同
- WebGL1 差异改为具体扩展名（OES_vertex_array_object、OES_element_index_uint、
  WEBGL_draw_buffers，不支持 GLSL ES 3.00/UBO/实例化内置支持/整型纹理），
  现在第 40 行只笼统说"要求不同"
- three/addons/ 路径说明：它是官方 importmap 别名，仅在浏览器 importmap 或已配置
  该别名的构建环境下有效；npm + 打包器环境的真实路径是 three/examples/jsm/...
  （现在未区分，学生在 Vite 工程里会直接报模块解析失败）
载体要求：≥ 2 图 + ≥ 4 个代码清单。
顺带修：\lstdefinelanguage{GLSL} 现在定义在 chapter08.tex 第 3 行的正文里，
而 main.tex 先 \input chapter06 再 \input chapter08——给第6章的着色器加
language=GLSL 会直接报 Undefined language。把它移入 main.tex 导言区，
补 GLSL ES 3.00 关键字（in/out/layout/mat4/mat3/sampler2D/texture/gl_Position/
#version/int/bool/const 等）并加 \lstalias{glsl}{GLSL}；第6章第 55 行补 language=GLSL。
```

```
【工作包】A6-2 · 坐标系与投影补全 ｜ 目标：chapter06.tex 正文净增 ≥ 4,000 字

【素材】L1 ch06 已删小节：空间参考系统与坐标转换；L2 **section06-03.md（26,524字）**

必须落地：
- **3 度带（现在完全没有，而水利工程大比例尺测图默认用 3 度带）**：
  n = floor((λ-1.5)/3)+1，λ0 = 3n；CGCS2000 3 度带 EPSG:4513-4533（含带号前缀）
  与 4534-4554（不含前缀），6 度带 4491-4501 与 4502-4512。
- **大地高与正常高的转换公式**（现在只有文字，无公式，而第7章第 206 行已声称
  "第6章已经说明分带、中央经线和高程基准"，形成章际悬空）：
  H_γ = h - ζ；并区分正常高（我国 1985 国家高程基准，对应高程异常 ζ）
  与正高（对应大地水准面差距 N，H_g = h - N）。删掉"术语不是'加速度重力异常'"
  这种针对不存在读者误解的否定句。
- **删掉第 135 行的错误数字**："不能硬编码'黄河19–21带、长江28–30带'"——
  按 6 度带，长江流域约 16-21 带，28-30 带对应 159°E-177°E，是太平洋中部。
  改为"不能在代码中硬编码某一固定带号，也不能在未标注 3 度带/6 度带口径的情况下
  引用带号区间"，或补齐口径后写正确值。
- **统一 proj 写法**：现在第6章用 +a/+rf 显式椭球 + x_0=19500000（带号前缀），
  第7章第 230-232 行用 +ellps=GRS80 + x_0=500000（无前缀）+ lon_0=117，两章矛盾。
  统一为 +ellps=GRS80（GRS80 与 CGCS2000 椭球参数一致，a=6378137，1/f=298.257222101）
  + k_0（+k 是历史别名，PROJ 6+ 推荐 +k_0）+ no_defs + type=crs；
  东坐标统一用无前缀并显式记录带号，交付数据再按规范加前缀，并在示例注释里
  标注等价的 EPSG 代码。
- 坐标转换链实例与精度评估。
载体要求：≥ 1 图 + ≥ 1 张 EPSG 对照表 + ≥ 3 个代码清单。
习题补两道计算题：某测站经度 113°42′E，分别求 6 度带、3 度带带号与中央经线；
某点 GNSS 测得大地高 h=245.30 m，该区高程异常 ζ=-8.62 m，求 1985 国家高程基准下的正常高。
```

```
【工作包】A6-3 · OGC 服务补全 ｜ 目标：chapter06.tex 正文净增 ≥ 3,000 字

【素材】L1 ch06 已删小节：GIS地图服务与三维场景集成 / GIS地图服务的类型与作用 / 二三维一体化集成方法 / 智慧水利业务图层叠加；L2 **section06-03.md**。手稿的 Cesium 用法注意 readyPromise→fromUrl+await

必须落地：
- tab:ogc-services 增加 WCS 行（覆盖栅格数据本体，可按范围/波段取原始像元值，
  用于 DEM 取值与淹没分析；bib 里 ogcWCS 现成，现在只有第9章用了）
  与 3D Tiles 行（说明它是 OGC 社区标准，支持 LOD 流式加载）。
  学习目标2 从"区分 WMS、WMTS 与 WFS"改为"区分 WMS、WMTS、WFS 与 WCS"。
- **三条最小合法 KVP 请求示例**（现在全节 0 条，而习题10 要求"比较 WMS、WMTS 和
  WFS 的返回内容"，学生只能背表格）：GetMap / GetFeature / GetCoverage，
  用 language=HTTP（main.tex 已定义）。
  必须提醒：WMS 1.3.0 使用 CRS 参数且 EPSG:4490 的 BBOX 轴序为纬度在前——
  这是国内最常见的踩坑点，非常适合作教学点。
- 补一句 OGC API 系列（Features/Tiles/Coverages/Maps）正在逐步替代经典 OWS，
  新建平台应评估该路线，与第9章第 56 行口径打通。
- GeoServer 发布流程与 GWC gridset 创建。
- **修 bug（会直接跑不出图）**：第 113-122 行 Cesium WMTS 示例——
  WebMapTileServiceImageryProvider 的 tilingScheme 默认值是 WebMercatorTilingScheme，
  而 tileMatrixSetID 指向 EPSG:4490（地理坐标瓦片矩阵集），Cesium 会按 Web 墨卡托的
  行列号请求地理格网瓦片，结果是空白或全图错位。必须显式传
  tilingScheme: new Cesium.GeographicTilingScheme()，并补 maximumLevel（否则会请求
  超出 gridset 层级的瓦片产生大量 404）。同时说明 GeoServer GWC 默认只内置 EPSG:4326
  与 EPSG:900913 两个 gridset，EPSG:4490 需手工创建。
- **补 Viewer 构造**：第 111 行声称"教学示例使用自建 GeoServer，不依赖商业底图密钥"，
  但 CesiumJS 默认 new Cesium.Viewer() 仍会加载 Ion 底图与地形并要求 token。
  补 { baseLayer: false, baseLayerPicker: false, geocoder: false, timeline: false,
  animation: false }，让这句承诺落到代码上。
载体要求：≥ 4 个代码清单。第 511 行的 JSON 清单补 language=JSON。
```

```
【工作包】A6-4 · 倾斜摄影与 BIM 补全 ｜ 目标：chapter06.tex 正文净增 ≥ 3,500 字

【素材】L1 ch06 已删小节：BIM与倾斜摄影三维模型构建 / 无人机倾斜摄影测量系统构成与特点 / 三维模型具体构建流程 / BIM模型在水利工程中的作用与融合 / 工程三维模型构建流程 / BIM与GIS融合技术 / 模型成果分析；L2 section06-04.md（14,717字）、section06-05.md（6,631字）

必须落地：
- **平面点位中误差 m_p = sqrt(m_x² + m_y²)**——国内测绘规范（CH/T 3007、GB/T 24356 等）
  按平面点位中误差和高程中误差两项给限差，不按 m_x、m_y 分别给限差。现在第 768 行
  习题要求"使用5个以上检查点分别计算 m_x、m_y、m_h，判断成果是否满足给定限差"，
  学生按正文算不出 m_p，无法完成。
- 粗差判定规则：检查点残差绝对值超过 2 倍中误差应复核，超过 3 倍按粗差处理并记录剔除理由。
- **§6.3 引入国标**（现在整节零国标引用，全章 11 条引文全是 OGC/EPSG/厂商文档/学术论文；
  bib 里的 SL 601-2013、SL/T 725-2016 在第6章一次未用）。至少补充并引用
  CH/Z 3004、CH/Z 3005（低空数字航空摄影测量内业/外业规范）、GB/T 18314（像控点施测），
  并给一组典型精度对照（如 1:500 成图对应 GSD 一般不大于 3 cm，平面中误差限差量级）。
  **具体数值须以现行规范为准，无法确认的标 TODO-核对，不要编。**
- 第 155 行"高程异常可达到十几米至几十米量级"改为给区间（我国大陆约 -40 ~ +70 m，
  东部平原一般 ±10 m 以内，西部高原可达数十米），并指明应使用经批准的区域似大地
  水准面模型（如 CNGG2011 或省级精化成果）并在元数据中记录模型名称与版本。
- 空三与像控施测流程细化；第 199 行对特征点/连接点/像控点/检查点的四层区分表述
  第四轮复核认为准确，保留不要改坏。
- 第 190 行 Bentley ContextCapture 补注"（现已并入 iTwin Capture Modeler 产品线）"。
载体要求：≥ 1 图 + ≥ 1 张精度指标表。
```

```
【工作包】A6-5 · 数字孪生节整理与交叉引用 ｜ 目标：chapter06.tex 正文净增 ≥ 4,000 字

【素材】L1 ch06 已删小节：水利工程数字孪生架构 / 数字孪生五维模型与技术架构；L2 section06-07.md。**"典型应用案例""关键技术挑战与解决方案""发展趋势与展望"三节是论文腔重灾区，不要回收**；五维模型的归属问题按 O1 的结论处理

**决策已定：采用轻方案，不重排章节结构。**
第6章 §6.4 与第8章 §8.5 在七个主题上大面积重复（6.4.5 模型卡↔8.5.11、
6.4.6 事件时间与质量码↔8.5.10、6.4.9 事件契约↔8.3.1、6.4.13 权限降级↔8.5.8/8.5.16、
6.4.14 血缘值守↔8.5.15/8.6.2、6.4.15 验收↔8.6.3、6.4.16 课程路线↔8.5.14）。

必须落地：
1. §6.4 改名为"数字孪生水利平台架构概览"，与第8章 8.5 的"案例实现"形成分层递进。
2. 上述七个重复小节各在起首加一句交叉引用，把重复"显式化"为"框架 vs 实现"：
   "本节给出方法框架，清源水库上的具体实现见 8.5.x 节。"第8章对应处反向 \ref。
3. 6.4.7"三维交互与决策证据链"（第 425-453 行详述颜色编码、图例、无障碍、LOD 降级）
   明确让位给第7章——压缩为一段并 \ref 指向第7章对应小节。第7章第 206 行已建立
   "第6章构建、第7章展示"的分工声明，第6章不应再详述。
4. **6.4.11 流域预报调度场景补一张表**：并列的 6.4.10 大坝安全监测场景配有
   tab:dam-twin-scenario，而 6.4.11 只有两段纯文字、无图无表，密度落差明显。
   而流域预报调度恰是数字孪生水利的国家级重点。补一张结构对称的表
   （输入 / 状态更新 / 模型服务 / 输出 / 反馈），内容填降雨预报—产汇流—水库调度—
   下游影响链路，并明确"预报"与"调度"两类模型的输入输出契约差异。
5. 本包是第6章的收尾包，需把 6.1-6.3 扩写后的内容与 6.4 的交叉引用理顺。
载体要求：≥ 1 表 + 全部新增图表被 \ref 引用。
本包完成后 chapter06.tex 应达到 28,000 字、≥ 14 个代码清单、≥ 12 图，门禁会验证。
```

## A7 系列 · 第7章数据展示（+16,102）

```
【工作包】A7-1 · 可视化设计基础 ｜ 目标：chapter07.tex 正文净增 ≥ 4,000 字

【素材】L1 ch07 已删小节：数据类型与展示方式 / 水利监测数据分类体系；L2 section07-01.md（3,301字）

背景：本章从 1696 行砍到 423 行，砍掉的恰恰是"数据可视化"的通识内核，保留的是
三维定位与拾取。结果是章名与学习目标名不副实。本包补最核心的一块。

必须落地：
- Bertin 视觉变量与感知精度序列（位置 > 长度 > 角度 > 面积 > 颜色），
  这是"为什么这样选图"的根，现在 7.1.1 标题叫"视觉变量"但正文无理论
- **"任务 ↔ 图型"决策表**（比较/趋势/分布/构成/相关/定位六类任务），
  现在全章只有第 123 行一句话罗列折线/柱状/散点/箱线/仪表盘
- 双轴图的误导陷阱与正确用法
- **雨量倒挂柱 + 水位过程线双轴组合图**——这是水利可视化的看家图式，全书竟无。
  必须给完整的 ECharts 配置代码。
- 专题地图表达：等值线、色斑图、流向箭头、站点符号地图（现在完全没有，
  而这是水利可视化的半壁江山）
载体要求：≥ 2 图 + ≥ 1 张决策表 + ≥ 3 个代码清单。
```

```
【工作包】A7-2 · 色彩与可读性 ｜ 目标：chapter07.tex 正文净增 ≥ 2,500 字

【素材】L2 section07-02.md；L1 ch07 已删小节：设备状态颜色编码与图标系统

必须落地（现在全章关于色彩只有第 145 行一句"不能只依赖红绿差异"）：
- 顺序型 / 发散型 / 定性型三类色板的适用场景
- 为什么禁用彩虹色阶
- WCAG 对比度 3:1 / 4.5:1 及验证方法
- 色觉障碍与 ECharts aria: { enabled: true, decal: { show: true } }
  （图案填充正是色觉障碍的标准方案）
- 键盘可达与焦点顺序、图表的表格化替代文本
- 蓝黄橙红四级预警的具体色值，以及在浅底/深底大屏上的可辨性验证
- **明确"数据质量状态色"与"预警等级色"是两个维度**：现在简答题5 要求"设计正常、
  关注、告警、离线和可疑数据的颜色、形状与文字组合"，这四态与第8章的蓝黄橙红
  不是同一套口径。第7章第 279 行其实点到了"业务状态与数据质量分开编码"，
  但没和第8章打通——本包打通它。
载体要求：≥ 1 图 + ≥ 1 张色板表 + ≥ 2 个代码清单。
```

```
【工作包】A7-3 · 时间序列处理 ｜ 目标：chapter07.tex 正文净增 ≥ 3,000 字

【素材】L1 ch07 已删小节：实时数据与历史数据处理机制 / 数据质量检验与异常值处理 / 多源异构数据标准化与融合；L2 section07-01.md

必须落地（现在第 93 行只有两句话）：
- 不同采样周期的重采样与对齐（渗压 1 h / 水位 5 min / 雨量 5 min）
- **缺测断线的实现**：数据点写 null 依赖 connectNulls:false 断开，或用 markArea 打阴影。
  现在第 93 行只说"缺测区间应断线或用明确的虚线/阴影表示"就止住了，而实践题第1题
  要求"实现 300 点滑动窗口和缺测断线"——书里一个字都没有。
  给出 quality==='missing' ? [t, null] : [t, v] 的完整写法。
- 累计量 vs 瞬时量的插值禁区（第 93 行提了一句但无示例）
- 事件时间 vs 处理时间、乱序与迟到数据（第8章第 683 行讲了 validTime/ingestTime，
  第7章反而没有）
- 时区与跨日处理
- 第 110 行的质量码 valid/suspect/missing 是自造三值，加一句"本书三值为教学简化，
  工程落地应映射到 SL/T 651 的质量标识"并 \cite{slt6512014}（bib 现成，本章一次未引）
- 第 68 行主张"滑动时间窗口"而代码是 slice(-300) 的计数窗口（水位按 5 min 采样时
  300 点≈25 h），两者口径统一或明确说明适用差异
载体要求：≥ 1 图 + ≥ 3 个代码清单。
```

```
【工作包】A7-4 · ECharts 工程实践 ｜ 目标：chapter07.tex 正文净增 ≥ 3,500 字

【素材】L1 ch07 已删小节：数据图表展示 / ECharts高级图表集成 / 时序数据的动态可视化 / 响应式图表与移动端适配（**Chart.js在三维场景中的集成一节不要回收，基线已统一为 ECharts**）；L2 section07-02.md

必须落地：
- **setOption 的合并语义**：默认 notMerge:false 时 series 按 id 合并、lazyUpdate:true
  可把多次更新合帧、删除序列必须用 replaceMerge:['series']；超大数据流式追加用
  chart.appendData({seriesIndex, data})。这是增量更新的全部要点，现在一处都没讲，
  第 149 行"必须先设置完整初始配置"只是结论没有机理。给一张三种合并模式对照小表。
- 内置 sampling:'lttb'（7.1.2 花整节讲 LTTB 原理，7.2.2 用 ECharts 画曲线，
  两处不打通。这是"先讲原理、再看库已经替你做了什么"的绝佳衔接点）
- dataZoom、markArea/markLine + visualMap.pieces 阈值带
- canvas vs svg renderer 选型、progressive/progressiveThreshold、large/largeThreshold
- ResizeObserver + chart.resize()、组件卸载时 chart.dispose()
  （不 dispose 是最常见的内存泄漏，现在只在散文里提了一句）
- **重写第 151-167 行的增量更新示例**：现在 chart.getOption() 每次返回整份合并后
  option 的深拷贝，在实时高频回调里逐帧调用是明确的性能反模式；且 series[0] 按下标
  取序列，而第 169 行解说词说的是"带稳定 ID 的序列"——一旦加入阈值带 markArea
  或第二条曲线，series[0] 就不再是 level。改为把数据缓冲保存在应用状态（闭包数组或
  Pinia）中，这恰恰是本章第 173 行自己提出的原则，代码却违反了它。
- **7.2.3 图表与三维联动补完整代码**——现在整节只有两段散文、零代码，而它是学习目标
  第2条后半句、章末交付物第4项、实践题第3题共同指向的核心。必须给出：
  chart.on('click', params => ...) 及 params.data/seriesId/dataIndex 如何取回 assetId；
  chart.dispatchAction({type:'highlight'|'showTip', seriesId, dataIndex}) 反向从三维
  点亮图表；多图联动的 echarts.connect([a,b]) / option.group；
  三维侧 object.userData.assetId → 图表的映射表；一个 25-30 行的双向联动控制器
  （含解绑）。**这一包是本章能否成立的分水岭。**
载体要求：≥ 1 表 + ≥ 5 个代码清单。
```

```
【工作包】A7-5 · LTTB 与三维交互补强 ｜ 目标：chapter07.tex 正文净增 ≥ 3,000 字

【素材】L1 ch07 已删小节：监测点坐标转换与空间定位 / LOD技术在监测点渲染中的应用 / 监测点聚合与分层显示策略 / 射线投射算法与碰撞检测 / 监测点信息面板设计与实现 / 多层级信息展示策略 / 触控设备交互优化（**16个代码清单被砍到6个，大部分在这里**）；L2 section07-03.md、section07-04.md

必须落地：
- **LTTB 分桶规则**（现在完全缺失，学生无法实现）：设原始序列 N 点、目标 m 点（m≥3），
  保留首尾，中间 N-2 点均分为 m-2 桶；遍历第 k 桶时，P_prev 为第 k-1 桶已选点，
  P_C̄ 为第 k+1 桶横纵坐标均值（末桶取尾点）。
- 记号修正：现在第 70-76 行左端 A 是面积、右端 x_A/y_A 是"前一已选点 A"，同一符号两义；
  且 A 与 C 从未在公式语境中定义。面积改记 S，点记 P_prev / P_cand / P_C̄。
  面积表达式本身与 Steinarsson 原文实现一致，是对的，不要改坏。
- 15 行左右的 LTTB 参考实现。
- **重绘图7-3**：标题是"LTTB 降采样的几何直觉"，但 TikZ 里只画了折线、3 条虚线和
  5 个保留点，"Largest Triangle"的核心三角形一个都没画，也没有图例区分原序列与
  降采样结果；且 3 条虚线把 [0,10] 分成 4 段，与桶边界不吻合。重绘：标出一个桶、
  桶内 2-3 个候选点、画出面积最大的那个三角形（半透明填充）、加 legend。
- **重绘图7-8**（几何画错，已用坐标验算）：射线 (5.1,1.2)→(9.2,2.5) 在 x=8.9 处
  y≈2.41，而"最近交点"标在 (8.9,1.9)，交点不在射线上；三角形
  (8.2,0.3)-(9.5,2.8)-(10.4,0.7) 在 x=8.9 处的内部区间约 y∈[0.43,1.65]，该点也在
  三角形外；且射线段止于 (9.2,2.5)，尚未触及三角形。重算坐标使交点落在射线与
  三角形边的真实交点上；第 316 行由屏幕指向相机的箭头方向与射线相反，易被误读，
  改为无箭头细虚线并标注"NDC 换算"。
- 第 353-364 行补 distanceToPoint 的定义（现在是未定义自由变量，而第 364 行恰好
  宣称"这里的 pickingRadiusWorld 已定义"）；补两句：camera.fov 是垂直视场角
  （本书公式用的正是垂直方向，是对的）；若 camera.zoom≠1 需再除以 zoom。
- 表7-1 把位移的展示方式定为"箭头"，但 8 个位移测点的方位角（北为0°、顺时针）
  如何转成场景向量全章没有。补 v = (d·sinα, 0, -d·cosα) 三行公式。
- 第 233-247 行 proj 示例补一句：+x_0=500000 得到的是不含带号的东坐标，而国内测绘
  成果交付的通用坐标常带带号前缀（如 3 度带 39 号 → 39500000.00），学生拿到实测数据
  一减局部原点就会得到 3800 万米级的偏移。给出剥离带号的写法。
- 第 269-275 行 $r_{px}$、$r_{world}$、$H_{px}$ 的多字母下标会排成数学斜体，
  改为 r_{\mathrm{px}} 等。
- 第 328-347 行 Möller–Trumbore 实现正确，但应交代返回的是交点坐标而非参数 t；
  若 direction 未归一化，t 不等于距离，与"按交点距离排序"的说法衔接不上。
载体要求：≥ 2 图重绘 + ≥ 3 个代码清单。
本包完成后 chapter07.tex 应达到 20,000 字、≥ 14 个代码清单、≥ 8 图，门禁会验证。
```

## A8 系列 · 第8章综合案例（+14,924）

```
【工作包】A8-1 · 数据库设计与 DDL ｜ 目标：chapter08.tex 正文净增 ≥ 3,500 字

【素材】L2 **section08-02.md（地形数据处理，23块代码）、section08-03.md（数据质量控制，15块代码）**；ch08 第三轮是净增的，L1 帮助有限

背景：本章是全书唯一的贯穿实战章，1114 行、40 个浮动体，但只有 3 段代码清单
（对比 ch04 有 14 段、ch05 有 12 段）。链条上数据库、实体类、监测主线接口、
前端实现、部署五环全断。本包补第一环。

必须落地：表8-4 现在仅以中文散文列"关键字段/约束"，无一句 DDL、无字段类型、
无主外键、无索引、无 TimescaleDB 超表与分区策略、无 PostGIS 几何列定义。补：
- 5 张核心表的完整 DDL：asset（含 geometry(PointZ, 4490) 列与空间索引）、
  reading（create_hypertable 超表 + 分区与连续聚合策略）、warning、work_order、model_run
- 主外键、约束、索引设计及每个索引的理由
- ER 图（TikZ）
- 数据字典表（字段 / 类型 / 约束 / 单位 / 说明）
**这套 DDL 是后续 A8-2 实体类、S2 代码仓库、S3 数据集的唯一来源，必须先定死。**
载体要求：≥ 1 图 + ≥ 3 个代码清单（language=SQL，若 main.tex 未定义 SQL 语言则先定义）。
```

```
【工作包】A8-2 · 后端实现切片 ｜ 目标：chapter08.tex 正文净增 ≥ 3,500 字

【素材】L2 **section08-03.md、section08-04.md（智能预警算法，19块代码）**、section08-01.md（30块代码）

必须落地：
- **@Entity 实体类**（现在全章 0 个），与 A8-1 的 DDL 逐字段对应
- Repository、Service、@RestController 完整一条链
- **监测主线接口清单表**——现在唯一的接口清单（表8-19）只覆盖数字孪生预演切片
  （/scenarios、/model-runs、/impact-analyses），清源水库监测主线（测点、观测、
  预警、工单）一个 endpoint 都没定义。补：GET /assets、
  GET /assets/{id}/readings?from&to&agg、POST /warnings/{id}/ack、POST /work-orders 等
- Kafka 消费者与幂等去重
- 与第5章技术基线严格一致（Spring Boot 3.2+、Jakarta、Security 6）
载体要求：≥ 5 个代码清单 + ≥ 1 张接口清单表。
```

```
【工作包】A8-3 · 前端实现切片 ｜ 目标：chapter08.tex 正文净增 ≥ 3,000 字

【素材】L2 section08-01.md、section08-02.md 中的前端片段

必须落地：**一个完整的 Vue 3 单文件组件**（现在全章 0 行 Vue 代码）：
测点筛选 + ECharts 曲线 + 三维定位联动，与 A8-2 的接口一一对应；
配套的 API 层（复用第4章 A4-5 的 request.js 封装）、路由配置、Pinia 状态。
这正是实践题1"在两课时内实现 Vue 页面对 28 个测点的筛选、曲线和三维定位联动"
的参照实现——现在这道题在书里完全无从下手。
载体要求：≥ 4 个代码清单。
```

```
【工作包】A8-4 · 部署与运维 ｜ 目标：chapter08.tex 正文净增 ≥ 2,500 字

【素材】L2 **section08-05.md（运维监控体系，31块代码）**

必须落地：**docker-compose.yml**（前端 + Spring Boot + PostgreSQL/PostGIS/Timescale
+ Redis + Kafka）与 **Nginx 反代配置**——现在 8.6.1 只有一张 TikZ 部署图，
全书零部署配置，而 main.tex 白白定义了 YAML 和 Nginx 两种 lst 语言从未使用；
健康检查与探针、环境变量与密钥管理、备份与恢复演练步骤、监控告警配置。
这正是实践题4"用容器编排或等价环境部署前端、Spring Boot、PostgreSQL 和 Redis，
并提交健康检查与配置说明"的参照。
载体要求：≥ 4 个代码清单（用 language=YAML 与 language=Nginx）。
```

```
【工作包】A8-5 · 案例参数补全与公式修正 ｜ 目标：chapter08.tex 正文净增 ≥ 2,500 字

【素材】L2 section08-01.md（平台概述与参数）；参数需与第1、7章对齐

必须落地：
- **表8-1 补泄洪设施**：现在案例设定列了坝高、蓄水位、四类测点、网关、5 类角色，
  **根本没有闸门**，而 8.5.5 整节（第 507-556 行）讲闸门正算/反算，公式里的单孔宽度 b、
  开度 a、闸孔数、底高程全部无值可代，第 669 行又突然出现"清源水库为大坝、闸门、
  测点……分配稳定编码"。补一行如"泄洪设施：3 孔弧形闸门，单孔净宽 8.0 m，
  闸底高程 152.0 m，最大开度 6.0 m"。
- **补全部特征水位**：现在只有坝高 52 m 和正常蓄水位 168.0 m，缺坝顶高程、死水位、
  汛限水位、设计洪水位、校核洪水位、总库容、流域面积。没有这些，"水位是否超限"
  "要不要泄洪""蓝黄橙红怎么划"全部悬空，第 848 行"用三种降雨情景形成水位包络线"
  也无参照系。给一组自洽的教学设定（示例：流域面积 320 km²、总库容 0.85 亿 m³、
  坝基高程 120.0 m、坝顶高程 172.0 m、防浪墙顶 173.2 m、正常蓄水位 168.0 m、
  汛限水位 165.5 m、设计洪水位 170.2 m(P=1%)、校核洪水位 171.6 m(P=0.1%)、
  死水位 148.0 m），并核对与 52 m 坝高自洽。
- **修水量平衡式符号**（第 775-779 行）：ΣS_i + ΣΔV_k = ΣD_j + L + E。
  若按字面 ΔV = V末 - V初（蓄水为正），调蓄蓄水会使左端供给侧增大，方向恰好相反。
  必须把 ΔV_k 明确定义为"调蓄补水量（放水为正、蓄水为负）"，或移到右端改号。
  另 E 现在写的是"未满足需求或平衡误差"——这两个量业务含义完全相反：缺水量是枯水
  情景下合法的计算结果，平衡残差是数值错误必须为零。合成一个符号后，一个正常的
  枯水方案会被"误差超阈值不得进入审批"的规则挡掉。拆为 U（未满足需求）与
  ε（闭合残差），审批门槛只挂在 |ε| 上。
- **闸孔出流公式补适用条件**（第 511-515 行）：Q = C_d·b·a·√(2gH) 本身是标准的
  闸孔自由出流简化式，可用于教学，但 H 只说"有效水头"未指明是自闸底板起算的闸前
  总水头（含行近流速水头）；未给适用范围（一般 a/H < 0.65，超过即转堰流，公式失效）；
  未给 C_d 典型取值区间（弧形闸门约 0.55-0.75）；第 515 行提了淹没条件但没给淹没系数
  σ 的位置。补齐，并用上面补的清源水库参数给一个代入算例。
- **补 2 道计算题**：全章 3 个公式、16 道习题里 0 道计算题，公式沦为装饰。
  补：给定 3 孔闸门参数与上下游水位，反算达到 1200 m³/s 泄流的开度组合；
  给定一个调度时段的供水/需水/调蓄数据，校核水量平衡闭合差。
- 第 583 行"查询目标泄流 1200 m³/s 的闸门方案"用上面补的流域面积锚定其合理性。
- 补模型卡模板表（第 326 行只用一句话罗列 9 个字段，而 8.5 有 23 张表，
  唯独最该给模板的模型卡没有表；实践题3 要求学生写模型卡）。
- 第 253 行"事务外盒"改为"事务发件箱"（Transactional Outbox 的通行中译，
  "外盒"会让学生检索不到任何资料）。
- 第 419/583/1111 行 $T+24\,h$ 中的 h 会排成数学斜体变量，改 \mathrm{h}；
  1200\,m$^3$/s 统一为 $1200\,\mathrm{m^3/s}$。
载体要求：≥ 2 张表 + 全部新增图表被 \ref 引用。
本包完成后 chapter08.tex 应达到 26,000 字、≥ 22 个代码清单、≥ 14 图，门禁会验证。
```

## A2 系列 · 第2章软件工程基础（+15,273）

```
【工作包】A2-1 · 软件过程模型补全 ｜ 目标：chapter02.tex 正文净增 ≥ 3,500 字

【素材】L1 ch02 已删小节：软件生命周期模型 / 增量模型 / 敏捷迭代模型 / 其他模型简述 / 生命周期模型选择决策表 / 水利项目选型案例1水库安全监测系统 / 案例2智慧灌区管理平台（这批是本包主体，直接回收）；L2 section02-01.md、section02-02.md（5,722字）

必须落地：**螺旋模型补四象限图与水利风险迭代实例**——瀑布、原型、增量三个模型
各配一张 TikZ 图，螺旋模型只有 3 句话且无图，而它恰恰是最依赖图形理解的模型
（Boehm 的四象限：确定目标 → 风险分析 → 开发验证 → 规划下轮）。给一个水利场景的
风险迭代实例（如"闸门控制接口联调"作为高风险轮次）。
敏捷/Scrum/看板展开（现在也只有 3 句话），补 Sprint/Backlog 与需求基线共存的具体做法；
DevOps 与持续交付；模型选择决策表（项目特征 → 推荐模型）。
载体要求：≥ 2 图 + ≥ 1 张决策表。
```

```
【工作包】A2-2 · 需求获取与分析 ｜ 目标：chapter02.tex 正文净增 ≥ 4,000 字

【素材】L1 ch02 已删小节：需求分析的特点/原则/重要性/任务/方法、用户与干系方需求的获取方法、需求分类与优先级划分；L2 section02-03.md（3,724字）、section02-04.md

必须落地：访谈/问卷/观察/原型/文档分析各自的适用场景与典型坑；
用例规约模板（前置条件、主成功场景、扩展流、异常流、后置条件）并给清源灌区完整实例；
用户故事与验收准则（Given-When-Then）；非功能需求分类与量化方法。
补 §2.4.3"需求验证与冲突处理"——现在只有两句，是全章最薄的一节，而学习目标第3条
明确包含"验证"。给一个清源灌区的真实冲突实例（用水户要求即时批准 vs 调度要求
水量平衡校核），演示按业务价值/安全/合规排序的决策过程。
载体要求：≥ 1 图 + ≥ 2 张模板表。
```

```
【工作包】A2-3 · 结构化与面向对象分析 ｜ 目标：chapter02.tex 正文净增 ≥ 3,500 字

【素材】L1 ch02 已删小节：自顶向下逐层分解 / 结构化分析步骤；L2 section02-05.md（5,316字）

必须落地：DFD 分层完整（0 层/1 层/2 层与平衡规则）；ER 与范式；状态转换图；判定树。
**修表2.6 决策表的完备性缺陷**：三个条件共 8 种组合，现有 4 条规则覆盖
规则1=(是,是,是)→批准、规则2=(是,否,是)→方案调整、规则3=(否,—,—)→退回补充、
规则4=(是,是,否)→方案调整，**(是,否,否) 这一组合无任何规则覆盖**。
而习题11 要求学生"编写一张至少含3个条件、4条规则的配水审批决策表"——范例本身
就不完备，等于示范了错误。把规则2 的"渠道可用"改为"—"（水量不满足时渠道状态无关），
规则表即完备；并补一段决策表的完备性检查方法（2ⁿ 组合 vs 无关项合并），
这恰是决策表最核心的教学点，现在完全缺失。
另修第 256 行：正文写"从'完整性检查'退回'提交计划'"，但图2.4 中节点实际是
"资料完整？"与"提交用水计划"——正文与图的术语必须逐字一致。
载体要求：≥ 2 图 + ≥ 1 张完备决策表。
```

```
【工作包】A2-4 · 需求规格与管理 ｜ 目标：chapter02.tex 正文净增 ≥ 4,000 字

【素材】L2 section02-05.md、section02-06.md（L1 帮助有限，本包以新写为主）

必须落地：SRS 结构（对照 GB/T 9385 与 ISO/IEC/IEEE 29148——注意 O8 已把这两条
标为待核，本包按 O8 的结论写；若结论未出，先写通用结构并保留 TODO 注释）；
需求评审检查单；变更控制流程；追踪矩阵实操。
**修表2.5 数据字典两处技术表述**：
(a) startTime/endTime 的"单位"栏填 UTC+8——UTC+8 是时区不是单位，会误导学生。
    改为"单位"栏填"—"，在"说明与校验"栏写"ISO 8601，本地时区 UTC+8，
    与 endTime 构成左闭右开时段"。
(b) applicantId 字符串/18——18 位强烈暗示用居民身份证号作为用水户主键。教材直接
    示范用身份证号做业务外键，在个人信息保护语境下不妥。改为代理键并加提示。
(c) 第 374 行只有 requestedVolume 一行被 \small 包裹以强行塞进 2.9cm 列，
    付印后会明显小一号。把第一列宽从 p{2.9cm} 调到 p{3.4cm}（第四列相应减到 4.3cm，
    总宽仍在 16cm 版心内），删掉 \small。
本包完成后 chapter02.tex 应达到 20,000 字、≥ 7 图，门禁会验证。
```

## A1 系列 · 第1章概述（+8,641）

```
【工作包】A1-1 · 智慧水利发展与政策 ｜ 目标：chapter01.tex 正文净增 ≥ 3,000 字

【素材】L1 ch01 已删小节：智慧水利的定义与特征 / 发展背景与政策驱动 / 国内外发展现状与趋势；L2 docs/chapters/chapter01/section01-01.md（6,236字）

必须落地：智慧水利发展脉络（信息化 → 数字化 → 智慧化 → 数字孪生）；
政策体系梳理（**引用按 O8 的核对结论定稿，未出结论的保留 TODO 注释，不要自行断言**）；
"四预"首次出现处展开全称"预报、预警、预演、预案"（现在第 48 行直接用简称，
全称只在章末术语表出现）；国内外对比。
载体要求：≥ 1 图 + ≥ 1 张政策/标准对照表。
表1.2 补标准名称（现在只写"水利通信规约 & SL/T 651-2014"，没有标准名
《水文监测数据通信规约》，学生无法据此检索）。
```

```
【工作包】A1-2 · 平台形态与典型系统 ｜ 目标：chapter01.tex 正文净增 ≥ 3,000 字

【素材】L1 ch01 已删小节：四层架构概览；L2 section01-01.md、section01-02.md

必须落地：**流域级/工程级/区域级平台形态对比与选型场景**——现在完全没有，
而学习目标第1条要求学生理解"能力边界"；典型子系统构成；一个可读的完整业务实例。
载体要求：≥ 1 图 + ≥ 1 张形态对比表。
```

```
【工作包】A1-3 · 架构原则展开与生命周期 ｜ 目标：chapter01.tex 正文净增 ≥ 2,641 字

【素材】L1 ch01 已删小节：软件的基本概念 / 软件工程的定义与目标 / 软件工程知识体系 / 软件工程方法对智慧水利开发的指导；L2 section01-02.md（4,267字）、section01-03.md

必须落地：**§1.2.2 五条架构原则的展开**——现在每条只有一句话断言
（如"业务与数据一致。对象编码、单位、时间基准和质量码贯通各层"），
没有一个反例、没有一段代码、没有一张对比表，随后直接把读者推给第3-7章。
作为第1章唯一的架构方法内容，密度严重不足。至少给 2 条原则各配一个清源水库正反例：
"失败可见并可降级"配一张"网络中断 → 数据龄期标记 → 页面降级"的状态表；
"高风险操作受控"配一张"查询/模拟/建议/审批/执行"五级权限矩阵。
生命周期一节补对应习题——学习目标第4条"使用软件工程生命周期理解智慧水利平台的
建设与持续运行"现在 8 道习题中没有一道涉及。
**修**：第 77 行说平台接入"雨量、水位和闸门状态"，但第8章参数表原本没有闸门测点
（A8-5 已补），本包与之对齐，写明"清源水库设溢洪道弧形闸门3孔（详细参数见 8.1 节）"。
第 77 行"清源水库是全书使用的虚构教学工程"表述过宽（第2章通篇用的是清源灌区），
改为"清源水库是第1、7、8章使用的贯穿教学工程；第2章另用清源灌区示例"。
本包完成后 chapter01.tex 应达到 12,000 字、≥ 4 图，门禁会验证。
```

## A3 系列 · 第3章架构设计（+2,179，以修错为主）

```
【工作包】A3-1 · UML 规范补全与三图重绘 ｜ 目标：chapter03.tex 正文净增 ≥ 1,200 字

【素材】L2 section03-01…03-06（**section03-07 SafeHome 家庭安防案例不要回收**）

这是第3章最严重的问题：学生按图模仿会直接学到错误画法。

必须落地：
1. **UML 关系符号表**（现在第 120-126 行把泛化说成"带箭头的实线"——泛化是实线+
   空心三角，与关联导航性的开放箭头在图上完全不同；聚合/组合只给"强弱"的模糊说法，
   完全没给空心菱形/实心菱形这两个唯一可判读的符号；缺"实现"关系，而第 358 行
   恰有一个 Java interface 正需要它）。补一张三线表：泛化 实线+空心三角 /
   实现 虚线+空心三角 / 关联 实线（可加开放箭头表导航性）/ 依赖 虚线+开放箭头 /
   聚合 实线+空心菱形（菱形在整体端）/ 组合 实线+实心菱形。
2. **类图重绘**（第 133-138 行）：class 样式用了 align=left，它会设置 \raggedright，
   行尾 \rightskip = 0pt plus 1fil 与 \hrulefill 内部的 \hfill 平分剩余空间，
   **三条 compartment 分隔线只画到约一半宽度就断掉，UML 三分栏在视觉上不成立**
   （已实际编译复现）。把 6 处 \hrulefill 全部换成 \rule{\linewidth}{0.4pt}，
   或改用 shapes.multipart 的 rectangle split；去掉 rounded corners（UML 类框是直角）。
   关联现在用 -> 实心箭头，UML 关联的导航性用开放箭头，改 -{Stealth[open]} 或去掉箭头；
   多重性现在标在连线中部无法判断归属，移到两端 near start / near end；
   AlarmEvent 侧的 0..* 改 1..*（一个告警事件不可能由 0 条监测记录触发）。
3. **用例图重绘**（第 91、101 行）：边界矩形右边在 x=4.4cm，而"维护预警规则"椭圆
   （minimum width=2.4cm，位于 x=3.0）的右端实测落在 x≈4.68cm，**穿出边界约 2.8mm**。
   用例必须位于系统边界内是 UML 语义规则不是美观问题。边界右边界改 (5.2,2.0)
   或把 rule 移到 (2.6,0.2) 并把 manager 移到 (6.4,0.2)；标题 y 从 1.72 降到 1.62。
   另：值班人员画火柴人、工程管理人员画圆角矩形且无 «actor» 构造型，两者统一为火柴人。
   补一条 «include» 虚线（"确认告警事件" include "记录处置日志"）和一条 «extend»
   （第 78-82 行详细定义了包含、扩展、泛化，图 3-1 里一条都没有）。
4. **时序图重绘**（第 162、171-175 行）：五条消息全部是 [->, thick] 实线实心箭头。
   UML 中同步消息=实线+实心箭头、**异步消息=实线+开放箭头**、**返回消息=虚线+开放箭头**。
   第 172 行标着"异步推送"却画成同步，第 175 行"确认结果"是回复消息却画成实线实心。
   而正文第 162 行明说此图用于"核对构件责任、**同步与异步边界**以及异常分支"——
   图本身把这个边界抹平了。改：异步用 -{Stealth[open]}，返回用 dashed + -{Stealth[open]}，
   补执行规范条（激活条），并在图注补箭头样式对照说明。
   第 174 行的消息标签压在"消息服务"的生命线上，加 fill=white, inner sep=1pt。
5. **补一张告警事件状态图**（新建 → 已通知 → 已确认 → 处置中 → 已闭环/已误报，
   含超时升级转移）——第 12 行学习目标白纸黑字写"能够绘制用例图、类图、活动图、
   状态图和时序图"，但活动图与状态图正文各只有 3-4 行定义文字、无图例无实例，
   习题10 也只要求用例图/类图/时序图，这条教学链完全断开。状态图在本章第 931、
   963 行已反复提及"事件生命周期可追踪"，画出来零成本且能闭环。
   活动图可补一张"预警处置流程"泳道活动图，或退而求其次把学习目标中的"活动图"删去
   （**若选删，需在同章补等量文字，门禁会拦字数下降**）。

【改完必须实际编译并逐图目视核对】本章的三个图形缺陷在源码上都不显眼，只有编译出来
才看得见。请在提交说明中附上你目视核对的结论。
载体要求：3 图重绘 + 1 图新增 + 1 张符号表。
```

```
【工作包】A3-2 · 分类维度重写与全章口径统一 ｜ 目标：chapter03.tex 正文净增 ≥ 979 字

【素材】同上；ch03 第三轮只删了 533 字，本包以修错为主，回收帮助有限

必须落地（本包条目多，逐条做完再提交）：
1. **表3-2 分类维度**（第 504-516 行）：把分层、C/S、分布式并列为互斥的"架构类型"
   做选型对照——分层是逻辑结构风格、C/S 是交互/部署风格、分布式是物理部署风格，
   三者正交而非互斥（分布式系统的每个服务内部通常仍是分层的）。加一列"划分维度"，
   表下加一句"三者可组合，如'分层的微服务分布式部署'"；习题6 同步改为
   "说明三者分别属于哪一划分维度，举例说明它们如何在同一系统中共存"。
2. **第 621 vs 623 行自相矛盾**：621 让读者在 MVC 与微服务之间二选一，623 又说
   "每个微服务内部可能使用 MVC"。改为按三个正交决策维度重写：系统分解层面
   （单体/模块化单体/微服务）、模块内部组织层面（MVC 等）、跨模块通信层面
   （同步调用/事件驱动）。
3. **三套"四层"口径**：ch1 的感知—平台—应用—用户、第 326 行的业务—应用—服务—
   基础设施、图3-4 的表示—业务逻辑—数据访问—数据库。第 445 行声称在统一口径，
   却把读者指向了第三套（sec:hierarchical-abstraction）。把第 326 行改标题为
   "抽象层次的一种划分示例"并显式声明"本书后续讨论软件分层时统一采用
   图\ref{fig:layered-architecture} 的口径；第1章的四层为业务视角，不与本节混用"；
   第 445 行的 \ref 改指向 fig:layered-architecture。
4. **层次顺序颠倒**：第 326-328 行把业务层置于应用层之上，且第 379 行把"渗流异常
   识别策略"这种纯领域算法放进应用层。改为"应用层（编排用例）→ 领域/业务层
   （规则与策略）→ 基础设施层（存储、通信、设备驱动）"，删除含义含混的"服务层"
   （第 330 行说它管数据存储和网络通信，第 332 行又让它发短信预警，前后打架），
   把"渗流异常识别策略"归入业务层。
5. **新增 ADR 小节**：学习目标（第 16 行）、第 632 行、章末交付物（第 985 行）
   三次要求"架构决策记录"，但正文只有第 57 行一句话，没有定义、要素清单或模板，
   学生无法交付。补标准要素（编号、标题、状态、上下文、决策、备选方案、后果、
   关联需求、日期与责任人）和一个填好的水利实例（可直接复用第 772-789 行的
   ATAM 演练结论：告警链路选用持久化消息队列）。
6. **ATAM 补效用树与非风险点**（第 770-789 行）：ATAM 的核心产出是六项——架构方法
   文档化、效用树、风险点、非风险点、敏感点、权衡点。正文缺"效用树"（缺了它就没有
   "按重要性×难度排优先级"这一 ATAM 的标志性步骤）和"非风险点"。另外第 772 行场景
   里的"消息节点"是方案 B 才有的构件，方案 A（同步调用）根本没有消息节点，用它去
   判定 A"不满足"是循环论证——场景必须用与方案无关的质量属性响应度量表述，
   改为"任一处理节点在处理中崩溃时，已被系统确认接收的告警事件不丢失，
   恢复后仍能完成推送"。
7. **安防原案例语义残留**：第 746 行 Sensor 类的 detectEvent() 让传感器承担事件判定，
   与第 426 行"监测接入模块仅负责数据采集与传输，不参与预警判定逻辑"和第 641 行的
   职责划分正面冲突——改为 readLatestValue() 或 selfCheck()，事件判定移到分析服务。
   第 328 行"启动或停止安全监测"是家庭安防的布防/撤防语义，而第 216 行本章自己写了
   "系统需支持 24/7 运行"、第 915 行"汛期保持持续运行"——改为受控检修语义
   （pauseAcquisition(pointId, reason, until) / resumeAcquisition(pointId)，
   注明仅用于设备检修等受控场景，需授权与到期自动恢复，不中断整站采集）。
8. **子模块命名前后不一**：第 639 行定义"监测数据采集/异常分析/预警触发"，
   第 641 行就变成"事件分析/报警触发"，第 648 行还让"事件分析子模块"去存储原始
   采集数据（违反刚划定的职责边界）。全段统一为"异常分析/预警触发"，
   第 648 行改为"异常分析子模块需要定义滑动窗口、基线与阈值规则的内存数据结构，
   原始数据的持久化由数据存储构件负责"。
9. **术语/角色/技术栈按 AGENTS.md 第三节统一**：告警78次/预警76次/报警13次三词混用，
   其中第 947、961 行的小标题写"报警构件""报警接口"而正文全用"预警"；
   角色名五个变体统一为值班员/专业分析员/审批人/运维员；第 220、674 行推荐
   Python/Django/MySQL/Oracle，与第8章第 26 行的技术基线冲突且 ch08 第 128 行专门
   立了禁止技术栈漂移的纪律——改为本书统一基线并说明替换需走 ADR。
10. **性能指标三处统一**：第 37 行"秒级延迟"、第 216 行"响应时间需小于1秒"
    （未限定何种操作）、第 772 行"P95 ≤ 5 秒"，数量级不同且互相冲突。统一为一张表
    并注明"以下为本书案例的假定指标，实际项目须由第2章需求基线确定"：
    交互查询 P95 ≤ 1 s；告警生成（数据入站→事件产生）P95 ≤ 5 s；告警推送送达 P95 ≤ 10 s。
11. 删第 57 行悬空句"避免把'架构决策周期'误当作质量属性"（该词全书从未出现），
    改为正面表述；删第 526 行与第 536 行近乎逐字重复的 MVC 映射段（保留 536 行的案例段）；
    第 736 行 getMonitoringData() 统一为 readMonitoringData()（全章其余四处均为后者，
    而这两句恰恰出现在讲"命名一致性原则"的地方）。
12. 质量属性表与 ISO/IEC 25010 对齐：第 35 行引用 25010 后直接给出五项自定义集合
    （性能/可靠性/安全性/可维护性/扩展性），而"扩展性"不是 25010 的顶层特性。
    表前加一句说明对应关系，并补 25010 八项特性的完整枚举。
13. MVC 与事件驱动补"代价"：微服务小节标题是"优势与挑战"并给了挑战，
    但 MVC（第 528 行）与事件驱动（第 607 行）都只列优势，而习题2 要求"优缺点"。
    标题统一改"优势与代价"，MVC 补胖控制器/贫血模型/视图与模型耦合，
    事件驱动补最终一致性/事件模式演化/调试追踪成本/幂等与死信。
14. 补对第4-8章的 5 处前指（微服务→第5章、前端原型→第4章、三维订阅→第6/7章、
    ADR 与预警等级→第8章）；补核心术语表（第1章有，第3章术语密度更高却没有）；
    补耦合度量指标（扇入扇出、接口数量、版本联动次数、共同变更频率）与微服务划分
    原则（业务能力边界、限界上下文、变更频率差异、团队所有权）——习题1、12 现在
    超出正文支撑；编号体系统一（现在混用六种风格）；MVC 图补 User 参与者与正确数据流。
15. 代码清单补 caption/label 并增补至少 5 段（DTO 定义、分层间接口契约等），
    满足门禁的清单下限 6。
本包完成后 chapter03.tex 应达到 34,000 字、≥ 6 个代码清单、≥ 9 图，门禁会验证。
```

## A9 · 第9章结语（+2,323）

```
【工作包】A9-1 · 第9章补齐章末要件与重写两节 ｜ 目标：chapter09.tex 正文净增 ≥ 2,323 字

【素材】L1 ch09 已删小节：本章思考题与练习题（**这10道题第三轮删得对，是错位题，重编不要原样回收**）、致谢、截至2026年4月的政策与建设现状（时点表述，不要回收）

**决策已定：第9章保持编号章，补齐章末要件与前八章对称。**

必须落地：
1. 补学习目标、小结、3-5 道综合性思考题、"课程总结报告"章末交付物。
   思考题示例："结合 9.2.2，为一个偏远雨量站给出 LoRaWAN 与 NB-IoT 的选型论证。"
2. **重写 §9.2.3**（第 62-64 行）：现在整节是编者自述——"对于教材而言，第九章最重要
   的作用不是追逐每一项新技术的最新宣传口径，而是帮助读者建立三点判断……这样，
   第九章才能既保持前沿性，又不过度依赖容易过时的行业细节。"读者视角完全错位
   （教材在向读者解释自己为什么这么写）。改写为面向学生的《如何判断一项新技术
   是否值得投入》，落到可操作判据（是否有标准、是否有开源实现、是否有可复现基准、
   迁移成本）。
3. **重写 §9.3.2**（第 80-84 行）：§9.2.3 说"应优先回到需求、架构、数据、接口和
   运行机制这些相对稳定的基本问题"，紧接着 §9.3.2 就是一份纯名词清单——粒子群、
   遗传算法、CUDA、OpenMP、Transformer、Attention、知识图谱、Hadoop、Spark、Flink、
   Kafka Streams、Kubernetes、Docker Swarm、模型压缩/量化/容器化，三段共罗列 20 余个
   技术名词，无一给出选择依据、学习顺序或与本书章节的衔接关系，**正是它自己反对的
   写法**。改造为"能力—问题—技术"三列表（如"仿真提速 → 单机瓶颈在哪 → 先 OpenMP
   后 CUDA，判断依据是……"），每类只保留 1-2 个代表技术并说明取舍；
   **删掉 Docker Swarm**（生态已边缘化）。
4. §9.2.2 标题"云边端协同与感知网络"与内容不符——第 50-52 行全部内容只讲 LoRaWAN
   与 NB-IoT 两种低功耗广域网选型，完全没有云边端协同（该主题实际在第6章 6.4.13）。
   改名为"感知网络与低功耗广域接入"并加一句"云边端协同的分层部署详见 6.4.13 节"，
   或补两段边缘计算职责划分内容。
5. 章号体例：全章现在用中文数字（"第一至三章""第四、五、六、七章"），而前言与
   第1、2章一律用阿拉伯数字；更矛盾的是第 19 行同一句里"8.5节"又是阿拉伯。
   全文改阿拉伯数字。
6. §9.3 下四个小节全用 \subsection*（既无编号也不进目录，目录里 §9.3 会显得空无内容），
   改为编号 \subsection。
7. 第 72、80、82、84、88、96、106、108 行用 \textbf{...} 手工充当小标题
   （标题与正文之间只有一个空格、无标点、无换行），而 main.tex 第 305 行已定义
   \paragraph 的不编号小标题样式，全部改为 \paragraph{...}。
8. 口号式表达改为可核证表述：第 84 行"随着监测数据量的指数增长"→"当单站分钟级数据、
   视频流与三维瓦片同时入库时，单实例关系数据库在写入吞吐和历史查询上会先出现瓶颈"；
   第 96 行"智慧水利产业正处于高速发展阶段……需求旺盛"→"水利信息化岗位通常同时
   要求业务理解与工程实现能力"；第 60 行"随着业务复杂度提升"删去该句式直接陈述。
9. 第 91 行"定期阅读……规划与指导文件（通常每年更新）"——规划纲要按五年期编制，
   指导意见不定期发布，删除括注或改为"（发布频次不固定，建议按季度检索）"。
10. 第 80 行期刊推荐只有《Computer-Aided Civil and Infrastructure Engineering》
    （土木方向），补 2-3 种水利/水文主刊（《水利学报》《水科学进展》、
    Water Resources Research、Journal of Hydrology、Environmental Modelling & Software）。
11. §9.1（第 7-20 行）逐章复述内容，与前言第 22-45 行信息几乎重叠，只是把阿拉伯数字
    换成中文数字。改为"能力回顾"视角（学完后你现在能做什么、还不能做什么）。
12. 第 5 行使用 ASCII 直引号，改全角弯引号。
本包完成后 chapter09.tex 应达到 5,500 字，且门禁的章末要件检查通过。
```

## A0 · 前言收尾

```
【工作包】A0 · 前言扩写收尾 ｜ 目标：preface.tex 达到 ≥ 2,500 字

O7 已完成承诺修正与配套资源节的骨架。本包在 S1/S2/S3 建成后回填具体信息：
配套代码仓库的实际目录结构、数据集的文件清单与字段说明、附录A 的位置与使用方式、
环境版本清单的确切版本号。若 S 系列尚未完成，本包顺延。
```

---

# 批次 S · 配套资源（本轮新增）

## S3（排在 A8-1 之后做）

```
仓库：E:\2026\教材\智慧水利平台架构与开发

【开工前】读 AGENTS.md 第 6、7 条（技术基线锁定、工程参数全书唯一）；
读方案第七节的批次 S 说明；读 chapter08.tex 的 8.1 参数表与 A8-1 补的 DDL。

【工作包】S3 · 示例数据集

【任务】新建 companion/datasets/，含：
- stations.csv / stations.json：清源水库 28 个测点的元数据（编码如 DAM-A-PZ-07、
  类型、坐标、高程、量程、精度、阈值、投运日期），12 渗压 + 8 位移 + 3 库水位 + 5 雨量
- water_level.csv：≥ 1000 条水位观测序列，5 min 间隔，**必须包含缺测（null）
  与可疑值（超量程、跳变）**，供第7章实践题1 直接使用
- rainfall.csv、piezometer.csv：雨量与渗压样例
- warnings.json：告警事件样例（含蓝黄橙红四级与"未评估"态，与 O3 的质量码模型一致）
- generate.py：可复现的生成脚本，随机种子固定，注释说明每类异常是怎么造出来的
- README.md：字段说明、单位、时间基准（ISO 8601 / UTC+8）、许可

【硬指标】
- 所有数值必须与 8.1 参数表（A8-5 补全的特征水位、闸门参数）自洽：
  水位序列不得超出死水位 148.0 与校核洪水位 171.6 的物理范围（异常值除外且需标注）。
- 编码规则、字段名、单位与 A8-1 的 DDL 逐字段一致。
- 生成脚本可重复运行产出完全相同的数据。

【自检】python tools/check_textbook.py --build 全绿（本包不改 tex，字数应与基线相等）。
另外运行 python companion/datasets/generate.py 两次，diff 确认输出一致。
【收尾】追加《修改记录-第五轮.md》并 git commit，首行 "S3 示例数据集"。做完停下汇报。
```

## S2（排在 A8-4 之后做）

```
仓库：E:\2026\教材\智慧水利平台架构与开发

【开工前】读 AGENTS.md 第 6 条（技术基线锁定）；读 chapter04.tex、chapter05.tex、
chapter08.tex 的全部代码清单。

【工作包】S2 · 配套代码仓库

【任务】新建 companion/water-platform-demo/：
- frontend/：Vue 3.4 + Vite 5 + Pinia 2 + Vue Router 4 + ECharts + Three.js r160+
- backend/：Spring Boot 3.2 + Java 17 + Jakarta + JPA + Security 6 + Kafka
- db/：A8-1 的 DDL 与初始化脚本，含 TimescaleDB 与 PostGIS 扩展
- docker-compose.yml：A8-4 的编排（前端 + 后端 + PostgreSQL/PostGIS/Timescale
  + Redis + Kafka），含健康检查
- README.md：环境版本清单、一键启动步骤、常见问题

【最重要的硬指标】**教材里的代码必须是从这个工程里摘出来的，不是另写一套。**
逐一核对：第4章的 request.js、Vue SFC、Router/Pinia 配置；第5章的实体、Repository、
Controller、SecurityFilterChain、JwtAuthenticationFilter、Kafka 生产者与消费者；
第8章的 DDL、接口、Vue 页面。**凡是教材与工程不一致的，以工程为准修改教材**
（改教材时注意不得使字数低于基线）。核对结果逐条写进提交说明。

【硬指标】
- docker-compose up 后前后端可访问，健康检查通过。
- 数据库初始化后能加载 S3 的数据集。
- 教材中所有代码清单在本工程中都能找到对应位置。

【自检】python tools/check_textbook.py --build 全绿；docker compose config 校验通过。
【收尾】追加《修改记录-第五轮.md》，附教材↔工程的逐条核对结果；git commit，
首行 "S2 配套代码仓库"。做完停下汇报。
```

## S1（排在 B4 之后做）

```
仓库：E:\2026\教材\智慧水利平台架构与开发

【开工前】读 AGENTS.md；确认 B4 习题体系终检已完成（否则题号会变，答案会错位）。

【工作包】S1 · 附录A 习题参考答案

【任务】
1. 新建 output/appendix/answers.tex，由 main.tex 在 \backmatter 之前 \input，
   标题"附录A 习题参考答案"，需进目录。
2. 收录全书客观题（选择、判断）的答案与一句话解析。
3. 简答题与设计题给出**评分要点**（3-5 条得分点）而非标准答案——教材惯例，
   也避免学生照抄。
4. 实践题给出验收清单（做到哪几条算完成）。
5. preface.tex 的"配套资源"节据此改写，写明附录A 的位置与使用建议
   （建议教师在布置作业后再让学生查阅）。

【硬指标】
- 每一道题都要有条目，不得遗漏。逐章清点题号，与各章章末习题一一对应。
- 答案必须与正文一致：凡是答案与正文对不上的，说明正文有问题，在提交说明中列出，
  **不要改答案去迁就正文，也不要改正文去迁就答案**，先报出来。
- 附录不计入正文字数目标（门禁只统计 chapters/ 下的文件），但仍需编译通过。

【自检】python tools/check_textbook.py --build 全绿。
【收尾】追加《修改记录-第五轮.md》并 git commit，首行 "S1 附录A习题参考答案"。
做完停下汇报。
```

---

# 批次 B · 体例与终验

```
【B1 · 术语与体例统一】
按 AGENTS.md 第三节的对照表全书统一：预警/告警/报警三词、五个角色名变体、
三个贯穿案例名、章节引用的中文数字与阿拉伯数字、ASCII 直引号与全角弯引号、
手工 \textbf 小标题与 \paragraph、第3章的六种编号风格、"事务外盒"→"事务发件箱"。
每改一类先全书 grep 出全部位置，改完再 grep 确认为零。字数不得下降。
```

```
【B2 · 语言去规范腔】
"必须/不得/不能/应当"的密度：ch04 0.9%、ch05 2.6%、**ch07 4.4%、ch08 3.8%**。
第7、8章读起来像 SL/T 标准正文而非教材——只有"应该做什么"，缺"为什么"和"怎么做"。
把 ch07、ch08 中约三分之一的规范条文改为陈述性讲解 + 反例演示，并插入 2-3 个具体的
失败案例小故事（可虚构但要具体，例如"某站点因为把设备故障值当成真实水位，
在 3 月 12 日凌晨触发了 47 条误报，值班员从此关掉了推送"）。
第8章的否定式排比 15 处（"不是A，而是B"），保留 4-5 处最有力的，其余改直陈。
第7章第 388 行、第8章第 1075 行的小结几乎逐字复述各自引言，改为
"三条最容易踩的坑 + 本章最该记住的 5 个判断"。
**这一包最容易掉字数，改写后各文件字数必须仍不低于基线。**
仓库里有 humanizer-zh 技能可以辅助识别 AI 腔，但最终判断由你做。
```

```
【B3 · 第8章图表删并】
12 张 TikZ 图高度同构（全部是 4-6 个圆角框横向串联 + 一条虚线反馈弧，读到第 5 张
已能预测第 6 张）：删去至少 5 张，其中 fig:simulation-evidence 与 fig:ai-meeting-loop
信息高度重叠、fig:shift-handover 完全可由表格承载；保留的图改用不同视觉语法
（时序泳道图、状态机图、时间轴、拓扑图各一）。
11 张三列"字段/内容/要求"表结构完全相同（p{2.x}p{4.x}p{5.x}，5-7 行，第三列都是
"…要求/检查/复核"），合并同类项至少 4 张（如 tab:inundation-evidence 与
tab:simulation-labeling 合成"证据与标注要求"），并把其中 3-4 张改写成正文段落。
**删图删表不减字数**：被删图表的正文说明必须保留并改写为段落，字数不得低于基线。
```

```
【B4 · 习题体系终检】
逐章清点：题量、题型分布（客观/简答/实践）、每题与正文的对应位置、难度梯度。
重点补：第6章正文有带号计算与投影矩阵公式却无计算题；第7章重点讲 LTTB 却无
LTTB 实现题（补"实现 LTTB 并与等间隔抽样对比峰谷保留率"）、无无障碍与大屏适配题；
第8章 16 题中 0 道计算题（A8-5 已补 2 道，本包复核）；第4章客观题3 的正文支撑
（A4-5 已补，复核）；第5章实践题的测试要求与习题15 的撤销要求（A5-6/A5-9 已补，复核）。
第8章客观题4"Cesium 是工程级精细交互的唯一选择（判断）"——带"唯一"的判断题几乎
必然为假，属送分题，改为有区分度的表述。
**定稿题号，S1 依赖本包的结果。**
```

```
【B5 · 全书交叉引用与前后指终检】
核对每一处"详见第X章""见 X.Y 节"指向正确；核对所有 \ref 渲染出的编号与正文描述一致；
核对第6章 §6.4 与第8章 §8.5 的双向交叉引用（A6-5 建立）是否成对；
核对第1、7、8章的工程参数（28 测点、坝高 52 m、特征水位、闸门参数、编码规则）
在全书一致；核对第4、5、8章的技术基线版本号一致。
```

```
【B6 · 终验】
从干净中间状态执行完整四段编译（xelatex → biber → xelatex ×2）；
python tools/check_textbook.py --build 全绿；
逐章抽查渲染页面（每章至少 3 页），确认无裁切、重叠、越界、孤行寡行；
统计最终页数与正文字数并与 200,000 目标对照；
汇总《修改记录-第五轮.md》为一份终验报告，列出全部工作包的字数增量、
第四轮 11 项阻断的闭环证据、10 条待核事实的处理结论。
git commit + tag。
```

---

# 附：抽查清单（人工，每包做完花 5 分钟）

1. **有没有真去回收**：提交说明里必须写清回收了哪些段落、来源文件与小节名。
   如果它说"新写了 4,000 字"却一个来源都没列，多半是凭空编的——退回，让它先去
   `git show d8beab0:...` 和 `docs/chapters/` 里找。
2. **回收的技术细节更新了没有**：grep 一下有没有把旧写法搬进来——
   `grep -n "javax\.\|WebSecurityConfigurerAdapter\|authorizeRequests\|beforeDestroy\|Vue\.use\|outputEncoding\|readyPromise\|Chart\.js\|new Vue(" output/chapters/*.tex`
   正常情况应该只在"迁移说明"语境里出现。
3. **字数是不是真增了**：看提交说明里的 before→after，再自己跑一次 `--report`。
4. **代码能不能跑**：挑一段新代码贴进 IDE 或 curl 一下。特别是 A5-6 的 JWT 链、
   A6-1/A6-3 的 Three.js 与 Cesium 初始化、A7-4 的联动控制器——这三处是历史重灾区。
5. **文字有没有实质**：挑一节读一遍。出现"具有重要意义""为…提供了有力支撑"
   "随着…的不断发展"这类空转句，退回重写。
6. **有没有偷偷删东西**：`git diff --stat HEAD~1` 看有没有大段减号。
7. **门禁有没有被改**：`git diff HEAD~1 -- tools/check_textbook.py` 应该是空的。
