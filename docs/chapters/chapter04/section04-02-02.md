# JavaScript核心语法与对象

本章节介绍JavaScript的核心语法和对象系统，这是开发智慧水利平台前端功能的基础。通过掌握这些核心概念，开发者可以实现各种复杂的交互功能和数据处理逻辑。

## 2.1 基础语法

### 2.1.1 变量与数据类型

JavaScript提供了多种数据类型，用于处理不同类型的水利监测数据和业务逻辑：

**基本数据类型：**
- **Number**：表示数值，如水位、流量数据
- **String**：表示文本，如站点名称、描述信息
- **Boolean**：表示真/假值，用于条件判断
- **null**：表示空值
- **undefined**：表示未定义的值
- **Symbol** (ES6)：表示唯一标识符

**引用数据类型：**
- **Object**：对象，如水利监测站点对象
- **Array**：数组，如水位历史数据集合
- **Function**：函数，封装特定功能
- **Date**：日期，处理时间相关数据

```javascript
// 水利监测数据变量示例
let stationName = "龙泉水库监测站";  // String类型
let currentWaterLevel = 145.23;      // Number类型
let isAlarmActive = false;           // Boolean类型
let lastReading = null;              // null类型
let measurementUnit = "米";          // String类型

// 引用类型示例
let waterLevelReadings = [142.5, 143.2, 144.8, 145.23];  // Array类型
let stationInfo = {                  // Object类型
    id: "ST10086",
    name: "龙泉水库监测站",
    location: {
        longitude: 116.345,
        latitude: 39.789
    },
    type: "水库",
    warningLevel: 150.0
};
```

在JavaScript中变量的声明可以使用`var`、`let`和`const`：
- `var`：函数作用域变量（传统方式，现代开发中较少使用）
- `let`：块级作用域变量，值可以改变
- `const`：块级作用域常量，值不可改变（对象内容可以修改）

```javascript
// 在智慧水利平台中的变量声明最佳实践
const WARNING_LEVEL = 150.0;  // 常量，警戒水位
let currentLevel = 145.23;    // 变量，当前水位
```

### 2.1.2 运算符与表达式

JavaScript提供了丰富的运算符，用于进行数学计算、逻辑判断等操作：

**算术运算符**：用于水文数据的计算
```javascript
// 计算蓄水量变化
let initialVolume = 2500000;  // 初始蓄水量(立方米)
let currentVolume = 2650000;  // 当前蓄水量(立方米)
let volumeChange = currentVolume - initialVolume;  // 蓄水量变化
let percentageChange = (volumeChange / initialVolume) * 100;  // 变化百分比
```

**比较运算符**：用于比较水文数据
```javascript
// 水位警戒判断
if (currentLevel > WARNING_LEVEL) {
    console.log("警告：水位超过警戒线！");
}

// 水质评级判断
const phValue = 7.2;
if (phValue >= 6.5 && phValue <= 8.5) {
    console.log("pH值在正常范围内");
}
```

**逻辑运算符**：用于组合条件判断
```javascript
// 复合条件预警判断
const highWaterLevel = currentLevel > WARNING_LEVEL;
const heavyRainfall = rainfallIntensity > 50;  // mm/h
const upstreamDischarge = upstreamFlow > 500;  // m³/s

if (highWaterLevel && (heavyRainfall || upstreamDischarge)) {
    console.log("严重警告：可能发生洪水风险！");
    activateEmergencyPlan();
}
```

### 2.1.3 控制结构

控制结构用于控制程序执行流程，在智慧水利平台中常用于实现业务逻辑和数据处理：

**条件语句**：
```javascript
// 水库水位预警等级判断
function getWaterLevelAlertLevel(waterLevel, warningLevel, dangerLevel) {
    if (waterLevel >= dangerLevel) {
        return "danger";
    } else if (waterLevel >= warningLevel) {
        return "warning";
    } else {
        return "normal";
    }
}

// 使用条件运算符(三元运算符)
const isRaining = rainfallIntensity > 0;
const weatherStatus = isRaining ? "降雨中" : "晴好";
```

**循环语句**：
```javascript
// for循环：处理多个监测站点数据
const stations = ["龙泉水库", "青龙湾", "丹江口", "密云水库"];
for (let i = 0; i < stations.length; i++) {
    fetchStationData(stations[i]);
}

// for...of循环：更现代的数组遍历方式
for (const station of stations) {
    displayStationInfo(station);
}

// while循环：持续监测直到条件满足
let waterLevel = getCurrentWaterLevel();
let targetLevel = 120.5;
while (waterLevel > targetLevel) {
    console.log(`当前水位: ${waterLevel}m，目标水位: ${targetLevel}m`);
    adjustDamDischarge(waterLevel - targetLevel);  // 调整泄流量
    // 等待一段时间后重新获取水位
    setTimeout(() => {
        waterLevel = getCurrentWaterLevel();
    }, 10000); // 10秒后重新检查
}
```

### 2.1.4 函数定义与调用

函数是JavaScript中的一等公民，在智慧水利平台中常用于封装特定的业务逻辑和数据处理：

**函数声明**：
```javascript
// 计算流域降雨量均值
function calculateAverageRainfall(rainfallData) {
    if (rainfallData.length === 0) return 0;
    
    let sum = 0;
    for (const data of rainfallData) {
        sum += data.value;
    }
    return sum / rainfallData.length;
}
```

**函数表达式**：
```javascript
// 使用函数表达式定义水位变化率计算函数
const calculateWaterLevelChangeRate = function(previousLevel, currentLevel, timeDiffHours) {
    return (currentLevel - previousLevel) / timeDiffHours;
};
```

**箭头函数**（ES6）：
```javascript
// 使用箭头函数简化监测数据过滤
const getAbnormalReadings = (readings, threshold) => 
    readings.filter(reading => reading.value > threshold);
```

**参数默认值**（ES6）：
```javascript
// 设置默认参数值
function fetchWaterQualityData(stationId, timeRange = "24h", parameters = ["pH", "溶解氧", "浊度"]) {
    console.log(`获取站点${stationId}的${timeRange}水质数据，包含参数：${parameters.join(', ')}`);
    // API调用逻辑
}
```

**实际应用示例**：水位监测数据处理
```javascript
// 水位监测数据处理函数
function analyzeWaterLevel(data) {
    const warningLevel = 95.0;
    let isWarning = false;
    
    for (let i = 0; i < data.length; i++) {
        if (data[i].level > warningLevel) {
            isWarning = true;
            console.log(`警告：${data[i].stationName}水位超过警戒线！`);
        }
    }
    
    return {
        maxLevel: Math.max(...data.map(item => item.level)),
        minLevel: Math.min(...data.map(item => item.level)),
        avgLevel: data.reduce((sum, item) => sum + item.level, 0) / data.length,
        isWarning: isWarning
    };
}

// 调用示例
const stationReadings = [
    { stationName: "龙泉水库", level: 94.5 },
    { stationName: "丹江口", level: 96.2 },
    { stationName: "密云水库", level: 93.8 }
];

const analysisResult = analyzeWaterLevel(stationReadings);
console.log(`最高水位: ${analysisResult.maxLevel}m`);
console.log(`最低水位: ${analysisResult.minLevel}m`);
console.log(`平均水位: ${analysisResult.avgLevel}m`);
console.log(`是否有预警: ${analysisResult.isWarning ? '是' : '否'}`);
```

## 2.2 对象与面向对象编程

JavaScript是一种基于原型的面向对象语言，通过对象可以更好地组织和管理智慧水利平台的数据和功能。

### 2.2.1 对象字面量

对象字面量是创建对象最简单的方式，适用于表示水利监测站点、水文参数等实体：

```javascript
// 使用对象字面量表示水库信息
const reservoir = {
    name: "丹江口水库",
    capacity: 29.05e9,  // 29.05亿立方米
    currentLevel: 165.23,
    normalLevel: 170.0,
    deadLevel: 140.0,
    catchmentArea: 95200,  // 95200平方公里
    location: {
        province: "湖北省",
        city: "十堰市",
        coordinates: {
            longitude: 111.5,
            latitude: 32.7
        }
    },
    // 方法
    getCurrentStorage: function() {
        // 实际中可能是一个更复杂的计算
        return this.capacity * (this.currentLevel - this.deadLevel) / 
               (this.normalLevel - this.deadLevel);
    },
    // ES6简写方法
    isLowWaterLevel() {
        return this.currentLevel < (this.deadLevel + 10);
    }
};

// 访问对象属性
console.log(`${reservoir.name}当前水位：${reservoir.currentLevel}m`);
console.log(`水库位置：${reservoir.location.province}${reservoir.location.city}`);

// 调用对象方法
const currentStorage = reservoir.getCurrentStorage();
console.log(`当前蓄水量约为：${(currentStorage/1e8).toFixed(2)}亿立方米`);
```

### 2.2.2 构造函数与类

对于需要创建多个相似对象的场景，如多个监测站点、设备等，可以使用构造函数或ES6类：

**构造函数方式**：
```javascript
// 监测站点构造函数
function MonitoringStation(id, name, location, type) {
    this.id = id;
    this.name = name;
    this.location = location;
    this.type = type;
    this.readings = [];
    
    // 方法
    this.addReading = function(time, value) {
        this.readings.push({ time, value });
    };
    
    this.getLatestReading = function() {
        if (this.readings.length === 0) return null;
        return this.readings[this.readings.length - 1];
    };
}

// 创建监测站点实例
const rainStation = new MonitoringStation(
    "RS001", 
    "龙泉山雨量站", 
    { longitude: 116.345, latitude: 39.789 },
    "rainfall"
);

// 添加监测数据
rainStation.addReading("2023-06-15T08:00:00", 5.2);
rainStation.addReading("2023-06-15T09:00:00", 7.8);

// 获取最新数据
const latestReading = rainStation.getLatestReading();
console.log(`最新降雨量: ${latestReading.value}mm，时间: ${latestReading.time}`);
```

**ES6类方式**（推荐）：
```javascript
// 监测站点类
class MonitoringStation {
    constructor(id, name, location, type) {
        this.id = id;
        this.name = name;
        this.location = location;
        this.type = type;
        this.readings = [];
    }
    
    // 添加读数
    addReading(time, value) {
        this.readings.push({ time, value });
    }
    
    // 获取最新读数
    getLatestReading() {
        if (this.readings.length === 0) return null;
        return this.readings[this.readings.length - 1];
    }
    
    // 计算最近n小时的平均值
    getAverageReading(hours = 24) {
        const now = new Date();
        const threshold = new Date(now - hours * 60 * 60 * 1000);
        
        const recentReadings = this.readings.filter(r => new Date(r.time) >= threshold);
        if (recentReadings.length === 0) return 0;
        
        return recentReadings.reduce((sum, r) => sum + r.value, 0) / recentReadings.length;
    }
}

// 创建实例
const waterLevelStation = new MonitoringStation(
    "WL001", 
    "龙泉水库水位站", 
    { longitude: 116.348, latitude: 39.792 },
    "waterLevel"
);

// 使用方法
waterLevelStation.addReading("2023-06-15T08:00:00", 142.5);
waterLevelStation.addReading("2023-06-15T12:00:00", 142.8);
waterLevelStation.addReading("2023-06-15T16:00:00", 143.2);

console.log(`最新水位: ${waterLevelStation.getLatestReading().value}m`);
console.log(`24小时平均水位: ${waterLevelStation.getAverageReading()}m`);
```

### 2.2.3 继承与多态

在智慧水利平台中，可以使用继承来表示不同类型的监测站点或设备：

```javascript
// 基础监测站点类
class MonitoringStation {
    constructor(id, name, location) {
        this.id = id;
        this.name = name;
        this.location = location;
        this.status = "normal";
    }
    
    getInfo() {
        return `监测站点：${this.name}（ID: ${this.id}）`;
    }
    
    checkStatus() {
        return this.status;
    }
}

// 水位监测站点（继承自基础监测站点）
class WaterLevelStation extends MonitoringStation {
    constructor(id, name, location, warningLevel, dangerLevel) {
        super(id, name, location);  // 调用父类构造函数
        this.warningLevel = warningLevel;
        this.dangerLevel = dangerLevel;
        this.currentLevel = 0;
    }
    
    updateLevel(level) {
        this.currentLevel = level;
        // 更新状态
        if (level >= this.dangerLevel) {
            this.status = "danger";
        } else if (level >= this.warningLevel) {
            this.status = "warning";
        } else {
            this.status = "normal";
        }
    }
    
    // 重写父类方法（多态）
    getInfo() {
        return `${super.getInfo()} - 当前水位：${this.currentLevel}m`;
    }
}

// 雨量监测站点
class RainfallStation extends MonitoringStation {
    constructor(id, name, location, warningThreshold) {
        super(id, name, location);
        this.warningThreshold = warningThreshold;  // mm/h
        this.currentRainfall = 0;
    }
    
    updateRainfall(rainfall) {
        this.currentRainfall = rainfall;
        // 更新状态
        if (rainfall >= this.warningThreshold) {
            this.status = "warning";
        } else {
            this.status = "normal";
        }
    }
    
    // 重写父类方法（多态）
    getInfo() {
        return `${super.getInfo()} - 当前降雨量：${this.currentRainfall}mm/h`;
    }
}

// 使用这些类
const waterStation = new WaterLevelStation(
    "WL002", 
    "青龙湾水位站", 
    { longitude: 116.4, latitude: 39.8 },
    145.0,  // 警戒水位
    147.0   // 危险水位
);

const rainStation = new RainfallStation(
    "RF002",
    "青龙湾雨量站",
    { longitude: 116.41, latitude: 39.81 },
    50.0    // 降雨预警阈值(mm/h)
);

// 更新数据
waterStation.updateLevel(146.2);
rainStation.updateRainfall(35.8);

// 获取信息
console.log(waterStation.getInfo());  // 水位站信息
console.log(rainStation.getInfo());   // 雨量站信息

// 检查状态
console.log(`水位站状态: ${waterStation.checkStatus()}`);
console.log(`雨量站状态: ${rainStation.checkStatus()}`);
```

### 2.2.4 封装与模块化

通过封装和模块化，可以更好地组织智慧水利平台的代码：

```javascript
// 水文数据处理模块
const HydrologicalDataProcessor = {
    // 计算流量
    calculateFlow(area, velocity) {
        return area * velocity;  // 断面面积 * 流速 = 流量
    },
    
    // 计算蒸发损失
    calculateEvaporationLoss(surfaceArea, evaporationRate, hours) {
        return surfaceArea * evaporationRate * hours;
    },
    
    // 洪水预报简化计算
    predictFloodPeak(upstreamFlow, rainfall, catchmentArea, timeToReach) {
        // 简化模型，实际应用中会有更复杂的算法
        const rainfallContribution = rainfall * catchmentArea * 0.6;  // 假设60%的降雨形成径流
        const predictedPeak = upstreamFlow + (rainfallContribution / (timeToReach * 3600));
        return predictedPeak;
    }
};

// 使用模块
const riverCrossSection = 120;  // 河道断面面积(m²)
const waterVelocity = 2.5;      // 水流速度(m/s)
const flow = HydrologicalDataProcessor.calculateFlow(riverCrossSection, waterVelocity);
console.log(`当前流量: ${flow}m³/s`);

// 洪水预报
const upstreamFlow = 500;      // 上游流量(m³/s)
const rainfall = 80;           // 降雨量(mm)
const catchmentArea = 2000e6;  // 集水面积(m²)
const timeToReach = 8;         // 汇流时间(h)

const predictedPeak = HydrologicalDataProcessor.predictFloodPeak(
    upstreamFlow, rainfall, catchmentArea, timeToReach
);
console.log(`预计洪峰流量: ${predictedPeak.toFixed(2)}m³/s`);
```

## 2.3 函数进阶

JavaScript中的函数具有强大而灵活的特性，掌握这些特性对于开发高质量的智慧水利平台至关重要。

### 2.3.1 函数是一等公民

在JavaScript中，函数是一等公民，可以赋值给变量、作为参数传递和作为返回值：

```javascript
// 函数赋值给变量
const calculateWaterVolume = function(depth, area) {
    return depth * area;
};

// 函数作为参数
function processReservoirData(data, processingFunction) {
    return processingFunction(data);
}

// 使用例子
const reservoirData = {
    depth: 45.6,
    area: 5600000  // 560万平方米
};

// 计算体积的函数
function calculateVolume(data) {
    return data.depth * data.area;
}

// 计算蓄水率的函数
function calculateStorageRate(data) {
    const maxDepth = 60;  // 最大水深
    return data.depth / maxDepth;
}

// 作为参数传递不同的函数
const volume = processReservoirData(reservoirData, calculateVolume);
const storageRate = processReservoirData(reservoirData, calculateStorageRate);

console.log(`水库当前蓄水量: ${volume/1000000}百万立方米`);
console.log(`水库当前蓄水率: ${(storageRate*100).toFixed(1)}%`);
```

### 2.3.2 闭包与作用域

闭包是JavaScript中重要的概念，可以用于创建私有变量和持久状态：

```javascript
// 使用闭包创建水位监测器
function createWaterLevelMonitor(stationId, warningLevel) {
    // 私有变量
    let readings = [];
    let lastAlertTime = null;
    
    // 返回包含方法的对象
    return {
        // 添加水位读数
        addReading(time, level) {
            readings.push({ time, level });
            
            // 检查是否需要发出警报
            if (level > warningLevel && (!lastAlertTime || new Date() - lastAlertTime > 3600000)) {
                this.triggerAlert(level);
                lastAlertTime = new Date();
            }
            
            // 只保留最近100条读数
            if (readings.length > 100) {
                readings.shift();
            }
        },
        
        // 获取历史读数
        getReadings() {
            return [...readings];  // 返回副本以保护原始数据
        },
        
        // 触发警报
        triggerAlert(level) {
            console.log(`警告：站点${stationId}水位(${level}m)超过警戒线(${warningLevel}m)！`);
            // 实际应用中可能会发送通知或触发其他操作
        },
        
        // 获取最新水位
        getLatestLevel() {
            if (readings.length === 0) return null;
            return readings[readings.length - 1].level;
        }
    };
}

// 使用闭包创建监测器
const monitor = createWaterLevelMonitor("WL003", 150.0);

// 添加读数
monitor.addReading("2023-06-15T10:00:00", 148.5);
monitor.addReading("2023-06-15T11:00:00", 149.2);
monitor.addReading("2023-06-15T12:00:00", 150.3);  // 将触发警报

// 获取最新水位
console.log(`最新水位: ${monitor.getLatestLevel()}m`);
```

### 2.3.3 箭头函数与this绑定

箭头函数提供了更简洁的语法，并且不绑定自己的`this`值，这在处理回调和事件处理时特别有用：

```javascript
// 传统函数与箭头函数比较
const waterQualityMonitor = {
    parameters: ["pH", "溶解氧", "浊度", "电导率"],
    readings: [],
    
    // 使用传统函数
    addReadingsTraditional: function(newReadings) {
        const self = this;  // 保存this引用
        newReadings.forEach(function(reading) {
            // 在传统函数内部，this不指向waterQualityMonitor
            self.readings.push(reading);
        });
    },
    
    // 使用箭头函数
    addReadingsArrow: function(newReadings) {
        // 箭头函数不绑定自己的this，使用外部作用域的this
        newReadings.forEach(reading => {
            this.readings.push(reading);
        });
    },
    
    // 处理数据的箭头函数示例
    processData: function() {
        // 使用箭头函数和map进行数据处理
        return this.readings.map(reading => ({
            time: reading.time,
            values: this.parameters.map(param => ({
                parameter: param,
                value: reading.values[param],
                status: this.evaluateParameter(param, reading.values[param])
            }))
        }));
    },
    
    // 评估参数
    evaluateParameter: function(parameter, value) {
        // 简化的参数评估逻辑
        const thresholds = {
            "pH": { min: 6.5, max: 8.5 },
            "溶解氧": { min: 5.0, max: Infinity },
            "浊度": { min: 0, max: 5.0 },
            "电导率": { min: 0, max: 2000 }
        };
        
        if (!thresholds[parameter]) return "unknown";
        
        if (value < thresholds[parameter].min) return "low";
        if (value > thresholds[parameter].max) return "high";
        return "normal";
    }
};

// 使用箭头函数方法
const newReadings = [
    {
        time: "2023-06-15T14:00:00",
        values: {
            "pH": 7.2,
            "溶解氧": 6.8,
            "浊度": 3.5,
            "电导率": 850
        }
    }
];

waterQualityMonitor.addReadingsArrow(newReadings);
const processedData = waterQualityMonitor.processData();
console.log(processedData);
```

### 2.3.4 Promise与异步编程

在智慧水利平台中，异步数据获取是常见需求，Promise提供了更优雅的异步编程方式：

```javascript
// 使用Promise获取水利数据
function fetchWaterResourceData(stationId) {
    return new Promise((resolve, reject) => {
        // 模拟API请求
        setTimeout(() => {
            if (stationId) {
                // 模拟成功返回数据
                const data = {
                    stationId: stationId,
                    name: `站点${stationId}`,
                    waterLevel: 145.2 + Math.random() * 5,
                    flow: 210 + Math.random() * 50,
                    timestamp: new Date().toISOString()
                };
                resolve(data);
            } else {
                // 模拟错误
                reject(new Error("未提供有效的站点ID"));
            }
        }, 1000);
    });
}

// 使用Promise
fetchWaterResourceData("WL004")
    .then(data => {
        console.log(`成功获取站点数据：`);
        console.log(`站点: ${data.name}`);
        console.log(`水位: ${data.waterLevel.toFixed(2)}m`);
        console.log(`流量: ${data.flow.toFixed(2)}m³/s`);
        
        // 链式调用：获取相关站点数据
        return fetchWaterResourceData("WL005");
    })
    .then(data => {
        console.log(`\n相关站点数据：`);
        console.log(`站点: ${data.name}`);
        console.log(`水位: ${data.waterLevel.toFixed(2)}m`);
    })
    .catch(error => {
        console.error(`获取数据失败: ${error.message}`);
    })
    .finally(() => {
        console.log("数据请求处理完成");
    });
```

### 2.3.5 async/await

`async/await`是基于Promise的语法糖，让异步代码更加清晰：

```javascript
// 使用async/await获取水利数据
async function fetchWaterResourceData(stationId) {
    try {
        const response = await fetch(`/api/stations/${stationId}/data`);
        if (!response.ok) {
            throw new Error('数据获取失败');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('获取水利数据出错:', error);
        return null;
    }
}

// 使用async/await更新多个站点数据
async function updateMultipleStations(stationIds) {
    try {
        console.log("开始更新站点数据...");
        
        // 并行请求多个站点数据
        const promises = stationIds.map(id => fetchWaterResourceData(id));
        const results = await Promise.all(promises);
        
        // 处理结果
        let validResults = 0;
        for (const data of results) {
            if (data) {
                updateStationDisplay(data);
                validResults++;
            }
        }
        
        console.log(`成功更新了${validResults}/${stationIds.length}个站点的数据`);
    } catch (error) {
        console.error("更新站点数据失败:", error);
    }
}

// 更新站点显示
function updateStationDisplay(data) {
    console.log(`更新站点${data.stationId}的显示数据`);
    // 实际应用中会更新DOM元素或图表
}

// 使用函数
updateMultipleStations(["WL001", "WL002", "WL003", "WL004"]);
```

## 2.4 小结

本章介绍了JavaScript的核心语法和对象系统，这些是开发智慧水利平台前端功能的基础。通过掌握这些概念，开发者可以：

1. 使用基本语法和数据类型处理各种水利数据
2. 通过对象和面向对象编程组织复杂的水利监测和管理系统
3. 利用函数的灵活特性实现各种业务逻辑
4. 使用闭包和模块化思想组织代码
5. 通过Promise和async/await优雅地处理异步操作

在下一章中，我们将学习DOM操作和事件处理，这是实现智慧水利平台用户交互功能的核心技术。 

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
