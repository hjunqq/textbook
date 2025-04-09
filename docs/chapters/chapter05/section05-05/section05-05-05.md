# 5.5.5 水利数据库应用案例

## 案例一：水文监测数据库

**需求分析**：
- 存储全省水文站点实时和历史监测数据
- 支持高频写入和多维度查询
- 数据按时间自动归档
- 支持水位、流量、降雨等多类型数据

**数据库选型**：
- 实时数据：TimescaleDB (PostgreSQL扩展)
- 归档数据：按年分区表
- 元数据：PostgreSQL

**概念模型**：

```
站点(StationID, StationName, RiverName, Location, ...)
    |
    +--> 水位数据(ID, StationID, Timestamp, WaterLevel, ...)
    |
    +--> 流量数据(ID, StationID, Timestamp, FlowRate, ...)
    |
    +--> 降雨数据(ID, StationID, Timestamp, Rainfall, ...)
```

**物理模型(SQL)**：

```sql
-- 站点表
CREATE TABLE stations (
    station_id VARCHAR(20) PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL,
    river_name VARCHAR(100),
    basin_name VARCHAR(100),
    longitude DECIMAL(9,6) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    elevation DECIMAL(8,2),
    drainage_area DECIMAL(10,2),
    station_type VARCHAR(50),
    install_date DATE,
    warning_level DECIMAL(6,2),
    management_unit VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 使用TimescaleDB创建水位数据表
CREATE TABLE water_level_data (
    id BIGSERIAL PRIMARY KEY,
    station_id VARCHAR(20) NOT NULL,
    measurement_time TIMESTAMP NOT NULL,
    water_level DECIMAL(6,2) NOT NULL,
    data_quality VARCHAR(20),
    data_source VARCHAR(50),
    remark TEXT,
    FOREIGN KEY (station_id) REFERENCES stations(station_id)
);

-- 转换为超表(Hypertable)
SELECT create_hypertable('water_level_data', 'measurement_time', 
                         chunk_time_interval => INTERVAL '1 day');

-- 创建压缩策略
ALTER TABLE water_level_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'station_id'
);

-- 创建压缩策略(7天后压缩)
SELECT add_compression_policy('water_level_data', INTERVAL '7 days');

-- 创建保留策略(保留3年数据)
SELECT add_retention_policy('water_level_data', INTERVAL '3 years');

-- 创建连续聚合视图(小时平均水位)
CREATE MATERIALIZED VIEW water_level_hourly
WITH (timescaledb.continuous) AS
SELECT 
    station_id,
    time_bucket('1 hour', measurement_time) AS hour,
    AVG(water_level) AS avg_level,
    MIN(water_level) AS min_level,
    MAX(water_level) AS max_level,
    COUNT(*) AS sample_count
FROM water_level_data
GROUP BY station_id, hour;

-- 设置连续聚合策略
SELECT add_continuous_aggregate_policy('water_level_hourly',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');
```

**优化措施**：
1. 使用TimescaleDB的分块存储提高查询性能
2. 建立连续聚合视图加速统计查询
3. 设置数据压缩和保留策略
4. 使用空间索引优化地理位置查询

## 案例二：水库调度决策支持数据库

**需求分析**：
- 存储水库基本信息和物理特性
- 记录水库运行状态和历史调度记录
- 支持调度计划管理
- 集成气象水文预报数据
- 支持调度方案模拟和评估

**数据库选型**：
- 关系型数据库：PostgreSQL
- 缓存层：Redis
- 文档数据库：MongoDB (非结构化数据)

**概念模型**：

```
水库(ReservoirID, Name, Location, Capacity, ...)
    |
    +--> 物理特性(ID, ReservoirID, StorageCapacityCurve, ...)
    |
    +--> 运行状态(ID, ReservoirID, Timestamp, WaterLevel, Storage, ...)
    |
    +--> 调度计划(PlanID, ReservoirID, StartDate, EndDate, Status, ...)
          |
          +--> 计划详情(ID, PlanID, Timestamp, TargetWaterLevel, ...)
    |
    +--> 调度记录(ID, ReservoirID, Timestamp, Inflow, Outflow, ...)
```

**实现示例**：

```sql
-- 水库基本信息
CREATE TABLE reservoirs (
    reservoir_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    river_name VARCHAR(100),
    longitude DECIMAL(9,6) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    total_capacity DECIMAL(12,4) NOT NULL COMMENT '总库容(亿立方米)',
    flood_capacity DECIMAL(12,4) COMMENT '防洪库容(亿立方米)',
    dead_capacity DECIMAL(12,4) COMMENT '死库容(亿立方米)',
    normal_high_level DECIMAL(8,2) COMMENT '正常蓄水位(米)',
    flood_limit_level DECIMAL(8,2) COMMENT '汛限水位(米)',
    dead_level DECIMAL(8,2) COMMENT '死水位(米)',
    dam_type VARCHAR(50),
    completion_year INT,
    management_unit VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active'
);

-- 水库调度计划
CREATE TABLE reservoir_scheduling_plans (
    plan_id VARCHAR(36) PRIMARY KEY,
    reservoir_id VARCHAR(20) NOT NULL,
    plan_name VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    description TEXT,
    plan_type VARCHAR(50) NOT NULL COMMENT '调度类型: 防洪/发电/供水/生态',
    status VARCHAR(20) DEFAULT 'draft' COMMENT '状态: draft/approved/executing/completed/cancelled',
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by VARCHAR(50),
    approved_at TIMESTAMP,
    FOREIGN KEY (reservoir_id) REFERENCES reservoirs(reservoir_id)
);

-- 调度计划详情
CREATE TABLE scheduling_plan_details (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    plan_id VARCHAR(36) NOT NULL,
    target_date DATE NOT NULL,
    target_water_level DECIMAL(8,2) NOT NULL,
    target_outflow DECIMAL(10,2) COMMENT '目标下泄流量(立方米/秒)',
    power_generation DECIMAL(10,2) COMMENT '计划发电量(万千瓦时)',
    remarks TEXT,
    FOREIGN KEY (plan_id) REFERENCES reservoir_scheduling_plans(plan_id),
    UNIQUE KEY (plan_id, target_date)
);

-- 水库运行状态
CREATE TABLE reservoir_status (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    reservoir_id VARCHAR(20) NOT NULL,
    measurement_time TIMESTAMP NOT NULL,
    water_level DECIMAL(8,2) NOT NULL COMMENT '水位(米)',
    storage DECIMAL(12,4) COMMENT '库容(亿立方米)',
    inflow DECIMAL(10,2) COMMENT '入库流量(立方米/秒)',
    outflow DECIMAL(10,2) COMMENT '出库流量(立方米/秒)',
    power_generation DECIMAL(10,2) COMMENT '发电量(万千瓦时)',
    data_source VARCHAR(50),
    FOREIGN KEY (reservoir_id) REFERENCES reservoirs(reservoir_id),
    INDEX idx_reservoir_time (reservoir_id, measurement_time)
);
```

**优化措施**：
1. 对实时状态数据使用Redis缓存
2. 历史数据按时间进行分区
3. 为时间范围查询建立复合索引
4. 使用存储过程优化复杂计算

## 案例三：水利工程安全监测数据库

**需求分析**：
- 存储大坝安全监测点信息和历史数据
- 支持多种类型的监测数据(位移、渗流、应力等)
- 实现监测数据异常检测和预警
- 提供数据分析和趋势预测功能

**数据库选型**：
- 实时数据：InfluxDB
- 关系数据：PostgreSQL
- 空间数据：PostGIS扩展

**InfluxDB数据模型示例**：

```
// 表结构设计
measurement: dam_deformation
tags:
  - dam_id
  - monitor_point_id
  - monitor_type
  - location_zone

fields:
  - x_displacement
  - y_displacement
  - z_displacement
  - temperature
  - humidity
  - measurement_quality

// 查询示例
SELECT MEAN(x_displacement) FROM dam_deformation 
WHERE dam_id='dam001' AND location_zone='crest' 
AND time > NOW() - 30d 
GROUP BY monitor_point_id, time(1d)
```

**预警规则表(PostgreSQL)**：

```sql
CREATE TABLE monitor_alert_rules (
    rule_id SERIAL PRIMARY KEY,
    dam_id VARCHAR(20) NOT NULL,
    monitor_type VARCHAR(50) NOT NULL,
    location_zone VARCHAR(50),
    monitor_point_id VARCHAR(50),
    alert_type VARCHAR(50) NOT NULL,
    threshold_value DECIMAL(10,4),
    threshold_unit VARCHAR(20),
    comparison_operator VARCHAR(10) NOT NULL,
    time_window VARCHAR(50),
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (dam_id, monitor_type, monitor_point_id, alert_type)
);
```

**优化措施**：
1. 使用InfluxDB高效存储时间序列监测数据
2. 基于时间窗口预计算异常检测指标
3. 对长期监测数据进行降采样处理
4. 使用PostgreSQL存储元数据和预警规则 