package edu.example.lesson52;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * S3 阶段起点：教材清单 5.1（返回写死的对象列表）与清单 5.2（路径参数、查询参数与契约错误体）
 * 合并成的一个可运行的类——书中第二个清单的注释写着“放在 AssetController 里”，这里就是那个类。
 * 除合并所需的 import 外，方法体与书中逐字一致。
 *
 * 它只做三件事：把方法暴露成 HTTP 接口、按契约区分 200/204/400/404、把异常翻译成 {code, message, field?}。
 * 数据库在 5.4 节接入，认证在 5.6 节接入；在那之前这个类就是第4章页面的真实后端。
 */
@RestController
@RequestMapping("/api/assets")
public class AssetController {
    /** 与 8.1 节契约表同名的字段；record 自动生成构造器与访问方法 */
    public record AssetDto(String assetId, String displayName,
                           String assetType, String unit) {}

    private static final List<AssetDto> FIXED = List.of(
        new AssetDto("DAM-A-PZ-07", "案例渗压07", "渗压", "kPa"),
        new AssetDto("DAM-A-WL-01", "案例库水位01", "库水位", "m"),
        new AssetDto("DAM-A-D-01", "案例位移01", "位移", "mm"),
        new AssetDto("DAM-A-RF-01", "案例雨量01", "雨量", "mm"));

    @GetMapping                      // GET /api/assets
    public List<AssetDto> assets() {
        return FIXED;
    }

    public record ReadingDto(String assetId, OffsetDateTime occurredAt, Double value,
                             String unit, String quality, String eventId, int version) {}

    @GetMapping("/{assetId}/readings/latest")
    public ResponseEntity<ReadingDto> latest(@PathVariable String assetId) {
        AssetDto asset = FIXED.stream().filter(a -> a.assetId().equals(assetId))
            .findFirst().orElseThrow(() -> new NotFound("ASSET_NOT_FOUND", "对象 " + assetId + " 不存在"));
        if (!asset.assetId().equals("DAM-A-PZ-07")) return ResponseEntity.noContent().build(); // 契约：无观测 204
        return ResponseEntity.ok(new ReadingDto(asset.assetId(),
            OffsetDateTime.parse("2026-07-01T23:55:00+08:00"), 185.091, "kPa", "valid", "evt-pz-0287-6", 1));
    }

    @GetMapping("/{assetId}/readings")
    public List<ReadingDto> readings(@PathVariable String assetId,
                                     @RequestParam OffsetDateTime from,
                                     @RequestParam OffsetDateTime to) {
        if (!from.isBefore(to)) throw new BadRequest("INVALID_RANGE", "from 必须早于 to", "from");
        return List.of();   // 5.4 节改为查数据库
    }

    // —— 两个最小异常与它们到 HTTP 的翻译 ——
    static class NotFound extends RuntimeException {
        final String code; NotFound(String code, String msg) { super(msg); this.code = code; }
    }
    static class BadRequest extends RuntimeException {
        final String code, field;
        BadRequest(String code, String msg, String field) { super(msg); this.code = code; this.field = field; }
    }
    @ExceptionHandler(NotFound.class)
    ResponseEntity<Map<String, String>> notFound(NotFound e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("code", e.code, "message", e.getMessage()));
    }
    @ExceptionHandler(BadRequest.class)
    ResponseEntity<Map<String, String>> badRequest(BadRequest e) {
        return ResponseEntity.badRequest().body(Map.of("code", e.code, "message", e.getMessage(), "field", e.field));
    }
}
