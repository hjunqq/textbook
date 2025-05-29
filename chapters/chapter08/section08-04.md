# 第四节 应急响应与决策支持系统

## 引言

应急响应与决策支持系统是智慧水利平台在关键时刻发挥作用的核心模块。该系统需要在洪水、干旱、工程事故等紧急情况下，快速分析态势、预测发展趋势、制定应对方案，并协调各方资源进行有效响应。

本节将详细介绍应急响应与决策支持系统的设计理念、核心功能和技术实现，为构建高效的水利应急管理体系提供技术支撑。

## 8.4.1 应急事件识别与预警

### 多级预警体系

```javascript
class EmergencyWarningSystem {
    constructor(config) {
        this.config = config;
        this.warningLevels = {
            'blue': { level: 1, name: '一般', threshold: 0.3 },
            'yellow': { level: 2, name: '较重', threshold: 0.6 },
            'orange': { level: 3, name: '严重', threshold: 0.8 },
            'red': { level: 4, name: '特别严重', threshold: 0.95 }
        };
        
        this.indicators = new Map();
        this.activeWarnings = new Map();
        this.subscriptions = new Map();
        
        this.initializeIndicators();
    }
    
    initializeIndicators() {
        // 水位预警指标
        this.indicators.set('water_level', {
            name: '水位预警',
            calculate: this.calculateWaterLevelRisk.bind(this),
            thresholds: {
                warning: 185.0,
                alert: 188.0,
                danger: 190.0,
                emergency: 192.0
            }
        });
        
        // 降雨预警指标
        this.indicators.set('rainfall', {
            name: '降雨预警',
            calculate: this.calculateRainfallRisk.bind(this),
            thresholds: {
                warning: 50,    // 24小时50mm
                alert: 100,     // 24小时100mm
                danger: 200,    // 24小时200mm
                emergency: 300  // 24小时300mm
            }
        });
        
        // 工程安全预警指标
        this.indicators.set('dam_safety', {
            name: '大坝安全预警',
            calculate: this.calculateDamSafetyRisk.bind(this),
            parameters: ['seepage', 'displacement', 'stress', 'vibration']
        });
    }
    
    async evaluateRiskLevel(stationData, forecastData) {
        const riskScores = new Map();
        
        // 计算各指标风险分数
        for (const [indicatorName, indicator] of this.indicators) {
            const score = await indicator.calculate(stationData, forecastData);
            riskScores.set(indicatorName, score);
        }
        
        // 综合风险评估
        const overallRisk = this.calculateOverallRisk(riskScores);
        
        // 确定预警等级
        const warningLevel = this.determineWarningLevel(overallRisk);
        
        return {
            overallRisk,
            warningLevel,
            indicatorScores: Object.fromEntries(riskScores),
            timestamp: new Date().toISOString()
        };
    }
    
    calculateWaterLevelRisk(stationData, forecastData) {
        const currentLevel = stationData.water_level;
        const thresholds = this.indicators.get('water_level').thresholds;
        
        // 当前水位风险
        let currentRisk = 0;
        if (currentLevel >= thresholds.emergency) currentRisk = 1.0;
        else if (currentLevel >= thresholds.danger) currentRisk = 0.8;
        else if (currentLevel >= thresholds.alert) currentRisk = 0.6;
        else if (currentLevel >= thresholds.warning) currentRisk = 0.3;
        
        // 预测水位风险
        let forecastRisk = 0;
        if (forecastData && forecastData.water_level_forecast) {
            const maxForecastLevel = Math.max(...forecastData.water_level_forecast);
            if (maxForecastLevel >= thresholds.emergency) forecastRisk = 1.0;
            else if (maxForecastLevel >= thresholds.danger) forecastRisk = 0.8;
            else if (maxForecastLevel >= thresholds.alert) forecastRisk = 0.6;
            else if (maxForecastLevel >= thresholds.warning) forecastRisk = 0.3;
        }
        
        // 水位变化趋势风险
        const trendRisk = this.calculateWaterLevelTrend(stationData.recent_data);
        
        return Math.max(currentRisk, forecastRisk, trendRisk);
    }
    
    calculateRainfallRisk(stationData, forecastData) {
        // 24小时累计降雨量
        const rainfall24h = this.calculateAccumulatedRainfall(stationData.recent_data, 24);
        const thresholds = this.indicators.get('rainfall').thresholds;
        
        let risk = 0;
        if (rainfall24h >= thresholds.emergency) risk = 1.0;
        else if (rainfall24h >= thresholds.danger) risk = 0.8;
        else if (rainfall24h >= thresholds.alert) risk = 0.6;
        else if (rainfall24h >= thresholds.warning) risk = 0.3;
        
        // 考虑预报降雨
        if (forecastData && forecastData.rainfall_forecast) {
            const forecastTotal = forecastData.rainfall_forecast.reduce((sum, val) => sum + val, 0);
            const combinedRainfall = rainfall24h + forecastTotal;
            
            let forecastRisk = 0;
            if (combinedRainfall >= thresholds.emergency) forecastRisk = 1.0;
            else if (combinedRainfall >= thresholds.danger) forecastRisk = 0.8;
            else if (combinedRainfall >= thresholds.alert) forecastRisk = 0.6;
            else if (combinedRainfall >= thresholds.warning) forecastRisk = 0.3;
            
            risk = Math.max(risk, forecastRisk);
        }
        
        return risk;
    }
    
    async triggerWarning(warningData) {
        const warningId = this.generateWarningId();
        const warning = {
            id: warningId,
            level: warningData.warningLevel,
            type: warningData.type || '综合预警',
            stations: warningData.stations,
            risk_score: warningData.overallRisk,
            details: warningData.indicatorScores,
            issued_at: new Date().toISOString(),
            status: 'active'
        };
        
        this.activeWarnings.set(warningId, warning);
        
        // 发送通知
        await this.sendWarningNotifications(warning);
        
        // 自动启动应急预案
        if (warning.level >= 3) {
            await this.activateEmergencyPlan(warning);
        }
        
        return warning;
    }
    
    async sendWarningNotifications(warning) {
        const notifications = [];
        
        // 短信通知
        notifications.push(this.sendSMSAlert(warning));
        
        // 邮件通知
        notifications.push(this.sendEmailAlert(warning));
        
        // 系统消息推送
        notifications.push(this.sendSystemNotification(warning));
        
        // 第三方接口通知
        notifications.push(this.sendExternalAPINotification(warning));
        
        await Promise.all(notifications);
    }
}
```

### 智能事件检测

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

class IntelligentEventDetector:
    """智能事件检测器"""
    
    def __init__(self, config):
        self.config = config
        self.models = {}
        self.scalers = {}
        self.detection_rules = self.load_detection_rules()
        
        # 加载预训练模型
        self.load_trained_models()
    
    def load_trained_models(self):
        """加载预训练的异常检测模型"""
        try:
            # 水位异常检测模型
            self.models['water_level'] = joblib.load('models/water_level_anomaly_model.pkl')
            self.scalers['water_level'] = joblib.load('models/water_level_scaler.pkl')
            
            # 降雨异常检测模型
            self.models['rainfall'] = joblib.load('models/rainfall_anomaly_model.pkl')
            self.scalers['rainfall'] = joblib.load('models/rainfall_scaler.pkl')
            
            # 综合异常检测模型
            self.models['comprehensive'] = joblib.load('models/comprehensive_anomaly_model.pkl')
            self.scalers['comprehensive'] = joblib.load('models/comprehensive_scaler.pkl')
            
        except FileNotFoundError:
            print("预训练模型不存在，将使用实时训练")
            self.train_online_models()
    
    def detect_anomalies(self, data, detection_type='comprehensive'):
        """检测异常事件"""
        
        # 数据预处理
        processed_data = self.preprocess_data(data, detection_type)
        
        if processed_data.empty:
            return []
        
        # 使用多种方法检测异常
        anomalies = []
        
        # 统计方法检测
        statistical_anomalies = self.statistical_anomaly_detection(processed_data)
        anomalies.extend(statistical_anomalies)
        
        # 机器学习方法检测
        if detection_type in self.models:
            ml_anomalies = self.ml_anomaly_detection(processed_data, detection_type)
            anomalies.extend(ml_anomalies)
        
        # 规则引擎检测
        rule_anomalies = self.rule_based_detection(processed_data)
        anomalies.extend(rule_anomalies)
        
        # 去重和排序
        unique_anomalies = self.deduplicate_anomalies(anomalies)
        sorted_anomalies = sorted(unique_anomalies, key=lambda x: x['severity'], reverse=True)
        
        return sorted_anomalies
    
    def statistical_anomaly_detection(self, data):
        """基于统计方法的异常检测"""
        anomalies = []
        
        for column in data.select_dtypes(include=[np.number]).columns:
            if column in ['timestamp']:
                continue
                
            values = data[column].dropna()
            if len(values) < 10:  # 数据量太少
                continue
            
            # Z-score方法
            z_scores = np.abs((values - values.mean()) / values.std())
            z_anomalies = values[z_scores > 3]
            
            for idx, value in z_anomalies.items():
                anomalies.append({
                    'timestamp': data.loc[idx, 'timestamp'],
                    'parameter': column,
                    'value': value,
                    'anomaly_score': z_scores[idx],
                    'method': 'z_score',
                    'severity': min(z_scores[idx] / 3, 1.0),
                    'description': f'{column}数值异常：{value}（Z-score: {z_scores[idx]:.2f}）'
                })
            
            # IQR方法
            q1 = values.quantile(0.25)
            q3 = values.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            iqr_anomalies = values[(values < lower_bound) | (values > upper_bound)]
            
            for idx, value in iqr_anomalies.items():
                severity = max(
                    (lower_bound - value) / iqr if value < lower_bound else 0,
                    (value - upper_bound) / iqr if value > upper_bound else 0
                ) / 1.5
                
                anomalies.append({
                    'timestamp': data.loc[idx, 'timestamp'],
                    'parameter': column,
                    'value': value,
                    'anomaly_score': severity,
                    'method': 'iqr',
                    'severity': min(severity, 1.0),
                    'description': f'{column}数值超出正常范围：{value}（范围：{lower_bound:.2f}-{upper_bound:.2f}）'
                })
        
        return anomalies
    
    def ml_anomaly_detection(self, data, detection_type):
        """基于机器学习的异常检测"""
        anomalies = []
        
        try:
            model = self.models[detection_type]
            scaler = self.scalers[detection_type]
            
            # 特征提取
            features = self.extract_features(data, detection_type)
            if features.empty:
                return anomalies
            
            # 数据标准化
            scaled_features = scaler.transform(features)
            
            # 异常检测
            anomaly_scores = model.decision_function(scaled_features)
            predictions = model.predict(scaled_features)
            
            # 处理检测结果
            for i, (score, prediction) in enumerate(zip(anomaly_scores, predictions)):
                if prediction == -1:  # 异常
                    anomalies.append({
                        'timestamp': data.iloc[i]['timestamp'],
                        'parameter': detection_type,
                        'anomaly_score': abs(score),
                        'method': 'isolation_forest',
                        'severity': min(abs(score), 1.0),
                        'description': f'{detection_type}模式异常（异常分数：{score:.3f}）'
                    })
        
        except Exception as e:
            print(f"机器学习异常检测失败：{e}")
        
        return anomalies
    
    def rule_based_detection(self, data):
        """基于规则的异常检测"""
        anomalies = []
        
        for rule in self.detection_rules:
            try:
                # 评估规则条件
                if self.evaluate_rule_condition(data, rule['condition']):
                    anomalies.append({
                        'timestamp': data.iloc[-1]['timestamp'] if not data.empty else pd.Timestamp.now(),
                        'parameter': rule['parameter'],
                        'rule_id': rule['id'],
                        'method': 'rule_based',
                        'severity': rule['severity'],
                        'description': rule['description'],
                        'action': rule.get('action', 'alert')
                    })
            except Exception as e:
                print(f"规则 {rule['id']} 评估失败：{e}")
        
        return anomalies
    
    def evaluate_rule_condition(self, data, condition):
        """评估规则条件"""
        try:
            # 简单的规则评估器
            # 支持基本的逻辑表达式
            namespace = {
                'data': data,
                'np': np,
                'pd': pd,
                'latest': data.iloc[-1] if not data.empty else None
            }
            
            return eval(condition, {"__builtins__": {}}, namespace)
        except:
            return False
    
    def train_online_models(self):
        """在线训练异常检测模型"""
        print("开始在线训练异常检测模型...")
        
        # 这里应该使用历史数据进行训练
        # 为演示目的，使用模拟数据
        
        for detection_type in ['water_level', 'rainfall', 'comprehensive']:
            # 生成训练数据（实际应用中从数据库获取）
            training_data = self.generate_training_data(detection_type)
            
            # 训练孤立森林模型
            model = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(training_data)
            
            model.fit(scaled_data)
            
            # 保存模型
            self.models[detection_type] = model
            self.scalers[detection_type] = scaler
            
            print(f"{detection_type} 模型训练完成")
```

## 8.4.2 应急预案管理

### 预案体系架构

```javascript
class EmergencyPlanManager {
    constructor(config) {
        this.config = config;
        this.plans = new Map();
        this.activePlans = new Map();
        this.planHistory = [];
        
        this.loadEmergencyPlans();
    }
    
    loadEmergencyPlans() {
        // 洪水应急预案
        this.plans.set('flood', {
            id: 'flood_response',
            name: '洪水应急响应预案',
            trigger_conditions: {
                water_level: { threshold: 188.0, operator: '>=' },
                rainfall_24h: { threshold: 100, operator: '>=' },
                risk_level: { threshold: 0.7, operator: '>=' }
            },
            phases: [
                {
                    phase: 'preparation',
                    name: '准备阶段',
                    duration: 30, // 分钟
                    actions: [
                        'activate_emergency_center',
                        'notify_key_personnel',
                        'check_communication_systems',
                        'prepare_emergency_supplies'
                    ]
                },
                {
                    phase: 'response',
                    name: '响应阶段',
                    duration: 120,
                    actions: [
                        'implement_flood_control_measures',
                        'coordinate_evacuation',
                        'monitor_water_levels',
                        'manage_reservoir_operations'
                    ]
                },
                {
                    phase: 'recovery',
                    name: '恢复阶段',
                    duration: 480,
                    actions: [
                        'assess_damage',
                        'restore_normal_operations',
                        'conduct_post_event_analysis',
                        'update_emergency_plans'
                    ]
                }
            ],
            resources: {
                personnel: ['emergency_manager', 'technical_experts', 'operators'],
                equipment: ['pumps', 'generators', 'communication_devices'],
                materials: ['sandbags', 'barriers', 'emergency_supplies']
            }
        });
        
        // 大坝安全应急预案
        this.plans.set('dam_safety', {
            id: 'dam_safety_response',
            name: '大坝安全应急预案',
            trigger_conditions: {
                seepage_rate: { threshold: 0.5, operator: '>=' },
                displacement: { threshold: 10, operator: '>=' },
                structural_alert: { threshold: 'red', operator: '==' }
            },
            phases: [
                {
                    phase: 'immediate',
                    name: '即时响应',
                    duration: 10,
                    actions: [
                        'activate_dam_safety_protocol',
                        'notify_dam_safety_team',
                        'implement_emergency_monitoring',
                        'prepare_evacuation_notice'
                    ]
                },
                {
                    phase: 'assessment',
                    name: '评估阶段',
                    duration: 60,
                    actions: [
                        'conduct_structural_assessment',
                        'analyze_monitoring_data',
                        'determine_risk_level',
                        'decide_mitigation_measures'
                    ]
                },
                {
                    phase: 'mitigation',
                    name: '缓解阶段',
                    duration: 240,
                    actions: [
                        'implement_structural_repairs',
                        'adjust_reservoir_operations',
                        'enhance_monitoring_coverage',
                        'coordinate_downstream_protection'
                    ]
                }
            ]
        });
    }
    
    async activatePlan(planId, triggerData, overrides = {}) {
        const plan = this.plans.get(planId);
        if (!plan) {
            throw new Error(`应急预案不存在: ${planId}`);
        }
        
        // 创建预案执行实例
        const execution = {
            id: this.generateExecutionId(),
            planId: planId,
            plan: plan,
            triggerData: triggerData,
            overrides: overrides,
            status: 'active',
            currentPhase: 0,
            startTime: new Date(),
            phases: plan.phases.map(phase => ({
                ...phase,
                status: 'pending',
                startTime: null,
                endTime: null,
                actions: phase.actions.map(action => ({
                    id: action,
                    status: 'pending',
                    assignee: null,
                    startTime: null,
                    endTime: null,
                    result: null
                }))
            }))
        };
        
        this.activePlans.set(execution.id, execution);
        
        // 启动第一个阶段
        await this.startPhase(execution, 0);
        
        // 记录预案激活
        this.logPlanActivation(execution);
        
        return execution;
    }
    
    async startPhase(execution, phaseIndex) {
        if (phaseIndex >= execution.phases.length) {
            await this.completePlan(execution);
            return;
        }
        
        const phase = execution.phases[phaseIndex];
        phase.status = 'active';
        phase.startTime = new Date();
        
        execution.currentPhase = phaseIndex;
        
        console.log(`启动预案阶段: ${phase.name}`);
        
        // 并行执行阶段中的所有行动
        const actionPromises = phase.actions.map(action => 
            this.executeAction(execution, phaseIndex, action)
        );
        
        // 等待所有行动完成或超时
        const timeout = phase.duration * 60 * 1000; // 转换为毫秒
        
        try {
            await Promise.race([
                Promise.all(actionPromises),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('阶段超时')), timeout)
                )
            ]);
            
            phase.status = 'completed';
            phase.endTime = new Date();
            
            // 启动下一个阶段
            await this.startPhase(execution, phaseIndex + 1);
            
        } catch (error) {
            phase.status = 'failed';
            phase.endTime = new Date();
            phase.error = error.message;
            
            // 处理阶段失败
            await this.handlePhaseFailure(execution, phaseIndex, error);
        }
    }
    
    async executeAction(execution, phaseIndex, action) {
        action.status = 'running';
        action.startTime = new Date();
        
        try {
            // 执行具体行动
            const result = await this.performAction(action.id, execution);
            
            action.status = 'completed';
            action.endTime = new Date();
            action.result = result;
            
            console.log(`行动完成: ${action.id}`);
            
        } catch (error) {
            action.status = 'failed';
            action.endTime = new Date();
            action.error = error.message;
            
            console.error(`行动失败: ${action.id} - ${error.message}`);
            throw error;
        }
    }
    
    async performAction(actionId, execution) {
        const actionHandlers = {
            // 通知相关人员
            notify_key_personnel: async () => {
                const notifications = await this.sendEmergencyNotifications(execution);
                return { notifications_sent: notifications.length };
            },
            
            // 激活应急中心
            activate_emergency_center: async () => {
                await this.activateEmergencyCenter(execution);
                return { center_activated: true };
            },
            
            // 实施防洪措施
            implement_flood_control_measures: async () => {
                const measures = await this.implementFloodControlMeasures(execution);
                return { measures_implemented: measures };
            },
            
            // 监测水位
            monitor_water_levels: async () => {
                await this.enhanceWaterLevelMonitoring(execution);
                return { enhanced_monitoring: true };
            },
            
            // 评估损失
            assess_damage: async () => {
                const assessment = await this.conductDamageAssessment(execution);
                return assessment;
            }
        };
        
        const handler = actionHandlers[actionId];
        if (handler) {
            return await handler();
        } else {
            throw new Error(`未知的行动类型: ${actionId}`);
        }
    }
    
    async sendEmergencyNotifications(execution) {
        const notifications = [];
        const personnel = execution.plan.resources.personnel;
        
        for (const role of personnel) {
            const contacts = await this.getPersonnelContacts(role);
            
            for (const contact of contacts) {
                try {
                    await this.sendNotification(contact, {
                        type: 'emergency_activation',
                        plan: execution.plan.name,
                        trigger: execution.triggerData,
                        urgency: 'high'
                    });
                    
                    notifications.push({
                        recipient: contact.name,
                        method: contact.preferred_method,
                        status: 'sent'
                    });
                } catch (error) {
                    notifications.push({
                        recipient: contact.name,
                        method: contact.preferred_method,
                        status: 'failed',
                        error: error.message
                    });
                }
            }
        }
        
        return notifications;
    }
    
    getExecutionStatus(executionId) {
        const execution = this.activePlans.get(executionId);
        if (!execution) {
            return null;
        }
        
        const currentPhase = execution.phases[execution.currentPhase];
        const completedActions = currentPhase ? 
            currentPhase.actions.filter(a => a.status === 'completed').length : 0;
        const totalActions = currentPhase ? currentPhase.actions.length : 0;
        
        return {
            executionId: execution.id,
            planName: execution.plan.name,
            status: execution.status,
            currentPhase: currentPhase ? currentPhase.name : null,
            progress: totalActions > 0 ? (completedActions / totalActions * 100) : 0,
            startTime: execution.startTime,
            estimatedCompletion: this.calculateEstimatedCompletion(execution)
        };
    }
}
```

## 8.4.3 决策支持分析

### 态势分析引擎

```python
class SituationAnalysisEngine:
    """态势分析引擎"""
    
    def __init__(self, config):
        self.config = config
        self.analysis_modules = {
            'flood_risk': FloodRiskAnalyzer(),
            'dam_safety': DamSafetyAnalyzer(), 
            'water_supply': WaterSupplyAnalyzer(),
            'drought_risk': DroughtRiskAnalyzer()
        }
        
    def analyze_current_situation(self, data_snapshot):
        """分析当前态势"""
        
        analysis_results = {}
        
        # 并行执行各模块分析
        for module_name, analyzer in self.analysis_modules.items():
            try:
                result = analyzer.analyze(data_snapshot)
                analysis_results[module_name] = result
            except Exception as e:
                print(f"分析模块 {module_name} 执行失败: {e}")
                analysis_results[module_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # 综合态势评估
        overall_assessment = self.generate_overall_assessment(analysis_results)
        
        return {
            'timestamp': data_snapshot['timestamp'],
            'module_results': analysis_results,
            'overall_assessment': overall_assessment,
            'recommendations': self.generate_recommendations(analysis_results)
        }
    
    def generate_overall_assessment(self, analysis_results):
        """生成综合态势评估"""
        
        # 提取各模块的风险等级
        risk_levels = []
        for module_name, result in analysis_results.items():
            if result.get('status') == 'success' and 'risk_level' in result:
                risk_levels.append(result['risk_level'])
        
        if not risk_levels:
            return {
                'overall_risk': 'unknown',
                'confidence': 0,
                'summary': '无法获取有效的风险评估数据'
            }
        
        # 计算综合风险等级
        max_risk = max(risk_levels)
        avg_risk = sum(risk_levels) / len(risk_levels)
        
        # 确定总体风险等级
        if max_risk >= 0.8:
            overall_risk = 'critical'
        elif max_risk >= 0.6:
            overall_risk = 'high'
        elif avg_risk >= 0.4:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'
        
        # 计算置信度
        confidence = min(len(risk_levels) / len(self.analysis_modules), 1.0)
        
        return {
            'overall_risk': overall_risk,
            'max_risk_level': max_risk,
            'average_risk_level': avg_risk,
            'confidence': confidence,
            'summary': self.generate_risk_summary(overall_risk, analysis_results)
        }
    
    def generate_recommendations(self, analysis_results):
        """生成决策建议"""
        
        recommendations = []
        
        for module_name, result in analysis_results.items():
            if result.get('status') == 'success' and 'recommendations' in result:
                module_recommendations = result['recommendations']
                
                for rec in module_recommendations:
                    recommendations.append({
                        'source_module': module_name,
                        'priority': rec.get('priority', 'medium'),
                        'action': rec['action'],
                        'rationale': rec.get('rationale', ''),
                        'estimated_impact': rec.get('impact', 'unknown'),
                        'implementation_time': rec.get('time_required', 'unknown')
                    })
        
        # 按优先级排序
        priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        recommendations.sort(
            key=lambda x: priority_order.get(x['priority'], 0),
            reverse=True
        )
        
        return recommendations

class FloodRiskAnalyzer:
    """洪水风险分析器"""
    
    def analyze(self, data_snapshot):
        """分析洪水风险"""
        
        try:
            # 提取相关数据
            water_levels = data_snapshot.get('water_levels', {})
            rainfall_data = data_snapshot.get('rainfall', {})
            weather_forecast = data_snapshot.get('weather_forecast', {})
            
            # 计算风险因素
            water_level_risk = self.assess_water_level_risk(water_levels)
            rainfall_risk = self.assess_rainfall_risk(rainfall_data)
            forecast_risk = self.assess_forecast_risk(weather_forecast)
            
            # 综合风险评估
            combined_risk = max(water_level_risk, rainfall_risk, forecast_risk)
            
            # 生成建议
            recommendations = self.generate_flood_recommendations(
                combined_risk, water_level_risk, rainfall_risk, forecast_risk
            )
            
            return {
                'status': 'success',
                'risk_level': combined_risk,
                'factors': {
                    'water_level_risk': water_level_risk,
                    'rainfall_risk': rainfall_risk,
                    'forecast_risk': forecast_risk
                },
                'recommendations': recommendations,
                'details': {
                    'critical_stations': self.identify_critical_stations(water_levels),
                    'peak_forecast': self.predict_flood_peak(data_snapshot)
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def assess_water_level_risk(self, water_levels):
        """评估水位风险"""
        if not water_levels:
            return 0
        
        max_risk = 0
        for station_id, level_data in water_levels.items():
            current_level = level_data.get('current_level', 0)
            warning_level = level_data.get('warning_level', float('inf'))
            alert_level = level_data.get('alert_level', float('inf'))
            
            if current_level >= alert_level:
                risk = 0.9
            elif current_level >= warning_level:
                risk = 0.6
            else:
                # 基于接近程度计算风险
                risk = max(0, (current_level - warning_level * 0.8) / (warning_level * 0.2))
            
            max_risk = max(max_risk, risk)
        
        return min(max_risk, 1.0)
    
    def generate_flood_recommendations(self, combined_risk, water_risk, rainfall_risk, forecast_risk):
        """生成洪水应对建议"""
        
        recommendations = []
        
        if combined_risk >= 0.8:
            recommendations.extend([
                {
                    'priority': 'critical',
                    'action': '立即启动防洪应急预案',
                    'rationale': f'综合洪水风险达到 {combined_risk:.2f}，超过临界阈值',
                    'impact': 'high',
                    'time_required': '立即'
                },
                {
                    'priority': 'critical', 
                    'action': '准备人员疏散',
                    'rationale': '洪水风险极高，需要准备下游区域人员疏散',
                    'impact': 'critical',
                    'time_required': '30分钟内'
                }
            ])
        
        if water_risk >= 0.6:
            recommendations.append({
                'priority': 'high',
                'action': '增加水库泄洪量',
                'rationale': f'水位风险为 {water_risk:.2f}，需要主动降低库水位',
                'impact': 'high',
                'time_required': '1小时内'
            })
        
        if rainfall_risk >= 0.5:
            recommendations.append({
                'priority': 'medium',
                'action': '加强降雨监测',
                'rationale': f'降雨风险为 {rainfall_risk:.2f}，需要密切监测降雨发展',
                'impact': 'medium',
                'time_required': '持续'
            })
        
        return recommendations
```

## 小结

应急响应与决策支持系统是智慧水利平台在关键时刻发挥作用的核心，通过智能事件检测、多级预警体系、应急预案管理和态势分析引擎，为水利应急管理提供全方位的技术支撑。

**关键要点总结**：

1. **预警体系**：建立多级、多维度的预警机制，实现早期识别和响应

2. **智能检测**：结合统计方法、机器学习和规则引擎，提高事件检测准确性

3. **预案管理**：构建标准化、流程化的应急预案执行体系

4. **决策支持**：通过态势分析和智能推荐，辅助应急决策制定

在下一节中，我们将探讨系统集成与运维管理的相关内容。

