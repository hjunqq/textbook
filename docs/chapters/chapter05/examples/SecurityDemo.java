package com.example.demo.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;

import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * Spring Security完整配置示例
 * 
 * 演示企业级安全控制的核心功能：
 * 1. JWT令牌认证机制
 * 2. 基于角色和权限的访问控制
 * 3. 方法级安全注解
 * 4. 自定义认证和授权逻辑
 * 5. 安全配置的最佳实践
 * 6. 跨域资源共享(CORS)配置
 */

/**
 * 主要安全配置类
 */
@Configuration
@EnableWebSecurity
@EnableGlobalMethodSecurity(prePostEnabled = true, securedEnabled = true, jsr250Enabled = true)
public class SecurityConfig {
    
    private final CustomUserDetailsService userDetailsService;
    private final JwtAuthenticationEntryPoint jwtAuthenticationEntryPoint;
    private final JwtRequestFilter jwtRequestFilter;
    
    public SecurityConfig(CustomUserDetailsService userDetailsService,
                         JwtAuthenticationEntryPoint jwtAuthenticationEntryPoint,
                         JwtRequestFilter jwtRequestFilter) {
        this.userDetailsService = userDetailsService;
        this.jwtAuthenticationEntryPoint = jwtAuthenticationEntryPoint;
        this.jwtRequestFilter = jwtRequestFilter;
    }
    
    /**
     * 密码编码器配置
     * 使用BCrypt算法进行密码哈希
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
    
    /**
     * 认证管理器配置
     */
    @Bean
    public AuthenticationManager authenticationManager(
            AuthenticationConfiguration authConfig) throws Exception {
        return authConfig.getAuthenticationManager();
    }
    
    /**
     * 核心安全过滤链配置
     */
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // 禁用CSRF保护（API使用JWT令牌）
            .csrf().disable()
            
            // 配置会话管理为无状态
            .sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            .and()
            
            // 配置URL访问权限
            .authorizeHttpRequests(authz -> authz
                // 公开接口（无需认证）
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/swagger-ui/**", "/v3/api-docs/**").permitAll()
                .requestMatchers("/actuator/health").permitAll()
                
                // 基于HTTP方法的权限控制
                .requestMatchers(HttpMethod.GET, "/api/users").hasRole("USER")
                .requestMatchers(HttpMethod.POST, "/api/users").hasRole("ADMIN")
                .requestMatchers(HttpMethod.PUT, "/api/users/**").hasRole("MANAGER")
                .requestMatchers(HttpMethod.DELETE, "/api/users/**").hasRole("ADMIN")
                
                // 基于URL模式的权限控制
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .requestMatchers("/api/manager/**").hasAnyRole("MANAGER", "ADMIN")
                .requestMatchers("/api/reports/**").hasAuthority("REPORT_ACCESS")
                
                // 其他请求需要认证
                .anyRequest().authenticated()
            )
            
            // 配置异常处理
            .exceptionHandling()
                .authenticationEntryPoint(jwtAuthenticationEntryPoint)
            .and()
            
            // 添加JWT过滤器
            .addFilterBefore(jwtRequestFilter, UsernamePasswordAuthenticationFilter.class);
            
        return http.build();
    }
    
    /**
     * CORS配置
     */
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(Arrays.asList("*"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(3600L);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", configuration);
        return source;
    }
}

/**
 * JWT工具类
 * 处理JWT令牌的生成、解析和验证
 */
@Component
public class JwtTokenUtil {
    
    // 实际项目中应从配置文件读取，且应该更复杂
    private static final String SECRET = "mySecretKey";
    private static final int JWT_TOKEN_VALIDITY = 5 * 60 * 60; // 5小时
    
    /**
     * 从令牌中获取用户名
     */
    public String getUsernameFromToken(String token) {
        return getClaimFromToken(token, Claims::getSubject);
    }
    
    /**
     * 从令牌中获取过期时间
     */
    public Date getExpirationDateFromToken(String token) {
        return getClaimFromToken(token, Claims::getExpiration);
    }
    
    /**
     * 从令牌中获取用户ID
     */
    public Long getUserIdFromToken(String token) {
        Claims claims = getAllClaimsFromToken(token);
        return claims.get("userId", Long.class);
    }
    
    /**
     * 从令牌中获取用户角色
     */
    @SuppressWarnings("unchecked")
    public List<String> getRolesFromToken(String token) {
        Claims claims = getAllClaimsFromToken(token);
        return (List<String>) claims.get("roles");
    }
    
    /**
     * 通用的声明提取方法
     */
    public <T> T getClaimFromToken(String token, Function<Claims, T> claimsResolver) {
        final Claims claims = getAllClaimsFromToken(token);
        return claimsResolver.apply(claims);
    }
    
    /**
     * 获取令牌中的所有声明
     */
    private Claims getAllClaimsFromToken(String token) {
        return Jwts.parser()
                .setSigningKey(SECRET)
                .parseClaimsJws(token)
                .getBody();
    }
    
    /**
     * 检查令牌是否过期
     */
    public Boolean isTokenExpired(String token) {
        final Date expiration = getExpirationDateFromToken(token);
        return expiration.before(new Date());
    }
    
    /**
     * 生成JWT令牌
     */
    public String generateToken(UserDetails userDetails) {
        Map<String, Object> claims = new HashMap<>();
        
        // 添加用户角色信息
        Collection<? extends GrantedAuthority> authorities = userDetails.getAuthorities();
        claims.put("roles", authorities.stream()
                .map(GrantedAuthority::getAuthority)
                .collect(Collectors.toList()));
                
        // 添加自定义用户信息
        if (userDetails instanceof CustomUserDetails) {
            CustomUserDetails customUser = (CustomUserDetails) userDetails;
            claims.put("userId", customUser.getUserId());
            claims.put("organizationId", customUser.getOrganizationId());
            claims.put("permissions", customUser.getPermissions());
        }
        
        return createToken(claims, userDetails.getUsername());
    }
    
    /**
     * 创建令牌
     */
    private String createToken(Map<String, Object> claims, String subject) {
        return Jwts.builder()
                .setClaims(claims)
                .setSubject(subject)
                .setIssuedAt(new Date(System.currentTimeMillis()))
                .setExpiration(new Date(System.currentTimeMillis() + JWT_TOKEN_VALIDITY * 1000))
                .signWith(SignatureAlgorithm.HS512, SECRET)
                .compact();
    }
    
    /**
     * 验证令牌
     */
    public Boolean validateToken(String token, UserDetails userDetails) {
        final String username = getUsernameFromToken(token);
        return (username.equals(userDetails.getUsername()) && !isTokenExpired(token));
    }
}

/**
 * JWT认证过滤器
 * 处理每个HTTP请求的JWT令牌验证
 */
@Component
public class JwtRequestFilter extends OncePerRequestFilter {
    
    private final CustomUserDetailsService userDetailsService;
    private final JwtTokenUtil jwtTokenUtil;
    
    public JwtRequestFilter(CustomUserDetailsService userDetailsService,
                           JwtTokenUtil jwtTokenUtil) {
        this.userDetailsService = userDetailsService;
        this.jwtTokenUtil = jwtTokenUtil;
    }
    
    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, 
                                  FilterChain chain) throws ServletException, IOException {
        
        final String requestTokenHeader = request.getHeader("Authorization");
        
        String username = null;
        String jwtToken = null;
        
        // JWT令牌格式: "Bearer token"
        if (requestTokenHeader != null && requestTokenHeader.startsWith("Bearer ")) {
            jwtToken = requestTokenHeader.substring(7);
            try {
                username = jwtTokenUtil.getUsernameFromToken(jwtToken);
            } catch (IllegalArgumentException e) {
                logger.error("无法获取JWT令牌", e);
            } catch (ExpiredJwtException e) {
                logger.error("JWT令牌已过期", e);
            }
        } else {
            logger.warn("JWT令牌格式不正确，缺少Bearer前缀");
        }
        
        // 验证令牌并设置认证上下文
        if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            
            UserDetails userDetails = this.userDetailsService.loadUserByUsername(username);
            
            if (jwtTokenUtil.validateToken(jwtToken, userDetails)) {
                UsernamePasswordAuthenticationToken authToken = 
                    new UsernamePasswordAuthenticationToken(
                        userDetails, null, userDetails.getAuthorities());
                authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                
                SecurityContextHolder.getContext().setAuthentication(authToken);
            }
        }
        
        chain.doFilter(request, response);
    }
}

/**
 * 自定义用户详情服务
 * 从数据库加载用户信息
 */
@Service
public class CustomUserDetailsService implements UserDetailsService {
    
    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    
    public CustomUserDetailsService(UserRepository userRepository,
                                  RoleRepository roleRepository) {
        this.userRepository = userRepository;
        this.roleRepository = roleRepository;
    }
    
    @Override
    @Transactional(readOnly = true)
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("用户不存在: " + username));
        
        if (!user.isActive()) {
            throw new DisabledException("用户账户已被禁用: " + username);
        }
        
        if (user.isLocked()) {
            throw new AccountExpiredException("用户账户已被锁定: " + username);
        }
        
        // 加载用户角色和权限
        List<Role> roles = roleRepository.findByUserId(user.getId());
        List<String> permissions = roles.stream()
                .flatMap(role -> role.getPermissions().stream())
                .map(Permission::getName)
                .distinct()
                .collect(Collectors.toList());
        
        return CustomUserDetails.builder()
                .userId(user.getId())
                .username(user.getUsername())
                .password(user.getPassword())
                .email(user.getEmail())
                .organizationId(user.getOrganizationId())
                .roles(roles.stream().map(Role::getName).collect(Collectors.toList()))
                .permissions(permissions)
                .enabled(user.isActive())
                .accountNonExpired(true)
                .accountNonLocked(!user.isLocked())
                .credentialsNonExpired(true)
                .build();
    }
}

/**
 * 自定义用户详情类
 * 扩展标准UserDetails接口，添加业务相关信息
 */
public class CustomUserDetails implements UserDetails {
    
    private Long userId;
    private String username;
    private String password;
    private String email;
    private Long organizationId;
    private List<String> roles;
    private List<String> permissions;
    private boolean enabled;
    private boolean accountNonExpired;
    private boolean accountNonLocked;
    private boolean credentialsNonExpired;
    
    // 构建器模式
    public static CustomUserDetailsBuilder builder() {
        return new CustomUserDetailsBuilder();
    }
    
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        List<GrantedAuthority> authorities = new ArrayList<>();
        
        // 添加角色权限（以ROLE_前缀标识）
        for (String role : roles) {
            authorities.add(new SimpleGrantedAuthority("ROLE_" + role));
        }
        
        // 添加具体权限
        for (String permission : permissions) {
            authorities.add(new SimpleGrantedAuthority(permission));
        }
        
        return authorities;
    }
    
    @Override
    public String getPassword() {
        return password;
    }
    
    @Override
    public String getUsername() {
        return username;
    }
    
    @Override
    public boolean isAccountNonExpired() {
        return accountNonExpired;
    }
    
    @Override
    public boolean isAccountNonLocked() {
        return accountNonLocked;
    }
    
    @Override
    public boolean isCredentialsNonExpired() {
        return credentialsNonExpired;
    }
    
    @Override
    public boolean isEnabled() {
        return enabled;
    }
    
    // 业务相关的getter方法
    public Long getUserId() { return userId; }
    public String getEmail() { return email; }
    public Long getOrganizationId() { return organizationId; }
    public List<String> getRoles() { return roles; }
    public List<String> getPermissions() { return permissions; }
    
    // 构建器类
    public static class CustomUserDetailsBuilder {
        private CustomUserDetails userDetails = new CustomUserDetails();
        
        public CustomUserDetailsBuilder userId(Long userId) { userDetails.userId = userId; return this; }
        public CustomUserDetailsBuilder username(String username) { userDetails.username = username; return this; }
        public CustomUserDetailsBuilder password(String password) { userDetails.password = password; return this; }
        public CustomUserDetailsBuilder email(String email) { userDetails.email = email; return this; }
        public CustomUserDetailsBuilder organizationId(Long organizationId) { userDetails.organizationId = organizationId; return this; }
        public CustomUserDetailsBuilder roles(List<String> roles) { userDetails.roles = roles; return this; }
        public CustomUserDetailsBuilder permissions(List<String> permissions) { userDetails.permissions = permissions; return this; }
        public CustomUserDetailsBuilder enabled(boolean enabled) { userDetails.enabled = enabled; return this; }
        public CustomUserDetailsBuilder accountNonExpired(boolean accountNonExpired) { userDetails.accountNonExpired = accountNonExpired; return this; }
        public CustomUserDetailsBuilder accountNonLocked(boolean accountNonLocked) { userDetails.accountNonLocked = accountNonLocked; return this; }
        public CustomUserDetailsBuilder credentialsNonExpired(boolean credentialsNonExpired) { userDetails.credentialsNonExpired = credentialsNonExpired; return this; }
        
        public CustomUserDetails build() { return userDetails; }
    }
}

/**
 * 认证入口点
 * 处理未认证请求的响应
 */
@Component
public class JwtAuthenticationEntryPoint implements AuthenticationEntryPoint {
    
    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response,
                        AuthenticationException authException) throws IOException {
        
        response.setContentType("application/json;charset=UTF-8");
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("success", false);
        errorResponse.put("errorCode", "UNAUTHORIZED");
        errorResponse.put("message", "访问令牌无效或已过期，请重新登录");
        errorResponse.put("timestamp", System.currentTimeMillis());
        
        ObjectMapper mapper = new ObjectMapper();
        response.getWriter().write(mapper.writeValueAsString(errorResponse));
    }
}

/**
 * 权限检查服务
 * 提供细粒度的权限验证功能
 */
@Service
public class SecurityService {
    
    private final UserRepository userRepository;
    private final RolePermissionRepository rolePermissionRepository;
    
    public SecurityService(UserRepository userRepository,
                         RolePermissionRepository rolePermissionRepository) {
        this.userRepository = userRepository;
        this.rolePermissionRepository = rolePermissionRepository;
    }
    
    /**
     * 检查用户是否拥有指定权限
     */
    public boolean hasPermission(String permission) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !(auth.getPrincipal() instanceof CustomUserDetails)) {
            return false;
        }
        
        CustomUserDetails userDetails = (CustomUserDetails) auth.getPrincipal();
        return userDetails.getPermissions().contains(permission);
    }
    
    /**
     * 检查用户是否拥有任一指定权限
     */
    public boolean hasAnyPermission(String... permissions) {
        return Arrays.stream(permissions).anyMatch(this::hasPermission);
    }
    
    /**
     * 检查用户是否拥有所有指定权限
     */
    public boolean hasAllPermissions(String... permissions) {
        return Arrays.stream(permissions).allMatch(this::hasPermission);
    }
    
    /**
     * 检查用户是否属于指定组织
     */
    public boolean belongsToOrganization(Long organizationId) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !(auth.getPrincipal() instanceof CustomUserDetails)) {
            return false;
        }
        
        CustomUserDetails userDetails = (CustomUserDetails) auth.getPrincipal();
        return Objects.equals(userDetails.getOrganizationId(), organizationId);
    }
    
    /**
     * 检查用户是否可以访问指定资源
     */
    public boolean canAccessResource(String resourceType, Long resourceId) {
        // 实现具体的资源访问控制逻辑
        // 这里可以根据用户角色、组织、资源类型等进行复杂的权限判断
        return hasPermission("RESOURCE_" + resourceType.toUpperCase() + "_ACCESS");
    }
}

/**
 * 方法级安全注解的使用示例
 */
@RestController
@RequestMapping("/api/secure")
public class SecureController {
    
    private final SecurityService securityService;
    private final UserService userService;
    
    public SecureController(SecurityService securityService,
                          UserService userService) {
        this.securityService = securityService;
        this.userService = userService;
    }
    
    /**
     * 需要ADMIN角色才能访问
     */
    @GetMapping("/admin-only")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<String> adminOnlyEndpoint() {
        return ResponseEntity.ok("这是管理员专用接口");
    }
    
    /**
     * 需要特定权限才能访问
     */
    @GetMapping("/reports")
    @PreAuthorize("hasAuthority('REPORT_ACCESS')")
    public ResponseEntity<String> reportsEndpoint() {
        return ResponseEntity.ok("报告数据");
    }
    
    /**
     * 复杂的权限表达式
     */
    @PostMapping("/sensitive")
    @PreAuthorize("hasRole('MANAGER') and @securityService.belongsToOrganization(#orgId)")
    public ResponseEntity<String> sensitiveOperation(@RequestParam Long orgId) {
        return ResponseEntity.ok("敏感操作执行成功");
    }
    
    /**
     * 基于返回值的安全控制
     */
    @GetMapping("/user/{id}")
    @PostAuthorize("returnObject.organizationId == authentication.principal.organizationId")
    public UserDto getUserById(@PathVariable Long id) {
        return userService.getUserById(id);
    }
    
    /**
     * 自定义权限检查
     */
    @DeleteMapping("/resource/{id}")
    @PreAuthorize("@securityService.canAccessResource('USER', #id)")
    public ResponseEntity<String> deleteResource(@PathVariable Long id) {
        return ResponseEntity.ok("资源删除成功");
    }
}

/**
 * 权限枚举定义
 * 统一管理系统中的所有权限
 */
public enum SystemPermission {
    // 用户管理权限
    USER_CREATE("用户创建"),
    USER_UPDATE("用户更新"),
    USER_DELETE("用户删除"),
    USER_VIEW("用户查看"),
    
    // 报告权限
    REPORT_ACCESS("报告访问"),
    REPORT_EXPORT("报告导出"),
    REPORT_MANAGE("报告管理"),
    
    // 系统管理权限
    SYSTEM_CONFIG("系统配置"),
    AUDIT_LOG_VIEW("审计日志查看"),
    
    // 数据权限
    DATA_IMPORT("数据导入"),
    DATA_EXPORT("数据导出"),
    DATA_MODIFY("数据修改");
    
    private final String description;
    
    SystemPermission(String description) {
        this.description = description;
    }
    
    public String getDescription() {
        return description;
    }
}