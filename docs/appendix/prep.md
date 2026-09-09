# 附录B 开发环境与语言衔接预备

本附录面向已经学过一门程序设计语言（Python、Java、C 或 C#）、但没有做过 Web 工程的读者，只补第4、5章正文默认已经会的三件事：在终端里运行和观察一个服务（P0）、从“会写 Java 类”走到“能读懂 Spring Boot 工程”（P2）、从“知道表”走到“能写出第5章需要的 SQL 和事务”（P3）。每个单元末尾的自测题做得出来，就可以直接进入对应章节；做不出来，按标注回到该单元的小节。本附录不讲语言语法。

## P0 终端、端口与浏览器开发者工具

**要解决的问题**

第4章第一次让你“启动教学接口，再启动开发服务器，然后在网络面板看请求”。这句话里有四个前提：知道当前目录在哪、知道两个程序为什么能同时运行、知道 8080 和 5173 是什么、知道去哪里看一次请求的状态码。

**目录与路径**

终端里的每条命令都在“当前目录”执行。`pwd`（Windows PowerShell 同样可用）打印当前目录，`cd companion/water-platform-demo`进入配套工程，`ls`（PowerShell 亦可用`dir`）列出内容。教材中所有相对路径都以配套工程根目录为起点：`node teaching-api/server.mjs`必须在`water-platform-demo`目录下执行，否则报“找不到模块”。路径写错是第一次实验最常见的失败原因，报错信息里一定会打印它尝试打开的完整路径，先核对这一行。

**进程与端口**

一个正在运行的程序是一个进程；网络服务进程会“监听”一个端口号，浏览器通过`主机:端口`找到它。本书约定：教学接口与真实后端都监听 8080，Vite 开发服务器监听 5173。两个进程同时运行需要两个终端窗口（或一个窗口里先后启动并保持前台不退出）。端口被占用时会报`EADDRINUSE`，说明上一次的进程还没退出：在那个终端按 Ctrl+C 结束它，或换端口`node teaching-api/server.mjs 8081`并同步修改 Vite 代理目标。

**读懂一条错误信息**

错误信息从下往上读。清单11.1是把路径写错时 Node 打出的信息，最后几行是调用栈，可以忽略；关键是第一行的错误码`ERR_MODULE_NOT_FOUND`和它后面的完整路径。浏览器控制台的错误同理：先看红色第一行的类型与文字，再看它指向的文件与行号。

**清单 11.1  一条典型的错误信息：先看错误码与路径**

```bash
$ node teaching-api/server.mjs
node:internal/modules/esm/resolve:264
    throw new ERR_MODULE_NOT_FOUND(...)
Error [ERR_MODULE_NOT_FOUND]: Cannot find module
  'D:\course\teaching-api\server.mjs' imported from D:\course\
    at finalizeResolution (node:internal/modules/esm/resolve:264:11)
    ...
{ code: 'ERR_MODULE_NOT_FOUND' }
# 解读：当前目录是 D:\course，而不是 water-platform-demo；先 cd 再运行
```

**浏览器开发者工具**

按 F12 打开。“控制台”看脚本输出与错误；“网络”面板列出页面发出的每一个请求，点开一条可以看到请求方法与路径、请求头（第4章的`Authorization`就在这里）、状态码、耗时和响应体。表11.1把第4、5章会用到的面板与用途对应起来；做第4章 4.5 节的实验前，先在网络面板里找到`POST /api/auth/login`这一条，确认你能看到它的响应体。

**表 11.1  第4、5章用到的开发者工具面板**

| 面板   | 看什么                                                   | 教材中的使用位置                             |
|:-------|:---------------------------------------------------------|:---------------------------------------------|
| 控制台 | 脚本输出、未捕获错误、`console.log`                      | 4.4 节示例、4.5 节 Promise 落定顺序          |
| 网络   | 每个请求的路径、状态码、请求头、响应体、耗时、是否被取消 | 4.5.2 运行记录、4.5.4 验证记录、5.6 认证联调 |
| 元素   | 当前 DOM 结构与 CSS 生效情况                             | 4.2、4.3 节                                  |
| 应用   | `sessionStorage` 中的令牌                                | 4.5.5 request.js                             |

**自测**

（1）不查资料，写出在配套工程根目录启动教学接口和开发服务器各用哪条命令、分别监听哪个端口。（2）故意把`node teaching-api/server.mjs`在上一级目录运行，找出错误信息里指出的完整路径。（3）打开 4.5 节阶段页后，在网络面板里指出`GET /api/assets`的响应体有多少个元素。三题都能完成即可进入第4章。

## P2 从 Java 类到 Spring Boot 工程

**要解决的问题**

你会写`class`、方法、`List`和`try/catch`，但第5章的清单里出现`@RestController`、`record`、构造器里凭空出现的参数，以及一个叫 Maven 的东西。本单元只解释读懂第5章工程需要的四个概念：工程目录、依赖与构建、注解、依赖注入。

**工程目录与 Maven**

Spring Boot 工程的源代码在`src/main/java`下按包名分目录，测试在`src/test/java`，配置在`src/main/resources/application.yml`。`pom.xml`是 Maven 的工程描述：它声明工程用到的第三方库（依赖）和 Java 版本，`mvn test`会自动下载依赖、编译、运行测试。你不需要手工管理 jar 文件；第一次执行会下载较多文件，之后走本地缓存。清单11.2是配套工程`pom.xml`中与第5章直接相关的片段。

**清单 11.2  pom.xml 片段：Java 版本与第5章用到的起步依赖**

```xml
<properties>
  <java.version>17</java.version>
</properties>
<dependencies>
  <dependency> <!-- Web：HTTP 接口、JSON 序列化 -->
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
  </dependency>
  <dependency> <!-- 数据访问：JPA 与 PostgreSQL 驱动在 5.4 节使用 -->
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
  </dependency>
  <dependency> <!-- 安全：5.6 节认证与权限 -->
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
  </dependency>
</dependencies>
```

**注解**

以`@`开头的注解是附在类、方法或参数上的标记，本身不执行任何逻辑；框架启动时扫描这些标记来决定“这个类要作为 HTTP 入口”“这个方法响应 GET 请求”。清单11.3是第5章第一个接口的最小形态，注解的含义写在注释里。`record`是 Java 17 的不可变数据类，一行声明就得到构造器、访问方法和`equals`，第5章用它表示接口的请求与响应。

**清单 11.3  最小的 HTTP 接口：注解告诉框架“这是入口”**

```java
package edu.example.qingyuan;

import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController                 // 这个类的方法返回 JSON，而不是页面
@RequestMapping("/api/assets")  // 类内所有路径的公共前缀，与 8.1 节契约一致
public class AssetController {
    public record AssetDto(String assetId, String displayName,
                           String assetType, String unit) {}

    private final AssetRepository assets;   // 由框架注入，见下文

    public AssetController(AssetRepository assets) {
        this.assets = assets;
    }

    @GetMapping                  // GET /api/assets
    public List<AssetDto> assets() {
        return assets.findByActiveTrueOrderByAssetId().stream()
            .map(e -> new AssetDto(e.getAssetId(), e.getDisplayName(),
                                   e.getAssetType(), e.getUnit()))
            .toList();
    }
}
```

**依赖注入**

清单11.3里没有任何一行`new AssetController(...)`，也没有`new AssetRepository()`，程序却能运行。框架在启动时创建所有带注解的类的实例（称为 Bean），并按构造器参数类型把需要的实例传进去——这就是依赖注入。它解决的问题是“对象之间怎么互相拿到对方”：类只声明“我需要一个 AssetRepository”，不关心它是数据库实现还是测试替身。第5章 5.2 节解释它的使用规则，Bean 的作用域与代理机制属于拓展。

**自测**

（1）说出`src/main/java`、`src/test/java`、`application.yml`、`pom.xml`各放什么。（2）把清单11.3中的`@GetMapping`删掉，预计访问`GET /api/assets`会得到什么状态码？（404：方法不再是入口。）（3）`AssetController`的构造器参数从哪里来？（框架注入，不是调用方 new 出来的。）

## P3 表、键、SQL 与事务

**要解决的问题**

第5章 5.4 节直接使用外键、参数化查询和事务，第8章的数据模型用复合主键与唯一索引保证观测不重复。本单元用案例水库的两张表把这些概念讲一遍，SQL 均可在配套工程的 PostgreSQL 中执行。

**表、行、列与键**

表11.2是第8章数据模型的教学子集：`asset`存工程对象（含测点），`reading`存观测。主键唯一标识一行；`reading.asset_id`是外键，指向`asset.asset_id`，数据库拒绝写入不存在的对象的观测。`reading`的主键由三列组成（复合主键），表达“同一对象、同一时刻、同一版本只能有一条”。空值`NULL`表示“没有值”，与 0 不同：缺测的观测`value`为`NULL`且`quality`为`missing`。

**表 11.2  第5章使用的两张表（第8章数据模型的教学子集）**

| 表      | 列                                                             | 约束                                                                                                                                |
|:--------|:---------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------|
| asset   | asset_id、asset_type、display_name、unit、active               | 主键 asset_id                                                                                                                       |
| reading | asset_id、occurred_at、version、event_id、value、unit、quality | 复合主键 (asset_id, occurred_at, version)；外键 asset_id；quality 只能是 valid/suspect/missing；value 为空时 quality 必须为 missing |

**四条基本语句**

清单11.4给出第5章需要的全部 SQL 形态：建表、插入、按条件查询、更新。`WHERE`里的条件决定影响哪些行；忘写`WHERE`的`UPDATE`会改掉整张表。`$1`是参数占位符：程序里绝不把用户输入拼进 SQL 字符串，而是把值作为参数传给驱动，这是 5.4 节“参数化访问”的含义，也是防止 SQL 注入的唯一正确做法。

**清单 11.4  第5章需要的 SQL 形态：建表、插入、查询、更新**

```sql
CREATE TABLE asset (
  asset_id     text PRIMARY KEY,
  asset_type   text NOT NULL,
  display_name text NOT NULL,
  unit         text,
  active       boolean NOT NULL DEFAULT true
);
CREATE TABLE reading (
  asset_id    text NOT NULL REFERENCES asset(asset_id),
  occurred_at timestamptz NOT NULL,
  version     integer NOT NULL DEFAULT 1,
  event_id    text NOT NULL,
  value       numeric,
  unit        text NOT NULL,
  quality     text NOT NULL CHECK (quality IN ('valid','suspect','missing')),
  PRIMARY KEY (asset_id, occurred_at, version),
  CHECK (value IS NOT NULL OR quality = 'missing')
);

INSERT INTO asset VALUES ('DAM-A-PZ-07', '渗压', '案例渗压07', 'kPa', true);
INSERT INTO reading (asset_id, occurred_at, event_id, value, unit, quality)
VALUES ('DAM-A-PZ-07', '2026-07-01T23:55:00+08:00', 'evt-pz-0287-6', 185.091, 'kPa', 'valid');

-- 参数化查询：$1、$2 由程序传入，不拼接字符串
SELECT occurred_at, value, quality FROM reading
 WHERE asset_id = $1 AND occurred_at >= $2 AND occurred_at < $3
 ORDER BY occurred_at;

UPDATE asset SET active = false WHERE asset_id = 'DAM-A-PZ-07';
```

**事务**

事务把几条语句捆成一个整体：要么全部生效，要么全部不生效。第8章“确认预警并创建工单”要同时更新`warning`表和插入`work_order`表，两条语句之间进程崩溃会留下“预警已确认但没有工单”的半成品，事务就是为此存在。清单11.5用最简单的形式演示：`BEGIN`开始，`COMMIT`提交，出错时`ROLLBACK`撤销。第5章 5.5 节把它写进 Java 的`@Transactional`，传播行为与隔离级别属于拓展。

**清单 11.5  事务：两条语句要么都生效，要么都不生效**

```sql
BEGIN;
UPDATE warning SET status = 'acknowledged'
 WHERE warning_id = 2 AND status = 'open';       -- 条件更新：只有 open 才能确认
INSERT INTO work_order (warning_id, owner_role, due_at, action)
VALUES (2, '值班员', '2026-07-02T08:00:00+08:00', '现场复核 PZ-07');
COMMIT;                                           -- 中途出错则 ROLLBACK，两张表都不变
```

**自测**

（1）向`reading`插入`asset_id`为`DAM-A-PZ-99`的一行会发生什么？为什么？（外键拒绝：对象不存在。）（2）再插入一条与清单11.4中完全相同时刻、相同版本的 PZ-07 观测会发生什么？（复合主键冲突；第8章用它实现幂等写入。）（3）清单11.5中若`UPDATE`影响了 0 行，是否还应该`COMMIT`？（不应该：说明预警已不是 open，工单不该创建，应 ROLLBACK 并向调用方返回冲突。）
