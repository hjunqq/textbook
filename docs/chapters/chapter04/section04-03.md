## 4.1.3 多媒体元素与Canvas API

HTML5在多媒体支持方面实现了革命性突破，原生支持音频、视频播放和图形绘制，彻底改变了Web平台的内容表现能力[7]。传统Web页面依赖Flash、Silverlight等第三方插件来实现多媒体功能，存在安全性差、性能低下、跨平台兼容性问题等诸多弊端。HTML5多媒体元素的引入，标志着Web平台向原生多媒体时代的跃迁，为智慧水利平台的可视化展示、实时监控、数据分析等功能提供了强大的技术支撑[8]。

在智慧水利系统中，多媒体元素具有重要的应用价值。视频元素可用于展示水利工程实况、培训教学内容、应急演练录像等；音频元素可用于预警提醒、语音播报、会议记录等；Canvas元素则为数据可视化、工程图纸绘制、交互式地图等功能提供了无限可能。这些技术的有机结合，能够构建出功能丰富、交互性强的现代化水利管理平台。

### HTML5视频元素

video元素是HTML5最重要的多媒体特性之一，它提供了标准化的视频播放解决方案，支持多种视频格式，具有丰富的API接口和自定义能力[9]。

#### 基础视频播放

```html
<section class="monitoring-video">
    <h2>大坝实时监控视频</h2>
    
    <video id="damMonitorVideo" 
           width="800" 
           height="600" 
           controls 
           preload="metadata"
           poster="assets/images/dam-poster.jpg">
        
        <!-- 多格式支持 -->
        <source src="videos/dam-monitor-hd.mp4" type="video/mp4">
        <source src="videos/dam-monitor-hd.webm" type="video/webm">
        <source src="videos/dam-monitor-hd.ogv" type="video/ogg">
        
        <!-- 字幕支持 -->
        <track kind="captions" 
               src="captions/dam-monitor-zh.vtt" 
               srclang="zh" 
               label="中文字幕"
               default>
        <track kind="captions" 
               src="captions/dam-monitor-en.vtt" 
               srclang="en" 
               label="English Subtitles">
        
        <!-- 降级内容 -->
        <p>您的浏览器不支持视频播放功能，请 
           <a href="videos/dam-monitor-hd.mp4">下载视频</a> 观看。
        </p>
    </video>
    
    <div class="video-info">
        <p>拍摄时间：<time datetime="2024-03-15T14:30:00+08:00">2024年3月15日 14:30</time></p>
        <p>拍摄位置：三峡大坝观景台</p>
        <p>视频分辨率：1920×1080 | 编码：H.264</p>
    </div>
</section>
```

video元素的主要属性包括：

| 属性 | 说明 | 示例值 |
|------|------|--------|
| `src` | 视频文件URL | "video.mp4" |
| `controls` | 显示播放控件 | 布尔属性 |
| `autoplay` | 自动播放 | 布尔属性 |
| `loop` | 循环播放 | 布尔属性 |
| `muted` | 静音播放 | 布尔属性 |
| `preload` | 预加载策略 | "none"/"metadata"/"auto" |
| `poster` | 封面图片 | "poster.jpg" |
| `width/height` | 尺寸 | 数值 |

#### 自定义视频播放器

为了更好地适应智慧水利平台的设计需求，通常需要开发自定义的视频播放器：

```html
<div class="custom-video-player">
    <video id="customVideo" 
           width="800" 
           height="450"
           preload="metadata"
           poster="assets/images/water-level-poster.jpg">
        <source src="videos/water-level-monitoring.mp4" type="video/mp4">
        <source src="videos/water-level-monitoring.webm" type="video/webm">
    </video>
    
    <div class="video-controls">
        <button id="playPauseBtn" class="control-btn" aria-label="播放/暂停">
            <span class="play-icon">▶</span>
            <span class="pause-icon" hidden>⏸</span>
        </button>
        
        <div class="progress-container">
            <input type="range" 
                   id="progressBar" 
                   min="0" 
                   max="100" 
                   value="0"
                   class="progress-bar"
                   aria-label="播放进度">
            <div class="progress-time">
                <span id="currentTime">0:00</span> / 
                <span id="duration">0:00</span>
            </div>
        </div>
        
        <div class="volume-container">
            <button id="muteBtn" class="control-btn" aria-label="静音">🔊</button>
            <input type="range" 
                   id="volumeBar" 
                   min="0" 
                   max="100" 
                   value="100"
                   class="volume-bar"
                   aria-label="音量控制">
        </div>
        
        <button id="fullscreenBtn" class="control-btn" aria-label="全屏">⛶</button>
    </div>
</div>

<script>
class CustomVideoPlayer {
    constructor(containerId) {
        this.container = document.querySelector(containerId);
        this.video = this.container.querySelector('video');
        this.playPauseBtn = this.container.querySelector('#playPauseBtn');
        this.progressBar = this.container.querySelector('#progressBar');
        this.currentTimeSpan = this.container.querySelector('#currentTime');
        this.durationSpan = this.container.querySelector('#duration');
        this.muteBtn = this.container.querySelector('#muteBtn');
        this.volumeBar = this.container.querySelector('#volumeBar');
        this.fullscreenBtn = this.container.querySelector('#fullscreenBtn');
        
        this.initializeEvents();
    }
    
    initializeEvents() {
        // 播放/暂停控制
        this.playPauseBtn.addEventListener('click', () => {
            if (this.video.paused) {
                this.video.play();
            } else {
                this.video.pause();
            }
        });
        
        // 视频状态变化
        this.video.addEventListener('play', () => {
            this.updatePlayPauseButton(false);
        });
        
        this.video.addEventListener('pause', () => {
            this.updatePlayPauseButton(true);
        });
        
        // 时间更新
        this.video.addEventListener('timeupdate', () => {
            this.updateProgress();
        });
        
        // 元数据加载完成
        this.video.addEventListener('loadedmetadata', () => {
            this.durationSpan.textContent = this.formatTime(this.video.duration);
            this.progressBar.max = this.video.duration;
        });
        
        // 进度条控制
        this.progressBar.addEventListener('input', () => {
            this.video.currentTime = this.progressBar.value;
        });
        
        // 音量控制
        this.volumeBar.addEventListener('input', () => {
            this.video.volume = this.volumeBar.value / 100;
            this.updateMuteButton();
        });
        
        // 静音控制
        this.muteBtn.addEventListener('click', () => {
            this.video.muted = !this.video.muted;
            this.updateMuteButton();
        });
        
        // 全屏控制
        this.fullscreenBtn.addEventListener('click', () => {
            this.toggleFullscreen();
        });
        
        // 键盘控制
        this.container.addEventListener('keydown', (e) => {
            this.handleKeyboard(e);
        });
    }
    
    updatePlayPauseButton(paused) {
        const playIcon = this.playPauseBtn.querySelector('.play-icon');
        const pauseIcon = this.playPauseBtn.querySelector('.pause-icon');
        
        if (paused) {
            playIcon.removeAttribute('hidden');
            pauseIcon.setAttribute('hidden', '');
        } else {
            playIcon.setAttribute('hidden', '');
            pauseIcon.removeAttribute('hidden');
        }
    }
    
    updateProgress() {
        const current = this.video.currentTime;
        this.progressBar.value = current;
        this.currentTimeSpan.textContent = this.formatTime(current);
    }
    
    updateMuteButton() {
        if (this.video.muted || this.video.volume === 0) {
            this.muteBtn.textContent = '🔇';
            this.volumeBar.value = 0;
        } else {
            this.muteBtn.textContent = '🔊';
            this.volumeBar.value = this.video.volume * 100;
        }
    }
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            this.container.requestFullscreen().catch(err => {
                console.error('无法进入全屏模式:', err);
            });
        } else {
            document.exitFullscreen();
        }
    }
    
    handleKeyboard(e) {
        switch(e.code) {
            case 'Space':
                e.preventDefault();
                this.playPauseBtn.click();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                this.video.currentTime = Math.max(0, this.video.currentTime - 10);
                break;
            case 'ArrowRight':
                e.preventDefault();
                this.video.currentTime = Math.min(
                    this.video.duration, 
                    this.video.currentTime + 10
                );
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.video.volume = Math.min(1, this.video.volume + 0.1);
                this.updateMuteButton();
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.video.volume = Math.max(0, this.video.volume - 0.1);
                this.updateMuteButton();
                break;
        }
    }
}

// 初始化播放器
document.addEventListener('DOMContentLoaded', () => {
    new CustomVideoPlayer('.custom-video-player');
});
</script>
```

### HTML5音频元素

audio元素为Web页面提供了原生的音频播放能力，在智慧水利平台中可用于预警提醒、语音播报、会议录音等场景。

#### 基础音频功能

```html
<section class="audio-alerts">
    <h2>预警音频系统</h2>
    
    <!-- 背景音频 -->
    <audio id="backgroundAudio" 
           loop 
           preload="auto"
           volume="0.3">
        <source src="audio/water-ambient.mp3" type="audio/mpeg">
        <source src="audio/water-ambient.ogg" type="audio/ogg">
        <p>您的浏览器不支持音频播放</p>
    </audio>
    
    <!-- 预警音频 -->
    <div class="alert-sounds">
        <h3>预警音效</h3>
        
        <div class="sound-item">
            <span>一般预警：</span>
            <audio controls preload="none">
                <source src="audio/alert-level1.mp3" type="audio/mpeg">
                <source src="audio/alert-level1.wav" type="audio/wav">
            </audio>
        </div>
        
        <div class="sound-item">
            <span>严重预警：</span>
            <audio controls preload="none">
                <source src="audio/alert-level2.mp3" type="audio/mpeg">
                <source src="audio/alert-level2.wav" type="audio/wav">
            </audio>
        </div>
        
        <div class="sound-item">
            <span>紧急预警：</span>
            <audio controls preload="none">
                <source src="audio/alert-emergency.mp3" type="audio/mpeg">
                <source src="audio/alert-emergency.wav" type="audio/wav">
            </audio>
        </div>
    </div>
</section>
```

#### 音频API应用

```javascript
class AudioAlertSystem {
    constructor() {
        this.audioContext = null;
        this.alertSounds = new Map();
        this.isInitialized = false;
        
        this.initializeAudioSystem();
    }
    
    async initializeAudioSystem() {
        try {
            // 创建音频上下文
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // 加载预警音效
            await this.loadAlertSounds();
            
            this.isInitialized = true;
            console.log('音频预警系统初始化完成');
        } catch (error) {
            console.error('音频系统初始化失败:', error);
        }
    }
    
    async loadAlertSounds() {
        const soundFiles = [
            { level: 'normal', url: 'audio/alert-level1.mp3' },
            { level: 'warning', url: 'audio/alert-level2.mp3' },
            { level: 'emergency', url: 'audio/alert-emergency.mp3' }
        ];
        
        for (const sound of soundFiles) {
            try {
                const audioBuffer = await this.loadAudioFile(sound.url);
                this.alertSounds.set(sound.level, audioBuffer);
            } catch (error) {
                console.error(`加载音频文件 ${sound.url} 失败:`, error);
            }
        }
    }
    
    async loadAudioFile(url) {
        const response = await fetch(url);
        const arrayBuffer = await response.arrayBuffer();
        return await this.audioContext.decodeAudioData(arrayBuffer);
    }
    
    playAlert(level, repeat = 1) {
        if (!this.isInitialized || !this.alertSounds.has(level)) {
            console.warn(`无法播放预警音效: ${level}`);
            return;
        }
        
        const audioBuffer = this.alertSounds.get(level);
        
        for (let i = 0; i < repeat; i++) {
            setTimeout(() => {
                this.playSound(audioBuffer);
            }, i * (audioBuffer.duration * 1000 + 500)); // 间隔500ms
        }
    }
    
    playSound(audioBuffer) {
        const source = this.audioContext.createBufferSource();
        const gainNode = this.audioContext.createGain();
        
        source.buffer = audioBuffer;
        source.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        // 设置音量淡入效果
        gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.8, this.audioContext.currentTime + 0.1);
        gainNode.gain.linearRampToValueAtTime(0, this.audioContext.currentTime + audioBuffer.duration - 0.1);
        
        source.start();
    }
    
    // 语音合成播报
    speakText(text, options = {}) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            
            // 设置语音参数
            utterance.lang = options.lang || 'zh-CN';
            utterance.rate = options.rate || 1.0;
            utterance.pitch = options.pitch || 1.0;
            utterance.volume = options.volume || 0.8;
            
            // 播放语音
            speechSynthesis.speak(utterance);
            
            return new Promise((resolve, reject) => {
                utterance.onend = resolve;
                utterance.onerror = reject;
            });
        } else {
            console.warn('浏览器不支持语音合成功能');
            return Promise.reject('不支持语音合成');
        }
    }
}

// 使用示例
const audioSystem = new AudioAlertSystem();

// 监听水位预警事件
document.addEventListener('waterLevelAlert', (event) => {
    const { level, stationName, waterLevel } = event.detail;
    
    // 播放预警音效
    audioSystem.playAlert(level, 3);
    
    // 语音播报
    const message = `${stationName}水位预警，当前水位${waterLevel}米`;
    audioSystem.speakText(message);
});
```

### Canvas API基础

Canvas元素是HTML5最强大的功能之一，它提供了一个可编程的绘图表面，能够通过JavaScript动态生成图形、动画和交互式内容[10]。在智慧水利平台中，Canvas的应用场景极其广泛：数据可视化图表、工程示意图、实时监控图表、地理信息展示等。

#### Canvas基础绘图

```html
<section class="canvas-charts">
    <h2>水位趋势图表</h2>
    
    <canvas id="waterLevelChart" 
            width="800" 
            height="400"
            style="border: 1px solid #ddd;"
            role="img"
            aria-label="水位变化趋势图表">
        <p>您的浏览器不支持Canvas，无法显示图表。</p>
    </canvas>
    
    <div class="chart-legend">
        <div class="legend-item">
            <span class="color-box" style="background: #2196F3"></span>
            <span>实际水位</span>
        </div>
        <div class="legend-item">
            <span class="color-box" style="background: #FF9800"></span>
            <span>预警水位</span>
        </div>
        <div class="legend-item">
            <span class="color-box" style="background: #F44336"></span>
            <span>危险水位</span>
        </div>
    </div>
</section>

<script>
class WaterLevelChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        
        // 设置画布属性
        this.width = this.canvas.width;
        this.height = this.canvas.height;
        this.padding = { top: 40, right: 40, bottom: 60, left: 80 };
        
        // 计算绘图区域
        this.chartWidth = this.width - this.padding.left - this.padding.right;
        this.chartHeight = this.height - this.padding.top - this.padding.bottom;
        
        // 数据和配置
        this.data = [];
        this.config = {
            lineColor: '#2196F3',
            warningColor: '#FF9800',
            dangerColor: '#F44336',
            gridColor: '#E0E0E0',
            textColor: '#333333'
        };
        
        this.setupCanvas();
    }
    
    setupCanvas() {
        // 设置高分辨率支持
        const dpr = window.devicePixelRatio || 1;
        const rect = this.canvas.getBoundingClientRect();
        
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
        this.ctx.scale(dpr, dpr);
        
        this.canvas.style.width = rect.width + 'px';
        this.canvas.style.height = rect.height + 'px';
    }
    
    setData(data) {
        this.data = data;
        this.draw();
    }
    
    draw() {
        // 清空画布
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        if (this.data.length === 0) return;
        
        // 计算数据范围
        const timestamps = this.data.map(d => new Date(d.timestamp));
        const values = this.data.map(d => d.waterLevel);
        
        this.minTime = Math.min(...timestamps);
        this.maxTime = Math.max(...timestamps);
        this.minValue = Math.min(...values) - 1;
        this.maxValue = Math.max(...values) + 1;
        
        // 绘制背景网格
        this.drawGrid();
        
        // 绘制坐标轴
        this.drawAxes();
        
        // 绘制预警线
        this.drawWarningLines();
        
        // 绘制数据线
        this.drawDataLine();
        
        // 绘制数据点
        this.drawDataPoints();
        
        // 绘制标题
        this.drawTitle();
    }
    
    drawGrid() {
        this.ctx.strokeStyle = this.config.gridColor;
        this.ctx.lineWidth = 1;
        this.ctx.setLineDash([2, 2]);
        
        // 垂直网格线
        for (let i = 0; i <= 10; i++) {
            const x = this.padding.left + (this.chartWidth / 10) * i;
            this.ctx.beginPath();
            this.ctx.moveTo(x, this.padding.top);
            this.ctx.lineTo(x, this.padding.top + this.chartHeight);
            this.ctx.stroke();
        }
        
        // 水平网格线
        for (let i = 0; i <= 8; i++) {
            const y = this.padding.top + (this.chartHeight / 8) * i;
            this.ctx.beginPath();
            this.ctx.moveTo(this.padding.left, y);
            this.ctx.lineTo(this.padding.left + this.chartWidth, y);
            this.ctx.stroke();
        }
        
        this.ctx.setLineDash([]);
    }
    
    drawAxes() {
        this.ctx.strokeStyle = this.config.textColor;
        this.ctx.lineWidth = 2;
        
        // X轴
        this.ctx.beginPath();
        this.ctx.moveTo(this.padding.left, this.padding.top + this.chartHeight);
        this.ctx.lineTo(this.padding.left + this.chartWidth, this.padding.top + this.chartHeight);
        this.ctx.stroke();
        
        // Y轴
        this.ctx.beginPath();
        this.ctx.moveTo(this.padding.left, this.padding.top);
        this.ctx.lineTo(this.padding.left, this.padding.top + this.chartHeight);
        this.ctx.stroke();
        
        // 绘制刻度标签
        this.drawAxisLabels();
    }
    
    drawAxisLabels() {
        this.ctx.fillStyle = this.config.textColor;
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'center';
        
        // X轴标签（时间）
        for (let i = 0; i <= 5; i++) {
            const x = this.padding.left + (this.chartWidth / 5) * i;
            const timeRatio = i / 5;
            const timestamp = this.minTime + (this.maxTime - this.minTime) * timeRatio;
            const date = new Date(timestamp);
            const label = `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
            
            this.ctx.fillText(label, x, this.padding.top + this.chartHeight + 20);
        }
        
        // Y轴标签（水位）
        this.ctx.textAlign = 'right';
        this.ctx.textBaseline = 'middle';
        
        for (let i = 0; i <= 8; i++) {
            const y = this.padding.top + this.chartHeight - (this.chartHeight / 8) * i;
            const value = this.minValue + (this.maxValue - this.minValue) * (i / 8);
            this.ctx.fillText(value.toFixed(1) + 'm', this.padding.left - 10, y);
        }
    }
    
    drawWarningLines() {
        // 预警水位线
        const warningLevel = 25.0;
        const dangerLevel = 27.0;
        
        // 预警线
        const warningY = this.valueToY(warningLevel);
        this.ctx.strokeStyle = this.config.warningColor;
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([5, 5]);
        
        this.ctx.beginPath();
        this.ctx.moveTo(this.padding.left, warningY);
        this.ctx.lineTo(this.padding.left + this.chartWidth, warningY);
        this.ctx.stroke();
        
        // 危险线
        const dangerY = this.valueToY(dangerLevel);
        this.ctx.strokeStyle = this.config.dangerColor;
        
        this.ctx.beginPath();
        this.ctx.moveTo(this.padding.left, dangerY);
        this.ctx.lineTo(this.padding.left + this.chartWidth, dangerY);
        this.ctx.stroke();
        
        this.ctx.setLineDash([]);
        
        // 标注文字
        this.ctx.fillStyle = this.config.warningColor;
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'left';
        this.ctx.fillText('预警水位', this.padding.left + 10, warningY - 5);
        
        this.ctx.fillStyle = this.config.dangerColor;
        this.ctx.fillText('危险水位', this.padding.left + 10, dangerY - 5);
    }
    
    drawDataLine() {
        if (this.data.length < 2) return;
        
        this.ctx.strokeStyle = this.config.lineColor;
        this.ctx.lineWidth = 3;
        this.ctx.lineJoin = 'round';
        this.ctx.lineCap = 'round';
        
        this.ctx.beginPath();
        
        this.data.forEach((point, index) => {
            const x = this.timeToX(new Date(point.timestamp));
            const y = this.valueToY(point.waterLevel);
            
            if (index === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        });
        
        this.ctx.stroke();
    }
    
    drawDataPoints() {
        this.data.forEach(point => {
            const x = this.timeToX(new Date(point.timestamp));
            const y = this.valueToY(point.waterLevel);
            
            // 绘制数据点
            this.ctx.fillStyle = this.config.lineColor;
            this.ctx.beginPath();
            this.ctx.arc(x, y, 4, 0, Math.PI * 2);
            this.ctx.fill();
            
            // 绘制白色内圈
            this.ctx.fillStyle = 'white';
            this.ctx.beginPath();
            this.ctx.arc(x, y, 2, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }
    
    drawTitle() {
        this.ctx.fillStyle = this.config.textColor;
        this.ctx.font = 'bold 16px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('水位变化趋势图', this.width / 2, 25);
    }
    
    timeToX(time) {
        const ratio = (time.getTime() - this.minTime) / (this.maxTime - this.minTime);
        return this.padding.left + ratio * this.chartWidth;
    }
    
    valueToY(value) {
        const ratio = (value - this.minValue) / (this.maxValue - this.minValue);
        return this.padding.top + this.chartHeight - ratio * this.chartHeight;
    }
}

// 使用示例
document.addEventListener('DOMContentLoaded', () => {
    const chart = new WaterLevelChart('waterLevelChart');
    
    // 模拟数据
    const sampleData = [
        { timestamp: '2024-03-15T00:00:00', waterLevel: 23.5 },
        { timestamp: '2024-03-15T04:00:00', waterLevel: 24.1 },
        { timestamp: '2024-03-15T08:00:00', waterLevel: 24.8 },
        { timestamp: '2024-03-15T12:00:00', waterLevel: 25.2 },
        { timestamp: '2024-03-15T16:00:00', waterLevel: 25.8 },
        { timestamp: '2024-03-15T20:00:00', waterLevel: 26.1 },
        { timestamp: '2024-03-15T24:00:00', waterLevel: 25.9 }
    ];
    
    chart.setData(sampleData);
});
</script>
```

通过合理运用HTML5的多媒体元素和Canvas API，我们能够创建出功能丰富、交互性强的智慧水利平台界面，为用户提供直观、生动的数据展示和操作体验。这些技术的灵活运用，将显著提升水利管理系统的用户体验和功能实现水平。
