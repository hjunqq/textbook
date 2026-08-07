package edu.example.qingyuan;

import java.time.OffsetDateTime;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ReadingRepository extends JpaRepository<ReadingEntity, ReadingEntity.ReadingId> {
    List<ReadingEntity> findByIdAssetIdAndIdOccurredAtBetweenOrderByIdOccurredAt(String assetId, OffsetDateTime from, OffsetDateTime to);
}
