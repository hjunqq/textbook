package edu.example.qingyuan;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class ReadingConsumer {
    private static final Logger log = LoggerFactory.getLogger(ReadingConsumer.class);
    private final ReadingService readings;
    private final ObjectMapper objectMapper;

    public ReadingConsumer(ReadingService readings, ObjectMapper objectMapper) {
        this.readings = readings; this.objectMapper = objectMapper;
    }

    @KafkaListener(topics = "${app.kafka.reading-topic:qingyuan.reading.v1}",
                   groupId = "qingyuan-quality")
    public void consume(String eventJson) {
        ReadingEvent event;
        try {
            event = objectMapper.readValue(eventJson, ReadingEvent.class);
        } catch (Exception malformed) {
            log.warn("丢弃无法解析的观测事件: {}", malformed.getMessage());
            return; // 教学工程直接丢弃；生产应投入死信主题
        }
        try {
            readings.accept(event);
        } catch (DataIntegrityViolationException duplicate) {
            // 并发重投由唯一索引裁决：事务已回滚，在事务边界之外
            // 捕获并确认消息，避免无谓的重试循环（与第8章口径一致）
            log.debug("重复事件已忽略: {}", event.eventId());
        }
    }
}
