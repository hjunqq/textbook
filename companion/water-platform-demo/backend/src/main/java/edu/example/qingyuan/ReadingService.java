package edu.example.qingyuan;

import java.time.OffsetDateTime;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ReadingService {
    private final ReadingRepository repository;
    public ReadingService(ReadingRepository repository) { this.repository = repository; }

    @Transactional(readOnly = true)
    public List<ReadingEntity> find(String assetId, OffsetDateTime from, OffsetDateTime to) {
        return repository.findByIdAssetIdAndIdOccurredAtBetweenOrderByIdOccurredAt(assetId, from, to);
    }

    /** 幂等写入：先按 eventId 预检，并发重投由数据库复合唯一索引兜底。 */
    @Transactional
    public void accept(ReadingEvent event) {
        if (repository.existsByEventId(event.eventId())) return;
        repository.saveAndFlush(new ReadingEntity(
                new ReadingEntity.ReadingId(event.assetId(), event.occurredAt(), event.version()),
                event.eventId(), event.value(), event.unit(), event.quality(), event.source()));
    }
}
