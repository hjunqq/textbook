package edu.example.qingyuan;

import java.time.Clock;
import java.time.Duration;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.crypto.factory.PasswordEncoderFactories;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

@Configuration
@EnableMethodSecurity
public class SecurityConfig {

    /** 教学密钥仅用于课堂演示；生产环境必须经 JWT_SECRET(_FILE) 注入并轮换。 */
    @Bean
    JwtService jwtService(
            @Value("${security.jwt.secret:cWluZ3l1YW4tdGVhY2hpbmctc2VjcmV0LTAxMjM0NTY3ODlhYmNkZWY=}") String secret,
            @Value("${security.jwt.access-seconds:1800}") long accessSeconds) {
        return new JwtService(secret, Duration.ofSeconds(accessSeconds), Clock.systemUTC());
    }

    /** 教学账号表：三个角色各一个账号，口令用 BCrypt 存储。 */
    @Bean
    InMemoryUserDetailsManager users(PasswordEncoder encoder) {
        return new InMemoryUserDetailsManager(
                User.withUsername("duty01").password(encoder.encode("duty123")).authorities("DUTY").build(),
                User.withUsername("analyst01").password(encoder.encode("analyst123")).authorities("ANALYST").build(),
                User.withUsername("ops01").password(encoder.encode("ops123")).authorities("OPS").build());
    }

    @Bean
    PasswordEncoder passwordEncoder() { return PasswordEncoderFactories.createDelegatingPasswordEncoder(); }

    @Bean
    SecurityFilterChain security(HttpSecurity http, JwtService jwtService) throws Exception {
        return http
                .csrf(csrf -> csrf.disable())
                .cors(Customizer.withDefaults())
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/actuator/health/**", "/api/auth/login").permitAll()
                        .anyRequest().authenticated())
                .addFilterBefore(new JwtAuthenticationFilter(jwtService),
                        UsernamePasswordAuthenticationFilter.class)
                // 契约（8.1 通用约定）：401 未登录或令牌失效，403 角色无权。
                // 不配这两个处理器时，匿名请求会落到默认的 403，页面无法区分
                // “没登录”和“登录了但没权限”——前者该跳登录页，后者不该跳。
                .exceptionHandling(e -> e
                        .authenticationEntryPoint((req, res, ex) ->
                                writeError(res, 401, "UNAUTHORIZED", "未登录或令牌已失效"))
                        .accessDeniedHandler((req, res, ex) ->
                                writeError(res, 403, "FORBIDDEN", "当前角色无权访问该资源")))
                .build();
    }

    /** 直接写契约错误体：安全过滤链在 @RestControllerAdvice 之前，异常到不了那一层。 */
    private static void writeError(jakarta.servlet.http.HttpServletResponse res,
                                   int status, String code, String message) throws java.io.IOException {
        res.setStatus(status);
        res.setContentType("application/json;charset=UTF-8");
        res.getWriter().write("{\"code\":\"" + code + "\",\"message\":\"" + message + "\"}");
    }

    /** 开发期允许 Vite dev server 跨域；生产由 Nginx 同源反代，此配置不生效。 */
    @Bean
    CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of("http://localhost:5173"));
        config.setAllowedMethods(List.of("GET", "POST"));
        config.setAllowedHeaders(List.of("Authorization", "Content-Type"));
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", config);
        return source;
    }
}
