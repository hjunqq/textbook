# 第三节 三维场景中的监测点设计

## 引言

三维场景中的监测点设计是将抽象的监测数据转化为直观空间信息的关键环节。与传统的二维地图标注不同，三维场景中的监测点需要考虑更多的视觉因素、空间关系和交互方式。有效的监测点设计不仅要准确传达数据信息，还要保持良好的视觉效果和用户体验。

在智慧水利平台中，监测点通常分布在广阔的地理空间内，既有地表的水位站、雨量站，也有高程不同的大坝监测点，还有水下的水质监测设备。如何在复杂的三维环境中清晰地展示这些监测点的位置、状态和数据，是三维可视化设计的重要挑战。

本节将详细介绍三维场景中监测点的设计原理、实现方法和最佳实践，帮助读者掌握构建高效监测点可视化系统的核心技术。

## 7.3.1 监测点空间定位

### 坐标系统转换

#### 地理坐标到三维场景坐标的转换
```javascript
class CoordinateTransformer {
    constructor(sceneOrigin, projectionType = 'UTM') {
        this.sceneOrigin = sceneOrigin; // 场景原点
        this.projectionType = projectionType;
        this.cesium = Cesium;
    }
    
    // WGS84经纬度转Cartesian3坐标
    geographicToCartesian(longitude, latitude, height = 0) {
        const cartographic = this.cesium.Cartographic.fromDegrees(
            longitude, latitude, height
        );
        return this.cesium.Cartographic.toCartesian(cartographic);
    }
    
    // 批量转换监测点坐标
    transformMonitoringPoints(stations) {
        return stations.map(station => {
            const position = this.geographicToCartesian(
                station.longitude,
                station.latitude,
                station.elevation || 0
            );
            
            return {
                ...station,
                position: position,
                cartographic: this.cesium.Cartographic.fromDegrees(
                    station.longitude,
                    station.latitude,
                    station.elevation || 0
                )
            };
        });
    }
    
    // 考虑地形的精确定位
    adjustToTerrain(viewer, stations) {
        const terrainProvider = viewer.terrainProvider;
        const promises = [];
        
        stations.forEach(station => {
            const promise = this.cesium.sampleTerrain(
                terrainProvider,
                15, // 地形细节级别
                [station.cartographic]
            ).then(() => {
                // 更新高程到地面以上指定距离
                station.cartographic.height += station.elevationOffset || 10;
                station.position = this.cesium.Cartographic.toCartesian(
                    station.cartographic
                );
            });
            
            promises.push(promise);
        });
        
        return Promise.all(promises);
    }
}
```

#### 相对定位与绝对定位
```python
class PositioningSystem:
    """监测点定位系统"""
    
    def __init__(self, reference_point):
        self.reference_point = reference_point
        self.positioning_modes = {
            'absolute': self.absolute_positioning,
            'relative': self.relative_positioning,
            'hybrid': self.hybrid_positioning
        }
    
    def absolute_positioning(self, station):
        """绝对定位：使用全球坐标系"""
        return {
            'longitude': station['longitude'],
            'latitude': station['latitude'],
            'elevation': station['elevation'],
            'coordinate_system': 'WGS84'
        }
    
    def relative_positioning(self, station):
        """相对定位：相对于参考点"""
        dx = station['longitude'] - self.reference_point['longitude']
        dy = station['latitude'] - self.reference_point['latitude']
        dz = station['elevation'] - self.reference_point['elevation']
        
        return {
            'offset_x': dx * 111320 * cos(radians(station['latitude'])),
            'offset_y': dy * 111320,
            'offset_z': dz,
            'reference': self.reference_point['id']
        }
    
    def hybrid_positioning(self, station):
        """混合定位：结合绝对和相对定位的优势"""
        absolute_pos = self.absolute_positioning(station)
        relative_pos = self.relative_positioning(station)
        
        return {
            **absolute_pos,
            'relative_offset': relative_pos,
            'positioning_mode': 'hybrid'
        }
```

### 高程处理

#### 地面贴合与悬浮展示
```javascript
class ElevationManager {
    constructor(viewer) {
        this.viewer = viewer;
        this.terrainProvider = viewer.terrainProvider;
    }
    
    // 自动贴合地面
    clampToGround(stations) {
        const cartographics = stations.map(station => 
            Cesium.Cartographic.fromDegrees(
                station.longitude,
                station.latitude
            )
        );
        
        return Cesium.sampleTerrain(this.terrainProvider, 15, cartographics)
            .then(() => {
                stations.forEach((station, index) => {
                    station.terrainHeight = cartographics[index].height;
                    station.displayHeight = station.terrainHeight + 
                        (station.elevationOffset || 10);
                });
                return stations;
            });
    }
    
    // 分层显示策略
    calculateDisplayLayers(stations) {
        const layers = {
            'ground': [],      // 地面层
            'water': [],       // 水面层
            'aerial': [],      // 空中层
            'underground': []  // 地下层
        };
        
        stations.forEach(station => {
            const relativeHeight = station.elevation - station.terrainHeight;
            
            if (relativeHeight < -5) {
                layers.underground.push(station);
            } else if (relativeHeight < 2) {
                layers.ground.push(station);
            } else if (relativeHeight < 50) {
                layers.water.push(station);
            } else {
                layers.aerial.push(station);
            }
        });
        
        return layers;
    }
    
    // 动态高程调整
    createDynamicElevation(station, animationDuration = 2000) {
        const startHeight = station.currentHeight;
        const endHeight = station.targetHeight;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / animationDuration, 1);
            
            // 使用缓动函数
            const easeProgress = this.easeInOutCubic(progress);
            station.currentHeight = startHeight + 
                (endHeight - startHeight) * easeProgress;
            
            // 更新位置
            this.updateStationPosition(station);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }
}
```

## 7.3.2 监测点视觉设计

### 图标设计系统

#### 分层图标体系
```javascript
class MonitoringPointIconSystem {
    constructor() {
        this.iconLibrary = this.initializeIconLibrary();
        this.colorSchemes = this.initializeColorSchemes();
        this.sizeMapping = this.initializeSizeMapping();
    }
    
    initializeIconLibrary() {
        return {
            // 水文监测图标
            'water_level': '💧',
            'flow_rate': '🌊',
            'rainfall': '🌧️',
            
            // 工程监测图标
            'dam_safety': '🏗️',
            'gate_status': '🚪',
            'pump_station': '⚙️',
            
            // 环境监测图标
            'water_quality': '🧪',
            'weather': '🌤️',
            'ecology': '🌱',
            
            // 系统状态图标
            'online': '✅',
            'offline': '❌',
            'warning': '⚠️',
            'error': '🚫'
        };
    }
    
    initializeColorSchemes() {
        return {
            status: {
                'normal': '#52c41a',
                'warning': '#faad14',
                'alert': '#f5222d',
                'offline': '#d9d9d9'
            },
            dataType: {
                'water_level': '#1890ff',
                'flow_rate': '#13c2c2',
                'rainfall': '#722ed1',
                'temperature': '#fa8c16',
                'water_quality': '#52c41a'
            },
            urgency: {
                'low': '#87d068',
                'medium': '#ffd666',
                'high': '#ff7875',
                'critical': '#f50'
            }
        };
    }
    
    initializeSizeMapping() {
        return {
            importance: {
                'low': 12,
                'medium': 16,
                'high': 20,
                'critical': 24
            },
            dataRange: {
                calculateSize: (value, min, max) => {
                    const normalized = (value - min) / (max - min);
                    return 10 + normalized * 15; // 10-25px范围
                }
            }
        };
    }
    
    createMonitoringPointIcon(station) {
        const iconConfig = {
            symbol: this.getIconSymbol(station.type),
            color: this.getIconColor(station),
            size: this.getIconSize(station),
            opacity: this.getIconOpacity(station),
            border: this.getIconBorder(station)
        };
        
        return this.renderIcon(iconConfig);
    }
    
    getIconSymbol(stationType) {
        return this.iconLibrary[stationType] || '📍';
    }
    
    getIconColor(station) {
        // 优先级：状态 > 数据类型 > 默认
        if (station.status !== 'normal') {
            return this.colorSchemes.status[station.status];
        }
        return this.colorSchemes.dataType[station.type] || '#1890ff';
    }
    
    getIconSize(station) {
        if (station.importance) {
            return this.sizeMapping.importance[station.importance];
        }
        
        if (station.dataValue && station.dataRange) {
            return this.sizeMapping.dataRange.calculateSize(
                station.dataValue,
                station.dataRange.min,
                station.dataRange.max
            );
        }
        
        return 16; // 默认大小
    }
}
```

#### 动态视觉效果
```javascript
class DynamicVisualEffects {
    constructor(scene) {
        this.scene = scene;
        this.animationFrames = new Map();
    }
    
    // 呼吸灯效果
    createBreathingEffect(station, options = {}) {
        const duration = options.duration || 2000;
        const minOpacity = options.minOpacity || 0.3;
        const maxOpacity = options.maxOpacity || 1.0;
        
        const animate = (timestamp) => {
            const cycle = (timestamp % duration) / duration;
            const opacity = minOpacity + 
                (maxOpacity - minOpacity) * 
                (Math.sin(cycle * Math.PI * 2) + 1) / 2;
            
            station.billboard.color = new Cesium.Color(
                station.color.red,
                station.color.green,
                station.color.blue,
                opacity
            );
            
            this.animationFrames.set(station.id, 
                requestAnimationFrame(animate)
            );
        };
        
        this.animationFrames.set(station.id,
            requestAnimationFrame(animate)
        );
    }
    
    // 数据脉冲效果
    createDataPulseEffect(station, dataValue) {
        const pulseIntensity = this.calculatePulseIntensity(
            dataValue, station.dataRange
        );
        
        const pulseAnimation = this.scene.tweens.create({
            duration: 1000,
            targets: station.billboard,
            scale: {
                from: 1.0,
                to: 1.0 + pulseIntensity * 0.5
            },
            opacity: {
                from: 1.0,
                to: 0.7
            },
            yoyo: true,
            repeat: 0,
            ease: 'Power2'
        });
        
        return pulseAnimation;
    }
    
    // 状态变化动画
    createStatusChangeAnimation(station, oldStatus, newStatus) {
        const oldColor = this.getStatusColor(oldStatus);
        const newColor = this.getStatusColor(newStatus);
        
        // 颜色渐变动画
        const colorTween = this.scene.tweens.create({
            duration: 800,
            targets: station.billboard.color,
            red: newColor.red,
            green: newColor.green,
            blue: newColor.blue,
            ease: 'Power2'
        });
        
        // 如果是告警状态，添加闪烁效果
        if (newStatus === 'alert' || newStatus === 'warning') {
            this.createAlertBlinkEffect(station);
        }
        
        return colorTween;
    }
    
    // 告警闪烁效果
    createAlertBlinkEffect(station) {
        let blinkCount = 0;
        const maxBlinks = 6;
        
        const blink = () => {
            if (blinkCount >= maxBlinks) return;
            
            station.billboard.show = !station.billboard.show;
            blinkCount++;
            
            setTimeout(blink, 200);
        };
        
        blink();
    }
    
    // 停止指定站点的所有动画
    stopAnimations(stationId) {
        if (this.animationFrames.has(stationId)) {
            cancelAnimationFrame(this.animationFrames.get(stationId));
            this.animationFrames.delete(stationId);
        }
    }
}
```

### 层次显示管理

#### LOD（细节层次）系统
```javascript
class MonitoringPointLOD {
    constructor(viewer) {
        this.viewer = viewer;
        this.lodLevels = this.initializeLODLevels();
        this.visibilityManager = new VisibilityManager();
    }
    
    initializeLODLevels() {
        return {
            // 远距离视图：只显示重要站点的简化图标
            far: {
                distance: [50000, Infinity],
                iconSize: 8,
                showLabels: false,
                showOnlyImportant: true,
                clustering: true
            },
            
            // 中距离视图：显示主要站点的标准图标
            medium: {
                distance: [5000, 50000],
                iconSize: 16,
                showLabels: true,
                showOnlyImportant: false,
                clustering: true
            },
            
            // 近距离视图：显示所有站点的详细信息
            near: {
                distance: [500, 5000],
                iconSize: 20,
                showLabels: true,
                showDataValues: true,
                clustering: false
            },
            
            // 极近距离视图：显示完整的监测点信息
            close: {
                distance: [0, 500],
                iconSize: 24,
                showLabels: true,
                showDataValues: true,
                showDetailedInfo: true,
                clustering: false
            }
        };
    }
    
    updateLOD(cameraPosition, stations) {
        stations.forEach(station => {
            const distance = this.calculateDistance(cameraPosition, station.position);
            const lodLevel = this.determineLODLevel(distance);
            
            this.applyLODSettings(station, lodLevel);
        });
    }
    
    calculateDistance(cameraPosition, stationPosition) {
        return Cesium.Cartesian3.distance(cameraPosition, stationPosition);
    }
    
    determineLODLevel(distance) {
        for (const [level, config] of Object.entries(this.lodLevels)) {
            if (distance >= config.distance[0] && distance < config.distance[1]) {
                return level;
            }
        }
        return 'far';
    }
    
    applyLODSettings(station, lodLevel) {
        const settings = this.lodLevels[lodLevel];
        
        // 更新图标大小
        station.billboard.scale = settings.iconSize / 16; // 基准大小16px
        
        // 更新标签显示
        if (station.label) {
            station.label.show = settings.showLabels;
        }
        
        // 更新数据值显示
        if (station.dataValueLabel) {
            station.dataValueLabel.show = settings.showDataValues || false;
        }
        
        // 更新详细信息显示
        if (station.detailPanel) {
            station.detailPanel.show = settings.showDetailedInfo || false;
        }
        
        // 应用重要性过滤
        if (settings.showOnlyImportant && station.importance !== 'high') {
            station.billboard.show = false;
        } else {
            station.billboard.show = true;
        }
    }
}
```

#### 聚类显示
```javascript
class MonitoringPointClustering {
    constructor(viewer) {
        this.viewer = viewer;
        this.clusteringEnabled = true;
        this.clusterDistance = 100; // 像素距离
        this.clusters = new Map();
    }
    
    performClustering(stations) {
        if (!this.clusteringEnabled) {
            return this.showAllStations(stations);
        }
        
        const screenPositions = this.calculateScreenPositions(stations);
        const clusters = this.buildClusters(stations, screenPositions);
        
        this.renderClusters(clusters);
        
        return clusters;
    }
    
    calculateScreenPositions(stations) {
        return stations.map(station => {
            const screenPosition = Cesium.SceneTransforms.wgs84ToWindowCoordinates(
                this.viewer.scene,
                station.position
            );
            
            return {
                station: station,
                screenPosition: screenPosition || new Cesium.Cartesian2(-1, -1)
            };
        });
    }
    
    buildClusters(stations, screenPositions) {
        const clusters = [];
        const processed = new Set();
        
        screenPositions.forEach((item, index) => {
            if (processed.has(index)) return;
            
            const cluster = {
                id: `cluster_${clusters.length}`,
                stations: [item.station],
                centerPosition: item.screenPosition,
                bounds: {
                    min: { ...item.screenPosition },
                    max: { ...item.screenPosition }
                }
            };
            
            // 查找临近的站点
            for (let i = index + 1; i < screenPositions.length; i++) {
                if (processed.has(i)) continue;
                
                const distance = Cesium.Cartesian2.distance(
                    item.screenPosition,
                    screenPositions[i].screenPosition
                );
                
                if (distance < this.clusterDistance) {
                    cluster.stations.push(screenPositions[i].station);
                    processed.add(i);
                    
                    // 更新聚类边界
                    this.updateClusterBounds(cluster, screenPositions[i].screenPosition);
                }
            }
            
            processed.add(index);
            clusters.push(cluster);
        });
        
        return clusters;
    }
    
    renderClusters(clusters) {
        // 清除现有聚类显示
        this.clearExistingClusters();
        
        clusters.forEach(cluster => {
            if (cluster.stations.length === 1) {
                // 单个站点，正常显示
                this.renderSingleStation(cluster.stations[0]);
            } else {
                // 多个站点，显示聚类图标
                this.renderClusterIcon(cluster);
            }
        });
    }
    
    renderClusterIcon(cluster) {
        const clusterPosition = this.calculateClusterPosition(cluster.stations);
        const clusterSize = this.calculateClusterSize(cluster.stations.length);
        const clusterColor = this.calculateClusterColor(cluster.stations);
        
        const clusterBillboard = this.viewer.entities.add({
            id: cluster.id,
            position: clusterPosition,
            billboard: {
                image: this.createClusterImage(
                    cluster.stations.length,
                    clusterSize,
                    clusterColor
                ),
                scale: 1.0,
                verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
            },
            label: {
                text: cluster.stations.length.toString(),
                font: '12pt sans-serif',
                fillColor: Cesium.Color.WHITE,
                outlineColor: Cesium.Color.BLACK,
                outlineWidth: 2,
                style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                pixelOffset: new Cesium.Cartesian2(0, -50)
            }
        });
        
        // 添加点击事件处理
        this.addClusterClickHandler(clusterBillboard, cluster);
    }
    
    createClusterImage(count, size, color) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        
        const ctx = canvas.getContext('2d');
        
        // 绘制圆形背景
        ctx.beginPath();
        ctx.arc(size / 2, size / 2, size / 2 - 2, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // 绘制数字
        ctx.fillStyle = 'white';
        ctx.font = `bold ${size / 3}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(count.toString(), size / 2, size / 2);
        
        return canvas.toDataURL();
    }
    
    addClusterClickHandler(clusterBillboard, cluster) {
        this.viewer.cesiumWidget.screenSpaceEventHandler.setInputAction((click) => {
            const pickedObject = this.viewer.scene.pick(click.position);
            
            if (Cesium.defined(pickedObject) && 
                pickedObject.id === clusterBillboard) {
                this.expandCluster(cluster);
            }
        }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
    }
    
    expandCluster(cluster) {
        // 缩放到聚类范围
        const positions = cluster.stations.map(station => station.position);
        const boundingSphere = Cesium.BoundingSphere.fromPoints(positions);
        
        this.viewer.camera.flyToBoundingSphere(boundingSphere, {
            duration: 1.5,
            complete: () => {
                // 展开后重新进行聚类计算
                setTimeout(() => {
                    this.performClustering(cluster.stations);
                }, 100);
            }
        });
    }
}
```

## 7.3.3 数据标注与展示

### 实时数据标签

#### 动态数据标签系统
```javascript
class DynamicDataLabels {
    constructor(viewer) {
        this.viewer = viewer;
        this.labelPool = new LabelPool();
        this.updateInterval = 1000; // 1秒更新一次
        this.activeLabels = new Map();
    }
    
    createDataLabel(station, dataType) {
        const labelId = `${station.id}_${dataType}_label`;
        
        const label = this.viewer.entities.add({
            id: labelId,
            position: this.calculateLabelPosition(station),
            label: {
                text: this.formatDataValue(station[dataType], dataType),
                font: '12pt sans-serif',
                fillColor: this.getDataTypeColor(dataType),
                outlineColor: Cesium.Color.BLACK,
                outlineWidth: 1,
                style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                pixelOffset: new Cesium.Cartesian2(0, -30),
                eyeOffset: new Cesium.Cartesian3(0, 0, -100),
                horizontalOrigin: Cesium.HorizontalOrigin.CENTER,
                verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                scale: 0.8,
                translucencyByDistance: new Cesium.NearFarScalar(
                    100, 1.0,    // 100米内完全不透明
                    1000, 0.3    // 1000米外30%透明度
                )
            }
        });
        
        this.activeLabels.set(labelId, {
            entity: label,
            station: station,
            dataType: dataType,
            lastUpdate: Date.now()
        });
        
        return label;
    }
    
    updateDataLabel(station, dataType, newValue) {
        const labelId = `${station.id}_${dataType}_label`;
        const labelInfo = this.activeLabels.get(labelId);
        
        if (labelInfo) {
            const oldText = labelInfo.entity.label.text;
            const newText = this.formatDataValue(newValue, dataType);
            
            // 数值变化动画
            if (oldText !== newText) {
                this.animateValueChange(labelInfo.entity, oldText, newText);
            }
            
            labelInfo.lastUpdate = Date.now();
        }
    }
    
    animateValueChange(labelEntity, oldText, newText) {
        // 先缩放到0
        const scaleDown = this.viewer.scene.tweens.create({
            duration: 200,
            targets: labelEntity.label,
            scale: 0,
            complete: () => {
                // 更新文本
                labelEntity.label.text = newText;
                
                // 再缩放回原大小
                this.viewer.scene.tweens.create({
                    duration: 200,
                    targets: labelEntity.label,
                    scale: 0.8
                });
            }
        });
    }
    
    formatDataValue(value, dataType) {
        const formatters = {
            'water_level': (val) => `${val.toFixed(2)}m`,
            'flow_rate': (val) => `${val.toFixed(1)}m³/s`,
            'rainfall': (val) => `${val.toFixed(1)}mm`,
            'temperature': (val) => `${val.toFixed(1)}°C`,
            'water_quality': (val) => `${val.toFixed(1)}`,
            'pressure': (val) => `${val.toFixed(2)}MPa`
        };
        
        return formatters[dataType] ? formatters[dataType](value) : value.toString();
    }
    
    // 批量更新所有数据标签
    updateAllLabels(stationsData) {
        stationsData.forEach(station => {
            Object.keys(station.monitoringData || {}).forEach(dataType => {
                this.updateDataLabel(
                    station,
                    dataType,
                    station.monitoringData[dataType]
                );
            });
        });
    }
    
    // 根据相机距离自动调整标签显示
    adjustLabelsForDistance() {
        const cameraPosition = this.viewer.camera.position;
        
        this.activeLabels.forEach((labelInfo, labelId) => {
            const distance = Cesium.Cartesian3.distance(
                cameraPosition,
                labelInfo.station.position
            );
            
            // 根据距离调整标签属性
            if (distance > 10000) {
                labelInfo.entity.label.show = false;
            } else if (distance > 5000) {
                labelInfo.entity.label.scale = 0.6;
                labelInfo.entity.label.show = true;
            } else {
                labelInfo.entity.label.scale = 0.8;
                labelInfo.entity.label.show = true;
            }
        });
    }
}
```

### 状态指示器

#### 多状态可视化
```javascript
class StatusIndicator {
    constructor() {
        this.statusDefinitions = this.initializeStatusDefinitions();
        this.indicatorStyles = this.initializeIndicatorStyles();
    }
    
    initializeStatusDefinitions() {
        return {
            operational: {
                normal: { priority: 1, color: '#52c41a', icon: '✓' },
                maintenance: { priority: 2, color: '#faad14', icon: '🔧' },
                testing: { priority: 3, color: '#1890ff', icon: '🧪' }
            },
            alert: {
                warning: { priority: 4, color: '#fa8c16', icon: '⚠️' },
                alarm: { priority: 5, color: '#f5222d', icon: '🚨' },
                critical: { priority: 6, color: '#a8071a', icon: '💥' }
            },
            communication: {
                online: { priority: 1, color: '#52c41a', icon: '📶' },
                offline: { priority: 7, color: '#d9d9d9', icon: '📵' },
                unstable: { priority: 4, color: '#fa8c16', icon: '📶' }
            },
            data: {
                valid: { priority: 1, color: '#52c41a', icon: '📊' },
                suspicious: { priority: 3, color: '#faad14', icon: '❓' },
                invalid: { priority: 5, color: '#f5222d', icon: '❌' }
            }
        };
    }
    
    initializeIndicatorStyles() {
        return {
            ring: this.createRingIndicator,
            badge: this.createBadgeIndicator,
            pulse: this.createPulseIndicator,
            icon: this.createIconIndicator
        };
    }
    
    createCompositeStatusIndicator(station) {
        const statusCategories = ['operational', 'alert', 'communication', 'data'];
        const primaryStatus = this.determinePrimaryStatus(station, statusCategories);
        
        const indicator = {
            primary: this.createPrimaryIndicator(primaryStatus),
            secondary: this.createSecondaryIndicators(station, statusCategories),
            animation: this.createStatusAnimation(primaryStatus)
        };
        
        return this.renderCompositeIndicator(indicator);
    }
    
    determinePrimaryStatus(station, categories) {
        let highestPriority = 0;
        let primaryStatus = null;
        
        categories.forEach(category => {
            const categoryStatus = station.status[category];
            if (categoryStatus) {
                const statusInfo = this.statusDefinitions[category][categoryStatus];
                if (statusInfo && statusInfo.priority > highestPriority) {
                    highestPriority = statusInfo.priority;
                    primaryStatus = {
                        category: category,
                        status: categoryStatus,
                        info: statusInfo
                    };
                }
            }
        });
        
        return primaryStatus;
    }
    
    createRingIndicator(status, size = 20) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        
        const ctx = canvas.getContext('2d');
        const centerX = size / 2;
        const centerY = size / 2;
        const radius = (size - 4) / 2;
        
        // 外圈
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        ctx.strokeStyle = status.color;
        ctx.lineWidth = 3;
        ctx.stroke();
        
        // 内圈（如果是告警状态）
        if (status.priority >= 4) {
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius - 6, 0, 2 * Math.PI);
            ctx.fillStyle = status.color;
            ctx.globalAlpha = 0.3;
            ctx.fill();
        }
        
        return canvas.toDataURL();
    }
    
    createPulseIndicator(status, size = 24) {
        // 创建脉冲动画的关键帧
        const keyframes = [];
        for (let i = 0; i <= 20; i++) {
            const progress = i / 20;
            const scale = 1 + Math.sin(progress * Math.PI) * 0.5;
            const opacity = 1 - progress * 0.5;
            
            keyframes.push({
                transform: `scale(${scale})`,
                opacity: opacity,
                offset: progress
            });
        }
        
        return {
            element: this.createRingIndicator(status, size),
            animation: {
                keyframes: keyframes,
                duration: 2000,
                iterations: Infinity
            }
        };
    }
    
    // 创建状态变化动画
    createStatusTransition(oldStatus, newStatus, duration = 800) {
        return {
            type: 'transition',
            phases: [
                {
                    // 淡出旧状态
                    duration: duration * 0.3,
                    opacity: { from: 1, to: 0 },
                    scale: { from: 1, to: 0.8 }
                },
                {
                    // 切换状态（瞬间）
                    duration: 0,
                    color: newStatus.color,
                    icon: newStatus.icon
                },
                {
                    // 淡入新状态
                    duration: duration * 0.7,
                    opacity: { from: 0, to: 1 },
                    scale: { from: 0.8, to: 1 }
                }
            ]
        };
    }
}
```

## 小结

三维场景中的监测点设计是数据可视化的关键环节，需要综合考虑空间定位、视觉设计和交互体验等多个方面。通过精确的坐标转换、层次化的显示管理和动态的状态指示，可以构建高效、直观的监测点可视化系统。

**关键要点总结**：

1. **空间定位**：掌握坐标系统转换和高程处理技术，确保监测点的精确定位

2. **视觉设计**：建立分层图标体系和动态视觉效果，提升用户体验

3. **层次管理**：实现LOD系统和聚类显示，优化大量监测点的显示性能

4. **数据标注**：设计动态数据标签和状态指示器，实时展示监测信息

在下一节中，我们将探讨监测数据的交互与查询技术，为用户提供灵活的数据分析工具。



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
