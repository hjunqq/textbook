# 第二节 水利工程三维场景设计

## 引言

水利工程三维场景设计是智慧水利平台可视化的核心组成部分，它将复杂的工程结构、地理环境和监测数据融合在一个直观的三维空间中。有效的三维场景设计不仅能够提供沉浸式的用户体验，更能支持工程管理、安全监测、应急响应等关键业务需求。

本节将以具体的水利工程项目为例，详细介绍三维场景设计的完整流程，包括需求分析、技术选型、建模方法、渲染优化和交互设计等关键环节。

## 8.2.1 项目需求分析与设计

### 典型项目案例：某大型水库三维可视化系统

#### 项目背景
某大型水库位于重要河流上游，承担防洪、供水、发电等多重功能。水库建设包括主坝、副坝、溢洪道、发电厂房等复杂工程结构，管理单位需要一个综合性的三维可视化平台来支持日常运行管理和安全监测。

#### 业务需求分析
```javascript
// 业务需求结构化分析
const businessRequirements = {
    // 核心功能需求
    core: {
        scene_visualization: {
            description: "全景三维场景展示",
            requirements: [
                "水库全貌鸟瞰视图",
                "工程结构细节展示", 
                "地形地貌真实还原",
                "水体动态效果"
            ],
            priority: "high"
        },
        
        monitoring_integration: {
            description: "监测数据集成展示",
            requirements: [
                "实时监测点位显示",
                "历史数据可视化",
                "异常状态预警",
                "数据趋势分析"
            ],
            priority: "high"
        },
        
        engineering_management: {
            description: "工程管理功能",
            requirements: [
                "设备状态监控",
                "维护计划管理",
                "安全评估展示",
                "运行参数分析"
            ],
            priority: "medium"
        }
    },
    
    // 技术需求
    technical: {
        performance: {
            frame_rate: "≥30fps",
            loading_time: "≤10s",
            concurrent_users: "≥50",
            data_update_interval: "≤5s"
        },
        
        compatibility: {
            browsers: ["Chrome", "Firefox", "Safari", "Edge"],
            devices: ["Desktop", "Tablet", "Mobile"],
            screen_resolutions: ["1920x1080", "2560x1440", "3840x2160"]
        },
        
        scalability: {
            scene_complexity: "支持百万级三角面片",
            data_volume: "TB级历史数据",
            concurrent_monitoring: "1000+监测点"
        }
    },
    
    // 用户体验需求
    user_experience: {
        interaction: {
            navigation: "平滑的场景漫游",
            selection: "直观的对象选择",
            information: "丰富的信息展示",
            customization: "个性化视图设置"
        },
        
        accessibility: {
            learning_curve: "低门槛上手",
            help_system: "在线帮助文档",
            error_handling: "友好的错误提示",
            multi_language: "中英文支持"
        }
    }
};
```

#### 技术架构设计
```javascript
class ReservoirVisualizationSystem {
    constructor(config) {
        this.config = config;
        this.architecture = this.designSystemArchitecture();
        this.components = this.initializeComponents();
    }
    
    designSystemArchitecture() {
        return {
            // 表现层
            presentation: {
                rendering_engine: "Cesium.js",
                ui_framework: "Vue.js + Element UI",
                chart_library: "ECharts",
                map_service: "Mapbox/高德地图"
            },
            
            // 业务逻辑层
            business: {
                scene_manager: "三维场景管理",
                data_processor: "数据处理引擎", 
                interaction_handler: "交互事件处理",
                animation_controller: "动画控制器"
            },
            
            // 数据访问层
            data: {
                spatial_data: "空间数据服务",
                monitoring_data: "监测数据API",
                model_assets: "模型资源管理",
                cache_layer: "缓存层"
            },
            
            // 基础设施层
            infrastructure: {
                web_server: "Nginx",
                application_server: "Node.js/Java",
                database: "PostgreSQL + InfluxDB",
                cdn: "静态资源CDN"
            }
        };
    }
    
    initializeComponents() {
        return {
            sceneManager: new SceneManager(this.config.scene),
            dataManager: new DataManager(this.config.data),
            interactionManager: new InteractionManager(this.config.interaction),
            uiManager: new UIManager(this.config.ui)
        };
    }
}
```

### 场景设计规划

#### 空间层次结构
```javascript
class SceneHierarchy {
    constructor() {
        this.levels = this.defineLevels();
        this.transitions = this.defineTransitions();
    }
    
    defineLevels() {
        return {
            // 宏观层：流域全景
            macro: {
                scale: "1:100000",
                coverage: "整个流域范围",
                elements: [
                    "流域边界",
                    "主要河流",
                    "水库位置", 
                    "城镇分布",
                    "交通网络"
                ],
                detail_level: "概要",
                view_distance: [50000, 200000]
            },
            
            // 中观层：水库全景
            meso: {
                scale: "1:10000", 
                coverage: "水库及周边区域",
                elements: [
                    "水库库区",
                    "主要建筑物",
                    "道路系统",
                    "地形地貌",
                    "植被覆盖"
                ],
                detail_level: "中等",
                view_distance: [5000, 50000]
            },
            
            // 微观层：工程细节
            micro: {
                scale: "1:1000",
                coverage: "具体工程结构",
                elements: [
                    "大坝结构",
                    "厂房设备", 
                    "监测设施",
                    "管道系统",
                    "安全设施"
                ],
                detail_level: "详细",
                view_distance: [10, 5000]
            },
            
            // 设备层：设备内部
            equipment: {
                scale: "1:10",
                coverage: "设备内部结构",
                elements: [
                    "机组部件",
                    "控制系统",
                    "传感器",
                    "维护接口"
                ],
                detail_level: "精细",
                view_distance: [1, 100]
            }
        };
    }
    
    defineTransitions() {
        return {
            zoom_based: {
                type: "基于距离的自动切换",
                implementation: this.createZoomBasedTransition.bind(this)
            },
            
            manual_selection: {
                type: "用户手动选择",
                implementation: this.createManualTransition.bind(this)
            },
            
            contextual: {
                type: "基于上下文的智能切换",
                implementation: this.createContextualTransition.bind(this)
            }
        };
    }
    
    createZoomBasedTransition(viewer) {
        viewer.camera.changed.addEventListener(() => {
            const distance = this.calculateCameraDistance(viewer);
            const targetLevel = this.determineLevelByDistance(distance);
            
            if (targetLevel !== this.currentLevel) {
                this.transitionToLevel(targetLevel);
            }
        });
    }
    
    transitionToLevel(targetLevel) {
        const transition = {
            from: this.currentLevel,
            to: targetLevel,
            duration: 1000,
            easing: 'easeInOutQuad'
        };
        
        this.executeTransition(transition);
        this.currentLevel = targetLevel;
    }
}
```

## 8.2.2 地形与环境建模

### 地形数据处理

#### DEM数据处理流程
```python
import rasterio
import numpy as np
from scipy import ndimage
import json

class TerrainProcessor:
    """地形数据处理器"""
    
    def __init__(self, dem_path, output_dir):
        self.dem_path = dem_path
        self.output_dir = output_dir
        self.tile_size = 1024  # 瓦片大小
        self.max_error = 15    # 最大误差（米）
        
    def process_dem_data(self):
        """处理DEM数据的完整流程"""
        # 1. 读取原始DEM数据
        with rasterio.open(self.dem_path) as src:
            elevation_data = src.read(1)
            transform = src.transform
            crs = src.crs
            
        # 2. 数据质量检查和修复
        cleaned_data = self.clean_elevation_data(elevation_data)
        
        # 3. 地形简化
        simplified_data = self.simplify_terrain(cleaned_data)
        
        # 4. 生成多级LOD
        lod_levels = self.generate_lod_levels(simplified_data)
        
        # 5. 切片处理
        tiles = self.create_terrain_tiles(lod_levels, transform, crs)
        
        # 6. 生成元数据
        metadata = self.generate_metadata(tiles, transform, crs)
        
        return {
            'tiles': tiles,
            'metadata': metadata,
            'lod_levels': len(lod_levels)
        }
    
    def clean_elevation_data(self, data):
        """清理高程数据"""
        # 处理无效值
        data = np.where(data < -1000, np.nan, data)  # 移除明显错误的负值
        data = np.where(data > 10000, np.nan, data)  # 移除明显错误的高值
        
        # 填补缺失值
        mask = np.isnan(data)
        if np.any(mask):
            # 使用距离加权插值填补
            from scipy.spatial.distance import cdist
            valid_points = np.column_stack(np.where(~mask))
            valid_values = data[~mask]
            
            missing_points = np.column_stack(np.where(mask))
            if len(missing_points) > 0 and len(valid_points) > 0:
                distances = cdist(missing_points, valid_points)
                weights = 1 / (distances + 1e-10)  # 避免除零
                weights /= weights.sum(axis=1, keepdims=True)
                
                interpolated_values = np.sum(weights * valid_values, axis=1)
                data[mask] = interpolated_values
        
        # 平滑滤波
        data = ndimage.gaussian_filter(data, sigma=1)
        
        return data
    
    def generate_lod_levels(self, data, levels=5):
        """生成多级LOD"""
        lod_data = [data]  # LOD 0 是原始数据
        
        current_data = data
        for level in range(1, levels):
            # 每级减少一半分辨率
            scale_factor = 2 ** level
            target_shape = (
                data.shape[0] // scale_factor,
                data.shape[1] // scale_factor
            )
            
            # 使用平均值下采样
            downsampled = self.downsample_terrain(current_data, target_shape)
            lod_data.append(downsampled)
            
        return lod_data
    
    def downsample_terrain(self, data, target_shape):
        """地形下采样"""
        h_factor = data.shape[0] / target_shape[0]
        w_factor = data.shape[1] / target_shape[1]
        
        # 创建目标数组
        downsampled = np.zeros(target_shape)
        
        for i in range(target_shape[0]):
            for j in range(target_shape[1]):
                # 计算源数据范围
                start_h = int(i * h_factor)
                end_h = int((i + 1) * h_factor)
                start_w = int(j * w_factor)
                end_w = int((j + 1) * w_factor)
                
                # 取平均值
                region = data[start_h:end_h, start_w:end_w]
                downsampled[i, j] = np.mean(region)
        
        return downsampled
    
    def create_terrain_tiles(self, lod_levels, transform, crs):
        """创建地形瓦片"""
        tiles = {}
        
        for level, data in enumerate(lod_levels):
            level_tiles = this.tile_data(data, level, transform, crs)
            tiles[level] = level_tiles
            
        return tiles
    
    def tile_data(self, data, level, transform, crs):
        """将数据切分为瓦片"""
        h, w = data.shape
        tiles = []
        
        tile_h = min(self.tile_size, h)
        tile_w = min(self.tile_size, w)
        
        for i in range(0, h, tile_h):
            for j in range(0, w, tile_w):
                # 提取瓦片数据
                tile_data = data[i:i+tile_h, j:j+tile_w]
                
                # 计算瓦片地理范围
                bounds = this.calculate_tile_bounds(i, j, tile_h, tile_w, transform)
                
                # 生成瓦片文件
                tile_info = this.save_tile(tile_data, level, i//tile_h, j//tile_w, bounds)
                tiles.append(tile_info)
                
        return tiles
    
    def save_tile(self, tile_data, level, row, col, bounds):
        """保存瓦片文件"""
        filename = f"terrain_L{level}_R{row}_C{col}.tif"
        filepath = os.path.join(this.output_dir, filename)
        
        # 保存为GeoTIFF
        with rasterio.open(
            filepath, 'w',
            driver='GTiff',
            height=tile_data.shape[0],
            width=tile_data.shape[1],
            count=1,
            dtype=tile_data.dtype,
            crs=bounds['crs'],
            transform=bounds['transform']
        ) as dst:
            dst.write(tile_data, 1)
        
        return {
            'level': level,
            'row': row, 
            'col': col,
            'filename': filename,
            'bounds': bounds,
            'size': tile_data.shape,
            'min_elevation': float(np.min(tile_data)),
            'max_elevation': float(np.max(tile_data))
        }
```

#### 地形网格生成
```javascript
class TerrainMeshGenerator {
    constructor(viewer) {
        this.viewer = viewer;
        this.terrainProvider = viewer.terrainProvider;
        this.meshCache = new Map();
    }
    
    async generateTerrainMesh(bounds, resolution) {
        const cacheKey = this.createCacheKey(bounds, resolution);
        
        if (this.meshCache.has(cacheKey)) {
            return this.meshCache.get(cacheKey);
        }
        
        // 创建采样点网格
        const samplingPoints = this.createSamplingGrid(bounds, resolution);
        
        // 获取高程数据
        const elevations = await this.sampleTerrainElevations(samplingPoints);
        
        // 生成三角网格
        const mesh = this.createTriangleMesh(elevations, bounds, resolution);
        
        // 优化网格
        const optimizedMesh = this.optimizeMesh(mesh);
        
        // 缓存结果
        this.meshCache.set(cacheKey, optimizedMesh);
        
        return optimizedMesh;
    }
    
    createSamplingGrid(bounds, resolution) {
        const points = [];
        const { west, south, east, north } = bounds;
        
        const lonStep = (east - west) / resolution;
        const latStep = (north - south) / resolution;
        
        for (let i = 0; i <= resolution; i++) {
            for (let j = 0; j <= resolution; j++) {
                const longitude = west + j * lonStep;
                const latitude = south + i * latStep;
                
                points.push(new Cesium.Cartographic(
                    Cesium.Math.toRadians(longitude),
                    Cesium.Math.toRadians(latitude)
                ));
            }
        }
        
        return points;
    }
    
    async sampleTerrainElevations(points) {
        // 使用Cesium的地形采样功能
        const sampledPoints = await Cesium.sampleTerrain(
            this.terrainProvider,
            15, // 地形细节级别
            points
        );
        
        return sampledPoints;
    }
    
    createTriangleMesh(points, bounds, resolution) {
        const vertices = [];
        const indices = [];
        const normals = [];
        const uvs = [];
        
        // 生成顶点
        points.forEach((point, index) => {
            const cartesian = Cesium.Cartographic.toCartesian(point);
            vertices.push(cartesian.x, cartesian.y, cartesian.z);
            
            // 计算UV坐标
            const row = Math.floor(index / (resolution + 1));
            const col = index % (resolution + 1);
            uvs.push(col / resolution, row / resolution);
        });
        
        // 生成三角形索引
        for (let i = 0; i < resolution; i++) {
            for (let j = 0; j < resolution; j++) {
                const topLeft = i * (resolution + 1) + j;
                const topRight = topLeft + 1;
                const bottomLeft = (i + 1) * (resolution + 1) + j;
                const bottomRight = bottomLeft + 1;
                
                // 第一个三角形
                indices.push(topLeft, bottomLeft, topRight);
                // 第二个三角形
                indices.push(topRight, bottomLeft, bottomRight);
            }
        }
        
        // 计算法向量
        this.calculateNormals(vertices, indices, normals);
        
        return {
            vertices: new Float32Array(vertices),
            indices: new Uint32Array(indices),
            normals: new Float32Array(normals),
            uvs: new Float32Array(uvs),
            bounds: bounds
        };
    }
    
    calculateNormals(vertices, indices, normals) {
        // 初始化法向量数组
        const vertexCount = vertices.length / 3;
        for (let i = 0; i < vertexCount * 3; i++) {
            normals[i] = 0;
        }
        
        // 计算每个三角形的法向量并累加到顶点
        for (let i = 0; i < indices.length; i += 3) {
            const i1 = indices[i] * 3;
            const i2 = indices[i + 1] * 3;
            const i3 = indices[i + 2] * 3;
            
            // 三角形的两条边
            const edge1 = [
                vertices[i2] - vertices[i1],
                vertices[i2 + 1] - vertices[i1 + 1],
                vertices[i2 + 2] - vertices[i1 + 2]
            ];
            
            const edge2 = [
                vertices[i3] - vertices[i1],
                vertices[i3 + 1] - vertices[i1 + 1],
                vertices[i3 + 2] - vertices[i1 + 2]
            ];
            
            // 计算叉积得到法向量
            const normal = [
                edge1[1] * edge2[2] - edge1[2] * edge2[1],
                edge1[2] * edge2[0] - edge1[0] * edge2[2],
                edge1[0] * edge2[1] - edge1[1] * edge2[0]
            ];
            
            // 累加到三个顶点
            [i1, i2, i3].forEach(idx => {
                normals[idx] += normal[0];
                normals[idx + 1] += normal[1];
                normals[idx + 2] += normal[2];
            });
        }
        
        // 归一化法向量
        for (let i = 0; i < normals.length; i += 3) {
            const length = Math.sqrt(
                normals[i] * normals[i] +
                normals[i + 1] * normals[i + 1] +
                normals[i + 2] * normals[i + 2]
            );
            
            if (length > 0) {
                normals[i] /= length;
                normals[i + 1] /= length;
                normals[i + 2] /= length;
            }
        }
    }
    
    optimizeMesh(mesh) {
        // 简化网格（减少不必要的顶点）
        const simplifiedMesh = this.simplifyMesh(mesh);
        
        // 优化顶点顺序（提高缓存效率）
        const optimizedMesh = this.optimizeVertexOrder(simplifiedMesh);
        
        return optimizedMesh;
    }
}
```

### 水体建模与动画

#### 水体几何建模
```javascript
class WaterBodyModeling {
    constructor(scene) {
        this.scene = scene;
        this.waterMaterial = this.createWaterMaterial();
        this.animationTime = 0;
    }
    
    createReservoirWater(waterLevel, reservoirBounds) {
        // 根据水位和库区边界创建水面
        const waterSurface = this.createWaterSurface(waterLevel, reservoirBounds);
        
        // 添加水体动画效果
        this.addWaterAnimation(waterSurface);
        
        // 设置水体属性
        this.configureWaterProperties(waterSurface);
        
        return waterSurface;
    }
    
    createWaterSurface(waterLevel, bounds) {
        const entity = this.scene.entities.add({
            id: 'reservoir_water',
            polygon: {
                hierarchy: this.createWaterBoundary(bounds),
                height: waterLevel,
                material: this.waterMaterial,
                outline: false,
                shadows: Cesium.ShadowMode.RECEIVE_ONLY
            }
        });
        
        return entity;
    }
    
    createWaterMaterial() {
        // 创建动态水体材质
        return new Cesium.Material({
            fabric: {
                type: 'Water',
                uniforms: {
                    baseWaterColor: new Cesium.Color(0.2, 0.3, 0.6, 1.0),
                    blendColor: new Cesium.Color(0.0, 0.2, 0.8, 1.0),
                    specularMap: '/assets/textures/water_specular.jpg',
                    normalMap: '/assets/textures/water_normal.jpg',
                    frequency: 1000.0,
                    animationSpeed: 0.01,
                    amplitude: 10.0,
                    specularIntensity: 0.5,
                    time: 0
                },
                source: this.getWaterShaderSource()
            }
        });
    }
    
    getWaterShaderSource() {
        return `
            czm_material czm_getMaterial(czm_materialInput materialInput) {
                czm_material material = czm_getDefaultMaterial(materialInput);
                
                float time = time * animationSpeed;
                vec2 st = materialInput.st;
                
                // 波纹效果
                vec2 wave1 = vec2(sin(time + st.s * frequency), cos(time + st.t * frequency));
                vec2 wave2 = vec2(cos(time * 0.7 + st.s * frequency * 0.8), sin(time * 0.9 + st.t * frequency * 1.2));
                
                vec2 distortion = (wave1 + wave2) * amplitude / 1000.0;
                vec2 distortedSt = st + distortion;
                
                // 采样法线贴图
                vec3 normalSample = texture2D(normalMap, distortedSt).xyz * 2.0 - 1.0;
                
                // 基础颜色混合
                vec3 color = mix(baseWaterColor.rgb, blendColor.rgb, 
                    sin(time + st.s * 10.0) * 0.5 + 0.5);
                
                // 高光效果
                float specular = pow(max(dot(normalSample, vec3(0.0, 0.0, 1.0)), 0.0), 32.0);
                color += specular * specularIntensity;
                
                material.diffuse = color;
                material.alpha = 0.8;
                material.normal = normalSample;
                material.specular = specularIntensity;
                
                return material;
            }
        `;
    }
    
    addWaterAnimation(waterEntity) {
        // 添加水位变化动画
        this.scene.preRender.addEventListener(() => {
            this.animationTime += 0.016; // 假设60FPS
            
            if (this.waterMaterial && this.waterMaterial.uniforms) {
                this.waterMaterial.uniforms.time = this.animationTime;
            }
        });
    }
    
    updateWaterLevel(newWaterLevel, animationDuration = 2000) {
        const waterEntity = this.scene.entities.getById('reservoir_water');
        if (!waterEntity) return;
        
        const currentHeight = waterEntity.polygon.height.getValue();
        const heightDifference = newWaterLevel - currentHeight;
        
        // 创建水位变化动画
        this.scene.tweens.create({
            duration: animationDuration,
            targets: { height: currentHeight },
            height: newWaterLevel,
            ease: 'Power2.easeInOut',
            onUpdate: function() {
                waterEntity.polygon.height = this.targets.height;
            },
            onComplete: () => {
                console.log(`水位已更新至 ${newWaterLevel}m`);
            }
        });
        
        // 触发水位变化事件
        this.onWaterLevelChange(newWaterLevel, heightDifference);
    }
    
    createWaterFlow(startPoint, endPoint, flowRate) {
        // 创建水流动画效果
        const flowPath = this.createFlowPath(startPoint, endPoint);
        const particles = this.createWaterParticles(flowPath, flowRate);
        
        return {
            path: flowPath,
            particles: particles,
            flowRate: flowRate
        };
    }
    
    createWaterParticles(path, flowRate) {
        // 创建粒子系统表示水流
        const particleSystem = this.scene.primitives.add(new Cesium.ParticleSystem({
            image: '/assets/textures/water_drop.png',
            startColor: new Cesium.Color(0.7, 0.8, 1.0, 1.0),
            endColor: new Cesium.Color(0.7, 0.8, 1.0, 0.0),
            startScale: 1.0,
            endScale: 2.0,
            minimumParticleLife: 1.0,
            maximumParticleLife: 3.0,
            minimumSpeed: flowRate * 0.5,
            maximumSpeed: flowRate * 1.5,
            imageSize: new Cesium.Cartesian2(10, 10),
            emissionRate: flowRate * 10,
            lifetime: 16.0,
            emitter: new Cesium.ConeEmitter(Cesium.Math.toRadians(15.0)),
            modelMatrix: this.calculateParticleMatrix(path.start),
            emitterModelMatrix: this.calculateEmitterMatrix(path)
        }));
        
        return particleSystem;
    }
}
```

## 8.2.3 工程结构建模

### 大坝建模

#### 参数化大坝生成
```javascript
class DamModeling {
    constructor(viewer) {
        this.viewer = viewer;
        this.damTypes = ['重力坝', '拱坝', '土石坝', '面板坝'];
        this.materials = this.initializeMaterials();
    }
    
    createParametricDam(parameters) {
        const { type, dimensions, position, materials } = parameters;
        
        switch (type) {
            case '重力坝':
                return this.createGravityDam(dimensions, position, materials);
            case '拱坝':
                return this.createArchDam(dimensions, position, materials);
            case '土石坝':
                return this.createEarthRockDam(dimensions, position, materials);
            default:
                throw new Error(`未支持的大坝类型: ${type}`);
        }
    }
    
    createGravityDam(dimensions, position, materials) {
        const { height, topWidth, bottomWidth, length } = dimensions;
        
        // 生成大坝横截面轮廓
        const profile = this.createGravityDamProfile(height, topWidth, bottomWidth);
        
        // 沿大坝轴线拉伸生成3D几何体
        const geometry = this.extrudeProfile(profile, length);
        
        // 创建大坝实体
        const damEntity = this.viewer.entities.add({
            id: 'gravity_dam',
            position: position,
            model: {
                uri: this.createDamModel(geometry, materials),
                scale: 1.0,
                minimumPixelSize: 100,
                maximumScale: 20000
            }
        });
        
        // 添加大坝详细信息
        this.addDamProperties(damEntity, dimensions, materials);
        
        return damEntity;
    }
    
    createGravityDamProfile(height, topWidth, bottomWidth) {
        // 重力坝典型梯形截面
        const profile = [
            { x: -topWidth / 2, y: height },      // 左上
            { x: topWidth / 2, y: height },       // 右上  
            { x: bottomWidth / 2, y: 0 },         // 右下
            { x: -bottomWidth / 2, y: 0 }         // 左下
        ];
        
        // 添加台阶和细节
        const steps = this.addDamSteps(profile, height);
        const detailed = this.addProfileDetails(steps);
        
        return detailed;
    }
    
    addDamSteps(baseProfile, height) {
        const stepCount = Math.floor(height / 20); // 每20米一个台阶
        const stepHeight = height / stepCount;
        const stepWidth = 1.5; // 台阶宽度
        
        const steppedProfile = [];
        
        for (let i = 0; i <= stepCount; i++) {
            const y = i * stepHeight;
            const widthRatio = 1 - (y / height) * 0.3; // 线性变化
            
            if (i < stepCount) {
                // 添加水平台阶
                steppedProfile.push({
                    x: -baseProfile[0].x * widthRatio - stepWidth,
                    y: y
                });
                steppedProfile.push({
                    x: -baseProfile[0].x * widthRatio,
                    y: y
                });
            }
            
            // 添加垂直面
            steppedProfile.push({
                x: -baseProfile[0].x * widthRatio,
                y: y + stepHeight
            });
        }
        
        return steppedProfile;
    }
    
    createArchDam(dimensions, position, materials) {
        const { height, crownThickness, radius, centralAngle } = dimensions;
        
        // 生成拱坝几何体
        const archGeometry = this.createArchGeometry(
            height, crownThickness, radius, centralAngle
        );
        
        // 创建拱坝实体
        const archDam = this.viewer.entities.add({
            id: 'arch_dam',
            position: position,
            model: {
                uri: this.createArchDamModel(archGeometry, materials),
                scale: 1.0
            }
        });
        
        return archDam;
    }
    
    createArchGeometry(height, thickness, radius, angle) {
        const segments = 32; // 弧段数量
        const layers = 20;   // 高度层数
        
        const vertices = [];
        const indices = [];
        
        // 生成拱坝顶点
        for (let layer = 0; layer <= layers; layer++) {
            const y = (layer / layers) * height;
            const currentRadius = radius * (1 + layer * 0.05); // 向下逐渐增大
            const currentThickness = thickness * (1 + layer * 0.1);
            
            for (let seg = 0; seg <= segments; seg++) {
                const theta = (seg / segments - 0.5) * angle;
                
                // 上游面
                const x1 = currentRadius * Math.sin(theta);
                const z1 = currentRadius * Math.cos(theta);
                vertices.push(x1, y, z1);
                
                // 下游面
                const x2 = (currentRadius + currentThickness) * Math.sin(theta);
                const z2 = (currentRadius + currentThickness) * Math.cos(theta);
                vertices.push(x2, y, z2);
            }
        }
        
        // 生成三角形索引
        this.generateArchDamIndices(indices, segments, layers);
        
        return {
            vertices: new Float32Array(vertices),
            indices: new Uint32Array(indices)
        };
    }
}
```

### 水电厂房建模

```javascript
class PowerhouseModeling {
    constructor(scene) {
        this.scene = scene;
        this.standardComponents = this.initializeStandardComponents();
    }
    
    createPowerhouse(config) {
        const { layout, equipment, structure } = config;
        
        // 创建主体结构
        const mainStructure = this.createMainStructure(structure);
        
        // 添加发电设备
        const generators = this.addGenerators(equipment.generators, layout);
        
        // 添加辅助设备
        const auxiliaryEquipment = this.addAuxiliaryEquipment(equipment.auxiliary);
        
        // 创建厂房组合
        const powerhouse = {
            id: 'powerhouse_complex',
            structure: mainStructure,
            equipment: {
                generators: generators,
                auxiliary: auxiliaryEquipment
            },
            systems: this.createSystemConnections(generators, auxiliaryEquipment)
        };
        
        return powerhouse;
    }
    
    createMainStructure(structure) {
        const { length, width, height, foundation } = structure;
        
        // 厂房主体框架
        const framework = this.scene.entities.add({
            id: 'powerhouse_framework',
            rectangle: {
                coordinates: this.calculateBounds(length, width),
                height: foundation.elevation,
                extrudedHeight: foundation.elevation + height,
                material: new Cesium.Color(0.8, 0.8, 0.8, 0.9),
                outline: true,
                outlineColor: Cesium.Color.BLACK
            }
        });
        
        // 厂房细节结构
        const details = this.addStructuralDetails(framework, structure);
        
        return {
            framework: framework,
            details: details
        };
    }
    
    addGenerators(generatorConfigs, layout) {
        const generators = [];
        
        generatorConfigs.forEach((config, index) => {
            const position = this.calculateGeneratorPosition(index, layout);
            const generator = this.createGenerator(config, position);
            generators.push(generator);
        });
        
        return generators;
    }
    
    createGenerator(config, position) {
        const { type, capacity, model } = config;
        
        // 水轮发电机组主体
        const turbineGenerator = this.scene.entities.add({
            id: `generator_${config.id}`,
            position: position,
            model: {
                uri: this.getGeneratorModelUri(type, model),
                scale: this.calculateGeneratorScale(capacity),
                minimumPixelSize: 50
            },
            label: {
                text: `${config.name}\n${capacity}MW`,
                font: '12pt sans-serif',
                fillColor: Cesium.Color.WHITE,
                outlineColor: Cesium.Color.BLACK,
                outlineWidth: 2,
                style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                pixelOffset: new Cesium.Cartesian2(0, -50)
            }
        });
        
        // 发电机组件
        const components = this.addGeneratorComponents(turbineGenerator, config);
        
        // 监测系统
        const monitoring = this.addGeneratorMonitoring(turbineGenerator, config);
        
        return {
            main: turbineGenerator,
            components: components,
            monitoring: monitoring,
            config: config
        };
    }
    
    addGeneratorComponents(mainUnit, config) {
        const components = {};
        
        // 水轮机
        components.turbine = this.scene.entities.add({
            id: `turbine_${config.id}`,
            position: mainUnit.position,
            model: {
                uri: '/assets/models/turbine.glb',
                scale: 0.8
            }
        });
        
        // 发电机
        components.generator = this.scene.entities.add({
            id: `generator_rotor_${config.id}`,
            position: mainUnit.position,
            model: {
                uri: '/assets/models/generator.glb',
                scale: 1.0
            }
        });
        
        // 变压器
        components.transformer = this.scene.entities.add({
            id: `transformer_${config.id}`,
            position: this.calculateTransformerPosition(mainUnit.position),
            model: {
                uri: '/assets/models/transformer.glb',
                scale: 0.6
            }
        });
        
        // 控制柜
        components.controlPanel = this.scene.entities.add({
            id: `control_${config.id}`,
            position: this.calculateControlPosition(mainUnit.position),
            model: {
                uri: '/assets/models/control_panel.glb',
                scale: 0.4
            }
        });
        
        return components;
    }
    
    addGeneratorMonitoring(generator, config) {
        const monitoringPoints = [];
        
        // 振动监测
        monitoringPoints.push(this.createMonitoringPoint({
            type: 'vibration',
            position: generator.position,
            parameters: ['振动幅值', '频率', '相位'],
            alertThresholds: config.monitoring.vibration
        }));
        
        // 温度监测
        monitoringPoints.push(this.createMonitoringPoint({
            type: 'temperature',
            position: generator.position,
            parameters: ['轴承温度', '绕组温度', '铁芯温度'],
            alertThresholds: config.monitoring.temperature
        }));
        
        // 电气监测
        monitoringPoints.push(this.createMonitoringPoint({
            type: 'electrical',
            position: generator.position,
            parameters: ['电压', '电流', '功率', '功率因数'],
            alertThresholds: config.monitoring.electrical
        }));
        
        return monitoringPoints;
    }
    
    createMonitoringPoint(config) {
        return this.scene.entities.add({
            id: `monitoring_${config.type}_${Date.now()}`,
            position: config.position,
            point: {
                pixelSize: 8,
                color: this.getMonitoringColor(config.type),
                outlineColor: Cesium.Color.WHITE,
                outlineWidth: 2,
                heightReference: Cesium.HeightReference.RELATIVE_TO_GROUND
            },
            properties: {
                monitoringType: config.type,
                parameters: config.parameters,
                thresholds: config.alertThresholds
            }
        });
    }
}
```

## 小结

水利工程三维场景设计是一个综合性的系统工程，需要结合业务需求、技术实现和用户体验等多个方面。通过科学的设计流程、先进的建模技术和优化的渲染方案，可以构建出功能完善、性能优良的三维可视化系统。

**关键要点总结**：

1. **需求分析**：深入理解业务需求，制定合理的技术架构和实现方案

2. **地形建模**：掌握地形数据处理、网格生成和优化技术

3. **工程建模**：实现参数化建模方法，支持复杂工程结构的精确表达

4. **性能优化**：采用LOD、缓存等技术手段保证系统流畅运行

在下一节中，我们将探讨监测数据处理与展示模块的设计与实现。



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
