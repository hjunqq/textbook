# 拓展专题

本附录集中讨论第5章引出的后端性能与可观测性。其他章节的进阶专题见配套网站“线上拓展专题”。

## 后端性能优化与可观测性

本节接第5章5.8节。性能优化先测量再修改：数据库查询建与查询模式匹配的索引并分页；热点且允许短暂陈旧的数据缓存；外部调用设连接、读取和总超时；线程池与连接池容量按压测结果定。

可观测性（observability）指从外部看得出系统内部在干什么，靠日志、指标和追踪三种数据。关键指标有请求延迟、错误率、数据库连接使用率、Kafka 消费积压和告警处理时延。健康检查只说明实例能提供服务，不说明业务结果正确。

### 缓存与 Redis 一致性

缓存保存可复用的查询结果，减少重复读取和数据库压力。测站最新状态、权限字典和短期统计适合缓存；原始监测记录、审计日志和需要强一致的版本检查仍以 PostgreSQL 为准。缓存键包含租户、测站、查询版本和单位，值里带生成时间与数据版本，界面显示缓存时间，用户才不会把一个旧快照当成实时水位。

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

清单C.1在写入事务提交后通过5.7节的提交后事件让缓存失效；事务回滚时不触发失效，旧缓存仍然正确。生产环境给不同缓存设 TTL 和容量上限，序列化用受控的 JSON 类型；JPA 实体和懒加载代理不能直接写进 Redis，序列化时会触发懒加载或者带出一堆用不着的字段。缓存命中、未命中、序列化失败和驱逐次数都做成指标，否则说不清缓存有没有真的减轻数据库压力。

缓存有三类常见风险。缓存穿透：大量请求查不存在的测站，每次都落到数据库，对策是对空结果短暂缓存、校验 ID 格式、限流。缓存击穿：一个热门键在同一时刻过期，大量请求同时去查库，对策是互斥锁、逻辑过期或预热任务。缓存雪崩：大量键同时过期或 Redis 集群故障，对策是随机 TTL、分批预热、熔断和数据库限流。降级读旧快照时标注时间和可信等级，不能装作“最新”。

### 分页、游标与查询预算

页码分页适合需要跳转和精确总数的管理界面，游标分页适合不断追加的时序数据。游标是“上一页最后一条记录的位置”：对一个测点来说，`(occurredAt, version)`是主键去掉对象编码后剩下的部分，不会并列（5.4.3节），游标就由最后一条记录的这两项组成，服务端编码或签名后作为不透明字符串返回；下一页用`(occurredAt, version) < (cursorTime, cursorVersion)`的联合条件，第一千页和第一页一样快，`OFFSET`则要先扫过前面所有行。游标绑定原查询的过滤条件和过期时间，客户端改不了边界。

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

清单C.2多取一条记录判断还有没有下一页，省掉一次`count(*)`；生产实现给游标签名或存在服务端，客户端改不了时间和对象编码。分页请求限制时间范围、单页大小和并发导出任务数，大范围报表转成异步任务返回任务 ID。性能预算写进接口契约：P95 查询时延、最大返回字节数和连接占用上限。

### 连接池与慢查询定位

连接池是应用预先打开、反复复用的一组数据库连接，请求要访问数据库时借一个，用完还回去。连接数太多，PostgreSQL 为每个连接开一个进程，争抢 CPU 和内存；太少，请求排队等连接。初始值按数据库最大连接数、服务实例数和后台任务估算，再用压测调。HikariCP 的连接超时、最大生命周期、空闲超时和泄漏检测都写明单位，日志显示池里活动、空闲、等待的连接数；只看 HTTP 线程数看不出连接池的问题。

慢查询沿“请求—Repository—SQL—执行计划”这条链定位。结构化日志带 traceId 和查询名，Micrometer 记耗时分位数；PostgreSQL 慢查询日志和`pg_stat_statements`给出 SQL 级证据；`EXPLAIN (ANALYZE, BUFFERS)`看有没有命中联合索引、有没有 N+1 或大范围顺序扫描（5.4.10节）。优化后重新压测，比较 P95、锁等待、缓存命中和连接池排队；本地跑一次得出的结论不算数。清单C.3是一组可以直接抄进`application.yml`的起始值，池大小与超时写明单位，慢查询阈值与日志开关一并列出。

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

清单里的默认值用于开发验证，生产值由容量评估和压测报告定。泄漏检测用来发现忘了关的流或失控的事务边界，找到以后要修，不是一直开着它。SQL 日志在生产环境脱敏并控制采样率，否则测站数据和参数全进了日志。连接池耗尽时触发告警和限流，服务返回 503 或可解释的降级结果，等待有上限。

### Actuator、Micrometer 与结构化日志

Actuator 是 Spring Boot 自带的一组运维端点（健康检查、指标、配置、线程转储等），按暴露风险分组。健康检查可以公开进程存活和依赖状态；指标端点只给运维员；`env`、`configprops`和线程转储在生产环境默认关闭，或经严格授权。健康状态分 liveness、readiness 和业务可用（第8章8.6.1节）：数据库不可达时实例还活着，但不该再接写入流量。

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

清单C.4把健康检查和业务指标分开：健康检查回答“实例能不能工作”，指标回答“处理质量和容量怎样”。指标标签用有限的枚举值，如质量码、结果类型和服务版本；测站 ID、用户 ID 或完整 URL 这类取值成千上万的标签会让监控系统的时间序列爆炸。运维告警的阈值与第8章8.1节参数表里的工程阈值是两回事，运维告警不改业务预警标准。

**表 C.1  后端性能与可运维关键指标**

| 指标                | 采集位置               | 处置动作                         |
|:--------------------|:-----------------------|:---------------------------------|
| HTTP P95/P99 延迟   | Micrometer Timer、网关 | 按路由定位慢查询或下游超时       |
| 连接池活动/等待数   | Hikari 指标            | 调整池大小、限流并检查事务泄漏   |
| 缓存命中率/驱逐数   | Redis 客户端           | 调整 TTL、键设计和预热策略       |
| Kafka 积压/死信数   | 消费者组、DLT          | 扩容消费者、修复模式或补发事件   |
| 错误率与401/403/503 | 结构化日志、计数器     | 区分客户端、权限、依赖和发布故障 |

表C.1里的指标都能关联到同一个 traceId 和发布版本，运维员才能从告警跳到具体请求和日志。指标只做趋势和阈值判断，根因还要看日志、执行计划和消息偏移量。告警规则设冷却时间、恢复通知和责任角色，同一个故障不在网关、服务、数据库和 Kafka 四层各报一遍。

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

清单C.5在请求进入时建立 traceId，离开线程前清理 MDC（日志框架里跟着当前线程走的一组键值），线程池复用线程时才不会串号。Kafka 事件、数据库审计、Redis 操作和异步任务显式传 traceId；跨服务只传可追踪的 ID，Authorization 头不进日志。结构化日志的字段固定为时间、级别、服务、版本、traceId、事件类型、耗时和结果码，中文描述作补充，机器能检索，人也能复核。

性能优化和容量、恢复一起验收。一次压测记录并发请求、P95/P99、数据库连接、缓存命中、Kafka 积压、错误分类和 CPU/内存；故障演练再看 Redis 不可用、数据库慢查询、Kafka 延迟和下游超时各自的降级结果。每项优化保留开关、回滚配置和前后对比；为了单次吞吐牺牲数据可信度或审计完整性，不划算。

### 性能故障的分层处置

接口变慢时，先用 traceId 看这次请求把时间花在了哪一段：网关排队、控制器参数校验、服务业务规则、数据库查询、Redis 访问还是 Kafka 发送。网关慢查连接和限流，服务慢查线程池和外部超时，数据库慢查执行计划、锁等待和连接池，缓存异常查命中率、序列化和网络延迟，消息积压查分区热点和消费者处理时间。分层看，问题才不会都归结成“数据库不够快”。

降级要保住业务语义。测站最新状态查询可以在短时间内返回标注时间的缓存快照；原始观测写入优先保证落库，消息通知通过发件箱延后；预警评估所需数据质量不足时返回“未评估”，不生成等级结论；权限和审计服务不可用时，高风险写操作拒绝并返回 503。每种降级记录原因、开始时间、影响的接口和恢复条件，恢复后自动清除或由运维员确认。

Actuator 和日志端点本身也是攻击面。只暴露健康和必要的指标，端点放在独立的管理网段或由 Spring Security 保护；健康详情不显示数据库地址、用户名、异常堆栈和令牌配置。结构化日志用 JSON 输出，敏感字段进 MDC 之前脱敏，异常堆栈关联内部事件 ID，不回显给客户端。日志采样跳过的只能是常规请求，安全失败、事务回滚、死信和数据拒收这几类事件一条都不能丢。

连接池和线程池一起估算。一个请求可能先占着数据库连接，再等 Kafka 回调或外部 HTTP：线程数远大于连接池，请求就在等连接；连接池远大于数据库容量，锁竞争就被放大。用压测数据定最大并发、队列长度、拒绝策略和优雅停机时间；停机先停止接收新消息，再等正在处理的事务提交或回滚，最后关连接池。健康检查等资源准备好了才报告 ready，滚动发布就不会把半初始化的实例放进流量。

缓存、分页和指标的配置纳入版本管理。每次改 TTL、最大页大小、连接池或告警阈值，变更记录写明预期收益、风险、验证查询和回滚值；环境变量覆盖只改部署参数，不改案例水库的工程参数。运维手册给一条从指标告警到日志、SQL、Kafka 偏移量和发布版本的排查路径，值班员照着走就能复现和升级问题。每次演练结束后归档指标快照、关键日志、执行计划和复盘结论，标上数据版本和运行环境，下一轮容量评估才有可比较的基线。
