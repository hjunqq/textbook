package edu.example.qingyuan;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ReadingRepository extends JpaRepository<ReadingEntity, ReadingEntity.ReadingId> {
    List<ReadingEntity> findByIdAssetIdAndIdOccurredAtBetweenOrderByIdOccurredAt(
            String assetId, OffsetDateTime from, OffsetDateTime to);
    boolean existsByEventId(String eventId);

    /** 契约 GET /api/assets/{id}/readings/latest：同一时刻可能有多个版本，取版本号最大的那条。 */
    Optional<ReadingEntity> findFirstByIdAssetIdOrderByIdOccurredAtDescIdVersionDesc(String assetId);
}
