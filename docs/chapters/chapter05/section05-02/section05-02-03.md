# 5.2.3 Python基础与应用

## Python核心特性

1. **简洁易读**：清晰的语法，减少样板代码
2. **动态类型**：灵活的类型系统
3. **解释执行**：开发迭代快速
4. **多范式**：支持面向对象、函数式、命令式编程
5. **丰富的库生态**：科学计算、数据分析、机器学习等领域的库
6. **胶水语言**：易于集成其他语言和系统

## Python开发环境配置

1. **Python安装**
   - 下载Python（推荐3.8+版本）
   - Anaconda/Miniconda环境管理

2. **虚拟环境**
   ```bash
   # 创建虚拟环境
   python -m venv water_env
   # 激活环境
   source water_env/bin/activate  # Linux/Mac
   water_env\Scripts\activate     # Windows
   ```

3. **包管理**
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   ```

4. **开发工具**
   - PyCharm
   - Visual Studio Code
   - Jupyter Notebook

## Python核心库

1. **数据分析与科学计算**
   - NumPy：高效数值计算
   - Pandas：数据分析和处理
   - Matplotlib/Plotly：数据可视化
   - SciPy：科学计算

2. **Web开发框架**
   - Django：全功能Web框架
   - Flask：轻量级Web框架
   - FastAPI：高性能API框架

3. **机器学习与AI**
   - Scikit-learn：机器学习库
   - TensorFlow/PyTorch：深度学习框架

## Python基础语法

### 数据类型和变量

```python
# 基本数据类型
station_id = "ST001"          # 字符串
water_level = 10.5            # 浮点数
warning_status = True         # 布尔值
measurements = None           # 空值

# 复合数据类型
stations = ["ST001", "ST002", "ST003"]  # 列表
station_info = {              # 字典
    "id": "ST001",
    "name": "金沙江水文站",
    "location": (104.0668, 30.5728),  # 元组
    "parameters": {"water_level", "flow_rate"}  # 集合
}
```

### 函数和类

```python
# 函数定义
def calculate_flow_rate(water_level, river_width, coefficient=0.8):
    """根据水位计算流量"""
    area = water_level * river_width
    return area * coefficient

# 类定义
class WaterMonitoringStation:
    """水文监测站类"""
    
    def __init__(self, station_id, name, location):
        self.station_id = station_id
        self.name = name
        self.location = location
        self.data = []
    
    def add_measurement(self, timestamp, water_level, flow_rate=None):
        """添加监测数据"""
        measurement = {
            "timestamp": timestamp,
            "water_level": water_level,
            "flow_rate": flow_rate or self.calculate_flow_rate(water_level)
        }
        self.data.append(measurement)
        return measurement
    
    def calculate_flow_rate(self, water_level):
        """计算流量（示例方法）"""
        # 实际应用中应使用更复杂的水文模型
        return water_level * 1.5
    
    def get_latest_measurement(self):
        """获取最新监测数据"""
        return self.data[-1] if self.data else None
```

### 数据分析与处理

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 生成示例数据
dates = pd.date_range(start="2023-01-01", periods=30, freq="D")
water_levels = np.random.normal(5, 1, size=30)  # 均值5，标准差1的正态分布

# 创建DataFrame
df = pd.DataFrame({
    "date": dates,
    "water_level": water_levels,
    "station": "ST001"
})

# 数据处理
daily_mean = df.groupby(df['date'].dt.date)['water_level'].mean()
rolling_avg = df['water_level'].rolling(window=7).mean()  # 7天滚动平均

# 数据可视化
plt.figure(figsize=(10, 6))
plt.plot(df['date'], df['water_level'], 'b-', label='水位')
plt.plot(df['date'], rolling_avg, 'r-', label='7天滚动平均')
plt.axhline(y=6.5, color='g', linestyle='--', label='警戒水位')
plt.title('水位监测数据分析')
plt.xlabel('日期')
plt.ylabel('水位 (m)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('water_level_analysis.png')
```

## Python在智慧水利中的典型应用

### 水文数据分析

```python
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# 读取水文数据
def analyze_water_level(station_id, start_date, end_date):
    # 从数据库或API获取数据
    df = pd.read_csv(f'data/{station_id}_water_level.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # 筛选时间范围
    mask = (df['datetime'] >= start_date) & (df['datetime'] <= end_date)
    period_data = df.loc[mask]
    
    # 统计分析
    stats_result = {
        'mean': period_data['water_level'].mean(),
        'max': period_data['water_level'].max(),
        'min': period_data['water_level'].min(),
        'std': period_data['water_level'].std()
    }
    
    # 趋势分析
    x = range(len(period_data))
    y = period_data['water_level'].values
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # 可视化
    plt.figure(figsize=(12, 6))
    plt.plot(period_data['datetime'], period_data['water_level'])
    plt.title(f'水位变化趋势 - 站点{station_id}')
    plt.xlabel('日期')
    plt.ylabel('水位(m)')
    plt.grid(True)
    plt.savefig(f'reports/{station_id}_water_level_trend.png')
    
    return stats_result, slope
```

### 洪水预报模型

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

class FloodPredictionModel:
    """洪水预报模型类"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
    
    def prepare_features(self, df):
        """准备特征数据"""
        # 添加时间特征
        df['hour'] = df['datetime'].dt.hour
        df['day'] = df['datetime'].dt.day
        df['month'] = df['datetime'].dt.month
        
        # 添加滞后特征
        for lag in [1, 3, 6, 12, 24]:
            df[f'water_level_lag_{lag}h'] = df['water_level'].shift(lag)
            df[f'rainfall_lag_{lag}h'] = df['rainfall'].shift(lag)
        
        # 添加累积降雨特征
        for window in [6, 12, 24, 48, 72]:
            df[f'rainfall_sum_{window}h'] = df['rainfall'].rolling(window=window).sum()
        
        return df.dropna()  # 删除缺失值
    
    def train(self, historical_data):
        """训练模型"""
        # 准备数据
        df = self.prepare_features(historical_data)
        
        # 定义特征和目标变量
        features = [col for col in df.columns if col not in ['datetime', 'water_level', 'station_id']]
        X = df[features]
        y = df['water_level']
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 训练模型
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # 评估模型
        y_pred = self.model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print(f"模型训练完成 - RMSE: {rmse:.2f}, R²: {r2:.2f}")
        return rmse, r2
    
    def predict(self, current_data, forecast_hours=24):
        """预测未来水位"""
        if not self.is_trained:
            raise ValueError("模型尚未训练")
        
        # 准备当前数据
        df = self.prepare_features(current_data)
        latest_data = df.iloc[-1:]
        
        # 预测结果存储
        predictions = []
        current_time = latest_data['datetime'].iloc[0]
        
        # 逐小时预测
        for hour in range(1, forecast_hours + 1):
            # 复制最新数据
            next_hour = latest_data.copy()
            next_hour['datetime'] = current_time + pd.Timedelta(hours=hour)
            next_hour['hour'] = next_hour['datetime'].dt.hour
            next_hour['day'] = next_hour['datetime'].dt.day
            next_hour['month'] = next_hour['datetime'].dt.month
            
            # 预测下一小时水位
            features = [col for col in next_hour.columns if col not in ['datetime', 'water_level', 'station_id']]
            prediction = self.model.predict(next_hour[features])[0]
            
            # 存储预测结果
            predictions.append({
                'datetime': next_hour['datetime'].iloc[0],
                'water_level': prediction
            })
            
            # 更新最新数据，用于下一小时预测
            latest_data['water_level'] = prediction
            # 更新滞后特征
            for lag in [1, 3, 6, 12, 24]:
                if hour >= lag:
                    prev_idx = hour - lag
                    latest_data[f'water_level_lag_{lag}h'] = predictions[prev_idx]['water_level']
        
        return pd.DataFrame(predictions)
```

## 习题与思考

1. 使用Python分析一个水文站点的历史数据，实现基本的数据清洗、统计分析和可视化，并解释您的代码。
2. 比较Python的Django和Flask框架在水利信息系统后端开发中的优缺点，并给出适合的应用场景。
3. 设计一个基于Python的洪水预警模型，考虑哪些特征和算法最适合预测特定河流的洪水风险？ 