package edu.example.lesson52;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.actuate.autoconfigure.security.servlet.ManagementWebSecurityAutoConfiguration;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.boot.autoconfigure.jdbc.DataSourceTransactionManagerAutoConfiguration;
import org.springframework.boot.autoconfigure.kafka.KafkaAutoConfiguration;
import org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration;
import org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration;
import org.springframework.boot.autoconfigure.security.servlet.UserDetailsServiceAutoConfiguration;

/**
 * S3 阶段起点（教材 5.2 节）：只有一个控制器、没有数据库、没有认证的最小 Spring Boot 应用。
 *
 * 运行：
 *   cd companion/water-platform-demo/backend
 *   mvn spring-boot:run -Dspring-boot.run.main-class=edu.example.lesson52.Lesson52Application
 *
 * 启动前先停掉教学接口（teaching-api），否则 8080 端口冲突——
 * 这正是 5.2.1 节“预期运行记录”表里最后一行要观察的现象。
 *
 * 本类刻意放在 edu.example.lesson52 包下，而不是 edu.example.qingyuan：
 * Spring Boot 的组件扫描以 @SpringBootApplication 所在包为根，
 * 放在 qingyuan 下会被完整工程一起扫到，两个 /api/assets 映射冲突，启动即失败。
 * 完整工程（S3 终点）的入口仍是 edu.example.qingyuan.WaterPlatformApplication。
 */
@SpringBootApplication(exclude = {
        // 5.2 节明确说“数据库到 5.4 节才接入”“本节还没有认证”。
        // 但完整工程的 classpath 上有 JPA、Kafka 与 Security，Spring Boot 会自动配置它们：
        // 不排除的话，这个起点包一启动就去连 PostgreSQL 并要求登录，直接失败。
        // 5.4 与 5.6 节写到对应内容时，学生在自己的工程里本来就没有这些依赖，不需要这份排除清单。
        DataSourceAutoConfiguration.class,
        DataSourceTransactionManagerAutoConfiguration.class,
        HibernateJpaAutoConfiguration.class,
        KafkaAutoConfiguration.class,
        SecurityAutoConfiguration.class,
        UserDetailsServiceAutoConfiguration.class,
        ManagementWebSecurityAutoConfiguration.class,
})
public class Lesson52Application {
    public static void main(String[] args) {
        SpringApplication.run(Lesson52Application.class, args);
    }
}
