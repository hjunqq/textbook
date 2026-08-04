package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

/**
 * Spring Boot 主启动类示例
 * 
 * 功能说明：
 * 1. @SpringBootApplication 组合注解包含了：
 *    - @Configuration：标识为配置类
 *    - @EnableAutoConfiguration：启用自动配置
 *    - @ComponentScan：启用组件扫描
 * 
 * 2. SpringApplication.run() 启动Spring应用上下文
 * 3. 自动配置会根据classpath中的依赖进行配置
 */
@SpringBootApplication
@EnableConfigurationProperties({AppProperties.class})
public class DemoApplication {

    /**
     * 应用程序入口点
     * 
     * @param args 命令行参数
     */
    public static void main(String[] args) {
        // 启动Spring Boot应用
        SpringApplication.run(DemoApplication.class, args);
        
        System.out.println("Spring Boot应用启动成功！");
        System.out.println("访问地址：http://localhost:8080");
    }
    
    /**
     * 自定义启动配置示例
     */
    public static void customMain(String[] args) {
        SpringApplication app = new SpringApplication(DemoApplication.class);
        
        // 自定义配置
        app.setAdditionalProfiles("custom");
        app.setBannerMode(Banner.Mode.OFF);
        
        // 启动应用
        app.run(args);
    }
}

/**
 * 应用程序配置属性类
 */
@ConfigurationProperties(prefix = "app")
@Data
public class AppProperties {
    
    /**
     * 应用名称
     */
    private String name = "Demo Application";
    
    /**
     * 应用版本
     */
    private String version = "1.0.0";
    
    /**
     * 安全配置
     */
    private Security security = new Security();
    
    /**
     * 数据库配置
     */
    private Database database = new Database();
    
    @Data
    public static class Security {
        /**
         * 是否启用安全功能
         */
        private boolean enabled = true;
        
        /**
         * 加密算法
         */
        private String algorithm = "SHA-256";
        
        /**
         * JWT令牌过期时间（小时）
         */
        private int tokenExpirationHours = 24;
    }
    
    @Data
    public static class Database {
        /**
         * 连接池最大连接数
         */
        private int maxPoolSize = 20;
        
        /**
         * 连接超时时间（秒）
         */
        private int connectionTimeout = 30;
        
        /**
         * 是否显示SQL语句
         */
        private boolean showSql = false;
    }
}