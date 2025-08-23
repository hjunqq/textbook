package com.example.demo.exception;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;
import org.springframework.context.MessageSource;
import org.springframework.context.i18n.LocaleContextHolder;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.validation.BindException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;

import javax.servlet.*;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.validation.ConstraintViolationException;
import java.io.IOException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.util.*;

/**
 * 统一异常处理和日志记录完整示例
 * 
 * 演示企业级异常处理的核心功能：
 * 1. 统一异常处理机制
 * 2. 业务异常分类管理
 * 3. 结构化日志记录
 * 4. 异常信息国际化
 * 5. 请求追踪和调试信息
 * 6. 性能监控集成
 * 7. 安全异常处理
 */

/**
 * 业务异常基类
 * 提供统一的异常处理框架
 */
public abstract class BusinessException extends RuntimeException {
    
    private final String errorCode;
    private final Object[] args;
    private final Map<String, Object> details;
    
    protected BusinessException(String errorCode, String message, Object... args) {
        super(message);
        this.errorCode = errorCode;
        this.args = args;
        this.details = new HashMap<>();
    }
    
    protected BusinessException(String errorCode, String message, Throwable cause, Object... args) {
        super(message, cause);
        this.errorCode = errorCode;
        this.args = args;
        this.details = new HashMap<>();
    }
    
    public String getErrorCode() {
        return errorCode;
    }
    
    public Object[] getArgs() {
        return args;
    }
    
    public Map<String, Object> getDetails() {
        return details;
    }
    
    public BusinessException addDetail(String key, Object value) {
        this.details.put(key, value);
        return this;
    }
}

/**
 * 具体业务异常类定义
 */

/**
 * 用户相关异常
 */
public class UserNotFoundException extends BusinessException {
    public UserNotFoundException(Long userId) {
        super("USER_NOT_FOUND", "用户不存在: {0}", userId);
        addDetail("userId", userId);
    }
    
    public UserNotFoundException(String username) {
        super("USER_NOT_FOUND", "用户不存在: {0}", username);
        addDetail("username", username);
    }
}

public class UserAlreadyExistsException extends BusinessException {
    public UserAlreadyExistsException(String username) {
        super("USER_ALREADY_EXISTS", "用户名已存在: {0}", username);
        addDetail("username", username);
    }
}

public class InvalidCredentialsException extends BusinessException {
    public InvalidCredentialsException(String username) {
        super("INVALID_CREDENTIALS", "用户名或密码错误");
        addDetail("username", username);
        addDetail("attemptTime", LocalDateTime.now());
    }
}

/**
 * 数据相关异常
 */
public class DataValidationException extends BusinessException {
    public DataValidationException(String field, String message) {
        super("DATA_VALIDATION_ERROR", "数据验证失败: {0}", field);
        addDetail("field", field);
        addDetail("validationMessage", message);
    }
}

public class InsufficientDataException extends BusinessException {
    public InsufficientDataException(String dataType, int required, int actual) {
        super("INSUFFICIENT_DATA", "数据不足，需要 {0} 条 {1} 数据，实际只有 {2} 条", required, dataType, actual);
        addDetail("dataType", dataType);
        addDetail("required", required);
        addDetail("actual", actual);
    }
}

/**
 * 业务逻辑异常
 */
public class InvalidOperationException extends BusinessException {
    public InvalidOperationException(String operation, String reason) {
        super("INVALID_OPERATION", "操作无效: {0}，原因: {1}", operation, reason);
        addDetail("operation", operation);
        addDetail("reason", reason);
    }
}

public class ResourceConflictException extends BusinessException {
    public ResourceConflictException(String resourceType, Object resourceId) {
        super("RESOURCE_CONFLICT", "资源冲突: {0} ID={1}", resourceType, resourceId);
        addDetail("resourceType", resourceType);
        addDetail("resourceId", resourceId);
    }
}

/**
 * 全局异常处理器
 * 统一处理所有异常，提供一致的错误响应格式
 */
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);
    
    private final MessageSource messageSource;
    private final AuditLogService auditLogService;
    private final ObjectMapper objectMapper;
    
    public GlobalExceptionHandler(MessageSource messageSource,
                                AuditLogService auditLogService,
                                ObjectMapper objectMapper) {
        this.messageSource = messageSource;
        this.auditLogService = auditLogService;
        this.objectMapper = objectMapper;
    }
    
    /**
     * 处理业务异常
     */
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(
            BusinessException ex, HttpServletRequest request, WebRequest webRequest) {
        
        String requestId = MDC.get("requestId");
        
        // 记录业务异常日志
        log.warn("业务异常 - RequestId: {}, ErrorCode: {}, Message: {}, Details: {}", 
                requestId, ex.getErrorCode(), ex.getMessage(), ex.getDetails(), ex);
        
        // 记录审计日志
        auditLogService.logException("BUSINESS_EXCEPTION", ex.getErrorCode(), ex.getMessage(), ex.getDetails());
        
        // 获取国际化消息
        String localizedMessage = getLocalizedMessage(ex.getErrorCode(), ex.getArgs());
        
        ErrorResponse errorResponse = ErrorResponse.builder()
                .success(false)
                .errorCode(ex.getErrorCode())
                .message(localizedMessage)
                .details(ex.getDetails())
                .requestId(requestId)
                .timestamp(System.currentTimeMillis())
                .path(request.getRequestURI())
                .method(request.getMethod())
                .build();
        
        return ResponseEntity.badRequest().body(errorResponse);
    }
    
    /**
     * 处理参数验证异常
     */
    @ExceptionHandler({MethodArgumentNotValidException.class, BindException.class})
    public ResponseEntity<ErrorResponse> handleValidationException(
            Exception ex, HttpServletRequest request) {
        
        String requestId = MDC.get("requestId");
        Map<String, String> fieldErrors = new HashMap<>();
        
        if (ex instanceof MethodArgumentNotValidException) {
            MethodArgumentNotValidException validationEx = (MethodArgumentNotValidException) ex;
            validationEx.getBindingResult().getFieldErrors().forEach(error -> {
                fieldErrors.put(error.getField(), error.getDefaultMessage());
            });
        } else if (ex instanceof BindException) {
            BindException bindEx = (BindException) ex;
            bindEx.getBindingResult().getFieldErrors().forEach(error -> {
                fieldErrors.put(error.getField(), error.getDefaultMessage());
            });
        }
        
        log.warn("参数验证异常 - RequestId: {}, Errors: {}", requestId, fieldErrors);
        
        ErrorResponse errorResponse = ErrorResponse.builder()
                .success(false)
                .errorCode("VALIDATION_ERROR")
                .message("请求参数验证失败")
                .details(Collections.singletonMap("fieldErrors", fieldErrors))
                .requestId(requestId)
                .timestamp(System.currentTimeMillis())
                .path(request.getRequestURI())
                .method(request.getMethod())
                .build();
        
        return ResponseEntity.badRequest().body(errorResponse);
    }
    
    /**
     * 处理约束违反异常
     */
    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<ErrorResponse> handleConstraintViolationException(
            ConstraintViolationException ex, HttpServletRequest request) {
        
        String requestId = MDC.get("requestId");
        Map<String, String> violations = new HashMap<>();
        
        ex.getConstraintViolations().forEach(violation -> {
            violations.put(violation.getPropertyPath().toString(), violation.getMessage());
        });
        
        log.warn("约束违反异常 - RequestId: {}, Violations: {}", requestId, violations);
        
        ErrorResponse errorResponse = ErrorResponse.builder()
                .success(false)
                .errorCode("CONSTRAINT_VIOLATION")
                .message("数据约束违反")
                .details(Collections.singletonMap("violations", violations))
                .requestId(requestId)
                .timestamp(System.currentTimeMillis())
                .path(request.getRequestURI())
                .method(request.getMethod())
                .build();
        
        return ResponseEntity.badRequest().body(errorResponse);
    }
    
    /**
     * 处理访问权限异常
     */
    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ErrorResponse> handleAccessDeniedException(
            AccessDeniedException ex, HttpServletRequest request) {
        
        String requestId = MDC.get("requestId");
        String username = getCurrentUsername();
        
        log.warn("访问权限异常 - RequestId: {}, User: {}, Path: {}, Message: {}", 
                requestId, username, request.getRequestURI(), ex.getMessage());
        
        // 记录安全相关的审计日志
        Map<String, Object> securityDetails = new HashMap<>();
        securityDetails.put("username", username);
        securityDetails.put("requestPath", request.getRequestURI());
        securityDetails.put("method", request.getMethod());
        securityDetails.put("userAgent", request.getHeader("User-Agent"));
        securityDetails.put("remoteAddr", getClientIpAddress(request));
        
        auditLogService.logSecurityEvent("ACCESS_DENIED", ex.getMessage(), securityDetails);
        
        ErrorResponse errorResponse = ErrorResponse.builder()
                .success(false)
                .errorCode("ACCESS_DENIED")
                .message("访问权限不足")
                .requestId(requestId)
                .timestamp(System.currentTimeMillis())
                .path(request.getRequestURI())
                .method(request.getMethod())
                .build();
        
        return ResponseEntity.status(HttpStatus.FORBIDDEN).body(errorResponse);
    }
    
    /**
     * 处理数据完整性异常
     */
    @ExceptionHandler(DataIntegrityViolationException.class)
    public ResponseEntity<ErrorResponse> handleDataIntegrityViolationException(
            DataIntegrityViolationException ex, HttpServletRequest request) {
        
        String requestId = MDC.get("requestId");
        log.error("数据完整性约束违反 - RequestId: {}", requestId, ex);
        
        String userFriendlyMessage = "数据操作失败";
        String errorCode = "DATA_INTEGRITY_VIOLATION";
        
        if (ex.getMessage() != null) {
            if (ex.getMessage().contains("Duplicate entry")) {
                userFriendlyMessage = "数据已存在，无法重复添加";
                errorCode = "DUPLICATE_ENTRY";
            } else if (ex.getMessage().contains("foreign key constraint")) {
                userFriendlyMessage = "数据存在关联关系，无法删除";
                errorCode = "FOREIGN_KEY_CONSTRAINT";
            }
        }
        
        ErrorResponse errorResponse = ErrorResponse.builder()
                .success(false)
                .errorCode(errorCode)
                .message(userFriendlyMessage)
                .requestId(requestId)
                .timestamp(System.currentTimeMillis())
                .path(request.getRequestURI())
                .method(request.getMethod())
                .build();
        
        return ResponseEntity.badRequest().body(errorResponse);
    }
    
    /**
     * 处理通用系统异常
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(
            Exception ex, HttpServletRequest request) {
        
        String requestId = MDC.get("requestId");
        log.error("系统异常 - RequestId: {}, URL: {}, Method: {}, Exception: {}", 
                requestId, request.getRequestURL(), request.getMethod(), ex.getClass().getSimpleName(), ex);
        
        // 记录详细的系统错误信息
        Map<String, Object> systemDetails = new HashMap<>();
        systemDetails.put("exceptionClass", ex.getClass().getName());
        systemDetails.put("stackTrace", getStackTraceAsString(ex));
        systemDetails.put("requestParams", getRequestParameters(request));
        systemDetails.put("headers", getRequestHeaders(request));
        
        auditLogService.logSystemError("UNHANDLED_EXCEPTION", ex.getMessage(), systemDetails);
        
        ErrorResponse errorResponse = ErrorResponse.builder()
                .success(false)
                .errorCode("INTERNAL_SERVER_ERROR")
                .message("系统内部错误，请联系管理员")
                .requestId(requestId)
                .timestamp(System.currentTimeMillis())
                .path(request.getRequestURI())
                .method(request.getMethod())
                .build();
        
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
    }
    
    /**
     * 获取国际化消息
     */
    private String getLocalizedMessage(String errorCode, Object[] args) {
        try {
            Locale locale = LocaleContextHolder.getLocale();
            return messageSource.getMessage(errorCode, args, locale);
        } catch (Exception e) {
            log.warn("获取国际化消息失败，使用默认错误码: {}", errorCode);
            return errorCode;
        }
    }
    
    /**
     * 获取当前用户名
     */
    private String getCurrentUsername() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth != null && auth.getPrincipal() instanceof UserDetails) {
            return ((UserDetails) auth.getPrincipal()).getUsername();
        }
        return "anonymous";
    }
    
    /**
     * 获取客户端IP地址
     */
    private String getClientIpAddress(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty() && !"unknown".equalsIgnoreCase(xForwardedFor)) {
            return xForwardedFor.split(",")[0];
        }
        
        String xRealIP = request.getHeader("X-Real-IP");
        if (xRealIP != null && !xRealIP.isEmpty() && !"unknown".equalsIgnoreCase(xRealIP)) {
            return xRealIP;
        }
        
        return request.getRemoteAddr();
    }
    
    /**
     * 将异常堆栈转换为字符串
     */
    private String getStackTraceAsString(Exception ex) {
        java.io.StringWriter sw = new java.io.StringWriter();
        java.io.PrintWriter pw = new java.io.PrintWriter(sw);
        ex.printStackTrace(pw);
        return sw.toString();
    }
    
    /**
     * 获取请求参数
     */
    private Map<String, String[]> getRequestParameters(HttpServletRequest request) {
        return request.getParameterMap();
    }
    
    /**
     * 获取请求头信息
     */
    private Map<String, String> getRequestHeaders(HttpServletRequest request) {
        Map<String, String> headers = new HashMap<>();
        Enumeration<String> headerNames = request.getHeaderNames();
        while (headerNames.hasMoreElements()) {
            String headerName = headerNames.nextElement();
            headers.put(headerName, request.getHeader(headerName));
        }
        return headers;
    }
}

/**
 * 错误响应统一格式
 */
class ErrorResponse {
    private boolean success;
    private String errorCode;
    private String message;
    private Map<String, Object> details;
    private String requestId;
    private Long timestamp;
    private String path;
    private String method;
    
    public static ErrorResponseBuilder builder() {
        return new ErrorResponseBuilder();
    }
    
    public static class ErrorResponseBuilder {
        private ErrorResponse response = new ErrorResponse();
        
        public ErrorResponseBuilder success(boolean success) { response.success = success; return this; }
        public ErrorResponseBuilder errorCode(String errorCode) { response.errorCode = errorCode; return this; }
        public ErrorResponseBuilder message(String message) { response.message = message; return this; }
        public ErrorResponseBuilder details(Map<String, Object> details) { response.details = details; return this; }
        public ErrorResponseBuilder requestId(String requestId) { response.requestId = requestId; return this; }
        public ErrorResponseBuilder timestamp(Long timestamp) { response.timestamp = timestamp; return this; }
        public ErrorResponseBuilder path(String path) { response.path = path; return this; }
        public ErrorResponseBuilder method(String method) { response.method = method; return this; }
        
        public ErrorResponse build() { return response; }
    }
    
    // Getter方法
    public boolean isSuccess() { return success; }
    public String getErrorCode() { return errorCode; }
    public String getMessage() { return message; }
    public Map<String, Object> getDetails() { return details; }
    public String getRequestId() { return requestId; }
    public Long getTimestamp() { return timestamp; }
    public String getPath() { return path; }
    public String getMethod() { return method; }
}

/**
 * 请求追踪过滤器
 * 为每个请求生成唯一ID，便于日志追踪
 */
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class RequestTrackingFilter implements Filter {
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) 
            throws IOException, ServletException {
        
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        HttpServletResponse httpResponse = (HttpServletResponse) response;
        
        // 生成唯一请求ID
        String requestId = UUID.randomUUID().toString().substring(0, 8);
        MDC.put("requestId", requestId);
        
        // 记录请求开始时间
        long startTime = System.currentTimeMillis();
        MDC.put("requestStartTime", String.valueOf(startTime));
        
        try {
            // 在响应头中添加请求ID
            httpResponse.setHeader("X-Request-Id", requestId);
            
            // 记录请求信息
            logRequestInfo(httpRequest, requestId);
            
            chain.doFilter(request, response);
            
            // 记录响应信息
            long duration = System.currentTimeMillis() - startTime;
            logResponseInfo(httpRequest, httpResponse, requestId, duration);
            
        } finally {
            // 清理MDC
            MDC.clear();
        }
    }
    
    private void logRequestInfo(HttpServletRequest request, String requestId) {
        if (log.isDebugEnabled()) {
            log.debug("请求开始 - RequestId: {}, Method: {}, URI: {}, RemoteAddr: {}, UserAgent: {}", 
                    requestId, 
                    request.getMethod(), 
                    request.getRequestURI(), 
                    getClientIpAddress(request), 
                    request.getHeader("User-Agent"));
        }
    }
    
    private void logResponseInfo(HttpServletRequest request, HttpServletResponse response, 
                               String requestId, long duration) {
        log.info("请求完成 - RequestId: {}, Method: {}, URI: {}, Status: {}, Duration: {}ms", 
                requestId, 
                request.getMethod(), 
                request.getRequestURI(), 
                response.getStatus(), 
                duration);
        
        // 如果响应时间过长，记录警告日志
        if (duration > 5000) {
            log.warn("慢请求警告 - RequestId: {}, Duration: {}ms, URI: {}", 
                    requestId, duration, request.getRequestURI());
        }
    }
    
    private String getClientIpAddress(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty()) {
            return xForwardedFor.split(",")[0];
        }
        return request.getRemoteAddr();
    }
}

/**
 * 审计日志服务
 * 记录系统中的重要事件和异常
 */
@Service
public class AuditLogService {
    
    private static final Logger auditLogger = LoggerFactory.getLogger("AUDIT");
    private static final Logger securityLogger = LoggerFactory.getLogger("SECURITY");
    private static final Logger performanceLogger = LoggerFactory.getLogger("PERFORMANCE");
    
    private final ObjectMapper objectMapper;
    
    public AuditLogService(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }
    
    /**
     * 记录异常日志
     */
    public void logException(String exceptionType, String errorCode, String message, Map<String, Object> details) {
        try {
            AuditLogEntry entry = AuditLogEntry.builder()
                    .timestamp(Instant.now())
                    .requestId(MDC.get("requestId"))
                    .eventType("EXCEPTION")
                    .exceptionType(exceptionType)
                    .errorCode(errorCode)
                    .message(message)
                    .details(details)
                    .username(getCurrentUsername())
                    .build();
                    
            auditLogger.error("EXCEPTION_LOG {}", objectMapper.writeValueAsString(entry));
            
        } catch (Exception e) {
            auditLogger.error("记录异常日志失败", e);
        }
    }
    
    /**
     * 记录安全事件
     */
    public void logSecurityEvent(String eventType, String message, Map<String, Object> details) {
        try {
            SecurityLogEntry entry = SecurityLogEntry.builder()
                    .timestamp(Instant.now())
                    .requestId(MDC.get("requestId"))
                    .eventType(eventType)
                    .message(message)
                    .details(details)
                    .severity("HIGH")
                    .build();
                    
            securityLogger.warn("SECURITY_EVENT {}", objectMapper.writeValueAsString(entry));
            
        } catch (Exception e) {
            securityLogger.error("记录安全事件失败", e);
        }
    }
    
    /**
     * 记录系统错误
     */
    public void logSystemError(String errorType, String message, Map<String, Object> details) {
        try {
            SystemErrorLogEntry entry = SystemErrorLogEntry.builder()
                    .timestamp(Instant.now())
                    .requestId(MDC.get("requestId"))
                    .errorType(errorType)
                    .message(message)
                    .details(details)
                    .serverInstance(getServerInstance())
                    .build();
                    
            auditLogger.error("SYSTEM_ERROR {}", objectMapper.writeValueAsString(entry));
            
        } catch (Exception e) {
            auditLogger.error("记录系统错误失败", e);
        }
    }
    
    /**
     * 记录性能指标
     */
    public void logPerformanceMetrics(String operation, long duration, Map<String, Object> context) {
        try {
            PerformanceLogEntry entry = PerformanceLogEntry.builder()
                    .timestamp(Instant.now())
                    .requestId(MDC.get("requestId"))
                    .operation(operation)
                    .duration(duration)
                    .context(context)
                    .build();
                    
            if (duration > 5000) {
                performanceLogger.warn("PERFORMANCE_SLOW {}", objectMapper.writeValueAsString(entry));
            } else {
                performanceLogger.info("PERFORMANCE {}", objectMapper.writeValueAsString(entry));
            }
            
        } catch (Exception e) {
            performanceLogger.error("记录性能日志失败", e);
        }
    }
    
    private String getCurrentUsername() {
        try {
            Authentication auth = SecurityContextHolder.getContext().getAuthentication();
            if (auth != null && auth.getPrincipal() instanceof UserDetails) {
                return ((UserDetails) auth.getPrincipal()).getUsername();
            }
        } catch (Exception e) {
            // 忽略异常，返回默认值
        }
        return "system";
    }
    
    private String getServerInstance() {
        try {
            return InetAddress.getLocalHost().getHostName();
        } catch (Exception e) {
            return "unknown";
        }
    }
}

/**
 * 日志条目类定义
 */

/**
 * 审计日志条目
 */
class AuditLogEntry {
    private Instant timestamp;
    private String requestId;
    private String eventType;
    private String exceptionType;
    private String errorCode;
    private String message;
    private Map<String, Object> details;
    private String username;
    
    public static AuditLogEntryBuilder builder() {
        return new AuditLogEntryBuilder();
    }
    
    public static class AuditLogEntryBuilder {
        private AuditLogEntry entry = new AuditLogEntry();
        
        public AuditLogEntryBuilder timestamp(Instant timestamp) { entry.timestamp = timestamp; return this; }
        public AuditLogEntryBuilder requestId(String requestId) { entry.requestId = requestId; return this; }
        public AuditLogEntryBuilder eventType(String eventType) { entry.eventType = eventType; return this; }
        public AuditLogEntryBuilder exceptionType(String exceptionType) { entry.exceptionType = exceptionType; return this; }
        public AuditLogEntryBuilder errorCode(String errorCode) { entry.errorCode = errorCode; return this; }
        public AuditLogEntryBuilder message(String message) { entry.message = message; return this; }
        public AuditLogEntryBuilder details(Map<String, Object> details) { entry.details = details; return this; }
        public AuditLogEntryBuilder username(String username) { entry.username = username; return this; }
        
        public AuditLogEntry build() { return entry; }
    }
    
    // Getter方法
    public Instant getTimestamp() { return timestamp; }
    public String getRequestId() { return requestId; }
    public String getEventType() { return eventType; }
    public String getExceptionType() { return exceptionType; }
    public String getErrorCode() { return errorCode; }
    public String getMessage() { return message; }
    public Map<String, Object> getDetails() { return details; }
    public String getUsername() { return username; }
}

/**
 * 安全日志条目
 */
class SecurityLogEntry {
    private Instant timestamp;
    private String requestId;
    private String eventType;
    private String message;
    private Map<String, Object> details;
    private String severity;
    
    public static SecurityLogEntryBuilder builder() {
        return new SecurityLogEntryBuilder();
    }
    
    public static class SecurityLogEntryBuilder {
        private SecurityLogEntry entry = new SecurityLogEntry();
        
        public SecurityLogEntryBuilder timestamp(Instant timestamp) { entry.timestamp = timestamp; return this; }
        public SecurityLogEntryBuilder requestId(String requestId) { entry.requestId = requestId; return this; }
        public SecurityLogEntryBuilder eventType(String eventType) { entry.eventType = eventType; return this; }
        public SecurityLogEntryBuilder message(String message) { entry.message = message; return this; }
        public SecurityLogEntryBuilder details(Map<String, Object> details) { entry.details = details; return this; }
        public SecurityLogEntryBuilder severity(String severity) { entry.severity = severity; return this; }
        
        public SecurityLogEntry build() { return entry; }
    }
    
    // Getter方法省略...
}

/**
 * 系统错误日志条目
 */
class SystemErrorLogEntry {
    private Instant timestamp;
    private String requestId;
    private String errorType;
    private String message;
    private Map<String, Object> details;
    private String serverInstance;
    
    public static SystemErrorLogEntryBuilder builder() {
        return new SystemErrorLogEntryBuilder();
    }
    
    public static class SystemErrorLogEntryBuilder {
        private SystemErrorLogEntry entry = new SystemErrorLogEntry();
        
        public SystemErrorLogEntryBuilder timestamp(Instant timestamp) { entry.timestamp = timestamp; return this; }
        public SystemErrorLogEntryBuilder requestId(String requestId) { entry.requestId = requestId; return this; }
        public SystemErrorLogEntryBuilder errorType(String errorType) { entry.errorType = errorType; return this; }
        public SystemErrorLogEntryBuilder message(String message) { entry.message = message; return this; }
        public SystemErrorLogEntryBuilder details(Map<String, Object> details) { entry.details = details; return this; }
        public SystemErrorLogEntryBuilder serverInstance(String serverInstance) { entry.serverInstance = serverInstance; return this; }
        
        public SystemErrorLogEntry build() { return entry; }
    }
    
    // Getter方法省略...
}

/**
 * 性能日志条目
 */
class PerformanceLogEntry {
    private Instant timestamp;
    private String requestId;
    private String operation;
    private long duration;
    private Map<String, Object> context;
    
    public static PerformanceLogEntryBuilder builder() {
        return new PerformanceLogEntryBuilder();
    }
    
    public static class PerformanceLogEntryBuilder {
        private PerformanceLogEntry entry = new PerformanceLogEntry();
        
        public PerformanceLogEntryBuilder timestamp(Instant timestamp) { entry.timestamp = timestamp; return this; }
        public PerformanceLogEntryBuilder requestId(String requestId) { entry.requestId = requestId; return this; }
        public PerformanceLogEntryBuilder operation(String operation) { entry.operation = operation; return this; }
        public PerformanceLogEntryBuilder duration(long duration) { entry.duration = duration; return this; }
        public PerformanceLogEntryBuilder context(Map<String, Object> context) { entry.context = context; return this; }
        
        public PerformanceLogEntry build() { return entry; }
    }
    
    // Getter方法省略...
}