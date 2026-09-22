package edu.example.qingyuan;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingRequestHeaderException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.servlet.resource.NoResourceFoundException;

/**
 * 契约错误体（8.1 节 tab:api-contract 的“通用约定”）：{code, message, field?}。
 *
 * 教学接口 teaching-api、S3 起点（edu.example.lesson52）和本工程必须产出同一形状的错误体，
 * 否则第4章的页面换数据源就要改错误分支——那样契约就没有意义了。
 * 这三个来源的一致性由 teaching-api/contract-check.mjs 逐条核对。
 *
 * 注意 MethodArgumentTypeMismatchException：5.2.2 节“一个会遇到的失败”说的就是它。
 * 时间参数解析失败发生在进入控制器方法之前，控制器里的 @ExceptionHandler 接不到，
 * 只有 @RestControllerAdvice 这一层能兜住。
 */
@RestControllerAdvice
public class ApiExceptionHandler {

    private static ResponseEntity<Map<String, String>> body(
            HttpStatus status, String code, String message, String field) {
        Map<String, String> payload = new LinkedHashMap<>();
        payload.put("code", code);
        payload.put("message", message);
        if (field != null) payload.put("field", field);
        return ResponseEntity.status(status).body(payload);
    }

    @ExceptionHandler(AssetController.AssetNotFoundException.class)
    ResponseEntity<Map<String, String>> assetNotFound(AssetController.AssetNotFoundException e) {
        return body(HttpStatus.NOT_FOUND, "ASSET_NOT_FOUND", e.getMessage(), null);
    }

    @ExceptionHandler(AssetController.InvalidRangeException.class)
    ResponseEntity<Map<String, String>> invalidRange(AssetController.InvalidRangeException e) {
        return body(HttpStatus.BAD_REQUEST, "INVALID_RANGE", e.getMessage(), "from");
    }

    /** 服务层的业务规则（5.5.1 节 ManualReadingService）：错误码和出错字段由异常自己带出。 */
    @ExceptionHandler(ManualReadingService.RuleViolation.class)
    ResponseEntity<Map<String, String>> ruleViolation(ManualReadingService.RuleViolation e) {
        return body(HttpStatus.BAD_REQUEST, e.code, e.getMessage(), e.field);
    }

    @ExceptionHandler(ManualReadingService.ReadingExists.class)
    ResponseEntity<Map<String, String>> readingExists(ManualReadingService.ReadingExists e) {
        return body(HttpStatus.CONFLICT, "READING_EXISTS", e.getMessage(), null);
    }

    /** from/to 写成不合法的时间格式，或把 + 号原样放进地址栏时走这里。 */
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    ResponseEntity<Map<String, String>> typeMismatch(MethodArgumentTypeMismatchException e) {
        return body(HttpStatus.BAD_REQUEST, "INVALID_PARAMETER",
                "参数 " + e.getName() + " 的取值无法解析，时间参数需为 ISO-8601 带时区格式", e.getName());
    }

    @ExceptionHandler(MissingServletRequestParameterException.class)
    ResponseEntity<Map<String, String>> missing(MissingServletRequestParameterException e) {
        return body(HttpStatus.BAD_REQUEST, "FIELD_REQUIRED",
                "缺少必填参数 " + e.getParameterName(), e.getParameterName());
    }

    /** 补录接口要求的 Idempotency-Key 头没有带上：与缺查询参数同样处理。 */
    @ExceptionHandler(MissingRequestHeaderException.class)
    ResponseEntity<Map<String, String>> missingHeader(MissingRequestHeaderException e) {
        return body(HttpStatus.BAD_REQUEST, "FIELD_REQUIRED",
                "缺少必填请求头 " + e.getHeaderName(), e.getHeaderName());
    }

    /** 这三种注解表达的都是“字段必须有”，它们的失败按契约算 FIELD_REQUIRED。 */
    private static final Set<String> PRESENCE_CONSTRAINTS = Set.of("NotNull", "NotBlank", "NotEmpty");

    /**
     * @Valid 请求体校验失败。FieldError.getCode() 是触发失败的注解名：
     * 缺字段（NotNull/NotBlank/NotEmpty）应答 FIELD_REQUIRED，与教学接口和 closeloop-check.mjs 一致；
     * 字段有值但不合形状（Pattern、DecimalMin 等）应答 VALIDATION_ERROR。
     * 契约的 field 是单数，取第一个出错的字段，页面据此定位输入框。
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<Map<String, String>> invalid(MethodArgumentNotValidException e) {
        FieldError first = e.getBindingResult().getFieldError();
        if (first == null) {
            return body(HttpStatus.BAD_REQUEST, "VALIDATION_ERROR", "请求参数无效", null);
        }
        if (PRESENCE_CONSTRAINTS.contains(first.getCode())) {
            return body(HttpStatus.BAD_REQUEST, "FIELD_REQUIRED",
                    "缺少必填字段 " + first.getField(), first.getField());
        }
        return body(HttpStatus.BAD_REQUEST, "VALIDATION_ERROR", "请求参数无效", first.getField());
    }

    /** 路径写错（例如 /api/asset 少一个 s）也要返回契约错误体，而不是 Spring 的默认页面。 */
    @ExceptionHandler(NoResourceFoundException.class)
    ResponseEntity<Map<String, String>> noResource(NoResourceFoundException e) {
        return body(HttpStatus.NOT_FOUND, "NOT_FOUND", "请求的路径不存在", null);
    }

    /**
     * 显式抛出的 ResponseStatusException 要保留它自己的状态码。
     * 这个处理器必须存在：否则它会落到下面的兜底分支，
     * 登录失败本该返回的 401 会被翻译成 500——错误口令看起来像服务端故障。
     */
    @ExceptionHandler(org.springframework.web.server.ResponseStatusException.class)
    ResponseEntity<Map<String, String>> statusException(
            org.springframework.web.server.ResponseStatusException e) {
        HttpStatus status = HttpStatus.valueOf(e.getStatusCode().value());
        String code = status == HttpStatus.UNAUTHORIZED ? "UNAUTHORIZED"
                : status == HttpStatus.FORBIDDEN ? "FORBIDDEN"
                : status == HttpStatus.NOT_FOUND ? "NOT_FOUND"
                : status == HttpStatus.CONFLICT ? "CONFLICT" : "REQUEST_REJECTED";
        return body(status, code, e.getReason() == null ? status.getReasonPhrase() : e.getReason(), null);
    }

    /**
     * @PreAuthorize 拒绝访问时抛出的 AccessDeniedException 发生在调用控制器方法的过程中，
     * Spring MVC 会先在本类里找处理器；没有这一条时它会落到下面的兜底分支，
     * 分析员调用只允许值班员调用的接口得到的就是 500 而不是 403，
     * SecurityConfig 里的 accessDeniedHandler 也没有机会处理。测试见 ReadingWriteControllerTest。
     */
    @ExceptionHandler(AccessDeniedException.class)
    ResponseEntity<Map<String, String>> accessDenied(AccessDeniedException e) {
        return body(HttpStatus.FORBIDDEN, "FORBIDDEN", "当前角色无权执行该操作", null);
    }

    /** 同理：控制器或服务层里抛出的认证异常保持 401，不能翻译成 500。 */
    @ExceptionHandler(AuthenticationException.class)
    ResponseEntity<Map<String, String>> unauthenticated(AuthenticationException e) {
        return body(HttpStatus.UNAUTHORIZED, "UNAUTHORIZED", "未登录或令牌已失效", null);
    }

    /** 兜底：技术细节留在服务端日志，响应体只给稳定错误码。 */
    @ExceptionHandler(Exception.class)
    ResponseEntity<Map<String, String>> unexpected(Exception e) {
        org.slf4j.LoggerFactory.getLogger(ApiExceptionHandler.class)
                .error("未处理的服务端异常", e);
        return body(HttpStatus.INTERNAL_SERVER_ERROR, "INTERNAL_ERROR", "服务端处理失败", null);
    }
}
