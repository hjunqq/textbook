# 第十一轮实际进度与迁移记录

计划见同目录 `PLAN.md`。本文件只记已经发生的事：改了什么、内容去了哪里、实际跑了哪些检查。未运行的检查写“未运行”，失败的保留原因。

## 状态总览（2026-09-21）

| 工作包 | 状态 | 说明 |
|---|---|---|
| R11-00 | 完成 | 接手核对、规则校准（决策 D-2026-09-21-8） |
| R11-01 | 8项均已修改；Java 相关项未能在本环境编译验证 | 见第二节 |
| R11-02 | 样章 + 补正小包完成：第5章主线统一到配套模型，5.3 精简，错误体合并 | 见第三节、第五节 |
| R11-03 | 第7章、第4章重编完成，经独立走读复核并修正 | 见第五节 |
| R11-04 | 第3章、第6章重编完成，经独立走读复核并修正 | 见第五节 |
| R11-05 | 完成：第8章 PZ-07 业务链；前言与第1、2、9章按真实课程能力重写 | 见第五、六节 |
| R11-06 | 完成第一遍：语言清理（5.6—5.9、6.3—6.4、8.5—8.6、附录C）、全书一致性核对、站点与 PDF 检查 | 见第七节 |

接手时核对：origin/master = 8b54678，origin/revision/undergraduate-r11 = d465437（仅 PLAN.md）。作者电脑上的工作目录检出的是 master，AGENTS.md 与仓库一致，未发现未提交的正文修订。本轮修改在云端克隆的修订分支上完成；该环境无推送权限，提交以 git bundle 和补丁交回，由作者拉入修订分支。

## 一、R11-00 规则校准

| 旧规则 | 性质 | 处理 |
|---|---|---|
| 各章正文不得低于第九轮字数基线 | 历史字数口径 | 改为提示 |
| 全书不超过240,000字 | 历史篇幅口径 | 改为提示 |
| 每章清单/图不少于定数；每1,200字一个载体 | 数量口径 | 改为提示，严格模式也不拦 |
| “宁可60行完整，不要20行片段” | 清单写法 | 改为：首次出现完整展示，后续只印变化部分并写明文件位置、入口与运行方法 |
| 悬空/重复/未引用 label、环境配对、文献、编译日志、改稿批注、章末要件 | 正确性 | 不变 |
| 单章一次减少超过1000字须先登记 `migration_ledger.json` | 无说明删除检查 | 不变 |
| `check_listings.py` 书中清单与配套文件一致 | 代码对应 | 不变，本轮新增8组 |
| `contract-check.mjs` 接口行为 | 接口行为 | 不变，新增 `--stage=lesson54` |

另修一处工具缺口：`check_textbook.py` 原来只认章文件里的 label，正文引用附录的表和节会被误判为悬空；现在附录的 label 计入“已定义”。

改动文件：`tools/check_textbook.py`、`AGENTS.md`（第一节、铁律1/2/5、第五节）、`DECISIONS.md`。

## 二、R11-01 逐项记录

| 编号 | 修改位置 | 做法 | 检查 |
|---|---|---|---|
| 01 | `index.md`、`docs/index.md` | 重写。九章目录与实际章名一致；克隆地址改为 `hjunqq/textbook`；删去“熟练掌握全栈”“Django/MySQL/K8s”等与书不符的内容；课程达成程度写成“读得懂、改得动、讲得清”；保留授权与生成图说明 | mkdocs 严格构建见第四节 |
| 02 | 第5章原清单 `lst:ch05-rest-layer`、`lst:ch05-read-only`，附录C `lst:ch05-cache-redis` | 三处都把“无读数”抛成404。服务层改为返回 `Optional`，控制器应答204；对象不存在才404。`lst:ch05-rest-layer` 在 R11-02 中换成配套工程的 `ReadingService` | `check_listings` 一致；教学接口契约27项通过；Java 未编译（见第四节） |
| 03 | 第3章3.1质量属性场景及表 `tab:ch03-quality-scenarios`、3.6 ATAM 演练 | 运行峰值统一为每秒10条（与3.5.2、第5章、附录A一致）。ATAM 演练保留每秒500条，但写明这是“区域平台设想”的压测负载，不是案例水库运行负载，并指向 ADR 的每秒200条重估条件 | 全书检索“条/秒”“每秒”已无矛盾 |
| 04 | 第8章清单8.2 的说明与标题 | 按清单实际能力重写说明；时间选择控件、曲线点击反向定位指向第7章 S5 的两个清单，可疑点差异显示改为练习。未给清单补功能，第8章重复实现问题留给 R11-05 | 人工对照清单逐句核对 |
| 05 | 第8章清单8.1 的说明与标题 | “水面起伏”改为“颜色动画”，写明顶点不动、与水动力计算无关，以及真正起伏和真实流态各需要什么 | 人工核对着色器代码 |
| 06 | 第5章5.7层次说明、章末交付物；前言表 `tab:preface-core-optional` | 异步概念（提交后事件、同步调用的故障传递，5.7引言与5.7.1）留在主线；Kafka 生产消费、幂等消费、重试死信、事务发件箱、分区顺序（5.7.2—5.7.6）列为选学。认证与基本授权仍在主线 | 前言与第5章口径一致 |
| 07 | 第3章 MVC、分布式架构、微服务三处 | 把“互不影响”“保证高可用高性能”改为写明成立条件：接口不变、服务无状态、瓶颈确在该服务、调用有超时与降级。MVC“案例分析”一段与前文示例重复，合并为图的引出句 | — |
| 08 | `tools/tex2site/convert.py` | 新增 `flatten_shortstack`：转换前把 `\shortstack` 各段首尾相接、合并相邻 `\texttt`，pandoc 不再把栈内换行当成表格行结束 | 见第四节对表8.3、表8.7生成结果的逐行核对 |

顺带处理的已证实技术错误（第5章与附录C）：讲解用实体的字段叫 `assetId`/`occurredAt`，访问方法和派生查询却写成 `getStationId`/`getMeasuredAt`/`findFirstByStationId…`。Spring Data 派生查询按实体属性名解析，这样的方法名启动即报 `PropertyReferenceException`；原文还说“重命名时编译器会提示错误”，也不对。已统一改名，并改正该句。

## 三、R11-02 第5章样章

### 顺序调整

| 原位置 | 内容 | 去向 | 处理 |
|---|---|---|---|
| 5.1 | 后端职责、请求链路图、HTTP 方法表、资源路径 | 5.1（新分5.1.1、5.1.2） | 保留并改写；新增一次应答的 JSON 及七个字段的水利含义；204与404的区别用案例说明 |
| 5.1 | 成熟的分层查询清单 `lst:ch05-rest-layer`、契约边界图、DTO 与依赖方向 | 新5.4.2“从一个类到三层” | 迁移；清单换成配套 `ReadingService.java`，同时解决 R11-01/02 |
| 5.1 | 写入控制器清单 `lst:ch05-rest-write` | 5.5.1 | 控制器部分与 `lst:ch05-crud-controller` 的 `create` 重复，删去；`CreateReadingRequest` 记录体（5.5各清单一直在用却从未定义）保留为短清单，连同写入顺序、BigDecimal 两段迁入 |
| 5.1 | 分页 URL 约定一段 | 5.4.5 派生查询与分页 | 迁移，并入202异步导出一句 |
| 5.1 | 游标分页、稳定排序两段 | — | 删除：与5.4.5末段及附录C“分页、游标与查询预算”重复 |
| 5.1 | 幂等键两段 | 5.5.4 | 与5.5.4“幂等请求与重试”重复，删除；“处置单状态迁移”“同键不同体应答冲突”两句并入5.5.4 |
| 5.1 | 错误响应字段一段（type/title/status/…） | — | 删除：与8.1契约 `{code, message, field?}` 及5.5.2不一致 |
| 5.1 | 服务发现、跨服务调用、API 版本化、健康检查四段 | 附录C新节“服务边界、接口版本与健康检查” | 迁移为选读；5.10节指路；`newman2021` 引文随迁到5.10指路句 |
| 5.1 | OpenAPI 文档一句 | 5.5.7 | 迁移 |
| 5.4.1 | “实体映射与 Repository 基础”开头两句 + 讲解用 `Reading` 实体 | 新5.4.1 + 5.4.2末尾 | 5.4.1改写为“把固定数据换成数据库查询”，用配套工程真实文件；原 `Reading` 实体保留，注明是5.4.3以后各小节的讲解模型 |

5.4 原5.4.2—5.4.14顺延为5.4.3—5.4.15，“本节层次”已同步；全书无其他按编号引用这些小节之处（已检索）。节号5.1—5.10不变，`lesson52`、`lesson56`、STAGES.md 中的节号无需改。

### 新增

- 5.2.2“读懂清单里的 Java 写法”：stream、lambda、`Optional`、`orElseThrow`、`record`，并给出等价的循环写法。
- 5.4.1：实体、Repository、控制器改动（只印变化部分）、连接配置、观测表复合主键与 BigDecimal、左闭右开时间窗的水利理由、运行记录表、故障练习、自测。
- 5.4.2：为什么分层（消息消费者也要用同样的查询）、服务层、控制器只做协议转换、反向试验（删 `existsById` 后404变204）、自测。
- 配套：`edu.example.lesson54.Lesson54Application`（S3 中点，只装配 qingyuan 包现有类，不复制业务代码）；`docker-compose.yml` 把 PostgreSQL 绑定到 `127.0.0.1:5432` 并加挂非 internal 的 `db-host` 网络（README 里的 psql 导入命令原先也连不上）；5.3.2节两个配置清单的库名、账号由 `water`/`water_app` 统一为配套工程的 `qingyuan`/`qingyuan_app`；`contract-check.mjs --stage=lesson54`；STAGES.md、MAPPING.md、README.md 同步。

### 删去的自我限定与口径句（第5章5.1—5.4）

两处重复的“进入本节所需知识”；“核心阅读按所列小节推进，实践成果按章末要求验收”；“字段一致允许复用页面，认证和数据能力齐备才允许替换整个服务”；“脚本分别检查各阶段已经实现的接口范围……另行联调”等。全书其余各节同类句子留给 R11-06 统一处理。

### 代表性修改前后对照

**对照一（5.1 开头）**

> 原：后端位于用户界面与数据资源之间，承担身份校验、业务计算、持久化、审计和系统集成。典型请求链路为“浏览器或设备网关—控制器—应用服务—Repository—数据库”。控制器只处理协议转换和输入校验，业务规则放在服务层，数据访问集中在Repository；若进一步拆分为微服务，还需显式管理边界、版本和分布式失败。

> 改：第4章的页面向`/api/assets`发出请求，拿到一段 JSON，再把它画成列表。应答这个请求的程序就是后端。它要做的事情比“返回数据”多：确认请求者是谁、有没有权限，检查参数是否合理，按业务规则读写数据库，留下审计记录，有时还要通知别的系统。……分层放在最后，是因为只有写过“全都挤在一个类里”的版本，才看得出每一层替你解决了什么麻烦。

**对照二（无读数的处理）**

> 原：查询结果为空时抛出领域可识别的异常，由统一异常处理器转换为404，客户端可以据此显示“暂无读数”或提示测站编号。

> 改：`latest`返回`Optional`：有观测就装着那条观测，没有就是空的。“没有观测”在这里是一种正常结果，不是异常；它对应 HTTP 的哪个状态码，服务层不关心，也不应该关心，因为调用它的不一定是 HTTP 请求。

**对照三（第3章 MVC）**

> 原：MVC 的主要优势在于其高可维护性和可扩展性。由于各部分相互独立，修改其中一个部分不会对其他部分产生直接影响。

> 改：MVC 的好处来自三部分之间约定好的接口。只要模型向视图提供的字段不变，调整监测总览界面的布局和配色就只涉及视图代码；一旦界面要多显示一个“质量码”，模型的查询、控制器的参数和视图就得一起改。

**对照四（第8章清单8.1）**

> 原：清单用它驱动水面起伏，每帧只更新这一个 uniform，不重建材质。

> 改：清单是片元着色器，它只改变每个像素的颜色……网格顶点没有移动，水面在几何上仍是一个平面；这种效果也与水动力计算无关，条纹的疏密和速度不代表波高或流速。

## 四、实际执行的检查（2026-09-21，云端 Linux 容器）

| 检查 | 结果 | 备注 |
|---|---|---|
| `python3 tools/check_textbook.py --strict --build` | 通过 | xelatex→biber→xelatex×2；日志无 Error、Overfull、缺字、未定义引用；410页。本环境无思源宋体，中文回退到 Fandol，页数与作者本机（约400页）不可比，**版式与页数须在作者本机复核** |
| `python3 tools/check_listings.py` | 31组一致，0组不一致 | 新增8组：第5章5.4.1/5.4.2的7个清单与 `application.yml` 片段 |
| `python3 tools/audit_learning_path.py` | errors 为空；核心节对拓展节引用 0 | 输出目录未入库 |
| `node teaching-api/contract-check.mjs … --stage=teaching` | 27项通过，0失败 | 对教学接口；脚本新增的 `lesson54` 分支只做了语法检查，未对真实后端运行 |
| 前端 `npm ci && npm test` | 11个文件112项通过 | |
| 后端 `mvn test`、`Lesson52/54Application` 启动、`--stage=lesson52/lesson54/full` | **未运行** | 出口策略拦截 Maven Central（403），依赖无法下载；本环境也没有 Docker。`Lesson54Application` 与 compose 网络改动只经过代码走读（含一次独立复核），需作者本机验证 |
| `tex2site/convert.py` → `build_tikz.py` → `convert.py` | 94个 SVG 校验通过 | 只提交了编号变化的图5.2/5.3；其余 SVG 因本环境 poppler 版本不同而逐字节不同，未提交，保持仓库原件 |
| `mkdocs build --strict -f mkdocs-ci.yml` | 通过 | |
| 表8.3、表8.7 网页生成结果 | 逐行核对通过 | 10条接口路径完整（如 `POST /api/work-orders/{id}/complete`），枚举 `NONE/BLUE/YELLOW/ORANGE/RED` 在一格内 |
| PDF 页面目检 | 只看了5.4.1开头两页 | 清单、交叉引用、缩进正常 |
| 浏览器检查站点 | 未运行 | |
| 编辑走读 | 5.1—5.4.2 由另一轮独立走读复核，采纳其23条意见（含下列实质性问题） | 不是学生试读 |
| 学生试读/试教 | 未进行 | |

独立复核发现并已改正的实质性问题：compose 中 PostgreSQL 只挂在 internal 网络，端口映射不会生效（已加挂 `db-host` 网络）；运行记录表里“最近一小时”的时间窗只在数据卷创建后30分钟内成立（改为宽时间窗并在 STAGES.md 说明）；`UPDATE active=false` 练习没有给执行方法和恢复步骤（已补）；“double 会把185.091变成185.0909…”的说法不准确（改为 numeric 列与累加比较误差）；“加号被浏览器当作空格”不准确（是服务端按 URL 规则解码）；`record` 自 Java 16 起而非17；契约边界图中的422未在正文引入（删去）。

## 五、第二批（2026-09-22）：R11-02 补正、R11-03、R11-04、R11-05（第8章）

### 5.1 R11-02 补正小包（作者 2026-09-21 决定）

四项决定的落点：(1) 主线统一到配套模型——5.3.3、5.4.1—5.4.7、5.5 全节、5.7.3、5.9.1 的清单均取自 `edu.example.qingyuan` 或 `db/001_init.sql`；(2) 自增主键 `Reading` 及其 Repository/CRUD 控制器/命令服务、`StationEntity` 关联清单、隔离测试清单删除，N+1、传播与隔离、执行计划、增量统计压为 5.4.8—5.4.11 选读；(3) `lst:ch05-exception-handler`（ProblemDetail）与 `lst:ch05-problem-advice` 合并为 `lst:ch05-error-handler`，取自配套 `ApiExceptionHandler.java`，ProblemDetail 只留三句对比；(4) 5.4.4 讲订正即追加版本，5.4.6 用预警状态条件更新讲并发冲突（影响行数0→409），`@Version` 简述，表 `tab:ch05-two-versions` 并列两个“版本”。正文已无对观测的 PUT 覆盖与 DELETE。

六项具体问题：A 5.3 改为四小节（起步依赖／连接配置／构造器注入／选读），用 `AssetController←AssetRepository/ReadingService` 讲注入，`JwtProperties` 移 5.6，测试切片移 5.9；B 起步依赖清单改为配套 `pom.xml` 3.2.10 的 BOM 导入片段并登记 PAIRS，说明与继承 parent 的异同；C `@Bean(destroyMethod="close")` 用在 `ExecutorService` 上在 Java 17 会启动失败（`close()` 自 Java 19 起），该清单不再承担 DI 教学而删除，5.3.4 一句写明正确写法 `shutdown`；D 5.4.2 改为“控制器负责协议转换，并可直接用 Repository 做不含规则的单次存在性查询；含规则、会被消息消费者复用的查询与写入放服务层”，与 `existsById` 一致，自测同步；E “先照写”“不要混淆”“讲解用的模型”等限定语通过统一实现消除，`readOnly` 首次出现当场解释；F 学习目标第5条、引言（不再写“经Kafka削峰”）、tipbox、5.7 引言与层次、小结、交付物、客观题3/5/6、简答10、实践题及附录A答案3/5/6/7/9/10/12/13同步，Kafka 配置清单移出核心小节。

新登记 PAIRS 7组（pom、ReadingEvent、ReadingService.accept、001_init.sql、ApiExceptionHandler、ReadingConsumer、ReadingWindowTest）。第5章字数 32469→33120，未减少。

补正中发现、未改 Java、由作者定的配套疑点：① `ApiExceptionHandler` 的 `Exception.class` 兜底可能先于 `accessDeniedHandler` 接住 `AccessDeniedException`，把 403 翻成 500（当前三个账号对查询接口都有权限，触发不到；第8章加 DUTY 专属端点后会暴露；5.9.2 写成条件式失败练习）；② `JpaRepository.save` 对已有主键走 merge，`accept` 在“主键相同、eventId 不同”时会更新原行而非报冲突（5.4.4 如实写出并给出 `INSERT … ON CONFLICT DO NOTHING` 做法）；③ `existsByEventId` 用不上 `(occurred_at,event_id)` 索引前导列（5.4.10 作为 EXPLAIN 练习）；④ 5.6 权限模型（`WaterSystemPermission`、刷新令牌）与配套（DUTY/ANALYST/OPS，无刷新端点）仍是两套，留 R11-06；⑤ 契约行 `GET/PUT /api/readings/{id}` 依赖 `reading_id`，配套实体未映射，补录与订正接口配套未实现。

### 5.2 各章顺序与迁移（详表见各章工作记录，此处只记结构与去向）

**第7章（R11-03）** 四节不变。7.1 六小节压为五：7.1.1 一条观测记录长什么样（合并旧7.1.1+7.1.6，新增三条真实 JSON）、7.1.2 质量码与缺测（前提）；旧7.1.2 时间窗口与 LTTB 跨节后移为 7.2.6。7.2 新增 7.2.1 第一条真实观测曲线（`lst:ch07-first-curve` 节选自 `lesson74/main.js` 与 `series-controller.js`，配故障练习）；旧7.2.1 选型→7.2.3；渲染/性能→7.2.7；专题地图→7.2.8；色彩→7.2.9。7.3 LOD 移到节末；7.4 触控与信息面板互换。LTTB 原理、公式（补叉积推导）、图、清单保留，新增“为什么适合监测曲线／什么时候不能用（预警判定、统计、审计）”。删除：`lst:ch07-chart`（与登记清单 append-data 重复）、`lst:ch07-visual-encoding`（与色板/专题层/新 suspect-symbol 重复）、`lst:ch07-pixels-to-world`（重写前一清单）；迁附录C：图表运行期预算/缓存/状态恢复（`app:ext-ch07-chart-runtime`）、颜色令牌与验收矩阵（`app:ext-ch07-color-tokens`）。改正：`tab:ch7-view-contract` 列了接口不返回的 `stateVersion`/`source`；“三千多万米”应为三千九百万米；渗压采样周期与数据集（5 min）不符处写明为讨论设定。字数 22606→19026。

**第4章（R11-03）** 八节不变。4.2 拆为三小节（文档流／表单与原生校验／键盘路径）；4.3 重排为盒模型→单位→Flex→Grid→断点→Flex 故障定位（指导）→层叠上下文（拓展）→大屏与暗色（拓展，样式迁附录C）；4.4 节首新增“从已学语言到 JavaScript”与表 `tab:ch04-js-bridge`；4.5 保持结构，补 Promise/async 白话解释，4.5.7/4.5.8 压缩；4.6 五个 subsubsection 取消并入；4.7 入口清单前移，阅读顺序 main.js→App.vue→路由→登录；4.8.3 部署迁附录C。删除的重复副本：第三份 login+fetch 封装 `lst:ch04-a49-auth-client`、ES 模块重复清单 `lst:ch04-js-lifecycle`、第二份完整 `defineConfig`、`lst:ch04-a48-env` 中的第四份 fetch、Flex/Grid 两个完整 HTML 页面只印 style 与 body、筛选页完整 SFC 只印相对 4.6.1/4.6.2 的改动、`fig:ch04-a46-lifecycle-cleanup`。迁附录C：`app:ext-fe-focus-list`（焦点管理、虚拟列表）、`app:ext-fe-theme`、`app:ext-fe-auth`、`app:ext-fe-release`。改正的技术错误 8 处：`lst:ch04-a44-modules` 未定义变量 `rawLevel`/`value`；`build.target es2020` 与顶层 await 冲突→es2022；`VITE_API_BASE` 与 request.js 读的 `VITE_API_ORIGIN` 不一致、会拼成 `/api/api`；路由清单导入路径 `./` 应为 `../`；筛选页用了契约里没有的 `asset.warning`/`asset.value`；main.js 归属 4.5.4 而非 4.5.5；“返回422”契约无此码；Pinia 方法名 `loadReadings` 应为 `loadLatest`。字数 30265→22718。

**第3章（R11-04）** 六节不变。3.1 五小节：需求与用例／系统边界／把需求分给模块（新）／质量属性场景／UML；3.2 架构类型三段式合并为“三个不同的问题”，MVC 四段，原型三段；3.3 重写为两类接口／走查“查询 PZ-07 最新观测”（表 `tab:ch03-walk-latest`）／走查“渗压超阈值产生预警”（表 `tab:ch03-walk-warning`）／接口设计经验；3.4 按变化来源划分／抽象与信息隐藏／新增一类传感器要改哪里／内聚耦合分级（拓展）；3.5 `sec:ch03-load-estimate` 原样，微服务与事件驱动改为“回答什么问题—何时值得—代价”；3.6 ADR 升为核心，评估方法与 90 分钟演练互换并标拓展。新增图 `fig:ch03-module-flow` 与六张表。删除：架构重要性长段、UML 逐条定义、“架构决策核心要素”五段、SafeHome 式非水利示例（GUI 控件、文本编辑器）、原型的问卷/小组讨论、构件协作三遍叙述、复杂度与风险泛论；迁附录C：基于构件的设计与复用（`app:ext-component-based-design`）。改正：`lst:ch03-monitoring-dto` 缺 `unit` 且字段名不符契约；`lst:ch03-controller` 无法表达 204；`lst:ch03-usecase-service` 每条入库都发异常事件；“执行计划见5.7节”指错。新增练习第13题（走查“确认黄色预警”），附录A已补答案。字数 35643→23478。

**第6章（R11-04）** 四节不变。6.1：首个场景（不动）→ 6.1.2 用几何体搭出坝体（新）→ 6.1.3 坐标变换与透视投影（补齐次坐标、M=TRS、V、P、透视除法）→ 6.1.4 加载现成模型（加单位/轴向/基面检查）→ 6.1.5 测点绑定（不动）→ 6.1.6 拓展：管线、能力探测、LOD 与实例化。6.2：CGCS2000→高程基准→新 6.2.3 局部原点、轴向换算与测点重新定位（含 `Math.fround` 实测）→OGC 服务→Cesium。6.3 公式顺序理顺；6.4 保留全部 `sec:ch06-twin-*` 标签，6.4.3 压缩，6.4.18“发展重点”撤掉。删除第二套 Three.js 骨架 `lst:ch06-three-minimal`；迁附录C：GeoServer 发布与缓存（`app:ext-ch06-gis-ops`）、坐标成果审计（`app:ext-ch06-crs-audit`）、倾斜摄影外业与空三检核（`app:ext-ch06-photogrammetry`）。改正：`lst:ch06-local-origin` 的 `z = north − origin` 镜像错误（应为 `−(north − origin)`，与 bind-assets.js 和第7章一致）；`lst:ch06-proj4-convert` 说“往返”却无反算；`DAM-001` 等编码不符 8.1；`stations.csv` 应为 `stations.json`。新增练习第18、19题，附录A已补答案。字数 30755→25734。作者待定：6.1.2 教学断面尺寸（顶宽8/底宽40/坝长160 m）是否进参数表；6.2.3 新写“坝轴线桩号”一段，数据集无桩号字段；数据集把28测点沿约4 km 斜线排开，与“埋在坝体里”不自洽；配套无 GLB，6.1.4 让学生自备。

**第8章（R11-05）** 六节不变，8.1 三张唯一来源表保留（契约表 readings 行按实际返回补 `assetId`）。章首改为 S6 三入口说明；8.1.3 末“PZ-07 六问”；8.2.1 新表 `tab:ch08-chain-modules`（每步用哪一章成果、本章加什么、配套入口）；8.2.3 指向 S5 页与 `MonitoringDashboard.vue`，`lst:ch08-monitoring-sfc` 删除；8.3 重排为 8.3.1 数据模型→8.3.2 质量检查→8.3.3 关系模型（DDL 与 `001_init.sql` 逐字一致并登记）→8.3.4 业务链 SQL→8.3.5 后端（工单/预警实体、条件更新 `transit`/`completeIfInProgress`、四个端点含新增 `GET /api/warnings`、409/404 映射）→8.3.6 前端 `api/warnings.js`→8.3.7 物理设计要点（拓展）→8.3.8；8.4.1 定级（`lst:ch08-classify-js` 节选自配套并登记）、8.4.2 七步走查为核心，8.4.3 拓展；闸门泄流与水量平衡计算题移到 8.5.5/8.5.11 公式之后；8.5 授权段与六幅截图图注与 HEAD 逐字节一致（已 diff 复核）；8.6 保留 compose/secrets/nginx，加 `smoke.sh` 步骤与口令失败例。删除与第4/5/7章重复的 Vue store/router/scene-bridge/entry 清单、实体与 Kafka 消费者清单、旧8.3.7 后半约60行要求堆叠、哈希分区说法（DDL 中不存在）；迁附录C：运维 SQL 17段、连续聚合与保留、告警规则与备份演练（`sec:appc-ch08-ops`）。改正：控制器调用不存在的 `service.start`、契约无 `/start` 端点（工单默认 `in_progress`）；预警状态集缺 `assigned`；旧“确认”非条件更新且会 500；`hasRole('DUTY_OFFICER')` 与配套 `DUTY` 不符；`Double score` 在 validate 下被拒→`BigDecimal`；公式先用后给。配套 `db/001_init.sql` 追加 `source_event_id` 列、状态 CHECK、索引、`work_order`、`model_run`（均可重复执行，**未在 PostgreSQL 上执行**）。字数 41736→28986。作者待定：`closeloop-check.mjs` 期望缺字段码 `FIELD_REQUIRED` 而配套 `@Valid` 失败返回 `VALIDATION_ERROR`，正文写为故障练习，是否改处理器或脚本。

### 5.3 独立走读复核

两轮走读（第4/7章一轮，第3/6/8章一轮）共 34 条意见，全部处理。其中实质性错误：第7章声称 `tests/lesson74.test.js` 保存坐标/相机参数（不实）；第4章 4.7.1 让学生整体替换路由表会删掉后续章节依赖的 `/monitoring`，且引用不存在的组件；4.3 的观察结果在给定 HTML 骨架上看不到；4.2.2 有 `novalidate` 却无脚本；第8章正文声称 `001_init.sql` 已含 `source_event_id`、`work_order`（原先没有）；`GET /api/warnings` 未实现导致闭环脚本在第4项停下；第3章“确认预警”在模块表、接口表、图和走查表里归属不一致；第6章“r156 起内置 addons 映射”应为 r144；若干字面案例参数改为 `case-params.tex` 宏。

### 5.4 检查（本批）

| 检查 | 结果 |
|---|---|
| `check_textbook.py --strict --build` | 通过；见下方编译记录 |
| `check_listings.py` | 42 组一致，0 不一致（本批新增 11 组） |
| `audit_learning_path.py` | errors 空，核心引用拓展 0 |
| 前端 vitest（lesson44/45/71/74、series-controller、window-chart、lesson84 等） | 走读代理实测通过（112 项全套上一批已跑；本批抽跑 lesson74/series-controller 18 项、lesson84 28 项） |
| 教学接口：七步 curl、`closeloop-check.mjs` | 20 项通过（第8章代理实测） |
| 后端 `mvn test`、lesson54 启动、`--stage=lesson54` | 本环境未运行（Maven Central 403，无 Docker）；**已由 CI 在 dcc0ec8 上通过**，见第六节 6.3。作业定义：`.github/workflows/ci.yml` 的 `stage-lesson54`：Java 17、GitHub Actions 服务容器 `timescale/timescaledb-ha:pg16`（一次性、随作业销毁，不触碰任何已有数据卷），执行 `mvn -q test`→psql 执行 001/002 脚本→启动 `Lesson54Application`→`--stage=lesson54`→两项运行记录表观察，全部日志与退出码作为 artifact `stage-lesson54-logs` 保留；`on.push` 增加 `revision/**`，推送修订分支即触发。本环境无 `gh` 且无推送权限，触发操作：作者推送后在 Actions 页查看，或手动 `workflow_dispatch` |
| `001_init.sql` 新增段 | 未执行；`stage-lesson54` 与 `stack-e2e` 作业会执行 |
| tex2site + mkdocs 严格构建 | 见编译记录 |
| 学生试读 | 未进行 |

编译记录（云端容器，Ubuntu，TeX Live 2024，xelatex；中文字体回退 FandolSong/FandolHei，非作者本机的思源字体；总页数因此**不可与本机比较**，只用于错误与 Overfull 检查）：第一次全书编译 388 页，Overfull 17 处（第5章 pom 清单长行 4 处、长 `	exttt` 12 处、附录1处），已用 `breakatwhitespace=false`/`llowbreak` 处理后重编译，结果见提交说明。

### 5.5 遗留与待作者决定

1. R11-05 剩余：第1、2、9章及前言（学时方案按达成程度、v0—v5 与 S0—S6 映射表、“不跳章”与按编号跳读的矛盾）未做。
2. R11-06 未做：全书“本节层次/进入本节所需知识”统一、6.4 与 5.6 中残留的“应……应……”句、术语与习题答案全查、站点浏览器检查。
3. 5.6 权限模型与配套两套并存（见 5.1 ⑤）。
4. 上述“作者待定”各项。
5. 编辑走读不等于学生试教；无任何学生试读。

## 六、第三批（2026-09-22）：R11-05 前言与第1、2、9章；CI 结果回填

### 6.1 结构与去向

**前言**：“学习方法”改为“怎样读这本书”，只留一条阅读规则（按章顺序读核心与指导实践，拓展在完成对应阶段后再读），删去“不建议跳章”与“按编号跳读”的矛盾；新增表 `tab:preface-version-stage`（v0—v5 ↔ S0—S6 ↔ 章节 ↔ 配套入口 ↔ 能力，含 S3 起点/中点/终点）；课程目标改为与 docs/index.md 一致的四条能力；技术篇四条与第4—7章现状对齐，应用篇改为 PZ-07 业务链、8.5 独立选读；三个学时方案改为按达成程度编制（32学时到 S3 中点：2+4+4+9+11+2；48学时到 S5：2+4+3+10+13+6+6+2+2；56学时到 S6 与部署，讲授:实验≈30:26），`tab:preface-core-optional` 六行按各章现行层次重核；配套资源段的文件名与 STAGES/MAPPING 一致。

**第1章**：1.1 八小节压为五（定义／政策主线与发展脉络（合并旧1.1.2、1.1.4、1.1.5，引文全部保留）／感知通信（升为核心）／智能边界／贯穿场景（补黄色以上人工确认、模拟建议不驱动闸门、suspect/missing 不参与评估，与第8章一致））；1.1.6 无出处的国内外路径对照删除；1.2.1 增加与 S0 实录五次请求、四种失败及 `tab:ch03-walk-latest` 的对应；1.2.4 的洪水链复述改为引用 1.1.5 的图并只留子系统边界结论；1.2.5 每条原则改为“解决什么问题—正例—反例—落到哪一章”；1.3 改为“为什么水利平台需要软件工程”+指路第2章，`fig:sdlc-flow` 与雨量测点例迁第2章2.1；1.2.4/1.2.5 的评审与治理段迁附录C（`app:ext-ch01-platform-review`）。字数 14189→10158。

**第2章**：2.1 五小节合为整体流程；2.2 保留瀑布/原型/迭代增量/敏捷/模型选择，螺旋、Scrum、看板、DevOps 压为 2.2.6 拓展；2.3.2+2.3.3 合并；2.6 改为四小节（从含糊陈述到验收条件／评审检查单／拓展：变更控制与追踪矩阵／方法迁移，并与 `tab:ch03-req-mon` 衔接，预警状态改为第8章实际的四态）；2.2.9/2.6.2 的评审记录与基线治理迁附录C（`app:ext-ch02-baseline-governance`）。第1章原练习9、10移为第2章13、14，答案随迁。字数 23175→18634。

**第9章**：9.1 按四条能力回顾并明确未涉及内容；O 表引用改正（ADR 在 3.6.1）；9.2.3 升为核心；新增练习6、7（O1—O7 自查、故障记录改写），附录A补答案。字数 6022→5648。

### 6.2 独立走读复核

一轮走读 21 条，全部处理。实质性问题：1.1.3 标为拓展却被学习目标/交付物/习题依赖（升为核心）；第9章全部习题依赖拓展小节（9.2.3 升核心并补两题）；前言 S2 行与第4章层次不一致（三处统一为 4.6.1—4.6.2 核心）；48学时表第4/5章学时与覆盖范围不匹配（改为10/13）；答案第1章第3题按四层名称重写；术语表“质量码”误含“修正”。

### 6.3 CI 结果（运行 35681402744，提交 dcc0ec8，2026-09-22 02:58Z 起）

| 作业 | 结果 |
|---|---|
| docker compose 配置校验 | 通过 |
| 前端测试与构建 | 通过 |
| 后端测试（`mvn -B -q test`） | 通过 |
| 在线版严格构建 | 通过 |
| 书中清单与配套代码一致 | 通过 |
| 教学接口契约与第8章闭环 | 通过 |
| S3 起点可启动且契约一致（lesson52） | 通过 |
| **S3 中点（lesson54）：mvn test → 001/002 建库 → 启动 Lesson54Application → `--stage=lesson54` → 运行记录表两项观察** | **通过（1 m 16 s）**；日志与退出码在 artifact `stage-lesson54-logs` |
| 整栈端到端（compose + smoke） | **失败**（exit 1，56 s） |

`stack-e2e` 的失败不是本轮引入：master 8b54678 上的运行 35567664778（第九轮末）同一作业已失败（58 s）。本环境无权读取作业日志，未能定位原因；从时长看在 `docker compose up --build --wait` 阶段即失败。本轮对 compose 的改动（PostgreSQL 回环端口与 `db-host` 网络）和 `001_init.sql` 追加段已由 `stage-lesson54`（同一镜像、同一脚本）证明可执行，但 compose 整栈仍待作者提供日志或本机复现。

据此，第四节中“未运行”的 `mvn test`、`Lesson54Application` 启动、`--stage=lesson54`、`001_init.sql` 新增段四项改记为 **CI 通过**；`--stage=full` 与 `smoke.sh` 仍为待核。

### 6.4 本批检查

`check_textbook.py --strict --build` 通过（386 页，Fandol 回退字体，Overfull 0）；`check_listings.py` 42 组一致；`audit_learning_path.py` errors 空；tex2site + mkdocs 严格构建通过；`migration_ledger.json` 登记 chapter01 4200、chapter02 4700 随本包提交，下一提交清空。

### 6.5 遗留

1. R11-06 未做：全书“本节层次/进入本节所需知识”统一、5.6/6.4 残留“应……应……”句、术语与习题答案全查、站点浏览器检查、PDF 逐章目检。
2. `stack-e2e` 失败原因待作者日志。
3. 上批列出的“作者待定”各项未变。

## 七、第四批（2026-09-22）：R11-06 全书语言、一致性与发布同步

### 7.1 语言清理（本轮此前未重写的部分）
范围：第5章 5.6（全节）、5.7（只改语言）、5.8、5.9；第6章 6.3、6.4（6.4.1—6.4.17 逐段）；第8章 8.5（授权段与六幅截图图注逐字未动）、8.6；附录C 全文。做法：把“应……应……”要求堆叠和面向审稿人的口径句改为直陈；概念首次出现补白话解释（JWT、过滤器链、CSRF、CORS、jti、令牌撤销与轮换、分区/偏移量/消费者组、死信主题、事务发件箱、孪生体、数据血缘、模型卡、连接池、Actuator、MDC、WAL、RPO、游标等）；与前文重复的 11 段删除或合并（去向见 5.6、8.5.15、附录C 运维练习各处，已在提交内登记）。5.6 开头新增两段如实说明：配套实现的是三角色最小版本（`SecurityConfig`、`JwtService`、`JwtAuthenticationFilter`、`AuthController`、`lesson56/RefreshTokenVerifier`），正文后半的细粒度权限、刷新与撤销是其上的扩展写法，配套未实现——权限模型是否统一仍待作者决定。角色名统一为值班员/专业分析员/审批人/运维员（6.4、8.1、8.5 共 7 处）。附录C “28 个测点”改为 `\cpStationCount`。

### 7.2 全书一致性核对
习题与附录A答案逐章数量、题号、题型一致（第6章第19题答案指向的检查项改正；第8章第12题答案的 Markdown 反引号改 `\texttt`）；48 个“本节层次”行全部可解析、所列小节存在且各出现一次，3.1、5.1 补齐小节编号；前言 `tab:preface-core-optional` 选学列补齐章内标为拓展的小节（4.3.7—4.3.8、4.5.9、4.8.3、6.2.5、7.1.4—7.1.5、7.2.8—7.2.9、7.3.3、7.4.3、8.2.2）；跨文件节号引用逐条核对（STAGES/MAPPING/TEACHING/README/S0 实录/docs/index.md/prep.tex/源码注释），改正 README 第 50 行与 `lesson52/AssetController.java`、`ReadingEntity.java` 两处过时注释；STAGES.md S6 行补 8.6 与 `smoke.sh`；术语检索无残留；21 个 `\includegraphics` 目标全部存在，generated/runtime 图无孤儿。

### 7.3 发布同步检查
- 站点：`tex2site` 三步 + `mkdocs build --strict` 通过；用 headless Chromium 逐页打开首页、前言、九章、三附录：全部 200，无失效图片（共 107 张），文章内站内链接无 404。控制台错误全部来自本环境被拦的外部 CDN（Google Fonts、jsdelivr 的 MathJax、polyfill.io），不是站点本身的问题。
- **发现并修正一处安全问题**：`mkdocs.yml` 与 `mkdocs-ci.yml` 的 `extra_javascript` 引用 `https://polyfill.io/v3/polyfill.min.js`。polyfill.io 域名 2024 年易主后曾向访问者投放恶意脚本，业界已普遍移除；MathJax 3 在现代浏览器上不需要该 polyfill。两处已删除，严格构建仍通过。
- PDF：`--strict --build` 通过，386 页（Fandol 回退字体），Overfull 0；抽查第 20、60、100、150、200、250、300、340 页（覆盖第1、3、4、5、6、7、8章与附录A）图表、清单、表格、页眉版式正常。

### 7.4 检查
`check_textbook.py --strict --build` 通过；`check_listings.py` 42 组一致；`audit_learning_path.py` errors 空；mkdocs 严格构建通过；站点逐页检查通过。CI（efa15b0）结果待查。

### 7.5 遗留
1. 作者待定项未变：5.6 权限模型与配套是否统一；`FIELD_REQUIRED`/`VALIDATION_ERROR` 差异改脚本还是改处理器；`ApiExceptionHandler` 兜底可能把 403 翻成 500；第6章教学断面尺寸是否进参数表、数据集测点分布、配套是否附 GLB；`stack-e2e` 失败原因（master 上已存在）。
2. 语言清理只做了本轮未重写的部分一遍；本轮重写的章节由各包的独立走读覆盖。全书没有经过学生试读。
3. 第5章 5.6 层次行无核心分组、5.8 全节拓展，与前言“JWT 认证与基本授权”列为主线的口径存在张力：5.6.1（过滤链）、5.6.3（解析令牌）、5.6.5（登录端点）现为指导实践，核心内容由配套工程承担；是否把 5.6.1 升为核心由作者定。

## 八、第五批（2026-09-23）：作者六项决定的落实

| 项 | 决定 | 落实 |
|---|---|---|
| 1 权限模型 | 配套保持 DUTY/ANALYST/OPS 最小实现；5.6.1 升核心；细粒度权限、刷新令牌、撤销、会话迁移为拓展 | 5.6 原先的最小实现正文位于任何小节之前，字面上的 5.6.1 是“威胁模型与认证边界”。为使“5.6.1 为核心”落在真正的最小实现上，新增 `\subsection{过滤器链、令牌解析与方法授权}` 作为 5.6.1，原 5.6.1—5.6.8 顺延为 5.6.2—5.6.9，层次行：核心 5.6.1；指导实践 5.6.4、5.6.6；拓展其余。开头段写明配套只实现三角色最小版本，扩展写法配套未实现、课程不要求。章内与第8章 8.6 对 5.6.x 的字面引用已同步。**编号顺延与作者原话（“5.6.1 认证与授权边界”）不同，请确认。** |
| 2 错误码 | 改 `ApiExceptionHandler`，不改脚本 | `MethodArgumentNotValidException`：首个字段错误的 `getCode()` 为 NotNull/NotBlank/NotEmpty → 400 `FIELD_REQUIRED`；否则 400 `VALIDATION_ERROR`；`field` 均为字段名。另补 `MissingRequestHeaderException` → `FIELD_REQUIRED`。书中 `lst:ch05-error-handler` 同步（逐字核对）；第8章 8.3.5 的故障练习按新行为改写。 |
| 3 403→500 | 显式处理 `AccessDeniedException`、`AuthenticationException`，500 只兜底未预期异常；加越权回归测试 | 处理器新增 403 `FORBIDDEN`、401 `UNAUTHORIZED`。为让测试有真实的 `@Valid` 请求体与角色限制端点，落实契约已有的 `POST /api/readings`（`ReadingWriteController` + `ManualReadingService`，限 ANALYST，`Idempotency-Key` 头，重发返回原记录，同一时刻已有观测→409 `READING_EXISTS`），书中 5.5.1 两个清单改为与配套逐字一致并登记。新增 `ReadingWriteControllerTest`（`@WebMvcTest` + `@Import(SecurityConfig)`，服务层 mock）六个用例：201、缺字段→FIELD_REQUIRED、@Pattern 失败→VALIDATION_ERROR、缺幂等头→FIELD_REQUIRED、DUTY 调用→403 FORBIDDEN 且服务层未被调用、匿名→401。5.9.2 改印该测试节选。 |
| 4 第6章 | 教学几何单列；重做数据集坐标；加教学 GLB | 6.1.2 新表 `tab:ch06-teaching-geometry`（顶宽8、底宽40、轴长160、坝基120、坝顶172，仅用于场景练习），8.1 参数表未动。`generate.py` 的 `stations()` 重写为“坝轴中点为原点的局部布置 + 高斯—克吕格反算”：PZ 4 断面×3 高程埋在坝内，D 坝顶/下游坡，WL 上游 150—700 m，RF 坝头及 1.1—1.7 km 流域；编码、SEED、观测序列与其他 CSV 逐字节不变；`stations.csv/json`、前端副本、`002_seed.sql` 同步。6.1.5、6.2.3 的派生数字重算（PZ-07 粗略/投影差 1.6 m→0.07 m，最远 RF-04 约 7.4 m，坝内为分米级）。新增 `frontend/public/models/generate-dam-glb.py`→`dam.glb`（1740 B，纯标准库生成，Y-up、米、基面 y=0），结构校验与 three r160 `GLTFLoader` 解析测试通过（`tests/lesson61-dam-glb.test.js`）；6.1.4 加载示例指向该文件。运行图 `s4-scene.png`、`s5-scene-chart.png` 按原方法（Playwright Chromium，同视口）重拍，README/manifest 记录差异（字体回退、坝体半透明以露出坝内测点）。 |
| 5 stack-e2e | 修 Dockerfile，使所有 Vite 入口进入构建上下文 | `frontend/Dockerfile` 改为拷贝 `public/`、六个 HTML、`lesson44.css`；本地以同一文件集 `npm run build` 通过。compose 整栈只能由 CI `stack-e2e` 验证，结果见终验。 |
| 6 篇幅 | 约 22 万字接受，不设新目标 | 记录于此；后续只因重复、逻辑或教学需要局部删改。 |

### 8.1 本批检查（云端）
`check_textbook.py --strict --build` 通过（388 页，Fandol 回退字体，Overfull 0）；`check_listings.py` 45 组一致；`audit_learning_path.py` errors 空；前端 vitest 12 文件 115 用例通过；tex2site + mkdocs 严格构建通过。Java 仍未在本环境编译，由 CI `backend`、`stage-lesson54`、`stack-e2e` 验证，结果回填于第九节。

## 九、终验记录（2026-09-23）

### 9.1 CI（运行于 aebe2aa，作者查看）
9 个作业中 8 个通过：docker compose 配置校验、前端测试与构建、后端测试（含新增 `ReadingWriteControllerTest` 六用例：FIELD_REQUIRED / VALIDATION_ERROR / 缺幂等头 / 越权 403 / 匿名 401 / 201）、在线版严格构建、清单一致、教学接口契约与闭环、S3 起点、S3 中点。`stack-e2e` 失败：Docker 内 `npm run build` 报 `Could not resolve "../../../shared/time.mjs" from "src/utils/readings.js"`。

### 9.2 收尾修复（stack-e2e）
- 原因：`src/utils/readings.js` 与 `src/lesson71/{quality,event-window,standardize,resample}.js` 都引用 `companion/water-platform-demo/shared/time.mjs`（前后端共用的时间解析），该目录在 `frontend/` 之外，而 compose 的构建上下文是 `./frontend`，`shared/` 进不了镜像。全仓库检索确认这是前端源码唯一一处跳出 `frontend/` 的相对依赖（测试文件里对 `output/case-params.tex` 的引用不参与镜像构建）。
- 修法：`docker-compose.yml` 的 frontend 构建改为 `context: .`（water-platform-demo）+ `dockerfile: frontend/Dockerfile`；Dockerfile 在 `/work/frontend` 下工作，`COPY shared /work/shared`，其余按原相对目录结构拷贝，`../../../shared/time.mjs` 在镜像内解析到 `/work/shared/time.mjs`。新增 `.dockerignore`（node_modules、dist、target、.git）。未改任何 import 路径，未复制重复文件。
- 本地验证：本环境 Docker 守护进程可启动但 Docker Hub 被出口策略拦截（`node:20-alpine`、`nginx:1.27-alpine` 均 403），无法真正 `docker build`。改做等价的干净构建：在空目录里只放 Dockerfile 各 `COPY` 指令所列的文件（`shared/`、`package.json`、`package-lock.json`、`src/`、`public/`、六个 HTML、`lesson44.css`、`vite.config.js`），`npm ci` 后 `npm run build` 通过，`dist/` 含六个入口页、`datasets/`、`models/`。`docker compose config -q` 通过。
- `docker compose up -d --build --wait → smoke.sh → --stage=full` 在本环境无法执行（镜像拉取被拦），由 CI `stack-e2e` 在推送后执行，结果由作者查看后回填于 9.3。

### 9.3 终验汇总

| 项 | 结果 | 出处 |
|---|---|---|
| 后端测试（`mvn -B -q test`，含 `ReadingWriteControllerTest`） | 通过 | CI `backend`（aebe2aa） |
| 权限 403 回归（DUTY 调 ANALYST 端点→403 FORBIDDEN，非 500） | 通过 | 同上，用例 `userWithoutAuthorityIs403NotInternalError` |
| 闭环错误码（缺字段→FIELD_REQUIRED；`closeloop-check.mjs` 未改） | 通过（教学接口）；真实后端由 `stack-e2e` 的 `--stage=full` 覆盖契约部分 | CI `teaching-api` |
| S3 中点（lesson54：建库→启动→契约核对） | 通过 | CI `stage-lesson54` |
| 前端 Docker 整栈（compose build + smoke + full contract） | 修复后**待 CI 复跑**；本地等价干净构建通过 | 见 9.2 |
| 全文静态门禁（`--strict`）、清单一致 45 组、学习路径审计 | 通过 | 云端 |
| PDF（`--strict --build`，388 页，Fandol 回退字体，Overfull 0） | 通过 | 云端 |
| 网站（tex2site + mkdocs 严格构建；逐页 headless 检查） | 通过 | 云端（逐页检查为 R11-06 时所做，之后正文改动已重新生成并严格构建） |
| 学生试读 / 试教 | **未做** | — |
