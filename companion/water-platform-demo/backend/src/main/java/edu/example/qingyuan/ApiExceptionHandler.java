package edu.example.qingyuan;

import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
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

    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<Map<String, String>> invalid(MethodArgumentNotValidException e) {
        String field = e.getBindingResult().getFieldErrors().stream()
                .map(org.springframework.validation.FieldError::getField).findFirst().orElse(null);
        return body(HttpStatus.BAD_REQUEST, "VALIDATION_ERROR", "请求参数无效", field);
    }

    /** 路径写错（例如 /api/asset 少一个 s）也要返回契约错误体，而不是 Spring 的默认页面。 */
    @ExceptionHandler(NoResourceFoundException.class)
    ResponseEntity<Map<String, String>> noResource(NoResourceFoundException e) {
        return body(HttpStatus.NOT_FOUND, "NOT_FOUND", "请求的路径不存在", null);
    }

    /** 兜底：技术细节留在服务端日志，响应体只给稳定错误码。 */
    @ExceptionHandler(Exception.class)
    ResponseEntity<Map<String, String>> unexpected(Exception e) {
        org.slf4j.LoggerFactory.getLogger(ApiExceptionHandler.class)
                .error("未处理的服务端异常", e);
        return body(HttpStatus.INTERNAL_SERVER_ERROR, "INTERNAL_ERROR", "服务端处理失败", null);
    }
}
