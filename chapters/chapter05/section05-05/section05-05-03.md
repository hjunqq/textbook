# 5.5.3 NoSQL数据库

## NoSQL数据库概述

NoSQL(Not Only SQL)数据库是一类非关系型数据库，设计用于处理关系型数据库难以高效处理的数据模型和访问模式。

**NoSQL特点**：
- 灵活的数据模型
- 高扩展性
- 高性能
- 无固定模式

## 键值存储数据库

键值数据库使用简单的键值对存储数据，适合需要快速访问的场景。

**代表产品**：Redis, DynamoDB, Memcached

**Redis示例**：
```
// 存储实时水位数据
SET station:ST001:water_level 102.5
// 设置过期时间
EXPIRE station:ST001:water_level 3600
// 获取实时水位
GET station:ST001:water_level

// 使用Hash存储站点信息
HMSET station:ST001 name "金沙江站" river "金沙江" longitude 104.0668 latitude 30.5728
// 获取特定字段
HGET station:ST001 name
// 获取所有信息
HGETALL station:ST001
```

**在智慧水利中的应用**：
- 实时监测数据缓存
- 会话管理
- 排行榜和计数器
- 分布式锁

## 文档型数据库

文档数据库存储半结构化的文档数据，通常是JSON或BSON格式。

**代表产品**：MongoDB, CouchDB

**MongoDB示例**：
```javascript
// 存储水文站点信息
db.stations.insertOne({
    station_id: "ST001",
    name: "金沙江站",
    location: {
        type: "Point",
        coordinates: [104.0668, 30.5728]
    },
    river: "金沙江",
    elevation: 450.5,
    sensors: [
        { type: "water_level", status: "active", install_date: ISODate("2020-01-15") },
        { type: "flow_rate", status: "active", install_date: ISODate("2020-01-15") },
        { type: "rainfall", status: "maintenance", install_date: ISODate("2020-01-15") }
    ],
    warning_levels: {
        blue: 95.0,
        yellow: 98.0,
        orange: 101.0,
        red: 103.0
    },
    status: "active"
})

// 查询特定流域的站点
db.stations.find({ river: "金沙江" })

// 地理空间查询
db.stations.find({
    location: {
        $near: {
            $geometry: {
                type: "Point",
                coordinates: [104.0, 30.5]
            },
            $maxDistance: 10000  // 10公里内
        }
    }
})
```

**在智慧水利中的应用**：
- 水利工程设施管理
- 传感器和监测点配置
- 灵活结构的业务数据存储
- 空间数据管理

## 列式数据库

列式数据库按列而非行存储数据，适合大规模分析查询。

**代表产品**：Cassandra, HBase

**在智慧水利中的应用**：
- 大规模水文历史数据存储
- 传感器时间序列数据
- 分布式监测系统

## 时序数据库

时序数据库专为时间序列数据设计，具有高写入率和高效的时间范围查询能力。

**代表产品**：InfluxDB, TimescaleDB, OpenTSDB

**InfluxDB示例**：
```
// 写入水位数据
INSERT water_levels,station=ST001,river=jinsha_river water_level=102.5 1634567890000000000

// 查询最近24小时平均水位
SELECT MEAN(water_level) FROM water_levels 
WHERE station='ST001' AND time > NOW() - 24h 
GROUP BY time(1h)

// 降采样和保留策略
CREATE RETENTION POLICY "one_year" ON "water_monitoring" DURATION 52w REPLICATION 1
```

**在智慧水利中的应用**：
- 实时水文监测数据存储
- 水库水位变化分析
- 长期历史数据存档 