package com.example.demo.lifecycle;

import org.springframework.beans.BeansException;
import org.springframework.beans.factory.BeanFactory;
import org.springframework.beans.factory.BeanFactoryAware;
import org.springframework.beans.factory.BeanNameAware;
import org.springframework.beans.factory.DisposableBean;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * Bean生命周期完整示例
 * 
 * 展示Spring Bean生命周期的各个阶段：
 * 1. Aware接口回调
 * 2. @PostConstruct注解方法
 * 3. InitializingBean接口方法
 * 4. 自定义init方法
 * 5. @PreDestroy注解方法
 * 6. DisposableBean接口方法
 * 7. 自定义destroy方法
 */
@Component
public class LifecycleAwareBean implements 
        BeanNameAware, 
        BeanFactoryAware, 
        ApplicationContextAware,
        InitializingBean,
        DisposableBean {
    
    // Bean基本信息
    private String beanName;
    private BeanFactory beanFactory;
    private ApplicationContext applicationContext;
    
    // 业务资源
    private ExecutorService executorService;
    private DatabaseConnectionPool connectionPool;
    private CacheManager cacheManager;
    
    // 生命周期统计
    private long initializationStartTime;
    private long initializationCompleteTime;
    private boolean initialized = false;
    
    /**
     * 1. BeanNameAware回调 - 获取Bean名称
     */
    @Override
    public void setBeanName(String name) {
        this.beanName = name;
        System.out.println("[1] BeanNameAware: Bean name is '" + name + "'");
        this.initializationStartTime = System.currentTimeMillis();
    }
    
    /**
     * 2. BeanFactoryAware回调 - 获取BeanFactory引用
     */
    @Override
    public void setBeanFactory(BeanFactory beanFactory) throws BeansException {
        this.beanFactory = beanFactory;
        System.out.println("[2] BeanFactoryAware: BeanFactory type is " + 
                          beanFactory.getClass().getSimpleName());
    }
    
    /**
     * 3. ApplicationContextAware回调 - 获取ApplicationContext引用
     */
    @Override
    public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
        this.applicationContext = applicationContext;
        System.out.println("[3] ApplicationContextAware: ApplicationContext type is " + 
                          applicationContext.getClass().getSimpleName());
        System.out.println("    - Context display name: " + applicationContext.getDisplayName());
        System.out.println("    - Bean definition count: " + applicationContext.getBeanDefinitionCount());
    }
    
    /**
     * 4. @PostConstruct注解方法 - 第一个初始化方法
     */
    @PostConstruct
    public void postConstructInit() {
        System.out.println("[4] @PostConstruct: Starting resource initialization...");
        
        // 初始化线程池
        this.executorService = Executors.newFixedThreadPool(5);
        System.out.println("    - ExecutorService initialized with 5 threads");
        
        // 初始化连接池
        this.connectionPool = new DatabaseConnectionPool(10, 20);
        System.out.println("    - Database connection pool initialized (min=10, max=20)");
        
        // 预加载缓存
        preloadCache();
        
        System.out.println("[4] @PostConstruct: Resource initialization completed");
    }
    
    /**
     * 5. InitializingBean接口方法 - 第二个初始化方法
     */
    @Override
    public void afterPropertiesSet() throws Exception {
        System.out.println("[5] InitializingBean: Validating bean configuration...");
        
        // 验证必需资源
        if (executorService == null) {
            throw new IllegalStateException("ExecutorService not initialized");
        }
        if (connectionPool == null) {
            throw new IllegalStateException("DatabaseConnectionPool not initialized");
        }
        
        // 启动后台监控任务
        startMonitoringTasks();
        
        // 注册应用事件监听器
        registerEventListeners();
        
        System.out.println("[5] InitializingBean: Bean configuration validated successfully");
    }
    
    /**
     * 6. 自定义初始化方法（通过@Bean的initMethod或XML配置）
     * 注意：这个方法需要在@Bean注解中指定
     */
    public void customInit() {
        System.out.println("[6] Custom init method: Performing final initialization...");
        
        // 标记初始化完成
        this.initialized = true;
        this.initializationCompleteTime = System.currentTimeMillis();
        
        long initDuration = initializationCompleteTime - initializationStartTime;
        System.out.println("    - Initialization completed in " + initDuration + " ms");
        
        // 发送初始化完成事件
        if (applicationContext != null) {
            BeanInitializedEvent event = new BeanInitializedEvent(this, beanName);
            applicationContext.publishEvent(event);
        }
        
        System.out.println("[6] Custom init method: Bean is now ready for use");
    }
    
    /**
     * 业务方法 - 验证Bean是否可用
     */
    public String processBusinessLogic(String input) {
        if (!initialized) {
            throw new IllegalStateException("Bean not fully initialized yet");
        }
        
        System.out.println("Processing business logic with input: " + input);
        
        // 模拟使用各种资源
        try {
            // 使用连接池
            DatabaseConnection connection = connectionPool.getConnection();
            String dbResult = connection.query("SELECT * FROM data WHERE input = '" + input + "'");
            connectionPool.releaseConnection(connection);
            
            // 使用缓存
            String cacheKey = "business_" + input;
            Object cachedResult = cacheManager.get(cacheKey);
            if (cachedResult == null) {
                cachedResult = "Processed: " + input;
                cacheManager.put(cacheKey, cachedResult);
            }
            
            return (String) cachedResult;
            
        } catch (Exception e) {
            System.err.println("Business logic processing failed: " + e.getMessage());
            return "Error processing: " + input;
        }
    }
    
    /**
     * 7. @PreDestroy注解方法 - 第一个销毁方法
     */
    @PreDestroy
    public void preDestroyCleanup() {
        System.out.println("[7] @PreDestroy: Starting resource cleanup...");
        
        // 停止监控任务
        stopMonitoringTasks();
        
        // 清理缓存
        if (cacheManager != null) {
            cacheManager.clear();
            System.out.println("    - Cache cleared");
        }
        
        // 关闭线程池
        if (executorService != null && !executorService.isShutdown()) {
            executorService.shutdown();
            try {
                if (!executorService.awaitTermination(5, TimeUnit.SECONDS)) {
                    executorService.shutdownNow();
                    System.out.println("    - ExecutorService force shutdown");
                } else {
                    System.out.println("    - ExecutorService shutdown gracefully");
                }
            } catch (InterruptedException e) {
                executorService.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
        
        System.out.println("[7] @PreDestroy: Resource cleanup completed");
    }
    
    /**
     * 8. DisposableBean接口方法 - 第二个销毁方法
     */
    @Override
    public void destroy() throws Exception {
        System.out.println("[8] DisposableBean: Performing final cleanup...");
        
        // 关闭数据库连接池
        if (connectionPool != null) {
            connectionPool.close();
            System.out.println("    - Database connection pool closed");
        }
        
        // 发送销毁事件
        if (applicationContext != null) {
            BeanDestroyedEvent event = new BeanDestroyedEvent(this, beanName);
            try {
                applicationContext.publishEvent(event);
            } catch (Exception e) {
                // 销毁过程中应用上下文可能已经关闭
                System.out.println("    - Could not publish destroy event: " + e.getMessage());
            }
        }
        
        // 重置状态
        this.initialized = false;
        
        System.out.println("[8] DisposableBean: Final cleanup completed");
    }
    
    /**
     * 9. 自定义销毁方法（通过@Bean的destroyMethod或XML配置）
     */
    public void customDestroy() {
        System.out.println("[9] Custom destroy method: Bean lifecycle completed");
        
        long totalLifetime = System.currentTimeMillis() - initializationStartTime;
        System.out.println("    - Total bean lifetime: " + totalLifetime + " ms");
        
        // 清理任何剩余资源
        this.beanName = null;
        this.beanFactory = null;
        this.applicationContext = null;
        
        System.out.println("[9] Custom destroy method: All references cleared");
    }
    
    // 辅助方法
    private void preloadCache() {
        this.cacheManager = new CacheManager();
        cacheManager.put("system_config", "default_config");
        cacheManager.put("app_settings", "production_settings");
        System.out.println("    - Cache preloaded with system data");
    }
    
    private void startMonitoringTasks() {
        if (executorService != null) {
            executorService.submit(() -> {
                while (!Thread.currentThread().isInterrupted()) {
                    try {
                        // 模拟监控任务
                        Thread.sleep(30000); // 每30秒监控一次
                        System.out.println("    - Monitoring task: System health OK");
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            });
        }
    }
    
    private void stopMonitoringTasks() {
        System.out.println("    - Monitoring tasks stopped");
    }
    
    private void registerEventListeners() {
        System.out.println("    - Event listeners registered");
    }
    
    // Getter方法
    public String getBeanName() { return beanName; }
    public boolean isInitialized() { return initialized; }
    public long getInitializationTime() { return initializationCompleteTime - initializationStartTime; }
}

/**
 * 支持类 - 数据库连接池
 */
class DatabaseConnectionPool {
    private final int minConnections;
    private final int maxConnections;
    private int activeConnections = 0;
    
    public DatabaseConnectionPool(int minConnections, int maxConnections) {
        this.minConnections = minConnections;
        this.maxConnections = maxConnections;
    }
    
    public DatabaseConnection getConnection() {
        activeConnections++;
        return new DatabaseConnection("connection_" + activeConnections);
    }
    
    public void releaseConnection(DatabaseConnection connection) {
        // 释放连接逻辑
    }
    
    public void close() {
        System.out.println("Database connection pool closed");
    }
}

/**
 * 支持类 - 数据库连接
 */
class DatabaseConnection {
    private final String connectionId;
    
    public DatabaseConnection(String connectionId) {
        this.connectionId = connectionId;
    }
    
    public String query(String sql) {
        return "Query result for: " + sql;
    }
}

/**
 * 支持类 - 缓存管理器
 */
class CacheManager {
    private final java.util.Map<String, Object> cache = new java.util.concurrent.ConcurrentHashMap<>();
    
    public void put(String key, Object value) {
        cache.put(key, value);
    }
    
    public Object get(String key) {
        return cache.get(key);
    }
    
    public void clear() {
        cache.clear();
    }
}

/**
 * 支持类 - Bean初始化事件
 */
class BeanInitializedEvent extends org.springframework.context.ApplicationEvent {
    private final String beanName;
    
    public BeanInitializedEvent(Object source, String beanName) {
        super(source);
        this.beanName = beanName;
    }
    
    public String getBeanName() { return beanName; }
}

/**
 * 支持类 - Bean销毁事件
 */
class BeanDestroyedEvent extends org.springframework.context.ApplicationEvent {
    private final String beanName;
    
    public BeanDestroyedEvent(Object source, String beanName) {
        super(source);
        this.beanName = beanName;
    }
    
    public String getBeanName() { return beanName; }
}