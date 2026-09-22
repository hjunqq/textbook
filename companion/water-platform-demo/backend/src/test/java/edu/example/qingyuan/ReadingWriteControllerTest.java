package edu.example.qingyuan;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;

/**
 * 5.5.2 节统一错误体与 5.9.2 节权限测试的落地：
 * 只装入 ReadingWriteController 与安全配置，服务层换成假的，数据库和 Kafka 都不参与。
 * 断言错误码而不断言 message 文字，文案调整时测试不必跟着改。
 */
@WebMvcTest(ReadingWriteController.class)
@Import(SecurityConfig.class)
class ReadingWriteControllerTest {
    @Autowired MockMvc mockMvc;
    @MockBean ManualReadingService service;

    private static final String KEY = "manual-pz07-20260701-0001";

    private static MockHttpServletRequestBuilder postReading(String json) {
        return post("/api/readings")
                .header("Idempotency-Key", KEY)
                .contentType(MediaType.APPLICATION_JSON)
                .content(json);
    }

    @Test
    @WithMockUser(authorities = "ANALYST")
    void validBodyIsCreated() throws Exception {
        ReadingEntity saved = new ReadingEntity(
                new ReadingEntity.ReadingId("DAM-A-PZ-07",
                        OffsetDateTime.parse("2026-07-01T08:00:00+08:00"), 1),
                KEY, new BigDecimal("185.091"), "kPa", "valid", "manual");
        when(service.record(any(), eq(KEY))).thenReturn(saved);
        mockMvc.perform(postReading("""
                {"assetId":"DAM-A-PZ-07","occurredAt":"2026-07-01T08:00:00+08:00",
                 "value":185.091,"unit":"kPa","quality":"valid"}
                """))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.assetId").value("DAM-A-PZ-07"))
                .andExpect(jsonPath("$.eventId").value(KEY))
                .andExpect(jsonPath("$.unit").value("kPa"));
    }

    /** 缺 @NotBlank 字段：契约错误码是 FIELD_REQUIRED，field 指出缺的是哪一个。 */
    @Test
    @WithMockUser(authorities = "ANALYST")
    void missingRequiredFieldIsFieldRequired() throws Exception {
        mockMvc.perform(postReading("""
                {"occurredAt":"2026-07-01T08:00:00+08:00",
                 "value":185.091,"unit":"kPa","quality":"valid"}
                """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("FIELD_REQUIRED"))
                .andExpect(jsonPath("$.field").value("assetId"));
        verifyNoInteractions(service);
    }

    /** 字段有值但不合形状（@Pattern 失败）：VALIDATION_ERROR，field 同样指出字段。 */
    @Test
    @WithMockUser(authorities = "ANALYST")
    void malformedFieldIsValidationError() throws Exception {
        mockMvc.perform(postReading("""
                {"assetId":"DAM-A-PZ-07","occurredAt":"2026-07-01T08:00:00+08:00",
                 "value":185.091,"unit":"kPa","quality":"bogus"}
                """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("VALIDATION_ERROR"))
                .andExpect(jsonPath("$.field").value("quality"));
        verifyNoInteractions(service);
    }

    /** 没带 Idempotency-Key 头：与缺查询参数同样按 FIELD_REQUIRED 处理。 */
    @Test
    @WithMockUser(authorities = "ANALYST")
    void missingIdempotencyKeyIsFieldRequired() throws Exception {
        mockMvc.perform(post("/api/readings")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                {"assetId":"DAM-A-PZ-07","occurredAt":"2026-07-01T08:00:00+08:00",
                 "value":185.091,"unit":"kPa","quality":"valid"}
                """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("FIELD_REQUIRED"))
                .andExpect(jsonPath("$.field").value("Idempotency-Key"));
        verifyNoInteractions(service);
    }

    /**
     * 值班员调用只对分析员开放的接口：@PreAuthorize 在调用控制器方法时抛出 AccessDeniedException，
     * ApiExceptionHandler 必须把它翻译成 403 FORBIDDEN，而不是落进兜底分支变成 500。
     */
    @Test
    @WithMockUser(authorities = "DUTY")
    void userWithoutAuthorityIs403NotInternalError() throws Exception {
        mockMvc.perform(postReading("""
                {"assetId":"DAM-A-PZ-07","occurredAt":"2026-07-01T08:00:00+08:00",
                 "value":185.091,"unit":"kPa","quality":"valid"}
                """))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.code").value("FORBIDDEN"));
        verifyNoInteractions(service);
    }

    /** 未登录在过滤器链就被拒绝：401 与 UNAUTHORIZED，由 SecurityConfig 直接写出错误体。 */
    @Test
    void anonymousRequestIs401() throws Exception {
        mockMvc.perform(postReading("{}"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.code").value("UNAUTHORIZED"));
        verifyNoInteractions(service);
    }
}
