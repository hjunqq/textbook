package edu.example.qingyuan;

import java.math.BigDecimal;
import java.time.OffsetDateTime;

/** Kafka 观测事件契约，字段与第8章 8.3 节一致。 */
public record ReadingEvent(String eventId, String assetId, OffsetDateTime occurredAt,
                           int version, BigDecimal value, String unit,
                           String quality, String source) {}
