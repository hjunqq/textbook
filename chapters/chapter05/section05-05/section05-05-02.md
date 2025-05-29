# 5.5.2 关系型数据库

## 关系模型基础

关系型数据库基于关系模型，使用表(Table)、行(Row)、列(Column)来组织数据，表之间通过关系(Relationship)连接。

**核心概念**：
- **表(Table)**：存储数据的二维结构
- **字段(Field/Column)**：表中的列，定义数据类型
- **记录(Record/Row)**：表中的一行数据
- **主键(Primary Key)**：唯一标识一条记录的字段
- **外键(Foreign Key)**：建立表间关联的字段
- **索引(Index)**：提高查询效率的数据结构

## 常用关系型数据库

1. **MySQL**
   - 开源、易用、成熟的关系型数据库
   - 适用场景：中小型水利信息系统、业务管理系统
   - 特点：部署简单、社区活跃、功能完备

2. **PostgreSQL**
   - 功能强大的开源对象关系型数据库
   - 适用场景：需要GIS功能的水利空间数据管理
   - 特点：空间数据支持(PostGIS)、JSON支持、扩展性强

3. **Oracle**
   - 企业级关系型数据库
   - 适用场景：大型水利信息系统、关键业务系统
   - 特点：高可靠性、高性能、完善的企业级功能

## SQL基础

SQL(Structured Query Language)是关系型数据库的标准查询语言。

**主要SQL语句类型**：
- **DDL(数据定义语言)**：CREATE, ALTER, DROP
- **DML(数据操作语言)**：INSERT, UPDATE, DELETE
- **DQL(数据查询语言)**：SELECT
- **DCL(数据控制语言)**：GRANT, REVOKE

**常用SQL示例**：

```sql
-- 创建水文站点表
CREATE TABLE stations (
    station_id VARCHAR(20) PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL,
    river_name VARCHAR(100),
    longitude DECIMAL(9,6) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    elevation DECIMAL(8,2),
    warning_level DECIMAL(6,2),
    station_type VARCHAR(50),
    install_date DATE,
    status VARCHAR(20) DEFAULT 'active'
);

-- 创建水位数据表
CREATE TABLE water_level_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    station_id VARCHAR(20) NOT NULL,
    measurement_time TIMESTAMP NOT NULL,
    water_level DECIMAL(6,2) NOT NULL,
    data_quality VARCHAR(20),
    FOREIGN KEY (station_id) REFERENCES stations(station_id),
    INDEX idx_station_time (station_id, measurement_time)
);

-- 基本查询
SELECT * FROM stations WHERE river_name = '长江';

-- 聚合查询
SELECT 
    station_id, 
    MIN(water_level) AS min_level,
    MAX(water_level) AS max_level,
    AVG(water_level) AS avg_level
FROM water_level_data
WHERE measurement_time BETWEEN '2023-01-01' AND '2023-12-31'
GROUP BY station_id;

-- 关联查询
SELECT 
    s.station_name,
    w.measurement_time,
    w.water_level
FROM stations s
JOIN water_level_data w ON s.station_id = w.station_id
WHERE s.river_name = '长江'
AND w.measurement_time > NOW() - INTERVAL 24 HOUR
ORDER BY s.station_name, w.measurement_time;
```

## 事务与ACID特性

事务是数据库中的一个操作序列，这些操作要么全部执行成功，要么全部失败回滚。

**ACID特性**：
- **原子性(Atomicity)**：事务是不可分割的工作单位
- **一致性(Consistency)**：事务执行前后数据库保持一致状态
- **隔离性(Isolation)**：事务执行不受其他事务干扰
- **持久性(Durability)**：事务完成后，结果永久保存

**隔离级别**：
- 读未提交(Read Uncommitted)
- 读已提交(Read Committed)
- 可重复读(Repeatable Read)
- 串行化(Serializable)

## 索引与性能优化

索引是数据库中用于提高查询性能的数据结构。

**常用索引类型**：
- **B-Tree索引**：最常用的索引类型
- **哈希索引**：等值查询性能好
- **全文索引**：用于文本搜索
- **空间索引**：用于地理数据查询

**索引设计原则**：
1. 为常用查询条件创建索引
2. 为外键创建索引
3. 避免对经常更新的列创建索引
4. 组合索引考虑列顺序
5. 不要过度索引

**性能优化建议**：
1. 使用EXPLAIN分析查询执行计划
2. 避免全表扫描
3. 优化JOIN操作
4. 定期维护索引和统计信息
5. 合理使用分区表 