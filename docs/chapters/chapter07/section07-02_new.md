## 7.2 数据融合技术

### 7.2.1 多源数据融合理论基础

数据融合是将来自多个数据源的信息进行有效整合，以获得比单一数据源更准确、更完整、更可靠信息的过程。在智慧水利系统中，数据融合技术是实现综合分析和智能决策的核心技术。

#### 数据融合层次结构

根据抽象程度，数据融合可分为三个层次：

**1. 数据级融合（Data Level Fusion）**
直接对原始传感器数据进行融合处理：

```python
class DataLevelFusion:
    def __init__(self):
        self.sensors = {}
        self.fusion_methods = {
            'weighted_average': self.weighted_average_fusion,
            'kalman_filter': self.kalman_filter_fusion,
            'bayesian_fusion': self.bayesian_fusion
        }
    
    def weighted_average_fusion(self, sensor_readings, weights):
        """加权平均融合"""
        if len(sensor_readings) != len(weights):
            raise ValueError("传感器读数和权重数量不匹配")
        
        numerator = sum(reading * weight for reading, weight in zip(sensor_readings, weights))
        denominator = sum(weights)
        
        return numerator / denominator if denominator > 0 else 0
    
    def calculate_dynamic_weights(self, sensor_data):
        """基于传感器精度动态计算权重"""
        weights = []
        for sensor_id, data in sensor_data.items():
            # 基于传感器历史准确度计算权重
            accuracy = self.get_sensor_accuracy(sensor_id)
            # 基于数据质量调整权重
            quality_score = self.assess_data_quality(data)
            
            weight = accuracy * quality_score
            weights.append(weight)
        
        # 归一化权重
        total_weight = sum(weights)
        return [w / total_weight for w in weights]
```

**2. 特征级融合（Feature Level Fusion）**
对提取的特征进行融合：

```python
class FeatureLevelFusion:
    def __init__(self):
        self.feature_extractors = {}
        self.fusion_algorithms = {}
    
    def extract_features(self, raw_data, sensor_type):
        """从原始数据中提取特征"""
        if sensor_type == 'water_level':
            features = {
                'mean': np.mean(raw_data),
                'std': np.std(raw_data),
                'trend': self.calculate_trend(raw_data),
                'seasonality': self.detect_seasonality(raw_data)
            }
        elif sensor_type == 'flow_rate':
            features = {
                'peak_flow': np.max(raw_data),
                'base_flow': np.percentile(raw_data, 10),
                'variability': self.coefficient_of_variation(raw_data)
            }
        
        return features
    
    def fuse_features(self, feature_sets, fusion_method='concatenation'):
        """特征融合"""
        if fusion_method == 'concatenation':
            # 简单拼接所有特征
            fused_features = {}
            for feature_set in feature_sets:
                fused_features.update(feature_set)
        
        elif fusion_method == 'pca':
            # 使用主成分分析降维融合
            from sklearn.decomposition import PCA
            
            # 将特征转换为矩阵形式
            feature_matrix = self.features_to_matrix(feature_sets)
            pca = PCA(n_components=0.95)  # 保留95%的方差
            fused_features = pca.fit_transform(feature_matrix)
        
        return fused_features
```

**3. 决策级融合（Decision Level Fusion）**
对多个算法的决策结果进行融合：

```python
class DecisionLevelFusion:
    def __init__(self):
        self.classifiers = []
        self.fusion_strategies = {
            'majority_voting': self.majority_voting,
            'weighted_voting': self.weighted_voting,
            'dempster_shafer': self.dempster_shafer_fusion
        }
    
    def majority_voting(self, predictions):
        """多数投票融合"""
        from collections import Counter
        vote_count = Counter(predictions)
        return vote_count.most_common(1)[0][0]
    
    def weighted_voting(self, predictions, weights):
        """加权投票融合"""
        vote_scores = {}
        for prediction, weight in zip(predictions, weights):
            if prediction in vote_scores:
                vote_scores[prediction] += weight
            else:
                vote_scores[prediction] = weight
        
        return max(vote_scores, key=vote_scores.get)
    
    def dempster_shafer_fusion(self, belief_functions):
        """基于D-S证据理论的融合"""
        # 简化的D-S融合实现
        combined_belief = {}
        
        for hypothesis in belief_functions[0].keys():
            combined_mass = 1.0
            for bf in belief_functions:
                combined_mass *= bf.get(hypothesis, 0)
            combined_belief[hypothesis] = combined_mass
        
        # 归一化
        total_mass = sum(combined_belief.values())
        for hypothesis in combined_belief:
            combined_belief[hypothesis] /= total_mass
        
        return combined_belief
```

### 7.2.2 时空数据融合算法实现

水利数据具有明显的时空特征，需要专门的融合算法处理时空维度的数据整合。

#### 时间对齐算法

```python
class TemporalAlignment:
    def __init__(self, reference_interval=300):  # 5分钟基准间隔
        self.reference_interval = reference_interval
        self.interpolation_methods = {
            'linear': self.linear_interpolation,
            'spline': self.spline_interpolation,
            'nearest': self.nearest_neighbor
        }
    
    def align_timeseries(self, timeseries_data, method='linear'):
        """时间序列对齐"""
        # 1. 找到时间范围
        start_time = min(min(ts['timestamps']) for ts in timeseries_data)
        end_time = max(max(ts['timestamps']) for ts in timeseries_data)
        
        # 2. 生成统一时间网格
        aligned_timestamps = self.generate_time_grid(start_time, end_time)
        
        # 3. 对每个时间序列进行插值
        aligned_data = {}
        for sensor_id, ts_data in timeseries_data.items():
            interpolated_values = self.interpolation_methods[method](
                ts_data['timestamps'], 
                ts_data['values'], 
                aligned_timestamps
            )
            aligned_data[sensor_id] = {
                'timestamps': aligned_timestamps,
                'values': interpolated_values
            }
        
        return aligned_data
    
    def generate_time_grid(self, start_time, end_time):
        """生成统一时间网格"""
        timestamps = []
        current_time = start_time
        while current_time <= end_time:
            timestamps.append(current_time)
            current_time += datetime.timedelta(seconds=self.reference_interval)
        return timestamps
    
    def linear_interpolation(self, timestamps, values, target_timestamps):
        """线性插值"""
        from scipy import interpolate
        
        # 转换为数值时间戳
        numeric_timestamps = [t.timestamp() for t in timestamps]
        target_numeric = [t.timestamp() for t in target_timestamps]
        
        f = interpolate.interp1d(
            numeric_timestamps, 
            values, 
            kind='linear',
            bounds_error=False,
            fill_value='extrapolate'
        )
        
        return f(target_numeric)
```

#### 空间插值算法

```python
class SpatialInterpolation:
    def __init__(self):
        self.interpolation_methods = {
            'idw': self.inverse_distance_weighting,
            'kriging': self.ordinary_kriging,
            'spline': self.thin_plate_spline
        }
    
    def inverse_distance_weighting(self, known_points, target_points, power=2):
        """反距离权重插值"""
        interpolated_values = []
        
        for target_x, target_y in target_points:
            weights = []
            values = []
            
            for (x, y, value) in known_points:
                distance = np.sqrt((target_x - x)**2 + (target_y - y)**2)
                if distance == 0:
                    # 目标点与已知点重合
                    interpolated_values.append(value)
                    break
                else:
                    weight = 1 / (distance ** power)
                    weights.append(weight)
                    values.append(value)
            else:
                # 加权平均
                weighted_sum = sum(w * v for w, v in zip(weights, values))
                weight_sum = sum(weights)
                interpolated_value = weighted_sum / weight_sum
                interpolated_values.append(interpolated_value)
        
        return interpolated_values
    
    def ordinary_kriging(self, known_points, target_points, variogram_model='spherical'):
        """普通克里金插值"""
        try:
            from pykrige.ok import OrdinaryKriging
            
            # 提取坐标和值
            x = [point[0] for point in known_points]
            y = [point[1] for point in known_points]
            values = [point[2] for point in known_points]
            
            # 创建克里金模型
            OK = OrdinaryKriging(
                x, y, values,
                variogram_model=variogram_model,
                verbose=False,
                enable_plotting=False
            )
            
            # 执行插值
            target_x = [point[0] for point in target_points]
            target_y = [point[1] for point in target_points]
            
            interpolated_values, variance = OK.execute('points', target_x, target_y)
            
            return interpolated_values, variance
            
        except ImportError:
            print("PyKrige library not available, falling back to IDW")
            return self.inverse_distance_weighting(known_points, target_points)
```

#### 时空联合融合算法

```python
class SpatioTemporalFusion:
    def __init__(self, spatial_weight=0.5, temporal_weight=0.5):
        self.spatial_weight = spatial_weight
        self.temporal_weight = temporal_weight
        self.spatial_interpolator = SpatialInterpolation()
        self.temporal_aligner = TemporalAlignment()
    
    def fuse_spatiotemporal_data(self, sensor_data, target_locations, target_times):
        """时空数据融合"""
        # 1. 时间维度对齐
        aligned_data = self.temporal_aligner.align_timeseries(sensor_data)
        
        # 2. 空间维度插值
        fused_results = []
        
        for target_time in target_times:
            # 获取该时刻的所有传感器数据
            time_slice_data = []
            for sensor_id, data in aligned_data.items():
                sensor_location = self.get_sensor_location(sensor_id)
                time_index = self.find_time_index(data['timestamps'], target_time)
                value = data['values'][time_index]
                
                time_slice_data.append((
                    sensor_location[0],  # x坐标
                    sensor_location[1],  # y坐标
                    value
                ))
            
            # 空间插值
            interpolated_values = self.spatial_interpolator.inverse_distance_weighting(
                time_slice_data, 
                target_locations
            )
            
            fused_results.append({
                'timestamp': target_time,
                'locations': target_locations,
                'values': interpolated_values
            })
        
        return fused_results
    
    def adaptive_weight_calculation(self, sensor_data, target_location, target_time):
        """自适应权重计算"""
        weights = {}
        
        for sensor_id, data in sensor_data.items():
            sensor_location = self.get_sensor_location(sensor_id)
            
            # 空间距离
            spatial_distance = np.sqrt(
                (target_location[0] - sensor_location[0])**2 + 
                (target_location[1] - sensor_location[1])**2
            )
            
            # 时间距离
            closest_time_index = self.find_closest_time_index(data['timestamps'], target_time)
            temporal_distance = abs((data['timestamps'][closest_time_index] - target_time).total_seconds())
            
            # 综合权重计算
            spatial_weight = 1 / (1 + spatial_distance)
            temporal_weight = 1 / (1 + temporal_distance)
            
            combined_weight = (
                self.spatial_weight * spatial_weight + 
                self.temporal_weight * temporal_weight
            )
            
            weights[sensor_id] = combined_weight
        
        # 归一化权重
        total_weight = sum(weights.values())
        return {k: v/total_weight for k, v in weights.items()}
```

### 7.2.3 异构数据格式转换技术

智慧水利系统中的数据来源多样，格式各异，需要建立统一的数据格式转换机制。

#### 数据格式标准化

```python
class DataFormatConverter:
    def __init__(self):
        self.supported_formats = {
            'csv': self.parse_csv,
            'json': self.parse_json,
            'xml': self.parse_xml,
            'shp': self.parse_shapefile,
            'netcdf': self.parse_netcdf,
            'hdf5': self.parse_hdf5
        }
        
        self.standard_schema = {
            'timestamp': 'datetime',
            'location': 'geometry',
            'value': 'float',
            'quality': 'string',
            'source': 'string'
        }
    
    def convert_to_standard_format(self, data, source_format):
        """转换为标准格式"""
        if source_format not in self.supported_formats:
            raise ValueError(f"不支持的数据格式: {source_format}")
        
        # 解析原始数据
        parsed_data = self.supported_formats[source_format](data)
        
        # 转换为标准格式
        standardized_data = self.standardize_data(parsed_data)
        
        # 验证数据格式
        self.validate_standard_format(standardized_data)
        
        return standardized_data
    
    def parse_csv(self, csv_data):
        """解析CSV格式数据"""
        import pandas as pd
        
        df = pd.read_csv(csv_data)
        
        # 自动检测时间列
        time_columns = self.detect_time_columns(df)
        
        # 自动检测坐标列
        coord_columns = self.detect_coordinate_columns(df)
        
        # 自动检测数值列
        value_columns = self.detect_value_columns(df)
        
        parsed_data = {
            'timestamps': df[time_columns[0]] if time_columns else None,
            'coordinates': df[coord_columns] if coord_columns else None,
            'values': df[value_columns] if value_columns else None
        }
        
        return parsed_data
    
    def parse_json(self, json_data):
        """解析JSON格式数据"""
        import json
        
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        # 递归解析嵌套JSON结构
        flattened_data = self.flatten_json(data)
        
        return flattened_data
    
    def parse_netcdf(self, netcdf_file):
        """解析NetCDF格式数据"""
        try:
            import xarray as xr
            
            ds = xr.open_dataset(netcdf_file)
            
            parsed_data = {
                'variables': list(ds.variables.keys()),
                'dimensions': list(ds.dims.keys()),
                'coordinates': {coord: ds.coords[coord].values for coord in ds.coords},
                'data': {var: ds[var].values for var in ds.data_vars}
            }
            
            return parsed_data
            
        except ImportError:
            raise ImportError("需要安装xarray库来处理NetCDF文件")
```

#### 数据质量标准化

```python
class DataQualityStandardizer:
    def __init__(self):
        self.quality_codes = {
            'excellent': 1.0,
            'good': 0.8,
            'fair': 0.6,
            'poor': 0.4,
            'bad': 0.2,
            'missing': 0.0
        }
        
        self.quality_rules = {
            'range_check': self.check_value_range,
            'trend_check': self.check_trend_consistency,
            'neighbor_check': self.check_neighbor_consistency
        }
    
    def standardize_quality_codes(self, data_with_quality):
        """标准化质量代码"""
        standardized_data = []
        
        for record in data_with_quality:
            if 'quality' in record:
                # 转换质量代码为标准格式
                original_quality = record['quality']
                standard_quality = self.map_quality_code(original_quality)
                record['quality_score'] = standard_quality
            
            # 应用质量检查规则
            quality_scores = []
            for rule_name, rule_func in self.quality_rules.items():
                score = rule_func(record)
                quality_scores.append(score)
            
            # 综合质量评分
            record['overall_quality'] = np.mean(quality_scores)
            standardized_data.append(record)
        
        return standardized_data
    
    def check_value_range(self, record):
        """检查数值是否在合理范围内"""
        value = record.get('value')
        sensor_type = record.get('sensor_type', 'unknown')
        
        ranges = self.get_sensor_ranges(sensor_type)
        
        if ranges['min'] <= value <= ranges['max']:
            return 1.0
        elif value < ranges['min'] - ranges['tolerance'] or value > ranges['max'] + ranges['tolerance']:
            return 0.0
        else:
            return 0.5
```

### 7.2.4 数据一致性处理方法

确保多源数据的一致性是数据融合的关键环节。

#### 一致性检查算法

```python
class ConsistencyChecker:
    def __init__(self):
        self.consistency_rules = {
            'temporal_consistency': self.check_temporal_consistency,
            'spatial_consistency': self.check_spatial_consistency,
            'logical_consistency': self.check_logical_consistency,
            'semantic_consistency': self.check_semantic_consistency
        }
    
    def check_temporal_consistency(self, data_series):
        """检查时间一致性"""
        issues = []
        
        # 检查时间戳单调性
        timestamps = [record['timestamp'] for record in data_series]
        if timestamps != sorted(timestamps):
            issues.append("时间戳非单调递增")
        
        # 检查时间间隔一致性
        intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                    for i in range(len(timestamps)-1)]
        
        if len(set(intervals)) > 1:  # 时间间隔不一致
            expected_interval = statistics.mode(intervals)
            inconsistent_indices = [i for i, interval in enumerate(intervals) 
                                  if abs(interval - expected_interval) > 60]  # 允许1分钟误差
            
            if inconsistent_indices:
                issues.append(f"时间间隔不一致，异常位置: {inconsistent_indices}")
        
        return {
            'is_consistent': len(issues) == 0,
            'issues': issues,
            'consistency_score': 1.0 - len(issues) / 10  # 简单评分
        }
    
    def check_spatial_consistency(self, multi_sensor_data):
        """检查空间一致性"""
        issues = []
        
        # 获取同一时刻不同传感器的数据
        time_slices = self.group_by_time(multi_sensor_data)
        
        for timestamp, sensor_readings in time_slices.items():
            if len(sensor_readings) > 1:
                # 计算空间相关性
                locations = [reading['location'] for reading in sensor_readings]
                values = [reading['value'] for reading in sensor_readings]
                
                # 距离权重相关性检查
                correlation_score = self.calculate_spatial_correlation(locations, values)
                
                if correlation_score < 0.3:  # 阈值可调整
                    issues.append(f"时刻 {timestamp} 空间一致性较差，相关性: {correlation_score:.3f}")
        
        return {
            'is_consistent': len(issues) == 0,
            'issues': issues,
            'consistency_score': 1.0 - len(issues) / len(time_slices)
        }
    
    def resolve_inconsistencies(self, inconsistent_data, resolution_strategy='weighted_average'):
        """解决数据不一致性"""
        if resolution_strategy == 'weighted_average':
            return self.weighted_average_resolution(inconsistent_data)
        elif resolution_strategy == 'trust_majority':
            return self.majority_trust_resolution(inconsistent_data)
        elif resolution_strategy == 'expert_rules':
            return self.expert_rules_resolution(inconsistent_data)
        else:
            raise ValueError(f"不支持的解决策略: {resolution_strategy}")
    
    def weighted_average_resolution(self, data_points):
        """加权平均解决不一致性"""
        weights = []
        values = []
        
        for point in data_points:
            # 基于数据质量和传感器可靠性计算权重
            weight = point.get('quality_score', 0.5) * point.get('sensor_reliability', 0.8)
            weights.append(weight)
            values.append(point['value'])
        
        # 加权平均
        weighted_sum = sum(w * v for w, v in zip(weights, values))
        weight_sum = sum(weights)
        
        resolved_value = weighted_sum / weight_sum if weight_sum > 0 else np.mean(values)
        
        return {
            'resolved_value': resolved_value,
            'confidence': weight_sum / len(weights),
            'original_values': values,
            'resolution_method': 'weighted_average'
        }
```

## 实践案例：多源数据融合系统

以流域洪水预警系统为例，展示完整的数据融合实现：

```python
class FloodWarningDataFusion:
    def __init__(self, config):
        self.config = config
        self.data_sources = {
            'sensors': SensorDataSource(),
            'weather': WeatherDataSource(),
            'satellite': SatelliteDataSource(),
            'historical': HistoricalDataSource()
        }
        
        self.fusion_engine = DataFusionEngine()
        self.consistency_checker = ConsistencyChecker()
    
    def run_fusion_pipeline(self, target_time, target_area):
        """运行数据融合流水线"""
        try:
            # 1. 数据采集
            raw_data = self.collect_multi_source_data(target_time, target_area)
            
            # 2. 数据预处理
            preprocessed_data = self.preprocess_data(raw_data)
            
            # 3. 一致性检查
            consistency_report = self.check_data_consistency(preprocessed_data)
            
            # 4. 不一致性处理
            if not consistency_report['is_consistent']:
                preprocessed_data = self.resolve_inconsistencies(
                    preprocessed_data, consistency_report
                )
            
            # 5. 数据融合
            fused_data = self.fusion_engine.fuse_data(
                preprocessed_data,
                fusion_method='adaptive_weighted'
            )
            
            # 6. 质量评估
            quality_metrics = self.evaluate_fusion_quality(fused_data, raw_data)
            
            return {
                'fused_data': fused_data,
                'quality_metrics': quality_metrics,
                'processing_metadata': {
                    'fusion_time': datetime.now(),
                    'data_sources_used': list(raw_data.keys()),
                    'consistency_issues': consistency_report.get('issues', [])
                }
            }
            
        except Exception as e:
            self.handle_fusion_error(e)
            return None
    
    def evaluate_fusion_quality(self, fused_data, original_data):
        """评估融合质量"""
        metrics = {
            'completeness': self.calculate_completeness(fused_data),
            'accuracy': self.estimate_accuracy(fused_data, original_data),
            'consistency': self.measure_consistency(fused_data),
            'timeliness': self.assess_timeliness(fused_data)
        }
        
        # 综合质量评分
        weights = self.config.get('quality_weights', {'completeness': 0.3, 'accuracy': 0.4, 'consistency': 0.2, 'timeliness': 0.1})
        overall_quality = sum(metrics[metric] * weights[metric] for metric in metrics)
        
        metrics['overall_quality'] = overall_quality
        
        return metrics
```

通过本节学习，学生应掌握多源数据融合的理论基础和实现方法，为构建高质量的智慧水利数据分析系统奠定基础。
