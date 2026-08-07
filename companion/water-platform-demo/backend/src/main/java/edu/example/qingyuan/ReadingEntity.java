package edu.example.qingyuan;

import java.time.OffsetDateTime;
import jakarta.persistence.*;

@Entity
@Table(name = "reading")
public class ReadingEntity {
    @EmbeddedId private ReadingId id;
    @Column(name = "event_id", nullable = false, unique = true) private String eventId;
    private Double value;
    @Column(nullable = false) private String unit;
    @Column(nullable = false) private String quality;
    @Column(nullable = false) private String source;
    protected ReadingEntity() {}
    @Embeddable public record ReadingId(@Column(name="asset_id") String assetId, @Column(name="occurred_at") OffsetDateTime occurredAt, int version) {}
}
