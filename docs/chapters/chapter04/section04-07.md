## 4.2.1 JavaScript基础语法与数据类型

JavaScript作为一门动态类型的解释性语言，其语法设计兼顾了灵活性和表达力[20]。理解JavaScript的基础语法和数据类型系统是掌握这门语言的第一步，也是编写高质量代码的基础。在智慧水利平台开发中，正确地使用变量、数据类型、操作符等基础概念，能够确保数据处理的准确性和程序运行的稳定性。

### 变量声明与作用域

ES6引入了`let`和`const`关键字，与传统的`var`一起构成了JavaScript的变量声明体系。理解它们的区别对于编写现代JavaScript代码至关重要。

#### var、let、const的区别

```javascript
// var：函数作用域，存在变量提升
function waterLevelMonitor() {
    console.log(level); // undefined（变量提升，但未赋值）
    
    if (true) {
        var level = 125.5; // 函数作用域
        var level = 130.0; // 可以重复声明
    }
    
    console.log(level); // 130.0（在函数内可访问）
}

// let：块作用域，暂时性死区
function modernWaterMonitor() {
    // console.log(currentLevel); // ReferenceError: 暂时性死区
    
    if (true) {
        let currentLevel = 125.5; // 块作用域
        // let currentLevel = 130.0; // SyntaxError: 不能重复声明
        console.log(currentLevel); // 125.5
    }
    
    // console.log(currentLevel); // ReferenceError: 块外不可访问
}

// const：块作用域，必须初始化，不可重新赋值
const DANGER_LEVEL = 150.0; // 必须在声明时初始化
// DANGER_LEVEL = 160.0; // TypeError: 不能重新赋值

// 但是对象和数组的内容可以修改
const station = {
    id: 'SH001',
    name: '上海监测站',
    level: 125.5
};

station.level = 130.0; // 可以修改对象属性
station.lastUpdate = new Date(); // 可以添加新属性

const readings = [120, 125, 130];
readings.push(135); // 可以修改数组内容
console.log(readings); // [120, 125, 130, 135]

// 如果需要完全不可变，使用Object.freeze()
const STATION_TYPES = Object.freeze({
    RIVER: 'river',
    LAKE: 'lake',
    RESERVOIR: 'reservoir'
});

// STATION_TYPES.RIVER = 'stream'; // 严格模式下会抛出错误
```

#### 作用域链与变量查找

```javascript
// 全局作用域
const GLOBAL_CONFIG = {
    maxLevel: 200,
    minLevel: 0,
    alertThreshold: 150
};

function createStationMonitor(stationId) {
    // 函数作用域
    const stationConfig = {
        id: stationId,
        checkInterval: 5000
    };
    
    function checkWaterLevel() {
        // 嵌套函数作用域
        let currentLevel = getCurrentLevel();
        
        // 作用域链查找：currentLevel -> stationConfig -> GLOBAL_CONFIG
        if (currentLevel > GLOBAL_CONFIG.alertThreshold) {
            console.log(`站点 ${stationConfig.id} 水位超过警戒线`);
        }
        
        // 块作用域
        if (currentLevel > stationConfig.emergencyLevel) {
            let emergencyAction = 'immediate_evacuation';
            console.log(`执行紧急行动: ${emergencyAction}`);
        }
        // emergencyAction在此处不可访问
    }
    
    function getCurrentLevel() {
        // 模拟获取水位数据
        return Math.random() * 200;
    }
    
    return {
        start: function() {
            setInterval(checkWaterLevel, stationConfig.checkInterval);
        }
    };
}

// 使用示例
const monitor = createStationMonitor('SH001');
monitor.start();
```

### 数据类型系统

JavaScript的数据类型分为原始类型（Primitive Types）和引用类型（Reference Types）两大类。

#### 原始数据类型

```javascript
// 1. Number - 数值类型
let waterLevel = 125.5;          // 浮点数
let stationCount = 10;           // 整数
let temperature = -5.2;          // 负数
let humidity = Infinity;         // 无穷大
let invalidReading = NaN;        // 非数值

// 数值的特殊操作
console.log(Number.isInteger(125));     // true
console.log(Number.isNaN(NaN));         // true
console.log(Number.parseFloat('125.5')); // 125.5
console.log(Number.parseInt('125.5'));   // 125

// 安全整数范围
console.log(Number.MAX_SAFE_INTEGER);   // 9007199254740991
console.log(Number.MIN_SAFE_INTEGER);   // -9007199254740991

// 2. String - 字符串类型
let stationName = '上海水位监测站';
let stationId = "SH001";
let alertMessage = `当前水位：${waterLevel}米`;

// 字符串方法示例
console.log(stationName.length);        // 7
console.log(stationId.toUpperCase());   // "SH001"
console.log(stationName.includes('上海')); // true
console.log(alertMessage.startsWith('当前')); // true

// 3. Boolean - 布尔类型
let isActive = true;
let hasWarning = false;
let isEmergency = Boolean(waterLevel > 150); // 显式转换

// 4. Undefined - 未定义类型
let uninitializedValue;
console.log(uninitializedValue);        // undefined
console.log(typeof uninitializedValue); // "undefined"

// 5. Null - 空值类型
let emptyData = null;
console.log(emptyData);                 // null
console.log(typeof emptyData);          // "object"（历史遗留问题）

// 6. Symbol - 符号类型（ES6新增）
const STATION_TYPE = Symbol('stationType');
const READING_TIME = Symbol('readingTime');

let station = {
    [STATION_TYPE]: 'river',
    [READING_TIME]: new Date(),
    name: '测试站点'
};

console.log(station[STATION_TYPE]);     // "river"
console.log(Object.keys(station));     // ["name"]（Symbol不出现在枚举中）

// 7. BigInt - 大整数类型（ES2020新增）
let largeNumber = 123456789012345678901234567890n;
let anotherLarge = BigInt('123456789012345678901234567890');
console.log(largeNumber + 1n);          // 123456789012345678901234567891n
```

#### 引用数据类型

```javascript
// 1. Object - 对象类型
let waterStation = {
    id: 'SH001',
    name: '上海监测站',
    coordinates: {
        latitude: 31.2304,
        longitude: 121.4737
    },
    readings: [],
    
    // 方法
    addReading: function(level, timestamp = new Date()) {
        this.readings.push({
            level: level,
            timestamp: timestamp
        });
    },
    
    getLatestReading: function() {
        return this.readings.length > 0 
            ? this.readings[this.readings.length - 1] 
            : null;
    }
};

// 对象属性访问
console.log(waterStation.name);              // 点记法
console.log(waterStation['coordinates']);    // 括号记法
console.log(waterStation.coordinates.latitude); // 嵌套访问

// 2. Array - 数组类型
let waterLevels = [120.5, 125.0, 130.2, 128.5, 135.0];

// 数组方法示例
let avgLevel = waterLevels.reduce((sum, level) => sum + level, 0) / waterLevels.length;
let highLevels = waterLevels.filter(level => level > 125);
let levelStatus = waterLevels.map(level => ({
    level: level,
    status: level > 130 ? 'high' : 'normal'
}));

console.log('平均水位:', avgLevel);
console.log('高水位读数:', highLevels);
console.log('水位状态:', levelStatus);

// 3. Function - 函数类型
function calculateFlowRate(volume, time) {
    if (time === 0) {
        throw new Error('时间不能为零');
    }
    return volume / time;
}

// 函数表达式
const checkAlert = function(level, threshold) {
    return level > threshold;
};

// 箭头函数
const formatLevel = (level) => `${level.toFixed(2)}m`;

// 4. Date - 日期类型
let now = new Date();
let specificDate = new Date('2024-01-15T10:30:00');
let timestamp = new Date(1642234200000);

console.log(now.toISOString());              // ISO格式
console.log(specificDate.getFullYear());    // 2024
console.log(timestamp.toLocaleDateString()); // 本地日期格式

// 5. RegExp - 正则表达式类型
let stationIdPattern = /^[A-Z]{2}\d{3}$/;
let phonePattern = new RegExp('^1[3-9]\\d{9}$');

console.log(stationIdPattern.test('SH001'));  // true
console.log(stationIdPattern.test('sh001'));  // false
console.log(phonePattern.test('13812345678')); // true
```

### 类型检测与转换

准确的类型检测和合理的类型转换是编写健壮代码的重要技能。

#### 类型检测方法

```javascript
// typeof 操作符
console.log(typeof 123);           // "number"
console.log(typeof 'hello');       // "string"
console.log(typeof true);          // "boolean"
console.log(typeof undefined);     // "undefined"
console.log(typeof null);          // "object"（已知bug）
console.log(typeof {});            // "object"
console.log(typeof []);            // "object"
console.log(typeof function(){}); // "function"

// instanceof 操作符
console.log([] instanceof Array);           // true
console.log({} instanceof Object);          // true
console.log(new Date() instanceof Date);    // true

// Object.prototype.toString 方法（最准确）
function getType(value) {
    return Object.prototype.toString.call(value).slice(8, -1);
}

console.log(getType(123));          // "Number"
console.log(getType('hello'));      // "String"
console.log(getType([]));           // "Array"
console.log(getType({}));           // "Object"
console.log(getType(null));         // "Null"
console.log(getType(new Date()));   // "Date"

// 实用的类型检测函数
function isArray(value) {
    return Array.isArray(value);
}

function isObject(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function isFunction(value) {
    return typeof value === 'function';
}

function isEmpty(value) {
    if (value == null) return true;
    if (typeof value === 'string' || Array.isArray(value)) {
        return value.length === 0;
    }
    if (typeof value === 'object') {
        return Object.keys(value).length === 0;
    }
    return false;
}

// 智慧水利应用示例
function validateStationData(data) {
    const errors = [];
    
    if (!isObject(data)) {
        errors.push('数据必须是对象类型');
        return errors;
    }
    
    if (typeof data.id !== 'string' || isEmpty(data.id)) {
        errors.push('站点ID必须是非空字符串');
    }
    
    if (typeof data.level !== 'number' || isNaN(data.level)) {
        errors.push('水位必须是有效数值');
    }
    
    if (!isArray(data.coordinates) || data.coordinates.length !== 2) {
        errors.push('坐标必须是包含两个元素的数组');
    }
    
    return errors;
}

// 使用示例
const testData = {
    id: 'SH001',
    level: 125.5,
    coordinates: [31.2304, 121.4737]
};

const validationErrors = validateStationData(testData);
if (validationErrors.length > 0) {
    console.error('数据验证失败:', validationErrors);
} else {
    console.log('数据验证通过');
}
```

#### 类型转换

```javascript
// 显式类型转换
let numberStr = '125.5';
let boolStr = 'true';
let dateStr = '2024-01-15';

// 转换为数值
let num1 = Number(numberStr);        // 125.5
let num2 = parseInt(numberStr);      // 125
let num3 = parseFloat(numberStr);    // 125.5
let num4 = +numberStr;               // 125.5（一元加号）

// 转换为字符串
let str1 = String(125.5);            // "125.5"
let str2 = (125.5).toString();       // "125.5"
let str3 = 125.5 + '';               // "125.5"（隐式转换）

// 转换为布尔值
let bool1 = Boolean('hello');        // true
let bool2 = Boolean('');             // false
let bool3 = Boolean(0);              // false
let bool4 = Boolean(125);            // true
let bool5 = !!125;                   // true（双重否定）

// 隐式类型转换（自动转换）
console.log('5' + 3);                // "53"（字符串拼接）
console.log('5' - 3);                // 2（数值运算）
console.log('5' * 3);                // 15（数值运算）
console.log('5' / 3);                // 1.6666666666666667
console.log(true + 1);               // 2
console.log(false + 1);              // 1

// 智慧水利中的类型转换应用
function processWaterLevelData(rawData) {
    const processedData = {
        stationId: String(rawData.stationId || ''),
        level: Number(rawData.level) || 0,
        timestamp: new Date(rawData.timestamp || Date.now()),
        isActive: Boolean(rawData.isActive),
        coordinates: Array.isArray(rawData.coordinates) 
            ? rawData.coordinates.map(Number) 
            : [0, 0]
    };
    
    // 数据验证
    if (isNaN(processedData.level)) {
        throw new Error('无效的水位数据');
    }
    
    if (processedData.coordinates.some(isNaN)) {
        throw new Error('无效的坐标数据');
    }
    
    return processedData;
}

// 使用示例
const rawInput = {
    stationId: 123,
    level: '125.5',
    timestamp: '2024-01-15T10:30:00',
    isActive: 1,
    coordinates: ['31.2304', '121.4737']
};

try {
    const cleanData = processWaterLevelData(rawInput);
    console.log('处理后的数据:', cleanData);
} catch (error) {
    console.error('数据处理失败:', error.message);
}
```

### 操作符详解

JavaScript提供了丰富的操作符用于各种数据操作。

#### 算术与比较操作符

```javascript
// 算术操作符
let a = 10, b = 3;

console.log(a + b);    // 13（加法）
console.log(a - b);    // 7（减法）
console.log(a * b);    // 30（乘法）
console.log(a / b);    // 3.3333333333333335（除法）
console.log(a % b);    // 1（取余）
console.log(a ** b);   // 1000（幂运算，ES2016）

// 水利计算示例
function calculateReservoirCapacity(length, width, depth) {
    return length * width * depth; // 立方米
}

function calculateFlowVelocity(flowRate, crossSectionArea) {
    if (crossSectionArea === 0) {
        throw new Error('横截面积不能为零');
    }
    return flowRate / crossSectionArea; // 米/秒
}

// 比较操作符
let level1 = 125;
let level2 = '125';
let level3 = 130;

console.log(level1 == level2);   // true（相等，类型转换）
console.log(level1 === level2);  // false（严格相等，不转换类型）
console.log(level1 != level3);   // true（不等）
console.log(level1 !== level2);  // true（严格不等）
console.log(level1 < level3);    // true（小于）
console.log(level1 <= level2);   // true（小于等于）

// 水位比较函数
function compareWaterLevels(current, threshold) {
    // 使用严格比较避免类型转换问题
    if (typeof current !== 'number' || typeof threshold !== 'number') {
        throw new Error('水位值必须是数值类型');
    }
    
    if (current > threshold) {
        return 'above';
    } else if (current < threshold) {
        return 'below';
    } else {
        return 'equal';
    }
}
```

#### 逻辑操作符与短路求值

```javascript
// 逻辑操作符
let isActive = true;
let hasData = false;
let level = 125;

console.log(isActive && hasData);    // false（逻辑与）
console.log(isActive || hasData);    // true（逻辑或）
console.log(!isActive);              // false（逻辑非）

// 短路求值的应用
function getStationName(station) {
    // 如果station存在且有name属性，返回name，否则返回默认值
    return station && station.name || '未知站点';
}

function processData(data) {
    // 只有在data存在时才调用process方法
    data && data.process && data.process();
}

// 空值合并操作符（ES2020）
let defaultLevel = null;
let actualLevel = defaultLevel ?? 0; // 0（只有null和undefined才使用默认值）

// 可选链操作符（ES2020）
let station = {
    info: {
        location: {
            city: '上海'
        }
    }
};

console.log(station?.info?.location?.city);     // "上海"
console.log(station?.info?.contact?.phone);     // undefined（不会抛错）

// 智慧水利应用示例
function getAlertLevel(station) {
    const currentLevel = station?.readings?.current?.level;
    const thresholds = station?.config?.thresholds;
    
    if (!currentLevel || !thresholds) {
        return 'unknown';
    }
    
    return currentLevel > thresholds.danger ? 'danger' :
           currentLevel > thresholds.warning ? 'warning' : 'normal';
}

function shouldSendAlert(station) {
    const isActive = station?.status?.active ?? false;
    const hasRecentData = station?.lastUpdate && 
                         (Date.now() - station.lastUpdate) < 300000; // 5分钟内
    const alertLevel = getAlertLevel(station);
    
    return isActive && hasRecentData && alertLevel !== 'normal';
}
```

### 控制结构

控制结构决定了程序的执行流程，是实现业务逻辑的重要工具。

#### 条件语句

```javascript
// if...else语句
function determineFloodRisk(waterLevel, historicalMax) {
    let riskLevel;
    
    if (waterLevel >= historicalMax * 0.95) {
        riskLevel = 'extremely-high';
    } else if (waterLevel >= historicalMax * 0.85) {
        riskLevel = 'high';
    } else if (waterLevel >= historicalMax * 0.70) {
        riskLevel = 'moderate';
    } else if (waterLevel >= historicalMax * 0.50) {
        riskLevel = 'low';
    } else {
        riskLevel = 'minimal';
    }
    
    return riskLevel;
}

// switch语句
function getAlertMessage(alertType) {
    let message;
    
    switch (alertType) {
        case 'flood-warning':
            message = '洪水预警：请注意安全，及时撤离低洼地区';
            break;
        case 'drought-alert':
            message = '干旱预警：请节约用水，关注水源状况';
            break;
        case 'equipment-failure':
            message = '设备故障：监测设备异常，正在进行维修';
            break;
        case 'data-anomaly':
            message = '数据异常：检测到不正常的监测数据';
            break;
        default:
            message = '系统通知：请关注最新的水利信息';
    }
    
    return message;
}

// 三元操作符
const getStatusColor = (level, threshold) => 
    level > threshold ? 'red' : 'green';

const formatLevel = (level) => 
    level !== null ? `${level.toFixed(2)}m` : '无数据';
```

#### 循环语句

```javascript
// for循环
function calculateAverageLevel(readings) {
    if (!Array.isArray(readings) || readings.length === 0) {
        return null;
    }
    
    let sum = 0;
    for (let i = 0; i < readings.length; i++) {
        if (typeof readings[i] === 'number' && !isNaN(readings[i])) {
            sum += readings[i];
        }
    }
    
    return sum / readings.length;
}

// for...of循环（遍历可迭代对象）
function findMaxLevel(readings) {
    let maxLevel = -Infinity;
    
    for (const reading of readings) {
        if (typeof reading === 'number' && reading > maxLevel) {
            maxLevel = reading;
        }
    }
    
    return maxLevel === -Infinity ? null : maxLevel;
}

// for...in循环（遍历对象属性）
function validateStationConfig(config) {
    const errors = [];
    const requiredFields = ['id', 'name', 'location', 'thresholds'];
    
    for (const field in config) {
        if (config.hasOwnProperty(field)) {
            console.log(`检查字段: ${field} = ${config[field]}`);
        }
    }
    
    for (const field of requiredFields) {
        if (!(field in config)) {
            errors.push(`缺少必需字段: ${field}`);
        }
    }
    
    return errors;
}

// while循环
function waitForStableReading(getReading, maxAttempts = 10) {
    let attempts = 0;
    let previousReading = null;
    let currentReading = getReading();
    
    while (attempts < maxAttempts) {
        if (previousReading !== null && 
            Math.abs(currentReading - previousReading) < 0.1) {
            console.log(`读数稳定: ${currentReading}m`);
            return currentReading;
        }
        
        previousReading = currentReading;
        currentReading = getReading();
        attempts++;
        
        // 模拟等待
        console.log(`第${attempts}次读数: ${currentReading}m`);
    }
    
    console.log('未能获得稳定读数');
    return null;
}

// do...while循环
function retryDataUpload(uploadFunction, maxRetries = 3) {
    let retryCount = 0;
    let success = false;
    
    do {
        try {
            uploadFunction();
            success = true;
            console.log('数据上传成功');
        } catch (error) {
            retryCount++;
            console.log(`上传失败，第${retryCount}次重试...`);
            
            if (retryCount >= maxRetries) {
                console.error('达到最大重试次数，上传失败');
                throw new Error('数据上传失败');
            }
        }
    } while (!success && retryCount < maxRetries);
    
    return success;
}
```

这些JavaScript基础语法和数据类型的知识构成了智慧水利平台开发的编程基础，掌握它们对于后续学习高级特性和框架技术至关重要。
