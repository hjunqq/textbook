package edu.example.lesson54;

import edu.example.qingyuan.ApiExceptionHandler;
import edu.example.qingyuan.AssetController;
import edu.example.qingyuan.AssetEntity;
import edu.example.qingyuan.AssetRepository;
import edu.example.qingyuan.ReadingService;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.actuate.autoconfigure.security.servlet.ManagementWebSecurityAutoConfiguration;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.boot.autoconfigure.kafka.KafkaAutoConfiguration;
import org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration;
import org.springframework.boot.autoconfigure.security.servlet.UserDetailsServiceAutoConfiguration;
import org.springframework.context.annotation.Import;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

/**
 * S3 阶段中点（教材 5.4.1、5.4.2 节）：对象与观测来自 PostgreSQL，控制器—服务—Repository 三层齐备，
 * 仍然没有认证，也不连 Kafka。用它观察“固定数据换成数据库查询”和“一个类拆成三层”之后接口行为不变。
 *
 * 运行（先按 STAGES.md 启动数据库）：
 *   cd companion/water-platform-demo/backend
 *   mvn spring-boot:run -Dspring-boot.run.main-class=edu.example.lesson54.Lesson54Application
 *
 * 本入口不复制任何业务代码：它只是把完整工程 edu.example.qingyuan 里与 5.4 节有关的类装起来。
 *   AssetEntity / ReadingEntity        —— 实体（@EntityScan 扫描 qingyuan 包）
 *   AssetRepository / ReadingRepository —— Repository（@EnableJpaRepositories）
 *   ReadingService                      —— 服务层
 *   AssetController                     —— 控制器；其上的 @PreAuthorize 在未启用方法级安全时不生效
 *   ApiExceptionHandler                 —— 契约错误体 {code, message, field?}，5.5 节讲解
 * 组件扫描的根是本包 edu.example.lesson54，所以 qingyuan 包里的 SecurityConfig、AuthController、
 * ReadingConsumer 等不会被装进来；认证在 5.6 节、消息消费在 5.7 节加入，那时改用完整工程入口。
 */
@SpringBootApplication(exclude = {
        KafkaAutoConfiguration.class,
        SecurityAutoConfiguration.class,
        UserDetailsServiceAutoConfiguration.class,
        ManagementWebSecurityAutoConfiguration.class,
})
@EntityScan(basePackageClasses = AssetEntity.class)
@EnableJpaRepositories(basePackageClasses = AssetRepository.class)
@Import({AssetController.class, ReadingService.class, ApiExceptionHandler.class})
public class Lesson54Application {
    public static void main(String[] args) {
        SpringApplication.run(Lesson54Application.class, args);
    }
}
