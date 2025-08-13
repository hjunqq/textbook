# 第三节 监测数据处理与展示模块

## 引言

监测数据处理与展示模块是智慧水利平台的核心组件，负责接收、处理、存储和展示来自各种监测设备的实时数据。该模块必须处理海量、高频、多源的监测数据，同时保证数据的准确性、完整性和实时性。

本节将详细介绍监测数据处理与展示模块的设计理念、技术架构、关键算法和实现方案，为构建高效、稳定的数据处理系统提供指导。

## 8.3.1 数据采集与预处理

### 多源数据接入架构

```javascript
class DataIngestionPlatform {
    constructor(config) {
        this.config = config;
        this.collectors = new Map();
        this.processors = new Map();
        this.messageQueue = null;
        this.initialize();
    }
    
    initialize() {
        // 初始化消息队列
        this.messageQueue = this.createMessageQueue();
        
        // 注册数据采集器
        this.registerCollectors();
        
        // 启动数据处理流水线
        this.startProcessingPipeline();
    }
    
    registerCollectors() {
        // 串口数据采集器
        this.collectors.set('serial', new SerialDataCollector({
            ports: this.config.serialPorts,
            baudRate: 9600,
            protocol: 'modbus'
        }));
        
        // TCP/UDP网络采集器
        this.collectors.set('network', new NetworkDataCollector({
            endpoints: this.config.networkEndpoints,
            protocols: ['tcp', 'udp', 'http']
        }));
        
        // MQTT消息采集器
        this.collectors.set('mqtt', new MQTTDataCollector({
            broker: this.config.mqttBroker,
            topics: this.config.mqttTopics,
            qos: 1
        }));
        
        // 数据库轮询采集器
        this.collectors.set('database', new DatabasePollingCollector({
            connections: this.config.databaseConnections,
            queries: this.config.pollingQueries,
            interval: 30000 // 30秒轮询一次
        }));
        
        // 文件监视采集器
        this.collectors.set('file', new FileWatcherCollector({
            directories: this.config.watchDirectories,
            patterns: ['*.csv', '*.json', '*.xml']
        }));
    }
    
    async startCollector(collectorType) {
        const collector = this.collectors.get(collectorType);
        if (!collector) {
            throw new Error(`未知的采集器类型: ${collectorType}`);
        }
        
        try {
            await collector.start();
            
            // 监听数据事件
            collector.on('data', (rawData) => {
                this.handleRawData(rawData, collectorType);
            });
            
            collector.on('error', (error) => {
                this.handleCollectorError(error, collectorType);
            });
            
            console.log(`${collectorType} 数据采集器启动成功`);
        } catch (error) {
            console.error(`启动 ${collectorType} 采集器失败:`, error);
            throw error;
        }
    }
    
    handleRawData(rawData, sourceType) {
        // 数据标准化
        const standardizedData = this.standardizeData(rawData, sourceType);
        
        // 发送到消息队列
        this.messageQueue.publish('raw_data', {
            data: standardizedData,
            source: sourceType,
            timestamp: new Date().toISOString(),
            messageId: this.generateMessageId()
        });
    }
    
    standardizeData(rawData, sourceType) {
        const standardizers = {
            serial: this.standardizeSerialData,
            network: this.standardizeNetworkData,
            mqtt: this.standardizeMQTTData,
            database: this.standardizeDatabaseData,
            file: this.standardizeFileData
        };
        
        const standardizer = standardizers[sourceType];
        return standardizer ? standardizer(rawData) : rawData;
    }
}
```

### 数据质量控制

```python
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

class DataQualityController:
    """数据质量控制器"""
    
    def __init__(self, config):
        self.config = config
        self.quality_rules = self.load_quality_rules()
        self.statistics = {
            'total_records': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'corrected_records': 0
        }
        
    def process_data_batch(self, data_batch):
        """批量处理数据质量检查"""
        results = []
        
        for record in data_batch:
            # 基础有效性检查
            if not self.basic_validation(record):
                self.statistics['invalid_records'] += 1
                continue
            
            # 数据范围检查
            range_check_result = self.range_validation(record)
            if range_check_result['status'] == 'invalid':
                self.statistics['invalid_records'] += 1
                continue
            elif range_check_result['status'] == 'corrected':
                record = range_check_result['data']
                self.statistics['corrected_records'] += 1
            
            # 时间序列一致性检查
            temporal_check_result = self.temporal_consistency_check(record)
            if temporal_check_result['status'] == 'invalid':
                self.statistics['invalid_records'] += 1
                continue
            elif temporal_check_result['status'] == 'corrected':
                record = temporal_check_result['data']
                self.statistics['corrected_records'] += 1
            
            # 多维数据关联性检查
            correlation_check_result = self.correlation_check(record)
            if correlation_check_result['status'] == 'invalid':
                self.statistics['invalid_records'] += 1
                continue
            
            # 标记数据质量等级
            record['quality_level'] = self.calculate_quality_level(record)
            record['quality_flags'] = self.generate_quality_flags(record)
            
            results.append(record)
            self.statistics['valid_records'] += 1
            
        self.statistics['total_records'] += len(data_batch)
        return results
    
    def basic_validation(self, record):
        """基础数据有效性验证"""
        # 检查必填字段
        required_fields = ['station_id', 'parameter_type', 'value', 'timestamp']
        for field in required_fields:
            if field not in record or record[field] is None:
                logging.warning(f"记录缺少必填字段: {field}")
                return False
        
        # 检查数值类型
        try:
            float(record['value'])
        except (ValueError, TypeError):
            logging.warning(f"无效的数值: {record['value']}")
            return False
        
        # 检查时间戳格式
        try:
            pd.to_datetime(record['timestamp'])
        except:
            logging.warning(f"无效的时间戳: {record['timestamp']}")
            return False
        
        return True
    
    def range_validation(self, record):
        """数据范围验证"""
        station_id = record['station_id']
        parameter_type = record['parameter_type']
        value = float(record['value'])
        
        # 获取参数范围配置
        range_config = self.get_parameter_range(station_id, parameter_type)
        if not range_config:
            return {'status': 'valid', 'data': record}
        
        min_value = range_config['min_value']
        max_value = range_config['max_value']
        soft_min = range_config.get('soft_min', min_value)
        soft_max = range_config.get('soft_max', max_value)
        
        # 硬边界检查（绝对不可能的值）
        if value < min_value or value > max_value:
            logging.warning(f"数值超出硬边界: {value} not in [{min_value}, {max_value}]")
            return {'status': 'invalid', 'data': record}
        
        # 软边界检查（可疑但可能的值）
        if value < soft_min or value > soft_max:
            # 尝试修正
            corrected_value = np.clip(value, soft_min, soft_max)
            record['value'] = corrected_value
            record['correction_flag'] = f"value_clipped_from_{value}_to_{corrected_value}"
            logging.info(f"数值已修正: {value} -> {corrected_value}")
            return {'status': 'corrected', 'data': record}
        
        return {'status': 'valid', 'data': record}
    
    def temporal_consistency_check(self, record):
        """时间一致性检查"""
        current_time = pd.to_datetime(record['timestamp'])
        current_value = float(record['value'])
        
        # 获取历史数据进行对比
        historical_data = self.get_recent_historical_data(
            record['station_id'], 
            record['parameter_type'],
            hours=24
        )
        
        if len(historical_data) < 2:
            return {'status': 'valid', 'data': record}
        
        # 计算变化率
        last_record = historical_data.iloc[-1]
        last_value = float(last_record['value'])
        time_diff = (current_time - pd.to_datetime(last_record['timestamp'])).total_seconds() / 3600
        
        if time_diff <= 0:
            logging.warning("时间戳顺序错误")
            return {'status': 'invalid', 'data': record}
        
        # 检查变化率是否合理
        change_rate = abs(current_value - last_value) / time_diff
        max_change_rate = self.get_max_change_rate(record['parameter_type'])
        
        if change_rate > max_change_rate:
            # 检查是否为系统性偏移
            if self.detect_systematic_shift(historical_data, current_value):
                # 可能是传感器校准或设备更换
                record['quality_flag'] = 'possible_sensor_change'
                return {'status': 'valid', 'data': record}
            else:
                logging.warning(f"异常变化率: {change_rate} > {max_change_rate}")
                return {'status': 'invalid', 'data': record}
        
        return {'status': 'valid', 'data': record}
    
    def correlation_check(self, record):
        """多参数关联性检查"""
        station_id = record['station_id']
        parameter_type = record['parameter_type']
        current_value = float(record['value'])
        
        # 获取同站点其他参数的当前值
        related_parameters = self.get_related_parameters(station_id, parameter_type)
        
        for related_param in related_parameters:
            correlation_rule = self.get_correlation_rule(parameter_type, related_param['type'])
            if not correlation_rule:
                continue
            
            # 执行关联性检查
            is_consistent = self.check_parameter_correlation(
                current_value, 
                related_param['value'],
                correlation_rule
            )
            
            if not is_consistent:
                logging.warning(f"参数关联性异常: {parameter_type}={current_value} vs {related_param['type']}={related_param['value']}")
                # 根据置信度决定是否拒绝数据
                if correlation_rule['confidence'] > 0.8:
                    return {'status': 'invalid', 'data': record}
                else:
                    record['quality_flag'] = 'correlation_warning'
        
        return {'status': 'valid', 'data': record}
    
    def calculate_quality_level(self, record):
        """计算数据质量等级"""
        score = 100  # 基础分数
        
        # 根据各种质量指标扣分
        if 'correction_flag' in record:
            score -= 10
        
        if 'quality_flag' in record:
            if record['quality_flag'] == 'correlation_warning':
                score -= 15
            elif record['quality_flag'] == 'possible_sensor_change':
                score -= 5
        
        # 根据历史稳定性调整
        stability_score = self.calculate_stability_score(record)
        score = score * (stability_score / 100)
        
        # 分级
        if score >= 95:
            return 'excellent'
        elif score >= 85:
            return 'good'
        elif score >= 70:
            return 'acceptable'
        elif score >= 50:
            return 'poor'
        else:
            return 'very_poor'
```

### 实时数据处理流水线

```javascript
class RealTimeProcessingPipeline {
    constructor(config) {
        this.config = config;
        this.stages = [];
        this.metrics = new ProcessingMetrics();
        this.errorHandler = new ErrorHandler();
        
        this.setupPipeline();
    }
    
    setupPipeline() {
        // 阶段1：数据接收与解析
        this.stages.push(new DataReceivingStage({
            inputSources: this.config.inputSources,
            bufferSize: 10000,
            batchSize: 100
        }));
        
        // 阶段2：数据验证与清洗
        this.stages.push(new DataValidationStage({
            validationRules: this.config.validationRules,
            cleaningStrategies: this.config.cleaningStrategies
        }));
        
        // 阶段3：数据补全与插值
        this.stages.push(new DataComplementStage({
            interpolationMethods: ['linear', 'polynomial', 'spline'],
            maxGapDuration: 3600 // 1小时
        }));
        
        // 阶段4：异常检测
        this.stages.push(new AnomalyDetectionStage({
            algorithms: ['isolation_forest', 'statistical', 'lstm'],
            thresholds: this.config.anomalyThresholds
        }));
        
        // 阶段5：数据聚合与计算
        this.stages.push(new DataAggregationStage({
            aggregationWindows: ['1min', '5min', '1hour', '1day'],
            derivedParameters: this.config.derivedParameters
        }));
        
        // 阶段6：数据存储分发
        this.stages.push(new DataDistributionStage({
            storageTargets: this.config.storageTargets,
            realtimeChannels: this.config.realtimeChannels
        }));
    }
    
    async processDataStream(dataStream) {
        let currentData = dataStream;
        
        for (let i = 0; i < this.stages.length; i++) {
            const stage = this.stages[i];
            const startTime = Date.now();
            
            try {
                // 执行处理阶段
                currentData = await stage.process(currentData);
                
                // 记录性能指标
                const processingTime = Date.now() - startTime;
                this.metrics.recordStageMetrics(stage.name, {
                    processingTime,
                    inputCount: Array.isArray(currentData) ? currentData.length : 1,
                    outputCount: Array.isArray(currentData) ? currentData.length : 1
                });
                
                // 检查数据是否为空（可能被过滤掉）
                if (!currentData || (Array.isArray(currentData) && currentData.length === 0)) {
                    break;
                }
                
            } catch (error) {
                // 错误处理
                const handled = await this.errorHandler.handleStageError(error, stage, currentData);
                
                if (!handled) {
                    // 无法恢复的错误，中断处理
                    throw new Error(`Pipeline stage ${stage.name} failed: ${error.message}`);
                }
                
                // 使用错误处理结果继续
                currentData = handled.data;
            }
        }
        
        return currentData;
    }
    
    // 批处理模式
    async processBatch(dataBatch) {
        const results = [];
        const errors = [];
        
        for (const dataItem of dataBatch) {
            try {
                const result = await this.processDataStream(dataItem);
                if (result) {
                    results.push(result);
                }
            } catch (error) {
                errors.push({
                    data: dataItem,
                    error: error.message,
                    timestamp: new Date().toISOString()
                });
            }
        }
        
        return {
            results,
            errors,
            summary: {
                totalInput: dataBatch.length,
                successCount: results.length,
                errorCount: errors.length,
                successRate: (results.length / dataBatch.length * 100).toFixed(2) + '%'
            }
        };
    }
    
    // 获取处理统计信息
    getProcessingStats() {
        return {
            pipeline: {
                stages: this.stages.map(stage => ({
                    name: stage.name,
                    status: stage.status,
                    processedCount: stage.processedCount,
                    errorCount: stage.errorCount
                }))
            },
            metrics: this.metrics.getSummary(),
            errors: this.errorHandler.getErrorSummary()
        };
    }
}
```

## 8.3.2 数据存储与管理

### 时序数据库设计

```python
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd
from datetime import datetime, timedelta

class TimeSeriesDataManager:
    """时序数据管理器"""
    
    def __init__(self, config):
        self.config = config
        self.influx_client = influxdb_client.InfluxDBClient(
            url=config['influxdb']['url'],
            token=config['influxdb']['token'],
            org=config['influxdb']['org']
        )
        self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.influx_client.query_api()
        self.bucket = config['influxdb']['bucket']
        
        # 数据保留策略
        self.retention_policies = {
            'raw_data': '90d',      # 原始数据保留90天
            'minute_avg': '1y',     # 分钟均值保留1年
            'hour_avg': '5y',       # 小时均值保留5年
            'day_avg': '20y'        # 日均值保留20年
        }
        
        self.setup_retention_policies()
    
    def write_real_time_data(self, data_points):
        """写入实时数据"""
        points = []
        
        for data_point in data_points:
            point = (
                influxdb_client.Point(data_point['measurement'])
                .tag("station_id", data_point['station_id'])
                .tag("parameter_type", data_point['parameter_type'])
                .tag("data_source", data_point.get('data_source', 'unknown'))
                .field("value", float(data_point['value']))
                .field("quality_level", data_point.get('quality_level', 'unknown'))
                .time(data_point['timestamp'])
            )
            
            # 添加额外的标签和字段
            if 'location' in data_point:
                point.tag("location", data_point['location'])
            
            if 'quality_flags' in data_point:
                point.field("quality_flags", data_point['quality_flags'])
                
            if 'additional_fields' in data_point:
                for key, value in data_point['additional_fields'].items():
                    point.field(key, value)
            
            points.append(point)
        
        try:
            self.write_api.write(bucket=self.bucket, record=points)
            return True
        except Exception as e:
            print(f"写入数据失败: {e}")
            return False
    
    def query_time_range_data(self, station_id, parameter_type, start_time, end_time, aggregation=None):
        """查询时间范围数据"""
        
        # 构建基础查询
        query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})
            |> filter(fn: (r) => r["_measurement"] == "monitoring_data")
            |> filter(fn: (r) => r["station_id"] == "{station_id}")
            |> filter(fn: (r) => r["parameter_type"] == "{parameter_type}")
            |> filter(fn: (r) => r["_field"] == "value")
        '''
        
        # 添加聚合函数
        if aggregation:
            if aggregation['type'] == 'mean':
                query += f'|> aggregateWindow(every: {aggregation["window"]}, fn: mean, createEmpty: false)'
            elif aggregation['type'] == 'max':
                query += f'|> aggregateWindow(every: {aggregation["window"]}, fn: max, createEmpty: false)'
            elif aggregation['type'] == 'min':
                query += f'|> aggregateWindow(every: {aggregation["window"]}, fn: min, createEmpty: false)'
        
        query += '|> yield(name: "result")'
        
        try:
            result = self.query_api.query(query=query)
            
            # 转换为pandas DataFrame
            data = []
            for table in result:
                for record in table.records:
                    data.append({
                        'timestamp': record.get_time(),
                        'value': record.get_value(),
                        'station_id': record.values.get('station_id'),
                        'parameter_type': record.values.get('parameter_type')
                    })
            
            return pd.DataFrame(data)
        
        except Exception as e:
            print(f"查询数据失败: {e}")
            return pd.DataFrame()
    
    def create_continuous_queries(self):
        """创建连续查询用于数据聚合"""
        
        # 分钟级聚合
        minute_query = '''
            CREATE CONTINUOUS QUERY "cq_minute_avg" ON "{database}"
            BEGIN
                SELECT mean("value") AS "mean_value",
                       max("value") AS "max_value",
                       min("value") AS "min_value",
                       count("value") AS "count"
                INTO "minute_avg"
                FROM "raw_data"
                GROUP BY time(1m), *
            END
        '''.format(database=self.bucket)
        
        # 小时级聚合
        hour_query = '''
            CREATE CONTINUOUS QUERY "cq_hour_avg" ON "{database}"
            BEGIN
                SELECT mean("mean_value") AS "mean_value",
                       max("max_value") AS "max_value",
                       min("min_value") AS "min_value",
                       sum("count") AS "count"
                INTO "hour_avg"
                FROM "minute_avg"
                GROUP BY time(1h), *
            END
        '''.format(database=self.bucket)
        
        # 日级聚合
        day_query = '''
            CREATE CONTINUOUS QUERY "cq_day_avg" ON "{database}"
            BEGIN
                SELECT mean("mean_value") AS "mean_value",
                       max("max_value") AS "max_value",
                       min("min_value") AS "min_value",
                       sum("count") AS "count"
                INTO "day_avg"
                FROM "hour_avg"
                GROUP BY time(1d), *
            END
        '''.format(database=self.bucket)
        
        return [minute_query, hour_query, day_query]
    
    def optimize_storage(self):
        """存储优化"""
        
        # 压缩旧数据
        compress_query = '''
            SELECT mean("value") as "value"
            INTO "compressed_data"
            FROM "raw_data"
            WHERE time < now() - 7d
            GROUP BY time(5m), *
        '''
        
        # 删除已压缩的原始数据
        delete_query = '''
            DELETE FROM "raw_data"
            WHERE time < now() - 7d
        '''
        
        try:
            self.query_api.query(compress_query)
            self.query_api.query(delete_query)
            return True
        except Exception as e:
            print(f"存储优化失败: {e}")
            return False
    
    def get_data_statistics(self, station_id=None, start_time=None, end_time=None):
        """获取数据统计信息"""
        
        filters = []
        if station_id:
            filters.append(f'r["station_id"] == "{station_id}"')
        if start_time:
            filters.append(f'r._time >= {start_time.isoformat()}')
        if end_time:
            filters.append(f'r._time <= {end_time.isoformat()}')
        
        filter_clause = ' and '.join(filters) if filters else 'true'
        
        query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -30d)
            |> filter(fn: (r) => {filter_clause})
            |> group(columns: ["station_id", "parameter_type"])
            |> count()
        '''
        
        try:
            result = self.query_api.query(query=query)
            statistics = {}
            
            for table in result:
                for record in table.records:
                    station = record.values.get('station_id')
                    parameter = record.values.get('parameter_type')
                    count = record.get_value()
                    
                    if station not in statistics:
                        statistics[station] = {}
                    statistics[station][parameter] = count
            
            return statistics
        
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {}
```

### 数据缓存策略

```javascript
class DataCacheManager {
    constructor(config) {
        this.config = config;
        this.memoryCache = new Map();
        this.redisClient = this.createRedisClient(config.redis);
        this.cacheStrategies = this.initializeCacheStrategies();
        
        // 缓存统计
        this.stats = {
            hits: 0,
            misses: 0,
            writes: 0,
            evictions: 0
        };
        
        this.setupCacheCleanup();
    }
    
    initializeCacheStrategies() {
        return {
            // 实时数据缓存（内存）
            realtime: {
                storage: 'memory',
                ttl: 300, // 5分钟
                maxSize: 10000,
                evictionPolicy: 'LRU'
            },
            
            // 历史数据缓存（Redis）
            historical: {
                storage: 'redis',
                ttl: 3600, // 1小时
                keyPattern: 'hist:{station_id}:{parameter}:{period}',
                compression: true
            },
            
            // 聚合数据缓存
            aggregated: {
                storage: 'redis',
                ttl: 7200, // 2小时
                keyPattern: 'agg:{type}:{period}:{station_id}',
                compression: false
            },
            
            // 查询结果缓存
            query_result: {
                storage: 'redis',
                ttl: 1800, // 30分钟
                keyPattern: 'query:{hash}',
                compression: true
            }
        };
    }
    
    async get(key, strategy = 'realtime') {
        const strategyConfig = this.cacheStrategies[strategy];
        
        try {
            let value;
            
            if (strategyConfig.storage === 'memory') {
                value = this.getFromMemory(key);
            } else if (strategyConfig.storage === 'redis') {
                value = await this.getFromRedis(key, strategyConfig);
            }
            
            if (value) {
                this.stats.hits++;
                return value;
            } else {
                this.stats.misses++;
                return null;
            }
        } catch (error) {
            console.error(`缓存获取失败: ${error.message}`);
            this.stats.misses++;
            return null;
        }
    }
    
    async set(key, value, strategy = 'realtime', customTTL = null) {
        const strategyConfig = this.cacheStrategies[strategy];
        const ttl = customTTL || strategyConfig.ttl;
        
        try {
            if (strategyConfig.storage === 'memory') {
                this.setToMemory(key, value, ttl, strategyConfig);
            } else if (strategyConfig.storage === 'redis') {
                await this.setToRedis(key, value, ttl, strategyConfig);
            }
            
            this.stats.writes++;
            return true;
        } catch (error) {
            console.error(`缓存设置失败: ${error.message}`);
            return false;
        }
    }
    
    getFromMemory(key) {
        const item = this.memoryCache.get(key);
        if (!item) return null;
        
        // 检查是否过期
        if (item.expiry && Date.now() > item.expiry) {
            this.memoryCache.delete(key);
            return null;
        }
        
        // 更新访问时间（用于LRU）
        item.lastAccess = Date.now();
        return item.value;
    }
    
    setToMemory(key, value, ttl, strategyConfig) {
        // 检查缓存大小限制
        if (this.memoryCache.size >= strategyConfig.maxSize) {
            this.evictFromMemory(strategyConfig.evictionPolicy);
        }
        
        const expiry = ttl ? Date.now() + ttl * 1000 : null;
        this.memoryCache.set(key, {
            value: value,
            expiry: expiry,
            lastAccess: Date.now(),
            createdAt: Date.now()
        });
    }
    
    evictFromMemory(policy) {
        if (policy === 'LRU') {
            // 找到最久未访问的项目
            let oldestKey = null;
            let oldestTime = Date.now();
            
            for (const [key, item] of this.memoryCache) {
                if (item.lastAccess < oldestTime) {
                    oldestTime = item.lastAccess;
                    oldestKey = key;
                }
            }
            
            if (oldestKey) {
                this.memoryCache.delete(oldestKey);
                this.stats.evictions++;
            }
        }
    }
    
    async getFromRedis(key, strategyConfig) {
        let value = await this.redisClient.get(key);
        
        if (value && strategyConfig.compression) {
            value = this.decompress(value);
        }
        
        return value ? JSON.parse(value) : null;
    }
    
    async setToRedis(key, value, ttl, strategyConfig) {
        let serializedValue = JSON.stringify(value);
        
        if (strategyConfig.compression) {
            serializedValue = this.compress(serializedValue);
        }
        
        if (ttl) {
            await this.redisClient.setex(key, ttl, serializedValue);
        } else {
            await this.redisClient.set(key, serializedValue);
        }
    }
    
    // 批量缓存操作
    async mget(keys, strategy = 'realtime') {
        const results = {};
        const missedKeys = [];
        
        // 先从缓存获取
        for (const key of keys) {
            const value = await this.get(key, strategy);
            if (value !== null) {
                results[key] = value;
            } else {
                missedKeys.push(key);
            }
        }
        
        return {
            results,
            missedKeys
        };
    }
    
    async mset(keyValuePairs, strategy = 'realtime') {
        const promises = [];
        
        for (const [key, value] of Object.entries(keyValuePairs)) {
            promises.push(this.set(key, value, strategy));
        }
        
        const results = await Promise.all(promises);
        return results.every(result => result === true);
    }
    
    // 智能缓存预热
    async warmupCache(stationIds, parameters, timeRange) {
        console.log('开始缓存预热...');
        
        const promises = [];
        
        for (const stationId of stationIds) {
            for (const parameter of parameters) {
                // 预热最近24小时的数据
                const promise = this.preloadTimeSeriesData(
                    stationId, 
                    parameter, 
                    timeRange
                );
                promises.push(promise);
            }
        }
        
        await Promise.all(promises);
        console.log('缓存预热完成');
    }
    
    async preloadTimeSeriesData(stationId, parameter, timeRange) {
        const cacheKey = `hist:${stationId}:${parameter}:${timeRange.start}-${timeRange.end}`;
        
        // 检查是否已缓存
        const cached = await this.get(cacheKey, 'historical');
        if (cached) return;
        
        // 从数据库加载数据
        const data = await this.loadDataFromDatabase(stationId, parameter, timeRange);
        
        // 缓存数据
        await this.set(cacheKey, data, 'historical');
    }
    
    // 缓存统计信息
    getStats() {
        const hitRate = this.stats.hits / (this.stats.hits + this.stats.misses) * 100;
        
        return {
            ...this.stats,
            hitRate: hitRate.toFixed(2) + '%',
            memoryUsage: {
                size: this.memoryCache.size,
                maxSize: this.cacheStrategies.realtime.maxSize
            }
        };
    }
    
    // 清理过期缓存
    setupCacheCleanup() {
        setInterval(() => {
            this.cleanupExpiredMemoryCache();
        }, 60000); // 每分钟清理一次
    }
    
    cleanupExpiredMemoryCache() {
        const now = Date.now();
        let cleanedCount = 0;
        
        for (const [key, item] of this.memoryCache) {
            if (item.expiry && now > item.expiry) {
                this.memoryCache.delete(key);
                cleanedCount++;
            }
        }
        
        if (cleanedCount > 0) {
            console.log(`清理了 ${cleanedCount} 个过期缓存项`);
        }
    }
}
```

## 小结

监测数据处理与展示模块是智慧水利平台的数据处理核心，通过多源数据接入、质量控制、实时处理流水线和高效的存储缓存机制，确保了数据的完整性、准确性和实时性。

**关键要点总结**：

1. **数据接入**：建立多源异构数据的统一接入框架，支持各种数据采集方式

2. **质量控制**：实施严格的数据质量检查和清洗流程，保证数据的可靠性

3. **实时处理**：构建高效的数据处理流水线，支持大规模实时数据处理

4. **存储管理**：采用时序数据库和智能缓存策略，平衡性能和存储成本

在下一节中，我们将探讨应急响应与决策支持系统的设计与实现。



## 思考题与练习

### 基础题

1. 请简述本节的核心概念，并说明其在智慧水利平台开发中的重要性。
2. 总结本节介绍的主要技术方法，并分析各方法的适用场景。
3. 结合智慧水利的实际需求，解释本节内容如何应用于实际项目中。

### 提高题

4. 分析本节涉及的技术难点，并提出可能的解决方案。
5. 比较本节介绍的不同方法的优缺点，并给出选择建议。
6. 设计一个简单的案例，说明如何将本节理论应用于智慧水利系统设计。

### 讨论题

7. 讨论本节内容与其他相关技术的集成方案，分析可能遇到的挑战。
8. 展望本节涉及技术的发展趋势，分析其对智慧水利未来发展的影响。

## 本节小结

本节内容为智慧水利平台的设计和开发提供了重要的理论基础和技术指导。通过学习本节内容，学生应能够理解相关概念的内涵和应用价值，掌握基本的分析方法和设计原则，为后续章节的学习和实际项目的开展奠定坚实基础。
