# 拓展专题

这些拓展专题适用于课程设计、毕业设计和平台运维，可结合性能测量或故障排查任务选读。学习后端优化前，先完成第5章的接口、存储与事务实践，再对照清单和表格检查缓存、连接池与监控配置。

## 服务边界、接口版本与健康检查

案例水库采用模块化单体（第3章3.5.2节），下面的内容在平台拆分为多个服务、或接口对外公开之后才会用到，供课程设计选读。

服务边界以业务能力划分。数据采集、读数查询、预警评估和通知可以是不同服务，但每个服务拥有明确的数据所有权和 API 契约；拆分不是把每个类都部署成独立进程。开发环境可用配置文件把逻辑服务名映射到固定地址，生产环境再接入服务注册与发现组件、健康检查和负载均衡。业务代码只依赖接口客户端，不能把某个注册中心的注解散落到领域层，这样基础设施实现与业务规则可以分别修改和测试。

跨服务调用要显式处理超时、重试和降级。查询测站详情可以在短超时后返回缓存快照，并在界面标注数据时间；写入监测值则不能因为重试而重复落库，应把请求 ID 和幂等键贯穿网关、服务日志与数据库。链路追踪至少传递`traceId`和`requestId`，错误响应包含可定位的错误码而不暴露内部堆栈。服务之间若共享 PostgreSQL 表，边界会失去意义，应改为通过版本化 API 或消息事件交换数据。

接口演进要兼顾兼容性和速度，并留下记录。对外公开的水利平台接口可以采用路径版本`/api/v1/assets`，在字段增加时保持旧字段语义不变；删除字段、改变单位或改变时间时区都属于破坏性变更，应发布`v2`并给出迁移窗口。版本号不应随着每次修复递增，补丁修复和兼容字段增加可以通过文档和变更日志说明。响应体可带`Deprecation`和`Sunset`提示，让调用方在停止旧版本前完成升级。

服务发现的健康检查至少分为进程存活、依赖可达和业务可用三类。进程存活用于重启异常实例，依赖可达检查数据库、Redis 和 Kafka 连接，业务可用则验证关键表结构、时序写入权限和预警规则加载。网关路由切换时先摘除不健康实例，再等待正在处理的请求完成；客户端重试只针对明确的瞬态错误，写入请求必须携带幂等键。

## 后端性能优化与可观测性

性能优化先测量再修改。数据库查询应建立与查询模式匹配的索引并使用分页；热点且允许短暂陈旧的数据可缓存；外部调用设置连接、读取和总超时；线程池与数据库连接池容量应依据压测结果配置。

可观测性包括日志、指标和追踪。关键指标可包含请求延迟、错误率、数据库连接使用率、Kafka消费积压和告警处理时延。健康检查只说明实例可服务，不等同于业务正确。

### 缓存与 Redis 一致性

缓存保存可复用的查询结果，以减少重复读取和下游压力。测站最新状态、权限字典和短期统计适合缓存；原始监测记录、审计日志和需要强一致的版本检查仍以 PostgreSQL 为准。缓存键要包含租户、测站、查询版本和单位，值中带生成时间与数据版本，界面显示缓存时间，避免把陈旧快照误当作实时水位。

**清单 C.1  Spring Cache 与 Redis 缓存读写**

```java
import org.springframework.cache.annotation.*;
import org.springframework.stereotype.Service;
import java.time.Duration;

@Service
class LatestReadingCache {
    private final ReadingService readings;   // 5.4.2 节的服务

    LatestReadingCache(ReadingService readings) {
        this.readings = readings;
    }

    @Cacheable(cacheNames = "latest-reading", key = "#assetId",
               unless = "#result == null")
    public Optional<AssetController.ReadingDto> get(String assetId) {
        // Spring Cache 会拆开 Optional 再缓存；尚无观测时 #result 为 null，不写缓存
        // 缓存的是 DTO（record），不是 JPA 实体
        return readings.latest(assetId).map(AssetController.ReadingDto::from);
    }

    @CacheEvict(cacheNames = "latest-reading", key = "#assetId")
    public void evictAfterWrite(String assetId) {
        // 由提交后事件调用，避免事务回滚时清错缓存
    }
}

@Configuration
class RedisCacheConfig {
    @Bean
    RedisCacheConfiguration cacheDefaults() {
        return RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofSeconds(30))
                .disableCachingNullValues();
    }
}
```

清单C.1在写入事务提交后通过事件使缓存失效；事务回滚时不触发失效，旧缓存仍然有效。生产环境为不同缓存设置 TTL 和容量上限，序列化采用受控 JSON 类型，禁止把 JPA 实体和懒加载代理直接写入 Redis。缓存命中、未命中、序列化失败和驱逐次数都要有指标，才能判断缓存是否真正降低了数据库压力。

缓存有三类常见风险。缓存穿透是大量请求查询不存在的测站，应用可以对空结果短暂缓存、校验 ID 格式并设置限流；缓存击穿是热门键在同一时刻过期，应用可以使用互斥锁、逻辑过期或预热任务；缓存雪崩是大量键同时过期或 Redis 集群故障，应用应加入随机 TTL、分批预热、熔断和数据库限流。降级读取旧快照时必须标注时间和可信等级，不能静默返回“最新”。

### 分页、游标与查询预算

页码分页适合需要跳转和精确总数的管理界面，游标分页适合不断追加的时序数据。对一个测点来说，`(occurredAt, version)`是主键去掉对象编码后剩下的部分，不会并列（5.4.3节），游标就由最后一条记录的这两项组成，服务端签名或编码后返回不透明字符串；下一页使用`(occurredAt, version) < (cursorTime, cursorVersion)`的联合条件，避免高页码`OFFSET`扫描历史数据。游标必须绑定原查询过滤条件和过期时间，客户端不能自行修改边界。

**清单 C.2  基于时间与版本号的游标分页**

```java
record ReadingCursor(OffsetDateTime occurredAt, int version) {}
record CursorPage<T>(List<T> content, String nextCursor,
                     boolean hasNext) {}

// —— ReadingRepository 中新增：取游标之前（更早）的若干条 ——
    @Query("""
            select r from ReadingEntity r where r.id.assetId = :assetId
            and (r.id.occurredAt < :time
                 or (r.id.occurredAt = :time and r.id.version < :version))
            order by r.id.occurredAt desc, r.id.version desc
            """)
    List<ReadingEntity> findBefore(@Param("assetId") String assetId,
            @Param("time") OffsetDateTime time, @Param("version") int version,
            Pageable limit);

@Service
class CursorReadingService {
    private final ReadingRepository repository;
    CursorReadingService(ReadingRepository repository) {
        this.repository = repository;
    }

    @Transactional(readOnly = true)
    CursorPage<AssetController.ReadingDto> next(String assetId, ReadingCursor cursor) {
        List<ReadingEntity> rows = repository.findBefore(assetId,
                cursor.occurredAt(), cursor.version(), PageRequest.of(0, 51));
        boolean hasNext = rows.size() > 50;
        List<ReadingEntity> page = hasNext ? rows.subList(0, 50) : rows;
        String next = hasNext ? encode(page.get(page.size() - 1)) : null;
        return new CursorPage<>(page.stream()
                .map(AssetController.ReadingDto::from).toList(), next, hasNext);
    }

    private String encode(ReadingEntity row) {
        return row.getId().occurredAt() + "|" + row.getId().version();
    }
}
```

清单C.2多取一条记录判断是否还有下一页，避免额外的`count(*)`；生产实现要对游标签名或使用服务器端存储，防止客户端篡改时间和对象编码。分页请求限制时间范围、单页大小和并发导出任务数，大范围报表转成异步任务并返回任务 ID。性能预算写在接口契约中，例如 P95 查询时延、最大返回字节数和连接占用上限。

### 连接池与慢查询定位

连接池容量影响数据库负载和请求等待。请求执行数据库操作时需要借用连接，连接数过大会让 PostgreSQL 争抢 CPU 和内存；连接数过小则请求排队。初始值根据数据库最大连接数、服务实例数和其他后台任务估算，再通过压测调整。HikariCP 的连接超时、最大生命周期、空闲超时和泄漏检测应有明确单位，日志显示池中活动、空闲、等待连接数，不能只看 HTTP 线程数量。

慢查询定位遵循“请求—Repository—SQL—执行计划”链路。结构化日志带 traceId 和查询名，Micrometer 记录耗时分位数；PostgreSQL 慢查询日志和`pg_stat_statements`提供 SQL 级证据；`EXPLAIN (ANALYZE, BUFFERS)`确认是否命中联合索引、是否发生 N+1 或大范围顺序扫描。优化后重新压测并比较 P95、锁等待、缓存命中和连接池排队，不能只凭一次本地运行下结论。清单C.3给出可以直接抄进`application.yml`的一组起始值，池大小与超时都写明单位，慢查询阈值与日志开关一并列出。

**清单 C.3  连接池、超时与慢查询日志配置**

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: ${DB_POOL_MAX:20}
      minimum-idle: ${DB_POOL_MIN:5}
      connection-timeout: 2000
      validation-timeout: 1000
      max-lifetime: 1800000
      leak-detection-threshold: 5000
  jpa:
    properties:
      hibernate.generate_statistics: false
logging:
  value:
    org.hibernate.SQL: INFO
    com.zaxxer.hikari: INFO
```

配置中的默认值只用于开发验证，生产值由容量评估和压测报告确定。泄漏检测用于发现忘记关闭流或事务边界失控，不能长期替代正确的资源管理；SQL 日志在生产环境要脱敏并控制采样率，避免把测站数据和参数全部写入日志。连接池耗尽应触发告警和限流，服务返回503或可解释的降级结果，并设置等待上限。

### Actuator、Micrometer 与结构化日志

Actuator 端点按暴露风险分组。健康检查可以公开进程存活和依赖状态，指标端点只允许运维角色访问，`env`、`configprops`和线程转储在生产环境默认关闭或经过严格授权。健康状态区分 liveness、readiness 和业务可用：数据库不可达时实例可能仍存活，但不应接收写入流量。

**清单 C.4  Actuator 健康检查与 Micrometer 指标**

```java
import io.micrometer.core.instrument.*;
import org.springframework.boot.actuate.health.*;
import org.springframework.context.annotation.*;
import org.springframework.dao.DataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

@Component
class ReadingHealthIndicator implements HealthIndicator {
    private final JdbcTemplate jdbc;
    ReadingHealthIndicator(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }
    public Health health() {
        try {
            jdbc.queryForObject("select 1", Integer.class);
            return Health.up().withDetail("store", "postgresql").build();
        } catch (DataAccessException unavailable) {
            return Health.down().withDetail("store", "unavailable").build();
        }
    }
}

@Configuration
class ReadingMetrics {
    ReadingMetrics(MeterRegistry registry) {
        Gauge.builder("water.reading.queue.depth", this,
                metrics -> metrics.queueDepth())
             .description("待处理读数队列深度").register(registry);
        Counter.builder("water.reading.rejected")
               .description("因质量或权限拒收的读数")
               .register(registry);
    }
    double queueDepth() { return 0; }
}
```

清单C.4把健康检查和业务指标分开：健康检查回答“实例是否能工作”，指标回答“处理质量和容量如何”。指标标签使用有限枚举，如质量码、结果类型和服务版本，不能把测站 ID、用户 ID 或完整 URL 作为高基数标签。告警阈值与案例水库 8.1 参数表中的工程阈值分离，运维告警不能修改业务预警标准。

**表 C.1  后端性能与可运维关键指标**

| 指标                | 采集位置               | 处置动作                         |
|:--------------------|:-----------------------|:---------------------------------|
| HTTP P95/P99 延迟   | Micrometer Timer、网关 | 按路由定位慢查询或下游超时       |
| 连接池活动/等待数   | Hikari 指标            | 调整池大小、限流并检查事务泄漏   |
| 缓存命中率/驱逐数   | Redis 客户端           | 调整 TTL、键设计和预热策略       |
| Kafka 积压/死信数   | 消费者组、DLT          | 扩容消费者、修复模式或补发事件   |
| 错误率与401/403/503 | 结构化日志、计数器     | 区分客户端、权限、依赖和发布故障 |

表C.1中的指标必须能关联同一 traceId 和发布版本，值班员才能从告警跳到具体请求和日志。指标只做趋势和阈值判断，根因仍需结合日志、数据库执行计划和消息偏移量。告警规则设置冷却、恢复通知和责任角色，避免同一故障在网关、服务、数据库和 Kafka 层重复轰炸。

**清单 C.5  traceId 贯穿请求与结构化日志**

```java
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.slf4j.MDC;
import org.springframework.web.filter.OncePerRequestFilter;
import java.io.IOException;
import java.util.UUID;

class TraceIdFilter extends OncePerRequestFilter {
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain)
            throws ServletException, IOException {
        String traceId = request.getHeader("X-Trace-Id");
        if (traceId == null || traceId.isBlank())
            traceId = UUID.randomUUID().toString();
        try (MDC.MDCCloseable ignored = MDC.putCloseable("traceId", traceId)) {
            response.setHeader("X-Trace-Id", traceId);
            chain.doFilter(request, response);
        }
    }
}
```

清单C.5在请求进入时建立 traceId，在离开线程前清理 MDC，避免线程池复用造成串号。Kafka 事件、数据库审计、Redis 操作和异步任务要显式传递 traceId；跨服务只传递可追踪 ID，不把 Authorization 头写入日志。结构化日志字段固定为时间、级别、服务、版本、traceId、事件类型、耗时和结果码，中文描述作为补充，便于机器检索和人工复核。

性能优化要与容量和恢复一起验收。一次压测至少记录并发请求、P95/P99、数据库连接、缓存命中、Kafka 积压、错误分类和 CPU/内存；故障演练再观察 Redis 不可用、数据库慢查询、Kafka 延迟和下游超时的降级结果。任何优化都保留开关、回滚配置和前后对比，避免为了追求单次吞吐牺牲数据可信度或审计完整性。

### 性能故障的分层处置

发现接口变慢时，先用 traceId 确认请求是否在网关排队、控制器参数校验、服务业务规则、数据库查询、Redis 访问还是 Kafka 发送阶段耗时。网关延迟高应检查连接和限流，服务耗时高应检查线程池和外部超时，数据库耗时高应查看执行计划、锁等待和连接池，缓存异常应查看命中率、序列化和网络延迟，消息积压则检查分区热点和消费者处理时间。分层诊断避免把所有问题都归结为“数据库不够快”。

降级策略要保持业务语义。测站最新状态查询可以在短时间内返回标注时间的缓存快照；原始读数写入应优先保证落库，消息通知通过发件箱延迟；预警评估所需数据质量不足时返回“未评估”，暂停生成等级结论；权限和审计服务不可用时，高风险写操作拒绝并返回503。每种降级都记录原因、开始时间、影响接口和恢复条件，恢复后自动清除或由运维确认。

Actuator 与日志端点本身也是生产攻击面。只暴露健康和必要指标，端点路径放在独立管理网或由 Spring Security 保护；健康详情不显示数据库地址、用户名、异常堆栈和令牌配置。结构化日志采用 JSON 输出，敏感字段在进入 MDC 前脱敏，异常堆栈关联内部事件 ID 而不是回显给客户端。日志采样不能丢失安全失败、事务回滚、死信和数据拒收事件，这些事件需要完整审计。

连接池和线程池必须共同估算。一个请求可能先占数据库连接，再等待 Kafka 回调或外部 HTTP，若线程数远大于连接池就会产生排队，若连接池远大于数据库容量则会放大锁竞争。使用压测数据设定最大并发、队列长度、拒绝策略和优雅停机时间；停机先停止接收新消息，再等待正在处理的事务提交或回滚，最后关闭连接池。健康检查只有在资源准备好后才报告 ready，滚动发布不会把半初始化实例加入流量。

缓存、分页和指标的配置要纳入版本管理。每次改变 TTL、最大页大小、连接池或告警阈值，都在变更记录中说明预期收益、风险、验证查询和回滚值；环境变量覆盖只改变部署参数，不改变案例水库的工程参数。运维手册提供一条从指标告警到日志、SQL、Kafka 偏移量和发布版本的排查路径，值班员按步骤即可复现和升级问题。 每次演练结束后还要归档指标快照、关键日志、执行计划和责任人复盘结论，形成下一轮容量评估的可追溯基线。 复盘结论应同步到发布记录和运维知识库。 容量评估还应标注数据版本和运行环境，保证不同批次的结果可比较。

## 基于构件的设计与复用

第3章3.4节按“因为什么而改动”划分模块，并用一个具体变化检验边界。模块如果要跨项目复用，例如把案例水库的监测接入、认证与审计用到灌区或河道项目上，还需要多做三件事：从领域里找出通用构件，接入前检验构件是否合格，把接口和配置设计成适合复用的样子。这套做法称为基于构件的设计（Component-Based Design，CBD），供课程设计选读。

### 领域工程：找出可复用的构件

领域工程是对某一类应用做调研，找出其中反复出现的通用功能，把它们做成可复用的构件。在水利信息系统里，身份验证、日志与审计、设备接入、观测数据的质量检查几乎每个项目都需要，流程和规则也大同小异，适合提取。

提取分两步。第一步识别通用功能：比较领域内的几个应用，列出它们共有的功能模块。第二步设计通用构件并封装领域知识：例如通用的身份验证构件除了校验用户名和密码，还把用户管理、权限控制的相关规则一并封装在内部；新项目只需配置和调用，不用重新开发。

### 构件合格性检验

构件接入系统之前，要检验它的接口行为、性能和质量约束是否满足需求。检验结果决定三种去向：直接采用，增加一层适配后采用，或者更换实现。

**单元测试**

单元测试验证构件内部的逻辑。对一个数据处理构件，检查它对各种输入的转换和计算是否正确，及时发现并修复内部缺陷。

**集成测试**

集成测试在构件装进系统以后进行，检查它与其他模块的交互是否正常。以通信构件为例，重点观察三种失败形态：连接建立不上；报文能发出但字段被截断；重传后同一条读数被写入两次。这三种情况在单元测试里都看不出来，只有把构件放回真实的系统环境才会暴露。

### 面向复用的接口与配置设计

**接口标准化**

对外提供通用的接口形式（如 REST API），调用方就不必为每个新系统改写一次适配代码。监测数据接入构件如果提供标准化的 REST 接口，监测平台、移动巡检应用和专题分析系统都可以直接调用，不用关心它的内部实现。

**配置灵活性**

把随场景变化的部分做成参数。传感器数据采集构件可以通过配置文件指定传感器类型、连接方式和采样频率，同一个构件就能适应不同类型的传感器和不同的工作环境。

**案例**

案例水库的监测接入模块遵循通用的接口标准和通信协议，不依赖特定业务系统的内部实现，因此可以移植到其他水利信息系统：河道水文监测系统用它采集流量、水位和雨量，泵站运行监测系统用它接入振动、电流和视频数据，各自更换一批协议适配器即可。

## 对话框焦点管理与长列表渲染

本节两段脚本是第4章4.2.3节和4.4.6节的延伸，阅读前需要4.4节的 DOM 与事件基础。

**对话框的焦点管理**

弹出详情对话框时，键盘焦点要移到对话框标题；关闭时回到触发它的按钮，值班员才能接着刚才的位置继续操作。清单C.6用原生`<dialog>`元素实现：`openDialog`先记下当前焦点所在的元素，`showModal()`打开模态对话框后把焦点交给带`autofocus`的标题；`closeDialog`关闭对话框并把焦点还回去；按 Esc 触发的`cancel`事件走同一个关闭函数。脚本只管交互，样式仍交给 CSS。换成 Vue 组件时，把两个函数放进组件，并在`onUnmounted`里移除事件监听。在控制台运行后只用键盘操作：回车打开，Esc 关闭，焦点应回到“查看测站详情”按钮上。

**清单 C.6  监测详情对话框的焦点管理**

```javascript
document.body.insertAdjacentHTML('beforeend', `
  <button id="open-station" type="button">查看测站详情</button>
  <dialog id="station-dialog">
    <h2 autofocus>测站详情</h2>
    <p>此处显示经过后端校验的测站信息。</p>
    <button data-close type="button">关闭</button>
  </dialog>`);

const dialog = document.querySelector('#station-dialog');
const openButton = document.querySelector('#open-station');
let lastFocused = null;

function openDialog() {
  lastFocused = document.activeElement;
  dialog.showModal();
  dialog.querySelector('[autofocus]')?.focus();
}

function closeDialog() {
  dialog.close();
  lastFocused?.focus();
}

openButton.addEventListener('click', openDialog);
dialog.querySelector('[data-close]')
  .addEventListener('click', closeDialog);
dialog.addEventListener('cancel', closeDialog);
```

**只渲染可视窗口的长列表**

列表到上万行时，瓶颈在节点数量和布局计算。虚拟滚动只为可视区域附近的几行创建节点，并把滚动位置换算成数据下标。清单C.7是固定行高时的基本思路：占位层把滚动条撑到全量高度，可见的 8 行用绝对定位放到各自的位置，滚动时重新计算起始下标。运行后拖动滚动条，“元素”面板里始终只有 8 个行节点。实际使用还要处理行高不固定、键盘焦点落在被回收的行上，以及向读屏软件说明“第几项，共几项”；测点卡片高度差别很大时，先用分页或分组折叠，确认性能不够再引入虚拟滚动。

**清单 C.7  长测站列表的可视窗口渲染思路**

```javascript
const root = document.createElement('div');
root.innerHTML = '<div id="virtual-list" style="height:160px;overflow:auto"></div>';
document.body.append(root);
const viewport = root.querySelector('#virtual-list');
const records = Array.from({ length: 1000 }, (_, index) => ({
  assetId: `DAM-A-PZ-${String(index + 1).padStart(4, '0')}`,
  value: (180 + index / 100).toFixed(2)
}));
const rowHeight = 32;
// 占位层把滚动条撑到全量高度，可见行再absolute定位到对应位置；
// 没有它 scrollTop 永远到不了后面的行
const spacer = document.createElement('div');
spacer.style.cssText =
  `position:relative;height:${records.length * rowHeight}px`;
viewport.append(spacer);

function renderWindow() {
  const first = Math.floor(viewport.scrollTop / rowHeight);
  const visible = records.slice(first, first + 8);
  spacer.replaceChildren(...visible.map((record, offset) => {
    const row = document.createElement('div');
    row.style.cssText = `position:absolute;left:0;right:0;` +
      `top:${(first + offset) * rowHeight}px;height:${rowHeight}px`;
    row.textContent = `${record.assetId}：${record.value} kPa`;
    return row;
  }));
}
viewport.addEventListener('scroll', renderWindow, { passive: true });
renderWindow();
```

## 明暗主题与高对比度样式

CSS 自定义属性在运行时可以被继承和覆盖，适合承载一整套主题。文字色、背景色、边框色、状态色和间距集中定义在`:root`或页面容器上，组件通过`var()`读取；值班室降低环境亮度时，只替换这一组变量，地图、卡片和表格保持同样的对比关系。暗色主题不能简单地把白色换成黑色，还要重新检查文字与背景的对比度、曲线颜色的区分度、预警颜色在暗底上的可见性和焦点环的边界。

主题由用户通过按钮或系统偏好决定，不随业务预警等级自动切换。`prefers-color-scheme`作为初始值，用户显式选择后存到本地并覆盖系统偏好；主题切换只改变呈现用的变量，不改变 DOM 顺序和语义。截图、打印和投影场景还要有高对比度的后备色，“正常”与“预警”不能只靠颜色区分。

清单C.8给出明暗主题和高对比度状态样式。`data-theme`属性由应用状态控制；`forced-colors`分支让操作系统的高对比度模式接管边框和文本颜色。把这段样式与清单4.2的页面组合后，先用窄屏和键盘完成基本任务，再到 1920、2560 和 3840 像素的画布上检查，最后切换暗色和高对比度模式，每种条件下水位、预警和时间信息都应可读。

**清单 C.8  监测页面的明暗主题与高对比度**

```css
:root {
  --surface: #ffffff;
  --surface-raised: #f5f9ff;
  --ink: #263238;
  --border: #b0bec5;
  --normal: #1565c0;
  --warning: #d46b08;
}

[data-theme="dark"] {
  --surface: #17212b;
  --surface-raised: #0f151b;
  --ink: #f5f7fa;
  --border: #607d8b;
  --normal: #90caf9;
  --warning: #ffb74d;
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { color-scheme: dark; }
}

.monitor-panel {
  color: var(--ink);
  background: var(--surface);
  border: 1px solid var(--border);
}
.monitor-panel.is-warning {
  outline: .2rem solid var(--warning);
}
@media (forced-colors: active) {
  .monitor-panel.is-warning { outline: 2px solid CanvasText; }
}
```

## 前后端认证联调的深入检查

本节承接第4章4.5.7、4.5.8节，阅读前需要第5章的认证与授权内容。

**先画状态机**

认证相关的页面状态至少有六种：匿名、已登录、令牌即将过期、令牌已过期、权限不足和服务不可达。每种状态都要规定界面文案、是否保留原路径、是否允许重试，以及日志里应出现的事件。例如匿名用户访问测点详情，守卫保存`redirect=/assets/DAM-A-PZ-07`并跳转登录，登录成功后只恢复一次导航；后端返回 403 时停留在业务页面并显示权限说明，不再跳到登录页。令牌过期后页面在登录页和业务页之间反复跳转，通常是把这六种状态折叠成了“有令牌”和“没令牌”两种。

**登出与多标签页**

登出除了删除浏览器里的令牌，还要调用后端的撤销接口，或者让短期令牌自然过期；多个标签页通过`storage`事件同步退出状态。刷新令牌如果放在 HttpOnly Cookie 里，前端读不到它，只能根据刷新接口的结果更新内存中的访问令牌。

**字段升级的节奏**

前后端对字段的兼容按“先增加、后切换、再清理”进行。后端新增`qualityFlag`时，一段时间内同时返回新旧字段；前端先读新字段、缺失时回退旧字段，并统计回退次数；确认所有客户端升级后再删除旧字段。删除之前检查缓存、导出任务和消息消费者。日期时间统一用带时区的 ISO 8601 字符串，数值单位写进字段说明，枚举值变化由版本化接口或兼容映射处理。组件不直接拼接 URL、读取令牌或解释状态码，这些集中在请求模块里；路径前缀或分页字段调整时，只改这一处。

**跨域与预检**

开发时浏览器向 Vite 发同源请求，再由代理转发。生产环境如果前端与接口不同源，允许的来源、方法、请求头和是否允许凭据由网关与后端共同约定。带`Authorization`头的请求会先发一次`OPTIONS`预检，服务端要正确应答预检，但预检通过不等于真正的请求可以跳过认证。`Access-Control-Allow-Origin: *`不能与带凭据的请求同时使用，允许来源应是配置好的白名单，不能把请求里的`Origin`原样返回。遇到“浏览器报跨域、curl 正常”时，分别检查预检响应、实际响应和网关是否丢掉了认证头。

**令牌放在哪里**

`sessionStorage`便于教学演示，标签页之间互相隔离，但同源脚本可以读取它；HttpOnly Cookie 让脚本读不到令牌，代价是服务端要设置 SameSite、Secure 并防护 CSRF。无论哪种方式，访问令牌都不能出现在 URL、页面标题或埋点参数里；浏览器控制台只输出状态码、错误码和追踪 ID，服务端日志对令牌做哈希或只记录 jti；前端构建产物中不能出现 JWT 签名密钥、数据库连接串和内部网段。

**认证的性能**

一次受保护请求的耗时分为令牌解析、撤销查询和业务查询三段。每次请求都访问远程撤销存储会增加延迟，完全不查又无法及时吊销泄露的令牌；折中做法是访问令牌设为短期，把 jti 撤销集合缓存在 Redis，过期时间与令牌的 exp 对齐。角色到权限的展开在服务端完成，前端据此隐藏不该出现的按钮，但“按钮不可见”不能代替后端授权。批量读取测点时，后端限制单次数量和时间窗口，避免一个合法令牌被用来放大高负载接口。

**可重放的联调记录**

固定测试数据和时间窗口：每个测点至少准备一条 valid、一条 suspect 和一条 missing 读数，分别验证正常展示、可信度降低和不参与判断；告警处置单准备“待确认—已确认—已关闭”三种状态，检查不同角色能执行的动作。测试请求携带固定的`X-Request-Id`，应用日志保留它以及测点编码、质量码和耗时，数据库审计记录补充操作者和事务结果。定位一次失败请求时，先记下用户动作和路由，再记请求方法、路径、状态码、错误码和追踪 ID，最后核对过滤器日志、业务日志与审计表是否指向同一操作者和测点。联调结束后删除调试开关和临时账号，把前端构建版本、后端提交号、数据库迁移版本、代理目标和测试账号角色一并归档，下次升级照同一份记录重放，就能分清问题来自新代码还是环境变化。

**按角色走查**

在案例水库的演练中，值班员从测点列表打开详情，专业分析员提交处置意见，审批人确认后才允许关闭事件。三个角色看到的按钮、请求权限和审计结果必须一致；任何一个角色在页面上看到可点击的操作却收到 403，就回到路由元数据、后端方法授权和角色映射逐层核对。

## 前端构建产物的发布与回滚

本节承接第4章4.8.3节。清单C.9给出构建与部署的命令和反向代理的两条关键规则：前端容器只提供静态文件，`/api/`转给后端，其余找不到的路径回退到`index.html`。

**清单 C.9  Vite 产物与 Docker Compose 部署契约**

```bash
# 构建阶段：在固定 Node 版本中生成 dist/
docker build --target build -t water-web-build .
# 运行阶段：静态服务器只读挂载产物，API 由反向代理转发
docker compose up -d water-web nginx

# nginx 关键规则（伪配置，部署时写入站点配置）
location /api/ { proxy_pass http://water-api:8080/; }
location / { try_files $uri $uri/ /index.html; }
```

**深链接与缓存分层**

浏览器直接打开`/assets/DAM-A-PZ-07`时，静态服务器先找同名文件，找不到就回退到`index.html`，再由 Vue Router 渲染详情页；`/api/`必须先于这条回退规则匹配。缓存头分三层：`index.html`短缓存并要求重新验证，避免用户拿到旧入口去请求已经删除的代码块；带内容哈希的脚本和样式长期缓存；监测接口按数据时效禁止缓存或设置很短的有效期。部署后用真实浏览器和命令行各验证一次，只看服务器状态码不够。

**构建流水线**

流水线分为依赖安装、静态检查、单元测试、生产构建、产物检查和发布六步。依赖安装使用锁文件（`npm ci`），不同机器得到相同版本；静态检查关注未使用变量、可访问性和路径别名解析；测试至少覆盖路由守卫、筛选计算和请求错误分类；构建日志记录 Node、Vite 和插件版本；产物体积超过预算时阻断发布。

**不可变目录与回滚**

每次构建把`dist/`复制为带提交号的版本目录，生成一份包含入口哈希、资源清单和构建时间的 manifest；反向代理通过符号链接或配置项指向当前版本。切换后依次检查首页、登录、测点详情和接口健康状态。发现路由 404、资源加载失败或接口异常时，切回上一个 manifest 即可恢复。回滚只改变静态文件的指向，不动数据库和时序数据；上一个版本保留到确认监测业务稳定之后再清理。

**产物安全检查**

检查分源代码、产物和运行时三个面。源代码扫描禁止把令牌、私钥和内部密码提交到仓库；产物扫描检查压缩后的 JavaScript 是否残留调试开关、源代码地图是否暴露内部路径；运行时检查内容安全策略、HTTPS、跨域策略和错误页面是否泄露堆栈。环境变量的`VITE_`前缀不是保密机制，进入前端产物的值一律视为公开。发布记录写明发布人、构建提交号、镜像摘要、变更范围、接口兼容性、验证结果和回滚入口，值班员交接班时据此判断当前版本状态。

## 地图服务的发布、缓存与运维

第6章6.2.4节说明了 WMS、WMTS、WFS、WCS 和 3D Tiles 各返回什么，以及怎样在 Cesium 里接入自建底图。把这些服务长期运行起来，还要处理发布、缓存、版本和故障，供课程设计选读。

**各类服务的数据生命周期**

WMS 的样式和图例变化时重新渲染即可，不必重建原始数据；WMTS 适合版本稳定的底图，更新时按区域和层级增量切片；WFS 的属性字段属于业务契约，字段改名通过版本化接口发布；WCS 的覆盖数据保留像元分辨率、NoData 值、单位和采样时间，供模型计算复现；3D Tiles 在每个瓦片里维护几何、纹理和层级元数据，客户端按视域和屏幕误差请求。这几类服务的缓存策略、权限边界和更新节奏各不相同，不宜包装成一个笼统的“地图接口”。

**GeoServer 发布步骤**

发布分四步，每一步都可以单独回退：在工作区登记数据源和坐标元数据；创建工作空间和图层；配置样式与访问权限；在 GeoWebCache（GWC）里创建或绑定瓦片矩阵集（gridset）并预生成热点区域的缓存。发布前用 GetCapabilities 确认服务版本、图层名和坐标系，发布后用一条 GetMap、一条 GetFeature 和一条 GetCoverage 请求做冒烟测试：GetMap 看颜色和图例，GetFeature 查属性、几何和轴序，GetCoverage 抽几个像元与原始文件比对，3D Tiles 检查 LOD 切换、纹理色彩空间和业务标识是否保留。冒烟通过后再启动预生成；预生成任务按层级和工程范围拆分，失败的任务可以重跑，缓存目录带版本号，避免新旧瓦片混用。缓存清理和重新切片要有任务编号与进度记录，不在高峰时段整体删除。

GeoServer 的 GWC 默认只内置 EPSG:4326 与 EPSG:900913 两个瓦片矩阵集，CGCS2000 经纬度（EPSG:4490）的需要手工创建，并核对原点、瓦片宽高、分辨率和层级数。清单C.10是一个教学配置片段：层0让$1^\circ\times1^\circ$的范围恰好落入一张$256\times256$的瓦片，以后逐层减半。

**清单 C.10  GeoServer GWC EPSG:4490 gridset配置要点**

```yaml
gridSet:
  name: EPSG:4490
  srs: 4490
  tileWidth: 256
  tileHeight: 256
  extent: [113.0, 34.0, 114.0, 35.0]
  metersPerUnit: 111319.490793
  levels:
    # 层 0 让 1°×1° 范围恰好落入一张 256×256 瓦片：
    # 1/256 ≈ 0.00390625 度/像素，逐层减半
    - {level: 0, resolution: 0.00390625}
    - {level: 1, resolution: 0.001953125}
  cacheLayers:
    - water:cgcs2000_basemap
```

实际工程从测区范围和服务规范计算分辨率、矩阵宽高与最大层级。图层声明的坐标系与瓦片矩阵集不一致时，缓存在切片阶段就会错位；最大层级没有与 Cesium 的`maximumLevel`同步时，客户端会持续请求不存在的瓦片，日志里出现大量404。发布脚本把这两项作为启动前检查。

**能力文档、缓存键与监控**

每个服务维护一份能力文档，列出服务版本、操作、图层或覆盖名称、坐标系、轴序、输出格式、最大请求范围和异常编码，示例请求使用脱敏域名和小范围数据。样式变更会改变 WMS 的像素结果，但不改变 WFS 属性和 WCS 像元，所以图层发布记录分别保存样式版本和数据版本。缓存键至少包含图层、样式、坐标系、范围、宽高、时间维度和数据版本；带时间维度的水位或降雨图层，时间参数必须进入缓存键，否则不同时刻会显示同一张图片。平台启动时对 GetCapabilities 做健康检查，运行中记录应答时延、返回字节数、缓存命中率、4xx 与 5xx 数量和上游数据库耗时。WMS 渲染失败时，前端提示专题图不可用并保留基础底图；WFS 或 WCS 不可用时，相关查询按钮置为不可用，不把空结果显示成“没有测站”或“没有积水”。查询参数进入数据库或栅格处理器之前做白名单校验，日志记录请求摘要、追踪号、图层、坐标系和耗时，不记录完整令牌。

**3D Tiles 发布检查**

检查瓦片内容的空间参考、几何误差和属性透传。每个瓦片的包围体用于视锥裁剪和屏幕空间误差判断，包围体错误会造成过早卸载或加载过多；业务属性通过稳定的对象编码关联到后端，不把完整的监测记录塞进瓦片。转换工具的输出日志包含源模型、坐标转换、LOD 阈值、纹理压缩和失败对象，抽样加载根节点、中间层和叶节点之后再开放服务。模型更新使用新目录和新版本号，客户端完成切换后再回收旧目录，避免长连接用户读到发布了一半的状态。

**向 OGC API 迁移**

OGC API 路线强调资源、链接和可发现性：Features 返回集合与分页链接，Tiles 返回瓦片集和地址模板，Coverages 返回覆盖描述与取子集的能力，Maps 返回渲染结果及样式信息。经典 WMS、WFS、WCS 仍是存量系统的主流，平台可以采用“兼容层加新接口”的做法：内部数据模型统一，对外按客户端能力提供两种接口；代理层把旧的键值对参数转换为新的路径和查询参数，并记录新旧请求的对应关系。迁移期间对同一测站和同一块 DEM 样本做双接口比对，坐标、属性数量和像元统计一致后再逐步切换；能力文档标出推荐接口和弃用时间，监控按接口版本分别统计流量，确认没有客户端被意外切断。

**故障演练**

人为关闭 GWC、缩小 WCS 允许范围或撤销某个图层的权限，观察客户端是否显示清楚的状态、服务端是否留下审计记录、缓存是否保持版本隔离。再用错误坐标系、越界范围、超大图片、未知图层和过期令牌等异常输入逐一请求，检查服务是否返回稳定的错误码和正确的 Content-Type，错误详情是否泄露内部路径、数据库或文件系统信息。演练结果写入运行手册，下一次发布前按同一脚本、同一批样本复核。

## 坐标成果的入库、审计与版本管理

第6章6.2.1至6.2.3节给出了坐标、高程和局部原点的换算。数据来自多个单位、平台长期运行时，还要把换算过程管起来。

**元数据分两级保存**

数据集级元数据保存统一的坐标系和版本：水平坐标系、投影方法、带宽、带号、中央经线、尺度因子、假东与假北、东坐标是否带带号前缀、高程类型、高程基准、单位、精度等级、转换模型版本和生产软件版本。要素级属性保存测站、控制点或构件的采集方法、精度和质量标识。同一图层混有不同来源的数据时，入库时拆成多个数据集并分别建立转换记录；来自外单位的数据同时保存原始坐标、转换前后的 EPSG 代码和转换日期。转换成功不等于精度合格，转换记录里还要有控制点数量、残差统计和审核人，成果复核时可以重算。

**原始区、标准区、发布区**

测量成果进入平台后分三层存放。原始区保存外业文件和原始坐标，不覆盖；标准区完成 EPSG、单位、高程基准和质量码的统一，生成带版本的数据库表；发布区按 WMS、WFS 或三维瓦片的需要生成切片、索引和缓存。每层保存源文件哈希、处理工具、参数和责任人，服务刷新只读取通过质量检查的标准区数据。出现定位问题时，可以按哈希和版本回放整条处理链。

**转换流水线的检查点**

接收阶段读取坐标系和高程基准，缺少元数据的数据进入隔离区，补全后重新校验；预处理阶段按带宽、中央经线和轴序完成转换，保留原始文件和工具版本；质量阶段用独立控制点计算残差，平面和高程分开统计最大绝对误差、均方根误差和样本数，检查是否存在整体平移、旋转或比例误差；发布阶段生成服务能力文档、EPSG 声明和数据字典；运行阶段新增测点继承同一套转换配置，配置变更时重新运行回归检查。控制点要覆盖坝轴线两端、闸室、廊道出入口和场景边界，不能集中在一小块区域。

**精度预算与变更控制**

坐标精度预算在需求阶段分配到数据采集、控制测量、转换计算、模型简化和渲染显示各环节。测量层的毫米级精度经过投影和局部原点平移后仍要可逆；模型简化允许视觉误差，但不改变用于定位闸门或测点的控制顶点；屏幕显示可以按像素取整，查询和分析仍使用原始的米制坐标。每次改变中央经线、局部原点或高程模型，重新生成控制点报告，并与上一版本比较残差和服务范围。

长期运行的平台把坐标配置当作基础设施契约，而不是前端常量。配置中心记录当前版本，后端接口在应答里返回坐标版本，前端加载模型时核对版本；不匹配时显示待更新状态并停止自动叠加，避免把新测量数据投到旧场景上。坐标版本更新要通知地图服务、三维瓦片和监测接口的维护者，发布说明列出受影响的图层、测站和查询时间窗，值班员据此抽查。

**可重复性测试**

用同一组经纬度和元数据在开发机、持续集成环境和生产镜像里各转换一次，比较东、北坐标和高程；差异超过约定精度时冻结发布，检查 PROJ 数据文件、浮点模式和参数顺序。测试样本既包含中央经线附近的点，也包含分带边缘的点和高程异常符号变化的点。部署后抽查一个测站，依次执行地图点选、三维拾取、后端查询和原始坐标回放，核对各步骤指向同一对象。验收记录写明转换日期、操作者、软件环境以及输入、输出文件的哈希；更新 PROJ 数据库或高程模型时，先在隔离环境重算并比较差异，旧版本数据保持可查询。

**教学实验**

先用一个已知控制点验证公式，再扩展到整批测站。实验报告列出原始经度、带宽、带号、中央经线、投影参数、转换后坐标、局部原点和误差统计；使用软件默认值时说明默认值的来源和适用条件。再做一个故意改变轴序或高程类型的反例，观察地图、三维模型和查询结果怎样分离。

## 倾斜摄影的外业设计、空三检核与成果验收

第6章6.3.1节说明了倾斜摄影的流程、四种点和精度评定公式。下面是生产环节的细则，供参加实际项目的读者查阅；各项限差以项目适用的规范条款为准。

**外业设计**

影像覆盖范围要超过成果边界，航带端部和转弯区留出缓冲；建筑物立面、坝肩和峡谷等遮挡严重的部位增加交叉航线或补拍方向，并在任务书里记录补拍原因。曝光时间、光圈和感光度与飞行速度、光照和地表反射率匹配，避免运动模糊和高光饱和。飞行日志保存航线版本、起降时间、设备编号、镜头组合、定位定姿数据（POS）来源、坐标基准、天气和异常处置，与影像文件用同一个任务编号关联。

**像控点与检查点的记录**

每个点保存点号、现场照片、点位描述、平面坐标、高程、坐标参考系、测量设备、观测时段和质量等级。点位选在纹理稳定、边缘清楚、多个视角都能辨认的位置；坝顶栏杆、水面反光区和临时堆料区会随时间变化，不宜作控制点。检查点使用同样的记录格式，在空三求解阶段锁定为独立数据，最终验收时才参与误差统计。

控制点的布设按工程对象的几何层次考虑：坝轴线两端控制整体方向，坝顶和坝脚控制高差与坡面，闸室、溢洪道和廊道出入口控制局部构件，场景边界控制模型裁切和瓦片范围。每一层至少保留一组独立检查点，误差统计才能分别回答“整体是否平移”“局部是否变形”“边界是否翘曲”。所有点都布在坝顶时，平面指标可能很好，坝脚和峡谷侧壁的失真却发现不了。项目报告把点位分层、点数和每层的最大残差列成表。

**内业检查**

处理从影像完整性检查开始：核对文件数量、命名、时间戳、相机姿态、POS 轨迹和坐标单位，统计模糊、过曝、欠曝、遮挡和重叠不足的影像。检查结果分为“可进入空三”“需补拍或重采”“隔离待人工复核”三类，原始影像和检查报告只读保存。匀光匀色保持地物纹理的相对关系，处理参数和输出版本写入报告，增强操作不覆盖原始像素。

**空三的四个阶段**

第一阶段检测每幅影像的特征点，在相邻影像和交叉航带之间匹配连接点，并经几何一致性检验剔除错误对应。第二阶段读取相机内方位元素、镜头畸变参数和 POS 初值，建立观测方程；相机标定文件注明获取日期、适用镜头和坐标单位。第三阶段把像控点作为带权观测加入光束法平差，迭代估计相机外方位元素、连接点坐标和必要的系统改正；平差报告列出迭代次数、单位权中误差、控制点残差和未参与平差的检查点清单。第四阶段用独立检查点验证成果；误差集中在某条航带或某个高差突变区时，回查航带重叠、POS 时间同步、控制点坐标和镜头标定，而不是调高软件的容差。

空三参数的调整采用小步回归：冻结通过检查的影像、控制点和相机标定版本，每次只改变一个参数组（连接点匹配阈值、POS 权重或畸变模型），输出平差迭代、控制点残差和独立检查点的$m_p$、$m_h$，与上一版本比较。整体误差下降而某一航带误差上升时，保留两版结果并分析原因。重复飞行或季度更新时，稳定的控制点作为跨期公共点，新增检查点用来检验地表变化；发生过施工变化的点位标注“不可跨期比较”，避免把工程改造误判为摄影测量误差。

**密集匹配与中间成果**

密集匹配之前冻结通过空三验收的相机和点云版本。水面、玻璃和植被边缘纹理不足，会出现空洞；坝体混凝土纹理重复，会出现条纹；狭窄廊道视角不足，可能生成错误表面。处理报告记录点云密度、异常点剔除规则、空洞填补策略和人工修补区域；用于变形监测的几何不做视觉平滑。从点云到网格的每一步保留可回放的中间成果：点云阶段记录坐标基准、密度和分类规则，网格阶段记录三角形数量、孔洞填补和简化误差，纹理阶段记录影像选择、接缝处理和压缩参数，切片阶段记录层级、包围盒、瓦片格式和服务版本。坝面、闸门和监测仪器等关键对象同时保存原始高密度模型与发布用的轻量模型，用稳定的对象编码关联：平台运行时使用轻量瓦片，专业复核时回到原始模型核对尺寸和位置。

**语义检查**

把坝顶、坝脚、溢洪道边墙和库岸水线分别作为可查询对象，检查对象编码是否与 BIM 或 GIS 目录一致；同一构件在不同 LOD 里的几何简化，核对其中心线、端点和高程是否在允许范围内。监测仪器的位置与实测点号一一对应，模型更新只替换几何和纹理，不改变历史观测的对象主键。模型表面与控制点一致而对象属性错配时，成果退回语义校核环节。

**验收结论**

交付验收覆盖几何精度、坐标基准、对象语义、版本血缘和服务性能五个方面，分别保存检查数据、误差报告、属性映射表和加载测试结果。平面限差、高程限差、中误差计算口径和粗差处置规则作为一个整体签字确认；项目采用地方细化规范或合同中更严的要求时，注明版本、条款和适用范围；规范版本变化后重新计算检查点并保留旧版报告。验收单给出“通过、限期整改、退回重算”三种结论之一，连同责任人、完成日期和复核证据：通过表示精度和语义均满足适用条款；限期整改表示问题已经定位，且不影响隔离范围以外的成果；退回重算表示控制网、基准或关键对象存在系统性风险。平台的发布服务只读取“通过”版本。每次复核保存输入清单、软件环境和脚本版本，同一批检查点在另一台机器上应得到相同结果；跨期更新的报告注明哪些差异来自新采集、哪些来自处理参数。

## 观测图表的更新预算、缓存与状态恢复

第7章7.2.7节说明了渲染器选择和更新节奏。图表从课堂演示走向长期运行的值班页面时，还会遇到下面几类问题，供课程设计选读。

**缩放、查询与缓存**

`dataZoom`只改变视图范围，浏览器里不必保留多年的原始数据。用户拖动到尚未缓存的时间段时，控制器按当前范围和合适的聚合粒度向服务端请求，并取消上一个未完成的请求；新应答返回后核对时间窗版本，晚到的旧应答不覆盖用户已经选定的新范围，做法与4.5.4节的序号核对相同。缓存键至少包含`assetId`、起止时间、聚合粒度、质量过滤条件、规则版本和时区，少了其中任何一项，同一条曲线在不同过滤条件下就可能被错误复用。在开发工具里显示缓存命中率、查询耗时和返回点数，可以看到“缩放流畅”主要取决于服务端按粒度聚合，而不是前端的某个技巧。

**联动事件的一致性**

图表点击、三维拾取和列表选择走同一个事件模型，事件里带着`assetId`、`occurredAt`、当前时间窗、质量码和来源组件。控制器先比较事件版本，再决定是否更新其他视图；给事件设幂等键，重复点击只更新一次焦点。指针移动产生的高频预览可以节流，确认预警、提交工单和导出报告不能节流。时间窗输入采用防抖并显示加载状态。服务端返回时如果规则版本已经变化，界面提示“按新规则重新计算”，不要静默替换颜色。地图、图表与三维场景之间共用一个选择状态对象，例如`{assetId, timeRange, qualityFilter, scenarioVersion}`；切换场景版本时清空或重新校验它，避免把上一版本的测点高亮到新模型上。

**保护用户的上下文**

数据刷新不重置当前的缩放范围、选中测点、键盘焦点和已展开的详情。规则版本改变时先保留旧视图并提示差异，用户确认后再切换。导出的图片或表格使用与屏幕相同的时间窗和过滤条件，并把采样周期、聚合方法、质量过滤和规则版本写入元数据，值班员看到的屏幕、分析员导出的报告和事后回放的记录才能互相核对。

**刷新与断线后的恢复**

浏览器刷新、网络短暂中断和标签页挂起都会打断实时页面。状态层可以保存一份快照：最近一次通过校验的时间窗、各序列的摘要、规则版本和最后一个事件游标。恢复时先显示“数据恢复中”，再按游标向服务端补拉增量，补拉的数据重新经过去重、迟到判断和质量规则。快照里不保存整个 ECharts 配置对象，也不保存临时的颜色，否则旧的合并结果会被当成新状态。补拉完成之前，断线期间在图上保持缺测阴影，不画成连续曲线。值班员确认预警的操作由后端记录确认人、时间和规则版本，刷新页面或换一台设备后确认状态仍在。

**可以复用的回归数据**

图表部分准备五组数据：单点连续到达；同一事件重复到达；乱序与迟到；含`missing`区间；一条序列删除后再加入。逐组检查曲线是否按`id`更新、旧图例是否清理、缺测是否断线、参考线是否与参数版本一致、联动能否在图表与三维之间往返。再在窄屏、深色主题、灰度打印和纯键盘操作下各测一遍，并确认实例销毁后没有残留的订阅。地图部分另加边界外的点、跨瓦片的点和坐标转换失败的点。每个失败用例保存输入快照、预期图形和实际图形，升级 ECharts 版本时用同一组数据回归。三维交互的回归再覆盖原点变更、LOD 切换和时间回放三者的组合，并记录相机位置、视场角、设备像素比、窗口尺寸、渲染器和浏览器版本，同一个点击坐标在不同设备上的结果才能对比；命中的三维对象、图表数据下标和事件时间三者不一致时，先修坐标或状态契约，不要靠调大拾取半径掩盖。

## 颜色令牌、验收矩阵与色板版本

第7章7.2.9节给出了色板类型、对比度公式和冗余通道的做法。多人协作、多主题的平台还需要把颜色当作配置来管理。

**颜色令牌**

先建立颜色令牌表，再让组件引用令牌名称，页面里不直接写十六进制色值。令牌分六组：背景、正文、边框、顺序型色阶、预警等级和质量状态。背景令牌有浅色和深色两套取值，正文令牌同时记录普通文字和大号文字的对比度结果。切换大屏主题时只替换一组令牌并重新计算对比度，不会出现地图已经变暗、图例仍是浅色文字的局部失配。每个令牌还记录适用对象和禁用对象：红色预警令牌只表示需要立即处置的业务等级，不兼作“数据无效”；蓝色预警令牌不兼作链接色或选中色。同一个点既是`suspect`又是橙色预警时，详情里质量码、等级、规则版本和处置建议分列为独立字段，颜色只是辅助。

**验收矩阵**

一张静态截图通过对比度检查，不能说明运行时也可读。按“背景×状态×组件×通道”建立矩阵：背景取浅色、深色、灰度和投影；状态取 NONE、BLUE、YELLOW、ORANGE、RED 与`valid`、`suspect`、`missing`的组合；组件取地图点、折线、柱状图、表格、按钮和弹窗；通道检查颜色、文字、图标、纹理和键盘焦点。每一格记录前景色、背景色、对比度、有无非颜色提示、读屏软件读出的文本和截图编号。某一格只依赖颜色时记为不通过，补上文字或形状后再复查。

**状态变化时的可读性**

预警等级从 NONE 升为 BLUE，界面除了变色，还显示“出现需关注变化”的文字，并在时间轴上留下状态变化的记录；从 BLUE 升为 YELLOW，同时更新处置入口和确认状态。质量码从`valid`变为`missing`时折线断开；恢复为`valid`后缺测区间保持空白，详情里显示恢复时间，补传的数据不伪装成连续的实时数据。动画时间要短并且可以暂停，闪烁只用于需要立即确认的事件。

**色板版本**

色板与预警规则版本一起放进配置仓库。每次调整蓝、黄、橙、红的色值，记录变更原因、影响的页面、对比度复测结果和导出报告样例；历史报告按生成时的色板版本解释，同一个等级在不同月份的报告里含义一致。前端加载令牌时发现版本不匹配，开发环境给出明显提示，生产环境回退到最近一次通过验收的版本并上报监控。

**打印与导出**

黑白打印时用线型、填充纹理和缩写文字区分等级。导出的表格把颜色还原成“预警等级”和“质量码”两列，并在表头给出解释。图片的替代文本按“对象—数值—质量—预警—时间”的顺序生成。验收时对比屏幕、打印件和导出文件，检查等级、质量与时间在三处是否能被一致地识别。

## 第8章数据库与部署的运行维护练习

第8章核心路线只用到建表、幂等写入、条件更新和按事件追溯。本节收录其余的数据库练习和部署运维要点，供实验课和课程设计选用。表结构见第8章8.3.3节；所有语句都在隔离的练习库里执行，不要对着有真实数据的库试验保留和压缩策略。

### 迁移版本、清单查询与空间查询

迁移脚本必须可重复执行，并把版本写入数据库。代码清单C.11示例用一个轻量 版本表记录迁移名称和校验摘要；发布工具还应记录执行人、开始时间、结束时间和失败日志。若 迁移中途失败，恢复脚本只回滚本次版本，不直接删除已有业务数据。

**清单 C.11  可重复执行的迁移版本记录**

```sql
CREATE TABLE IF NOT EXISTS schema_migration (
    version      text PRIMARY KEY,
    description  text NOT NULL,
    checksum     text NOT NULL,
    applied_at   timestamptz NOT NULL DEFAULT now(),
    applied_by   text NOT NULL
);

INSERT INTO schema_migration(version, description, checksum, applied_by)
-- checksum 由发布流水线对迁移脚本正文计算后填入，禁止手工编造
VALUES ('QY-DDL-001', 'core asset reading warning ddl',
        'sha256:9f2d1c0a...(流水线填入)', current_user)
ON CONFLICT (version) DO NOTHING;
```

对象清单是最频繁的读路径之一。代码清单C.12用状态和类型过滤有效测点， 并只取前端需要的列；不使用`SELECT *`可以避免新增列后无意扩大接口载荷，也能让数据库更容易 复用覆盖索引。分页时应使用稳定的`asset_id`游标，不能把页码当作长期一致性的依据。

**清单 C.12  按类型和状态读取测点清单**

```sql
SELECT asset_id, display_name, asset_type, unit,
       ST_X(geometry) AS longitude,
       ST_Y(geometry) AS latitude,
       elevation_m
FROM asset
WHERE active = true
  AND asset_type = :asset_type
  AND (:after_id IS NULL OR asset_id > :after_id)
ORDER BY asset_id
LIMIT :page_size;
```

空间查询必须明确输入多边形的坐标系。代码清单C.13先把外部边界转换到 4490，再用 GiST 支持的包围盒过滤和精确谓词；若输入无效，接口应在参数校验阶段返回错误，而不是让 数据库把空结果当作“区域内没有测点”。

**清单 C.13  影响区内测点的空间查询**

```sql
WITH area AS (
    SELECT ST_Transform(
        ST_SetSRID(ST_GeomFromText(:wkt), :input_srid), 4490
    ) AS boundary
)
SELECT a.asset_id, a.display_name, a.asset_type
FROM asset AS a CROSS JOIN area
WHERE a.active
  AND a.geometry && area.boundary
  AND ST_Within(a.geometry, area.boundary)
ORDER BY a.asset_id;
```

工单到期查询需要使用数据库当前时间和明确的状态集合。代码清单C.14把已经 取消或完成的工单排除，并返回预警等级，值班员可以先处理高等级且临近截止时间的事项。更新状态 时还要携带版本号，防止两个角色互相覆盖。

**清单 C.14  即将到期工单查询**

```sql
SELECT w.work_order_id, w.warning_id, w.owner_role,
       w.due_at, w.action, p.level
FROM work_order AS w
JOIN warning AS p ON p.warning_id = w.warning_id
WHERE w.status = 'in_progress'
  AND w.due_at <= now() + INTERVAL '2 hours'
ORDER BY p.level DESC, w.due_at;
```

模型运行审计必须把版本和输入快照一起返回。代码清单C.15按模型名称和时间窗 筛选成功与失败运行，失败运行只用于故障定位，不能被下游当作可复现结果。若结果需要重新发布，应 建立新的运行记录而不是覆盖旧结果。

**清单 C.15  模型运行审计查询**

```sql
SELECT run_id, model_name, model_version, status,
       started_at, finished_at, input_snapshot
FROM model_run
WHERE model_name = :model_name
  AND started_at >= :start_at
  AND started_at < :end_at
ORDER BY started_at DESC;
```

建表和升级的顺序也要事先定好。部署脚本先安装扩展，再创建`asset`，随后是引用它的`reading`和`warning`，最后是`work_order`与`model_run`。已经产生证据的表不能靠删表来回滚：先停止写入，导出审计快照，再把迁移标记为失效。升级字段时按“增加列—双写—回填—切换—观察—清理”六步走，观察期内保留旧列，直到备份和一次恢复演练都成功。

### 连续聚合、保留与压缩

连续聚合是TimescaleDB提供的一种物化视图：数据库按时间桶预先算好平均值、最值和样本数，并随新数据自动刷新，重复读取趋势时不必每次扫描原始观测。清单C.16在`reading`上建立十五分钟聚合`reading_15m`，只纳入`valid`观测，并保留样本数，页面可以据此解释“平均值为什么没有算上某条数据”。刷新策略要有一个回看窗口来覆盖迟到的消息；例中回看30天、延迟5分钟是教学参数，实际窗口应覆盖通信补传和消息重投的最长时间。

**清单 C.16  十五分钟连续聚合视图与刷新策略**

```sql
CREATE MATERIALIZED VIEW reading_15m
WITH (timescaledb.continuous) AS
SELECT asset_id,
       time_bucket('15 minutes', occurred_at) AS bucket,
       avg(value) AS value_avg, min(value) AS value_min,
       max(value) AS value_max, count(*) AS sample_count
FROM reading
WHERE quality = 'valid'
GROUP BY asset_id, bucket
WITH NO DATA;

SELECT add_continuous_aggregate_policy(
    'reading_15m',
    start_offset => INTERVAL '30 days',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes'
);
```

聚合结果适合重复读取的统计，不能代替证据。预警计算可以读十五分钟平均值来降低延迟，但触发处置之前要保留对应的原始时间窗、样本数和质量分布。聚合表不能手工编辑；数值要修正，就回到原始观测追加订正版本，再重新刷新聚合。

连续聚合查询只读取已物化的时间桶。代码清单C.17把桶边界、样本数和 质量语义一起返回，前端可以在样本不足时显示“数据稀疏”而不绘制误导性的折线。对于跨越夏令时或 多时区的部署，数据库统一使用 UTC，展示层再按用户时区转换。

**清单 C.17  读取十五分钟连续聚合结果**

```sql
SELECT bucket, value_avg, value_min, value_max, sample_count
FROM reading_15m
WHERE asset_id = :asset_id
  AND bucket >= :start_at
  AND bucket < :end_at
ORDER BY bucket;
```

迟到消息会让最近的聚合桶需要重算。代码清单C.18展示手工刷新窗口的 语句；它只在运维员确认补传范围后执行，并在变更记录中写明起止时间。自动策略继续负责日常刷新， 手工刷新不能成为绕过质量审核的常规写入口。

**清单 C.18  补传后的连续聚合刷新**

```sql
CALL refresh_continuous_aggregate(
    'reading_15m', :refresh_start, :refresh_end
);

INSERT INTO schema_migration(version, description, checksum, applied_by)
VALUES (:audit_version, 'late data aggregate refresh', :checksum, current_user);
```

冷数据保留策略必须服从证据保留期限。代码清单C.19用 TimescaleDB 策略对象 表达自动清理窗口；教学示例没有把窗口写死为工程参数，生产项目应从法规、合同和审计要求中取得批准 值，并在删除前完成备份校验。若某段数据仍被未关闭工单引用，业务服务应先延长其保留期限。

**清单 C.19  时序数据保留策略示例**

```sql
SELECT add_retention_policy(
    'reading', drop_after => INTERVAL '730 days'
);

-- 发布前由项目配置替换保留窗口，并核对审计与备份要求
SELECT hypertable_name, num_chunks, compression_enabled
FROM timescaledb_information.hypertables
WHERE hypertable_name = 'reading';
```

压缩策略要避开仍在频繁更新的热数据。代码清单C.20把压缩按时间列组织， 并先查询压缩状态再决定是否执行；质量修订窗口没有关闭前，不应提前压缩。压缩不是删除，恢复演练 仍需验证索引、连续聚合和原始版本都可读。

**清单 C.20  按时间块配置时序压缩**

```sql
ALTER TABLE reading SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'asset_id',
    timescaledb.compress_orderby = 'occurred_at DESC'
);

SELECT add_compression_policy(
    'reading', compress_after => INTERVAL '30 days'
);
```

时间分块的意义是把“最近的数据最常用”变成物理上的局部性：查最近一小时不碰几年前的块，归档两年前的数据不锁住正在写入的块。块的大小用有代表性的写入数据压测后确定：太小，规划器要管理大量对象；太大，压缩和备份的粒度变粗。

### 健康检查、备份登记、权限视图与修订审计

数据库健康检查关注约束违反的前兆。代码清单C.21统计缺少有效坐标、异常 质量码和未来时间戳的记录；它不自动改数据，只产生检查报告。每日检查结果应和发布版本关联，才能在 出现异常时判断是设备问题、迁移问题还是程序问题。

**清单 C.21  核心表健康检查**

```sql
SELECT 'asset_without_geometry' AS check_name, count(*) AS failures
FROM asset WHERE geometry IS NULL
UNION ALL
SELECT 'reading_bad_quality', count(*)
FROM reading WHERE quality NOT IN ('valid','suspect','missing')
UNION ALL
SELECT 'reading_in_future', count(*)
FROM reading WHERE occurred_at > now();
```

备份恢复演练需要验证“能否恢复业务链”而不只是“文件存在”。代码清单C.22列出 恢复演练所需的最小对象集合；实际备份工具负责导出数据和权限，SQL 只用于登记快照元信息。演练完成 后要用一条事件 ID 串起测点、观测、预警、工单和模型运行，确认外键和 JSONB 证据均可读取。

**清单 C.22  备份快照登记**

```sql
CREATE TABLE IF NOT EXISTS backup_snapshot (
    snapshot_id  text PRIMARY KEY,
    started_at   timestamptz NOT NULL,
    finished_at  timestamptz,
    object_count integer NOT NULL,
    checksum     text NOT NULL,
    verified     boolean NOT NULL DEFAULT false
);
INSERT INTO backup_snapshot(snapshot_id, started_at, object_count, checksum)
VALUES (:snapshot_id, now(), :object_count, :checksum);
```

权限查询只返回当前角色可见的对象。代码清单C.23采用视图封装敏感字段， 让报表用户看见编码、等级和统计结果，但看不到不必要的个人信息或完整设备密钥。生产环境还要结合 应用层授权和数据库审计，视图本身不能替代角色管理。

**清单 C.23  面向报表角色的最小视图**

```sql
CREATE OR REPLACE VIEW warning_report AS
SELECT warning_id, asset_id, level, evaluable,
       score, reason, status, created_at
FROM warning
WHERE status <> 'closed' OR created_at >= now() - INTERVAL '90 days';

GRANT SELECT ON warning_report TO report_reader;
```

异常数据修复必须可审计。代码清单C.24把修订前后的值登记为 JSONB， 并在写入新观测版本前生成审计行；如果修订没有批准号，接口应拒绝提交。审计表可以独立归档，不能 因为前端只展示最新值就删除。

**清单 C.24  观测修订审计登记**

```sql
CREATE TABLE IF NOT EXISTS reading_revision_audit (
    audit_id       bigserial PRIMARY KEY,
    event_id       text NOT NULL,
    old_value      numeric,
    new_value      numeric,
    old_quality    text NOT NULL,
    new_quality    text NOT NULL,
    reason         text NOT NULL,
    approved_by    text NOT NULL,
    audited_at     timestamptz NOT NULL DEFAULT now()
);
```

数据库观察指标要与业务指标对应。代码清单C.25从系统视图读取超表大小、 索引大小和最近数据时间；它不直接给出“系统健康”结论，而是为压测和运维看板提供证据。指标异常时 应同时查看 Kafka 积压、质量码分布和工单延迟，不能只看数据库 CPU。

**清单 C.25  数据库容量与新鲜度观察**

```sql
SELECT hypertable_name, table_bytes, index_bytes,
       total_bytes
FROM hypertable_detailed_size('reading');

SELECT max(occurred_at) AS latest_reading,
       now() - max(occurred_at) AS data_lag
FROM reading;
```

备份策略要同时覆盖结构、数据、权限和扩展。PostGIS 的空间列、TimescaleDB 的超表元数据、连续 聚合策略和角色授权缺一项都可能导致恢复后查询失败。全量备份之外还要保留增量或归档日志，并定期在 隔离环境恢复。恢复后按事件标识查询测点、原始观测、质量结论、预警记录、工单回执和模型输入， 再检查角色授权是否正确、新的时间块能否继续写入；任一项失败，都应记录恢复缺口。

权限设计遵循最小必要原则。采集角色只写观测和发件箱，质量角色可更新质量标记但不能修改原始值， 预警角色可创建和关闭预警，值班员可确认工单并提交回执，分析员可读取脱敏的历史数据，运维员才可 执行分区、压缩和恢复操作。数据库角色与应用角色一一对应，凭据存放在密钥服务中，代码和教材示例不 出现真实口令。审计日志至少保留角色、对象、操作、时间、请求追踪号和结果摘要，便于把数据库行为与 Kafka 消息、HTTP 请求和前端操作对应起来。

模式演进要优先考虑兼容。增加可空列通常可以向后兼容，删除列和改变枚举则必须经过观察期；大表添加 非空约束应先回填并验证，再分阶段切换。实体类和 DTO 不应复制一套互不相同的字段名，数据库字典是 唯一来源，代码生成或手工实现都应在代码审查中逐列核对。若后端需要把`asset`映射为 Java 实体，应保留`asset_id`、`geometry`和`metadata`的原语义，并对空间类型 明确转换策略；若 S3 生成示例数据，应按照同一编码规则和质量码集合生成，不能为方便而使用随机中文键。

测试要覆盖约束、查询计划和故障恢复三个层次。单元测试验证质量优先级和分类结果，集成测试验证外键、 唯一键、空间坐标系、超表写入和连续聚合，端到端测试验证从事件接入到工单回执的链路。性能测试使用 与目标测点规模相近的数据分布，分别记录高峰写入、最近查询、空间查询、预警队列和聚合刷新延迟。 故障测试包括消息重复、乱序、数据库短暂不可用、超表块压缩失败和恢复后重放；每个故障都要说明预期 质量码、状态转移和用户可见提示。

数据库容量规划也应从测点数量、采样周期和保留期限推导。估算时先计算每天的事件行数，再加入索引、 JSONB 证据、备份副本和压缩后的增长系数；写入峰值还要考虑设备同时上线、补传和消息重投。估算结果 只用于容量初始值，最终仍要用接近生产分布的回放数据压测。压测不仅看平均吞吐，还要记录第九十五和 第九十九百分位延迟、锁等待、超表块数量、连续聚合刷新滞后以及故障重试后的积压恢复时间。

### 告警规则、容量与备份恢复演练

健康检查分存活、就绪和业务烟测三层。存活探针只回答进程是否响应，失败时允许重启；就绪探针还检查数据库连接、迁移版本和 Kafka 生产者，失败时摘除流量但不立即重启；业务烟测用只读测点请求验证认证、查询和质量码字段，在发布后及每日交接时执行。三层探针不能共用一个返回 200 的接口，否则数据库故障会被误判为应用正常。

**清单 C.26  监控指标与告警规则基线**

```yaml
groups:
  - name: qingyuan-platform
    interval: 30s
    rules:
      - alert: ApiReadinessFailed
        expr: api_readiness == 0
        for: 2m
        labels: {severity: critical, owner: ops}
      - alert: ReadingIngestLag
        expr: qingyuan_reading_ingest_lag_seconds > 300
        for: 5m
        labels: {severity: warning, owner: duty}
      - alert: TimescaleDiskPressure
        expr: qingyuan_db_free_bytes < 20000000000
        for: 10m
        labels: {severity: critical, owner: ops}
      - alert: WarningAckTimeout
        expr: qingyuan_warning_unacked_seconds > 900
        for: 5m
        labels: {severity: warning, owner: duty}
```

代码清单C.26把告警规则按基础设施、数据链路和业务闭环分开，每条告警都有责任角色与处置手册。阈值要结合补传最大重投周期、TimescaleDB压缩窗口和工单确认时限，再用历史分位数校准。告警和恢复都记录时间、规则版本、当前值和证据链接，同一根因的指标按服务和时间窗聚合，避免告警风暴。 容量评估覆盖 API 并发、Kafka 分区、Redis 内存、数据库写入吞吐和时序增长。28 个测点的教学规模可以单节点运行，但不能推断生产容量；压测纳入补传、模型运行和备份并发。扩容前后使用同一场景复测，并记录消息最老年龄、WAL增长、磁盘剩余比例和查询P95，确保容量提升没有换来数据延迟或权限错误。 备份策略回答可接受的数据丢失窗口、一致性点和恢复验证方法。PostgreSQL使用全量加WAL归档，TimescaleDB压缩和分区策略与备份窗口错开；对象存储保存模型、纹理、报告和备份清单版本；Kafka保留足够日志以便重放，重放前依据 `event_id` 幂等约束清理重复风险。Redis只保存可重建缓存，不进入唯一备份范围。

**清单 C.27  备份恢复演练与健康检查清单**

```yaml
backup: {schedule: "15 2 * * *", retention_days: 35, mode: "base-plus-wal", verify: [checksum, restore-schema, latest-reading-time]}
object_store: {versioning: true, retention_days: 90}
kafka: {topic: qingyuan.reading.v1, replay_window_hours: 72}
rehearsal:
  target: isolated-restore
  steps: [stop-writes, restore-postgres-and-wal, restore-object-manifest, start-api-readonly, verify-trace, replay-with-event-id-deduplication, run-smoke-test]
  pass_conditions: [latest_reading_within_rpo, api_readiness_up, no_duplicate_warning, audit_trace_continuous]
```

代码清单C.27把“有备份”改成可观察证据。开始前冻结变更窗口并记录最后一个观测、预警和工单 ID；恢复后先以只读模式校验对象关系、时序最新时间和审计链，再开放写入。Kafka只重放恢复点之后且数据库没有的事件，缓存由 API 根据数据库重建。任一条件失败，演练结果为不通过，并写明缺失备份、迁移错误或无法解释的事件。 生产故障处置遵循观测、隔离、恢复、复盘顺序。运维员先确认探针和指标是否同时异常，避免把单个浏览器问题误判为全局故障；再依据 runbook 摘除异常实例或暂停消费，保护数据库和消息证据；恢复后用业务烟测验证测点到工单链路，专业分析员复核质量码和预警是否重复计算。每次演练沉淀恢复时长、数据丢失窗口、告警命中率和人工确认点，反过来校准保留策略、探针阈值和容量预算。 环境一致性还需要检查时区、字符集、容器用户和文件权限。数据库统一使用 UTC 保存发生时间，展示层按照值班员时区转换；所有容器以非 root 用户运行，备份目录只授予备份进程写权限。发布前用同一份配置渲染开发、测试和生产三套文件，比较渲染结果的键集合，发现多余或缺失变量就停止发布。配置差异要写入决策记录，不能靠运维员记忆。

服务启动分为迁移、就绪和接流量三个阶段。迁移任务使用独立的一次性容器并记录版本，API 进程启动时只验证当前版本，不在多个副本中同时执行结构变更。就绪探针恢复后再逐步放量，先让一个实例接收只读查询，再开放观测写入和工单写入。若错误率或延迟超过发布阈值，立即停止放量并保留旧副本，回滚决策由值班员和审批人共同确认。

健康检查结果要区分“进程活着”“依赖可用”和“业务正确”。例如数据库连接池耗尽时，存活探针可以继续返回成功，但就绪探针应标记失败；Kafka 网络短暂抖动时，API 可以继续查询历史数据，却不能承诺新观测已经进入时序库。业务烟测不修改数据，使用固定测点和时间窗，并核对质量码、追踪号和权限字段，避免测试请求制造假预警。

监控标签遵守最小维度原则。测点编号、工程编号、服务名和环境是稳定标签，用户姓名、完整请求参数和原始观测值不能直接写入指标，防止高基数和敏感信息泄露。日志记录请求号、状态码、耗时和错误类型，详细堆栈只进入受控日志库。运维看板同时展示基础设施、数据质量和业务闭环，值班员看到的是可行动的提示，而不是无法解释的技术计数。

告警处理有确认、抑制、升级和恢复四个状态。值班员确认并不代表故障已解决，只有烟测和业务链路验证通过才能关闭事件；同一服务在维护窗口内产生的预期告警应被抑制，但抑制规则必须有开始和结束时间。关键告警超过确认时限自动升级给运维员，超过处置时限再通知审批人。每次升级都保留原始告警和责任转移记录，避免交接后丢失上下文。

数据库和对象存储的恢复点要互相对应。只恢复数据库而没有模型卡、报告或场景版本，数字孪生预演就无法复现；只恢复对象文件而缺少审计和工单状态，也不能证明处置链完整。恢复演练先生成恢复点清单，列出数据库 WAL 位置、对象清单版本、Kafka 最老消息和配置摘要，再按清单逐项核对，最后由专业分析员签字确认业务结果。

Kafka 重放和定时补传都可能造成重复事件。服务端以 `event_id` 唯一约束和事务处理保证幂等，运维员在演练中主动重放一条已经消费的消息，确认不会重复创建预警或工单。重放窗口必须覆盖消息最大重投周期，并把分区、偏移量和过滤条件写入演练记录。发现重复时先暂停消费者，保留现场，再由开发人员依据审计链修复，不能直接删除数据库记录。

备份保留周期由恢复目标、法规要求和容量预算共同决定。保留时间过短会使长周期趋势无法复盘，保留时间过长则增加成本和恢复扫描时间。清理任务只删除已经通过校验且超出保留期的版本，删除前生成清单并等待审批。压缩、分区和归档策略每次变更都要先在恢复环境验证，避免线上压缩过程影响实时写入。

部署验收应包含故障注入而不只是正常路径。可以暂时停止 Redis，观察 API 是否降级为数据库查询；暂停 Kafka 消费，观察积压告警和恢复后的幂等；限制数据库磁盘，观察容量告警和写入保护；撤销一个角色，观察 403 是否被正确展示。每项注入都设置最长持续时间和回滚动作，演练完成后确认没有遗留进程、临时密钥或未关闭的维护窗口。

部署实验应提交以下记录：编排文件的版本、渲染后的非敏感配置、探针响应、告警触发与恢复时间、备份校验摘要、恢复后的业务烟测和变更审批号。教师可以据此判断部署是否可重复、数据是否可恢复、权限是否有效以及运维责任是否清晰。迁移到多节点编排环境时，还应补充节点故障、持久卷调度与跨节点网络的恢复测试。

## 平台形态并存时的隔离、抽查与评审方法

### “问题—尺度—证据”卡片与租户隔离

形态选型可以用一张“问题—尺度—证据”卡片完成。问题栏写清需要解决的业务动作，尺度栏写清涉及的工程、管理站、区域或流域范围，证据栏写清需要看到的字段、时延、权限和回执。例如“管理站是否能在网络波动时完成配水计划复核”属于区域与工程交界问题，既要有本地缓存和数据龄期标记，也要有计划版本、审批人和恢复后补传记录；“多工程联合调度是否采用同一来水过程”属于流域协同问题，重点则是统一时空基准、模型版本和跨域交换协议。卡片让选型讨论围绕可验证行为展开，而不是围绕“平台大不大”争论。

当一个平台同时服务三种形态时，租户隔离、数据域和角色权限要在架构初期确定。流域分析员可以读取多个区域的汇总序列，工程值班员只能访问所属工程的原始状态，审批人可以查看影响范围和回退条件但不一定拥有设备操作权限。跨域调用要带调用方、用途、数据版本和有效期，服务端再次校验而不是信任前端传来的角色名。这样才能在共享代码和基础设施的同时，保持每个形态的责任边界清晰。

验收时还要按平台形态分别抽取样本。流域级抽查跨区域汇总和模型回放，区域级抽查计划、配水和统计口径，工程级抽查测点质量、值班确认和设备回执；三类样本都要能沿对象编码、时间基准和审计事件反向定位到原始记录。若同一水位在三个尺度显示不同，先检查聚合窗口、质量过滤和版本，而不是简单修改页面数字。抽查结果记录样本范围、观察时间和责任人，便于下一轮版本比较。

每次形态调整都应同步更新接口目录、权限矩阵、运行手册和回滚预案。这些交付物共同构成平台形态选择的可审计依据，也为后续容量、性能和安全评估提供共同输入；评估结论随版本和责任边界一并归档，归档包至少包含形态选择依据、数据域说明、接口版本、权限矩阵、样本结果和回滚负责人——这些材料同时是后续扩展到更大空间尺度时判断兼容性的基线。

### 架构原则的“正例—反例—证据”三栏评审

架构评审还可以采用“正例—反例—证据”三栏法。正例描述系统应当如何工作，反例描述一个看似方便但会造成责任或数据风险的实现，证据栏则指定测试数据、日志字段、权限记录或演练步骤。以“高风险操作受控”为例，正例是专业分析员提交调度建议、审批人批准、值班员按设备回执执行；反例是任何能打开页面的人都能调用控制接口；证据应包括角色令牌、审批事件、指令有效期、设备回执和回滚记录。以“全过程可观测”为例，正例是一次预警可以追溯到输入快照和模型版本，反例是只保存最终颜色，证据则是追踪ID、规则版本和复核结论。三栏法让原则变成可执行的评审任务。

每次架构决策都应形成简短记录：先写业务问题和受影响对象，再列出候选方案及其取舍，随后说明选择依据、风险、观察指标、回滚条件和责任人。记录不能只写“采用高可用架构”或“加强安全”，而要写成可检查的句子，例如“网络中断超过心跳窗口后，边缘节点继续保存原始观测并标记数据龄期；模型服务拒绝使用超过时效的输入；恢复后按事件ID去重并补写审计记录”。这样的决策记录既能指导实现，也能在维护阶段解释为什么某个看似保守的限制是必要的。

原则落地还需要跨角色复核。业务代表检查对象、岗位和处置流程，专业分析员检查单位、时间、质量码和模型边界，开发人员检查接口、异常和依赖，测试人员检查可复现判据，运维人员检查监控、备份和回退，安全人员检查身份、最小权限和审计留存。小团队可以由同一人兼任多个角色，但评审记录仍应分栏写明每个视角的结论。若某一条原则暂时不能验证，应标记为待补证据并给出关闭条件，不应以“后续再看”结束评审。

评审结论应绑定版本号和复核日期，避免同一条原则在后续迭代中失去上下文；每次复核保留参与角色和未关闭风险的清单，随发布包一并保存。

## 生命周期选型评审记录与需求基线治理

### 选型评审记录与两周试验

选型评审的输出至少包括：项目特征证据、模型组合、每个模型的前置条件、第一轮可验证交付物、主要风险、审批人和模型切换触发条件。项目进行中如果用户参与频率下降、接口风险暴露或合规范围扩大，应重新评估活动顺序、参与方式与验证条件，并更新模型选择记录。评审时可对照前后两版记录，说明调整依据及其对交付计划的影响。

实际评审可以采用“先排除、再组合、后试验”的顺序。先排除无法满足合规、现场条件或团队能力的模型；再把全局基线、局部原型、增量交付和风险轮次组合起来；最后用一个两周左右可观察的试验验证假设。试验不以代码行数为完成标准，而以是否获得关键证据为标准，例如接口是否能在断网后安全恢复、审批人能否独立完成退回与再提交、数据质量问题能否被追溯。试验结束后将结果写入选型记录，明确继续、调整或停止的决定，下一次评审直接引用这些证据。

评审记录还应标出参与者、评审日期和所依据的基线版本，下一轮评审先核对这些字段，确认各方比较的是同一范围，再讨论模型是否需要调整。记录中还要写明模型选择后的第一个可验证交付物、风险负责人、预期证据、观察窗口和停止条件；若证据不足，就延长验证或退回组合设计，不能用“进度已完成”替代模型有效性。人员、设备或试点范围变化后，可据此比较前后条件，核查原先的风险判断和验证结果是否仍然适用。

### 需求基线的版本包、变更委员会与基线复核

矩阵可以放在版本库中由构建检查，或由项目管理工具维护，但字段含义必须固定。需求ID、版本、来源、责任人、设计对象、接口路径、测试用例、验收结果和变更号共同关联需求来源、实现与验收结果；删除一条需求时保留废止原因和替代需求，不能让历史测试失去解释。发布前由需求负责人抽样反向追踪，确保“已完成”至少有一项可复现证据，未完成项明确进入下一版本。

实施变更时要维护“旧版本可读、新版本可验证、失败可回退”三条边界。数据库字段增加可以先向后兼容，再在新版本使用；字段含义改变时应新建版本或迁移脚本，保留旧字段读取期；接口响应新增字段要确认旧客户端忽略它不会破坏流程。涉及代理键和个人信息时，迁移脚本只搬运业务标识，不把身份证号等敏感字段复制到新主键；回滚时要检查审计记录和外部消息是否已经发出，不能只恢复数据库快照而留下无法解释的任务状态。

基线发布需要一个可复现的版本包。除了SRS正文，还应冻结引用的模型文件、数据字典、接口示例、测试数据、评审纪要和待确认问题；版本包生成校验摘要，发布人和审批人签名。开发、测试和运维使用同一摘要确认自己拿到的是同一份需求，遇到争议时先核对版本再讨论实现。修订时保留差异说明，指出新增、修改、废止和迁移字段，不能用“全文更新”四个字替代影响分析。

变更委员会的职责可以按四类角色分工：业务代表确认价值和范围，安全与合规人员确认硬约束，技术负责人确认实现和迁移风险，测试与运维负责人确认验证、观察和回退条件。小团队可以由同一人兼任多个角色，但每个角色的决策记录仍要单独填写。涉及闸门控制或防洪调度的变更，即使只是调整默认参数，也应至少经过审批人和专业分析员复核；普通报表排序可以采用轻量流程，但仍要留下版本号和回归用例。

一份合格的SRS还应在交付时附上阅读说明：先读范围和角色，再读功能用例与数据契约，最后对照质量指标、追踪矩阵和变更历史。读者按照同一路径检查，能在不依赖作者口头解释的情况下复现关键决策和验收步骤。

需求基线发布后还要安排一次“基线复核”，确认文档、模型、接口示例和测试数据来自同一版本摘要。复核时随机抽取几条需求，从业务目标追到验收证据，再从测试失败反查责任人和变更号；如果任一方向出现断点，就把断点登记为发布风险并规定关闭条件。对案例灌区这类持续接收设备数据的系统，复核还应覆盖跨日时段、重复提交、权限变化和网络恢复等边界场景，确保文字规则在真实运行节奏下仍然可执行。只有通过基线复核，版本包才适合作为开发、测试、培训和运维共同引用的唯一依据。
