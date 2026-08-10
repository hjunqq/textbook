package edu.example.qingyuan;

import java.time.OffsetDateTime;
import jakarta.persistence.*;

@Entity
@Table(name = "reading")
public class ReadingEntity {
    @EmbeddedId private ReadingId id;
    // 幂等键：数据库层为 (occurred_at, event_id) 复合唯一索引
    //（TimescaleDB 超表的唯一索引必须包含分区列，见第8章 8.3 节）
    @Column(name = "event_id", nullable = false) private String eventId;
    @Column(name = "value") private Double value;
    @Column(nullable = false) private String unit;
    @Column(nullable = false) private String quality;
    @Column(nullable = false) private String source;

    protected ReadingEntity() {}
    public ReadingEntity(ReadingId id, String eventId, Double value,
                         String unit, String quality, String source) {
        this.id = id; this.eventId = eventId; this.value = value;
        this.unit = unit; this.quality = quality; this.source = source;
    }

    @Embeddable
    public record ReadingId(@Column(name = "asset_id") String assetId,
                            @Column(name = "occurred_at") OffsetDateTime occurredAt,
                            int version) implements java.io.Serializable {}

    public ReadingId getId() { return id; }
    public String getEventId() { return eventId; }
    public Double getValue() { return value; }
    public String getUnit() { return unit; }
    public String getQuality() { return quality; }
    public String getSource() { return source; }
}
