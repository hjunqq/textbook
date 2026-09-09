# 决策记录（仅记录改变项目方向的决策）

## D-2026-09-09-1 篇幅上限与分层迁移权
- 问题：第九轮"基础递进"需要新增解释与过程追踪，但全书已 226,201 字（门禁口径）/ 435 页，超出原 20 万字目标。
- 原方案：AGENTS 铁律 1"只增不删"，增量防删除拦截 >1000 字/次的删减。
- 新证据：读者为 64 学时左右的大三课程，500 页教材不可用；三层划分若无迁移权只是贴标签。
- 决策：可以删减，上限 240,000 字（门禁 TOTAL_CEILING）不得突破；拓展层内容可迁附录/实验手册/线上，须在 tools/migration_ledger.json 登记后提交；各章绝对安全线为第九轮起点的 85%（wordcount_baseline.json）；过程追踪图、故障记录、自测题列为铁律 5 合法载体。
- 否决的替代：不设上限（每包净增，篇幅失控）；保持只增不删（重组被门禁反向阻拦，执行者绕道注水）。
- 影响：可逆（改回基线文件即可）。后续：R0 逐节层次标注后，可把安全线细化为"核心层不低于基线"。

## D-2026-09-09-2 学生起点
- 作者答复：学生已学 Python、Java、C、C# 基础。
- 决策：取消审核方案 P1（变量/分支/循环复习单元）；P0（终端/端口/开发者工具/读错误信息）保留；P2 收缩为"Java 源文件→Maven 工程→Spring 注解"的工程衔接，不讲语言本身；P3（表/键/SQL/事务）保留，是否已学数据库待作者确认。
- 作者补充答复（2026-09-09）：课程 56 学时，本学期（2026 秋）开课。
- 决策：学时方案按 56 学时重排（审核方案 64 学时表按比例压缩：第4、5章各 14，第2、3章各 5，第6、7章各 5，第1章 2，第8章 5，第9章 1；讲授:实验约 30:26），以样章试教实测校准；R1 第4章样章必须在 2026-10 中旬前交付，进入本学期课堂试教，试教记录作为 M4 门控证据。

## D-2026-09-09-3 第九轮路线
- 决策：两段式（B）。本轮只做 R0 盘点 + R1 第4章样章 + R2 全书分层标注与预备单元（约 12–15 人日）；试教或试读后再决定 R3–R6；纸书付印不等 S 阶段包，阶段包作为线上配套分期发布。
- 否决：A 全量（35–45 人日，付印推后一学期）；C 不改。
- 影响：目标从"付印"扩展为"付印 + 可教"；付印时点取决于 R2 完成与试教结论。

## D-2026-09-09-4 接口契约统一
- 问题：R0 发现接口路径四套并存（ch03 monitoring/pointId、ch04 stations、ch05 readings+stations、ch08+companion assets），8.1 节无接口表，R1 教学接口无契约可对齐。
- 决策：以 ch08 + companion 的 asset/reading/warning/work-order 模型为唯一契约；契约表 `tab:api-contract` 与故障注入表 `tab:api-teach-faults` 放在 8.1 节（与参数表同处），原 8.3 节的接口表并入并删除；ch04 在 R1、ch05 在 R4、ch03 在 R2 改名归一。
- 否决：以 ch04 stations 为契约（需改 companion、DDL、ch06–08、CI，代价约三倍）。
- 影响：可逆但成本随章节推进递增；contract 中 `readings/latest` 端点骨架尚未实现，标为“教学接口；第5章实现”。

## D-2026-09-09-5 不等试教，全面推进
- 问题：D3 两段式把第 1–3 章重组与 R3–R6 挂在 R1 试教反馈之后；作者要求不依赖试教、全部推进。
- 决策：路线改为 A（全量）：R2-4 第 1–3 章重组 → R3 第4章全章 → R4 第5章 → R5 第6–7章 → R6 第8–9章 → R7 配套 → R8 验收，仍一包一提交、门禁不放宽；篇幅靠拓展层迁移换取（migration_ledger）。
- 代价与风险：教学单元的体例没有学生证据校准，试教发现的问题将作为第十轮整改而不是本轮门控；工作量 25–35 人日。
- 可逆性：每包独立提交，可按包回退。

## D-2026-09-09-6 Kafka 镜像改用官方 apache/kafka；配套 pom 不继承 starter-parent
- 问题：R8-c 实跑 `docker compose up` 时 `bitnami/kafka:3.7` 拉取失败——Bitnami 2025 年把旧版本迁入 `bitnamilegacy/` 归档仓库，不再更新，`bitnami/kafka` 下已无 3.x 标签。
- 决策：书（8.6 compose 清单）与配套一律改用官方 `apache/kafka:3.7.2`；环境变量去掉 bitnami 特有的 `CFG_` 段（`KAFKA_CFG_NODE_ID` → `KAFKA_NODE_ID`），卷路径改 `/var/lib/kafka/data`，健康检查改 `/opt/kafka/bin/kafka-topics.sh`。**不得回退到 `bitnamilegacy/`**：教材要用若干年，不能钉在明示不再维护的归档镜像上。CI 的 compose-config job 已断言新变量名。
- 附带记录：配套 `backend/pom.xml` 走 `dependencyManagement` 导入 BOM，**不继承** `spring-boot-starter-parent`（与书中清单 lst:ch05-boot-dependencies 的教法不同）。代价是 parent 默认提供的 `-parameters` 编译参数没有了，`@PathVariable String assetId` 这类写法在运行期抛 `parameter name information not available via reflection` 并返回 500——R8-b 实跑才发现，所有带路径/查询参数的接口都是坏的。现由显式声明的 maven-compiler-plugin 补上。**改动该 pom 时不要删掉那段 `<parameters>true</parameters>`。**
- 影响：可逆但需同步改书、配套、CI 三处；书与配套的 pom 差异已在配套 pom 的注释中说明。
