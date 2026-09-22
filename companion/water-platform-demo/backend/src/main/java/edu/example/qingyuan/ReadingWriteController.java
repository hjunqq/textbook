package edu.example.qingyuan;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import java.math.BigDecimal;
import java.time.OffsetDateTime;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 契约 POST /api/readings（8.1 节 tab:api-contract）：专业分析员人工补录一条观测。
 * 教材 5.5.1 节逐行讲解本类；三层校验的分工见 5.5.3 节表 tab:ch05-error-codes。
 *
 * 表示层只检查请求体的形状（Bean Validation 注解 + @Valid）；
 * 单位是否与台账一致、缺测才允许没有数值、该时刻是否已有观测，都在 ManualReadingService 里判断。
 */
@RestController
@RequestMapping("/api/readings")
public class ReadingWriteController {
    public record CreateReadingRequest(
            @NotBlank String assetId,
            @NotNull OffsetDateTime occurredAt,
            BigDecimal value,          // 缺测时为 null；能不能为空取决于 quality，由服务层判断
            @NotBlank String unit,
            @NotNull @Pattern(regexp = "valid|suspect|missing") String quality) {}

    private final ManualReadingService service;
    public ReadingWriteController(ManualReadingService service) { this.service = service; }

    @PostMapping
    @PreAuthorize("hasAuthority('ANALYST')")           // 契约：补录与订正限专业分析员
    public ResponseEntity<AssetController.ReadingDto> create(
            @RequestHeader("Idempotency-Key") String key,
            @Valid @RequestBody CreateReadingRequest body) {
        ReadingEntity saved = service.record(body, key);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(AssetController.ReadingDto.from(saved));
    }
}
