# 数据库与存储环境配置

> 本小节是[第四节 开发环境配置与工具使用](section03-04.md)的一部分

数据库和存储系统是智慧水利平台的核心组成部分，负责管理和存储各类水利数据，包括实时监测数据、历史数据、GIS空间数据等。本小节将详细介绍智慧水利平台常用的数据库与存储环境配置方法，涵盖关系型数据库、NoSQL数据库、时序数据库以及对象存储等内容。

## 3.4.4.1 关系型数据库环境

关系型数据库在智慧水利平台中主要用于存储结构化业务数据，如用户信息、站点信息、设备管理、权限管理等。

### PostgreSQL配置

PostgreSQL是智慧水利平台常用的开源关系型数据库，尤其是结合PostGIS扩展，能够高效处理空间数据。

**安装与基本配置**：

1. **Windows安装**：
   ```bash
   # 从PostgreSQL官网下载安装包
   # 运行安装程序，按照向导完成安装
   # 通常会安装PostgreSQL服务器、pgAdmin管理工具
   ```

2. **Linux(Ubuntu)安装**：
   ```bash
   # 添加PostgreSQL仓库
   sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
   wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
   
   # 更新包信息并安装
   sudo apt-get update
   sudo apt-get install postgresql-14 postgresql-contrib-14
   
   # 安装PostGIS扩展
   sudo apt-get install postgresql-14-postgis-3
   ```

3. **Docker安装**：
   ```bash
   # 拉取PostgreSQL镜像
   docker pull postgres:14
   
   # 启动PostgreSQL容器
   docker run --name postgres-water -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres:14
   
   # 带PostGIS的镜像
   docker pull postgis/postgis:14-3.3
   docker run --name postgis-water -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgis/postgis:14-3.3
   ```

**性能优化配置**：

PostgreSQL配置文件(postgresql.conf)中的关键性能参数：

```ini
# 内存配置
shared_buffers = 2GB                # 1/4系统内存建议值
work_mem = 32MB                     # 复杂查询使用的内存
maintenance_work_mem = 256MB        # 维护操作使用的内存
effective_cache_size = 6GB          # 系统缓存的估计值，通常设为系统内存的1/2

# 写入性能
wal_buffers = 16MB                  # WAL缓冲区大小
synchronous_commit = off            # 禁用同步提交可提高性能
checkpoint_completion_target = 0.9  # 控制检查点写入速度

# 并发设置
max_connections = 100               # 最大并发连接数
max_worker_processes = 8            # 后台工作进程数
max_parallel_workers_per_gather = 4 # 每个查询的并行工作进程数
max_parallel_workers = 8            # 最大并行工作进程数
```

**PostGIS扩展设置**：

在PostgreSQL中启用PostGIS扩展用于空间数据处理：

```sql
-- 创建数据库
CREATE DATABASE water_gis;

-- 连接到新数据库
\c water_gis

-- 启用PostGIS扩展
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION postgis_raster;

-- 验证安装
SELECT PostGIS_version();
```

**数据库备份配置**：

配置定时备份：

```bash
# 创建备份脚本
cat > backup_postgres.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump -U postgres -d water_gis -F c -f $BACKUP_DIR/water_gis_$DATE.dump
find $BACKUP_DIR -name "water_gis_*.dump" -type f -mtime +7 -delete
EOF

# 设置执行权限
chmod +x backup_postgres.sh

# 添加到crontab
echo "0 2 * * * /path/to/backup_postgres.sh" | crontab -
```

### MySQL/MariaDB配置

MySQL和MariaDB也是智慧水利平台中常用的关系型数据库。

**安装与基本配置**：

1. **Windows安装**：
   ```bash
   # 从MySQL官网下载安装包
   # 运行安装程序，按照向导完成安装
   ```

2. **Linux(Ubuntu)安装**：
   ```bash
   # MySQL
   sudo apt-get update
   sudo apt-get install mysql-server
   
   # MariaDB
   sudo apt-get update
   sudo apt-get install mariadb-server
   
   # 配置安全设置
   sudo mysql_secure_installation
   ```

3. **Docker安装**：
   ```bash
   # MySQL
   docker pull mysql:8.0
   docker run --name mysql-water -e MYSQL_ROOT_PASSWORD=mysecretpassword -p 3306:3306 -d mysql:8.0
   
   # MariaDB
   docker pull mariadb:10.6
   docker run --name mariadb-water -e MYSQL_ROOT_PASSWORD=mysecretpassword -p 3306:3306 -d mariadb:10.6
   ```

**性能优化配置**：

MySQL配置文件(my.cnf)中的关键性能参数：

```ini
[mysqld]
# 内存配置
innodb_buffer_pool_size = 2G       # 通常为系统内存的50%-70%
innodb_log_file_size = 256M        # 重做日志文件大小
innodb_log_buffer_size = 16M       # 日志缓冲区大小
key_buffer_size = 128M             # MyISAM表索引缓存大小

# 并发设置
max_connections = 150              # 最大连接数
thread_cache_size = 8              # 线程缓存大小
innodb_read_io_threads = 8         # 读I/O线程数
innodb_write_io_threads = 8        # 写I/O线程数

# 优化设置
innodb_flush_log_at_trx_commit = 2 # 为持久性和性能之间取平衡
innodb_flush_method = O_DIRECT     # Linux系统上推荐
innodb_file_per_table = 1          # 每个表使用单独的文件
```

**空间数据支持**：

MySQL 8.0+ 内置对空间数据的支持：

```sql
-- 创建具有空间数据的表
CREATE TABLE water_stations (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    name VARCHAR(100) NOT NULL,
    location POINT NOT NULL,
    SPATIAL INDEX(location)
);

-- 插入空间数据
INSERT INTO water_stations (name, location)
VALUES ('Station A', ST_GeomFromText('POINT(121.48 31.22)'));

-- 空间查询示例
SELECT name, ST_AsText(location) 
FROM water_stations 
WHERE ST_Distance(location, ST_GeomFromText('POINT(121.45 31.20)')) < 5000;
```

## 3.4.4.2 NoSQL数据库环境

NoSQL数据库在智慧水利平台中用于处理非结构化或半结构化数据，如设备状态、日志、传感器数据等。

### MongoDB配置

MongoDB是一个文档型NoSQL数据库，适合存储JSON格式的灵活数据结构。

**安装与基本配置**：

1. **Windows安装**：
   ```bash
   # 从MongoDB官网下载安装包
   # 运行安装程序，按照向导完成安装
   ```

2. **Linux(Ubuntu)安装**：
   ```bash
   # 导入公钥
   wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
   
   # 添加源
   echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
   
   # 安装
   sudo apt-get update
   sudo apt-get install -y mongodb-org
   
   # 启动服务
   sudo systemctl start mongod
   sudo systemctl enable mongod
   ```

3. **Docker安装**：
   ```bash
   # 拉取MongoDB镜像
   docker pull mongo:5.0
   
   # 启动MongoDB容器
   docker run --name mongo-water -p 27017:27017 -d mongo:5.0
   ```

**配置文件设置**：

MongoDB配置文件(mongod.conf)关键设置：

```yaml
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
  wiredTiger:
    engineConfig:
      cacheSizeGB: 2   # 适当调整缓存大小

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

net:
  port: 27017
  bindIp: 127.0.0.1    # 生产环境应设置为具体IP或0.0.0.0

security:
  authorization: enabled  # 启用身份验证

operationProfiling:
  slowOpThresholdMs: 100  # 慢查询阈值
  mode: slowOp
```

**创建用户与授权**：

设置MongoDB访问安全：

```javascript
// 连接MongoDB
mongo

// 切换到admin数据库
use admin

// 创建管理员用户
db.createUser({
  user: "admin",
  pwd: "securePassword",
  roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
})

// 认证
db.auth("admin", "securePassword")

// 创建应用程序用户
use water_monitoring
db.createUser({
  user: "water_app",
  pwd: "appPassword",
  roles: [ { role: "readWrite", db: "water_monitoring" } ]
})
```

**数据模型示例**：

水位监测站点的MongoDB数据模型：

```javascript
// 水位站点集合
db.stations.insertOne({
  code: "STA001",
  name: "长江南京站",
  location: {
    type: "Point",
    coordinates: [118.7965, 32.0584]  // 经度, 纬度
  },
  type: "river",
  parameters: ["water_level", "flow_rate", "rainfall"],
  warningLevels: {
    attention: 10.0,
    warning: 12.0,
    danger: 14.0
  },
  status: "active",
  createdAt: new Date(),
  modifiedAt: new Date()
})

// 水位数据集合
db.waterLevels.insertOne({
  stationCode: "STA001",
  timestamp: new Date(),
  values: {
    water_level: 8.75,
    flow_rate: 2450,
    rainfall: 0
  },
  quality: {
    source: "sensor",
    verified: false
  }
})

// 创建索引
db.stations.createIndex({ code: 1 }, { unique: true })
db.stations.createIndex({ location: "2dsphere" })
db.waterLevels.createIndex({ stationCode: 1, timestamp: -1 })
```

### Redis配置

Redis是一个高性能的键值存储数据库，在智慧水利平台中常用于缓存、会话存储和消息队列。

**安装与基本配置**：

1. **Windows安装**：
   ```bash
   # 由于官方不支持Windows，使用Microsoft提供的版本或WSL
   # 从https://github.com/microsoftarchive/redis/releases下载
   ```

2. **Linux(Ubuntu)安装**：
   ```bash
   sudo apt-get update
   sudo apt-get install redis-server
   
   # 启动服务
   sudo systemctl start redis-server
   sudo systemctl enable redis-server
   ```

3. **Docker安装**：
   ```bash
   # 拉取Redis镜像
   docker pull redis:6.2
   
   # 启动Redis容器
   docker run --name redis-water -p 6379:6379 -d redis:6.2
   ```

**配置文件设置**：

Redis配置文件(redis.conf)关键设置：

```
# 内存配置
maxmemory 1gb
maxmemory-policy allkeys-lru

# 持久化配置
appendonly yes
appendfsync everysec

# 安全设置
requirepass StrongPassword

# 连接配置
bind 127.0.0.1
port 6379
timeout 300
tcp-keepalive 300

# 高级设置
databases 16
```

**常用缓存模式**：

在智慧水利平台中应用Redis的常见模式：

1. **实时数据缓存**：
```
# 存储最新水位数据
SET station:STA001:latest_level 8.75
# 设置过期时间（1小时）
EXPIRE station:STA001:latest_level 3600

# 哈希存储站点最新所有参数
HMSET station:STA001:latest 
  water_level 8.75 
  flow_rate 2450 
  rainfall 0 
  updated_at "2023-04-15T13:45:00Z"
```

2. **排行榜/统计数据**：
```
# 存储水位最高的前10个站点
ZADD highest_water_levels 8.75 "STA001"
ZADD highest_water_levels 9.12 "STA002"
ZADD highest_water_levels 7.33 "STA003"

# 获取排名前3的站点
ZREVRANGE highest_water_levels 0 2 WITHSCORES
```

3. **地理空间索引**：
```
# 添加站点地理位置
GEOADD stations 118.7965 32.0584 "STA001"
GEOADD stations 118.8432 31.9654 "STA002"
GEOADD stations 118.6401 32.1253 "STA003"

# 查找某个位置5公里内的站点
GEORADIUS stations 118.7800 32.0500 5 km
```

4. **消息队列/发布订阅**：
```
# 订阅水位警报消息
SUBSCRIBE water_alerts

# 发布水位警报
PUBLISH water_alerts "{\"station\":\"STA001\",\"level\":13.2,\"severity\":\"warning\"}"
```

## 3.4.4.3 时序数据库配置

时序数据库专门设计用于处理时间序列数据，非常适合智慧水利平台中的监测数据存储和分析。

### InfluxDB配置

InfluxDB是一个专为时序数据设计的数据库，适合存储水位、流量、降雨量等监测数据。

**安装与基本配置**：

1. **Windows安装**：
   ```bash
   # 从InfluxDB官网下载安装包
   # 解压并运行influxd.exe
   ```

2. **Linux(Ubuntu)安装**：
   ```bash
   # 添加仓库
   wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
   source /etc/lsb-release
   echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
   
   # 安装
   sudo apt-get update
   sudo apt-get install influxdb
   
   # 启动服务
   sudo systemctl start influxdb
   sudo systemctl enable influxdb
   ```

3. **Docker安装**：
   ```bash
   # 拉取InfluxDB镜像
   docker pull influxdb:2.3
   
   # 启动InfluxDB容器
   docker run --name influxdb-water -p 8086:8086 -v influxdb-data:/var/lib/influxdb2 -d influxdb:2.3
   ```

**配置InfluxDB 2.x**：

设置初始配置：

```bash
# 初始化设置
influx setup \
  --username admin \
  --password StrongPassword \
  --org WaterOrg \
  --bucket WaterMonitoring \
  --retention 30d \
  --force
```

**数据模型与查询示例**：

1. **使用Flux语言写入数据**：
```javascript
// 使用InfluxDB客户端库写入数据
import { InfluxDB, Point } from '@influxdata/influxdb-client'

const client = new InfluxDB({
  url: 'http://localhost:8086',
  token: 'YourAuthToken'
})

const writeApi = client.getWriteApi('WaterOrg', 'WaterMonitoring')
writeApi.useDefaultTags({ location: 'NanjingStation' })

const point = new Point('water_metrics')
  .tag('station_id', 'STA001')
  .tag('river', 'ChangJiang')
  .floatField('water_level', 8.75)
  .floatField('flow_rate', 2450)
  .timestamp(new Date())

writeApi.writePoint(point)
writeApi.close()
```

2. **使用Flux查询数据**：
```javascript
// 查询过去24小时的水位数据
const query = `
  from(bucket: "WaterMonitoring")
    |> range(start: -24h)
    |> filter(fn: (r) => r._measurement == "water_metrics" and r.station_id == "STA001")
    |> filter(fn: (r) => r._field == "water_level")
    |> aggregateWindow(every: 1h, fn: mean)
`

const queryApi = client.getQueryApi('WaterOrg')
queryApi.queryRows(query, {
  next(row, tableMeta) {
    const o = tableMeta.toObject(row)
    console.log(`${o._time}: ${o._value}`)
  },
  error(error) {
    console.error(error)
  },
  complete() {
    console.log('Query completed')
  }
})
```

### TimescaleDB配置

TimescaleDB是PostgreSQL的时序数据扩展，结合了关系数据库和时序数据库的优点。

**安装与基本配置**：

1. **在PostgreSQL中安装扩展**：
   ```bash
   # Ubuntu
   sudo apt-get install postgresql-12-timescaledb
   
   # 调整PostgreSQL配置
   sudo timescaledb-tune
   
   # 重启PostgreSQL
   sudo systemctl restart postgresql
   ```

2. **Docker安装**：
   ```bash
   # 拉取TimescaleDB镜像
   docker pull timescale/timescaledb:latest-pg14
   
   # 启动TimescaleDB容器
   docker run --name timescaledb-water -e POSTGRES_PASSWORD=password -p 5432:5432 -d timescale/timescaledb:latest-pg14
   ```

**创建时序表**：

```sql
-- 连接数据库
\c water_monitoring

-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建普通表
CREATE TABLE water_levels (
  time TIMESTAMPTZ NOT NULL,
  station_id TEXT NOT NULL,
  water_level DOUBLE PRECISION,
  flow_rate DOUBLE PRECISION,
  rainfall DOUBLE PRECISION
);

-- 转换为超表(hypertable)
SELECT create_hypertable('water_levels', 'time');

-- 创建索引
CREATE INDEX ON water_levels (station_id, time DESC);

-- 设置保留策略(数据保留13个月)
SELECT add_retention_policy('water_levels', INTERVAL '13 months');
```

**数据查询示例**：

```sql
-- 插入数据
INSERT INTO water_levels (time, station_id, water_level, flow_rate, rainfall)
VALUES (NOW(), 'STA001', 8.75, 2450, 0);

-- 基本查询：获取最近24小时的水位数据
SELECT time, station_id, water_level
FROM water_levels
WHERE station_id = 'STA001'
  AND time > NOW() - INTERVAL '24 hours'
ORDER BY time DESC;

-- 聚合查询：按小时计算平均水位
SELECT
  time_bucket('1 hour', time) AS hour,
  station_id,
  AVG(water_level) AS avg_level
FROM water_levels
WHERE station_id = 'STA001'
  AND time > NOW() - INTERVAL '7 days'
GROUP BY hour, station_id
ORDER BY hour DESC;

-- 高级分析：计算变化率
SELECT
  time,
  station_id,
  water_level,
  (water_level - LAG(water_level) OVER (PARTITION BY station_id ORDER BY time)) / 
  EXTRACT(EPOCH FROM (time - LAG(time) OVER (PARTITION BY station_id ORDER BY time))) * 3600 AS hourly_change_rate
FROM water_levels
WHERE station_id = 'STA001'
  AND time > NOW() - INTERVAL '24 hours'
ORDER BY time DESC;
```

## 3.4.4.4 对象存储配置

对象存储系统在智慧水利平台中用于存储大量非结构化数据，如图像、视频、文档等。

### MinIO配置

MinIO是一个开源的对象存储服务器，兼容Amazon S3 API。

**安装与基本配置**：

1. **Linux服务器安装**：
   ```bash
   # 下载MinIO
   wget https://dl.min.io/server/minio/release/linux-amd64/minio
   
   # 设置执行权限
   chmod +x minio
   
   # 创建数据目录
   mkdir -p /data/minio
   
   # 运行MinIO服务
   MINIO_ROOT_USER=wateradmin MINIO_ROOT_PASSWORD=secretpassword ./minio server /data/minio --console-address ":9001"
   ```

2. **Docker安装**：
   ```bash
   # 拉取MinIO镜像
   docker pull minio/minio
   
   # 启动MinIO容器
   docker run -p 9000:9000 -p 9001:9001 \
     --name minio-water \
     -e "MINIO_ROOT_USER=wateradmin" \
     -e "MINIO_ROOT_PASSWORD=secretpassword" \
     -v /data/minio:/data \
     -d minio/minio server /data --console-address ":9001"
   ```

**使用MinIO SDK**：

Java示例：

```java
import io.minio.*;
import io.minio.errors.*;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;

public class MinioExample {
    public static void main(String[] args) {
        try {
            // 创建MinIO客户端
            MinioClient minioClient = MinioClient.builder()
                    .endpoint("http://localhost:9000")
                    .credentials("wateradmin", "secretpassword")
                    .build();

            // 检查存储桶是否存在
            boolean bucketExists = minioClient.bucketExists(
                    BucketExistsArgs.builder().bucket("water-images").build());
            if (!bucketExists) {
                // 创建存储桶
                minioClient.makeBucket(
                        MakeBucketArgs.builder().bucket("water-images").build());
            }

            // 上传文件
            String content = "测试文件内容";
            ByteArrayInputStream bais = new ByteArrayInputStream(content.getBytes("UTF-8"));
            minioClient.putObject(
                    PutObjectArgs.builder()
                            .bucket("water-images")
                            .object("test.txt")
                            .stream(bais, bais.available(), -1)
                            .contentType("text/plain")
                            .build());
            bais.close();

            System.out.println("文件上传成功");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

### S3兼容存储配置

对于云平台部署的智慧水利系统，可以使用Amazon S3或其他兼容S3的存储服务。

**AWS S3配置**：

1. **创建S3存储桶**：
   - 登录AWS管理控制台
   - 导航到S3服务
   - 创建存储桶(Bucket)
   - 配置权限和生命周期规则

2. **Java SDK使用示例**：

```java
import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.*;

import java.io.File;

public class S3Example {
    public static void main(String[] args) {
        // 创建S3客户端
        S3Client s3Client = S3Client.builder()
                .region(Region.AP_EAST_1)  // 选择适当的区域
                .credentialsProvider(ProfileCredentialsProvider.create())
                .build();

        // 上传文件
        try {
            File file = new File("./flood-report.pdf");
            PutObjectRequest request = PutObjectRequest.builder()
                    .bucket("water-reports")
                    .key("2023/flood-report.pdf")
                    .contentType("application/pdf")
                    .build();
            
            s3Client.putObject(request, RequestBody.fromFile(file));
            System.out.println("文件上传成功");
            
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            s3Client.close();
        }
    }
}
```

## 3.4.4.5 多数据库架构整合

在智慧水利平台中，通常需要整合多种类型的数据库来满足不同的存储和查询需求。

### 典型架构设计

以下是一个智慧水利平台的多数据库架构设计：

1. **PostgreSQL + PostGIS**：
   - 存储用户、权限、站点、设备等基础数据
   - 管理GIS空间数据（河流、水库、流域等）
   - 处理复杂的空间查询和分析

2. **TimescaleDB/InfluxDB**：
   - 存储监测站点的实时和历史数据
   - 处理高频时序数据的写入和查询
   - 支持时序数据的聚合和分析

3. **Redis**：
   - 缓存热点数据（最新监测值、用户会话）
   - 提供实时数据的快速访问
   - 实现消息队列和发布订阅功能

4. **MongoDB**：
   - 存储非结构化或半结构化数据
   - 管理设备状态、日志、报警信息
   - 处理灵活模式的业务数据

5. **MinIO/S3**：
   - 存储图像、视频、报告文档
   - 管理大数据文件和历史数据归档
   - 提供高可靠的文件存储服务

### 微服务环境中的数据库配置

在微服务架构下配置多数据库环境：

```yaml
# docker-compose.yml 示例
version: '3.8'

services:
  postgres:
    image: postgis/postgis:14-3.3
    container_name: water-postgres
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: water_platform
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - water-net

  timescaledb:
    image: timescale/timescaledb:latest-pg14
    container_name: water-timescale
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: water_monitoring
    ports:
      - "5433:5432"
    volumes:
      - timescale-data:/var/lib/postgresql/data
    networks:
      - water-net

  redis:
    image: redis:6.2
    container_name: water-redis
    command: redis-server --requirepass redispassword
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - water-net

  mongodb:
    image: mongo:5.0
    container_name: water-mongo
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: mongopassword
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db
    networks:
      - water-net

  minio:
    image: minio/minio
    container_name: water-minio
    environment:
      MINIO_ROOT_USER: wateradmin
      MINIO_ROOT_PASSWORD: miniopassword
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio-data:/data
    command: server /data --console-address ":9001"
    networks:
      - water-net

networks:
  water-net:
    driver: bridge

volumes:
  postgres-data:
  timescale-data:
  redis-data:
  mongo-data:
  minio-data:
```

### 数据同步与集成

在多数据库架构中处理数据同步与集成：

1. **变更数据捕获(CDC)**：
   - 使用Debezium捕获PostgreSQL中的数据变更
   - 通过Kafka分发变更事件到各个服务和数据存储

2. **批处理ETL**：
   - 使用Apache NiFi或Spring Batch等工具
   - 定期从关系数据库抽取数据到时序数据库或数据仓库

3. **实时数据流**：
   - 使用Kafka Streams或Apache Flink处理实时数据
   - 将处理结果写入到适合的数据存储中

4. **API网关集成**：
   - 通过API网关统一数据访问接口
   - 在服务层处理跨数据库的数据整合

## 思考与练习

### 思考题

1. 在智慧水利平台中，为什么通常需要使用多种类型的数据库？不同类型的数据库在处理水利业务数据时各有哪些优势和局限性？

2. 对于智慧水利平台中的实时监测数据(如水位、流量、降雨量等)，应该选择什么类型的数据库？请比较TimescaleDB和InfluxDB的优缺点。

3. 智慧水利平台的数据存储系统需要处理大量的时空数据，如何设计一个高效的数据模型来支持空间查询和时间序列分析？

4. 随着智慧水利平台数据量的增长，数据库性能可能会下降。请讨论几种数据库性能优化和扩展策略，包括分片、复制、缓存等方面。

### 实践练习

1. 使用Docker配置一个包含PostgreSQL(PostGIS)、TimescaleDB、Redis和MinIO的开发环境，并编写简单的Java或Python程序来测试对各个数据库的基本操作。

2. 设计并实现一个水位监测数据的存储方案，要求能够高效地存储和查询大量的时序数据，并支持数据可视化和告警功能。

3. 使用PostgreSQL+PostGIS实现一个简单的空间数据管理系统，能够存储和查询河流、水库等水利设施的空间信息，并实现基于位置的查询功能。 