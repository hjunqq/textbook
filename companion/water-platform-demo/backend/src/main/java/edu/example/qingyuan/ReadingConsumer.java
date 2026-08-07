package edu.example.qingyuan;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class ReadingConsumer {
    private final ReadingRepository repository;
    public ReadingConsumer(ReadingRepository repository) { this.repository = repository; }
    @KafkaListener(topics = "qingyuan.reading.v1", groupId = "qingyuan-quality")
    public void consume(String eventJson) {
        // Deserialize to ReadingEntity and rely on event_id's unique constraint for idempotency.
    }
}
