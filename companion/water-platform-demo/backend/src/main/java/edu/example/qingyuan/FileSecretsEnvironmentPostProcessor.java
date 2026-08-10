package edu.example.qingyuan;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.env.EnvironmentPostProcessor;
import org.springframework.core.env.ConfigurableEnvironment;
import org.springframework.core.env.MapPropertySource;

/**
 * 支持 Docker secrets 的 *_FILE 约定：对每个形如 X_FILE 的环境变量，
 * 读取其指向文件的内容并注入为属性 X（去掉 _FILE 后缀）。
 * 这样 compose 传入 DB_PASSWORD_FILE=/run/secrets/db_password 时，
 * application.yml 中的 ${DB_PASSWORD} 就能取到真实口令，
 * 而口令本身不出现在环境变量或进程列表中。
 */
public class FileSecretsEnvironmentPostProcessor implements EnvironmentPostProcessor {
    @Override
    public void postProcessEnvironment(ConfigurableEnvironment environment, SpringApplication application) {
        Map<String, Object> resolved = new HashMap<>();
        System.getenv().forEach((key, value) -> {
            if (!key.endsWith("_FILE") || value == null || value.isBlank()) return;
            Path secretFile = Path.of(value);
            if (!Files.isReadable(secretFile)) return;
            try {
                resolved.put(key.substring(0, key.length() - "_FILE".length()),
                        Files.readString(secretFile).trim());
            } catch (Exception ignored) {
                // 文件不可读时保持缺省值，由数据源连接失败暴露问题
            }
        });
        if (!resolved.isEmpty()) {
            environment.getPropertySources()
                    .addFirst(new MapPropertySource("fileSecrets", resolved));
        }
    }
}
