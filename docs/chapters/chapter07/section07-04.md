# 7.4 监测点互动与拾取技术

## 学习目标
通过本节学习，学生应能够：
1. 掌握三维射线检测与对象拾取的核心原理
2. 理解用户交互设计模式和最佳实践
3. 熟练实现各种监测点交互功能
4. 能够优化触控设备的交互体验

## 引言

在智慧水利三维场景中，**监测点的互动与拾取技术**是实现用户与数据深度交互的关键技术。用户通过鼠标点击、触摸操作、悬停等方式与监测点进行交互，系统需要准确识别用户意图，提供相应的信息展示和操作功能。

良好的交互设计不仅能提升用户体验，更能帮助用户快速理解监测数据的含义和趋势。本节将深入探讨三维射线检测技术、交互事件处理、信息面板设计以及多设备适配等核心技术。

## 7.4.1 三维射线检测原理

### 射线投射算法

射线投射是三维场景中对象拾取的基础技术，通过从视点发射射线检测与场景对象的交点：

```javascript
class RaycastingSystem {
    constructor(viewer) {
        this.viewer = viewer;
        this.scene = viewer.scene;
        this.camera = viewer.camera;
        this.raycaster = new THREE.Raycaster();
        this.pickingResults = [];
    }
    
    // 屏幕坐标转射线
    screenToRay(screenPosition) {
        // 标准化设备坐标（NDC）
        const x = (screenPosition.x / this.viewer.canvas.clientWidth) * 2 - 1;
        const y = -(screenPosition.y / this.viewer.canvas.clientHeight) * 2 + 1;
        
        // 创建射线原点（相机位置）
        const rayOrigin = this.camera.position.clone();
        
        // 计算射线方向
        const rayDirection = new THREE.Vector3(x, y, -1);
        rayDirection.unproject(this.camera);
        rayDirection.sub(rayOrigin).normalize();
        
        return {
            origin: rayOrigin,
            direction: rayDirection
        };
    }
    
    // 执行射线检测
    performRaycast(screenPosition, targetObjects) {
        const ray = this.screenToRay(screenPosition);
        
        // 设置射线参数
        this.raycaster.set(ray.origin, ray.direction);
        
        // 执行相交检测
        const intersections = this.raycaster.intersectObjects(targetObjects, true);
        
        // 处理检测结果
        return this.processIntersections(intersections);
    }
    
    processIntersections(intersections) {
        const results = [];
        
        intersections.forEach((intersection, index) => {
            const result = {
                object: intersection.object,
                point: intersection.point,
                distance: intersection.distance,
                normal: intersection.face ? intersection.face.normal : null,
                uv: intersection.uv,
                index: index,
                priority: this.calculatePickingPriority(intersection.object)
            };
            
            results.push(result);
        });
        
        // 按优先级和距离排序
        return results.sort((a, b) => {
            if (a.priority !== b.priority) {
                return b.priority - a.priority; // 高优先级优先
            }
            return a.distance - b.distance; // 距离近的优先
        });
    }
    
    calculatePickingPriority(object) {
        // 根据对象类型设置拾取优先级
        if (object.userData.isMonitoringPoint) {
            return 100;
        }
        if (object.userData.isLabel) {
            return 90;
        }
        if (object.userData.isUIElement) {
            return 80;
        }
        if (object.userData.isTerrain) {
            return 10;
        }
        return 50; // 默认优先级
    }
    
    // 多层级拾取检测
    performMultiLevelPicking(screenPosition) {
        const layers = {
            ui: [],
            monitoring: [],
            terrain: [],
            other: []
        };
        
        const allResults = this.performRaycast(screenPosition, this.scene.children);
        
        // 将结果按类型分类
        allResults.forEach(result => {
            const object = result.object;
            if (object.userData.isUIElement) {
                layers.ui.push(result);
            } else if (object.userData.isMonitoringPoint) {
                layers.monitoring.push(result);
            } else if (object.userData.isTerrain) {
                layers.terrain.push(result);
            } else {
                layers.other.push(result);
            }
        });
        
        return layers;
    }
    
    // 精确拾取检测（像素级）
    performPrecisePicking(screenPosition, tolerance = 5) {
        const candidates = [];
        
        // 在指定容差范围内进行多次检测
        for (let dx = -tolerance; dx <= tolerance; dx++) {
            for (let dy = -tolerance; dy <= tolerance; dy++) {
                const testPosition = {
                    x: screenPosition.x + dx,
                    y: screenPosition.y + dy
                };
                
                const results = this.performRaycast(testPosition, this.getPickableObjects());
                candidates.push(...results);
            }
        }
        
        // 去重和排序
        const uniqueCandidates = this.removeDuplicates(candidates);
        return uniqueCandidates.sort((a, b) => a.distance - b.distance);
    }
    
    removeDuplicates(candidates) {
        const seen = new Set();
        return candidates.filter(candidate => {
            const key = candidate.object.uuid + '_' + candidate.distance.toFixed(6);
            if (seen.has(key)) {
                return false;
            }
            seen.add(key);
            return true;
        });
    }
}
```

### 碰撞检测优化

针对大量监测点的高效碰撞检测优化：

```javascript
class OptimizedCollisionDetection {
    constructor(viewer) {
        this.viewer = viewer;
        this.spatialIndex = new SpatialIndex();
        this.boundingBoxes = new Map();
        this.pickingCache = new Map();
        this.frustumCuller = new FrustumCuller();
    }
    
    // 构建空间索引
    buildSpatialIndex(monitoringPoints) {
        this.spatialIndex.clear();
        this.boundingBoxes.clear();
        
        monitoringPoints.forEach(point => {
            // 计算监测点的包围盒
            const boundingBox = this.calculateBoundingBox(point);
            this.boundingBoxes.set(point.id, boundingBox);
            
            // 添加到空间索引
            this.spatialIndex.insert(point.id, boundingBox);
        });
    }
    
    calculateBoundingBox(monitoringPoint) {
        const position = monitoringPoint.position;
        const size = monitoringPoint.size || 20; // 默认20像素
        
        // 转换为屏幕坐标
        const screenPos = this.worldToScreen(position);
        
        return {
            min: { x: screenPos.x - size/2, y: screenPos.y - size/2 },
            max: { x: screenPos.x + size/2, y: screenPos.y + size/2 },
            worldPosition: position,
            depth: screenPos.z
        };
    }
    
    // 快速碰撞检测
    fastCollisionDetection(screenPosition, searchRadius = 50) {
        // 定义搜索区域
        const searchBounds = {
            min: {
                x: screenPosition.x - searchRadius,
                y: screenPosition.y - searchRadius
            },
            max: {
                x: screenPosition.x + searchRadius,
                y: screenPosition.y + searchRadius
            }
        };
        
        // 使用空间索引快速查找候选对象
        const candidates = this.spatialIndex.query(searchBounds);
        
        // 精确碰撞检测
        const hits = [];
        candidates.forEach(candidateId => {
            const boundingBox = this.boundingBoxes.get(candidateId);
            if (this.pointInBoundingBox(screenPosition, boundingBox)) {
                hits.push({
                    id: candidateId,
                    boundingBox: boundingBox,
                    distance: this.calculateScreenDistance(screenPosition, boundingBox)
                });
            }
        });
        
        // 按距离排序
        return hits.sort((a, b) => a.distance - b.distance);
    }
    
    pointInBoundingBox(point, boundingBox) {
        return point.x >= boundingBox.min.x &&
               point.x <= boundingBox.max.x &&
               point.y >= boundingBox.min.y &&
               point.y <= boundingBox.max.y;
    }
    
    calculateScreenDistance(point, boundingBox) {
        const centerX = (boundingBox.min.x + boundingBox.max.x) / 2;
        const centerY = (boundingBox.min.y + boundingBox.max.y) / 2;
        
        const dx = point.x - centerX;
        const dy = point.y - centerY;
        
        return Math.sqrt(dx * dx + dy * dy);
    }
    
    // 视锥体裁剪
    performFrustumCulling(monitoringPoints) {
        const frustum = this.frustumCuller.getFrustum(this.viewer.camera);
        
        return monitoringPoints.filter(point => {
            return this.frustumCuller.isPointInFrustum(point.position, frustum);
        });
    }
    
    // 动态LOD碰撞检测
    performLODCollisionDetection(screenPosition) {
        const cameraDistance = this.getCameraDistance();
        
        if (cameraDistance > 50000) {
            // 远距离：只检测聚类对象
            return this.detectClusterCollision(screenPosition);
        } else if (cameraDistance > 10000) {
            // 中距离：检测重要监测点
            return this.detectImportantPointsCollision(screenPosition);
        } else {
            // 近距离：全精度检测
            return this.fastCollisionDetection(screenPosition);
        }
    }
    
    detectClusterCollision(screenPosition) {
        const clusters = this.getVisibleClusters();
        const hits = [];
        
        clusters.forEach(cluster => {
            const clusterBounds = this.calculateClusterBounds(cluster);
            if (this.pointInBoundingBox(screenPosition, clusterBounds)) {
                hits.push({
                    type: 'cluster',
                    id: cluster.id,
                    cluster: cluster,
                    distance: this.calculateScreenDistance(screenPosition, clusterBounds)
                });
            }
        });
        
        return hits;
    }
    
    // 缓存机制
    getCachedResult(cacheKey) {
        const cached = this.pickingCache.get(cacheKey);
        if (cached && (Date.now() - cached.timestamp) < 100) { // 100ms缓存
            return cached.result;
        }
        return null;
    }
    
    setCachedResult(cacheKey, result) {
        this.pickingCache.set(cacheKey, {
            result: result,
            timestamp: Date.now()
        });
        
        // 限制缓存大小
        if (this.pickingCache.size > 1000) {
            const oldestKey = this.pickingCache.keys().next().value;
            this.pickingCache.delete(oldestKey);
        }
    }
}
```

## 7.4.2 交互事件处理

### 多种交互事件支持

实现鼠标、触摸、键盘等多种输入方式的统一处理：

```javascript
class UnifiedInteractionHandler {
    constructor(viewer) {
        this.viewer = viewer;
        this.eventHandlers = new Map();
        this.interactionState = {
            isMouseDown: false,
            isDragging: false,
            startPosition: null,
            currentHover: null,
            selectedObjects: new Set(),
            multiSelectMode: false
        };
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const canvas = this.viewer.canvas;
        
        // 鼠标事件
        canvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
        canvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
        canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        canvas.addEventListener('wheel', this.handleMouseWheel.bind(this));
        canvas.addEventListener('contextmenu', this.handleContextMenu.bind(this));
        
        // 触摸事件
        canvas.addEventListener('touchstart', this.handleTouchStart.bind(this));
        canvas.addEventListener('touchmove', this.handleTouchMove.bind(this));
        canvas.addEventListener('touchend', this.handleTouchEnd.bind(this));
        
        // 键盘事件
        document.addEventListener('keydown', this.handleKeyDown.bind(this));
        document.addEventListener('keyup', this.handleKeyUp.bind(this));
        
        // 双击事件
        canvas.addEventListener('dblclick', this.handleDoubleClick.bind(this));
    }
    
    handleMouseDown(event) {
        this.interactionState.isMouseDown = true;
        this.interactionState.startPosition = {
            x: event.clientX,
            y: event.clientY
        };
        
        // 检测多选模式
        this.interactionState.multiSelectMode = event.ctrlKey || event.metaKey;
        
        const pickResult = this.performPicking(event);
        this.processPickingResult(pickResult, 'mousedown');
    }
    
    handleMouseUp(event) {
        this.interactionState.isMouseDown = false;
        
        if (!this.interactionState.isDragging) {
            // 单击事件
            const pickResult = this.performPicking(event);
            this.processClick(pickResult);
        }
        
        this.interactionState.isDragging = false;
    }
    
    handleMouseMove(event) {
        if (this.interactionState.isMouseDown) {
            const currentPosition = { x: event.clientX, y: event.clientY };
            const dragDistance = this.calculateDistance(
                this.interactionState.startPosition,
                currentPosition
            );
            
            if (dragDistance > 5) {
                this.interactionState.isDragging = true;
            }
        }
        
        // 悬停检测
        this.handleHover(event);
    }
    
    handleHover(event) {
        const pickResult = this.performPicking(event);
        const newHover = pickResult.length > 0 ? pickResult[0] : null;
        
        if (this.interactionState.currentHover !== newHover) {
            // 移除旧的悬停效果
            if (this.interactionState.currentHover) {
                this.triggerEvent('hover-exit', this.interactionState.currentHover);
            }
            
            // 应用新的悬停效果
            if (newHover) {
                this.triggerEvent('hover-enter', newHover);
            }
            
            this.interactionState.currentHover = newHover;
            this.updateCursor(newHover);
        }
    }
    
    handleDoubleClick(event) {
        const pickResult = this.performPicking(event);
        if (pickResult.length > 0) {
            this.triggerEvent('double-click', pickResult[0]);
        }
    }
    
    handleContextMenu(event) {
        event.preventDefault();
        
        const pickResult = this.performPicking(event);
        this.showContextMenu(event.clientX, event.clientY, pickResult);
    }
    
    // 触摸事件处理
    handleTouchStart(event) {
        event.preventDefault();
        
        const touches = Array.from(event.touches);
        
        if (touches.length === 1) {
            // 单点触摸
            this.handleSingleTouch(touches[0]);
        } else if (touches.length === 2) {
            // 双点触摸（缩放/旋转）
            this.handleMultiTouch(touches);
        }
    }
    
    handleSingleTouch(touch) {
        const mockEvent = {
            clientX: touch.clientX,
            clientY: touch.clientY
        };
        
        this.handleMouseDown(mockEvent);
        
        // 设置触摸超时，用于长按检测
        this.touchTimeout = setTimeout(() => {
            this.handleLongPress(touch);
        }, 500);
    }
    
    handleLongPress(touch) {
        const mockEvent = {
            clientX: touch.clientX,
            clientY: touch.clientY
        };
        
        this.handleContextMenu(mockEvent);
    }
    
    // 性能优化的拾取函数
    performPicking(event) {
        const screenPosition = {
            x: event.clientX,
            y: event.clientY
        };
        
        // 使用优化的碰撞检测
        return this.optimizedCollisionDetection.performLODCollisionDetection(screenPosition);
    }
    
    processClick(pickResult) {
        if (pickResult.length === 0) {
            // 点击空白区域
            if (!this.interactionState.multiSelectMode) {
                this.clearSelection();
            }
            return;
        }
        
        const topPick = pickResult[0];
        
        if (this.interactionState.multiSelectMode) {
            // 多选模式
            this.toggleSelection(topPick);
        } else {
            // 单选模式
            this.selectObject(topPick);
        }
        
        this.triggerEvent('click', topPick);
    }
    
    selectObject(pickResult) {
        this.clearSelection();
        this.interactionState.selectedObjects.add(pickResult.id);
        this.triggerEvent('selection-changed', Array.from(this.interactionState.selectedObjects));
    }
    
    toggleSelection(pickResult) {
        if (this.interactionState.selectedObjects.has(pickResult.id)) {
            this.interactionState.selectedObjects.delete(pickResult.id);
        } else {
            this.interactionState.selectedObjects.add(pickResult.id);
        }
        
        this.triggerEvent('selection-changed', Array.from(this.interactionState.selectedObjects));
    }
    
    clearSelection() {
        this.interactionState.selectedObjects.clear();
        this.triggerEvent('selection-changed', []);
    }
    
    // 事件管理
    on(eventType, handler) {
        if (!this.eventHandlers.has(eventType)) {
            this.eventHandlers.set(eventType, []);
        }
        this.eventHandlers.get(eventType).push(handler);
    }
    
    off(eventType, handler) {
        if (this.eventHandlers.has(eventType)) {
            const handlers = this.eventHandlers.get(eventType);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }
    
    triggerEvent(eventType, data) {
        if (this.eventHandlers.has(eventType)) {
            this.eventHandlers.get(eventType).forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`事件处理器错误 (${eventType}):`, error);
                }
            });
        }
    }
    
    updateCursor(hoverObject) {
        const canvas = this.viewer.canvas;
        
        if (hoverObject && hoverObject.type === 'monitoring-point') {
            canvas.style.cursor = 'pointer';
        } else if (hoverObject && hoverObject.type === 'cluster') {
            canvas.style.cursor = 'zoom-in';
        } else {
            canvas.style.cursor = 'default';
        }
    }
}
```

### 交互状态管理

管理复杂的交互状态和用户操作序列：

```javascript
class InteractionStateManager {
    constructor() {
        this.states = {
            idle: new IdleState(),
            selecting: new SelectingState(),
            dragging: new DraggingState(),
            measuring: new MeasuringState(),
            drawing: new DrawingState()
        };
        
        this.currentState = this.states.idle;
        this.stateHistory = [];
        this.maxHistorySize = 50;
        
        this.context = {
            selectedObjects: new Set(),
            hoverObject: null,
            tool: 'select',
            modifierKeys: {
                ctrl: false,
                shift: false,
                alt: false
            }
        };
    }
    
    // 状态转换
    transitionTo(stateName, ...args) {
        if (!this.states[stateName]) {
            console.error(`未知状态: ${stateName}`);
            return;
        }
        
        // 记录状态历史
        this.recordStateTransition(stateName);
        
        // 执行当前状态的退出逻辑
        this.currentState.exit(this.context);
        
        // 切换到新状态
        const previousState = this.currentState;
        this.currentState = this.states[stateName];
        
        // 执行新状态的进入逻辑
        this.currentState.enter(this.context, previousState, ...args);
    }
    
    // 处理输入事件
    handleInput(eventType, eventData) {
        const nextState = this.currentState.handleInput(eventType, eventData, this.context);
        
        if (nextState && nextState !== this.currentState.name) {
            this.transitionTo(nextState, eventData);
        }
    }
    
    // 更新上下文
    updateContext(updates) {
        Object.assign(this.context, updates);
        this.currentState.updateContext(this.context);
    }
    
    recordStateTransition(stateName) {
        this.stateHistory.push({
            from: this.currentState.name,
            to: stateName,
            timestamp: Date.now(),
            context: { ...this.context }
        });
        
        // 限制历史记录大小
        if (this.stateHistory.length > this.maxHistorySize) {
            this.stateHistory.shift();
        }
    }
}

// 状态基类
class InteractionState {
    constructor(name) {
        this.name = name;
    }
    
    enter(context, previousState, ...args) {
        // 进入状态时的初始化逻辑
    }
    
    exit(context) {
        // 离开状态时的清理逻辑
    }
    
    handleInput(eventType, eventData, context) {
        // 处理输入事件，返回下一个状态名称或null
        return null;
    }
    
    updateContext(context) {
        // 更新上下文信息
    }
}

// 具体状态实现
class SelectingState extends InteractionState {
    constructor() {
        super('selecting');
        this.selectionBox = null;
    }
    
    enter(context, previousState, startPosition) {
        this.startPosition = startPosition;
        this.createSelectionBox(startPosition);
    }
    
    exit(context) {
        this.destroySelectionBox();
    }
    
    handleInput(eventType, eventData, context) {
        switch (eventType) {
            case 'mousemove':
                this.updateSelectionBox(eventData.position);
                break;
                
            case 'mouseup':
                this.finishSelection(eventData, context);
                return 'idle';
                
            case 'keydown':
                if (eventData.key === 'Escape') {
                    return 'idle';
                }
                break;
        }
        
        return null;
    }
    
    createSelectionBox(startPosition) {
        this.selectionBox = document.createElement('div');
        this.selectionBox.className = 'selection-box';
        this.selectionBox.style.cssText = `
            position: absolute;
            border: 2px dashed #00BFFF;
            background: rgba(0, 191, 255, 0.1);
            pointer-events: none;
            z-index: 10000;
            left: ${startPosition.x}px;
            top: ${startPosition.y}px;
            width: 0;
            height: 0;
        `;
        
        document.body.appendChild(this.selectionBox);
    }
    
    updateSelectionBox(currentPosition) {
        if (!this.selectionBox) return;
        
        const left = Math.min(this.startPosition.x, currentPosition.x);
        const top = Math.min(this.startPosition.y, currentPosition.y);
        const width = Math.abs(currentPosition.x - this.startPosition.x);
        const height = Math.abs(currentPosition.y - this.startPosition.y);
        
        this.selectionBox.style.left = left + 'px';
        this.selectionBox.style.top = top + 'px';
        this.selectionBox.style.width = width + 'px';
        this.selectionBox.style.height = height + 'px';
    }
    
    finishSelection(eventData, context) {
        const selectionBounds = this.getSelectionBounds(eventData.position);
        const selectedObjects = this.findObjectsInBounds(selectionBounds);
        
        if (context.modifierKeys.ctrl) {
            // 添加到现有选择
            selectedObjects.forEach(obj => context.selectedObjects.add(obj.id));
        } else {
            // 替换选择
            context.selectedObjects.clear();
            selectedObjects.forEach(obj => context.selectedObjects.add(obj.id));
        }
    }
    
    destroySelectionBox() {
        if (this.selectionBox) {
            document.body.removeChild(this.selectionBox);
            this.selectionBox = null;
        }
    }
}
```

## 7.4.3 信息面板设计

### 动态信息面板

设计可适应不同监测点类型的动态信息展示面板：

```javascript
class DynamicInfoPanel {
    constructor(container) {
        this.container = container;
        this.currentPanel = null;
        this.panelTypes = new Map();
        this.animationQueue = [];
        
        this.initializePanelTypes();
        this.createPanelContainer();
    }
    
    initializePanelTypes() {
        // 水位监测站面板
        this.panelTypes.set('water_level', {
            template: 'water-level-panel',
            fields: [
                { key: 'currentLevel', label: '当前水位', unit: 'm', format: '0.2f' },
                { key: 'alertLevel', label: '警戒水位', unit: 'm', format: '0.2f' },
                { key: 'floodLevel', label: '洪水位', unit: 'm', format: '0.2f' },
                { key: 'lastUpdate', label: '更新时间', format: 'datetime' },
                { key: 'trend', label: '变化趋势', format: 'trend' },
                { key: 'status', label: '状态', format: 'status' }
            ],
            charts: ['trend-chart', 'level-gauge'],
            actions: ['详细数据', '历史趋势', '导出数据', '设置告警']
        });
        
        // 流量监测站面板
        this.panelTypes.set('flow_rate', {
            template: 'flow-rate-panel',
            fields: [
                { key: 'currentFlow', label: '当前流量', unit: 'm³/s', format: '0.2f' },
                { key: 'avgFlow', label: '平均流量', unit: 'm³/s', format: '0.2f' },
                { key: 'peakFlow', label: '峰值流量', unit: 'm³/s', format: '0.2f' },
                { key: 'velocity', label: '流速', unit: 'm/s', format: '0.2f' },
                { key: 'lastUpdate', label: '更新时间', format: 'datetime' }
            ],
            charts: ['flow-chart', 'velocity-chart'],
            actions: ['流量过程线', '流速分布', '输沙率', '设置告警']
        });
        
        // 降雨监测站面板
        this.panelTypes.set('rainfall', {
            template: 'rainfall-panel',
            fields: [
                { key: 'hourlyRain', label: '小时雨量', unit: 'mm', format: '0.1f' },
                { key: 'dailyRain', label: '日雨量', unit: 'mm', format: '0.1f' },
                { key: 'monthlyRain', label: '月雨量', unit: 'mm', format: '0.1f' },
                { key: 'intensity', label: '降雨强度', unit: 'mm/h', format: '0.1f' },
                { key: 'duration', label: '持续时间', unit: '小时', format: '0.0f' }
            ],
            charts: ['rainfall-histogram', 'intensity-chart'],
            actions: ['降雨过程', '强度分析', '频率分析', '预警设置']
        });
    }
    
    createPanelContainer() {
        const panelHTML = `
            <div class="info-panel-overlay" id="infoPanelOverlay">
                <div class="info-panel" id="infoPanel">
                    <div class="panel-header">
                        <h3 class="panel-title" id="panelTitle"></h3>
                        <div class="panel-controls">
                            <button class="pin-btn" id="pinBtn" title="固定面板">📌</button>
                            <button class="close-btn" id="closeBtn" title="关闭">✕</button>
                        </div>
                    </div>
                    <div class="panel-content" id="panelContent">
                        <!-- 动态内容 -->
                    </div>
                    <div class="panel-footer" id="panelFooter">
                        <!-- 操作按钮 -->
                    </div>
                </div>
            </div>
        `;
        
        this.container.innerHTML = panelHTML;
        this.bindEvents();
    }
    
    bindEvents() {
        const closeBtn = document.getElementById('closeBtn');
        const pinBtn = document.getElementById('pinBtn');
        const overlay = document.getElementById('infoPanelOverlay');
        
        closeBtn.addEventListener('click', () => this.hidePanel());
        pinBtn.addEventListener('click', () => this.togglePin());
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) this.hidePanel();
        });
    }
    
    showPanel(monitoringPoint, position) {
        const panelType = this.panelTypes.get(monitoringPoint.type);
        if (!panelType) {
            console.error(`未知的监测点类型: ${monitoringPoint.type}`);
            return;
        }
        
        this.currentPanel = {
            point: monitoringPoint,
            type: panelType,
            position: position,
            isPinned: false
        };
        
        this.updatePanelContent();
        this.positionPanel(position);
        this.animateIn();
    }
    
    updatePanelContent() {
        const { point, type } = this.currentPanel;
        
        // 更新标题
        document.getElementById('panelTitle').textContent = 
            `${point.name} - ${this.getStationTypeLabel(point.type)}`;
        
        // 更新内容
        this.updatePanelFields();
        this.updatePanelCharts();
        this.updatePanelActions();
    }
    
    updatePanelFields() {
        const { point, type } = this.currentPanel;
        const content = document.getElementById('panelContent');
        
        const fieldsHTML = `
            <div class="panel-section">
                <h4>基础信息</h4>
                <div class="info-grid">
                    ${type.fields.map(field => `
                        <div class="info-item">
                            <span class="info-label">${field.label}:</span>
                            <span class="info-value ${this.getValueClass(field.key, point)}">
                                ${this.formatValue(point.data[field.key], field)}
                            </span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        content.innerHTML = fieldsHTML;
    }
    
    updatePanelCharts() {
        const { point, type } = this.currentPanel;
        
        if (type.charts && type.charts.length > 0) {
            const chartsHTML = `
                <div class="panel-section">
                    <h4>数据图表</h4>
                    <div class="charts-container">
                        ${type.charts.map(chartType => `
                            <div class="chart-item" id="chart-${chartType}">
                                <div class="chart-loading">加载中...</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            
            document.getElementById('panelContent').innerHTML += chartsHTML;
            
            // 异步加载图表
            type.charts.forEach(chartType => {
                this.loadChart(chartType, point);
            });
        }
    }
    
    updatePanelActions() {
        const { type } = this.currentPanel;
        const footer = document.getElementById('panelFooter');
        
        if (type.actions && type.actions.length > 0) {
            const actionsHTML = `
                <div class="action-buttons">
                    ${type.actions.map((action, index) => `
                        <button class="action-btn" data-action="${action}">
                            ${action}
                        </button>
                    `).join('')}
                </div>
            `;
            
            footer.innerHTML = actionsHTML;
            
            // 绑定操作事件
            footer.addEventListener('click', (e) => {
                if (e.target.classList.contains('action-btn')) {
                    this.handleAction(e.target.dataset.action);
                }
            });
        }
    }
    
    formatValue(value, field) {
        if (value === null || value === undefined) {
            return '--';
        }
        
        switch (field.format) {
            case '0.1f':
                return value.toFixed(1) + (field.unit ? ' ' + field.unit : '');
            case '0.2f':
                return value.toFixed(2) + (field.unit ? ' ' + field.unit : '');
            case 'datetime':
                return new Date(value).toLocaleString();
            case 'trend':
                return this.formatTrend(value);
            case 'status':
                return this.formatStatus(value);
            default:
                return value.toString() + (field.unit ? ' ' + field.unit : '');
        }
    }
    
    formatTrend(trend) {
        const trendMap = {
            'rising': '↗️ 上升',
            'falling': '↘️ 下降',
            'stable': '→ 稳定',
            'fluctuating': '⚬ 波动'
        };
        return trendMap[trend] || trend;
    }
    
    formatStatus(status) {
        const statusMap = {
            'normal': '<span class="status-normal">●</span> 正常',
            'warning': '<span class="status-warning">●</span> 预警',
            'alert': '<span class="status-alert">●</span> 告警',
            'offline': '<span class="status-offline">●</span> 离线'
        };
        return statusMap[status] || status;
    }
    
    getValueClass(key, point) {
        // 根据数据值和阈值返回CSS类名
        if (key === 'currentLevel' && point.alertLevel) {
            if (point.data.currentLevel > point.data.alertLevel) {
                return 'value-warning';
            } else if (point.data.currentLevel > point.data.floodLevel) {
                return 'value-alert';
            }
        }
        
        return 'value-normal';
    }
    
    positionPanel(screenPosition) {
        const panel = document.getElementById('infoPanel');
        const overlay = document.getElementById('infoPanelOverlay');
        
        // 获取面板尺寸
        const panelRect = panel.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        let left = screenPosition.x + 10;
        let top = screenPosition.y - panelRect.height / 2;
        
        // 边界检查和调整
        if (left + panelRect.width > viewportWidth) {
            left = screenPosition.x - panelRect.width - 10;
        }
        
        if (top < 0) {
            top = 10;
        } else if (top + panelRect.height > viewportHeight) {
            top = viewportHeight - panelRect.height - 10;
        }
        
        panel.style.left = left + 'px';
        panel.style.top = top + 'px';
        
        overlay.style.display = 'block';
    }
    
    animateIn() {
        const panel = document.getElementById('infoPanel');
        
        panel.style.transform = 'scale(0.8) translateY(-10px)';
        panel.style.opacity = '0';
        
        // 触发动画
        requestAnimationFrame(() => {
            panel.style.transition = 'all 0.3s ease-out';
            panel.style.transform = 'scale(1) translateY(0)';
            panel.style.opacity = '1';
        });
    }
    
    hidePanel() {
        const overlay = document.getElementById('infoPanelOverlay');
        const panel = document.getElementById('infoPanel');
        
        panel.style.transition = 'all 0.2s ease-in';
        panel.style.transform = 'scale(0.8) translateY(-10px)';
        panel.style.opacity = '0';
        
        setTimeout(() => {
            overlay.style.display = 'none';
            this.currentPanel = null;
        }, 200);
    }
    
    loadChart(chartType, monitoringPoint) {
        // 异步加载并渲染图表
        setTimeout(() => {
            const chartContainer = document.getElementById(`chart-${chartType}`);
            if (chartContainer) {
                this.renderChart(chartType, monitoringPoint, chartContainer);
            }
        }, 500);
    }
    
    renderChart(chartType, point, container) {
        // 根据图表类型渲染相应的图表
        switch (chartType) {
            case 'trend-chart':
                this.renderTrendChart(point, container);
                break;
            case 'level-gauge':
                this.renderLevelGauge(point, container);
                break;
            case 'flow-chart':
                this.renderFlowChart(point, container);
                break;
            default:
                container.innerHTML = '<div class="chart-placeholder">暂无图表数据</div>';
        }
    }
    
    renderTrendChart(point, container) {
        // 使用Chart.js渲染趋势图
        const canvas = document.createElement('canvas');
        canvas.width = 280;
        canvas.height = 120;
        container.innerHTML = '';
        container.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: point.historicalData?.timestamps || [],
                datasets: [{
                    label: '水位',
                    data: point.historicalData?.values || [],
                    borderColor: '#00BFFF',
                    backgroundColor: 'rgba(0, 191, 255, 0.1)',
                    borderWidth: 2,
                    fill: true
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        display: false
                    },
                    y: {
                        beginAtZero: false
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}
```

## 7.4.4 触控设备优化

### 触摸交互适配

针对触摸设备的特殊交互优化：

```javascript
class TouchInteractionOptimizer {
    constructor(viewer) {
        this.viewer = viewer;
        this.touchState = {
            touches: [],
            gestureStartDistance: 0,
            gestureStartAngle: 0,
            lastTapTime: 0,
            lastTapPosition: null
        };
        
        this.setupTouchOptimizations();
    }
    
    setupTouchOptimizations() {
        const canvas = this.viewer.canvas;
        
        // 禁用默认的触摸行为
        canvas.style.touchAction = 'none';
        
        // 增大触摸目标
        this.enlargeTouchTargets();
        
        // 设置触摸反馈
        this.setupTouchFeedback();
        
        // 优化触摸事件处理
        this.optimizeTouchEvents();
    }
    
    enlargeTouchTargets() {
        // 为监测点添加更大的触摸区域
        const monitoringPoints = this.viewer.scene.monitoringPoints;
        
        monitoringPoints.forEach(point => {
            if (point.billboard) {
                // 增大触摸检测半径
                point.touchRadius = Math.max(point.billboard.scale * 20, 44); // 最小44px
                
                // 创建透明的触摸区域
                point.touchArea = this.createTouchArea(point);
            }
        });
    }
    
    createTouchArea(monitoringPoint) {
        return {
            center: monitoringPoint.position,
            radius: monitoringPoint.touchRadius,
            element: monitoringPoint,
            priority: monitoringPoint.importance || 1
        };
    }
    
    setupTouchFeedback() {
        // 创建触摸反馈系统
        this.feedbackSystem = {
            haptic: 'vibration' in navigator,
            visual: true,
            audio: false
        };
        
        // 预加载反馈资源
        this.preloadFeedbackAssets();
    }
    
    optimizeTouchEvents() {
        const canvas = this.viewer.canvas;
        
        // 使用passive事件监听器优化性能
        const passiveOptions = { passive: false };
        
        canvas.addEventListener('touchstart', this.handleTouchStart.bind(this), passiveOptions);
        canvas.addEventListener('touchmove', this.handleTouchMove.bind(this), passiveOptions);
        canvas.addEventListener('touchend', this.handleTouchEnd.bind(this), passiveOptions);
    }
    
    handleTouchStart(event) {
        event.preventDefault();
        
        const touches = Array.from(event.touches);
        this.touchState.touches = touches;
        
        if (touches.length === 1) {
            this.handleSingleTouchStart(touches[0]);
        } else if (touches.length === 2) {
            this.handleMultiTouchStart(touches);
        }
    }
    
    handleSingleTouchStart(touch) {
        const touchPosition = {
            x: touch.clientX,
            y: touch.clientY
        };
        
        // 检测双击
        const now = Date.now();
        const isDoubleTap = this.detectDoubleTap(touchPosition, now);
        
        if (isDoubleTap) {
            this.handleDoubleTap(touchPosition);
            return;
        }
        
        // 更新最后点击信息
        this.touchState.lastTapTime = now;
        this.touchState.lastTapPosition = touchPosition;
        
        // 开始长按检测
        this.startLongPressDetection(touchPosition);
        
        // 检测触摸目标
        this.detectTouchTarget(touchPosition);
    }
    
    detectDoubleTap(position, currentTime) {
        const doubleTapThreshold = 300; // 300ms
        const distanceThreshold = 50;   // 50px
        
        if (!this.touchState.lastTapTime || !this.touchState.lastTapPosition) {
            return false;
        }
        
        const timeDiff = currentTime - this.touchState.lastTapTime;
        const distance = this.calculateDistance(position, this.touchState.lastTapPosition);
        
        return timeDiff < doubleTapThreshold && distance < distanceThreshold;
    }
    
    handleDoubleTap(position) {
        // 双击缩放到目标
        const pickResult = this.performTouchPicking(position);
        
        if (pickResult.length > 0) {
            this.zoomToTarget(pickResult[0]);
        } else {
            // 双击空白区域，缩放到全景
            this.zoomToExtent();
        }
        
        this.provideTouchFeedback('success');
    }
    
    startLongPressDetection(position) {
        // 清除之前的长按定时器
        if (this.longPressTimer) {
            clearTimeout(this.longPressTimer);
        }
        
        this.longPressTimer = setTimeout(() => {
            this.handleLongPress(position);
        }, 500); // 500ms长按阈值
    }
    
    handleLongPress(position) {
        const pickResult = this.performTouchPicking(position);
        
        if (pickResult.length > 0) {
            // 显示上下文菜单
            this.showTouchContextMenu(pickResult[0], position);
        }
        
        this.provideTouchFeedback('longPress');
    }
    
    performTouchPicking(position) {
        const enlargedRadius = 25; // 扩大触摸检测半径
        const candidates = [];
        
        // 在扩大的区域内查找触摸目标
        for (let dx = -enlargedRadius; dx <= enlargedRadius; dx += 5) {
            for (let dy = -enlargedRadius; dy <= enlargedRadius; dy += 5) {
                const testPosition = {
                    x: position.x + dx,
                    y: position.y + dy
                };
                
                const results = this.collisionDetection.fastCollisionDetection(testPosition);
                candidates.push(...results);
            }
        }
        
        // 去重并按距离排序
        return this.deduplicateAndSort(candidates, position);
    }
    
    deduplicateAndSort(candidates, touchPosition) {
        const unique = new Map();
        
        candidates.forEach(candidate => {
            const key = candidate.id;
            if (!unique.has(key) || unique.get(key).distance > candidate.distance) {
                unique.set(key, candidate);
            }
        });
        
        return Array.from(unique.values()).sort((a, b) => a.distance - b.distance);
    }
    
    showTouchContextMenu(target, position) {
        const menuItems = this.generateContextMenuItems(target);
        
        // 创建触摸友好的上下文菜单
        const menu = document.createElement('div');
        menu.className = 'touch-context-menu';
        menu.innerHTML = `
            <div class="menu-backdrop"></div>
            <div class="menu-panel">
                <div class="menu-header">
                    <h4>${target.name || '操作菜单'}</h4>
                    <button class="menu-close">✕</button>
                </div>
                <div class="menu-items">
                    ${menuItems.map(item => `
                        <button class="menu-item" data-action="${item.action}">
                            <span class="menu-icon">${item.icon}</span>
                            <span class="menu-text">${item.text}</span>
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
        
        // 定位菜单
        this.positionTouchMenu(menu, position);
        
        // 添加到页面
        document.body.appendChild(menu);
        
        // 绑定事件
        this.bindTouchMenuEvents(menu, target);
    }
    
    generateContextMenuItems(target) {
        const baseItems = [
            { action: 'info', icon: 'ℹ️', text: '详细信息' },
            { action: 'trend', icon: '📈', text: '查看趋势' },
            { action: 'export', icon: '💾', text: '导出数据' }
        ];
        
        if (target.type === 'monitoring-point') {
            baseItems.push({ action: 'alert', icon: '🔔', text: '设置告警' });
        }
        
        if (target.type === 'cluster') {
            baseItems.push({ action: 'expand', icon: '🔍', text: '展开聚类' });
        }
        
        return baseItems;
    }
    
    provideTouchFeedback(type) {
        // 触觉反馈
        if (this.feedbackSystem.haptic && navigator.vibrate) {
            switch (type) {
                case 'tap':
                    navigator.vibrate(10);
                    break;
                case 'longPress':
                    navigator.vibrate([10, 50, 10]);
                    break;
                case 'success':
                    navigator.vibrate([10, 30, 10]);
                    break;
                case 'error':
                    navigator.vibrate([100, 50, 100]);
                    break;
            }
        }
        
        // 视觉反馈
        if (this.feedbackSystem.visual) {
            this.showVisualFeedback(type);
        }
    }
    
    showVisualFeedback(type) {
        const feedback = document.createElement('div');
        feedback.className = `touch-feedback touch-feedback-${type}`;
        
        switch (type) {
            case 'tap':
                feedback.innerHTML = '👆';
                break;
            case 'longPress':
                feedback.innerHTML = '⏳';
                break;
            case 'success':
                feedback.innerHTML = '✅';
                break;
            case 'error':
                feedback.innerHTML = '❌';
                break;
        }
        
        document.body.appendChild(feedback);
        
        // 动画显示
        setTimeout(() => {
            feedback.classList.add('show');
        }, 10);
        
        // 自动移除
        setTimeout(() => {
            feedback.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(feedback);
            }, 300);
        }, 1000);
    }
    
    calculateDistance(point1, point2) {
        const dx = point1.x - point2.x;
        const dy = point1.y - point2.y;
        return Math.sqrt(dx * dx + dy * dy);
    }
}
```

## 7.4.5 本节小结

本节全面介绍了监测点互动与拾取技术的核心内容：

**射线检测技术**：
- 详细阐述了三维射线投射算法的原理和实现
- 提供了多种碰撞检测优化策略，提升大规模场景的检测性能
- 实现了多层级拾取和精确检测机制

**交互事件处理**：
- 建立了统一的多输入设备事件处理框架
- 设计了灵活的交互状态管理系统
- 支持复杂的用户操作序列和状态转换

**信息面板设计**：
- 创建了动态适应不同监测点类型的信息展示面板
- 实现了丰富的数据格式化和可视化功能
- 提供了流畅的面板动画和交互体验

**触控优化**：
- 专门针对触摸设备进行了交互优化
- 增强了触摸目标检测的准确性和容错性
- 集成了多种触摸反馈机制，提升用户体验

这些技术确保了智慧水利三维场景中监测点交互的流畅性和准确性，为用户提供了直观、高效的数据探索和分析工具。

## 思考题与练习

### 基础题

1. 解释三维射线投射算法的基本原理，并说明其在对象拾取中的作用机制。
2. 分析触摸设备与鼠标设备在交互设计上的主要差异和相应的适配策略。
3. 简述动态信息面板的设计原则和实现要点。

### 提高题

4. 设计一个高效的大规模监测点碰撞检测算法，考虑性能优化和准确性平衡。
5. 分析多种交互状态管理的优缺点，并提出适合复杂三维场景的状态管理方案。
6. 设计一个自适应的信息面板系统，能够根据不同监测点类型动态调整展示内容。

### 实践题

7. 实现一个支持多点触控的手势识别系统，包括缩放、旋转、平移等操作。
8. 开发一个智能的上下文菜单系统，能够根据选中对象的类型和状态动态生成菜单项。
9. 创建一个高性能的批量对象拾取系统，支持框选、圈选等多种选择方式。

### 综合题

10. 设计并实现一个完整的三维场景交互框架，集成射线检测、事件处理、信息展示和触控优化等所有功能模块。