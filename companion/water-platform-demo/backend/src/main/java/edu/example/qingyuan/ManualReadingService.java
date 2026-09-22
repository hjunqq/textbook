package edu.example.qingyuan;

import edu.example.qingyuan.ReadingWriteController.CreateReadingRequest;
import java.time.OffsetDateTime;
import java.util.Optional;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 人工补录的服务层规则（教材 5.5.1 节“第二层”）。
 * 这里不出现任何 HTTP 类型：异常怎样变成状态码由 ApiExceptionHandler 决定。
 * 消息消费者走的是 ReadingService.accept，不经过本类；数据库约束是两条路径共用的最后一道关。
 */
@Service
public class ManualReadingService {
    /** 违反业务规则：由统一异常处理转成 400，code 与 field 原样带出。 */
    public static class RuleViolation extends RuntimeException {
        public final String code, field;
        public RuleViolation(String code, String message, String field) {
            super(message); this.code = code; this.field = field;
        }
    }
    /** 该对象在这一时刻已有观测：转成 409 READING_EXISTS。 */
    public static class ReadingExists extends RuntimeException {
        public ReadingExists(String assetId, OffsetDateTime occurredAt) {
            super("对象 " + assetId + " 在 " + occurredAt + " 已有观测，更正请走订正");
        }
    }

    private final AssetRepository assets;
    private final ReadingRepository readings;
    public ManualReadingService(AssetRepository assets, ReadingRepository readings) {
        this.assets = assets; this.readings = readings;
    }

    @Transactional
    public ReadingEntity record(CreateReadingRequest body, String idempotencyKey) {
        AssetEntity asset = assets.findById(body.assetId()).filter(AssetEntity::isActive)
                .orElseThrow(() -> new AssetController.AssetNotFoundException(body.assetId()));
        if (!body.unit().equals(asset.getUnit()))
            throw new RuleViolation("UNIT_MISMATCH",
                    "对象 " + asset.getAssetId() + " 的单位是 " + asset.getUnit(), "unit");
        if (body.value() == null && !"missing".equals(body.quality()))
            throw new RuleViolation("VALUE_REQUIRED", "只有缺测（missing）的观测可以没有数值", "value");

        Optional<ReadingEntity> replay = readings.findByEventId(idempotencyKey);  // Repository 中新增的派生查询
        if (replay.isPresent()) return replay.get();              // 重发的请求：返回上一次的记录
        var id = new ReadingEntity.ReadingId(body.assetId(), body.occurredAt(), 1);
        if (readings.existsById(id))                              // 这一时刻已有观测：应当走订正
            throw new ReadingExists(body.assetId(), body.occurredAt());
        return readings.saveAndFlush(new ReadingEntity(id, idempotencyKey,
                body.value(), body.unit(), body.quality(), "manual"));
    }
}
