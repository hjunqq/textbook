# 7.3 三维场景中的监测点绘制

## 学习目标
通过本节学习，学生应能够：
1. 掌握监测点在三维空间中的定位和绘制技术
2. 理解大规模监测点的渲染优化策略
3. 熟练运用符号系统设计监测点的可视化方案
4. 能够实现监测点状态的动态表达和交互响应

## 引言

在智慧水利三维场景中，**监测点的可视化绘制**是连接真实世界传感器设备与虚拟三维环境的重要桥梁。每个监测点不仅要准确反映其在现实中的地理位置，还要通过直观的视觉符号传达设备状态、数据质量、预警信息等关键信息。

与传统的二维地图标点不同，三维场景中的监测点绘制需要考虑空间层次、视觉遮挡、多尺度显示等复杂因素。同时，现代水利监测系统往往包含数百甚至数千个监测点，如何在保证渲染性能的前提下实现清晰、准确、实时的监测点可视化，是本节要解决的核心技术问题。

## 7.3.1 监测点空间定位技术

### 坐标系统转换

监测点的准确定位是可视化的基础，需要将真实世界的地理坐标转换为三维场景中的空间坐标：

```javascript
class CoordinateTransformer {
    constructor(sceneOrigin, sceneScale) {
        // 场景原点地理坐标 (经度, 纬度, 海拔)
        this.sceneOrigin = sceneOrigin;
        // 场景缩放比例 (米/单位)
        this.sceneScale = sceneScale;
        
        // 地球半径 (米)
        this.earthRadius = 6378137.0;
        // 弧度转换常数
        this.degToRad = Math.PI / 180.0;
    }
    
    // 将地理坐标转换为场景坐标
    geoToScene(longitude, latitude, elevation = 0) {
        // 计算相对于场景原点的经纬度差
        const deltaLon = longitude - this.sceneOrigin.longitude;
        const deltaLat = latitude - this.sceneOrigin.latitude;
        const deltaElev = elevation - this.sceneOrigin.elevation;
        
        // 转换为米制距离
        const x = deltaLon * this.degToRad * this.earthRadius * 
                 Math.cos(this.sceneOrigin.latitude * this.degToRad);
        const y = deltaElev; // 高程方向
        const z = deltaLat * this.degToRad * this.earthRadius;
        
        // 应用场景缩放
        return {
            x: x / this.sceneScale,
            y: y / this.sceneScale,
            z: z / this.sceneScale
        };
    }
    
    // 将场景坐标转换回地理坐标
    sceneToGeo(x, y, z) {
        // 应用场景缩放
        const realX = x * this.sceneScale;
        const realY = y * this.sceneScale;
        const realZ = z * this.sceneScale;
        
        // 转换为经纬度差
        const deltaLon = realX / (this.earthRadius * Math.cos(this.sceneOrigin.latitude * this.degToRad)) / this.degToRad;
        const deltaLat = realZ / this.earthRadius / this.degToRad;
        
        return {
            longitude: this.sceneOrigin.longitude + deltaLon,
            latitude: this.sceneOrigin.latitude + deltaLat,
            elevation: this.sceneOrigin.elevation + realY
        };
    }
    
    // 批量坐标转换
    batchGeoToScene(geoPoints) {
        return geoPoints.map(point => ({
            id: point.id,
            scenePos: this.geoToScene(point.longitude, point.latitude, point.elevation),
            originalGeo: point
        }));
    }
    
    // 高精度坐标转换（考虑地球曲率）
    preciseGeoToScene(longitude, latitude, elevation = 0) {
        // 使用更精确的椭球体参数
        const a = 6378137.0; // 长半轴
        const f = 1 / 298.257223563; // 扁率
        const e2 = 2 * f - f * f; // 第一偏心率平方
        
        const lat = latitude * this.degToRad;
        const lon = longitude * this.degToRad;
        const h = elevation;
        
        // 计算卯酉圈曲率半径
        const N = a / Math.sqrt(1 - e2 * Math.sin(lat) * Math.sin(lat));
        
        // 转换为直角坐标
        const X = (N + h) * Math.cos(lat) * Math.cos(lon);
        const Y = (N + h) * Math.cos(lat) * Math.sin(lon);
        const Z = ((1 - e2) * N + h) * Math.sin(lat);
        
        // 转换为场景坐标
        const originX = this.geoToECEF(this.sceneOrigin.longitude, this.sceneOrigin.latitude, this.sceneOrigin.elevation).X;
        const originY = this.geoToECEF(this.sceneOrigin.longitude, this.sceneOrigin.latitude, this.sceneOrigin.elevation).Y;
        const originZ = this.geoToECEF(this.sceneOrigin.longitude, this.sceneOrigin.latitude, this.sceneOrigin.elevation).Z;
        
        return {
            x: (X - originX) / this.sceneScale,
            y: (Y - originY) / this.sceneScale,
            z: (Z - originZ) / this.sceneScale
        };
    }
}
```

### 地形适配定位

考虑地形高度的监测点定位系统：

```javascript
class TerrainAwarePositioning {
    constructor(viewer) {
        this.viewer = viewer;
        this.terrainProvider = viewer.terrainProvider;
        this.cesium = Cesium;
    }
    
    // 地形采样定位
    async positionOnTerrain(stations) {
        // 将站点转换为地理坐标格式
        const cartographics = stations.map(station => 
            this.cesium.Cartographic.fromDegrees(
                station.longitude,
                station.latitude,
                0
            )
        );
        
        // 采样地形高度
        await this.cesium.sampleTerrain(this.terrainProvider, 15, cartographics);
        
        // 更新站点位置
        stations.forEach((station, index) => {
            const cartographic = cartographics[index];
            station.terrainHeight = cartographic.height;
            
            // 设置显示高度（地面以上指定距离）
            station.displayHeight = cartographic.height + (station.elevationOffset || 10);
            
            // 转换为笛卡尔坐标
            station.position = this.cesium.Cartographic.toCartesian(
                this.cesium.Cartographic.fromDegrees(
                    station.longitude,
                    station.latitude,
                    station.displayHeight
                )
            );
        });
        
        return stations;
    }
    
    // 考虑地形的精确定位
    adjustToTerrain(viewer, stations) {
        const terrainProvider = viewer.terrainProvider;
        const promises = [];
        
        stations.forEach(station => {
            const cartographic = this.cesium.Cartographic.fromDegrees(
                station.longitude,
                station.latitude,
                0
            );
            
            const promise = this.cesium.sampleTerrain(
                terrainProvider,
                15, // 地形细节级别
                [cartographic]
            ).then(() => {
                // 更新高程到地面以上指定距离
                cartographic.height += station.elevationOffset || 10;
                station.position = this.cesium.Cartographic.toCartesian(cartographic);
            });
            
            promises.push(promise);
        });
        
        return Promise.all(promises);
    }
    
    // 分层定位策略
    layeredPositioning(stations) {
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
                station.displayLayer = 'underground';
                station.elevationOffset = -2; // 地下2米显示
            } else if (relativeHeight < 2) {
                layers.ground.push(station);
                station.displayLayer = 'ground';
                station.elevationOffset = 10; // 地面上10米显示
            } else if (relativeHeight < 50) {
                layers.water.push(station);
                station.displayLayer = 'water';
                station.elevationOffset = 5; // 水面上5米显示
            } else {
                layers.aerial.push(station);
                station.displayLayer = 'aerial';
                station.elevationOffset = 0; // 保持原高度
            }
        });
        
        return layers;
    }
}
```

## 7.3.2 监测点符号设计

### 分类符号系统

建立统一的监测点符号分类和编码体系：

```javascript
class MonitoringSymbolSystem {
    constructor() {
        this.symbolLibrary = this.initializeSymbolLibrary();
        this.colorSchemes = this.initializeColorSchemes();
        this.sizeMapping = this.initializeSizeMapping();
    }
    
    initializeSymbolLibrary() {
        return {
            // 水文监测符号
            hydrological: {
                'water_level': {
                    icon: '🌊',
                    shape: 'circle',
                    primaryColor: '#1890ff',
                    description: '水位监测站'
                },
                'flow_velocity': {
                    icon: '💨',
                    shape: 'diamond',
                    primaryColor: '#13c2c2',
                    description: '流速监测站'
                },
                'flow_rate': {
                    icon: '🌊',
                    shape: 'hexagon',
                    primaryColor: '#096dd9',
                    description: '流量监测站'
                }
            },
            
            // 气象监测符号
            meteorological: {
                'rainfall': {
                    icon: '🌧️',
                    shape: 'triangle',
                    primaryColor: '#722ed1',
                    description: '雨量监测站'
                },
                'wind_speed': {
                    icon: '💨',
                    shape: 'arrow',
                    primaryColor: '#52c41a',
                    description: '风速监测站'
                },
                'temperature': {
                    icon: '🌡️',
                    shape: 'square',
                    primaryColor: '#fa8c16',
                    description: '温度监测站'
                }
            },
            
            // 工程监测符号
            engineering: {
                'dam_safety': {
                    icon: '🏗️',
                    shape: 'rectangle',
                    primaryColor: '#8c8c8c',
                    description: '大坝安全监测站'
                },
                'gate_opening': {
                    icon: '🚪',
                    shape: 'parallelogram',
                    primaryColor: '#fa541c',
                    description: '闸门开度监测站'
                },
                'pump_status': {
                    icon: '⚙️',
                    shape: 'gear',
                    primaryColor: '#eb2f96',
                    description: '泵站状态监测站'
                }
            },
            
            // 水质监测符号
            quality: {
                'ph_level': {
                    icon: '🧪',
                    shape: 'flask',
                    primaryColor: '#52c41a',
                    description: 'pH值监测站'
                },
                'dissolved_oxygen': {
                    icon: '💧',
                    shape: 'circle',
                    primaryColor: '#40a9ff',
                    description: '溶解氧监测站'
                },
                'turbidity': {
                    icon: '🌫️',
                    shape: 'cloud',
                    primaryColor: '#bfbfbf',
                    description: '浊度监测站'
                }
            }
        };
    }
    
    initializeColorSchemes() {
        return {
            status: {
                'normal': '#52c41a',
                'warning': '#faad14', 
                'alert': '#f5222d',
                'offline': '#d9d9d9',
                'maintenance': '#722ed1'
            },
            priority: {
                'low': '#87d068',
                'medium': '#ffd666',
                'high': '#ff7875',
                'critical': '#f50'
            },
            dataQuality: {
                'excellent': '#52c41a',
                'good': '#73d13d',
                'fair': '#faad14',
                'poor': '#ff7875',
                'bad': '#f5222d'
            }
        };
    }
    
    initializeSizeMapping() {
        return {
            importance: {
                'low': { scale: 0.8, pixelSize: 12 },
                'medium': { scale: 1.0, pixelSize: 16 },
                'high': { scale: 1.2, pixelSize: 20 },
                'critical': { scale: 1.5, pixelSize: 24 }
            },
            distance: {
                calculateScale: (distance) => {
                    if (distance < 1000) return 1.2;
                    if (distance < 5000) return 1.0;
                    if (distance < 20000) return 0.8;
                    return 0.6;
                }
            }
        };
    }
    
    // 创建监测点符号
    createMonitoringSymbol(station) {
        const category = this.determineCategory(station.type);
        const symbolDef = this.symbolLibrary[category][station.type];
        
        if (!symbolDef) {
            console.warn(`未找到监测点类型 ${station.type} 的符号定义`);
            return this.createDefaultSymbol(station);
        }
        
        const symbolConfig = {
            id: `symbol_${station.id}`,
            position: station.position,
            billboard: this.createBillboardSymbol(station, symbolDef),
            label: this.createLabelSymbol(station),
            metadata: {
                stationId: station.id,
                type: station.type,
                category: category
            }
        };
        
        return symbolConfig;
    }
    
    createBillboardSymbol(station, symbolDef) {
        return {
            image: this.generateSymbolImage(station, symbolDef),
            scale: this.calculateSymbolScale(station),
            verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            heightReference: station.displayLayer === 'ground' ? 
                Cesium.HeightReference.CLAMP_TO_GROUND : 
                Cesium.HeightReference.NONE,
            color: this.getSymbolColor(station),
            pixelOffset: new Cesium.Cartesian2(0, 0),
            eyeOffset: new Cesium.Cartesian3(0, 0, 0),
            horizontalOrigin: Cesium.HorizontalOrigin.CENTER,
            scaleByDistance: new Cesium.NearFarScalar(
                1000, 1.0,    // 1km内正常大小
                50000, 0.5    // 50km外缩小50%
            ),
            translucencyByDistance: new Cesium.NearFarScalar(
                1000, 1.0,    // 1km内完全不透明
                100000, 0.3   // 100km外30%透明度
            )
        };
    }
    
    // 生成符号图像
    generateSymbolImage(station, symbolDef) {
        const canvas = document.createElement('canvas');
        const size = this.calculateSymbolSize(station);
        canvas.width = size;
        canvas.height = size;
        
        const ctx = canvas.getContext('2d');
        
        // 绘制符号背景
        this.drawSymbolBackground(ctx, size, symbolDef.shape, this.getSymbolColor(station));
        
        // 绘制符号图标
        this.drawSymbolIcon(ctx, size, symbolDef.icon);
        
        // 绘制状态指示器
        this.drawStatusIndicator(ctx, size, station.status);
        
        return canvas.toDataURL();
    }
    
    drawSymbolBackground(ctx, size, shape, color) {
        const centerX = size / 2;
        const centerY = size / 2;
        const radius = (size - 4) / 2;
        
        ctx.fillStyle = color;
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        
        ctx.beginPath();
        
        switch (shape) {
            case 'circle':
                ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
                break;
            case 'square':
                ctx.rect(centerX - radius, centerY - radius, radius * 2, radius * 2);
                break;
            case 'diamond':
                ctx.moveTo(centerX, centerY - radius);
                ctx.lineTo(centerX + radius, centerY);
                ctx.lineTo(centerX, centerY + radius);
                ctx.lineTo(centerX - radius, centerY);
                ctx.closePath();
                break;
            case 'triangle':
                ctx.moveTo(centerX, centerY - radius);
                ctx.lineTo(centerX + radius * Math.cos(Math.PI/6), centerY + radius * Math.sin(Math.PI/6));
                ctx.lineTo(centerX - radius * Math.cos(Math.PI/6), centerY + radius * Math.sin(Math.PI/6));
                ctx.closePath();
                break;
            case 'hexagon':
                for (let i = 0; i < 6; i++) {
                    const angle = i * Math.PI / 3;
                    const x = centerX + radius * Math.cos(angle);
                    const y = centerY + radius * Math.sin(angle);
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.closePath();
                break;
            default:
                ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        }
        
        ctx.fill();
        ctx.stroke();
    }
    
    drawStatusIndicator(ctx, size, status) {
        const indicatorSize = size * 0.3;
        const x = size - indicatorSize;
        const y = indicatorSize;
        
        ctx.fillStyle = this.colorSchemes.status[status] || '#d9d9d9';
        ctx.beginPath();
        ctx.arc(x, y, indicatorSize / 2, 0, 2 * Math.PI);
        ctx.fill();
        
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.stroke();
    }
}
```

### 动态视觉效果

实现监测点的动态视觉表现：

```javascript
class DynamicVisualEffects {
    constructor(viewer) {
        this.viewer = viewer;
        this.animationFrames = new Map();
        this.effectTypes = {
            'pulse': this.createPulseEffect,
            'breathing': this.createBreathingEffect,
            'ripple': this.createRippleEffect,
            'glow': this.createGlowEffect
        };
    }
    
    // 脉冲效果
    createPulseEffect(station, options = {}) {
        const duration = options.duration || 1500;
        const maxScale = options.maxScale || 1.5;
        const minOpacity = options.minOpacity || 0.6;
        
        let startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = (elapsed % duration) / duration;
            
            // 使用正弦波创建脉冲效果
            const pulseProgress = Math.sin(progress * Math.PI * 2);
            const scale = 1 + (maxScale - 1) * Math.abs(pulseProgress) * 0.5;
            const opacity = minOpacity + (1 - minOpacity) * (1 - Math.abs(pulseProgress) * 0.5);
            
            // 更新billboard属性
            station.billboard.scale = scale;
            station.billboard.color = new Cesium.Color(
                station.color.red,
                station.color.green,
                station.color.blue,
                opacity
            );
            
            this.animationFrames.set(station.id + '_pulse', 
                requestAnimationFrame(animate)
            );
        };
        
        this.animationFrames.set(station.id + '_pulse',
            requestAnimationFrame(animate)
        );
    }
    
    // 呼吸效果
    createBreathingEffect(station, options = {}) {
        const duration = options.duration || 3000;
        const minOpacity = options.minOpacity || 0.3;
        const maxOpacity = options.maxOpacity || 1.0;
        
        let startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = (elapsed % duration) / duration;
            
            // 使用余弦波创建平滑的呼吸效果
            const breathProgress = (Math.cos(progress * Math.PI * 2) + 1) / 2;
            const opacity = minOpacity + (maxOpacity - minOpacity) * breathProgress;
            
            station.billboard.color = new Cesium.Color(
                station.color.red,
                station.color.green,
                station.color.blue,
                opacity
            );
            
            this.animationFrames.set(station.id + '_breathing',
                requestAnimationFrame(animate)
            );
        };
        
        this.animationFrames.set(station.id + '_breathing',
            requestAnimationFrame(animate)
        );
    }
    
    // 涟漪效果
    createRippleEffect(station, options = {}) {
        const rippleCount = options.rippleCount || 3;
        const maxRadius = options.maxRadius || 50;
        const duration = options.duration || 2000;
        
        // 创建多个涟漪圆环
        for (let i = 0; i < rippleCount; i++) {
            setTimeout(() => {
                this.createSingleRipple(station, maxRadius, duration);
            }, i * (duration / rippleCount));
        }
    }
    
    createSingleRipple(station, maxRadius, duration) {
        const rippleEntity = this.viewer.entities.add({
            position: station.position,
            ellipse: {
                semiMajorAxis: 1,
                semiMinorAxis: 1,
                material: Cesium.Color.fromCssColorString(station.color).withAlpha(0.5),
                outline: true,
                outlineColor: Cesium.Color.fromCssColorString(station.color),
                heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
            }
        });
        
        // 涟漪扩散动画
        let startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = elapsed / duration;
            
            if (progress >= 1) {
                this.viewer.entities.remove(rippleEntity);
                return;
            }
            
            const radius = maxRadius * progress;
            const opacity = 1 - progress;
            
            rippleEntity.ellipse.semiMajorAxis = radius;
            rippleEntity.ellipse.semiMinorAxis = radius;
            rippleEntity.ellipse.material = Cesium.Color.fromCssColorString(station.color).withAlpha(opacity * 0.3);
            rippleEntity.ellipse.outlineColor = Cesium.Color.fromCssColorString(station.color).withAlpha(opacity);
            
            requestAnimationFrame(animate);
        };
        
        requestAnimationFrame(animate);
    }
    
    // 数据变化动画
    createDataChangeAnimation(station, oldValue, newValue) {
        const isIncrease = newValue > oldValue;
        const changePercent = Math.abs((newValue - oldValue) / oldValue);
        
        // 根据变化程度选择动画强度
        if (changePercent > 0.1) {
            this.createPulseEffect(station, {
                duration: 1000,
                maxScale: 1.3,
                minOpacity: 0.7
            });
        }
        
        // 颜色渐变表示变化方向
        const targetColor = isIncrease ? 
            Cesium.Color.fromCssColorString('#52c41a') : // 绿色表示增加
            Cesium.Color.fromCssColorString('#ff4d4f');  // 红色表示减少
        
        this.createColorTransition(station, station.color, targetColor, 800);
    }
    
    createColorTransition(station, fromColor, toColor, duration) {
        let startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentColor = Cesium.Color.lerp(
                fromColor,
                toColor,
                progress,
                new Cesium.Color()
            );
            
            station.billboard.color = currentColor;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                // 动画完成后恢复原色
                setTimeout(() => {
                    this.createColorTransition(station, currentColor, station.originalColor, 500);
                }, 1000);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    // 停止所有动画
    stopAllAnimations(stationId) {
        const animationKeys = ['_pulse', '_breathing', '_ripple', '_glow'];
        
        animationKeys.forEach(suffix => {
            const key = stationId + suffix;
            if (this.animationFrames.has(key)) {
                cancelAnimationFrame(this.animationFrames.get(key));
                this.animationFrames.delete(key);
            }
        });
    }
}
```

## 7.3.3 大规模监测点渲染优化

### LOD（细节层次）系统

针对大量监测点的分层次显示管理：

```javascript
class MonitoringPointLOD {
    constructor(viewer) {
        this.viewer = viewer;
        this.lodManager = new LODManager();
        this.visibilityManager = new VisibilityManager();
        this.clusteringManager = new ClusteringManager();
    }
    
    // LOD配置
    configureLODLevels() {
        return {
            // 远视角：聚类显示，只显示重要监测点
            far: {
                distanceRange: [50000, Infinity],
                strategy: 'clustering',
                maxVisiblePoints: 50,
                clustering: {
                    enabled: true,
                    pixelRange: 100,
                    minimumClusterSize: 2
                },
                iconSize: 8,
                showLabels: false,
                showOnlyImportant: true
            },
            
            // 中视角：简化显示，显示主要监测点
            medium: {
                distanceRange: [10000, 50000],
                strategy: 'selective',
                maxVisiblePoints: 200,
                clustering: {
                    enabled: true,
                    pixelRange: 50,
                    minimumClusterSize: 2
                },
                iconSize: 12,
                showLabels: false,
                filterByImportance: true
            },
            
            // 近视角：正常显示，显示所有监测点
            near: {
                distanceRange: [2000, 10000],
                strategy: 'normal',
                maxVisiblePoints: 500,
                clustering: {
                    enabled: false
                },
                iconSize: 16,
                showLabels: true,
                showDataValues: false
            },
            
            // 极近视角：详细显示，显示所有信息
            close: {
                distanceRange: [0, 2000],
                strategy: 'detailed',
                maxVisiblePoints: 1000,
                clustering: {
                    enabled: false
                },
                iconSize: 20,
                showLabels: true,
                showDataValues: true,
                showStatusDetails: true
            }
        };
    }
    
    // 动态LOD更新
    updateLOD(cameraPosition, allStations) {
        const lodLevels = this.configureLODLevels();
        const cameraHeight = this.calculateCameraHeight();
        const currentLODLevel = this.determineLODLevel(cameraHeight);
        
        // 根据LOD级别处理监测点显示
        this.processStationsForLOD(allStations, lodLevels[currentLODLevel]);
    }
    
    processStationsForLOD(stations, lodConfig) {
        // 预处理：距离计算和排序
        const cameraPosition = this.viewer.camera.position;
        const processedStations = stations.map(station => ({
            ...station,
            distance: Cesium.Cartesian3.distance(cameraPosition, station.position),
            importance: this.calculateStationImportance(station)
        })).sort((a, b) => a.distance - b.distance);
        
        // 应用LOD策略
        switch (lodConfig.strategy) {
            case 'clustering':
                this.applyClustering(processedStations, lodConfig);
                break;
            case 'selective':
                this.applySelectiveDisplay(processedStations, lodConfig);
                break;
            case 'normal':
                this.applyNormalDisplay(processedStations, lodConfig);
                break;
            case 'detailed':
                this.applyDetailedDisplay(processedStations, lodConfig);
                break;
        }
    }
    
    applyClustering(stations, config) {
        // 首先应用重要性过滤
        let visibleStations = config.showOnlyImportant ? 
            stations.filter(s => s.importance >= 0.7) : 
            stations;
        
        // 限制显示数量
        visibleStations = visibleStations.slice(0, config.maxVisiblePoints);
        
        // 执行聚类
        const clusters = this.clusteringManager.performClustering(visibleStations, config.clustering);
        
        // 渲染聚类结果
        this.renderClusters(clusters, config);
    }
    
    applySelectiveDisplay(stations, config) {
        // 基于重要性和距离的选择性显示
        const selectedStations = this.selectStationsByImportance(stations, config.maxVisiblePoints);
        
        // 应用聚类（如果启用）
        if (config.clustering.enabled) {
            const clusters = this.clusteringManager.performClustering(selectedStations, config.clustering);
            this.renderClusters(clusters, config);
        } else {
            this.renderIndividualStations(selectedStations, config);
        }
    }
    
    selectStationsByImportance(stations, maxCount) {
        // 计算综合得分（重要性 + 距离权重）
        const scored = stations.map(station => ({
            ...station,
            score: station.importance * 0.7 + (1 - station.distance / 100000) * 0.3
        }));
        
        // 排序并选择前N个
        return scored
            .sort((a, b) => b.score - a.score)
            .slice(0, maxCount);
    }
    
    calculateStationImportance(station) {
        let importance = 0.5; // 基础重要性
        
        // 根据监测点类型调整重要性
        const typeImportance = {
            'water_level': 0.9,
            'flow_rate': 0.8,
            'dam_safety': 1.0,
            'water_quality': 0.7,
            'rainfall': 0.6
        };
        
        importance += (typeImportance[station.type] || 0.5) * 0.3;
        
        // 根据状态调整重要性
        const statusImportance = {
            'alert': 1.0,
            'warning': 0.8,
            'normal': 0.3,
            'offline': 0.1
        };
        
        importance += (statusImportance[station.status] || 0.3) * 0.2;
        
        // 根据数据变化频率调整重要性
        if (station.dataChangeFrequency > 0.1) {
            importance += 0.1;
        }
        
        return Math.min(importance, 1.0);
    }
}
```

### 聚类算法优化

实现高效的监测点聚类显示：

```javascript
class OptimizedClustering {
    constructor() {
        this.clusterCache = new Map();
        this.spatialIndex = new SpatialIndex();
    }
    
    // 基于密度的聚类算法（DBSCAN改进版）
    performDBSCANClustering(stations, epsilon, minPoints) {
        const clusters = [];
        const visited = new Set();
        const clustered = new Set();
        
        // 构建空间索引以加速邻域查询
        this.spatialIndex.buildIndex(stations);
        
        stations.forEach(station => {
            if (visited.has(station.id)) return;
            
            visited.add(station.id);
            const neighbors = this.spatialIndex.getNeighbors(station.position, epsilon);
            
            if (neighbors.length < minPoints) {
                // 标记为噪音点
                station.cluster = 'noise';
            } else {
                // 创建新聚类
                const cluster = {
                    id: `cluster_${clusters.length}`,
                    stations: [],
                    center: null,
                    bounds: null
                };
                
                this.expandCluster(station, neighbors, cluster, epsilon, minPoints, visited, clustered);
                
                // 计算聚类中心和边界
                this.calculateClusterProperties(cluster);
                clusters.push(cluster);
            }
        });
        
        return clusters;
    }
    
    expandCluster(station, neighbors, cluster, epsilon, minPoints, visited, clustered) {
        cluster.stations.push(station);
        clustered.add(station.id);
        
        let i = 0;
        while (i < neighbors.length) {
            const neighbor = neighbors[i];
            
            if (!visited.has(neighbor.id)) {
                visited.add(neighbor.id);
                const neighborNeighbors = this.spatialIndex.getNeighbors(neighbor.position, epsilon);
                
                if (neighborNeighbors.length >= minPoints) {
                    neighbors.push(...neighborNeighbors.filter(n => !visited.has(n.id)));
                }
            }
            
            if (!clustered.has(neighbor.id)) {
                cluster.stations.push(neighbor);
                clustered.add(neighbor.id);
            }
            
            i++;
        }
    }
    
    // 层次聚类算法
    performHierarchicalClustering(stations, maxDistance) {
        let clusters = stations.map(station => ({
            id: station.id,
            stations: [station],
            center: station.position
        }));
        
        while (clusters.length > 1) {
            let minDistance = Infinity;
            let mergeIndices = [-1, -1];
            
            // 找到最近的两个聚类
            for (let i = 0; i < clusters.length; i++) {
                for (let j = i + 1; j < clusters.length; j++) {
                    const distance = Cesium.Cartesian3.distance(
                        clusters[i].center,
                        clusters[j].center
                    );
                    
                    if (distance < minDistance) {
                        minDistance = distance;
                        mergeIndices = [i, j];
                    }
                }
            }
            
            // 如果最近距离超过阈值，停止聚类
            if (minDistance > maxDistance) break;
            
            // 合并聚类
            const [i, j] = mergeIndices;
            const mergedCluster = {
                id: `merged_${clusters[i].id}_${clusters[j].id}`,
                stations: [...clusters[i].stations, ...clusters[j].stations],
                center: null
            };
            
            // 计算新的中心点
            mergedCluster.center = this.calculateClusterCenter(mergedCluster.stations);
            
            // 移除原聚类，添加合并后的聚类
            clusters.splice(Math.max(i, j), 1);
            clusters.splice(Math.min(i, j), 1);
            clusters.push(mergedCluster);
        }
        
        return clusters;
    }
    
    // 自适应聚类算法
    performAdaptiveClustering(stations, viewerDistance) {
        // 根据观察距离自适应调整聚类参数
        const adaptiveParams = this.calculateAdaptiveParameters(viewerDistance);
        
        // 选择合适的聚类算法
        if (stations.length > 1000) {
            return this.performGridBasedClustering(stations, adaptiveParams);
        } else if (stations.length > 100) {
            return this.performDBSCANClustering(
                stations, 
                adaptiveParams.epsilon, 
                adaptiveParams.minPoints
            );
        } else {
            return this.performHierarchicalClustering(
                stations, 
                adaptiveParams.maxDistance
            );
        }
    }
    
    // 基于网格的快速聚类
    performGridBasedClustering(stations, params) {
        const gridSize = params.gridSize || 1000; // 网格大小（米）
        const grid = new Map();
        
        // 将监测点分配到网格
        stations.forEach(station => {
            const gridKey = this.getGridKey(station.position, gridSize);
            
            if (!grid.has(gridKey)) {
                grid.set(gridKey, []);
            }
            
            grid.get(gridKey).push(station);
        });
        
        // 为每个非空网格创建聚类
        const clusters = [];
        grid.forEach((gridStations, gridKey) => {
            if (gridStations.length > 0) {
                const cluster = {
                    id: `grid_cluster_${gridKey}`,
                    stations: gridStations,
                    center: this.calculateClusterCenter(gridStations),
                    gridKey: gridKey
                };
                
                clusters.push(cluster);
            }
        });
        
        return clusters;
    }
    
    calculateAdaptiveParameters(viewerDistance) {
        // 根据视距计算聚类参数
        if (viewerDistance > 50000) {
            return {
                epsilon: 5000,
                minPoints: 3,
                maxDistance: 10000,
                gridSize: 5000
            };
        } else if (viewerDistance > 10000) {
            return {
                epsilon: 1000,
                minPoints: 2,
                maxDistance: 2000,
                gridSize: 1000
            };
        } else {
            return {
                epsilon: 500,
                minPoints: 2,
                maxDistance: 1000,
                gridSize: 500
            };
        }
    }
    
    getGridKey(position, gridSize) {
        const x = Math.floor(position.x / gridSize);
        const y = Math.floor(position.y / gridSize);
        const z = Math.floor(position.z / gridSize);
        return `${x}_${y}_${z}`;
    }
    
    calculateClusterCenter(stations) {
        const sum = stations.reduce((acc, station) => {
            return Cesium.Cartesian3.add(acc, station.position, acc);
        }, new Cesium.Cartesian3());
        
        return Cesium.Cartesian3.divideByScalar(
            sum, 
            stations.length, 
            new Cesium.Cartesian3()
        );
    }
}
```

## 7.3.4 本节小结

本节详细介绍了三维场景中监测点绘制的核心技术：

**空间定位技术**：
- 实现了精确的地理坐标到场景坐标的转换算法
- 提供了地形适配定位，确保监测点与地形的正确关系
- 支持多层次定位策略，适应不同类型的监测需求

**符号设计系统**：
- 建立了完整的分类符号体系，覆盖水文、气象、工程、水质等各类监测点
- 实现了动态视觉效果，包括脉冲、呼吸、涟漪等多种动画
- 提供了状态指示和数据变化的可视化表达

**渲染优化策略**：
- 实现了LOD（细节层次）系统，根据视距动态调整显示质量
- 开发了多种聚类算法，有效处理大规模监测点的显示问题
- 提供了自适应的性能优化方案

这些技术为智慧水利系统提供了高效、直观、可扩展的监测点可视化解决方案，确保在各种规模和场景下都能提供良好的用户体验。

## 思考题与练习

### 基础题

1. 解释地理坐标转换为三维场景坐标的基本原理，并说明地球曲率对转换精度的影响。
2. 分析不同LOD级别下监测点显示策略的设计原则，并说明各级别的适用场景。
3. 比较DBSCAN和层次聚类算法在监测点聚类中的优缺点。

### 提高题

4. 设计一个自适应的监测点重要性评估算法，考虑监测类型、状态、数据质量等多个因素。
5. 分析大规模监测点渲染的性能瓶颈，并提出针对性的优化方案。
6. 设计一个监测点符号的动态生成系统，支持用户自定义符号样式。

### 实践题

7. 实现一个基于WebGL的监测点批量渲染系统，支持10000+监测点的流畅显示。
8. 开发一个监测点聚类的可视化调试工具，帮助调优聚类参数。
9. 创建一个监测点状态变化的动画演示系统，展示不同类型的动态效果。

### 综合题

10. 设计并实现一个完整的智慧水利监测点管理系统，包括空间定位、符号管理、动态效果和性能优化等功能模块。