## 5.1.6 最新技术发展趋势与智慧水利应用

### 5.1.6.1 云原生技术在智慧水利中的应用

**容器化技术的普及**

随着Docker和Kubernetes技术的成熟，智慧水利平台正在向容器化部署方向发展。容器化技术为水利应用带来了以下优势：

```yaml
# 智慧水利服务容器化配置示例
apiVersion: apps/v1
kind: Deployment
metadata:
  name: water-monitoring-service
  namespace: smart-water
spec:
  replicas: 3
  selector:
    matchLabels:
      app: water-monitoring
  template:
    metadata:
      labels:
        app: water-monitoring
    spec:
      containers:
      - name: monitoring-api
        image: smart-water/monitoring-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: REDIS_HOST
          value: "redis-service"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: water-monitoring-service
spec:
  selector:
    app: water-monitoring
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

**服务网格技术**

Service Mesh技术为智慧水利平台的微服务架构提供了更好的服务间通信管理：

```java
/**
 * 基于Istio的智慧水利服务通信配置
 */
@RestController
@RequestMapping("/api/water-data")
public class WaterDataController {
    
    @Autowired
    private HydrologyService hydrologyService;
    
    @Autowired
    private ReservoirService reservoirService;
    
    /**
     * 获取流域综合水情数据
     * 通过服务网格实现服务发现和负载均衡
     */
    @GetMapping("/basin/{basinId}/comprehensive")
    @TracingEnabled // 分布式链路追踪
    @RateLimited(value = 100, window = "1m") // 限流控制
    public ResponseEntity<BasinWaterData> getBasinComprehensiveData(
            @PathVariable String basinId,
            @RequestParam(defaultValue = "real-time") String dataType) {
        
        try {
            // 并行调用多个微服务
            CompletableFuture<List<HydrologyData>> hydrologyFuture = 
                hydrologyService.getBasinHydrologyDataAsync(basinId);
            
            CompletableFuture<List<ReservoirData>> reservoirFuture = 
                reservoirService.getBasinReservoirDataAsync(basinId);
            
            CompletableFuture<WeatherData> weatherFuture = 
                weatherService.getBasinWeatherDataAsync(basinId);
            
            // 等待所有服务响应
            CompletableFuture<Void> allFutures = CompletableFuture.allOf(
                hydrologyFuture, reservoirFuture, weatherFuture
            );
            
            BasinWaterData comprehensiveData = allFutures.thenApply(v -> {
                List<HydrologyData> hydrologyData = hydrologyFuture.join();
                List<ReservoirData> reservoirData = reservoirFuture.join();
                WeatherData weatherData = weatherFuture.join();
                
                return BasinWaterData.builder()
                    .basinId(basinId)
                    .hydrologyData(hydrologyData)
                    .reservoirData(reservoirData)
                    .weatherData(weatherData)
                    .timestamp(Instant.now())
                    .build();
            }).get(5, TimeUnit.SECONDS); // 设置超时时间
            
            return ResponseEntity.ok(comprehensiveData);
            
        } catch (TimeoutException e) {
            // 超时降级处理
            return ResponseEntity.status(HttpStatus.PARTIAL_CONTENT)
                .body(getBasinDataFromCache(basinId));
        } catch (Exception e) {
            log.error("获取流域数据失败: basinId={}", basinId, e);
            throw new WaterDataServiceException("服务暂时不可用", e);
        }
    }
}
```

### 5.1.6.2 边缘计算在水利监测中的应用

**边缘设备数据处理**

随着物联网设备的普及，边缘计算成为智慧水利的重要技术趋势：

```python
"""
水利监测站边缘计算节点
基于边缘计算框架实现本地数据处理和智能分析
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
from edge_computing_framework import EdgeNode, SensorManager, AlertManager

class WaterMonitoringEdgeNode(EdgeNode):
    """
    水利监测边缘计算节点
    在监测站点本地实现数据预处理、异常检测和紧急响应
    """
    
    def __init__(self, node_config: Dict):
        super().__init__(node_config)
        self.sensor_manager = SensorManager()
        self.alert_manager = AlertManager()
        self.data_buffer = []
        self.model_cache = {}
        self.emergency_thresholds = node_config.get('emergency_thresholds', {})
        
        # 加载预训练的异常检测模型
        self.load_anomaly_detection_models()
        
    async def initialize(self):
        """初始化边缘节点"""
        try:
            # 连接传感器设备
            await self.sensor_manager.connect_sensors([
                {'type': 'water_level', 'address': '192.168.1.100'},
                {'type': 'flow_rate', 'address': '192.168.1.101'},
                {'type': 'water_quality', 'address': '192.168.1.102'},
                {'type': 'rainfall', 'address': '192.168.1.103'}
            ])
            
            # 启动数据采集任务
            asyncio.create_task(self.continuous_data_collection())
            
            # 启动实时分析任务
            asyncio.create_task(self.real_time_analysis())
            
            # 启动云端同步任务
            asyncio.create_task(self.cloud_synchronization())
            
            logging.info("水利监测边缘节点初始化完成")
            
        except Exception as e:
            logging.error(f"边缘节点初始化失败: {e}")
            raise
    
    async def continuous_data_collection(self):
        """持续数据采集"""
        while True:
            try:
                # 从所有传感器采集数据
                sensor_data = await self.sensor_manager.collect_all_data()
                
                # 数据预处理
                processed_data = self.preprocess_sensor_data(sensor_data)
                
                # 添加到本地缓冲区
                self.data_buffer.append({
                    'timestamp': datetime.now().isoformat(),
                    'data': processed_data,
                    'node_id': self.node_id
                })
                
                # 维护缓冲区大小
                if len(self.data_buffer) > 1000:
                    self.data_buffer = self.data_buffer[-1000:]
                
                # 立即检查紧急情况
                await self.check_emergency_conditions(processed_data)
                
            except Exception as e:
                logging.error(f"数据采集错误: {e}")
                
            await asyncio.sleep(10)  # 每10秒采集一次
    
    def preprocess_sensor_data(self, raw_data: Dict) -> Dict:
        """传感器数据预处理"""
        processed = {}
        
        for sensor_type, values in raw_data.items():
            if sensor_type == 'water_level':
                # 水位数据校准和滤波
                processed[sensor_type] = self.calibrate_water_level(values)
            elif sensor_type == 'flow_rate':
                # 流量数据平滑处理
                processed[sensor_type] = self.smooth_flow_data(values)
            elif sensor_type == 'water_quality':
                # 水质数据标准化
                processed[sensor_type] = self.normalize_water_quality(values)
            elif sensor_type == 'rainfall':
                # 降雨数据累积计算
                processed[sensor_type] = self.accumulate_rainfall(values)
        
        return processed
    
    async def real_time_analysis(self):
        """实时数据分析"""
        while True:
            try:
                if len(self.data_buffer) >= 6:  # 至少1分钟的数据
                    recent_data = self.data_buffer[-6:]
                    
                    # 趋势分析
                    trends = self.analyze_trends(recent_data)
                    
                    # 异常检测
                    anomalies = await self.detect_anomalies(recent_data)
                    
                    # 预测分析
                    predictions = self.generate_predictions(recent_data)
                    
                    # 生成分析报告
                    analysis_result = {
                        'timestamp': datetime.now().isoformat(),
                        'trends': trends,
                        'anomalies': anomalies,
                        'predictions': predictions,
                        'node_id': self.node_id
                    }
                    
                    # 如果发现异常，触发告警
                    if anomalies:
                        await self.handle_anomalies(anomalies)
                    
                    # 将分析结果添加到上传队列
                    await self.queue_for_cloud_sync(analysis_result)
                    
            except Exception as e:
                logging.error(f"实时分析错误: {e}")
                
            await asyncio.sleep(30)  # 每30秒分析一次
    
    async def detect_anomalies(self, data_window: List[Dict]) -> List[Dict]:
        """异常检测"""
        anomalies = []
        
        # 提取时间序列数据
        water_levels = [d['data'].get('water_level', 0) for d in data_window]
        flow_rates = [d['data'].get('flow_rate', 0) for d in data_window]
        
        # 使用预训练模型进行异常检测
        if 'water_level_anomaly' in self.model_cache:
            wl_anomaly_score = self.model_cache['water_level_anomaly'].predict([water_levels])
            if wl_anomaly_score > 0.8:  # 异常阈值
                anomalies.append({
                    'type': 'water_level_anomaly',
                    'score': float(wl_anomaly_score),
                    'current_value': water_levels[-1],
                    'severity': 'high' if wl_anomaly_score > 0.9 else 'medium'
                })
        
        # 统计方法异常检测
        if len(water_levels) >= 6:
            mean_wl = np.mean(water_levels[:-1])
            std_wl = np.std(water_levels[:-1])
            current_wl = water_levels[-1]
            
            # 3-sigma规则
            if abs(current_wl - mean_wl) > 3 * std_wl:
                anomalies.append({
                    'type': 'statistical_anomaly',
                    'parameter': 'water_level',
                    'z_score': (current_wl - mean_wl) / std_wl,
                    'current_value': current_wl,
                    'severity': 'medium'
                })
        
        return anomalies
    
    async def check_emergency_conditions(self, data: Dict):
        """检查紧急情况"""
        emergency_alerts = []
        
        # 检查水位紧急阈值
        water_level = data.get('water_level', 0)
        if water_level > self.emergency_thresholds.get('critical_water_level', 999):
            emergency_alerts.append({
                'type': 'critical_water_level',
                'value': water_level,
                'threshold': self.emergency_thresholds['critical_water_level'],
                'action_required': True
            })
        
        # 检查流量异常
        flow_rate = data.get('flow_rate', 0)
        if flow_rate > self.emergency_thresholds.get('max_flow_rate', 9999):
            emergency_alerts.append({
                'type': 'excessive_flow',
                'value': flow_rate,
                'threshold': self.emergency_thresholds['max_flow_rate'],
                'action_required': True
            })
        
        # 如果有紧急情况，立即处理
        if emergency_alerts:
            await self.handle_emergency_alerts(emergency_alerts)
    
    async def handle_emergency_alerts(self, alerts: List[Dict]):
        """处理紧急告警"""
        for alert in alerts:
            # 本地告警处理
            await self.alert_manager.trigger_local_alert(alert)
            
            # 立即尝试向云端发送紧急告警
            try:
                await self.send_emergency_to_cloud(alert)
            except Exception as e:
                logging.error(f"发送紧急告警到云端失败: {e}")
                # 将告警存储到本地，等待网络恢复后重传
                self.store_failed_alert(alert)
            
            # 如果需要，触发本地自动响应
            if alert.get('action_required'):
                await self.execute_emergency_response(alert)
    
    async def cloud_synchronization(self):
        """云端数据同步"""
        while True:
            try:
                # 检查网络连接
                if await self.check_cloud_connectivity():
                    # 上传缓存的数据
                    await self.upload_buffered_data()
                    
                    # 下载最新配置和模型
                    await self.download_updates()
                    
                else:
                    logging.warning("云端连接不可用，继续本地运行")
                    
            except Exception as e:
                logging.error(f"云端同步错误: {e}")
                
            await asyncio.sleep(300)  # 每5分钟同步一次
```

### 5.1.6.3 人工智能增强的后端服务

**智能水文预测服务**

结合深度学习和传统水文模型，提供更准确的预测服务：

```python
"""
基于AI的智能水文预测服务
集成深度学习模型和物理模型，提供高精度水文预测
"""

import torch
import torch.nn as nn
from transformers import TimeSeriesTransformer
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import asyncio
import logging

class IntelligentHydrologicalService:
    """
    智能水文预测服务
    整合多种AI模型和物理模型，提供综合预测能力
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.models = {}
        self.ensemble_weights = {}
        self.load_prediction_models()
        
    def load_prediction_models(self):
        """加载预测模型"""
        try:
            # 加载LSTM流量预测模型
            self.models['lstm_flow'] = self.load_lstm_model('flow_prediction')
            
            # 加载Transformer降雨径流模型
            self.models['transformer_runoff'] = self.load_transformer_model('runoff_prediction')
            
            # 加载物理水文模型
            self.models['physical_model'] = self.load_physical_model('xaj_model')
            
            # 加载集成学习模型
            self.models['ensemble'] = self.load_ensemble_model('prediction_ensemble')
            
            logging.info("所有预测模型加载完成")
            
        except Exception as e:
            logging.error(f"模型加载失败: {e}")
            raise
    
    async def predict_streamflow(self, 
                                station_id: str,
                                forecast_hours: int = 72,
                                input_data: Optional[Dict] = None) -> Dict:
        """
        河流流量预测
        使用多模型集成方法提供高精度预测
        """
        try:
            # 获取历史数据
            if input_data is None:
                input_data = await self.get_station_historical_data(station_id, days=30)
            
            # 数据预处理
            processed_data = self.preprocess_for_prediction(input_data)
            
            # 多模型预测
            predictions = {}
            
            # LSTM模型预测
            lstm_pred = await self.run_lstm_prediction(processed_data, forecast_hours)
            predictions['lstm'] = lstm_pred
            
            # Transformer模型预测
            transformer_pred = await self.run_transformer_prediction(processed_data, forecast_hours)
            predictions['transformer'] = transformer_pred
            
            # 物理模型预测
            physical_pred = await self.run_physical_model_prediction(processed_data, forecast_hours)
            predictions['physical'] = physical_pred
            
            # 集成预测
            ensemble_pred = self.ensemble_predictions(predictions)
            
            # 计算预测不确定性
            uncertainty = self.calculate_prediction_uncertainty(predictions)
            
            # 生成预测报告
            prediction_result = {
                'station_id': station_id,
                'forecast_time': datetime.now().isoformat(),
                'forecast_horizon_hours': forecast_hours,
                'predictions': {
                    'ensemble': ensemble_pred,
                    'individual_models': predictions,
                    'uncertainty_bounds': uncertainty
                },
                'confidence_level': self.calculate_confidence_level(predictions),
                'model_performance': await self.get_recent_model_performance(station_id)
            }
            
            return prediction_result
            
        except Exception as e:
            logging.error(f"流量预测失败: station_id={station_id}, error={e}")
            raise
    
    async def run_lstm_prediction(self, data: Dict, forecast_hours: int) -> List[float]:
        """运行LSTM模型预测"""
        model = self.models['lstm_flow']
        
        # 准备输入序列
        input_sequence = self.prepare_lstm_input(data)
        
        # 模型推理
        with torch.no_grad():
            model.eval()
            predictions = []
            
            current_input = torch.tensor(input_sequence, dtype=torch.float32).unsqueeze(0)
            
            for hour in range(forecast_hours):
                # 单步预测
                pred = model(current_input)
                predictions.append(float(pred.item()))
                
                # 更新输入序列（滑动窗口）
                current_input = torch.cat([
                    current_input[:, 1:, :],
                    pred.unsqueeze(1)
                ], dim=1)
        
        return predictions
    
    async def run_transformer_prediction(self, data: Dict, forecast_hours: int) -> List[float]:
        """运行Transformer模型预测"""
        model = self.models['transformer_runoff']
        
        # 准备多变量时间序列输入
        input_features = self.prepare_transformer_input(data)
        
        # 使用Transformer进行序列到序列预测
        with torch.no_grad():
            model.eval()
            # 一次性预测整个序列
            predictions = model.generate(
                input_features,
                max_length=forecast_hours,
                temperature=0.8,
                num_return_sequences=1
            )
        
        return predictions[0].tolist()
    
    async def run_physical_model_prediction(self, data: Dict, forecast_hours: int) -> List[float]:
        """运行物理水文模型预测"""
        model = self.models['physical_model']
        
        # 准备物理模型参数
        model_params = {
            'rainfall': data['rainfall_forecast'],
            'evaporation': data['evaporation_forecast'],
            'initial_conditions': data['current_state'],
            'basin_characteristics': data['basin_properties']
        }
        
        # 运行新安江模型
        predictions = await model.simulate(
            parameters=model_params,
            time_steps=forecast_hours
        )
        
        return predictions['streamflow']
    
    def ensemble_predictions(self, predictions: Dict) -> List[float]:
        """集成多个模型的预测结果"""
        # 获取预测长度
        pred_length = len(list(predictions.values())[0])
        
        ensemble_result = []
        
        for i in range(pred_length):
            # 加权平均集成
            weighted_sum = 0
            total_weight = 0
            
            for model_name, pred_values in predictions.items():
                weight = self.ensemble_weights.get(model_name, 1.0)
                weighted_sum += pred_values[i] * weight
                total_weight += weight
            
            ensemble_value = weighted_sum / total_weight
            ensemble_result.append(ensemble_value)
        
        return ensemble_result
    
    def calculate_prediction_uncertainty(self, predictions: Dict) -> Dict:
        """计算预测不确定性"""
        pred_length = len(list(predictions.values())[0])
        
        upper_bounds = []
        lower_bounds = []
        
        for i in range(pred_length):
            values = [pred[i] for pred in predictions.values()]
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            # 95%置信区间
            upper_bounds.append(mean_val + 1.96 * std_val)
            lower_bounds.append(mean_val - 1.96 * std_val)
        
        return {
            'upper_95': upper_bounds,
            'lower_95': lower_bounds,
            'standard_deviation': [np.std([pred[i] for pred in predictions.values()]) 
                                 for i in range(pred_length)]
        }
    
    async def adaptive_model_update(self, station_id: str, observed_data: Dict):
        """自适应模型更新"""
        try:
            # 获取最近预测结果
            recent_predictions = await self.get_recent_predictions(station_id, days=7)
            
            # 计算模型性能
            model_performance = {}
            for model_name in self.models.keys():
                if model_name in recent_predictions:
                    performance = self.evaluate_model_performance(
                        recent_predictions[model_name],
                        observed_data
                    )
                    model_performance[model_name] = performance
            
            # 更新集成权重
            self.update_ensemble_weights(model_performance)
            
            # 如果性能下降，触发模型重训练
            for model_name, performance in model_performance.items():
                if performance['rmse'] > self.config['performance_thresholds'][model_name]:
                    await self.schedule_model_retraining(model_name, station_id)
            
            logging.info(f"模型自适应更新完成: station_id={station_id}")
            
        except Exception as e:
            logging.error(f"自适应模型更新失败: {e}")
```

### 5.1.6.4 区块链技术在水利数据管理中的应用

**水权交易智能合约**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * 智慧水利水权交易智能合约
 * 实现水权的数字化确权、交易和管理
 */
contract WaterRightsTrading {
    
    struct WaterRight {
        uint256 id;
        address owner;
        string location; // 地理位置信息
        uint256 allocatedVolume; // 分配水量 (立方米)
        uint256 usedVolume; // 已使用水量
        uint256 validUntil; // 有效期至
        bool isActive;
        string waterSource; // 水源信息
        uint256 priority; // 用水优先级
    }
    
    struct TradeOffer {
        uint256 id;
        uint256 waterRightId;
        address seller;
        uint256 volume; // 交易水量
        uint256 price; // 价格 (wei per cubic meter)
        uint256 validUntil; // 报价有效期
        bool isActive;
        TradeType tradeType;
    }
    
    enum TradeType { Permanent, Temporary, Lease }
    
    mapping(uint256 => WaterRight) public waterRights;
    mapping(uint256 => TradeOffer) public tradeOffers;
    mapping(address => uint256[]) public userWaterRights;
    
    uint256 public nextWaterRightId = 1;
    uint256 public nextTradeOfferId = 1;
    
    address public regulator; // 监管机构地址
    
    event WaterRightIssued(uint256 indexed id, address indexed owner, uint256 volume);
    event TradeOfferCreated(uint256 indexed id, uint256 indexed waterRightId, uint256 volume, uint256 price);
    event TradeExecuted(uint256 indexed offerId, address indexed buyer, address indexed seller, uint256 volume);
    event WaterUsageRecorded(uint256 indexed waterRightId, uint256 volume, uint256 timestamp);
    
    modifier onlyRegulator() {
        require(msg.sender == regulator, "Only regulator can perform this action");
        _;
    }
    
    modifier onlyOwner(uint256 waterRightId) {
        require(waterRights[waterRightId].owner == msg.sender, "Not the owner of this water right");
        _;
    }
    
    constructor() {
        regulator = msg.sender;
    }
    
    /**
     * 发放水权证
     */
    function issueWaterRight(
        address owner,
        string memory location,
        uint256 allocatedVolume,
        uint256 validUntil,
        string memory waterSource,
        uint256 priority
    ) external onlyRegulator returns (uint256) {
        
        uint256 waterRightId = nextWaterRightId++;
        
        waterRights[waterRightId] = WaterRight({
            id: waterRightId,
            owner: owner,
            location: location,
            allocatedVolume: allocatedVolume,
            usedVolume: 0,
            validUntil: validUntil,
            isActive: true,
            waterSource: waterSource,
            priority: priority
        });
        
        userWaterRights[owner].push(waterRightId);
        
        emit WaterRightIssued(waterRightId, owner, allocatedVolume);
        
        return waterRightId;
    }
    
    /**
     * 创建水权交易报价
     */
    function createTradeOffer(
        uint256 waterRightId,
        uint256 volume,
        uint256 pricePerCubicMeter,
        uint256 validUntil,
        TradeType tradeType
    ) external onlyOwner(waterRightId) returns (uint256) {
        
        WaterRight storage waterRight = waterRights[waterRightId];
        require(waterRight.isActive, "Water right is not active");
        require(waterRight.allocatedVolume - waterRight.usedVolume >= volume, "Insufficient available volume");
        require(block.timestamp < waterRight.validUntil, "Water right has expired");
        
        uint256 offerId = nextTradeOfferId++;
        
        tradeOffers[offerId] = TradeOffer({
            id: offerId,
            waterRightId: waterRightId,
            seller: msg.sender,
            volume: volume,
            price: pricePerCubicMeter,
            validUntil: validUntil,
            isActive: true,
            tradeType: tradeType
        });
        
        emit TradeOfferCreated(offerId, waterRightId, volume, pricePerCubicMeter);
        
        return offerId;
    }
    
    /**
     * 执行水权交易
     */
    function executeTrade(uint256 offerId) external payable {
        TradeOffer storage offer = tradeOffers[offerId];
        require(offer.isActive, "Trade offer is not active");
        require(block.timestamp <= offer.validUntil, "Trade offer has expired");
        require(msg.sender != offer.seller, "Cannot buy your own offer");
        
        uint256 totalPrice = offer.volume * offer.price;
        require(msg.value >= totalPrice, "Insufficient payment");
        
        WaterRight storage waterRight = waterRights[offer.waterRightId];
        require(waterRight.isActive, "Water right is not active");
        
        // 执行交易
        if (offer.tradeType == TradeType.Permanent) {
            // 永久转让
            _transferWaterRight(offer.waterRightId, offer.seller, msg.sender, offer.volume);
        } else {
            // 临时交易或租赁
            _createTemporaryRight(offer.waterRightId, msg.sender, offer.volume, offer.tradeType);
        }
        
        // 转账给卖方
        payable(offer.seller).transfer(totalPrice);
        
        // 退还多余资金
        if (msg.value > totalPrice) {
            payable(msg.sender).transfer(msg.value - totalPrice);
        }
        
        // 取消交易报价
        offer.isActive = false;
        
        emit TradeExecuted(offerId, msg.sender, offer.seller, offer.volume);
    }
    
    /**
     * 记录用水量
     */
    function recordWaterUsage(
        uint256 waterRightId,
        uint256 volume,
        bytes32 measurementHash // 用水量测量数据的哈希
    ) external {
        // 只有授权的监测设备或监管机构可以记录用水量
        require(
            msg.sender == regulator || isAuthorizedDevice(msg.sender),
            "Not authorized to record usage"
        );
        
        WaterRight storage waterRight = waterRights[waterRightId];
        require(waterRight.isActive, "Water right is not active");
        require(waterRight.usedVolume + volume <= waterRight.allocatedVolume, "Exceeds allocated volume");
        
        waterRight.usedVolume += volume;
        
        emit WaterUsageRecorded(waterRightId, volume, block.timestamp);
        
        // 如果用水量接近限额，发出警告
        if (waterRight.usedVolume >= waterRight.allocatedVolume * 90 / 100) {
            emit WaterUsageWarning(waterRightId, waterRight.usedVolume, waterRight.allocatedVolume);
        }
    }
    
    /**
     * 获取用户的水权信息
     */
    function getUserWaterRights(address user) external view returns (uint256[] memory) {
        return userWaterRights[user];
    }
    
    /**
     * 获取水权详细信息
     */
    function getWaterRightDetails(uint256 waterRightId) external view returns (WaterRight memory) {
        return waterRights[waterRightId];
    }
    
    // 内部函数
    function _transferWaterRight(
        uint256 waterRightId,
        address from,
        address to,
        uint256 volume
    ) internal {
        // 实现水权转让逻辑
        WaterRight storage waterRight = waterRights[waterRightId];
        
        if (volume == waterRight.allocatedVolume) {
            // 完全转让
            waterRight.owner = to;
            _removeFromUserRights(from, waterRightId);
            userWaterRights[to].push(waterRightId);
        } else {
            // 部分转让，需要拆分水权
            _splitWaterRight(waterRightId, from, to, volume);
        }
    }
    
    function _createTemporaryRight(
        uint256 originalRightId,
        address temporaryOwner,
        uint256 volume,
        TradeType tradeType
    ) internal {
        // 创建临时水权
        uint256 tempRightId = nextWaterRightId++;
        WaterRight storage originalRight = waterRights[originalRightId];
        
        uint256 validUntil = tradeType == TradeType.Lease ? 
            block.timestamp + 365 days : originalRight.validUntil;
        
        waterRights[tempRightId] = WaterRight({
            id: tempRightId,
            owner: temporaryOwner,
            location: originalRight.location,
            allocatedVolume: volume,
            usedVolume: 0,
            validUntil: validUntil,
            isActive: true,
            waterSource: originalRight.waterSource,
            priority: originalRight.priority
        });
        
        userWaterRights[temporaryOwner].push(tempRightId);
    }
    
    event WaterUsageWarning(uint256 indexed waterRightId, uint256 usedVolume, uint256 allocatedVolume);
}
```

本节展示了智慧水利后端开发的最新技术趋势，包括云原生技术、边缘计算、人工智能和区块链等前沿技术的应用。这些技术的融合将为智慧水利平台带来更强的处理能力、更高的可靠性和更好的用户体验。
