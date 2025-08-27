# 7.1 数据类型与展示方式

## 学习目标

通过本节学习，学生应能够：

- **理解水利监测数据的分类特征**：掌握水位、流量、压力、位移等不同类型监测数据的基本概念、物理特征和数据规律
- **掌握实时数据与历史数据的处理机制**：熟练运用不同时效性数据的处理策略，建立科学的数据管理体系
- **熟悉数据质量检验与异常值处理方法**：具备数据质量控制的专业技能，确保数据的准确性和可靠性
- **理解多源异构数据的标准化与融合技术**：掌握不同数据源的整合方法，实现数据的统一管理和应用

## 引言

在三维可视化的智慧水利监测系统中，**观测数据的科学分类与有效展示**是连接物理世界与数字化管理的关键桥梁。来自传感器、监测仪器、遥感设备等多种数据源的海量信息，蕴含着水利工程运行状态、水文变化规律、环境演变趋势等宝贵的决策支撑信息。

**数据类型的准确识别和合理展示**直接影响到管理人员对水利工程运行状态的理解和判断能力。与传统的二维图表不同，三维场景中的数据展示需要充分考虑空间定位、视觉层次、交互方式等多重因素，实现"数据即场景、场景即数据"的深度融合，为水利工程的智能化管理提供直观准确的决策支持。

## 7.1.1 水利监测数据分类体系

### 按监测要素分类

智慧水利平台涉及的监测数据类型繁多，根据监测对象和物理属性的不同，可以构建完整的分类管理体系。

#### **水文监测数据**

**水位数据**是水利监测中最基础且最重要的数据类型。

- **定义**：水位数据是指水体表面相对于某一基准面（如海平面、工程基准面）的高程数值，通常以米（m）为单位进行表示
- **特点**：具有连续性变化、时效性强、精度要求高的特征，是防洪调度、水资源管理的核心指标
- **优势**：获取方式相对简单、监测成本较低、实时性好，能够直观反映水体蓄量变化
- **适用场景**：河道水情监测、水库调度管理、防洪预警决策、灌溉用水调配、生态流量保障

在水利信息系统中，水位数据的标准化存储结构设计如下：

```javascript
// 水位监测数据结构标准定义
const WaterLevelData = {
    // 基础信息
    stationId: "WL001",                    // 监测站编码
    stationName: "长江大通水位站",          // 监测站名称
    riverName: "长江",                     // 所属河流
    basinCode: "YTZ",                      // 流域编码
    
    // 地理位置
    coordinates: {
        longitude: 117.625,                // 经度(度)
        latitude: 30.767,                  // 纬度(度)  
        elevation: 8.56                    // 测站基面高程(m)
    },
    
    // 监测数值
    timestamp: "2024-08-27T10:30:00+08:00", // 观测时间(ISO8601格式)
    waterLevel: 12.85,                     // 实测水位(m)
    waterLevelChange: 0.02,                // 与前次相比变化(m)
    
    // 特征水位
    characteristicLevels: {
        deadLevel: 8.0,                    // 死水位(m)
        normalLevel: 15.0,                 // 正常蓄水位(m)
        floodControlLevel: 18.0,           // 防洪限制水位(m)
        designFloodLevel: 20.5             // 设计洪水位(m)
    },
    
    // 数据质量
    dataQuality: "GOOD",                   // 数据质量等级
    validationStatus: "VALIDATED",         // 验证状态
    instrumentType: "PRESSURE_SENSOR",     // 仪器类型
    measurementAccuracy: 0.001             // 测量精度(m)
};
```

**流量数据**反映水体的动态流动特征，是水量平衡分析的关键参数。

- **定义**：流量是指单位时间内通过某一过水断面的水量，通常以立方米每秒（m³/s）为单位
- **特点**：数值变化幅度大、计算过程复杂、影响因素众多，与水位、降雨、人类活动密切相关
- **优势**：直接反映水量动态变化、支撑水资源调度决策、为防洪减灾提供重要依据
- **适用场景**：流域水量平衡计算、水库闸坝调度操作、取用水管理监督、河流生态流量保障

```javascript
// 流量监测数据结构标准定义  
const FlowData = {
    // 基础信息
    stationId: "FL002",                    // 流量站编码
    stationName: "黄河小浪底流量站",        // 流量站名称
    crossSectionId: "XLD_CS001",           // 断面编号
    
    // 测量数据
    timestamp: "2024-08-27T10:30:00+08:00",
    discharge: 1850.5,                     // 流量值(m³/s)
    velocity: 2.3,                         // 断面平均流速(m/s)
    crossSectionArea: 804.6,               // 过水断面面积(m²)
    correspondingWaterLevel: 188.2,        // 对应水位(m)
    
    // 计算方法
    measurementMethod: "ADCP",             // 测量方法:声学多普勒流速剖面仪
    calculationFormula: "VELOCITY_AREA",   // 计算公式
    pointsNumber: 25,                      // 测点数量
    
    // 质量评估
    dataQuality: "GOOD",                   // 数据质量
    uncertaintyLevel: 0.05,                // 不确定度
    calibrationDate: "2024-01-15"         // 率定日期
};
```

#### **工程安全监测数据**

**变形监测数据**是评估水工建筑物结构安全的重要指标。

- **定义**：变形监测数据是指通过精密测量仪器获取的工程结构位移、沉降、倾斜等形变参数
- **特点**：精度要求极高（毫米级甚至亚毫米级）、变化相对缓慢、累积性明显、与工程安全直接相关
- **优势**：能够及早发现安全隐患、为工程维护提供科学依据、支撑安全评估决策
- **适用场景**：大坝安全监测、闸站结构监控、堤防变形观测、地基沉降监测

```javascript
// 大坝变形监测数据结构定义
const DamDeformationData = {
    // 监测点信息
    pointId: "DM001",                      // 监测点编码
    pointName: "大坝表面位移点1#",          // 监测点名称
    pointType: "SURFACE_DISPLACEMENT",     // 监测点类型
    location: {
        damSection: "0+120",               // 坝轴线桩号
        elevation: 185.5,                  // 点位高程(m)
        coordinates: [116.234, 39.567, 185.5] // 三维坐标
    },
    
    // 变形测量值
    timestamp: "2024-08-27T10:30:00+08:00",
    displacement: {
        horizontal: {
            upstreamDownstream: 2.3,       // 顺河向位移(mm)
            leftRightBank: -1.2,           // 横河向位移(mm)  
            resultantHorizontal: 2.6       // 水平合位移(mm)
        },
        vertical: -0.8,                    // 竖向位移(mm)
        totalDisplacement: 2.7             // 三维总位移(mm)
    },
    
    // 变形速率
    velocity: {
        daily: 0.1,                        // 日变化率(mm/day)
        monthly: 3.2,                      // 月变化率(mm/month)
        annual: 38.5                       // 年变化率(mm/year)
    },
    
    // 环境条件
    environmentalFactors: {
        reservoirLevel: 182.3,             // 库水位(m)
        temperature: 12.5,                 // 环境温度(°C)
        atmosphericPressure: 1013.2        // 大气压力(hPa)
    },
    
    // 预警状态
    alertLevel: "NORMAL",                  // 预警等级
    thresholds: {
        attention: 10.0,                   // 关注阈值(mm)
        warning: 20.0,                     // 预警阈值(mm)
        danger: 50.0                       // 危险阈值(mm)
    }
};
```

#### **水质环境监测数据**

**水质参数数据**用于评估水体的环境质量状况和污染程度。

- **定义**：水质参数数据是指反映水体物理、化学、生物特性的各项指标数值
- **特点**：参数种类繁多、分析成本较高、变化周期相对较长、相互之间存在复杂关联
- **优势**：全面评价水环境质量、指导污染防治工作、保障饮用水安全
- **适用场景**：饮用水源地保护、工业废水监管、河流湖泊生态评估、污染事故应急响应

水质监测涉及多个关键参数，各参数特征对比如下：

| 监测参数 | 单位 | 正常范围 | 变化特征 | 监测频率 | 主要用途 |
|----------|------|----------|----------|----------|----------|
| **pH值** | - | 6.5-8.5 | 日变化明显 | 1小时 | 酸碱性评价 |
| **溶解氧(DO)** | mg/L | >5.0 | 昼夜波动大 | 1小时 | 水体富营养化 |
| **化学需氧量(COD)** | mg/L | <20 | 相对稳定 | 4小时 | 有机污染程度 |
| **氨氮(NH₃-N)** | mg/L | <1.0 | 季节性变化 | 2小时 | 营养盐污染 |
| **总磷(TP)** | mg/L | <0.2 | 波动较大 | 4小时 | 富营养化风险 |
| **浊度** | NTU | <10 | 随降雨变化 | 1小时 | 水体透明度 |

```javascript
// 水质监测数据结构定义
const WaterQualityData = {
    // 监测站信息
    stationId: "WQ003",                    // 水质站编码
    stationName: "太湖梅梁湾水质站",        // 水质站名称
    waterBodyName: "太湖",                 // 水体名称
    monitoringDepth: 1.0,                  // 监测深度(m)
    
    // 物理参数
    physicalParameters: {
        waterTemperature: 18.5,            // 水温(°C)
        turbidity: 12.3,                   // 浊度(NTU)
        transparency: 2.1,                 // 透明度(m)
        color: 15,                         // 色度(度)
        electricalConductivity: 450        // 电导率(μS/cm)
    },
    
    // 化学参数
    chemicalParameters: {
        pH: 7.2,                           // pH值
        dissolvedOxygen: 8.5,              // 溶解氧(mg/L)  
        cod: 15.2,                         // 化学需氧量(mg/L)
        bod5: 3.8,                         // 生化需氧量(mg/L)
        ammoniaNitrogen: 0.5,              // 氨氮(mg/L)
        totalPhosphorus: 0.05,             // 总磷(mg/L)
        totalNitrogen: 1.2                 // 总氮(mg/L)
    },
    
    // 生物参数
    biologicalParameters: {
        coliformBacteria: 240,             // 大肠菌群(个/L)
        chlorophyllA: 12.5,                // 叶绿素a(μg/L)
        phytoplanktonBiomass: 1.8          // 浮游植物生物量(mg/L)
    },
    
    // 综合评价
    qualityAssessment: {
        waterQualityIndex: 85,             // 水质指数
        qualityGrade: "II",                // 水质类别
        primaryPollutant: "总氮",          // 主要污染物
        assessmentStandard: "GB3838-2002"  // 评价标准
    },
    
    timestamp: "2024-08-27T10:00:00+08:00"
};
```

### 按时间特性分类

根据数据的时效性和更新频率，水利监测数据可分为实时数据和历史数据两大类型。

#### **实时数据处理机制**

**实时监测数据**为水利管理系统提供当前时刻的运行状态信息。

- **定义**：实时数据是指以分钟级或更短时间间隔采集传输的最新监测数据
- **特点**：时效性要求严格、数据传输量大、处理计算要求高、对系统可靠性要求极高
- **优势**：支持及时决策响应、实现快速预警功能、为应急调度提供实时依据
- **适用场景**：防洪调度决策、水库实时调度、突发事件应急响应、自动化控制系统

实时数据处理系统需要具备以下核心技术能力：

```javascript
// 实时数据处理引擎
class RealTimeDataProcessor {
    constructor(config) {
        this.config = config;
        this.dataBuffer = new Map();           // 数据缓冲队列
        this.processInterval = 60000;          // 处理间隔(毫秒)
        this.maxBufferSize = 10000;            // 最大缓冲区大小
        this.alertThresholds = new Map();      // 预警阈值配置
        
        this.initializeProcessor();
    }
    
    // 初始化处理器配置
    initializeProcessor() {
        // 启动定时处理任务
        this.processingTimer = setInterval(() => {
            this.processBufferedData();
        }, this.processInterval);
        
        // 配置不同类型数据的预警阈值
        this.alertThresholds.set('water_level', {
            attention: 185.0,      // 关注水位(m)
            warning: 188.0,        // 警戒水位(m)
            danger: 190.0,         // 危险水位(m)
            emergency: 192.0       // 紧急水位(m)
        });
        
        this.alertThresholds.set('dam_displacement', {
            attention: 10.0,       // 关注位移(mm)
            warning: 20.0,         // 预警位移(mm)
            danger: 50.0          // 危险位移(mm)
        });
    }
    
    // 接收新数据
    receiveData(sensorData) {
        const { stationId, timestamp, value, dataType } = sensorData;
        
        try {
            // 数据有效性验证
            if (this.validateIncomingData(sensorData)) {
                // 数据预处理
                const processedData = this.preprocessData(sensorData);
                
                // 存入缓冲队列
                this.bufferData(processedData);
                
                // 立即进行预警检查
                this.checkAlertConditions(processedData);
                
                // 更新系统状态
                this.updateSystemStatus(stationId, 'ACTIVE');
                
            } else {
                console.warn(`数据验证失败: 站点${stationId}, 时间${timestamp}`);
                this.handleInvalidData(sensorData);
            }
        } catch (error) {
            console.error(`数据处理异常: ${error.message}`);
            this.handleProcessingError(sensorData, error);
        }
    }
    
    // 数据有效性验证
    validateIncomingData(data) {
        const { stationId, value, dataType, timestamp } = data;
        
        // 基础字段检查
        if (!stationId || !dataType || value === undefined || !timestamp) {
            return false;
        }
        
        // 数值范围检查
        if (isNaN(value) || !isFinite(value)) {
            return false;
        }
        
        // 时间戳检查 - 确保数据不过期
        const dataTime = new Date(timestamp);
        const currentTime = new Date();
        const timeDiff = currentTime - dataTime;
        
        if (timeDiff > 300000) { // 数据超过5分钟视为过期
            console.warn(`数据过期: 延迟${timeDiff/1000}秒`);
            return false;
        }
        
        // 数据类型特定验证
        return this.validateByDataType(data);
    }
    
    // 按数据类型进行专门验证
    validateByDataType(data) {
        const { dataType, value } = data;
        
        switch (dataType) {
            case 'water_level':
                return value >= -50 && value <= 500; // 合理水位范围
            case 'flow_rate':
                return value >= 0 && value <= 100000; // 流量非负且不超过最大值
            case 'water_quality_ph':
                return value >= 0 && value <= 14; // pH值范围
            case 'dam_displacement':
                return Math.abs(value) <= 1000; // 位移绝对值限制
            default:
                return true; // 未知类型暂不验证
        }
    }
    
    // 数据预处理
    preprocessData(rawData) {
        return {
            ...rawData,
            processedTime: new Date().toISOString(),
            processingId: this.generateProcessingId(),
            qualityFlag: this.assessDataQuality(rawData),
            normalized: this.normalizeDataValue(rawData)
        };
    }
    
    // 预警条件检查
    checkAlertConditions(data) {
        const { dataType, value, stationId } = data;
        const thresholds = this.alertThresholds.get(dataType);
        
        if (!thresholds) return;
        
        let alertLevel = 'NORMAL';
        let thresholdValue = null;
        
        // 确定预警等级
        if (value >= thresholds.emergency) {
            alertLevel = 'EMERGENCY';
            thresholdValue = thresholds.emergency;
        } else if (value >= thresholds.danger) {
            alertLevel = 'DANGER';
            thresholdValue = thresholds.danger;
        } else if (value >= thresholds.warning) {
            alertLevel = 'WARNING';
            thresholdValue = thresholds.warning;
        } else if (value >= thresholds.attention) {
            alertLevel = 'ATTENTION';
            thresholdValue = thresholds.attention;
        }
        
        // 触发相应级别的预警
        if (alertLevel !== 'NORMAL') {
            this.triggerAlert({
                stationId,
                dataType,
                value,
                alertLevel,
                threshold: thresholdValue,
                timestamp: data.timestamp,
                severity: this.calculateSeverity(alertLevel, value, thresholdValue)
            });
        }
    }
    
    // 触发预警
    triggerAlert(alertInfo) {
        console.log(`🚨 预警触发: ${JSON.stringify(alertInfo)}`);
        
        // 发送预警通知
        this.sendAlertNotification(alertInfo);
        
        // 记录预警日志
        this.logAlert(alertInfo);
        
        // 更新预警状态
        this.updateAlertStatus(alertInfo);
    }
    
    // 计算预警严重程度
    calculateSeverity(alertLevel, currentValue, thresholdValue) {
        const exceedanceRatio = (currentValue - thresholdValue) / thresholdValue;
        
        return {
            level: alertLevel,
            exceedanceRatio: exceedanceRatio,
            riskScore: Math.min(exceedanceRatio * 100, 100) // 0-100分
        };
    }
}
```

#### **历史数据分析处理**

**历史监测数据**为趋势分析、统计建模和规律发现提供数据基础。

- **定义**：历史数据是指长期积累存储的监测记录数据，通常跨越数月、数年甚至数十年
- **特点**：数据总量庞大、质量参差不齐、时间跨度长、包含丰富的规律信息和异常事件
- **优势**：支持长期趋势分析、规律模式发现、统计建模分析、为预测预报提供训练数据
- **适用场景**：年度水情分析、多年调节计算、水文统计分析、洪水频率计算、工程安全评估

历史数据的有效管理和深度分析需要专门的数据仓库技术：

```javascript
// 历史数据分析处理系统
class HistoricalDataAnalyzer {
    constructor(databaseConnection, cacheManager) {
        this.database = databaseConnection;
        this.cache = cacheManager;
        this.analysisResults = new Map();
        this.statisticalModels = new Map();
        
        this.initializeAnalysisModels();
    }
    
    // 初始化分析模型
    initializeAnalysisModels() {
        this.statisticalModels.set('trend_analysis', new TrendAnalysisModel());
        this.statisticalModels.set('seasonal_decomposition', new SeasonalDecompositionModel());
        this.statisticalModels.set('frequency_analysis', new FrequencyAnalysisModel());
        this.statisticalModels.set('correlation_analysis', new CorrelationAnalysisModel());
    }
    
    // 综合趋势分析
    async analyzeTrend(stationId, parameter, timeRange, options = {}) {
        const cacheKey = `trend_${stationId}_${parameter}_${timeRange.start}_${timeRange.end}`;
        
        // 检查分析结果缓存
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }
        
        try {
            // 查询历史数据
            const historicalData = await this.queryHistoricalData({
                stationId,
                parameter,
                startTime: timeRange.start,
                endTime: timeRange.end,
                orderBy: 'timestamp ASC'
            });
            
            if (historicalData.length < 30) {
                throw new Error('历史数据量不足，无法进行趋势分析');
            }
            
            // 数据预处理
            const cleanedData = this.cleanHistoricalData(historicalData);
            
            // 执行趋势分析
            const trendAnalysis = await this.performTrendAnalysis(cleanedData, options);
            
            // 缓存分析结果
            this.cache.set(cacheKey, trendAnalysis, { ttl: 3600 }); // 缓存1小时
            
            return trendAnalysis;
            
        } catch (error) {
            console.error(`趋势分析失败: ${error.message}`);
            throw error;
        }
    }
    
    // 执行趋势分析计算
    async performTrendAnalysis(data, options) {
        const analysisResult = {
            basicStatistics: this.calculateBasicStatistics(data),
            trendIndicators: this.calculateTrendIndicators(data),
            seasonalPattern: this.identifySeasonalPattern(data),
            anomalyDetection: this.detectHistoricalAnomalies(data),
            forecastingModel: null,
            recommendations: []
        };
        
        // 计算基础统计指标
        analysisResult.basicStatistics = {
            dataPoints: data.length,
            timeSpan: this.calculateTimeSpan(data),
            average: this.calculateMean(data),
            median: this.calculateMedian(data),
            standardDeviation: this.calculateStdDev(data),
            minimum: { value: Math.min(...data.map(d => d.value)), ...this.findExtremePoint(data, 'min') },
            maximum: { value: Math.max(...data.map(d => d.value)), ...this.findExtremePoint(data, 'max') },
            variance: this.calculateVariance(data),
            skewness: this.calculateSkewness(data),
            kurtosis: this.calculateKurtosis(data)
        };
        
        // 趋势指标计算
        analysisResult.trendIndicators = {
            overallTrend: this.calculateOverallTrend(data),
            trendSlope: this.calculateTrendSlope(data),
            changeRate: this.calculateChangeRate(data),
            trendSignificance: this.testTrendSignificance(data),
            inflectionPoints: this.identifyInflectionPoints(data),
            volatilityLevel: this.assessVolatility(data)
        };
        
        // 生成分析建议
        analysisResult.recommendations = this.generateAnalysisRecommendations(analysisResult);
        
        return analysisResult;
    }
    
    // 计算整体趋势方向
    calculateOverallTrend(data) {
        if (data.length < 2) return 'INSUFFICIENT_DATA';
        
        // 分段计算趋势
        const segments = Math.floor(data.length / 4);
        const firstSegment = data.slice(0, segments);
        const lastSegment = data.slice(-segments);
        
        const firstAvg = this.calculateMean(firstSegment);
        const lastAvg = this.calculateMean(lastSegment);
        
        const changeRate = (lastAvg - firstAvg) / Math.abs(firstAvg);
        const absoluteChange = Math.abs(changeRate);
        
        if (absoluteChange < 0.05) {
            return 'STABLE';           // 变化小于5%
        } else if (changeRate > 0.05) {
            return 'RISING';           // 上升趋势
        } else if (changeRate < -0.05) {
            return 'DECLINING';        // 下降趋势
        } else {
            return 'FLUCTUATING';      // 波动变化
        }
    }
    
    // 异常值检测
    detectHistoricalAnomalies(data) {
        const anomalies = [];
        const values = data.map(d => d.value);
        
        // 使用3σ原则检测异常值
        const mean = this.calculateMean(data);
        const stdDev = this.calculateStdDev(data);
        const threshold = 3 * stdDev;
        
        data.forEach((point, index) => {
            const deviation = Math.abs(point.value - mean);
            if (deviation > threshold) {
                anomalies.push({
                    index: index,
                    timestamp: point.timestamp,
                    value: point.value,
                    deviation: deviation,
                    zScore: deviation / stdDev,
                    severity: deviation > 4 * stdDev ? 'EXTREME' : 'HIGH',
                    type: point.value > mean ? 'UPPER_OUTLIER' : 'LOWER_OUTLIER'
                });
            }
        });
        
        // 使用滑动窗口检测局部异常
        const windowSize = Math.min(30, Math.floor(data.length / 10));
        const localAnomalies = this.detectLocalAnomalies(data, windowSize);
        
        return {
            globalAnomalies: anomalies,
            localAnomalies: localAnomalies,
            totalAnomalies: anomalies.length + localAnomalies.length,
            anomalyRate: (anomalies.length + localAnomalies.length) / data.length
        };
    }
    
    // 生成分析建议
    generateAnalysisRecommendations(analysisResult) {
        const recommendations = [];
        const { basicStatistics, trendIndicators, anomalyDetection } = analysisResult;
        
        // 基于趋势的建议
        switch (trendIndicators.overallTrend) {
            case 'RISING':
                recommendations.push('监测数据呈上升趋势，建议加强监控并分析成因');
                break;
            case 'DECLINING':
                recommendations.push('监测数据呈下降趋势，建议评估是否影响正常运行');
                break;
            case 'FLUCTUATING':
                recommendations.push('数据波动较大，建议检查设备状态和环境因素');
                break;
        }
        
        // 基于异常情况的建议
        if (anomalyDetection.anomalyRate > 0.05) {
            recommendations.push('异常数据比例较高，建议审查数据质量和设备运行状态');
        }
        
        // 基于数据质量的建议
        if (basicStatistics.dataPoints < 1000) {
            recommendations.push('历史数据量相对较少，建议继续积累数据以提高分析精度');
        }
        
        return recommendations;
    }
}
```

## 7.1.2 数据质量检验与异常值处理

### 数据质量控制体系

**数据质量控制**是确保监测数据准确可靠的关键技术环节，直接影响后续分析和决策的科学性。

数据质量问题在水利监测系统中表现多样，主要包括以下几个方面：

| 质量问题类型 | 具体表现形式 | 对系统影响程度 | 主要处理策略 | 技术实现方法 |
|-------------|-------------|--------------|------------|-------------|
| **完整性问题** | 数据缺失、记录中断、字段不全 | 高 | 插值补全、缺失标记 | 时间序列插值、邻近站点推算 |
| **准确性问题** | 数值明显错误、设备误差、传输错误 | 极高 | 交叉验证、误差纠正 | 多站点比对、物理规律校验 |
| **一致性问题** | 数据格式不统一、量纲混乱、编码差异 | 中高 | 格式标准化、单位转换 | 数据映射转换、标准化接口 |
| **时效性问题** | 数据延迟传输、时钟同步误差 | 高 | 时间校准、延迟处理 | NTP时间同步、延迟补偿算法 |
| **逻辑性问题** | 数据间逻辑关系错误、物理约束违反 | 中 | 逻辑校验、关系修正 | 业务规则引擎、约束条件检查 |

```javascript
// 综合数据质量控制系统
class ComprehensiveDataQualityController {
    constructor(config) {
        this.config = config;
        this.qualityRules = new Map();         // 质量规则库
        this.qualityMetrics = {                // 质量评估指标
            completeness: 0,       // 完整性得分
            accuracy: 0,           // 准确性得分
            consistency: 0,        // 一致性得分
            timeliness: 0,         // 时效性得分
            validity: 0            // 有效性得分
        };
        this.qualityHistory = [];              // 质量评估历史
        
        this.initializeQualityRules();
    }
    
    // 初始化质量控制规则
    initializeQualityRules() {
        // 水位数据质量规则
        this.qualityRules.set('water_level', {
            range: { 
                min: 0,                    // 最小合理值(m)
                max: 300,                  // 最大合理值(m)
                typical: { min: 50, max: 200 }  // 典型值范围
            },
            precision: 0.01,               // 精度要求(m)
            continuity: { 
                maxJump: 5,                // 最大跳跃值(m)
                maxRate: 2                 // 最大变化率(m/h)
            },
            frequency: { 
                expected: 3600,            // 期望频率(秒)
                tolerance: 300             // 允许偏差(秒)
            },
            crossValidation: {
                relatedStations: [],       // 相关站点
                correlationThreshold: 0.7  // 相关性阈值
            }
        });
        
        // 流量数据质量规则
        this.qualityRules.set('flow', {
            range: { min: 0, max: 50000, typical: { min: 10, max: 10000 }},
            precision: 0.1,
            continuity: { maxJump: 1000, maxRate: 500 },
            frequency: { expected: 3600, tolerance: 300 },
            physicalConstraints: {
                waterLevelCorrelation: true,  // 必须与水位相关
                minimumCorrelation: 0.8
            }
        });
        
        // 水质数据质量规则  
        this.qualityRules.set('water_quality', {
            parameters: {
                pH: { min: 0, max: 14, precision: 0.1, typical: { min: 6, max: 9 }},
                DO: { min: 0, max: 20, precision: 0.1, typical: { min: 3, max: 15 }},
                COD: { min: 0, max: 100, precision: 0.1, typical: { min: 2, max: 40 }}
            },
            interParameterRules: [
                { if: 'DO < 2', then: 'COD should be high' },
                { if: 'pH < 6 OR pH > 9', then: 'flag as abnormal' }
            ]
        });
    }
    
    // 执行全面质量检查
    performComprehensiveQualityCheck(dataset) {
        const qualityReport = {
            overall: 'UNKNOWN',
            timestamp: new Date().toISOString(),
            datasetInfo: {
                totalRecords: dataset.length,
                timeSpan: this.calculateTimeSpan(dataset),
                dataTypes: this.identifyDataTypes(dataset)
            },
            qualityMetrics: {},
            detailedIssues: [],
            recommendations: [],
            actionItems: []
        };
        
        try {
            // 1. 完整性检查
            const completenessResult = this.checkCompleteness(dataset);
            qualityReport.qualityMetrics.completeness = completenessResult;
            
            // 2. 准确性检查
            const accuracyResult = this.checkAccuracy(dataset);
            qualityReport.qualityMetrics.accuracy = accuracyResult;
            
            // 3. 一致性检查
            const consistencyResult = this.checkConsistency(dataset);
            qualityReport.qualityMetrics.consistency = consistencyResult;
            
            // 4. 时效性检查
            const timelinessResult = this.checkTimeliness(dataset);
            qualityReport.qualityMetrics.timeliness = timelinessResult;
            
            // 5. 逻辑有效性检查
            const validityResult = this.checkLogicalValidity(dataset);
            qualityReport.qualityMetrics.validity = validityResult;
            
            // 计算综合质量评分
            const overallScore = this.calculateOverallQualityScore(qualityReport.qualityMetrics);
            qualityReport.overall = this.getQualityGrade(overallScore);
            
            // 生成改进建议
            qualityReport.recommendations = this.generateImprovementRecommendations(qualityReport);
            
            return qualityReport;
            
        } catch (error) {
            console.error(`质量检查执行失败: ${error.message}`);
            qualityReport.overall = 'ERROR';
            qualityReport.error = error.message;
            return qualityReport;
        }
    }
    
    // 完整性检查实现
    checkCompleteness(dataset) {
        const requiredFields = ['stationId', 'timestamp', 'value', 'dataType'];
        let completeRecords = 0;
        const missingFieldStats = {};
        const temporalGaps = [];
        
        // 检查必需字段完整性
        dataset.forEach((record, index) => {
            const missingFields = requiredFields.filter(field => 
                record[field] === undefined || record[field] === null || record[field] === ''
            );
            
            if (missingFields.length === 0) {
                completeRecords++;
            } else {
                // 统计缺失字段
                missingFields.forEach(field => {
                    missingFieldStats[field] = (missingFieldStats[field] || 0) + 1;
                });
            }
        });
        
        // 检查时间序列完整性
        const sortedData = dataset.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        for (let i = 1; i < sortedData.length; i++) {
            const prevTime = new Date(sortedData[i-1].timestamp);
            const currentTime = new Date(sortedData[i].timestamp);
            const expectedInterval = this.getExpectedInterval(sortedData[i].dataType);
            const actualInterval = currentTime - prevTime;
            
            if (actualInterval > expectedInterval * 2) { // 超过期望间隔2倍
                temporalGaps.push({
                    startTime: prevTime,
                    endTime: currentTime,
                    gapDuration: actualInterval,
                    expectedInterval: expectedInterval
                });
            }
        }
        
        const completenessRate = completeRecords / dataset.length;
        
        return {
            score: completenessRate * 100,
            completeRecords: completeRecords,
            incompleteRecords: dataset.length - completeRecords,
            missingFieldStats: missingFieldStats,
            temporalGaps: temporalGaps,
            assessment: this.getCompletenessGrade(completenessRate)
        };
    }
    
    // 准确性检查实现
    checkAccuracy(dataset) {
        let accurateRecords = 0;
        const accuracyIssues = [];
        
        dataset.forEach((record, index) => {
            const dataType = record.dataType;
            const rules = this.qualityRules.get(dataType);
            
            if (rules) {
                const validationResult = this.validateDataAccuracy(record, rules);
                if (validationResult.isValid) {
                    accurateRecords++;
                } else {
                    accuracyIssues.push({
                        recordIndex: index,
                        stationId: record.stationId,
                        timestamp: record.timestamp,
                        value: record.value,
                        issues: validationResult.issues,
                        severity: validationResult.severity
                    });
                }
            }
        });
        
        const accuracyRate = dataset.length > 0 ? accurateRecords / dataset.length : 0;
        
        return {
            score: accuracyRate * 100,
            accurateRecords: accurateRecords,
            inaccurateRecords: dataset.length - accurateRecords,
            issues: accuracyIssues,
            assessment: this.getAccuracyGrade(accuracyRate)
        };
    }
    
    // 数据准确性详细验证
    validateDataAccuracy(record, rules) {
        const issues = [];
        let severity = 'LOW';
        
        const { value, dataType, timestamp } = record;
        
        // 数值范围检查
        if (rules.range) {
            if (value < rules.range.min || value > rules.range.max) {
                issues.push(`数值${value}超出合理范围[${rules.range.min}, ${rules.range.max}]`);
                severity = 'HIGH';
            } else if (rules.range.typical && 
                      (value < rules.range.typical.min || value > rules.range.typical.max)) {
                issues.push(`数值${value}超出典型范围，可能存在异常`);
                severity = Math.max(severity, 'MEDIUM');
            }
        }
        
        // 精度检查
        if (rules.precision) {
            const decimalPlaces = this.getDecimalPlaces(value);
            const expectedDecimals = this.getDecimalPlaces(rules.precision);
            if (decimalPlaces > expectedDecimals + 1) { // 允许一位精度误差
                issues.push(`数值精度${decimalPlaces}位超出要求${expectedDecimals}位`);
                severity = Math.max(severity, 'MEDIUM');
            }
        }
        
        // 物理约束检查
        if (rules.physicalConstraints) {
            const constraintViolations = this.checkPhysicalConstraints(record, rules.physicalConstraints);
            if (constraintViolations.length > 0) {
                issues.push(...constraintViolations);
                severity = 'HIGH';
            }
        }
        
        return {
            isValid: issues.length === 0,
            issues: issues,
            severity: severity
        };
    }
    
    // 获取小数位数
    getDecimalPlaces(value) {
        const str = value.toString();
        if (str.indexOf('.') !== -1) {
            return str.split('.')[1].length;
        }
        return 0;
    }
}
```

### 异常值检测与处理

**异常值检测技术**是保证数据质量的重要手段，需要结合统计学方法和领域知识进行综合判断。

异常值在水利监测数据中的产生原因复杂多样：

- **设备硬件故障**：传感器损坏、校准偏移、电路异常、供电不稳
- **环境干扰因素**：极端天气事件、人为活动干扰、动物影响、电磁干扰
- **数据传输问题**：通信线路故障、协议解析错误、数据包丢失、网络延迟
- **人为操作失误**：设备误操作、参数设置错误、维护不当、校准失误

```javascript
// 智能异常检测系统
class IntelligentAnomalyDetector {
    constructor() {
        this.detectionMethods = {
            'statistical': this.statisticalDetection.bind(this),
            'machine_learning': this.machineLearningDetection.bind(this),
            'domain_knowledge': this.domainKnowledgeDetection.bind(this),
            'ensemble': this.ensembleDetection.bind(this)
        };
        
        this.anomalyHistory = new Map();
        this.detectionModels = new Map();
        
        this.initializeDetectionModels();
    }
    
    // 初始化检测模型
    initializeDetectionModels() {
        // 统计检测模型参数
        this.detectionModels.set('z_score', {
            threshold: 3,
            windowSize: 100,
            adaptiveThreshold: true
        });
        
        this.detectionModels.set('isolation_forest', {
            contamination: 0.1,
            nEstimators: 100,
            maxSamples: 'auto'
        });
        
        // 领域知识规则
        this.detectionModels.set('domain_rules', {
            water_level: {
                maxDailyChange: 5.0,      // 日最大变化量(m)
                physicalLimits: { min: 0, max: 300 },
                seasonalPattern: true,
                correlationWithRainfall: true
            },
            flow: {
                maxDailyChange: 1000,     // 日最大变化量(m³/s)
                physicalLimits: { min: 0, max: 50000 },
                waterLevelCorrelation: 0.8
            }
        });
    }
    
    // 统计方法异常检测
    statisticalDetection(data, config = {}) {
        const {
            method = 'z_score',        // 检测方法
            threshold = 3,             // 阈值参数
            windowSize = 100,          // 滑动窗口大小
            adaptiveThreshold = true   // 自适应阈值
        } = config;
        
        const anomalies = [];
        const values = data.map(d => d.value);
        
        // Z-Score方法检测
        if (method === 'z_score' || method === 'all') {
            for (let i = windowSize; i < data.length; i++) {
                const window = values.slice(i - windowSize, i);
                const currentValue = values[i];
                
                const mean = this.calculateMean(window);
                const stdDev = this.calculateStdDev(window);
                
                if (stdDev > 0) {
                    const zScore = Math.abs(currentValue - mean) / stdDev;
                    const adaptiveThresh = adaptiveThreshold ? 
                                         this.calculateAdaptiveThreshold(window, threshold) : threshold;
                    
                    if (zScore > adaptiveThresh) {
                        anomalies.push({
                            index: i,
                            timestamp: data[i].timestamp,
                            value: currentValue,
                            method: 'z_score',
                            score: zScore,
                            threshold: adaptiveThresh,
                            severity: zScore > adaptiveThresh * 1.5 ? 'HIGH' : 'MEDIUM',
                            context: this.getAnomalyContext(data, i, windowSize)
                        });
                    }
                }
            }
        }
        
        // IQR方法检测
        if (method === 'iqr' || method === 'all') {
            for (let i = windowSize; i < data.length; i++) {
                const window = values.slice(i - windowSize, i);
                const currentValue = values[i];
                
                const sortedWindow = [...window].sort((a, b) => a - b);
                const q1 = this.calculatePercentile(sortedWindow, 25);
                const q3 = this.calculatePercentile(sortedWindow, 75);
                const iqr = q3 - q1;
                
                const lowerBound = q1 - 1.5 * iqr;
                const upperBound = q3 + 1.5 * iqr;
                
                if (currentValue < lowerBound || currentValue > upperBound) {
                    const deviation = Math.max(lowerBound - currentValue, currentValue - upperBound, 0);
                    
                    anomalies.push({
                        index: i,
                        timestamp: data[i].timestamp,
                        value: currentValue,
                        method: 'iqr',
                        score: deviation / iqr,
                        bounds: { lower: lowerBound, upper: upperBound },
                        severity: deviation > iqr * 2 ? 'HIGH' : 'MEDIUM',
                        context: this.getAnomalyContext(data, i, windowSize)
                    });
                }
            }
        }
        
        return {
            method: method,
            totalAnomalies: anomalies.length,
            anomalies: anomalies,
            anomalyRate: anomalies.length / data.length,
            summary: this.summarizeAnomalies(anomalies)
        };
    }
    
    // 领域知识异常检测
    domainKnowledgeDetection(data, dataType) {
        const rules = this.detectionModels.get('domain_rules')[dataType];
        if (!rules) return { anomalies: [], summary: 'No domain rules defined' };
        
        const anomalies = [];
        
        for (let i = 1; i < data.length; i++) {
            const currentPoint = data[i];
            const previousPoint = data[i - 1];
            
            // 物理限制检查
            if (rules.physicalLimits) {
                if (currentPoint.value < rules.physicalLimits.min || 
                    currentPoint.value > rules.physicalLimits.max) {
                    anomalies.push({
                        index: i,
                        timestamp: currentPoint.timestamp,
                        value: currentPoint.value,
                        method: 'physical_limits',
                        violation: 'PHYSICAL_CONSTRAINT',
                        severity: 'HIGH',
                        description: `数值${currentPoint.value}超出物理限制范围`
                    });
                }
            }
            
            // 变化率检查
            if (rules.maxDailyChange && previousPoint) {
                const timeDiff = (new Date(currentPoint.timestamp) - new Date(previousPoint.timestamp)) / 1000 / 3600; // 小时
                const valueChange = Math.abs(currentPoint.value - previousPoint.value);
                const changeRate = valueChange / timeDiff;
                
                if (changeRate > rules.maxDailyChange / 24) { // 转换为小时变化率
                    anomalies.push({
                        index: i,
                        timestamp: currentPoint.timestamp,
                        value: currentPoint.value,
                        method: 'change_rate',
                        violation: 'EXCESSIVE_CHANGE_RATE',
                        severity: changeRate > rules.maxDailyChange / 12 ? 'HIGH' : 'MEDIUM',
                        changeRate: changeRate,
                        maxAllowed: rules.maxDailyChange / 24,
                        description: `变化率${changeRate.toFixed(2)}超过允许范围`
                    });
                }
            }
        }
        
        return {
            method: 'domain_knowledge',
            dataType: dataType,
            totalAnomalies: anomalies.length,
            anomalies: anomalies,
            summary: this.summarizeAnomalies(anomalies)
        };
    }
    
    // 异常值处理策略实现
    handleAnomalies(data, anomalies, strategy = 'interpolation', options = {}) {
        const processedData = JSON.parse(JSON.stringify(data)); // 深拷贝
        const handlingReport = {
            strategy: strategy,
            totalAnomalies: anomalies.length,
            handledAnomalies: 0,
            failedHandling: 0,
            processingLog: []
        };
        
        // 按索引降序排列，避免处理过程中索引变化
        const sortedAnomalies = anomalies.sort((a, b) => b.index - a.index);
        
        sortedAnomalies.forEach(anomaly => {
            try {
                const handlingResult = this.applySingleAnomalyHandling(
                    processedData, anomaly, strategy, options
                );
                
                if (handlingResult.success) {
                    handlingReport.handledAnomalies++;
                    handlingReport.processingLog.push({
                        index: anomaly.index,
                        action: handlingResult.action,
                        originalValue: anomaly.value,
                        newValue: handlingResult.newValue,
                        method: handlingResult.method
                    });
                } else {
                    handlingReport.failedHandling++;
                    handlingReport.processingLog.push({
                        index: anomaly.index,
                        action: 'FAILED',
                        error: handlingResult.error
                    });
                }
            } catch (error) {
                handlingReport.failedHandling++;
                handlingReport.processingLog.push({
                    index: anomaly.index,
                    action: 'FAILED',
                    error: error.message
                });
            }
        });
        
        return {
            processedData: processedData,
            handlingReport: handlingReport
        };
    }
    
    // 单个异常值处理实现
    applySingleAnomalyHandling(data, anomaly, strategy, options) {
        const index = anomaly.index;
        
        switch (strategy) {
            case 'interpolation':
                return this.interpolationHandling(data, index, options);
                
            case 'replacement':
                return this.replacementHandling(data, index, anomaly, options);
                
            case 'removal':
                return this.removalHandling(data, index, options);
                
            case 'flagging':
                return this.flaggingHandling(data, index, anomaly, options);
                
            case 'model_based':
                return this.modelBasedHandling(data, index, options);
                
            default:
                throw new Error(`不支持的处理策略: ${strategy}`);
        }
    }
    
    // 插值处理方法
    interpolationHandling(data, targetIndex, options = {}) {
        const { method = 'linear', maxGap = 5 } = options;
        
        // 寻找前后有效数据点
        let prevValidIndex = targetIndex - 1;
        let nextValidIndex = targetIndex + 1;
        
        // 向前搜索有效点
        while (prevValidIndex >= 0 && 
               (data[prevValidIndex].quality === 'ANOMALY' || 
                data[prevValidIndex].value === null)) {
            prevValidIndex--;
        }
        
        // 向后搜索有效点
        while (nextValidIndex < data.length && 
               (data[nextValidIndex].quality === 'ANOMALY' || 
                data[nextValidIndex].value === null)) {
            nextValidIndex++;
        }
        
        // 检查插值可行性
        if (prevValidIndex < 0 || nextValidIndex >= data.length) {
            return {
                success: false,
                error: '无法找到足够的有效数据点进行插值'
            };
        }
        
        const gap = nextValidIndex - prevValidIndex - 1;
        if (gap > maxGap) {
            return {
                success: false,
                error: `数据间隔${gap}超过最大插值间隔${maxGap}`
            };
        }
        
        // 执行插值计算
        let interpolatedValue;
        
        if (method === 'linear') {
            // 线性插值
            const prevPoint = data[prevValidIndex];
            const nextPoint = data[nextValidIndex];
            const prevTime = new Date(prevPoint.timestamp).getTime();
            const nextTime = new Date(nextPoint.timestamp).getTime();
            const targetTime = new Date(data[targetIndex].timestamp).getTime();
            
            const timeWeight = (targetTime - prevTime) / (nextTime - prevTime);
            interpolatedValue = prevPoint.value + (nextPoint.value - prevPoint.value) * timeWeight;
            
        } else if (method === 'spline') {
            // 三次样条插值（简化实现）
            const points = [
                data[Math.max(0, prevValidIndex - 1)],
                data[prevValidIndex],
                data[nextValidIndex],
                data[Math.min(data.length - 1, nextValidIndex + 1)]
            ].filter(p => p && p.value !== null);
            
            interpolatedValue = this.splineInterpolation(points, data[targetIndex].timestamp);
        }
        
        // 更新数据点
        data[targetIndex].value = Math.round(interpolatedValue * 1000) / 1000; // 保留3位小数
        data[targetIndex].quality = 'INTERPOLATED';
        data[targetIndex].processingInfo = {
            originalValue: data[targetIndex].value,
            method: 'interpolation',
            interpolationMethod: method,
            processedAt: new Date().toISOString()
        };
        
        return {
            success: true,
            action: 'INTERPOLATED',
            method: method,
            newValue: data[targetIndex].value
        };
    }
    
    // 获取异常值上下文信息
    getAnomalyContext(data, index, windowSize = 10) {
        const contextStart = Math.max(0, index - windowSize);
        const contextEnd = Math.min(data.length, index + windowSize + 1);
        const contextData = data.slice(contextStart, contextEnd);
        
        return {
            windowSize: contextData.length,
            beforeAnomaly: contextData.slice(0, index - contextStart),
            afterAnomaly: contextData.slice(index - contextStart + 1),
            neighboringValues: {
                before: contextData[index - contextStart - 1]?.value,
                after: contextData[index - contextStart + 1]?.value
            },
            localStatistics: {
                mean: this.calculateMean(contextData.map(d => d.value)),
                stdDev: this.calculateStdDev(contextData.map(d => d.value)),
                median: this.calculateMedian(contextData.map(d => d.value))
            }
        };
    }
}
```

## 7.1.3 多源异构数据标准化与融合

### 数据标准化处理框架

**多源异构数据的标准化处理**是实现不同数据源有效融合的前提条件。

水利监测系统中的数据来源广泛多样：
- **自动监测站**：数据格式相对标准、采集频率固定、质量相对较高
- **人工观测记录**：格式多样化、精度差异大、时间不规律、需要人工转换
- **第三方系统接口**：协议标准不同、数据结构各异、需要适配转换
- **历史档案数据**：格式老旧、需要数字化处理、质量参差不齐

```javascript
// 多源数据标准化处理引擎
class MultiSourceDataStandardizer {
    constructor() {
        // 标准数据模式定义
        this.standardSchema = {
            // 基础字段
            stationId: { 
                type: 'string', 
                required: true, 
                format: /^[A-Z]{2}\d{4}$/,
                description: '站点编码，格式为两位字母+四位数字'
            },
            timestamp: { 
                type: 'datetime', 
                required: true, 
                format: 'ISO8601',
                description: '观测时间，ISO8601格式'
            },
            value: { 
                type: 'number', 
                required: true, 
                precision: 3,
                description: '观测数值，保留3位小数'
            },
            unit: { 
                type: 'string', 
                required: true, 
                enum: ['m', 'm³/s', 'mg/L', 'NTU', 'mm', '°C', '%', 'kPa'],
                description: '数值单位'
            },
            dataType: {
                type: 'string',
                required: true,
                enum: ['water_level', 'flow', 'rainfall', 'water_quality', 'dam_safety'],
                description: '数据类型'
            },
            quality: { 
                type: 'string', 
                required: true, 
                enum: ['EXCELLENT', 'GOOD', 'FAIR', 'POOR', 'BAD'],
                description: '数据质量等级'
            },
            dataSource: { 
                type: 'string', 
                required: true,
                description: '数据来源标识'
            }
        };
        
        // 单位转换规则
        this.unitConversions = new Map();
        this.initializeUnitConversions();
        
        // 数据源配置
        this.sourceConfigs = new Map();
        this.fieldMappingRules = new Map();
        
        this.initializeSourceConfigurations();
    }
    
    // 初始化单位转换规则
    initializeUnitConversions() {
        // 长度单位转换矩阵
        this.unitConversions.set('length', {
            'mm': { 'm': 0.001, 'cm': 0.1, 'mm': 1, 'km': 0.000001 },
            'cm': { 'm': 0.01, 'cm': 1, 'mm': 10, 'km': 0.00001 },
            'm': { 'm': 1, 'cm': 100, 'mm': 1000, 'km': 0.001 },
            'km': { 'm': 1000, 'cm': 100000, 'mm': 1000000, 'km': 1 }
        });
        
        // 流量单位转换矩阵
        this.unitConversions.set('flow', {
            'm³/s': { 'm³/s': 1, 'L/s': 1000, 'm³/h': 3600, 'L/min': 60000 },
            'L/s': { 'm³/s': 0.001, 'L/s': 1, 'm³/h': 3.6, 'L/min': 60 },
            'm³/h': { 'm³/s': 0.000278, 'L/s': 0.278, 'm³/h': 1, 'L/min': 16.667 },
            'L/min': { 'm³/s': 0.0000167, 'L/s': 0.0167, 'm³/h': 0.06, 'L/min': 1 }
        });
        
        // 温度单位转换
        this.unitConversions.set('temperature', {
            '°C': { '°C': (v) => v, '°F': (v) => v * 9/5 + 32, 'K': (v) => v + 273.15 },
            '°F': { '°C': (v) => (v - 32) * 5/9, '°F': (v) => v, 'K': (v) => (v - 32) * 5/9 + 273.15 },
            'K': { '°C': (v) => v - 273.15, '°F': (v) => (v - 273.15) * 9/5 + 32, 'K': (v) => v }
        });
    }
    
    // 初始化数据源配置
    initializeSourceConfigurations() {
        // 自动监测站配置
        this.sourceConfigs.set('auto_station', {
            sourceType: 'AUTOMATIC',
            dataFormat: 'JSON',
            timeFormat: 'ISO8601',
            qualityReliable: true,
            defaultQuality: 'GOOD',
            fieldMapping: {
                'station_code': 'stationId',
                'observe_time': 'timestamp',
                'measure_value': 'value',
                'value_unit': 'unit',
                'measure_type': 'dataType'
            }
        });
        
        // 人工观测配置
        this.sourceConfigs.set('manual_observation', {
            sourceType: 'MANUAL',
            dataFormat: 'CSV',
            timeFormat: 'YYYY-MM-DD HH:mm:ss',
            qualityReliable: false,
            defaultQuality: 'FAIR',
            fieldMapping: {
                '站点编码': 'stationId',
                '观测时间': 'timestamp',
                '观测值': 'value',
                '单位': 'unit',
                '要素类型': 'dataType'
            }
        });
        
        // 第三方系统配置
        this.sourceConfigs.set('third_party_system', {
            sourceType: 'EXTERNAL_API',
            dataFormat: 'XML',
            timeFormat: 'UNIX_TIMESTAMP',
            qualityReliable: false,
            defaultQuality: 'UNKNOWN',
            fieldMapping: {
                'SiteID': 'stationId',
                'DateTime': 'timestamp',
                'Value': 'value',
                'Unit': 'unit',
                'Parameter': 'dataType'
            }
        });
    }
    
    // 标准化单个数据记录
    standardizeRecord(rawRecord, sourceConfigId) {
        const sourceConfig = this.sourceConfigs.get(sourceConfigId);
        if (!sourceConfig) {
            throw new Error(`未找到数据源配置: ${sourceConfigId}`);
        }
        
        const standardizedRecord = {};
        
        try {
            // 1. 字段映射转换
            Object.entries(sourceConfig.fieldMapping).forEach(([sourceField, standardField]) => {
                if (rawRecord[sourceField] !== undefined) {
                    standardizedRecord[standardField] = rawRecord[sourceField];
                }
            });
            
            // 2. 数据类型转换和验证
            standardizedRecord.stationId = this.standardizeStationId(
                standardizedRecord.stationId, sourceConfig.stationIdFormat
            );
            
            standardizedRecord.timestamp = this.standardizeTimestamp(
                standardizedRecord.timestamp, sourceConfig.timeFormat
            );
            
            standardizedRecord.value = this.standardizeValue(
                standardizedRecord.value, sourceConfig.valueFormat
            );
            
            // 3. 单位标准化
            if (sourceConfig.unitMapping && standardizedRecord.unit) {
                const mappedUnit = sourceConfig.unitMapping[standardizedRecord.unit];
                if (mappedUnit) {
                    // 执行单位转换
                    const conversionResult = this.convertUnit(
                        standardizedRecord.value,
                        standardizedRecord.unit,
                        mappedUnit.targetUnit,
                        mappedUnit.parameterType
                    );
                    
                    standardizedRecord.value = conversionResult.value;
                    standardizedRecord.unit = conversionResult.unit;
                }
            }
            
            // 4. 质量等级处理
            standardizedRecord.quality = this.mapQualityLevel(
                rawRecord.quality || rawRecord.status,
                sourceConfig.qualityMapping,
                sourceConfig.defaultQuality
            );
            
            // 5. 添加元数据
            standardizedRecord.dataSource = sourceConfigId;
            standardizedRecord.standardizedAt = new Date().toISOString();
            standardizedRecord.originalData = rawRecord; // 保留原始数据引用
            
            // 6. 最终验证
            const validationResult = this.validateStandardizedRecord(standardizedRecord);
            if (!validationResult.isValid) {
                throw new Error(`标准化后验证失败: ${validationResult.errors.join(', ')}`);
            }
            
            return {
                success: true,
                data: standardizedRecord,
                warnings: validationResult.warnings || []
            };
            
        } catch (error) {
            return {
                success: false,
                error: error.message,
                originalData: rawRecord,
                partialData: standardizedRecord
            };
        }
    }
    
    // 站点编码标准化
    standardizeStationId(sourceId, format) {
        if (!sourceId) {
            throw new Error('站点编码不能为空');
        }
        
        const sourceIdStr = sourceId.toString().trim();
        
        switch (format) {
            case 'numeric_only':
                // 纯数字格式转换 (如: 12345 -> WL0001)
                const numId = parseInt(sourceIdStr);
                if (isNaN(numId)) {
                    throw new Error(`无效的数字格式站点编码: ${sourceIdStr}`);
                }
                return `WL${numId.toString().padStart(4, '0')}`;
                
            case 'legacy_format':
                // 旧格式转换 (如: Station_001, STA001 -> WL0001)  
                const match = sourceIdStr.match(/(\d+)$/);
                if (!match) {
                    throw new Error(`无法从旧格式中提取站点编号: ${sourceIdStr}`);
                }
                const extractedId = parseInt(match[1]);
                return `WL${extractedId.toString().padStart(4, '0')}`;
                
            case 'prefixed_format':
                // 带前缀格式 (如: WL001 -> WL0001, FL123 -> FL0123)
                const prefixMatch = sourceIdStr.match(/^([A-Z]{2})(\d+)$/);
                if (!prefixMatch) {
                    throw new Error(`无效的前缀格式: ${sourceIdStr}`);
                }
                const prefix = prefixMatch[1];
                const number = parseInt(prefixMatch[2]);
                return `${prefix}${number.toString().padStart(4, '0')}`;
                
            case 'standard':
                // 已是标准格式，验证即可
                if (!/^[A-Z]{2}\d{4}$/.test(sourceIdStr)) {
                    throw new Error(`标准格式验证失败: ${sourceIdStr}`);
                }
                return sourceIdStr;
                
            default:
                // 尝试自动识别格式
                return this.autoDetectAndConvertStationId(sourceIdStr);
        }
    }
    
    // 时间戳标准化
    standardizeTimestamp(sourceTime, format) {
        if (!sourceTime) {
            throw new Error('时间戳不能为空');
        }
        
        let parsedTime;
        
        switch (format) {
            case 'unix_timestamp_seconds':
                const unixSeconds = parseInt(sourceTime);
                if (isNaN(unixSeconds)) {
                    throw new Error(`无效的Unix时间戳(秒): ${sourceTime}`);
                }
                parsedTime = new Date(unixSeconds * 1000);
                break;
                
            case 'unix_timestamp_milliseconds':
                const unixMillis = parseInt(sourceTime);
                if (isNaN(unixMillis)) {
                    throw new Error(`无效的Unix时间戳(毫秒): ${sourceTime}`);
                }
                parsedTime = new Date(unixMillis);
                break;
                
            case 'iso8601':
                parsedTime = new Date(sourceTime);
                break;
                
            case 'custom_format':
                // 自定义格式解析 (如: 2024-08-27 10:30:00)
                const timePattern = /^(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})$/;
                const timeMatch = sourceTime.match(timePattern);
                if (!timeMatch) {
                    throw new Error(`无法解析自定义时间格式: ${sourceTime}`);
                }
                
                const [, year, month, day, hour, minute, second] = timeMatch;
                parsedTime = new Date(
                    parseInt(year), 
                    parseInt(month) - 1, 
                    parseInt(day),
                    parseInt(hour), 
                    parseInt(minute), 
                    parseInt(second)
                );
                break;
                
            case 'excel_serial_date':
                // Excel日期序列号转换
                const excelSerial = parseFloat(sourceTime);
                if (isNaN(excelSerial)) {
                    throw new Error(`无效的Excel日期序列号: ${sourceTime}`);
                }
                // Excel日期基准是1900年1月1日，但Excel错误地认为1900年是闰年
                const excelEpoch = new Date(1899, 11, 30); // 1899年12月30日
                parsedTime = new Date(excelEpoch.getTime() + excelSerial * 24 * 60 * 60 * 1000);
                break;
                
            default:
                // 尝试自动解析
                parsedTime = new Date(sourceTime);
        }
        
        // 验证解析结果
        if (isNaN(parsedTime.getTime())) {
            throw new Error(`时间戳解析失败: ${sourceTime}`);
        }
        
        // 合理性检查
        const now = new Date();
        const minDate = new Date(1900, 0, 1); // 最早1900年
        const maxDate = new Date(now.getTime() + 365 * 24 * 60 * 60 * 1000); // 最晚当前时间+1年
        
        if (parsedTime < minDate || parsedTime > maxDate) {
            console.warn(`时间戳可能不合理: ${parsedTime.toISOString()}`);
        }
        
        return parsedTime.toISOString();
    }
    
    // 数值标准化
    standardizeValue(sourceValue, format) {
        if (sourceValue === null || sourceValue === undefined) {
            throw new Error('数值不能为空');
        }
        
        let numericValue;
        
        // 处理不同类型的输入
        if (typeof sourceValue === 'string') {
            // 去除可能的空格和特殊字符
            const cleanValue = sourceValue.trim().replace(/,/g, ''); // 移除千位分隔符
            numericValue = parseFloat(cleanValue);
        } else if (typeof sourceValue === 'number') {
            numericValue = sourceValue;
        } else {
            throw new Error(`不支持的数值类型: ${typeof sourceValue}`);
        }
        
        if (isNaN(numericValue) || !isFinite(numericValue)) {
            throw new Error(`无效的数值: ${sourceValue}`);
        }
        
        // 根据格式要求调整精度
        if (format && format.precision !== undefined) {
            numericValue = parseFloat(numericValue.toFixed(format.precision));
        } else {
            // 默认保留3位小数
            numericValue = parseFloat(numericValue.toFixed(3));
        }
        
        return numericValue;
    }
    
    // 单位转换实现
    convertUnit(value, sourceUnit, targetUnit, parameterType) {
        if (sourceUnit === targetUnit) {
            return { value: value, unit: targetUnit };
        }
        
        const conversions = this.unitConversions.get(parameterType);
        
        if (!conversions || !conversions[sourceUnit] || !conversions[sourceUnit][targetUnit]) {
            console.warn(`不支持的单位转换: ${sourceUnit} -> ${targetUnit} (${parameterType})`);
            return { value: value, unit: sourceUnit }; // 保持原单位
        }
        
        const conversionFactor = conversions[sourceUnit][targetUnit];
        let convertedValue;
        
        if (typeof conversionFactor === 'function') {
            // 函数式转换（如温度转换）
            convertedValue = conversionFactor(value);
        } else {
            // 乘法因子转换
            convertedValue = value * conversionFactor;
        }
        
        // 保持合理精度
        convertedValue = parseFloat(convertedValue.toFixed(6));
        
        return {
            value: convertedValue,
            unit: targetUnit,
            originalValue: value,
            originalUnit: sourceUnit,
            conversionFactor: conversionFactor
        };
    }
    
    // 质量等级映射
    mapQualityLevel(sourceQuality, mapping, defaultQuality = 'UNKNOWN') {
        if (!sourceQuality) return defaultQuality;
        
        const sourceQualityStr = sourceQuality.toString().toUpperCase();
        
        // 使用自定义映射
        if (mapping && mapping[sourceQualityStr]) {
            return mapping[sourceQualityStr];
        }
        
        // 使用通用映射规则
        const commonMappings = {
            '优': 'EXCELLENT',
            'EXCELLENT': 'EXCELLENT',
            'A': 'EXCELLENT',
            '1': 'EXCELLENT',
            
            '良': 'GOOD',
            'GOOD': 'GOOD',
            'B': 'GOOD',
            '2': 'GOOD',
            
            '中': 'FAIR',
            'FAIR': 'FAIR',
            'C': 'FAIR',
            '3': 'FAIR',
            
            '差': 'POOR',
            'POOR': 'POOR',
            'D': 'POOR',
            '4': 'POOR',
            
            '劣': 'BAD',
            'BAD': 'BAD',
            'E': 'BAD',
            'F': 'BAD',
            '5': 'BAD'
        };
        
        return commonMappings[sourceQualityStr] || defaultQuality;
    }
    
    // 验证标准化后的记录
    validateStandardizedRecord(record) {
        const errors = [];
        const warnings = [];
        
        // 必需字段检查
        Object.entries(this.standardSchema).forEach(([field, schema]) => {
            if (schema.required && (record[field] === undefined || record[field] === null)) {
                errors.push(`缺少必需字段: ${field}`);
                return;
            }
            
            if (record[field] !== undefined && record[field] !== null) {
                // 数据类型检查
                const actualType = typeof record[field];
                let expectedType = schema.type;
                
                if (expectedType === 'datetime') expectedType = 'string';
                
                if (expectedType === 'number' && actualType !== 'number') {
                    errors.push(`字段${field}类型错误，期望${expectedType}，实际${actualType}`);
                }
                
                // 枚举值检查
                if (schema.enum && !schema.enum.includes(record[field])) {
                    errors.push(`字段${field}值"${record[field]}"不在允许范围: ${schema.enum.join(', ')}`);
                }
                
                // 格式检查
                if (schema.format && schema.format instanceof RegExp) {
                    if (typeof record[field] === 'string' && !schema.format.test(record[field])) {
                        errors.push(`字段${field}格式不符合要求: ${schema.format}`);
                    }
                }
                
                // 精度检查
                if (schema.precision && typeof record[field] === 'number') {
                    const decimalPlaces = this.getDecimalPlaces(record[field]);
                    if (decimalPlaces > schema.precision) {
                        warnings.push(`字段${field}精度${decimalPlaces}超过建议精度${schema.precision}`);
                    }
                }
            }
        });
        
        return {
            isValid: errors.length === 0,
            errors: errors,
            warnings: warnings
        };
    }
    
    // 获取小数位数
    getDecimalPlaces(value) {
        const str = value.toString();
        if (str.indexOf('.') !== -1 && str.indexOf('e-') === -1) {
            return str.split('.')[1].length;
        }
        return 0;
    }
}
```

### 数据融合技术实现

**多源数据融合**通过整合不同来源和类型的监测数据，构建更完整、准确的信息视图。

```javascript
// 智能数据融合引擎
class IntelligentDataFusionEngine {
    constructor() {
        this.fusionStrategies = {
            'weighted_average': this.weightedAverageFusion.bind(this),
            'priority_based': this.priorityBasedFusion.bind(this),
            'consensus_voting': this.consensusVotingFusion.bind(this),
            'kalman_filter': this.kalmanFilterFusion.bind(this),
            'bayesian_fusion': this.bayesianFusion.bind(this)
        };
        
        this.fusionHistory = [];
        this.conflictResolution = new ConflictResolutionEngine();
        this.qualityAssessment = new DataQualityAssessment();
        
        this.initializeFusionModels();
    }
    
    // 初始化融合模型
    initializeFusionModels() {
        this.weightingStrategies = {
            'quality_based': {
                'EXCELLENT': 1.0,
                'GOOD': 0.8,
                'FAIR': 0.6,
                'POOR': 0.3,
                'BAD': 0.1
            },
            'reliability_based': {
                'auto_station': 0.9,
                'manual_observation': 0.7,
                'third_party_system': 0.6,
                'historical_archive': 0.5
            },
            'temporal_based': {
                maxAge: 3600000, // 1小时
                decayFactor: 0.9
            }
        };
    }
    
    // 执行多源数据融合
    async performDataFusion(dataSources, fusionConfig) {
        const fusionResult = {
            success: false,
            fusedData: [],
            conflicts: [],
            statistics: {
                totalSources: dataSources.length,
                totalRecords: 0,
                fusedRecords: 0,
                conflictCount: 0,
                qualityScore: 0
            },
            metadata: {
                fusionStrategy: fusionConfig.strategy,
                fusionTime: new Date().toISOString(),
                parameters: fusionConfig.parameters
            },
            performanceMetrics: {}
        };
        
        const startTime = performance.now();
        
        try {
            // 1. 数据预处理和验证
            const preprocessedSources = await this.preprocessDataSources(dataSources, fusionConfig);
            fusionResult.statistics.totalRecords = preprocessedSources.reduce((sum, source) => sum + source.data.length, 0);
            
            // 2. 时间对齐
            const alignedData = await this.alignDataByTime(preprocessedSources, fusionConfig.timeAlignment);
            
            // 3. 数据融合执行
            const fusionStrategy = this.fusionStrategies[fusionConfig.strategy];
            if (!fusionStrategy) {
                throw new Error(`不支持的融合策略: ${fusionConfig.strategy}`);
            }
            
            const fusionOutput = await fusionStrategy(alignedData, fusionConfig.parameters);
            fusionResult.fusedData = fusionOutput.fusedData;
            fusionResult.statistics.fusedRecords = fusionOutput.fusedData.length;
            
            // 4. 冲突检测与处理
            const conflictAnalysis = await this.detectAndResolveConflicts(alignedData, fusionResult.fusedData);
            fusionResult.conflicts = conflictAnalysis.conflicts;
            fusionResult.statistics.conflictCount = conflictAnalysis.conflicts.length;
            
            // 5. 质量评估
            const qualityAssessment = await this.assessFusionQuality(fusionResult.fusedData, dataSources);
            fusionResult.statistics.qualityScore = qualityAssessment.overallScore;
            fusionResult.qualityReport = qualityAssessment;
            
            // 6. 性能统计
            const endTime = performance.now();
            fusionResult.performanceMetrics = {
                executionTime: endTime - startTime,
                throughput: fusionResult.statistics.fusedRecords / ((endTime - startTime) / 1000),
                memoryUsage: this.estimateMemoryUsage(fusionResult.fusedData)
            };
            
            fusionResult.success = true;
            
            // 记录融合历史
            this.fusionHistory.push({
                timestamp: new Date().toISOString(),
                config: fusionConfig,
                result: {
                    recordCount: fusionResult.statistics.fusedRecords,
                    qualityScore: fusionResult.statistics.qualityScore,
                    conflictCount: fusionResult.statistics.conflictCount
                }
            });
            
            return fusionResult;
            
        } catch (error) {
            fusionResult.success = false;
            fusionResult.error = error.message;
            console.error(`数据融合失败: ${error.message}`);
            return fusionResult;
        }
    }
    
    // 加权平均融合策略
    async weightedAverageFusion(alignedData, parameters) {
        const {
            weightingStrategy = 'quality_based',
            qualityThreshold = 0.5,
            minDataSources = 2
        } = parameters;
        
        const fusedData = [];
        
        // 遍历每个时间点
        alignedData.timePoints.forEach(timePoint => {
            const fusedRecord = {
                timestamp: timePoint,
                fusedValues: {},
                sourceContributions: {},
                fusionMetadata: {
                    method: 'weighted_average',
                    weightingStrategy: weightingStrategy,
                    sourceCount: 0
                }
            };
            
            // 获取该时间点的所有数据源记录
            const recordsAtTime = alignedData.sources
                .map(source => ({
                    source: source,
                    record: source.alignedData.find(r => r.timestamp === timePoint)
                }))
                .filter(item => item.record !== undefined);
            
            if (recordsAtTime.length < minDataSources) {
                // 数据源不足，跳过该时间点
                return;
            }
            
            // 按参数类型分组处理
            const parameterGroups = this.groupRecordsByParameter(recordsAtTime);
            
            Object.entries(parameterGroups).forEach(([parameter, parameterRecords]) => {
                let weightedSum = 0;
                let totalWeight = 0;
                const contributions = [];
                
                parameterRecords.forEach(({ source, record }) => {
                    const value = record.values[parameter];
                    if (value !== undefined && value !== null) {
                        const weight = this.calculateFusionWeight(record, source, weightingStrategy);
                        
                        if (weight >= qualityThreshold) {
                            weightedSum += value * weight;
                            totalWeight += weight;
                            
                            contributions.push({
                                sourceId: source.sourceId,
                                value: value,
                                weight: weight,
                                quality: record.quality,
                                confidence: record.confidence || 0.8
                            });
                        }
                    }
                });
                
                if (totalWeight > 0) {
                    fusedRecord.fusedValues[parameter] = weightedSum / totalWeight;
                    fusedRecord.sourceContributions[parameter] = contributions;
                    fusedRecord.fusionMetadata.sourceCount = Math.max(
                        fusedRecord.fusionMetadata.sourceCount,
                        contributions.length
                    );
                }
            });
            
            // 只有当融合出有效数值时才添加记录
            if (Object.keys(fusedRecord.fusedValues).length > 0) {
                // 计算融合置信度
                fusedRecord.fusionMetadata.confidence = this.calculateFusionConfidence(
                    fusedRecord.sourceContributions
                );
                
                // 分配融合质量等级
                fusedRecord.quality = this.determineFusionQuality(
                    fusedRecord.sourceContributions,
                    fusedRecord.fusionMetadata.confidence
                );
                
                fusedData.push(fusedRecord);
            }
        });
        
        return {
            fusedData: fusedData,
            strategy: 'weighted_average',
            parameters: parameters
        };
    }
    
    // 基于优先级的融合策略
    async priorityBasedFusion(alignedData, parameters) {
        const {
            sourcePriorities = {},
            fallbackStrategy = 'highest_quality',
            conflictThreshold = 0.1
        } = parameters;
        
        const fusedData = [];
        
        alignedData.timePoints.forEach(timePoint => {
            const fusedRecord = {
                timestamp: timePoint,
                fusedValues: {},
                selectedSources: {},
                conflictInfo: {},
                fusionMetadata: {
                    method: 'priority_based',
                    fallbackStrategy: fallbackStrategy
                }
            };
            
            const recordsAtTime = alignedData.sources
                .map(source => ({
                    source: source,
                    record: source.alignedData.find(r => r.timestamp === timePoint),
                    priority: sourcePriorities[source.sourceId] || 0
                }))
                .filter(item => item.record !== undefined)
                .sort((a, b) => b.priority - a.priority); // 按优先级降序排列
            
            if (recordsAtTime.length === 0) return;
            
            // 按参数处理
            const parameterGroups = this.groupRecordsByParameter(recordsAtTime);
            
            Object.entries(parameterGroups).forEach(([parameter, parameterRecords]) => {
                const candidates = parameterRecords
                    .filter(({ record }) => record.values[parameter] !== undefined)
                    .map(({ source, record, priority }) => ({
                        sourceId: source.sourceId,
                        value: record.values[parameter],
                        quality: record.quality,
                        priority: priority,
                        confidence: record.confidence || 0.8,
                        timestamp: record.timestamp
                    }));
                
                if (candidates.length === 0) return;
                
                // 选择最高优先级数据
                let selectedCandidate = candidates[0];
                
                // 检测冲突
                const conflicts = this.detectValueConflicts(candidates, parameter, conflictThreshold);
                if (conflicts.length > 0) {
                    // 存在冲突，根据回退策略选择
                    switch (fallbackStrategy) {
                        case 'highest_quality':
                            selectedCandidate = this.selectByQuality(candidates);
                            break;
                        case 'most_recent':
                            selectedCandidate = this.selectByTime(candidates);
                            break;
                        case 'consensus':
                            selectedCandidate = this.selectByConsensus(candidates);
                            break;
                        default:
                            selectedCandidate = candidates[0]; // 保持优先级选择
                    }
                    
                    fusedRecord.conflictInfo[parameter] = {
                        conflictCount: conflicts.length,
                        resolution: fallbackStrategy,
                        alternativeValues: candidates.map(c => ({
                            source: c.sourceId,
                            value: c.value
                        }))
                    };
                }
                
                fusedRecord.fusedValues[parameter] = selectedCandidate.value;
                fusedRecord.selectedSources[parameter] = selectedCandidate.sourceId;
            });
            
            if (Object.keys(fusedRecord.fusedValues).length > 0) {
                fusedRecord.quality = this.determineFusionQualityFromSources(fusedRecord.selectedSources, recordsAtTime);
                fusedData.push(fusedRecord);
            }
        });
        
        return {
            fusedData: fusedData,
            strategy: 'priority_based',
            parameters: parameters
        };
    }
    
    // 计算融合权重
    calculateFusionWeight(record, source, strategy) {
        const weights = this.weightingStrategies[strategy];
        if (!weights) return 0.5; // 默认权重
        
        switch (strategy) {
            case 'quality_based':
                return weights[record.quality] || 0.5;
                
            case 'reliability_based':
                return weights[source.sourceType] || 0.5;
                
            case 'temporal_based':
                const recordTime = new Date(record.timestamp);
                const currentTime = new Date();
                const age = currentTime - recordTime;
                const maxAge = weights.maxAge;
                
                if (age > maxAge) {
                    return weights.decayFactor * Math.exp(-age / maxAge);
                }
                return 1.0;
                
            case 'hybrid':
                // 综合多种策略
                const qualityWeight = weights.quality[record.quality] || 0.5;
                const reliabilityWeight = weights.reliability[source.sourceType] || 0.5;
                const temporalWeight = this.calculateFusionWeight(record, source, 'temporal_based');
                
                return (qualityWeight * 0.4 + reliabilityWeight * 0.3 + temporalWeight * 0.3);
                
            default:
                return 0.5;
        }
    }
    
    // 计算融合置信度
    calculateFusionConfidence(sourceContributions) {
        if (Object.keys(sourceContributions).length === 0) return 0;
        
        let totalConfidence = 0;
        let totalParameters = 0;
        
        Object.values(sourceContributions).forEach(contributions => {
            if (Array.isArray(contributions) && contributions.length > 0) {
                const parameterConfidence = contributions.reduce((sum, contrib) => {
                    return sum + contrib.confidence * contrib.weight;
                }, 0) / contributions.reduce((sum, contrib) => sum + contrib.weight, 0);
                
                totalConfidence += parameterConfidence;
                totalParameters++;
            }
        });
        
        return totalParameters > 0 ? totalConfidence / totalParameters : 0;
    }
}
```

## 本节小结

本节系统建立了智慧水利监测数据的完整分类体系和标准化处理框架，为三维场景中的数据展示奠定了坚实基础。

### **关键知识点掌握**

**数据分类管理体系**：
- 按监测要素构建了涵盖水文、工程安全、水质环境等多类型的数据分类框架
- 按时间特性区分了实时数据和历史数据的不同处理机制和应用场景
- 建立了统一的数据结构定义和标准化存储格式

**数据质量控制技术**：
- 构建了完整性、准确性、一致性、时效性、逻辑性五个维度的质量评估体系
- 掌握了统计学方法、机器学习、领域知识等多种异常值检测技术
- 实现了插值、替换、删除、标记等多种异常值处理策略

**多源数据融合方法**：
- 设计了字段映射、单位转换、格式标准化的数据标准化处理流程
- 实现了加权平均、优先级选择、一致性投票等多种数据融合算法
- 建立了冲突检测与解决机制，确保融合结果的可靠性

### **技术能力提升**
- 具备了设计和实现数据质量控制系统的专业能力
- 掌握了处理多源异构数据整合的技术方法
- 学会了根据不同应用场景选择合适的数据处理策略
- 建立了面向水利行业的数据管理专业素养

### **实践应用价值**
- 为构建可靠的智慧水利数据管理平台提供了技术支撑
- 支撑基于数据驱动的科学决策和智能分析
- 保障监测数据的准确性、完整性和一致性
- 提升水利管理的信息化和现代化水平

通过本节学习，读者应该具备了处理复杂水利监测数据的综合能力，为后续章节中的数据可视化、三维场景集成和交互技术应用提供了可靠的数据基础。